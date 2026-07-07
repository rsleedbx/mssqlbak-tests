"""Spatial edge cell coverage.

The existing spatial-index fixture checks only that geometry values are
non-null.  This fixture checks concrete WKT output for geometry and geography
edge shapes seen in real-world cell failures.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon
from tools.make_spatial_edge_fixture import (
    EXPECTED_GEOGRAPHY,
    EXPECTED_GEOMETRY,
    GEOGRAPHY_TABLE,
    GEOMETRY_TABLE,
)

GEOMETRY_SENTINELS: dict[int, str] = {
    5: "POINT (-122.408489591016 37.7605893030868)",
    6: "POINT (1 2 3 4)",
    7: "LINESTRING (0 0, 1 1, 2 1)",
    8: "GEOMETRYCOLLECTION (POINT (1 2), LINESTRING (0 0, 1 1))",
    9: "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1))",
}

GEOGRAPHY_SENTINELS: dict[int, str] = {
    5: "POINT (-122.408489591016 37.7605893030868)",
}


def _rows(fixture: Path, table_name: str) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == table_name), None)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in fixture")
    return list(read_table_rows(store, tbl))


def test_spatial_edge_geometry_values(fixture_bak_spatial_edge: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_spatial_edge, GEOMETRY_TABLE)}
    assert set(rows_by_id) == set(EXPECTED_GEOMETRY)
    for row_id, expected_wkt in EXPECTED_GEOMETRY.items():
        assert canon(rows_by_id[row_id]["shape"], "geometry") == canon(expected_wkt, "geometry")


def test_spatial_edge_geography_values(fixture_bak_spatial_edge: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_spatial_edge, GEOGRAPHY_TABLE)}
    assert set(rows_by_id) == set(EXPECTED_GEOGRAPHY)
    for row_id, expected_wkt in EXPECTED_GEOGRAPHY.items():
        assert canon(rows_by_id[row_id]["shape"], "geography") == canon(expected_wkt, "geography")


def test_spatial_edge_sentinel_shapes(fixture_bak_spatial_edge: Path) -> None:
    geometry = {r["id"]: r for r in _rows(fixture_bak_spatial_edge, GEOMETRY_TABLE)}
    geography = {r["id"]: r for r in _rows(fixture_bak_spatial_edge, GEOGRAPHY_TABLE)}

    for row_id, expected_wkt in GEOMETRY_SENTINELS.items():
        assert canon(geometry[row_id]["shape"], "geometry") == canon(expected_wkt, "geometry")
    for row_id, expected_wkt in GEOGRAPHY_SENTINELS.items():
        assert canon(geography[row_id]["shape"], "geography") == canon(expected_wkt, "geography")
