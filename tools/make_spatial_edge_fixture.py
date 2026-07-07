#!/usr/bin/env python3
"""Generate ``spatial_edge_full.bak`` — spatial value edge cases."""
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
    skip_if_exists,
)

DB_NAME = "SpatialEdgeCells"
GEOMETRY_TABLE = "geometry_edge"
GEOGRAPHY_TABLE = "geography_edge"

EXPECTED_GEOMETRY: dict[int, str | None] = {
    1: "POINT (10 20)",
    2: "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))",
    3: "MULTIPOLYGON (((0 0, 2 0, 2 2, 0 2, 0 0)), ((5 5, 7 5, 7 7, 5 7, 5 5)))",
    4: None,
    5: "POINT (-122.408489591016 37.7605893030868)",
    6: "POINT (1 2 3 4)",
    7: "LINESTRING (0 0, 1 1, 2 1)",
    8: "GEOMETRYCOLLECTION (POINT (1 2), LINESTRING (0 0, 1 1))",
    9: "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1))",
}
EXPECTED_GEOGRAPHY: dict[int, str | None] = {
    1: "POINT (-122.349 47.651)",
    2: "POLYGON ((-122 47, -121 47, -121 48, -122 48, -122 47))",
    3: "FULLGLOBE",
    4: None,
    5: "POINT (-122.408489591016 37.7605893030868)",
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "spatial_edge_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    geometry_rows = ",\n    ".join(
        f"({row_id}, {_geometry_sql(wkt)})"
        for row_id, wkt in EXPECTED_GEOMETRY.items()
    )
    geography_rows = ",\n    ".join(
        f"({row_id}, {_geography_sql(row_id, wkt)})"
        for row_id, wkt in EXPECTED_GEOGRAPHY.items()
    )
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{GEOMETRY_TABLE} (
    id    INT      NOT NULL PRIMARY KEY CLUSTERED,
    shape geometry NULL
)""",
        f"""INSERT INTO dbo.{GEOMETRY_TABLE} (id, shape) VALUES
    {geometry_rows}""",
        f"""CREATE TABLE dbo.{GEOGRAPHY_TABLE} (
    id    INT       NOT NULL PRIMARY KEY CLUSTERED,
    shape geography NULL
)""",
        f"""INSERT INTO dbo.{GEOGRAPHY_TABLE} (id, shape) VALUES
    {geography_rows}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def _geometry_sql(wkt: str | None) -> str:
    if wkt is None:
        return "NULL"
    return f"geometry::STGeomFromText({_str_sql(wkt)}, 0)"


def _geography_sql(row_id: int, wkt: str | None) -> str:
    if wkt is None:
        return "NULL"
    if wkt == "FULLGLOBE":
        return "geography::STGeomFromText(N'FULLGLOBE', 4326)"
    # SQL Server geography input uses latitude/longitude order for points.
    if row_id == 1:
        return "geography::Point(47.651, -122.349, 4326)"
    if row_id == 5:
        return "geography::Point(37.7605893030868, -122.408489591016, 4326)"
    return f"geography::STGeomFromText({_str_sql(wkt)}, 4326)"


def _str_sql(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print("inserting spatial edge rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
