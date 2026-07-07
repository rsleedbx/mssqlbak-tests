#!/usr/bin/env python3
"""Generate dirtycoverage_committed_delete_v4.bak and
dirtycoverage_committed_update_v4.bak.

V4 uses the newer fixture convention:

* **fkr__seed** for fast row generation (no cross-join CTEs).
* **mssql_python** direct TCP connections for the timing-critical dirty backup
  step — no ``podman exec sqlcmd`` round-trip overhead, so the 30–50 ms
  concurrency window is reliably hit within ~3–5 retries.
* ``require_cds=True``: the delete fixture is rejected until
  ``committed_delete_slots > 0`` (not accepted by accident).
* ``redo_patches > 0`` is verified before the update fixture is accepted.

This file is **standalone** — it does not import from ``make_dirty_fixture``.
New dirty-backup fixtures should follow this template rather than adding
scenarios to the old monolithic generator.

Usage (preferred — all running SQL Server versions in one call)::

    .venv/bin/python -m tools.fixture_run all-versions --suite dirty-v4

Single version::

    .venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 dirty-v4

Direct (credentials already exported)::

    .venv/bin/python -m tools.make_dirty_v4_fixture [--force] [--only delete|update]
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

DB_NAME_DELETE = "DirtyV4Del"
DB_NAME_UPDATE = "DirtyV4Upd"

ROW_COUNT    = 5_000   # total rows inserted
DELETE_COUNT = 1_000   # ids 1..DELETE_COUNT are deleted in the dirty-delete fixture
UPDATE_COUNT = 1_000   # ids 1..UPDATE_COUNT are updated in the dirty-update fixture

EXPECTED_ROWS_AFTER_DELETE = ROW_COUNT - DELETE_COUNT   # 4 000
EXPECTED_ROWS_AFTER_UPDATE = ROW_COUNT                  # 5 000 (no rows removed)

# ids of rows that are deleted / updated (inclusive range)
DELETED_ID_LO  = 1
DELETED_ID_HI  = DELETE_COUNT
UPDATED_ID_LO  = 1
UPDATED_ID_HI  = UPDATE_COUNT

# column names present in dbo.dirty_v4 (imported by tests)
COLUMNS = [
    "id",
    "phase",
    "val_int",
    "val_str",
    "val_nstr",
    "val_float",
    "val_dt",
    "val_guid",
]

# ---------------------------------------------------------------------------
# Internal path constants
# ---------------------------------------------------------------------------

_BAK_DIR = "/var/opt/mssql/data"
_CONTAINER_BAK_DELETE = f"{_BAK_DIR}/dirtycoverage_committed_delete_v4.bak"
_CONTAINER_BAK_UPDATE = f"{_BAK_DIR}/dirtycoverage_committed_update_v4.bak"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

OUT_DELETE = FIXTURE_DIR / "dirtycoverage_committed_delete_v4.bak"
OUT_UPDATE = FIXTURE_DIR / "dirtycoverage_committed_update_v4.bak"


# ---------------------------------------------------------------------------
# SQL builders
# ---------------------------------------------------------------------------

def _setup_stmts(db_name: str, phase_label: str) -> list[str]:
    """Return DDL + DML statements that create the DB and populate ROW_COUNT rows.

    Does NOT include a BACKUP DATABASE statement — the dirty backup step is
    handled separately by ``_dirty_backup_concurrent``.
    """
    stmts: list[str] = [
        f"""IF DB_ID(N'{db_name}') IS NOT NULL BEGIN
  ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db_name}]
END""",
        f"CREATE DATABASE [{db_name}]",
        f"USE [{db_name}]",
    ]
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        """CREATE TABLE dbo.dirty_v4 (
    id         INT              NOT NULL PRIMARY KEY CLUSTERED,
    phase      VARCHAR(10)      NOT NULL,
    val_int    INT              NOT NULL,
    val_str    VARCHAR(100)     NOT NULL,
    val_nstr   NVARCHAR(100)    NOT NULL,
    val_float  FLOAT            NOT NULL,
    val_dt     DATETIME2(3)     NOT NULL,
    val_guid   UNIQUEIDENTIFIER NOT NULL
)""",
        f"""INSERT INTO dbo.dirty_v4 (id, phase, val_int, val_str, val_nstr, val_float, val_dt, val_guid)
