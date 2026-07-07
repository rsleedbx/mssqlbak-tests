#!/usr/bin/env python3
"""Generate ``cci_lob_full.bak`` — CCI tables with VARCHAR(MAX), NVARCHAR(MAX),
VARBINARY(MAX) columns (Gap C-6).

## Purpose

Gap C-6 covers ``(max)``-length LOB types in Columnstore Indexes.  These types
use a different dictionary-encoding format than their bounded-length cousins:

- ``VARCHAR(MAX)``    — cp1252 payload with varint length prefix + 0x21 separator
- ``NVARCHAR(MAX)``   — UTF-16LE payload with varint length prefix + 0x21 separator
- ``VARBINARY(MAX)``  — raw bytes payload with varint length prefix + 0x21 separator

The key discriminating case is ``NVARCHAR(MAX)`` with values longer than 127 chars
(≥ 128 chars = ≥ 256 bytes in UTF-16LE).  Below that threshold the regular
1-byte-length UTF-16LE dictionary format works; at or above it the varint format
fires.  If the varint payload is decoded as cp1252 instead of UTF-16LE the result
is a doubled-length string with interleaved NUL bytes.

## Table layout (one per type)

Each table has schema:

    id   INT NOT NULL
    val  <TYPE> NULL

Structural rows (ids 1-4):
    id=1  low   — empty / b'' value  (0-byte payload, tests empty varint entry)
    id=2  mid   — moderate-length value (< 127 chars, tests 1-byte-length format)
    id=3  high  — long value (≥ 128 chars / bytes, triggers varint encoding)
    id=4  null  — NULL value

Filler rows (ids 7..1202):
    1,196 rows with NULL val — pads the row group so CCI segment compression fires.

Total: 1,200 rows per table.

## Exported constants (imported by the coverage test)

  DB_NAME          — database name used in the backup
  ROWS_PER_TABLE   — total rows in each table
  STRUCTURAL_IDS   — mapping label → id
  TABLE_DEFS       — ordered list of TableDef(name, sql_type, ...)

Usage (preferred):
    python -m tools.fixture_run cci-lob
    python -m tools.fixture_run all-versions --suite cci-lob

Direct:
    python -m tools.make_cci_lob_fixture
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
)

DB_NAME = "CciLob"

_STRUCTURAL_ROWS = 4   # ids 1-4 (low / mid / high / null)
_FILLER_ROWS = 1_196   # ids 7..1_202
ROWS_PER_TABLE = _STRUCTURAL_ROWS + _FILLER_ROWS  # 1,200

# ids 5 and 6 are reserved for the differential-backup convention.
_FILLER_START_ID = 7

STRUCTURAL_IDS: dict[str, int] = {"low": 1, "mid": 2, "high": 3, "null": 4}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_lob_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


@dataclass(frozen=True)
class TableDef:
    """One table in the C-6 LOB fixture."""

    name: str           # table name
    sql_type: str       # SQL Server type declaration
    low: Any            # Python reference value for id=1 (empty)
    mid: Any            # Python reference value for id=2 (fits 1-byte-length)
    high: Any           # Python reference value for id=3 (needs varint)
    low_sql: str        # SQL literal for id=1
    mid_sql: str        # SQL literal for id=2
    high_sql: str       # SQL literal for id=3


TABLE_DEFS: list[TableDef] = [
    # ------------------------------------------------------------------
    # VARCHAR(MAX): cp1252 payload with varint length prefix
    #
    # low  = ''           (empty — 0 bytes, varint = 0x01 0x21)
    # mid  = 'A' * 100   (100 bytes, fits 1-byte length ≤ 255)
    # high = 'Z' * 300   (300 bytes, needs varint: 1-byte can only hold ≤ 255)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_varchar_max",
        sql_type="VARCHAR(MAX)",
        low="",
        mid="A" * 100,
        high="Z" * 300,
        low_sql="''",
        mid_sql="REPLICATE('A', 100)",
        high_sql="REPLICATE('Z', 300)",
    ),
    # ------------------------------------------------------------------
    # NVARCHAR(MAX): UTF-16LE payload with varint length prefix
    #
    # The key discriminating case for Bug C-6: values encoded as UTF-16LE
    # bytes in the varint format.  If decoded as cp1252, the mid/high values
    # become strings with interleaved NUL characters.
    #
    # low  = ''            (empty)
    # mid  = 'N' * 200    (200 chars = 400 bytes UTF-16LE; 1-byte-length max
    #                       is 255 bytes = 127 chars, so this needs varint)
    # high = 'Z' * 500    (500 chars = 1000 bytes UTF-16LE, definitely varint)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_nvarchar_max",
        sql_type="NVARCHAR(MAX)",
        low="",
        mid="N" * 200,
        high="Z" * 500,
        low_sql="N''",
        mid_sql="REPLICATE(N'N', 200)",
        high_sql="REPLICATE(N'Z', 500)",
    ),
    # ------------------------------------------------------------------
    # VARBINARY(MAX): raw bytes payload with varint length prefix
    #
    # low  = b''            (empty)
    # mid  = b'\xaa' * 100  (100 bytes, fits 1-byte)
    # high = b'\xff' * 300  (300 bytes, needs varint)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_varbinary_max",
        sql_type="VARBINARY(MAX)",
        low=b"",
        mid=b"\xaa" * 100,
        high=b"\xff" * 300,
        low_sql="0x",
        mid_sql="0x" + "AA" * 100,
        high_sql="0x" + "FF" * 300,
    ),
]


def _table_stmts(td: TableDef) -> list[str]:
    """Return statements for one table: CREATE, structural inserts, filler, REORGANIZE."""
    tbl = td.name
    cci = f"idx_cci_{tbl}"
    filler_start = _FILLER_START_ID
    filler_count = _FILLER_ROWS

    return [
        f"CREATE TABLE {tbl} (id INT NOT NULL, val {td.sql_type} NULL)",
        f"CREATE CLUSTERED COLUMNSTORE INDEX {cci} ON {tbl}",
        f"INSERT INTO {tbl} (id, val) VALUES (1, {td.low_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (2, {td.mid_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (3, {td.high_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (4, NULL)",
        # fkr__seed: pk is 0-based; filler rows all get NULL for the LOB column
        f"INSERT INTO {tbl} (id, val)"
        f" SELECT pk + {filler_start}, NULL"
        f" FROM fkr__seed WHERE pk < {filler_count}",
        f"ALTER INDEX {cci} ON {tbl} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def build_stmts() -> list[str]:
    """Return all statements for the C-6 LOB fixture database."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(_FILLER_ROWS)
    for td in TABLE_DEFS:
        stmts += _table_stmts(td)
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
