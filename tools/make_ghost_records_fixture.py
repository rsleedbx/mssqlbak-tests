#!/usr/bin/env python3
"""Generate ``ghost_records_full.bak`` — heap with ghost (deleted) records (Gap H-2).

## Purpose

``DELETE`` marks rows as **ghost** records (status bit in the record header)
but leaves them physically on the page.  Ghost cleanup runs asynchronously on
a background thread; a backup taken before cleanup captures both live rows and
ghost records on the same pages.

A heap scanner that does not check the ghost-record status bit will
**over-count** rows.  This matches the existing failure mode in
``dirtycoverage_temporal_update`` but without the temporal-table complexity
that makes that fixture hard to isolate.

## How ghost records are guaranteed to be present

SQL Server trace flag 661 disables the ghost record cleanup process for the
server session.  The fixture enables TF 661 before the DELETE and disables it
after the BACKUP.  This guarantees that ghost records are present in the .bak
regardless of timing.  TF 661 is available on SQL Server 2008+ (all supported
versions).

## Schema and data pattern

  - ``dbo.ghost_heap``    — heap (no clustered index); id INT, val VARCHAR(100)
  - TOTAL_ROWS inserted (id 1 .. TOTAL_ROWS)
  - Rows where id > LIVE_ROW_COUNT deleted → DELETED_ROWS ghost records on pages

After backup:
  - Live rows:  id 1 .. LIVE_ROW_COUNT  (800 rows)
  - Ghost rows: id LIVE_ROW_COUNT+1 .. TOTAL_ROWS  (200 ghost records, still on pages)

## Exported constants (imported by the coverage test)

  - ``DB_NAME``          — database name used in the backup
  - ``TOTAL_ROWS``       — rows inserted (1,000)
  - ``LIVE_ROW_COUNT``   — rows expected after DELETE (800)
  - ``DELETED_ROWS``     — rows deleted / ghost records on page (200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run ghost-records
    python -m tools.fixture_run all-versions --suite ghost-records

Direct (set env vars manually):
    python -m tools.make_ghost_records_fixture
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
    skip_if_exists,
)

# ---------------------------------------------------------------------------
# Constants (imported by the coverage test)
# ---------------------------------------------------------------------------

DB_NAME = "GhostRecordsCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

TOTAL_ROWS = 1_000
DELETED_ROWS = 200
LIVE_ROW_COUNT = TOTAL_ROWS - DELETED_ROWS  # 800

OUT_PATH = FIXTURE_DIR / "ghost_records_full.bak"


# ---------------------------------------------------------------------------
# SQL builder (pure function — no side effects)
# ---------------------------------------------------------------------------

def build_stmts() -> list[str]:
    """Return DDL + DML + BACKUP statements for the ghost-records fixture."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
  ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "DBCC TRACEON(661, -1) WITH NO_INFOMSGS",
    ]
    stmts += seed_sql(TOTAL_ROWS)
    stmts += [
        """CREATE TABLE dbo.ghost_heap (
    id   INT          NOT NULL,
    val  VARCHAR(100) NOT NULL
)""",
        f"""INSERT INTO dbo.ghost_heap (id, val)
SELECT CAST(pk + 1 AS INT), 'row_' + CAST(pk + 1 AS VARCHAR(20))
FROM fkr__seed
WHERE pk < {TOTAL_ROWS}""",
        f"DELETE FROM dbo.ghost_heap WHERE id > {LIVE_ROW_COUNT}",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
        "DBCC TRACEOFF(661, -1) WITH NO_INFOMSGS",
    ]
    return stmts


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate ghost_records_full.bak — heap with ghost (deleted) "
            "records (Gap H-2)."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing .bak",
    )
    args = parser.parse_args()

    out = OUT_PATH

    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(
        f"inserting {TOTAL_ROWS:,} rows, deleting {DELETED_ROWS:,} "
        f"(ghost records preserved via TF 661) …"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
