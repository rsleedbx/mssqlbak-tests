#!/usr/bin/env python3
"""Build the table-organization coverage fixtures from the wide-column matrix.

Generates two ``.bak`` files:

    tests/fixtures/tabletypecoverage_full.bak
        Full backup of the ``TabletypeCoverage`` database.  Contains five
        tables (tt_plain, tt_heap, tt_cluster, tt_partition, tt_column) each
        with one column per TYPE_CASE (minus columnstore-incompatible types for
        tt_column).  Four rows per table: id=1 low, 2 high, 3 mid, 4 null.

    tests/fixtures/tabletypecoverage_diff.bak
        Differential backup taken after inserting two extra rows (id=5 and
        id=6) into every table.  Used to validate the base-merge path once
        differential restores are implemented (currently PLANNED).

Connection: same as make_fixture.py — set ``FIXTURE_DBA_PASSWORD`` and ensure
a SQL Server container is reachable via ``podman ps``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_fixture import (  # noqa: E402
    discover_container,
    sql_literal,
    sqlcmd_base,
    _load_and_backup,
    _copy_out,
)
from tools.fixture_utils import seed_sql  # noqa: E402
from tools.tabletypematrix import (  # noqa: E402
    LABEL_ID,
    LABELS,
    ORG_CASES,
    OrgCase,
    _cols_ddl,
    supported_cases,
    table_name,
)

DB_NAME = "TabletypeCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

# Structural rows: low / high / mid / null.  Always present regardless of --rows.
DEFAULT_ROWS = 4

CONTAINER_BAK_FULL = f"/tmp/{DB_NAME}_full.bak"
CONTAINER_BAK_DIFF = f"/tmp/{DB_NAME}_diff.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME}.sql"


def _out_paths(rows: int) -> tuple[Path, Path]:
    """Return (full_bak, diff_bak) paths for *rows* total rows per table.

    ``DEFAULT_ROWS`` (4) → stable names used by tests.
    Any other count  → names with the row count suffix to avoid overwriting.
    """
    if rows == DEFAULT_ROWS:
        return (
            FIXTURE_DIR / "tabletypecoverage_full.bak",
            FIXTURE_DIR / "tabletypecoverage_diff.bak",
        )
    return (
        FIXTURE_DIR / f"tabletypecoverage_full_{rows}.bak",
        FIXTURE_DIR / f"tabletypecoverage_diff_{rows}.bak",
    )


# ---------------------------------------------------------------------------
# Reference value lookup
# ---------------------------------------------------------------------------
def _value_for(case_name: str, label: str) -> Any:
    """Return the reference Python value for a given type case and row label."""
    from tools.typematrix import TYPE_CASES as _TC  # local import to avoid re-export confusion
    for case in _TC:
        if case.name == case_name:
            for row in case.rows:
                if row.label == label:
                    return row.value
    return None


def _sql_for(case_name: str, label: str) -> str:
    """Return the SQL literal override (if any) or the auto-rendered literal."""
    from tools.typematrix import TYPE_CASES as _TC
    for case in _TC:
        if case.name == case_name:
            for row in case.rows:
                if row.label == label:
                    if row.sql is not None:
                        return row.sql
                    return sql_literal(row.value)
    return "NULL"


# ---------------------------------------------------------------------------
# DDL helpers
# ---------------------------------------------------------------------------
def _partition_ddl() -> str:
    """Partition function + scheme for the tt_partition table."""
    return (
        "CREATE PARTITION FUNCTION pf_tt_id (int) AS RANGE LEFT FOR VALUES (5);\n"
        "GO\n"
        "CREATE PARTITION SCHEME ps_tt_id AS PARTITION pf_tt_id ALL TO ([PRIMARY]);\n"
        "GO\n"
    )


def _create_table(org: OrgCase) -> str:
    """Emit the CREATE TABLE (and post-create index) SQL for one org."""
    tbl = table_name(org)
    cols = _cols_ddl(org.skip_types)
    ddl = org.create_ddl.format(tbl=tbl, cols=cols)
    if org.post_create_ddl:
        post = org.post_create_ddl.format(tbl=tbl)
        ddl = f"{ddl}\nGO\n{post}"
    return ddl


def _insert_rows(org: OrgCase, labels: list[str] | None = None) -> str:
    """Emit INSERT statements for the given row labels."""
    tbl = table_name(org)
    cases = supported_cases(org)
    parts: list[str] = []
    for label in (labels or LABELS):
        row_id = LABEL_ID[label]
        col_names = ["id"] + [
            f"c_{c.name}" for c in cases if not c.auto
        ]
        col_vals = [str(row_id)] + [_sql_for(c.name, label) for c in cases if not c.auto]
        parts.append(
            f"INSERT INTO [{tbl}] ({', '.join(col_names)})\n"
            f"VALUES ({', '.join(col_vals)});"
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Full SQL script
# ---------------------------------------------------------------------------
def _insert_filler_rows(org: OrgCase, extra_rows: int) -> str:
    """Insert *extra_rows* scale-filler rows using only the ``id`` column.

    All type columns are nullable, so omitting them is valid.  Row IDs start
    at 7: ids 1-4 are the structural rows; 5-6 are reserved for the diff-backup
    rows inserted by ``build_diff_sql``.
    """
    tbl = table_name(org)
    return f"INSERT INTO [{tbl}] (id) SELECT CAST(pk + 7 AS INT) FROM fkr__seed WHERE pk < {extra_rows};"


def build_full_sql(rows: int = DEFAULT_ROWS) -> str:
    """Assemble the create/insert script for the full backup.

    *rows* controls the total number of rows per table.  The four structural
    rows (low/high/mid/null) are always generated; any excess beyond
    ``DEFAULT_ROWS`` is filled with id-only NULL rows for IAM-scale testing.
    """
    extra_rows = rows - DEFAULT_ROWS
    parts: list[str] = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
        _partition_ddl(),
    ]
    if extra_rows > 0:
        for stmt in seed_sql(extra_rows):
            parts.append(stmt + ";")
            parts.append("GO")
    for org in ORG_CASES:
        parts.append(_create_table(org))
        parts.append("GO")
        parts.append(_insert_rows(org))
        parts.append("GO")
        if extra_rows > 0:
            parts.append(_insert_filler_rows(org, extra_rows))
            parts.append("GO")
        if org.post_create_ddl:
            # Force all delta-store rows into compressed row groups so that
            # the mssqlbak columnstore decoder finds segment blobs in the .bak.
            # Without this, a small table (<102400 rows) stays in the delta
            # store (B-tree pages), not in LOB segment blobs.
            tbl = table_name(org)
            # Index name is "cci_{tbl}" from post_create_ddl pattern.
            parts.append(
                f"ALTER INDEX [cci_{tbl}] ON [{tbl}] "
                "REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);"
            )
            parts.append("GO")
    return "\n".join(parts) + "\n"


def build_diff_sql() -> str:
    """Insert two extra rows (id=5 'extra', id=6 'extra2') into every table.

    Called after the full backup; makes pages dirty so the differential
    backup captures them.  Uses the 'low' and 'high' row values as the extra
    row payloads (just different id values, same data).
    """
    parts: list[str] = [f"USE [{DB_NAME}];", "GO"]
    for org in ORG_CASES:
        tbl = table_name(org)
        cases = supported_cases(org)
        for extra_id, src_label in [(5, "low"), (6, "high")]:
            col_names = ["id"] + [f"c_{c.name}" for c in cases if not c.auto]
            col_vals = [str(extra_id)] + [_sql_for(c.name, src_label) for c in cases if not c.auto]
            parts.append(
                f"INSERT INTO [{tbl}] ({', '.join(col_names)})\n"
                f"VALUES ({', '.join(col_vals)});"
            )
        parts.append("GO")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        metavar="N",
        help=(
            f"total rows per table (default: {DEFAULT_ROWS}). "
            "The 4 type-coverage rows (low/high/mid/null) are always included; "
            "extra rows use only the id column (all type columns NULL) for "
            "IAM-scale testing.  Use --rows 50000 to reproduce the IAM "
            "traversal bug across all table organisations."
        ),
    )
    args = p.parse_args()
    rows = max(args.rows, DEFAULT_ROWS)

    out_full, out_diff = _out_paths(rows)
    if out_full.exists() and out_diff.exists():
        print(f"skip (already exists): {out_full.name}, {out_diff.name}", file=sys.stderr)
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

    # --- full backup --------------------------------------------------------
    # Not COPY_ONLY so the differential can reference this as the base.
    full_sql = (
        build_full_sql(rows)
        + "USE [master];\nGO\n"
        + f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK_FULL}'"
        + " WITH FORMAT, INIT;\nGO\n"
    )
    _load_and_backup(container, sqlcmd, full_sql, CONTAINER_SQL)
    size = _copy_out(container, CONTAINER_BAK_FULL, out_full)
    print(f"wrote {out_full} ({size:,} bytes)")

    # --- differential backup (after inserting extra rows) -------------------
    diff_sql = (
        build_diff_sql()
        + "USE [master];\nGO\n"
        + f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK_DIFF}'"
        + " WITH FORMAT, INIT, DIFFERENTIAL;\nGO\n"
    )
    _load_and_backup(container, sqlcmd, diff_sql, CONTAINER_SQL)
    size = _copy_out(container, CONTAINER_BAK_DIFF, out_diff)
    print(f"wrote {out_diff} ({size:,} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
