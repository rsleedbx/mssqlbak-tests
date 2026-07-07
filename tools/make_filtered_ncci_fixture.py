#!/usr/bin/env python3
"""Generate ``filtered_ncci_full.bak`` — NCCI with WHERE filter clause (Gap C-4).

## Purpose

A *filtered* NONCLUSTERED COLUMNSTORE INDEX restricts which rows are included
in the index via a WHERE clause:

    CREATE NONCLUSTERED COLUMNSTORE INDEX ix
        ON dbo.t (val)
        WHERE (active = 1)

Only rows that satisfy the predicate are stored in the NCCI segments.  A reader
that uses the NCCI for row extraction would mis-count (fewer rows than the base
table).  mssqlbak must read from the base clustered index and return all rows
regardless of the NCCI filter.

## Schema and data

``dbo.filtered_ncci_base`` — (id INT PK, val INT, active BIT)

- 1,000 rows total
- 500 rows with active = 1  (id 1..500)
- 500 rows with active = 0  (id 501..1000)

Filtered NCCI covers only the active = 1 rows (500 of 1,000).

``dbo.filtered_ncci_heap`` — same columns but WITHOUT clustered index (heap).

Filtered NCCI with WHERE (active = 1) on the heap table.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``        — database name used in the backup
  - ``TABLE_CLUSTERED`` — clustered table name
  - ``TABLE_HEAP``     — heap table name
  - ``ROW_COUNT``      — total rows per table (1,000)
  - ``ACTIVE_COUNT``   — rows matching the NCCI filter (500)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run filtered-ncci
    python -m tools.fixture_run all-versions --suite filtered-ncci

Direct (set env vars manually):
    python -m tools.make_filtered_ncci_fixture
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
    seed_sql,
)

DB_NAME = "FilteredNcci"
TABLE_CLUSTERED = "filtered_ncci_base"
TABLE_HEAP = "filtered_ncci_heap"
ROW_COUNT = 400
ACTIVE_COUNT = 200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "filtered_ncci_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create, populate and backup both tables."""
    stmts: list[str] = [
        # Required for filtered indexes.
        "SET QUOTED_IDENTIFIER ON",
        "SET ANSI_NULLS ON",
        "SET ANSI_PADDING ON",
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        # Clustered table
        f"""CREATE TABLE dbo.{TABLE_CLUSTERED} (
    id     INT  NOT NULL PRIMARY KEY CLUSTERED,
    val    INT  NOT NULL,
    active BIT  NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE_CLUSTERED} (id, val, active)
SELECT
    pk + 1,
    (pk + 1) * 7,
    CASE WHEN pk < {ACTIVE_COUNT} THEN 1 ELSE 0 END
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Filtered NCCI on clustered table — covers only active=1 rows
        f"""CREATE NONCLUSTERED COLUMNSTORE INDEX ix_filtered_ncci
    ON dbo.{TABLE_CLUSTERED} (val)
    WHERE (active = 1)""",
        # Heap table — same schema, no clustered key
        f"""CREATE TABLE dbo.{TABLE_HEAP} (
    id     INT  NOT NULL,
    val    INT  NOT NULL,
    active BIT  NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE_HEAP} (id, val, active)
SELECT
    pk + 1,
    (pk + 1) * 7,
    CASE WHEN pk < {ACTIVE_COUNT} THEN 1 ELSE 0 END
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Filtered NCCI on heap — RID-based locator
        f"""CREATE NONCLUSTERED COLUMNSTORE INDEX ix_filtered_ncci_heap
    ON dbo.{TABLE_HEAP} (val)
    WHERE (active = 1)""",
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
    print(f"inserting {ROW_COUNT:,} rows ({ACTIVE_COUNT} active) into both tables …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
