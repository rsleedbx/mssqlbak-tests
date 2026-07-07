#!/usr/bin/env python3
"""Generate ``compressed_nvarchar_full.bak`` — ROW-compressed nvarchar regression fixture.

## Purpose

Under ROW compression SQL Server stores ``nchar``/``nvarchar`` values using
**SCSU** (Standard Compression Scheme for Unicode) when that encoding is strictly
shorter than UTF-16LE, and as plain **UTF-16LE** otherwise.  The decision is made
per value at write time:

  - ASCII strings → SCSU (each char = 1 byte + trailing SC0 0x10) — always shorter.
  - Cyrillic / Greek / other scripts with a single dominant Unicode block →
    SCSU with a window-select prefix — usually shorter.
  - CJK ideographs → UTF-16LE wins because SCSU requires a window-switch per
    character and gains nothing for characters spread across many blocks.

``mssqlbak.rowcompress._is_utf16le_not_scsu`` chooses the decoder for each value.
A bug in that heuristic silently corrupts any nvarchar column under ROW/PAGE
compression, and no end-to-end ``.bak`` fixture existed to catch a regression.

## Table schema

    CREATE TABLE dbo.compressed_nvar (
        id  INT           NOT NULL PRIMARY KEY CLUSTERED,
        val NVARCHAR(200) NULL
    ) WITH (DATA_COMPRESSION = ROW)

## Rows

  id=1   "Hello"            ASCII — SCSU passthrough, odd length (5 bytes)
  id=2   "Привет"           Cyrillic (U+041F…U+0442) — SCSU window-select
  id=3   "山田"             CJK (U+5C71 U+7530) — UTF-16LE (SCSU would cost more)
  id=4   "Αλφα"             Greek (U+0391…U+03B1) — SCSU window-select
  id=5   "Hello свет"       Mixed ASCII+Cyrillic — SCSU with window switch
  id=6   NULL               — always-NULL control
  id=7   "Test " × 20       Long ASCII (100 chars) — SCSU passthrough, odd length
  id=8   "我要测试"          CJK (U+6211 U+8981 U+6D4B U+8BD5) — UTF-16LE

## Exported constants (imported by the coverage test)

  - ``DB_NAME``    — database name
  - ``TABLE``      — table name ("compressed_nvar")
  - ``EXPECTED``   — dict mapping id → expected Python str (or None for NULL)
  - ``ROW_COUNT``  — total rows inserted

Usage:
    python -m tools.fixture_run compressed-nvarchar
    python -m tools.fixture_run all-versions --suite compressed-nvarchar
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "CompressedNvarchar"
TABLE = "compressed_nvar"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "compressed_nvarchar_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

# Expected values indexed by id — imported by the coverage test to avoid drift.
# Multi-byte Unicode literals are spelled out via NCHAR() in the SQL to sidestep
# source-file encoding concerns (see _SQL_VALS below).
EXPECTED: dict[int, str | None] = {
    # ASCII → SCSU passthrough (odd-length: 5 bytes).  Heuristic returns False.
    1: "Hello",
    # Cyrillic "Привет" (U+041F U+0440 U+0438 U+0432 U+0435 U+0442).
    # SCSU with Cyrillic window: 7 bytes vs 12 bytes UTF-16LE → SCSU wins.
    2: "\u041f\u0440\u0438\u0432\u0435\u0442",
    # CJK "山田" (U+5C71 U+7530).
    # UTF-16LE: 4 bytes; SCSU would need 6 bytes → UTF-16LE wins.
    # Heuristic: bytes 71 5C 30 75 — even length, all in 0x20–0x7F → True (UTF-16LE).
    3: "\u5c71\u7530",
    # Greek "Αλφα" (U+0391 U+03BB U+03C6 U+03B1).
    # SCSU with Greek window: 5 bytes vs 8 bytes UTF-16LE → SCSU wins.
    4: "\u0391\u03bb\u03c6\u03b1",
    # Mixed ASCII+Cyrillic "Hello свет" (ASCII 'Hello ' + U+0441 U+0432 U+0435 U+0442).
    # SCSU with window switch: shorter than UTF-16LE for the Cyrillic tail.
    5: "Hello \u0441\u0432\u0435\u0442",
    # NULL — always-NULL row, exercises the null-handling branch.
    6: None,
    # Long ASCII REPLICATE("Test ", 20) = 100 chars.
    # SCSU: 100 bytes (odd? 100 is even, so SQL Server appends SC0 0x10 → 101 bytes).
    # Heuristic: odd length → False → SCSU.
    7: "Test " * 20,
    # CJK "我要测试" (U+6211 U+8981 U+6D4B U+8BD5).
    # UTF-16LE: 8 bytes; SCSU needs window switches → UTF-16LE wins.
    8: "\u6211\u8981\u6d4b\u8bd5",
}

# T-SQL expressions that produce each value; NCHAR() avoids source-file encoding issues.
_SQL_VALS: dict[int, str] = {
    1: "N'Hello'",
    2: (
        "NCHAR(0x41F)+NCHAR(0x440)+NCHAR(0x438)"
        "+NCHAR(0x432)+NCHAR(0x435)+NCHAR(0x442)"
    ),
    3: "NCHAR(0x5C71)+NCHAR(0x7530)",
    4: "NCHAR(0x391)+NCHAR(0x3BB)+NCHAR(0x3C6)+NCHAR(0x3B1)",
    5: "N'Hello '+NCHAR(0x441)+NCHAR(0x432)+NCHAR(0x435)+NCHAR(0x442)",
    6: "NULL",
    7: "REPLICATE(N'Test ',20)",
    8: "NCHAR(0x6211)+NCHAR(0x8981)+NCHAR(0x6D4B)+NCHAR(0x8BD5)",
}

ROW_COUNT = len(EXPECTED)


def build_stmts() -> list[str]:
    values_clause = ",\n    ".join(
        f"({row_id}, {_SQL_VALS[row_id]})"
        for row_id in sorted(_SQL_VALS)
    )
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id  INT           NOT NULL PRIMARY KEY CLUSTERED,
    val NVARCHAR(200) NULL
) WITH (DATA_COMPRESSION = ROW)""",
        f"INSERT INTO dbo.{TABLE} (id, val) VALUES\n    {values_clause}",
        # Rebuild forces the clustered index to recompress all rows in ROW format.
        f"ALTER INDEX ALL ON dbo.{TABLE} REBUILD WITH (DATA_COMPRESSION = ROW)",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(
        f"inserting {ROW_COUNT} ROW-compressed nvarchar rows "
        "(ASCII/Cyrillic/CJK/Greek/mixed/NULL)"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
