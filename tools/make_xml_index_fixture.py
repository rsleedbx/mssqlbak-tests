#!/usr/bin/env python3
"""Generate ``xml_index_full.bak`` — XML index internal node table (Gap E-3).

## Purpose

A PRIMARY XML INDEX materializes an internal "node table" (object type IT =
internal_table) alongside the user table.  The node table stores the shredded
XML path/value pairs in a system-owned clustered B-tree with hidden columns
(pk1, id, nid, tag, value, hid, etc.).

Failure mode: if ``recover_schema`` enumerates the internal node table as a user
table, it emits a bogus table with hidden-column layout; if ``read_table_rows``
walks those pages with the rowstore reader it will crash on the unexpected
record shape.

The fix is that ``recover_schema`` already filters on ``sysschobjs.type == 'U'``
(user tables only).  ``type = 'IT'`` (internal tables) are never returned.
This fixture proves that guarantee holds even when a primary + secondary XML
index exists on the same database.

## Schema and data

``dbo.xml_docs`` — 100-row table with an untyped XML column.

    id   INT NOT NULL PRIMARY KEY
    doc  XML NULL
    tag  VARCHAR(20) NOT NULL

A PRIMARY XML INDEX and a secondary FOR PATH XML index are created.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE``
  - ``ROW_COUNT``

Usage:
    python -m tools.fixture_run xml-index
    python -m tools.fixture_run all-versions --suite xml-index
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

DB_NAME = "XmlIndex"
TABLE = "xml_docs"
ROW_COUNT = 100

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "xml_index_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
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
    id   INT          NOT NULL PRIMARY KEY CLUSTERED,
    doc  XML          NULL,
    tag  VARCHAR(20)  NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, doc, tag)
SELECT
    pk + 1,
    '<item id="' + CAST(pk + 1 AS VARCHAR(10)) + '"><val>' + CAST((pk + 1) * 7 AS VARCHAR(10)) + '</val></item>',
    'tag_' + CAST((pk + 1) % 5 AS VARCHAR(5))
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Primary XML index (prerequisite for secondary)
        f"CREATE PRIMARY XML INDEX pxi_{TABLE} ON dbo.{TABLE}(doc)",
        # Secondary XML index (FOR PATH — creates additional internal node table)
        f"CREATE XML INDEX sxi_{TABLE}_path ON dbo.{TABLE}(doc)"
        f" USING XML INDEX pxi_{TABLE} FOR PATH",
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
    print(f"creating XML index on {ROW_COUNT} rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
