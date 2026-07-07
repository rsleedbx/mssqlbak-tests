#!/usr/bin/env python3
"""Generate ``spatial_index_full.bak`` — spatial index internal tessellation table (Gap E-4).

## Purpose

A spatial index creates an internal system-owned B-tree of ``(cell_id, pk)``
pairs for the tessellated grid.  This tessellation table has object type IT
(internal_table) in sysschobjs, not type U (user table).

Failure mode: same as E-3 (XML index) — if ``recover_schema`` enumerates the
internal tessellation table as a user table, it emits bogus rows and/or crashes
on the unusual record layout.

The fix is that ``recover_schema`` filters on ``sysschobjs.type == 'U'`` only.
This fixture proves the guarantee holds even with a spatial index present.

## Schema and data

``dbo.spatial_pts`` — 200-row geometry table with a spatial index.

    id   INT NOT NULL PRIMARY KEY
    loc  GEOMETRY NOT NULL    -- random POINT within a 1000×1000 grid
    name VARCHAR(20) NOT NULL

A SPATIAL INDEX (GEOMETRY_GRID) is created over ``loc``.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE``
  - ``ROW_COUNT``

Usage:
    python -m tools.fixture_run spatial-index
    python -m tools.fixture_run all-versions --suite spatial-index
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

DB_NAME = "SpatialIndex"
TABLE = "spatial_pts"
ROW_COUNT = 200

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "spatial_index_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
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
        f"""CREATE TABLE dbo.{TABLE} (
    id   INT          NOT NULL PRIMARY KEY CLUSTERED,
    loc  GEOMETRY     NOT NULL,
    name VARCHAR(20)  NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, loc, name)
SELECT
    pk + 1,
    geometry::STPointFromText(
        'POINT(' + CAST((pk * 137 + 50) % 1000 AS VARCHAR(10))
               + ' ' + CAST((pk * 251 + 75) % 1000 AS VARCHAR(10)) + ')',
        0),
    'pt_' + CAST(pk + 1 AS VARCHAR(10))
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Spatial index on geometry column (GEOMETRY_GRID tessellation)
        f"""CREATE SPATIAL INDEX si_{TABLE}
    ON dbo.{TABLE}(loc)
    WITH (
        BOUNDING_BOX = (0, 0, 1000, 1000),
        GRIDS = (MEDIUM, MEDIUM, MEDIUM, MEDIUM)
    )""",
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
    print(f"creating spatial index on {ROW_COUNT} geometry points …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
