#!/usr/bin/env python3
"""Generate ``rowversion_extract_full.bak`` — rowversion / timestamp column (Gap D-3).

## Purpose

``rowversion`` (formerly ``timestamp``) is a fixed 8-byte binary auto-incremented
counter: the database-wide ``@@DBTS`` value at the time of the last row
modification is stored as a big-endian 8-byte value in the record.  It is
*not* a datetime; the name ``timestamp`` is a deprecated synonym.

On the data page the column occupies 8 bytes in the fixed-length section of the
row record.  The bytes are stored big-endian (most-significant byte first),
which differs from ``BIGINT`` (little-endian).

Failure modes:
  - Decoded as ``BIGINT`` → byte-reversed garbage value.
  - Decoded as a datetime type → nonsense.
  - Not returned at all (column skipped due to unrecognised type code).

Expected output: each row's ``rv`` column should be an 8-byte ``bytes`` object.
Values should be distinct across rows and monotonically increasing (DB timestamp
increments on each INSERT).

## Schema and data

``dbo.rv_tbl`` — (id INT PK, label VARCHAR(30), rv rowversion)

100 rows; ``rv`` is populated automatically by SQL Server on every INSERT.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``   — database name used in the backup
  - ``TABLE``     — table name
  - ``ROW_COUNT`` — total rows inserted (100)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run rowversion-extract
    python -m tools.fixture_run all-versions --suite rowversion-extract

Direct (set env vars manually):
    python -m tools.make_rowversion_extract_fixture
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

DB_NAME = "RowversionExtract"
TABLE = "rv_tbl"
ROW_COUNT = 100

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "rowversion_extract_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the rowversion table."""
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
    id    INT          NOT NULL PRIMARY KEY CLUSTERED,
    label VARCHAR(30)  NOT NULL,
    rv    rowversion   NOT NULL
)""",
        # rowversion is auto-populated; do not include it in the INSERT column list
        f"""INSERT INTO dbo.{TABLE} (id, label)
SELECT
    pk + 1,
    'row_' + CAST(pk + 1 AS VARCHAR(10))
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
    print(f"inserting {ROW_COUNT:,} rows with rowversion …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
