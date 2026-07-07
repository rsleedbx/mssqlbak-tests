#!/usr/bin/env python3
"""Generate ``tabletype_cci_large_full.bak`` — wide-type CCI with 1,200 rows (Gap K-1).

## Purpose

The existing ``tabletypecoverage_full.bak`` carries only 4 rows in ``tt_column``
(the clustered columnstore table).  Although ``REORGANIZE WITH
(COMPRESS_ALL_ROW_GROUPS = ON)`` forces those 4 rows into a compressed segment,
the resulting row group is trivially small: dictionary encoding, bit-packing,
and RLE are all degenerate at 4 rows.  The segment decoder is exercised in
name only — its real encoding paths (multi-entry dictionaries, bitmask arrays,
run-length null vectors) are never reached for any of the 25 CCI-compatible
types.

This fixture creates a fresh database ``TabletypeCciLarge`` with a single
table ``tt_column`` that contains:

  * 4 structural rows (id=1 low, 2 high, 3 mid, 4 null) — identical type
    values to ``tabletypecoverage_full.bak`` so the reference matrix can be
    reused in tests.
  * 1,196 filler rows (ids 7..1,202) with all type columns NULL — forces
    non-trivial null bit-vectors and dictionary encoding across all 25 types.

A clustered columnstore index is created on the empty table, rows are inserted
(→ delta store), then ``REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)``
flushes every row into a compressed segment before backup.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``           — database name used in the backup
  - ``TOTAL_ROWS``        — rows in ``tt_column`` (structural + filler = 1,200)
  - ``STRUCTURAL_ROW_IDS`` — mapping of label → id for the 4 reference rows

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run tabletype-cci-large
    python -m tools.fixture_run all-versions --suite tabletype-cci-large

Direct (set env vars manually):
    python -m tools.make_tabletype_cci_large_fixture
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
    _load_and_backup,
    discover_container,
    sqlcmd_base,
)
from tools.make_tabletype_fixture import (  # noqa: E402
    _create_table,
    _insert_filler_rows,
    _insert_rows,
)
from tools.tabletypematrix import LABEL_ID, ORG_CASES, table_name  # noqa: E402

DB_NAME = "TabletypeCciLarge"

# 4 structural rows (low/high/mid/null) + 1,196 filler rows = 1,200 total.
# 1,200 rows is enough to produce non-trivial dictionary encoding, bit-packing,
# and null bit-vectors in the compressed CCI segment.
TOTAL_ROWS = 1_200
_STRUCTURAL_ROWS = 4  # ids 1-4 (low/high/mid/null via LABEL_ID)

# Expose for tests so they can assert id → label mapping.
STRUCTURAL_ROW_IDS: dict[str, int] = dict(LABEL_ID)  # {"low": 1, "high": 2, ...}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "tabletype_cci_large_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
_CONTAINER_SQL = f"/tmp/load_{DB_NAME}.sql"


def build_sql() -> str:
    """Return the T-SQL script that creates, populates, and compresses ``tt_column``."""
    col_org = next(o for o in ORG_CASES if o.name == "column")
    tbl = table_name(col_org)  # "tt_column"
    filler_count = TOTAL_ROWS - _STRUCTURAL_ROWS  # 1,196

    parts: list[str] = [
        "USE [master];",
        "GO",
        # Drop and recreate the database unconditionally so reruns are clean.
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
        # _create_table emits CREATE TABLE ... + GO + CREATE CLUSTERED COLUMNSTORE INDEX.
        _create_table(col_org),
        "GO",
        # Structural rows: id 1=low, 2=high, 3=mid, 4=null.
        _insert_rows(col_org),
        "GO",
        # Filler rows start at id=7 (ids 5-6 are reserved for diff-backup convention).
        # All type columns are NULL; only id is populated.
        _insert_filler_rows(col_org, filler_count),
        "GO",
        # Push every delta-store row into a compressed row group so that the CCI
        # segment decoder (not the B-tree delta-store reader) is exercised.
        f"ALTER INDEX [cci_{tbl}] ON [{tbl}] REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);",
        "GO",
    ]
    return "\n".join(parts) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print(
            "error: set FIXTURE_DBA_PASSWORD (forgedb setup blob -> dba.password)",
            file=sys.stderr,
        )
        return 2

    container = discover_container()
    print(f"using container {container} as {user}")
    sqlcmd = sqlcmd_base(user, password, container)

    sql = (
        build_sql()
        + "USE [master];\nGO\n"
        + f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{_CONTAINER_BAK}'"
        + " WITH FORMAT, INIT, COPY_ONLY;\nGO\n"
    )
    _load_and_backup(container, sqlcmd, sql, _CONTAINER_SQL)
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
