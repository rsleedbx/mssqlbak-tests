#!/usr/bin/env python3
"""Generate ``ncci_heap_full.bak`` — NCCI on a heap table (Gap C-5).

## Purpose

A NONCLUSTERED COLUMNSTORE INDEX on a *heap* uses a row identifier (RID =
file:page:slot) as the row locator instead of the clustered-key pointer used
with a B-tree base.  Each NCCI segment carries a matching RID column alongside
the value columns.

Failure mode: if mssqlbak confuses the RID-locator column for a data column
it will produce a wrong column count or decode garbled values.  The fixture
verifies that mssqlbak correctly reads all rows from the heap (via the heap
IAM chain, not the NCCI) and that the NCCI does not introduce spurious extra
columns or rows.

## Schema and data

``dbo.ncci_heap`` — heap table (no clustered index)

    id   INT  NOT NULL
    val  INT  NOT NULL
    name VARCHAR(30) NOT NULL

    NONCLUSTERED COLUMNSTORE INDEX ix_ncci ON (id, val)

1,200 rows inserted, then ``ALTER INDEX ix_ncci ... REORGANIZE WITH
(COMPRESS_ALL_ROW_GROUPS = ON)`` to force compression.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``   — database name used in the backup
  - ``TABLE``     — table name
  - ``ROW_COUNT`` — total rows inserted (1,200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run ncci-heap
    python -m tools.fixture_run all-versions --suite ncci-heap

Direct (set env vars manually):
    python -m tools.make_ncci_heap_fixture
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

DB_NAME = "NcciHeap"
TABLE = "ncci_heap"
ROW_COUNT = 400

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "ncci_heap_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the heap + NCCI table."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        # Heap — intentionally no PRIMARY KEY / clustered index
        f"""CREATE TABLE dbo.{TABLE} (
    id   INT          NOT NULL,
    val  INT          NOT NULL,
    name VARCHAR(30)  NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, val, name)
SELECT
    pk + 1,
    (pk + 1) * 13,
    'row_' + CAST(pk + 1 AS VARCHAR(10))
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # NCCI on id + val columns; heap rows get RID locators in the segment
        f"""CREATE NONCLUSTERED COLUMNSTORE INDEX ix_ncci
    ON dbo.{TABLE} (id, val)""",
        # Force compression of all row groups
        f"""ALTER INDEX ix_ncci ON dbo.{TABLE}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
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
    print(f"inserting {ROW_COUNT:,} rows into a heap with NCCI …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
