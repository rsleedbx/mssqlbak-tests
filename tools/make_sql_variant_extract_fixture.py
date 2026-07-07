#!/usr/bin/env python3
"""Generate ``sql_variant_extract_full.bak`` — sql_variant value extraction (Gap D-2).

## Purpose

``sql_variant`` stores a per-value type-metadata header (base type, precision,
scale, collation, max-length) followed by the actual value.  A single column
can hold different SQL types row-to-row — e.g. ``INT``, ``DECIMAL``,
``NVARCHAR``, ``DATETIME2`` in different rows.

Currently mssqlbak lists ``sql_variant`` in ``_MINMAX_SKIP_TYPES`` (min/max
extraction skipped), but the value itself should still be extracted correctly.
Without a dedicated extraction test, silent corruption of ``sql_variant`` values
would go undetected.

The per-value header format:
  - 1 byte: DBTYPE ordinal for the base type
  - Variable: type-specific metadata (precision+scale for DECIMAL, max-length for
    NVARCHAR, etc.)
  - N bytes: the actual value in the same wire format as its base type

mssqlbak must parse the header to select the correct type decoder, then decode
the value payload.

## Schema and data

``dbo.sv`` — (id INT PRIMARY KEY, val SQL_VARIANT NULL)

id 1 — CAST(42        AS INT)
id 2 — CAST(3.14      AS DECIMAL(8,4))
id 3 — CAST(N'hello'  AS NVARCHAR(20))
id 4 — CAST(1         AS BIGINT)
id 5 — CAST('2025-01-01' AS DATETIME2(0))
id 6 — NULL
id 7 — CAST(CONVERT(uniqueidentifier, '11111111-1111-1111-1111-111111111111') AS sql_variant)
id 8 — CAST(0xDEADBEEF AS sql_variant)
id 9 — CAST(CONVERT(datetimeoffset, '2020-01-02T03:04:05.1234567+05:30') AS sql_variant)
id 10 — CAST(CAST(1.2300 AS decimal(10,4)) AS sql_variant)

## Exported constants (imported by the coverage test)

  - ``DB_NAME``         — database name used in the backup
  - ``ROW_COUNT``       — total rows inserted (10)
  - ``EXPECTED_VALUES`` — dict[id, expected Python value] for non-null rows

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run sql-variant-extract
    python -m tools.fixture_run all-versions --suite sql-variant-extract

Direct (set env vars manually):
    python -m tools.make_sql_variant_extract_fixture
"""
from __future__ import annotations

import argparse
import decimal
import datetime
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
)

DB_NAME = "SqlVariantExtract"
ROW_COUNT = 10

# Expected Python values per id (None = SQL NULL).
# sql_variant preserves the original type; mssqlbak should return the
# Python equivalent of the stored base type.
EXPECTED_VALUES: dict[int, object] = {
    1: 42,                              # INT → int
    2: decimal.Decimal("3.1400"),       # DECIMAL(8,4) → Decimal
    3: "hello",                         # NVARCHAR(20) → str
    4: 1,                               # BIGINT → int
    5: datetime.datetime(2025, 1, 1),   # DATETIME2(0) → datetime
    6: None,                            # NULL
    7: "11111111-1111-1111-1111-111111111111",
    8: "0xdeadbeef",
    9: "2020-01-02 03:04:05.123456 +05:30",
    10: decimal.Decimal("1.2300"),
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "sql_variant_extract_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the sql_variant table."""
    rows = [
        (1, "CAST(42 AS INT)"),
        (2, "CAST(3.14 AS DECIMAL(8,4))"),
        (3, "CAST(N'hello' AS NVARCHAR(20))"),
        (4, "CAST(1 AS BIGINT)"),
        (5, "CAST('2025-01-01' AS DATETIME2(0))"),
        (6, "NULL"),
        (7, "CAST(CONVERT(uniqueidentifier, '11111111-1111-1111-1111-111111111111') AS sql_variant)"),
        (8, "CAST(0xDEADBEEF AS sql_variant)"),
        (9, "CAST(CONVERT(datetimeoffset, '2020-01-02T03:04:05.1234567+05:30') AS sql_variant)"),
        (10, "CAST(CAST(1.2300 AS decimal(10,4)) AS sql_variant)"),
    ]
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        """CREATE TABLE dbo.sv (
    id  INT         NOT NULL PRIMARY KEY CLUSTERED,
    val SQL_VARIANT NULL
)""",
    ]
    for row_id, val_expr in rows:
        stmts.append(f"INSERT INTO dbo.sv (id, val) VALUES ({row_id}, {val_expr})")
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
    print(f"inserting {ROW_COUNT} sql_variant rows with mixed types …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
