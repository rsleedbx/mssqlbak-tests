#!/usr/bin/env python3
"""Generate ``cci_types_large_full.bak`` — one-table-per-type CCI with 1,200 rows (Gap K-3).

## Purpose

Gap K-3 targets five CCI-compatible types that either:
  (a) have no large-row-group compressed-segment coverage at all, or
  (b) need validation with a realistic mix of distinct non-null filler values
      rather than the mostly-NULL fillers used by the K-1 wide-type fixture.

The five types:

  CHAR(20)         — fixed-stride dictionary; K-1 has char_10 with only 3 distinct
                     non-null values.  K-3 uses 26+ distinct char values to stress
                     the multi-entry dictionary decoder.

  BINARY(16)       — fixed-width binary pool; E3B bug expected (same root cause as
                     binary_8 in K-1).  This fixture provides a focused reproduction
                     case at a different width.

  VARBINARY(16)    — variable-length binary pool; NOT present in the type matrix at
                     all (only varbinary_max exists there).  First compressed-segment
                     coverage for this type family.

  UNIQUEIDENTIFIER — fixed 16-byte pool; E3A bug expected (same as K-1).  Focused
                     reproduction with non-trivial dictionary.

  BIT              — boolean bitpack; K-1 has bit with ~1196 NULLs and only 3 rows.
                     K-3 uses 600 TRUE / 600 FALSE rows to stress the bitpack encoder.

## Table layout (one per type)

Each table has schema:

    id   INT NOT NULL
    val  <TYPE> NULL

Rows:
    id=1  — low structural value   (known reference)
    id=2  — high structural value  (known reference)
    id=3  — NULL sentinel          (known reference)
    id=7..1203  — 1,197 non-null filler rows (varied values)

Total: 1,200 rows per table.

All rows are inserted into the delta store then flushed via
``REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`` before backup so that the
segment decoder (not the B-tree delta-store reader) is exercised.

## Exported constants (imported by the coverage test)

  DB_NAME          — database name used in the backup
  ROWS_PER_TABLE   — total rows in each table (structural + filler)
  STRUCTURAL_IDS   — mapping of label → id: {"low": 1, "high": 2, "null": 3}
  TABLE_DEFS       — ordered list of TableDef(name, sql_type, low, high)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run cci-types-large
    python -m tools.fixture_run all-versions --suite cci-types-large

Direct (set env vars manually):
    python -m tools.make_cci_types_large_fixture
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
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

DB_NAME = "CciTypesLarge"

_STRUCTURAL_ROWS = 3   # ids 1, 2, 3  (low / high / null)
_FILLER_ROWS = 1_197   # ids 7..1_203
ROWS_PER_TABLE = _STRUCTURAL_ROWS + _FILLER_ROWS  # 1,200

# ids 5 and 6 are reserved for the differential-backup convention.
_FILLER_START_ID = 7

STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_types_large_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

@dataclass(frozen=True)
class TableDef:
    """One table in the K-3 fixture."""

    name: str          # table name (also index suffix)
    sql_type: str      # SQL Server type declaration
    low: Any           # Python reference value for id=1
    high: Any          # Python reference value for id=2
    low_sql: str       # SQL literal for the low row
    high_sql: str      # SQL literal for the high row
    filler_expr: str   # SQL expression for val, parameterised on n (the ROW_NUMBER alias)


TABLE_DEFS: list[TableDef] = [
    # ------------------------------------------------------------------
    # CHAR(20): fixed-stride dictionary
    # low = 'LLLLLLLLLLLLLLLLLLLL' (20 × 'L')
    # high = 'HHHHHHHHHHHHHHHHHHHH' (20 × 'H')
    # filler: 26 distinct values cycling through A–Z (uppercase)
    # low/high deliberately fall mid-alphabet so the dictionary's native
    # (data_id) order differs from alphabetical order — this discriminates the
    # enc=3 v4 dictionary ordering (Bug K3A); see docs/260618-2-enc3-bugs.md §7.
    # ------------------------------------------------------------------
    TableDef(
        name="cci_char",
        sql_type="CHAR(20)",
        low="L" * 20,
        high="H" * 20,
        low_sql="'LLLLLLLLLLLLLLLLLLLL'",
        high_sql="'HHHHHHHHHHHHHHHHHHHH'",
        filler_expr="REPLICATE(CHAR(65 + ((n - 1) % 26)), 20)",
    ),
    # ------------------------------------------------------------------
    # VARBINARY(16): variable-length binary pool (NEW — not in K-1)
    # low = 0x01 (1 byte)
    # high = 0xFF repeated 16 times (16 bytes)
    # filler: CAST(n AS VARBINARY(16)) — length varies with value magnitude
    # ------------------------------------------------------------------
    TableDef(
        name="cci_varbinary",
        sql_type="VARBINARY(16)",
        low=b"\x01",
        high=b"\xff" * 16,
        low_sql="0x01",
        high_sql="0x" + "FF" * 16,
        filler_expr="CAST(n AS VARBINARY(16))",
    ),
    # ------------------------------------------------------------------
    # BIT: boolean bitpack
    # low = False (0), high = True (1)
    # filler: alternating 0/1 → 598 FALSE + 599 TRUE (or similar)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_bit",
        sql_type="BIT",
        low=False,
        high=True,
        low_sql="0",
        high_sql="1",
        filler_expr="CAST((n % 2) AS BIT)",
    ),
    # ------------------------------------------------------------------
    # BINARY(16): fixed-width binary pool — E3B bug expected
    # low = 0x00…01 (15 zero bytes + 0x01)
    # high = 0xFF repeated 16 times
    # filler: CAST(n AS BINARY(16)) — fixed 16 bytes, value varies
    # ------------------------------------------------------------------
    TableDef(
        name="cci_binary",
        sql_type="BINARY(16)",
        low=b"\x00" * 15 + b"\x01",
        high=b"\xff" * 16,
        low_sql="0x" + "00" * 15 + "01",
        high_sql="0x" + "FF" * 16,
        filler_expr="CAST(n AS BINARY(16))",
    ),
    # ------------------------------------------------------------------
    # UNIQUEIDENTIFIER: fixed 16-byte pool — E3A bug expected
    # low = 00000001-0000-0000-0000-000000000000
    # high = FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF
    # filler: sequential UUIDs from n
    # ------------------------------------------------------------------
    TableDef(
        name="cci_uuid",
        sql_type="UNIQUEIDENTIFIER",
        low=uuid.UUID("00000001-0000-0000-0000-000000000000"),
        high=uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
        low_sql="'00000001-0000-0000-0000-000000000000'",
        high_sql="'FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF'",
        filler_expr=(
            "CAST(CONCAT("
            "RIGHT(CONCAT(REPLICATE('0', 8), CAST(n AS VARCHAR(10))), 8),"
            "'-0000-0000-0000-000000000000') AS UNIQUEIDENTIFIER)"
        ),
    ),
]


def _table_stmts(td: TableDef) -> list[str]:
    """Return statements for one table: CREATE, CCI, structural inserts, filler, REORGANIZE."""
    tbl = td.name
    cci = f"cci_{tbl}"
    filler_start = _FILLER_START_ID
    filler_count = _FILLER_ROWS

    return [
        f"CREATE TABLE {tbl} (id INT NOT NULL, val {td.sql_type} NULL)",
        f"CREATE CLUSTERED COLUMNSTORE INDEX {cci} ON {tbl}",
        f"INSERT INTO {tbl} (id, val) VALUES (1, {td.low_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (2, {td.high_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (3, NULL)",
        # fkr__seed: pk is 0-based; expose pk+1 as n (1-based) for filler_expr
        f"INSERT INTO {tbl} (id, val)"
        f" SELECT pk + {filler_start} AS id, {td.filler_expr} AS val"
        f" FROM (SELECT pk, pk + 1 AS n FROM fkr__seed WHERE pk < {filler_count}) AS _f",
        f"ALTER INDEX {cci} ON {tbl} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def build_stmts() -> list[str]:
    """Return all statements for the K-3 fixture database."""
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
