#!/usr/bin/env python3
"""Generate ``max_row_width_full.bak`` — single row per page edge case (Gap H-3).

## Purpose

SQL Server's maximum in-row data per page is **8,060 bytes**.  A row engineered
to occupy nearly the whole page produces a page with a single slot entry in the
slot array.

Off-by-one errors in free-space or slot-count arithmetic surface when a page
contains exactly one slot:
  - The slot array (at the page end) may be misread if code assumes ≥ 2 rows.
  - ``page_header.slot_count`` of 1 may be treated as an error sentinel.
  - The row offset stored in slot[0] might be confused with the start of the
    slot array itself.

## Schema and data

``dbo.wide_row`` — (id INT PRIMARY KEY, data CHAR(8000))
    8,004 bytes per row (4-byte INT + 8,000-byte CHAR).  SQL Server fits exactly
    one row per 8,192-byte page (96-byte header + slot array overhead).

Five rows with id 1–5, each with a distinct 8,000-character fill value
(all 'A's for id 1, all 'B's for id 2, etc.) to distinguish rows in tests.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``    — database name used in the backup
  - ``ROW_COUNT``  — number of rows inserted (5)
  - ``DATA_LEN``   — CHAR length (8,000)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run max-row-width
    python -m tools.fixture_run all-versions --suite max-row-width

Direct (set env vars manually):
    python -m tools.make_max_row_width_fixture
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
)

DB_NAME = "MaxRowWidth"
ROW_COUNT = 5
DATA_LEN = 8_000

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "max_row_width_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

# Fill characters: one distinct character per row so rows are distinguishable.
_FILL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def build_stmts() -> list[str]:
    """Return statements that create and populate the wide-row table."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.wide_row (
    id   INT      NOT NULL PRIMARY KEY CLUSTERED,
    data CHAR({DATA_LEN}) NOT NULL
)""",
    ]
    for i in range(1, ROW_COUNT + 1):
        fill = _FILL_CHARS[(i - 1) % len(_FILL_CHARS)]
        stmts.append(
            f"INSERT INTO dbo.wide_row (id, data) "
            f"VALUES ({i}, REPLICATE('{fill}', {DATA_LEN}))"
        )
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
    print(f"inserting {ROW_COUNT} rows of CHAR({DATA_LEN}) (one row per page) …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
