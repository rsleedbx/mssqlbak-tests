#!/usr/bin/env python3
"""Generate ``forwarded_records_full.bak`` — heap with forwarded records (Gap H-1).

## Purpose

When a heap row is widened (e.g. via UPDATE to a longer varchar) and no longer
fits on its original page, SQL Server writes the real row elsewhere and leaves a
**forwarding stub** (record type ``0x04``) on the original page pointing to the
new RID.

A heap scanner that:
  - counts forwarding stubs **and** the real row  → double-counts rows
  - reads the stub bytes as row data             → produces garbage values
  - skips forwarded targets                      → under-counts rows

This pattern matches the silent row-count errors observed on real-world heaps
in the corpus.

## Schema and data pattern

  - ``dbo.fwd_heap``  — heap (no clustered index); id INT, val VARCHAR(8000)
  - ``dbo.fwd_control`` — clustered table with the same rows (always correct)
  - ROW_COUNT rows inserted with short val (``REPLICATE('x', 10)``)
  - Odd IDs (1, 3, …, ROW_COUNT-1) updated to long val (``REPLICATE('y', 7000)``)
    → those rows no longer fit alongside other rows and are forwarded

After backup:
  - Even IDs: val length = SHORT_VAL_LEN (10)  — stay in original page slot
  - Odd IDs:  val length = LONG_VAL_LEN (7000) — forwarding stub in original slot,
              real row on a new page

## Exported constants (imported by the coverage test)

  - ``DB_NAME``        — database name used in the backup
  - ``ROW_COUNT``      — total rows (1,000)
  - ``SHORT_VAL_LEN``  — 10; length of val for even IDs
  - ``LONG_VAL_LEN``   — 7000; length of val for odd IDs

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run forwarded-records
    python -m tools.fixture_run all-versions --suite forwarded-records

Direct (set env vars manually):
    python -m tools.make_forwarded_records_fixture
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

DB_NAME = "ForwardedRecordsCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

ROW_COUNT = 1_000
SHORT_VAL_LEN = 10
LONG_VAL_LEN = 7_000

OUT_PATH = FIXTURE_DIR / "forwarded_records_full.bak"


# ---------------------------------------------------------------------------
# SQL builder (pure function — no side effects)
# ---------------------------------------------------------------------------

def build_stmts() -> list[str]:
    """Return DDL + DML + BACKUP statements for the forwarded-records fixture."""
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
        """CREATE TABLE dbo.fwd_heap (
    id   INT           NOT NULL,
    val  VARCHAR(8000) NOT NULL
)""",
        """CREATE TABLE dbo.fwd_control (
    id   INT           NOT NULL PRIMARY KEY CLUSTERED,
    val  VARCHAR(8000) NOT NULL
)""",
        f"""INSERT INTO dbo.fwd_heap (id, val)
SELECT CAST(pk + 1 AS INT), REPLICATE('x', {SHORT_VAL_LEN})
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        f"""INSERT INTO dbo.fwd_control (id, val)
SELECT CAST(pk + 1 AS INT), REPLICATE('x', {SHORT_VAL_LEN})
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        f"UPDATE dbo.fwd_heap SET val = REPLICATE('y', {LONG_VAL_LEN}) WHERE id % 2 = 1",
        f"UPDATE dbo.fwd_control SET val = REPLICATE('y', {LONG_VAL_LEN}) WHERE id % 2 = 1",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate forwarded_records_full.bak — heap with forwarded records "
            "(Gap H-1)."
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
        f"seeding {ROW_COUNT:,} rows, then widening "
        f"{ROW_COUNT // 2:,} odd-id rows to force forwarding …"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
