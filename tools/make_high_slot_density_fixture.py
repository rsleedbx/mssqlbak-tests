#!/usr/bin/env python3
"""Generate ``high_slot_density_full.bak`` — many tiny rows per page (Gap H-4).

## Purpose

Very small rows (e.g. a single ``TINYINT``) pack hundreds of slots per page.
The slot array at the end of each 8 KB page grows accordingly: at minimum
4 bytes per slot (2-byte offset + 2-byte length), so 100 slots consume 400 bytes
out of the page's 8,096 usable bytes.

Slot-array iteration bugs surface when the slot count is large:
  - Wrong ``slot_count`` field → row over- or under-count
  - Reading past the last slot → garbage values or crash
  - Off-by-one in the slot-array walk

A ``TINYINT NOT NULL`` row occupies roughly 14 bytes on the page (7-byte fixed
header + 1-byte fixed data + null bitmap + 4-byte slot entry), fitting ~500 rows
per page.  For 100,000 rows across ~200 pages, the slot array is exercised at
its practical maximum density.

## Schema and data

``dbo.tiny_row`` — (a TINYINT NOT NULL)
  - 100,000 rows, a = (pk mod 256)  (so values cycle 0–255)

## Exported constants (imported by the coverage test)

  - ``DB_NAME``    — database name used in the backup
  - ``ROW_COUNT``  — total rows inserted (100,000)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run high-slot-density
    python -m tools.fixture_run all-versions --suite high-slot-density

Direct (set env vars manually):
    python -m tools.make_high_slot_density_fixture
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

DB_NAME = "HighSlotDensity"
ROW_COUNT = 100_000

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "high_slot_density_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the tiny-row heap."""
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
        """CREATE TABLE dbo.tiny_row (
    a TINYINT NOT NULL
)""",
        # Insert 100,000 rows; a cycles through 0–255
        f"""INSERT INTO dbo.tiny_row (a)
SELECT CAST(pk % 256 AS TINYINT)
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
    print(f"inserting {ROW_COUNT:,} TINYINT rows (high slot density) …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
