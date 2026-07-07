#!/usr/bin/env python3
"""Generate ``cci_btree_nci_full.bak`` — CCI + rowstore B-tree NC index (Gap C-12).

## Purpose

A table can have a CLUSTERED COLUMNSTORE INDEX as its primary storage and one or
more regular B-tree NONCLUSTERED indexes alongside it (SQL Server 2016+).  The
B-tree NC index pages use the standard heap/B-tree page format, while the CCI
pages use the columnstore segment format.  Both types of pages share the same
IAM chain structure.

Failure mode: mssqlbak might mis-route B-tree NC index pages through the
columnstore decoder, producing garbled output or a crash.  Alternatively it
might count B-tree index rows as extra CCI rows (double-count).

## Schema and data

``dbo.cci_with_btree`` — CCI table with two rowstore NC indexes

    id    INT          NOT NULL
    code  INT          NOT NULL  -- NC index 1 key
    name  VARCHAR(50)  NOT NULL  -- NC index 2 key
    val   INT          NOT NULL

    INDEX cci CLUSTERED COLUMNSTORE
    CREATE NONCLUSTERED INDEX ix_code  ON dbo.cci_with_btree (code)
    CREATE NONCLUSTERED INDEX ix_name  ON dbo.cci_with_btree (name)

1,200 rows inserted, then REORGANIZE to compress all rowgroups.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``   — database name used in the backup
  - ``TABLE``     — table name
  - ``ROW_COUNT`` — total rows inserted (1,200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run cci-btree-nci
    python -m tools.fixture_run all-versions --suite cci-btree-nci

Direct (set env vars manually):
    python -m tools.make_cci_btree_nci_fixture
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

DB_NAME = "CciBtreeNci"
TABLE = "cci_with_btree"
ROW_COUNT = 1_200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_btree_nci_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create the CCI+B-tree-NC table and take a backup."""
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
        f"""CREATE TABLE dbo.{TABLE} (
    id   INT          NOT NULL,
    code INT          NOT NULL,
    name VARCHAR(50)  NOT NULL,
    val  INT          NOT NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        f"""INSERT INTO dbo.{TABLE} (id, code, name, val)
SELECT
    pk + 1,
    (pk + 1) % 100,
    'item_' + CAST(pk + 1 AS VARCHAR(10)),
    (pk + 1) * 5
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # B-tree NC indexes on the CCI table
        f"CREATE NONCLUSTERED INDEX ix_code ON dbo.{TABLE} (code)",
        f"CREATE NONCLUSTERED INDEX ix_name ON dbo.{TABLE} (name)",
        # Force compression
        f"""ALTER INDEX cci ON dbo.{TABLE}
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
    print(f"inserting {ROW_COUNT:,} rows into CCI + 2 B-tree NC indexes …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
