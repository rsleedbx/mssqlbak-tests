#!/usr/bin/env python3
"""Generate ``delta_rowgroup_full.bak`` — CCI with an open (uncompressed) delta store (Gap C-1).

## Purpose

SQL Server's clustered columnstore index stores newly inserted rows in a B-tree
"delta store" (open rowgroup) until enough rows accumulate to compress into a
segment (≥ 1,048,576 rows), or until an explicit ``REORGANIZE`` flushes them.

When a database is backed up with rows still in the open delta store, the
``_read_columnstore_delta_rows`` path in ``mssqlbak/columnstore.py`` must find
and read those B-tree rows, then combine them with any already-compressed
segment rows.  Without a fixture that exercises this path, the delta store
reader has no regression coverage.

This fixture creates the ``DeltaRowgroup`` database with two tables:

``cs_mixed`` — compressed segment rows + open delta rows in the same CCI
    (columns: ``id INT``, ``kind INT``, ``val INT``)
    * 100 rows (id 1–100, kind=1) — inserted, then compressed
      via ``REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)``
    * 50 rows (id 101–150, kind=2) — inserted after REORGANIZE;
      these stay in the open delta store at backup time

``cs_delta_only`` — CCI with all rows in the open delta store (no segment)
    * 30 rows (id 1–30) — inserted but never reorganized

## Exported constants (imported by the coverage test)

  - ``DB_NAME``                 — database name used in the backup
  - ``CS_MIXED_COMPRESSED``     — row count in the compressed segment
  - ``CS_MIXED_DELTA``          — row count in the open delta store
  - ``CS_MIXED_TOTAL``          — CS_MIXED_COMPRESSED + CS_MIXED_DELTA
  - ``CS_DELTA_ONLY_ROWS``      — row count for cs_delta_only

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run delta-rowgroup
    python -m tools.fixture_run all-versions --suite delta-rowgroup

Direct (set env vars manually):
    python -m tools.make_delta_rowgroup_fixture
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

DB_NAME = "DeltaRowgroup"

# cs_mixed row counts
CS_MIXED_COMPRESSED = 100   # rows flushed into a compressed segment via REORGANIZE
CS_MIXED_DELTA = 50         # rows remaining in the open delta store at backup time
CS_MIXED_TOTAL = CS_MIXED_COMPRESSED + CS_MIXED_DELTA

# cs_delta_only: all rows in the open delta store, no compressed segment
CS_DELTA_ONLY_ROWS = 30

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "delta_rowgroup_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
def build_stmts() -> list[str]:
    """Return statements that create and populate the two CCI tables."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(CS_MIXED_COMPRESSED)  # largest needed: 100 rows
    stmts += [
        """CREATE TABLE cs_mixed (
    id   INT  NOT NULL,
    kind INT  NULL,
    val  INT  NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cs_mixed ON cs_mixed",
        # Batch 1: compressed rows
        f"""INSERT INTO cs_mixed (id, kind, val)
SELECT pk + 1 AS id, 1 AS kind, pk + 1 AS val
FROM fkr__seed
WHERE pk < {CS_MIXED_COMPRESSED}""",
        "ALTER INDEX cci_cs_mixed ON cs_mixed REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # Batch 2: delta rows (inserted after REORGANIZE — stay in open delta store)
        f"""INSERT INTO cs_mixed (id, kind, val)
SELECT pk + {CS_MIXED_COMPRESSED + 1}       AS id,
       2                                    AS kind,
       (pk + {CS_MIXED_COMPRESSED + 1}) * 10 AS val
FROM fkr__seed
WHERE pk < {CS_MIXED_DELTA}""",
        """CREATE TABLE cs_delta_only (
    id  INT  NOT NULL,
    val INT  NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cs_delta_only ON cs_delta_only",
        f"""INSERT INTO cs_delta_only (id, val)
SELECT pk + 1 AS id, pk + 1 AS val
FROM fkr__seed
WHERE pk < {CS_DELTA_ONLY_ROWS}""",
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

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
