#!/usr/bin/env python3
"""Generate ``cci_reorganize_full.bak`` — CCI REORGANIZE + deleted-row bitmap (Gap C-10).

## Purpose

When rows are **deleted** from a Clustered Columnstore Index (CCI) compressed
rowgroup, SQL Server does **not** immediately rewrite the segment.  Instead it
records the deleted row positions in a per-segment "delete bitmap" (stored as
a separate blob in the internal catalog).  A subsequent ``REORGANIZE`` compacts
the segments and physically removes the deleted rows.

mssqlbak may encounter two sub-scenarios:

1. **Delete without REORGANIZE** (``cci_deleted_no_reorg``): deleted rows are
   tracked only via the delete bitmap; the compressed segment still contains
   1,200 rows but only 1,000 are live.  mssqlbak must read the delete bitmap
   to exclude deleted rows.  If it reads raw segment data without checking the
   bitmap it over-counts (returns 1,200 instead of 1,000).

2. **Delete + REORGANIZE** (``cci_deleted_reorg``): after REORGANIZE the
   segment is rewritten with exactly the 1,000 live rows; the delete bitmap is
   cleared.  mssqlbak just reads the compacted segment normally.

Both tables are present in the fixture so mssqlbak can be tested for both paths.

## Schema and data

``dbo.cci_deleted_no_reorg`` — 1,200 rows inserted, compressed, then 200 rows
    deleted.  No REORGANIZE.  Backup contains the original 1,200-row segment +
    delete bitmap marking 200 positions as deleted.  Expected live rows: 1,000.

``dbo.cci_deleted_reorg`` — same data pattern, but REORGANIZE is run after
    the DELETE.  The segment is compacted to exactly 1,000 rows.
    Expected live rows: 1,000.

Rows with ``id % 6 == 0`` are deleted (200 out of 1,200).

## Exported constants (imported by the coverage test)

  - ``DB_NAME``            — database name used in the backup
  - ``TOTAL_INSERTED``     — rows inserted before deletes (1,200)
  - ``DELETED_MOD``        — the modulus for deleted rows (6)
  - ``DELETED_COUNT``      — rows deleted (200)
  - ``LIVE_COUNT``         — expected live rows (1,000)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run cci-reorganize
    python -m tools.fixture_run all-versions --suite cci-reorganize

Direct (set env vars manually):
    python -m tools.make_cci_reorganize_fixture
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

DB_NAME = "CciReorganize"

TOTAL_INSERTED = 1_200
DELETED_MOD = 6          # delete rows where id % DELETED_MOD == 0
DELETED_COUNT = TOTAL_INSERTED // DELETED_MOD   # 200
LIVE_COUNT = TOTAL_INSERTED - DELETED_COUNT     # 1,000

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_reorganize_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

_SCHEMA = """\
    id  INT NOT NULL,
    val INT NOT NULL"""

_DELETE_STMT = f"WHERE id % {DELETED_MOD} = 0"


def _build_cci_table(name: str, reorganize_after_delete: bool) -> list[str]:
    """Return DDL + DML for one CCI table in the fixture."""
    stmts = [
        f"""CREATE TABLE dbo.{name} (
{_SCHEMA}
)""",
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{name} ON dbo.{name}",
        # Insert all rows
        f"""INSERT INTO dbo.{name} (id, val)
SELECT pk + 1 AS id, (pk + 1) * 10 AS val
FROM fkr__seed
WHERE pk < {TOTAL_INSERTED}""",
        # Compress into a rowgroup
        f"ALTER INDEX cci_{name} ON dbo.{name} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # Delete DELETED_COUNT rows — these stay in the segment or get compacted
        f"DELETE FROM dbo.{name} {_DELETE_STMT}",
    ]
    if reorganize_after_delete:
        # Compact the segment: deleted rows are physically removed
        stmts.append(
            f"ALTER INDEX cci_{name} ON dbo.{name} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)"
        )
    return stmts


def build_stmts() -> list[str]:
    """Return statements that create and populate both CCI delete test tables."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(TOTAL_INSERTED)
    stmts += _build_cci_table("cci_deleted_no_reorg", reorganize_after_delete=False)
    stmts += _build_cci_table("cci_deleted_reorg",    reorganize_after_delete=True)
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
    print(
        f"inserting {TOTAL_INSERTED:,} rows, deleting {DELETED_COUNT:,} "
        f"(rows where id % {DELETED_MOD} = 0) from two CCI tables …"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
