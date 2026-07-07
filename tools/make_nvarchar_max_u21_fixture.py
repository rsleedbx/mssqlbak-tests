#!/usr/bin/env python3
"""Generate ``nvarchar_max_u21_full.bak`` — nvarchar(max) values whose first
UTF-16LE byte is 0x21.

Regression fixture for the inline nvarchar(max) 0x21-prefix bug: rows.py used
to strip the first byte from any inline nvarchar(max) cell whose first byte was
0x21, treating it as a SQL Server type-marker.  Characters in several Unicode
scripts begin with 0x21 in UTF-16LE:

    U+0021  !  ASCII exclamation mark      bytes: 21 00
    U+0421  С  Cyrillic capital letter Es  bytes: 21 04
    U+0921  ड  Devanagari letter DDA       bytes: 21 09
    U+0C21  డ  Telugu letter DDA           bytes: 21 0C
    U+7121  無 CJK unified ideograph       bytes: 21 71

Stripping the 0x21 left an odd byte count → _decode_nchar returned None.
The fix guards nvarchar(max) by checking cell parity: a genuine 0x21 prefix
produces odd total length (1 prefix + even UTF-16LE data); an even total means
the 0x21 is the first data byte.
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

DB_NAME = "NvarcharMaxU21"
TABLE = "nvarchar_max_u21probe"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "nvarchar_max_u21_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

# Expected values indexed by id — used by the coverage test to avoid drift.
# Constructed with NCHAR() in SQL to sidestep source-file encoding concerns.
EXPECTED: dict[int, str | None] = {
    # Single char: each starts with 0x21 in UTF-16LE
    1: "!",                                        # U+0021 — ASCII ! — bytes 21 00
    2: "С",                                        # U+0421 — Cyrillic
    3: "ड",                                        # U+0921 — Devanagari
    4: "డ",                                        # U+0C21 — Telugu
    5: "無",                                       # U+7121 — CJK
    # Multi-char strings starting with 0x21-first-byte characters
    6: "Сочетание",                                # Russian word, starts with С
    7: "無差別設計",                                 # Chinese phrase, starts with 無
    8: "!" * 20,                                   # 20 ASCII ! chars, all 0x21-first-byte
    # Row whose value does NOT start with 0x21 (positive control)
    9: "Hello world",                              # plain ASCII, first byte 0x48
    # NULL
    10: None,
}

# T-SQL NCHAR() expressions for each value
_SQL_VALS: dict[int, str] = {
    1:  "NCHAR(0x21)",
    2:  "NCHAR(0x421)",
    3:  "NCHAR(0x921)",
    4:  "NCHAR(0xC21)",
    5:  "NCHAR(0x7121)",
    6:  "NCHAR(0x421)+N'очетание'",
    7:  "NCHAR(0x7121)+N'\u5DEE\u5225\u8A2D\u8A08'",
    8:  "REPLICATE(NCHAR(0x21),20)",
    9:  "N'Hello world'",
    10: "NULL",
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
    val NVARCHAR(MAX) NULL
)""",
        f"INSERT INTO dbo.{TABLE} (id, val) VALUES\n    {values_clause}",
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
    print(f"inserting {ROW_COUNT} nvarchar(max) rows with 0x21-first-byte values")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
