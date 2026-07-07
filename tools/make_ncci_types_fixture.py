#!/usr/bin/env python3
"""Generate ``ncci_types_full.bak`` — one-table-per-type rowstore with NCCI (Gap K-5).

## Purpose

Gap K-5 extends NCCI type coverage beyond the four columns in ``ncci_table``
(featurecoverage_full.bak).  The existing NCCI is built only on ``INT`` and
``DECIMAL`` columns.  This fixture exercises every CCI-compatible type via the
NCCI segment encoder with 1,200 rows per table, ensuring:

  1. NCCI segment encoding/decoding is exercised for all major types.
  2. The row-locator column (clustered-key pointer INT) stored beside each NCCI
     segment does not corrupt type-dependent segment parsing.
  3. NULL rows, low/high boundary values, and varied fillers are all present.

## NCCI vs CCI difference

Each table has a normal clustered B-tree primary key (``id INT NOT NULL PRIMARY
KEY CLUSTERED``) plus a ``CREATE NONCLUSTERED COLUMNSTORE INDEX`` on the
value column.  Unlike CCI, the NCCI stores a row-locator (clustered-key pointer)
column beside every value segment.  The segment encoding for the value column is
identical to CCI; the extra locator column must not disturb value decoding.

## Types covered

  BIGINT           — 8-byte signed integer
  SMALLINT         — 2-byte signed integer
  TINYINT          — 1-byte unsigned integer
  BIT              — boolean bitpack
  FLOAT            — 8-byte IEEE 754
  REAL             — 4-byte IEEE 754
  MONEY            — fixed-point, 8 bytes
  SMALLMONEY       — fixed-point, 4 bytes
  DATE             — calendar date (3 bytes)
  DATETIME2(3)     — timestamp with 100ns precision
  TIME(3)          — time-of-day
  DATETIMEOFFSET(3)— timezone-aware timestamp
  CHAR(10)         — fixed-width ASCII
  NCHAR(10)        — fixed-width Unicode
  VARCHAR(50)      — variable-width ASCII
  NVARCHAR(50)     — variable-width Unicode
  BINARY(8)        — fixed-width binary
  VARBINARY(8)     — variable-width binary
  UNIQUEIDENTIFIER — 16-byte GUID

## Table layout (one per type)

Each table:

    id   INT NOT NULL PRIMARY KEY CLUSTERED
    val  <TYPE> NULL

    NONCLUSTERED COLUMNSTORE INDEX ncci ON <table> (val)

Rows:
    id=1  — low boundary value
    id=2  — high boundary value
    id=3  — NULL sentinel
    id=7..1206  — 1,200 filler rows (varied values; skip 4,5,6 per convention)

Total: 1,203 rows per table.
All rows are inserted then flushed via
``REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`` before backup.

## Exported constants (imported by the coverage test)

  DB_NAME          — database name used in the backup
  ROWS_PER_TABLE   — total rows in each table
  STRUCTURAL_IDS   — {"low": 1, "high": 2, "null": 3}
  TABLE_DEFS       — ordered list of TableDef(name, sql_type, low, high, ...)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run ncci-types
    python -m tools.fixture_run all-versions --suite ncci-types

Direct (set env vars manually):
    python -m tools.make_ncci_types_fixture
"""
from __future__ import annotations

import argparse
import datetime
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

DB_NAME = "NcciTypes"

_STRUCTURAL_ROWS = 3    # ids 1, 2, 3 (low / high / null)
_FILLER_ROWS = 1_200    # ids 7..1206
ROWS_PER_TABLE = _STRUCTURAL_ROWS + _FILLER_ROWS   # 1,203

# ids 4, 5, 6 are reserved for the differential-backup convention.
_FILLER_START_ID = 7

STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "ncci_types_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


@dataclass(frozen=True)
class TableDef:
    """One table in the K-5 NCCI fixture."""

    name: str           # table name (ncci_<type>)
    sql_type: str       # SQL Server type declaration
    low: Any            # Python reference value for id=1
    high: Any           # Python reference value for id=2
    low_sql: str        # SQL literal for the low row
    high_sql: str       # SQL literal for the high row
    filler_expr: str    # SQL expression for val, parameterised on n (1-based ROW_NUMBER alias)