SELECT
    pk + 1                                                                   AS id,
    CASE WHEN pk < {DELETE_COUNT} THEN '{phase_label}' ELSE 'keep' END      AS phase,
    (pk + 1) * 3                                                             AS val_int,
    'original_' + CAST(pk + 1 AS VARCHAR(10))                               AS val_str,
    N'row_' + CAST(pk + 1 AS NVARCHAR(10))                                  AS val_nstr,
    CAST(pk + 1 AS FLOAT) / 7.0                                             AS val_float,
    DATEADD(day, CAST(pk % 3650 AS INT), CAST('2000-01-01' AS DATETIME2(3))) AS val_dt,
    NEWID()                                                                  AS val_guid
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
    ]
    return stmts


def _reset_stmts_delete() -> list[str]:
    """Restore rows 1..DELETE_COUNT after they were deleted.

    Called before each retry attempt (idempotent: first deletes any leftover
    rows in that range, then re-inserts them).
    """
    return [
        f"DELETE FROM dbo.dirty_v4 WHERE id <= {DELETE_COUNT}",
        f"""INSERT INTO dbo.dirty_v4 (id, phase, val_int, val_str, val_nstr, val_float, val_dt, val_guid)
SELECT
    pk + 1,
    'delete',
    (pk + 1) * 3,
    'original_' + CAST(pk + 1 AS VARCHAR(10)),
    N'row_' + CAST(pk + 1 AS NVARCHAR(10)),
    CAST(pk + 1 AS FLOAT) / 7.0,
    DATEADD(day, CAST(pk % 3650 AS INT), CAST('2000-01-01' AS DATETIME2(3))),
    NEWID()
FROM fkr__seed
WHERE pk < {DELETE_COUNT}""",
    ]


def _reset_stmts_update() -> list[str]:
    """Restore val_str to 'original_N' for rows 1..UPDATE_COUNT (idempotent)."""
    return [
        f"UPDATE dbo.dirty_v4 SET val_str = 'original_' + CAST(id AS VARCHAR(10)) WHERE id <= {UPDATE_COUNT}",
    ]


def _dml_sql_delete() -> str:
    return f"DELETE FROM dbo.dirty_v4 WHERE id <= {DELETE_COUNT}"


def _dml_sql_update() -> str:
    return (
        f"UPDATE dbo.dirty_v4"
        f" SET val_str = 'updated_' + CAST(id AS VARCHAR(10))"
        f" WHERE id <= {UPDATE_COUNT}"
    )


# ---------------------------------------------------------------------------
# Per-fixture builders
# ---------------------------------------------------------------------------

def _build_delete(container: str, user: str, password: str, out: Path) -> None:
    print(
        f"\n=== V4 DELETE: committed_delete_slots guaranteed "
        f"({ROW_COUNT} rows → {EXPECTED_ROWS_AFTER_DELETE} surviving) ===",
        file=sys.stderr,
    )
    load_and_backup_stmts(container, user, password, _setup_stmts(DB_NAME_DELETE, "delete"))
    dirty_backup_concurrent(
        container, user, password,
        DB_NAME_DELETE, _CONTAINER_BAK_DELETE,
        _dml_sql_delete(), _reset_stmts_delete(),
        require_cds=True,
    )
    size = _copy_out(container, _CONTAINER_BAK_DELETE, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)


def _build_update(container: str, user: str, password: str, out: Path) -> None:
    print(
        f"\n=== V4 UPDATE: redo_patches guaranteed "
        f"({ROW_COUNT} rows, {UPDATE_COUNT} updated mid-backup) ===",
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
            "Generate dirtycoverage_committed_{delete,update}_v4.bak — "
            "V4 dirty backup fixtures with guaranteed committed_delete_slots / "
            "redo_patches using mssql_python + fkr__seed."
        )
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing .bak files")
    parser.add_argument(
        "--only",
        choices=["delete", "update"],
        help="build only one of the two fixtures (default: both)",
    )
    args = parser.parse_args()

    out_del = FIXTURE_DIR / "dirtycoverage_committed_delete_v4.bak"
    out_upd = FIXTURE_DIR / "dirtycoverage_committed_update_v4.bak"

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
