from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon
from tools.make_float_extreme_fixture import EXPECTED_ROWS, TABLE


def _rows(fixture: Path) -> dict[int, dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == TABLE), None)
    if table is None:
        pytest.fail(f"Table {TABLE!r} not found")
    return {int(row["id"]): row for row in read_table_rows(store, table)}


def test_float_extreme_values(fixture_bak_float_extreme: Path) -> None:
    rows = _rows(fixture_bak_float_extreme)
    assert set(rows) == set(EXPECTED_ROWS)
    for row_id, expected in EXPECTED_ROWS.items():
        assert canon(rows[row_id]["f64"], "float") == canon(expected["f64"], "float")
        assert canon(rows[row_id]["f32"], "real") == canon(expected["f32"], "real")
