#!/usr/bin/env python3
"""Generate ``backup_blocksize_full.bak`` — non-default BLOCKSIZE (Gap A-5).

## Purpose

SQL Server accepts ``BACKUP DATABASE ... WITH BLOCKSIZE = N`` where N can be any
power-of-two from 512 to 65536 bytes (default is 65536).  mssqlbak's
``_detect_block_size()`` probes every candidate size automatically, so a
BLOCKSIZE=4096 backup must be detected and read correctly.

## Schema and data

``dbo.blksz_tbl`` — 100-row simple table (id INT, val VARCHAR(30), n INT)

A backup taken with ``BLOCKSIZE = 4096`` is used.  The same rows must be
returned by mssqlbak regardless of block size.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``   — database name used in the backup
  - ``TABLE``     — table name
  - ``ROW_COUNT`` — total rows inserted (100)
  - ``BLOCK_SIZE`` — BLOCKSIZE used in the backup (4096)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run backup-blocksize
    python -m tools.fixture_run all-versions --suite backup-blocksize
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

DB_NAME = "BackupBlocksize"
TABLE = "blksz_tbl"
ROW_COUNT = 100
BLOCK_SIZE = 4096

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "backup_blocksize_full.bak"
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
    val  VARCHAR(30)  NOT NULL,
    n    INT          NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, val, n)
SELECT
    pk + 1,
    'row_' + CAST(pk + 1 AS VARCHAR(10)),
    (pk + 1) * 7
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        "USE [master]",
        # Non-default block size — the key differentiator for this fixture.
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}'"
        f" WITH FORMAT, INIT, COPY_ONLY, BLOCKSIZE = {BLOCK_SIZE}",
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
    print(f"backing up {ROW_COUNT} rows with BLOCKSIZE={BLOCK_SIZE} …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
