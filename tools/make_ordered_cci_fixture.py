#!/usr/bin/env python3
"""Generate ``ordered_cci_full.bak`` — Ordered CCI with ORDER clause (Gap C-7, SS2022+).

## Purpose

SQL Server 2022 introduced the ``ORDER`` clause for ``CREATE CLUSTERED COLUMNSTORE
INDEX``.  An ordered CCI pre-sorts rows within each rowgroup by the specified
key columns before compression.  This enables segment elimination: the optimizer
can skip segments whose min/max metadata does not overlap the query predicate.

From mssqlbak's perspective, an ordered CCI has the same on-disk segment format
as a regular CCI — the ORDER clause changes how rows are arranged before
encoding, not the encoding format itself.  The risk is that the segment
min/max metadata stored for an ordered CCI differs from that of a regular CCI
in a way that breaks mssqlbak's metadata reader.

## Schema and data

``dbo.ordered_cci`` — CCI with ORDER (id)

    id   INT NOT NULL    -- sort key
    val  INT NOT NULL
    grp  INT NOT NULL

``dbo.regular_cci`` — identical schema, regular CCI (no ORDER) for comparison

1,200 rows in each table, inserted in random order (ORDER BY NEWID()) so that
the ordered CCI's sorting effect is visible in the segment min/max metadata.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``        — database name used in the backup
  - ``TABLE_ORDERED``  — ordered CCI table name
  - ``TABLE_REGULAR``  — regular CCI table name (comparison baseline)
  - ``ROW_COUNT``      — total rows per table (1,200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run ordered-cci
    python -m tools.fixture_run all-versions --suite ordered-cci --version 2022 --version 2025

Direct (set env vars manually):
    python -m tools.make_ordered_cci_fixture
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
    skip_if_server_older_than,
)

DB_NAME = "OrderedCci"
TABLE_ORDERED = "ordered_cci"
TABLE_REGULAR = "regular_cci"
ROW_COUNT = 1_200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "ordered_cci_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create, populate, and backup both CCI tables."""
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
        # Ordered CCI (ORDER clause — SS2022+)
        f"""CREATE TABLE dbo.{TABLE_ORDERED} (
    id   INT NOT NULL,
    val  INT NOT NULL,
    grp  INT NOT NULL,
    INDEX cci CLUSTERED COLUMNSTORE ORDER (id)
)""",
        # Random-order insert so the ORDER clause actually re-sorts
        f"""INSERT INTO dbo.{TABLE_ORDERED} (id, val, grp)
SELECT
    pk + 1,
    (pk + 1) * 7,
    (pk % 10) + 1
FROM fkr__seed
WHERE pk < {ROW_COUNT}
ORDER BY NEWID()""",
        # Regular CCI (no ORDER clause) for comparison
        f"""CREATE TABLE dbo.{TABLE_REGULAR} (
    id   INT NOT NULL,
    val  INT NOT NULL,
    grp  INT NOT NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        f"""INSERT INTO dbo.{TABLE_REGULAR} (id, val, grp)
SELECT
    pk + 1,
    (pk + 1) * 7,
    (pk % 10) + 1
FROM fkr__seed
WHERE pk < {ROW_COUNT}
ORDER BY NEWID()""",
        # Compress both
        f"""ALTER INDEX cci ON dbo.{TABLE_ORDERED}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
        f"""ALTER INDEX cci ON dbo.{TABLE_REGULAR}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_server_older_than(2022):
        return 0

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT:,} rows into ordered CCI + regular CCI …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
