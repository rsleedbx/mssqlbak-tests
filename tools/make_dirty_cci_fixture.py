#!/usr/bin/env python3
"""Generate dirtycoverage_cci_delete.bak and dirtycoverage_cci_update.bak.

These fixtures exercise mssqlbak's dirty-backup handling for tables stored
as a **Clustered Columnstore Index (CCI)** — a storage layout that has never
been covered by the existing dirty-backup suite.

## Why CCI is different in a dirty backup

A CCI stores data in two distinct on-disk structures:

* **Compressed rowgroups** — read-only columnar segments written by
  REORGANIZE / REBUILD or large-batch inserts.  Each rowgroup is several
  pages; rows inside it can only be "deleted" via a separate delete-bitmap
  rowgroup, not by modifying the compressed segment.
* **Open delta store** — a B-tree heap of recently inserted rows that have
  not yet been compressed.  This is structurally identical to an ordinary
  rowstore heap, so DELETEs and UPDATEs on delta rows produce the same
  ``committed_delete_slots`` / ``redo_patches`` log records as rowstore.

The fixture strategy:

1. Insert ``COMPRESSED_ROWS`` rows, then
   ``ALTER INDEX … REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`` to force
   them into a compressed rowgroup.
2. Insert ``DELTA_ROWS`` more rows — these stay in the open delta store.
3. Run a dirty backup concurrently with a DELETE (or UPDATE) targeting
   only the delta-store rows.

This ensures both page types (compressed rowgroup and delta store) appear in
the backup and that the REDO / suppress pass is exercised on the delta pages.

Usage (preferred)::

    .venv/bin/python -m tools.fixture_run all-versions --suite dirty-cci

Single version::

    .venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 dirty-cci

Direct::

    .venv/bin/python -m tools.make_dirty_cci_fixture [--force] [--only delete|update]
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
    dirty_backup_concurrent,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
    skip_if_exists,
)

# ---------------------------------------------------------------------------
# Public constants (imported by tests to avoid drift)
# ---------------------------------------------------------------------------

DB_NAME_DELETE = "DirtyCCIDel"
DB_NAME_UPDATE = "DirtyCCIUpd"

# Rows compressed into a rowgroup (forced by REORGANIZE after insertion)
COMPRESSED_ROWS = 5_000
# Rows inserted after REORGANIZE — stay in open delta store (B-tree pages)
DELTA_ROWS = 2_000
TOTAL_ROWS = COMPRESSED_ROWS + DELTA_ROWS   # 7 000

# IDs of delta-store rows that are modified mid-backup (first DELETE/UPDATE_COUNT deltas)
DELETE_COUNT = 1_000   # ids COMPRESSED_ROWS+1 .. COMPRESSED_ROWS+DELETE_COUNT
UPDATE_COUNT = 1_000   # ids COMPRESSED_ROWS+1 .. COMPRESSED_ROWS+UPDATE_COUNT

DELETED_ID_LO = COMPRESSED_ROWS + 1
DELETED_ID_HI = COMPRESSED_ROWS + DELETE_COUNT    # 6 000
UPDATED_ID_LO = COMPRESSED_ROWS + 1
UPDATED_ID_HI = COMPRESSED_ROWS + UPDATE_COUNT    # 6 000

EXPECTED_ROWS_AFTER_DELETE = TOTAL_ROWS - DELETE_COUNT   # 6 000
EXPECTED_ROWS_AFTER_UPDATE = TOTAL_ROWS                  # 7 000

# Column names present in dbo.dirty_cci (imported by tests)
COLUMNS = ["id", "phase", "val", "score"]

# ---------------------------------------------------------------------------
# Internal path constants
# ---------------------------------------------------------------------------

_BAK_DIR = "/var/opt/mssql/data"
_CONTAINER_BAK_DELETE = f"{_BAK_DIR}/dirtycoverage_cci_delete.bak"
_CONTAINER_BAK_UPDATE = f"{_BAK_DIR}/dirtycoverage_cci_update.bak"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

OUT_DELETE = FIXTURE_DIR / "dirtycoverage_cci_delete.bak"
OUT_UPDATE = FIXTURE_DIR / "dirtycoverage_cci_update.bak"


# ---------------------------------------------------------------------------
# SQL builders
# ---------------------------------------------------------------------------

def _setup_stmts(db_name: str, delta_phase: str) -> list[str]:
    """Return DDL + DML statements that build the CCI DB (no BACKUP DATABASE).

    Structure:
      * Insert COMPRESSED_ROWS rows (phase='compressed') then REORGANIZE them
        into a compressed rowgroup.
      * Insert DELTA_ROWS rows (phase=*delta_phase*) — these stay in the open
        delta store and are the DML target during the dirty backup.
    """
    stmts: list[str] = [
        f"""IF DB_ID(N'{db_name}') IS NOT NULL BEGIN
  ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db_name}]
END""",
        f"CREATE DATABASE [{db_name}]",
        f"USE [{db_name}]",
    ]
    stmts += seed_sql(TOTAL_ROWS)
    stmts += [
        """CREATE TABLE dbo.dirty_cci (
    id    INT          NOT NULL,
    phase VARCHAR(10)  NOT NULL,
    val   VARCHAR(100) NOT NULL,
    score FLOAT        NOT NULL,
    INDEX cci_idx CLUSTERED COLUMNSTORE
)""",
        # First batch → will be REORGANIZE'd into a compressed rowgroup
        f"""INSERT INTO dbo.dirty_cci (id, phase, val, score)
