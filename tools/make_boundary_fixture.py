#!/usr/bin/env python3
"""Build the boundary-value columnstore fixture.

Creates ``BoundaryCoverage`` — one table per BoundaryCase, each with:
  - N_LABELED boundary rows (min, max, sec_min, sec_max, zero/mid, null)
  - N_FILLER filler rows generated via a recursive CTE

Total 1200 rows per table forces SQL Server to use enc=4 compression in the
clustered columnstore index, exercising the enc=4 null-sentinel code path for
bigint and money (where mn == INT64_MIN).

Connection: same env vars as make_fixture.py.
  FIXTURE_DBA_PASSWORD  (required)
  FIXTURE_DBA_USER      (default: sa)
  FIXTURE_CONTAINER     (optional override for podman container name)

Usage::

    python tools/make_boundary_fixture.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_fixture import (  # noqa: E402
    _copy_out,
    _load_and_backup,
    discover_container,
    sql_literal,
    sqlcmd_base,
)
from tools.boundary_matrix import BOUNDARY_CASES, N_FILLER  # noqa: E402

DB_NAME = "BoundaryCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures"))) / "boundarycoverage_full.bak"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME}.sql"


def _tbl(case_name: str) -> str:
    return f"tb_{case_name}"


def build_sql() -> str:
    """Assemble the full create/insert script for the boundary fixture."""
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
    ]

    for case in BOUNDARY_CASES:
        tbl = _tbl(case.name)

        # 1. Create heap table (no index yet — rows inserted into delta store
        #    after CCI is created, then flushed via REORGANIZE).
        parts += [
            f"CREATE TABLE [{tbl}] (\n"
            f"    id    INT IDENTITY(1,1) NOT NULL,\n"
            f"    label VARCHAR(10) NULL,\n"
            f"    v     {case.sql_type} NULL\n"
            f");",
            "GO",
        ]

        # 2. Add the clustered columnstore index while the table is empty.
        #    Subsequent INSERTs go to the delta store; REORGANIZE flushes them.
        parts += [
            f"CREATE CLUSTERED COLUMNSTORE INDEX [cci_{tbl}] ON [{tbl}];",
            "GO",
        ]

        # 3. Insert the N_LABELED labeled boundary rows.
        for row in case.rows:
            v_lit = sql_literal(row.value) if row.value is not None else "NULL"
            parts.append(
                f"INSERT INTO [{tbl}] (label, v) VALUES ({sql_literal(row.label)}, {v_lit});"
            )
        parts.append("GO")

        # 4. Insert N_FILLER filler rows via a recursive CTE.
        #    Values are sequential small integers — different from the labeled
        #    boundary values so they don't corrupt label-based lookups.
        #    MAXRECURSION must equal N_FILLER; 0 would also work but is less safe.
        parts += [
            f"WITH n(n) AS (\n"
            f"    SELECT 1 UNION ALL SELECT n + 1 FROM n WHERE n < {N_FILLER}\n"
            f")\n"
            f"INSERT INTO [{tbl}] (label, v)\n"
            f"SELECT NULL, {case.filler_sql} FROM n\n"
            f"OPTION (MAXRECURSION {N_FILLER});",
            "GO",
        ]

        # 5. Force delta-store rows into compressed column segments.
        #    Without this step a small table (<102 400 rows) stays in the
        #    delta store (B-tree pages) and the columnstore decoder never
        #    sees a compressed segment blob in the .bak.
        parts += [
            f"ALTER INDEX [cci_{tbl}] ON [{tbl}]"
            f" REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);",
            "GO",
        ]

    return "\n".join(parts) + "\n"


def main() -> int:
    if OUT_PATH.exists():
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

    sql = (
        build_sql()
        + "USE [master];\nGO\n"
        + f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}'"
        + " WITH FORMAT, INIT, COPY_ONLY;\nGO\n"
    )
    _load_and_backup(container, sqlcmd_base(user, password, container), sql, CONTAINER_SQL)
    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
