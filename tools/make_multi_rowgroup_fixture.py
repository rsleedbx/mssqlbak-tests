#!/usr/bin/env python3
"""Generate ``multi_rowgroup_full.bak`` — CCI with multiple small compressed rowgroups (Gap C-3).

## Purpose

SQL Server stores CCI data in compressed "rowgroups".  The segment index in the
catalog (``sys.column_store_row_groups`` / ``syscscolsegments``) contains one
entry per (rowgroup, column) pair.  mssqlbak groups segments by ``(hobt_id,
seg_id)`` to reconstruct each rowgroup.

If mssqlbak stops after reading the first rowgroup it will silently drop all
rows from subsequent rowgroups — a row-count error with no exception.

This fixture creates three compressed rowgroups by inserting rows in three
batches and running ``REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`` between
each batch.  Each REORGANIZE closes the open delta store into a new compressed
rowgroup without merging existing ones.

## Schema

``dbo.cs_multi`` — (id INT, batch INT, val INT)
  * Batch 1: 1,200 rows (id   1– 1,200, batch=1)  → rowgroup 0
  * Batch 2:   600 rows (id 1,201– 1,800, batch=2) → rowgroup 1
  * Batch 3:   300 rows (id 1,801– 2,100, batch=3) → rowgroup 2
  Total: 2,100 rows in 3 compressed rowgroups.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``          — database name used in the backup
  - ``BATCH1_ROWS``      — rows in batch 1 (rowgroup 0)
  - ``BATCH2_ROWS``      — rows in batch 2 (rowgroup 1)
  - ``BATCH3_ROWS``      — rows in batch 3 (rowgroup 2)
  - ``TOTAL_ROWS``       — total rows (3,100)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run multi-rowgroup
    python -m tools.fixture_run all-versions --suite multi-rowgroup

Direct (set env vars manually):
    python -m tools.make_multi_rowgroup_fixture
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

DB_NAME = "MultiRowgroup"

BATCH1_ROWS = 1_200
BATCH2_ROWS = 600
BATCH3_ROWS = 300
TOTAL_ROWS = BATCH1_ROWS + BATCH2_ROWS + BATCH3_ROWS  # 2,100

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "multi_rowgroup_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the multi-rowgroup CCI table."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    # seed table needs enough rows for the largest batch
    stmts += seed_sql(BATCH1_ROWS)
    stmts += [
        """CREATE TABLE dbo.cs_multi (
    id    INT NOT NULL,
    batch INT NOT NULL,
    val   INT NOT NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cs_multi ON dbo.cs_multi",
        # --- Batch 1 ---
        f"""INSERT INTO dbo.cs_multi (id, batch, val)
SELECT pk + 1 AS id, 1 AS batch, (pk + 1) * 10 AS val
FROM fkr__seed
WHERE pk < {BATCH1_ROWS}""",
        # Flush batch 1 → rowgroup 0 (compressed, closed)
        "ALTER INDEX cci_cs_multi ON dbo.cs_multi REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # --- Batch 2 ---
        f"""INSERT INTO dbo.cs_multi (id, batch, val)
SELECT pk + {BATCH1_ROWS + 1} AS id, 2 AS batch, (pk + {BATCH1_ROWS + 1}) * 10 AS val
FROM fkr__seed
WHERE pk < {BATCH2_ROWS}""",
        # Flush batch 2 → rowgroup 1 (compressed, closed)
        "ALTER INDEX cci_cs_multi ON dbo.cs_multi REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # --- Batch 3 ---
        f"""INSERT INTO dbo.cs_multi (id, batch, val)
SELECT pk + {BATCH1_ROWS + BATCH2_ROWS + 1} AS id, 3 AS batch, (pk + {BATCH1_ROWS + BATCH2_ROWS + 1}) * 10 AS val
FROM fkr__seed
WHERE pk < {BATCH3_ROWS}""",
        # Flush batch 3 → rowgroup 2 (compressed, closed)
        "ALTER INDEX cci_cs_multi ON dbo.cs_multi REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
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
    print(
        f"inserting {TOTAL_ROWS:,} rows in 3 batches "
        f"({BATCH1_ROWS}, {BATCH2_ROWS}, {BATCH3_ROWS}) "
        "with REORGANIZE between each batch …"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
