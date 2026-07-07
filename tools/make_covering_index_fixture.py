#!/usr/bin/env python3
"""Generate ``covering_index_full.bak`` — nonclustered index with included columns (Gap E-1).

## Purpose

A "covering index" adds non-key columns to the leaf level of a nonclustered
B-tree index via the ``INCLUDE`` clause:

    CREATE NONCLUSTERED INDEX ix ON t(k) INCLUDE (a_varchar, b_decimal);

The NC leaf page record carries:
  - the key column(s) (``k``)
  - included columns (``a_varchar``, ``b_decimal``)
  - the clustered-key or RID locator

Each leaf record has its own NULL bitmap and variable-length section for the
included columns.  An NC-page reader that assumes the leaf record contains only
key columns will produce wrong offsets for the included columns.

mssqlbak's primary extraction path reads the clustered index (or heap) and
does not use NC indexes for row data.  This fixture verifies that:

1. ``classify_table`` correctly identifies the base table as extractable.
2. Row extraction from the base table returns all rows with correct values
   (i.e. the NC index does not interfere with the base-table read).
3. The NC index object does not cause mssqlbak to emit spurious extra rows.

## Schema and data

``dbo.covering_base`` — (id INT PK, code INT, name VARCHAR(50), amount DECIMAL(10,2))
    1,000 rows.

NC index: ``CREATE NONCLUSTERED INDEX ix_covering ON dbo.covering_base(code)
    INCLUDE (name, amount)``

## Exported constants (imported by the coverage test)

  - ``DB_NAME``    — database name used in the backup
  - ``ROW_COUNT``  — total rows inserted (1,000)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run covering-index
    python -m tools.fixture_run all-versions --suite covering-index

Direct (set env vars manually):
    python -m tools.make_covering_index_fixture
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

DB_NAME = "CoveringIndex"
ROW_COUNT = 1_000

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "covering_index_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the covering-index table."""
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
        """CREATE TABLE dbo.covering_base (
    id     INT            NOT NULL PRIMARY KEY CLUSTERED,
    code   INT            NOT NULL,
    name   VARCHAR(50)    NOT NULL,
    amount DECIMAL(10,2)  NOT NULL
)""",
        # NC covering index: key=code, includes name+amount
        """CREATE NONCLUSTERED INDEX ix_covering
    ON dbo.covering_base (code)
    INCLUDE (name, amount)""",
        f"""INSERT INTO dbo.covering_base (id, code, name, amount)
SELECT
    pk + 1                                         AS id,
    (pk + 1) % 100                                 AS code,
    'item_' + CAST(pk + 1 AS VARCHAR(10))          AS name,
    CAST((pk + 1) * 1.25 AS DECIMAL(10,2))         AS amount
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
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
    print(f"inserting {ROW_COUNT:,} rows with a covering NC index (INCLUDE name, amount) …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
