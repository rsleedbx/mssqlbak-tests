#!/usr/bin/env python3
"""Generate ``cci_computed_full.bak`` — non-persisted computed columns in CCI (Gap C-11).

## Purpose

SQL Server CCI (Clustered Columnstore Index) can only include PERSISTED computed
columns; non-persisted computed columns are excluded from the CCI segment storage
and are re-evaluated at query time.  A table may have *both* kinds alongside a CCI.

Schema behaviour:
  - Non-persisted computed column: stored only in the row record of a heap/B-tree,
    NOT in CCI segments.  On a CCI table, non-persisted computed columns have no
    segment storage at all — they are computed on the fly.
  - Persisted computed column: stored in the CCI segment like any regular column.

Failure mode: mssqlbak might try to locate a segment for a non-persisted computed
column in the CCI metadata and either raise an error (missing segment), return NULL
for every row, or return a wrong column count.

## Schema and data

``dbo.cci_computed`` — CCI table with mixed column types

    id        INT NOT NULL
    val       INT NOT NULL
    val_x2    AS (val * 2) PERSISTED       -- stored in CCI segments
    val_label AS ('lbl_' + CAST(val AS VARCHAR(10)))  -- NOT persisted; absent from CCI
    grp       INT NOT NULL

    CREATE CLUSTERED COLUMNSTORE INDEX cci ON dbo.cci_computed

1,200 rows inserted, then REORGANIZE to compress.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``      — database name used in the backup
  - ``TABLE``        — table name
  - ``ROW_COUNT``    — total rows inserted (1,200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run cci-computed
    python -m tools.fixture_run all-versions --suite cci-computed

Direct (set env vars manually):
    python -m tools.make_cci_computed_fixture
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

DB_NAME = "CciComputed"
TABLE = "cci_computed"
ROW_COUNT = 1_200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_computed_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the CCI-with-computed table."""
    stmts: list[str] = [
        # Required for tables with computed columns, filtered indexes, and indexed views.
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
        # Create the table with plain columns and inline CCI first.
        # Computed columns cannot be present at CCI creation time; they are
        # added via ALTER TABLE after the CCI is established.
        f"""CREATE TABLE dbo.{TABLE} (
    id   INT NOT NULL,
    val  INT NOT NULL,
    grp  INT NOT NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        f"""INSERT INTO dbo.{TABLE} (id, val, grp)
SELECT
    pk + 1,
    (pk + 1) * 3,
    (pk % 10) + 1
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Compress before adding computed columns so that the CCI rowgroups
        # are fully formed.  Computed columns are then added to the table
        # definition; they are not stored in the CCI segments.
        f"""ALTER INDEX cci ON dbo.{TABLE}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
        # SQL Server prohibits adding PERSISTED computed columns to a CCI table
        # (Columnstore index cannot include a computed column).  Only non-persisted
        # computed columns can be added after the CCI is created.  They are never
        # stored on disk; mssqlbak must not crash looking for a segment.
        f"ALTER TABLE dbo.{TABLE} ADD val_label AS ('lbl_' + CAST(val AS VARCHAR(10)))",
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
    print(f"inserting {ROW_COUNT:,} rows into CCI with persisted + non-persisted computed columns …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