SELECT
    pk + 1                                          AS id,
    'compressed'                                    AS phase,
    'val_' + CAST(pk + 1 AS VARCHAR(10))            AS val,
    CAST(pk + 1 AS FLOAT) / 3.0                     AS score
FROM fkr__seed
WHERE pk < {COMPRESSED_ROWS}""",
        # Force all open delta groups into compressed rowgroups
        "ALTER INDEX cci_idx ON dbo.dirty_cci REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        # Second batch → stays in open delta store; these are the dirty DML target
        f"""INSERT INTO dbo.dirty_cci (id, phase, val, score)
SELECT
    pk + 1                                                 AS id,
    '{delta_phase}'                                        AS phase,
    'original_' + CAST(pk + 1 AS VARCHAR(10))              AS val,
    CAST(pk + 1 AS FLOAT) / 5.0                            AS score
FROM fkr__seed
WHERE pk >= {COMPRESSED_ROWS} AND pk < {TOTAL_ROWS}""",
    ]
    return stmts


def _reset_stmts_delete() -> list[str]:
    """Re-insert deleted delta rows (ids DELETED_ID_LO..DELETED_ID_HI) — idempotent."""
    return [
        f"DELETE FROM dbo.dirty_cci WHERE id >= {DELETED_ID_LO} AND id <= {DELETED_ID_HI}",
        f"""INSERT INTO dbo.dirty_cci (id, phase, val, score)
SELECT
    pk + 1,
    'delete',
    'original_' + CAST(pk + 1 AS VARCHAR(10)),
    CAST(pk + 1 AS FLOAT) / 5.0
FROM fkr__seed
WHERE pk >= {COMPRESSED_ROWS} AND pk < {COMPRESSED_ROWS + DELETE_COUNT}""",
    ]


def _reset_stmts_update() -> list[str]:
    """Restore val to 'original_N' for delta rows (ids UPDATED_ID_LO..UPDATED_ID_HI)."""
    return [
        f"UPDATE dbo.dirty_cci"
        f" SET val = 'original_' + CAST(id AS VARCHAR(10))"
        f" WHERE id >= {UPDATED_ID_LO} AND id <= {UPDATED_ID_HI}",
    ]


def _dml_sql_delete() -> str:
    return f"DELETE FROM dbo.dirty_cci WHERE id >= {DELETED_ID_LO} AND id <= {DELETED_ID_HI}"


def _dml_sql_update() -> str:
    return (
        f"UPDATE dbo.dirty_cci"
        f" SET val = 'updated_' + CAST(id AS VARCHAR(10))"
        f" WHERE id >= {UPDATED_ID_LO} AND id <= {UPDATED_ID_HI}"
    )


# ---------------------------------------------------------------------------
# Per-fixture builders
# ---------------------------------------------------------------------------

def _build_delete(container: str, user: str, password: str, out: Path) -> None:
    print(
        f"\n=== CCI DELETE: {COMPRESSED_ROWS} compressed + {DELTA_ROWS} delta rows; "
        f"DELETE {DELETE_COUNT} delta rows mid-backup ===",
        file=sys.stderr,
    )
    load_and_backup_stmts(container, user, password, _setup_stmts(DB_NAME_DELETE, "delete"))
    dirty_backup_concurrent(
        container, user, password,
        DB_NAME_DELETE, _CONTAINER_BAK_DELETE,
        _dml_sql_delete(), _reset_stmts_delete(),
        require_cds=False,
    )
    size = _copy_out(container, _CONTAINER_BAK_DELETE, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)


def _build_update(container: str, user: str, password: str, out: Path) -> None:
    print(
        f"\n=== CCI UPDATE: {COMPRESSED_ROWS} compressed + {DELTA_ROWS} delta rows; "
        f"UPDATE {UPDATE_COUNT} delta rows mid-backup ===",
        file=sys.stderr,
    )
    load_and_backup_stmts(container, user, password, _setup_stmts(DB_NAME_UPDATE, "update"))
    dirty_backup_concurrent(
        container, user, password,
        DB_NAME_UPDATE, _CONTAINER_BAK_UPDATE,
        _dml_sql_update(), _reset_stmts_update(),
        require_cds=False,
    )
    size = _copy_out(container, _CONTAINER_BAK_UPDATE, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate dirtycoverage_cci_{delete,update}.bak — "
            "dirty backup fixtures with a Clustered Columnstore Index table "
            "(compressed rowgroup + open delta store) using mssql_python + fkr__seed."
        )
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing .bak files")
    parser.add_argument(
        "--only",
        choices=["delete", "update"],
        help="build only one of the two fixtures (default: both)",
    )
    args = parser.parse_args()

    out_del = FIXTURE_DIR / "dirtycoverage_cci_delete.bak"
    out_upd = FIXTURE_DIR / "dirtycoverage_cci_update.bak"

    want_delete = args.only in (None, "delete")
    want_update = args.only in (None, "update")

    targets = [p for p, want in [(out_del, want_delete), (out_upd, want_update)] if want]
    if skip_if_exists(*targets, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)

    if want_delete and (not out_del.exists() or args.force):
        _build_delete(container, user, password, out_del)

    if want_update and (not out_upd.exists() or args.force):
        _build_update(container, user, password, out_upd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