TABLE_DEFS: list[TableDef] = [
    # ------------------------------------------------------------------
    # BIGINT — 8-byte signed integer
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_bigint",
        sql_type="BIGINT",
        low=-9_223_372_036_854_775_808,
        high=9_223_372_036_854_775_807,
        low_sql="-9223372036854775808",
        high_sql="9223372036854775807",
        filler_expr="CAST(n AS BIGINT) * 1000000",
    ),
    # ------------------------------------------------------------------
    # SMALLINT — 2-byte signed integer
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_smallint",
        sql_type="SMALLINT",
        low=-32_768,
        high=32_767,
        low_sql="-32768",
        high_sql="32767",
        filler_expr="CAST((n % 65535) - 32767 AS SMALLINT)",
    ),
    # ------------------------------------------------------------------
    # TINYINT — 1-byte unsigned integer (0-255)
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_tinyint",
        sql_type="TINYINT",
        low=0,
        high=255,
        low_sql="0",
        high_sql="255",
        filler_expr="CAST(n % 256 AS TINYINT)",
    ),
    # ------------------------------------------------------------------
    # BIT — boolean bitpack; 600 FALSE / 600 TRUE fillers
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_bit",
        sql_type="BIT",
        low=False,
        high=True,
        low_sql="0",
        high_sql="1",
        filler_expr="CAST(n % 2 AS BIT)",
    ),
    # ------------------------------------------------------------------
    # FLOAT — 8-byte IEEE 754 double precision
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_float",
        sql_type="FLOAT",
        low=-1.7976931348623157e308,
        high=1.7976931348623157e308,
        low_sql="-1.7976931348623157E+308",
        high_sql="1.7976931348623157E+308",
        filler_expr="CAST(n AS FLOAT) * 3.14159265358979",
    ),
    # ------------------------------------------------------------------
    # REAL — 4-byte IEEE 754 single precision
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_real",
        sql_type="REAL",
        low=-3.4028235e38,
        high=3.4028235e38,
        low_sql="-3.4028235E+38",
        high_sql="3.4028235E+38",
        filler_expr="CAST(n AS REAL) * 3.14",
    ),
    # ------------------------------------------------------------------
    # MONEY — fixed-point; range -922337203685477.5808 to 922337203685477.5807
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_money",
        sql_type="MONEY",
        low=-922_337_203_685_477.5808,
        high=922_337_203_685_477.5807,
        low_sql="-922337203685477.5808",
        high_sql="922337203685477.5807",
        filler_expr="CAST(n AS MONEY) * 100.0",
    ),
    # ------------------------------------------------------------------
    # SMALLMONEY — fixed-point; range -214748.3648 to 214748.3647
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_smallmoney",
        sql_type="SMALLMONEY",
        low=-214_748.3648,
        high=214_748.3647,
        low_sql="-214748.3648",
        high_sql="214748.3647",
        filler_expr="CAST((n % 2147) AS SMALLMONEY) * 100.0",
    ),
    # ------------------------------------------------------------------
    # DATE — 3-byte calendar date; 0001-01-01 to 9999-12-31
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_date",
        sql_type="DATE",
        low=datetime.date(2000, 1, 1),
        high=datetime.date(2099, 12, 31),
        low_sql="'2000-01-01'",
        high_sql="'2099-12-31'",
        filler_expr="DATEADD(DAY, n, '2000-01-01')",
    ),
    # ------------------------------------------------------------------
    # DATETIME2(3) — 100ns-precision timestamp
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_datetime2",
        sql_type="DATETIME2(3)",
        low=datetime.datetime(2000, 1, 1, 0, 0, 0, 0),
        high=datetime.datetime(2099, 12, 31, 23, 59, 59, 999_000),
        low_sql="'2000-01-01 00:00:00.000'",
        high_sql="'2099-12-31 23:59:59.999'",
        filler_expr="DATEADD(SECOND, n, '2000-01-01 00:00:00.000')",
    ),
    # ------------------------------------------------------------------
    # TIME(3) — time-of-day with 3 fractional seconds
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_time",
        sql_type="TIME(3)",
        low=datetime.time(0, 0, 0, 0),
        high=datetime.time(23, 59, 59, 999_000),
        low_sql="'00:00:00.000'",
        high_sql="'23:59:59.999'",
        filler_expr="CAST(DATEADD(SECOND, n % 86400, '00:00:00') AS TIME(3))",
    ),
    # ------------------------------------------------------------------
    # DATETIMEOFFSET(3) — timezone-aware timestamp
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_datetimeoffset",
        sql_type="DATETIMEOFFSET(3)",
        low=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc),
        high=datetime.datetime(2099, 12, 31, 23, 59, 59, 999_000, tzinfo=datetime.timezone.utc),
        low_sql="'2000-01-01 00:00:00.000 +00:00'",
        high_sql="'2099-12-31 23:59:59.999 +00:00'",
        filler_expr="TODATETIMEOFFSET(DATEADD(SECOND, n, '2000-01-01 00:00:00'), '+00:00')",
    ),
    # ------------------------------------------------------------------
    # CHAR(10) — fixed-width ASCII; 26 distinct values cycling A-Z
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_char",
        sql_type="CHAR(10)",
        low="L" * 10,
        high="H" * 10,
        low_sql="'LLLLLLLLLL'",
        high_sql="'HHHHHHHHHH'",
        filler_expr="REPLICATE(CHAR(65 + ((n - 1) % 26)), 10)",
    ),
    # ------------------------------------------------------------------
    # NCHAR(10) — fixed-width Unicode; 26 distinct values cycling A-Z
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_nchar",
        sql_type="NCHAR(10)",
        low="L" * 10,
        high="H" * 10,
        low_sql="N'LLLLLLLLLL'",
        high_sql="N'HHHHHHHHHH'",
        filler_expr="REPLICATE(NCHAR(65 + ((n - 1) % 26)), 10)",
    ),
    # ------------------------------------------------------------------
    # VARCHAR(50) — variable-width ASCII
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_varchar",
        sql_type="VARCHAR(50)",
        low="row_low",
        high="row_high",
        low_sql="'row_low'",
        high_sql="'row_high'",
        filler_expr="'row_' + CAST(n AS VARCHAR(10))",
    ),
    # ------------------------------------------------------------------
    # NVARCHAR(50) — variable-width Unicode
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_nvarchar",
        sql_type="NVARCHAR(50)",
        low="row_low",
        high="row_high",
        low_sql="N'row_low'",
        high_sql="N'row_high'",
        filler_expr="N'row_' + CAST(n AS NVARCHAR(10))",
    ),
    # ------------------------------------------------------------------
    # BINARY(8) — fixed-width binary; trailing zeros stripped under ROW compression
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_binary",
        sql_type="BINARY(8)",
        low=b"\x00" * 7 + b"\x01",
        high=b"\xff" * 8,
        low_sql="0x" + "00" * 7 + "01",
        high_sql="0x" + "FF" * 8,
        filler_expr="CAST(n AS BINARY(8))",
    ),
    # ------------------------------------------------------------------
    # VARBINARY(8) — variable-width binary
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_varbinary",
        sql_type="VARBINARY(8)",
        low=b"\x01",
        high=b"\xff" * 8,
        low_sql="0x01",
        high_sql="0x" + "FF" * 8,
        filler_expr="CAST(n AS VARBINARY(8))",
    ),
    # ------------------------------------------------------------------
    # UNIQUEIDENTIFIER — 16-byte GUID
    # ------------------------------------------------------------------
    TableDef(
        name="ncci_uuid",
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
    """Statements for one table: CREATE, NCCI, structural inserts, fillers, REORGANIZE."""
    tbl = td.name
    ncci_idx = f"ncci_{tbl}"
    filler_count = _FILLER_ROWS

    return [
        f"CREATE TABLE {tbl} (id INT NOT NULL CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED, val {td.sql_type} NULL)",
        f"CREATE NONCLUSTERED COLUMNSTORE INDEX {ncci_idx} ON {tbl} (val)",
        f"INSERT INTO {tbl} (id, val) VALUES (1, {td.low_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (2, {td.high_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (3, NULL)",
        # fkr__seed: pk is 0-based; expose pk+1 as n (1-based) for filler_expr.
        f"INSERT INTO {tbl} (id, val)"
        f" SELECT pk + {_FILLER_START_ID} AS id, {td.filler_expr} AS val"
        f" FROM (SELECT pk, pk + 1 AS n FROM fkr__seed WHERE pk < {filler_count}) AS _f",
        f"ALTER INDEX {ncci_idx} ON {tbl} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def build_stmts() -> list[str]:
    """Return all statements for the K-5 NCCI-types fixture database."""
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
    print(f"using container {container} as {user}", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
