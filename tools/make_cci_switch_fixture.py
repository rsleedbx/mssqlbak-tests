#!/usr/bin/env python3
"""Generate ``cci_switch_full.bak`` — CCI PARTITION SWITCH (Gap C-9).

## Purpose

``ALTER TABLE src SWITCH TO dst`` is a metadata-only operation: it reassigns
page ownership from one object to another without moving physical pages.  For
a Clustered Columnstore Index (CCI) table this means the compressed rowgroup
blob pages are re-attributed to the destination object in the catalog.

mssqlbak finds CCI rowgroup pages by looking up ``rowset_id`` / ``hobt_id``
from ``table.alloc_units``.  After a SWITCH the catalog maps those IDs to the
destination table.  If mssqlbak were to use a stale or physical scan it would
either:
  - Return rows under the *source* table (wrong object)
  - Return 0 rows under the *destination* table (missed mapping)
  - Double-count if it walks both

## Schema and data

``dbo.cci_switch_src`` — 1,200 rows (id, batch=1, val) in a single compressed
    rowgroup.  After ``SWITCH TO cci_switch_dst``, this table is empty.

``dbo.cci_switch_dst`` — same schema, empty CCI before switch; 1,200 rows
    after switch.

Backup is taken after the SWITCH, so the catalog reflects the post-switch state.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``         — database name used in the backup
  - ``SRC_TABLE``       — source table name (empty after switch)
  - ``DST_TABLE``       — destination table name (1,200 rows after switch)
  - ``SWITCHED_ROWS``   — number of rows transferred by the switch (1,200)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run cci-switch
    python -m tools.fixture_run all-versions --suite cci-switch

Direct (set env vars manually):
    python -m tools.make_cci_switch_fixture
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

DB_NAME = "CciSwitch"
SRC_TABLE = "cci_switch_src"
DST_TABLE = "cci_switch_dst"
SWITCHED_ROWS = 1_200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_switch_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

_SCHEMA = """\
    id    INT NOT NULL,
    batch INT NOT NULL,
    val   INT NOT NULL"""


def build_stmts() -> list[str]:
    """Return statements that create, switch, and backup the CCI tables."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(SWITCHED_ROWS)
    stmts += [
        # Source table: populated + compressed
        f"""CREATE TABLE dbo.{SRC_TABLE} (
{_SCHEMA}
)""",
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{SRC_TABLE} ON dbo.{SRC_TABLE}",
        f"""INSERT INTO dbo.{SRC_TABLE} (id, batch, val)
SELECT pk + 1 AS id, 1 AS batch, (pk + 1) * 10 AS val
FROM fkr__seed
WHERE pk < {SWITCHED_ROWS}""",
        f"ALTER INDEX cci_{SRC_TABLE} ON dbo.{SRC_TABLE} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # Destination table: empty CCI with same schema (required for SWITCH)
        f"""CREATE TABLE dbo.{DST_TABLE} (
{_SCHEMA}
)""",
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{DST_TABLE} ON dbo.{DST_TABLE}",
        # PARTITION SWITCH: metadata-only, reassigns rowgroup ownership
        f"ALTER TABLE dbo.{SRC_TABLE} SWITCH TO dbo.{DST_TABLE}",
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
        f"inserting {SWITCHED_ROWS:,} rows into {SRC_TABLE!r}, "
        f"compressing, then switching to {DST_TABLE!r} …"
    )

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
