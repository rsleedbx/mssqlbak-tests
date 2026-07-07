from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon
from tools.make_realworld_numeric_digest_fixture import EXPECTED_ROWS, TABLES


def _table_rows(fixture: Path, table_name: str) -> dict[int, dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        pytest.fail(f"Table {table_name!r} not found")
    return {int(row["id"]): row for row in read_table_rows(store, table)}


@pytest.mark.parametrize("table_name", TABLES)
def test_realworld_numeric_digest_values(
    fixture_bak_realworld_numeric_digest: Path,
    table_name: str,
) -> None:
    rows = _table_rows(fixture_bak_realworld_numeric_digest, table_name)
    assert set(rows) == set(EXPECTED_ROWS)
    for row_id, expected in EXPECTED_ROWS.items():
        actual = rows[row_id]
        assert canon(actual["pickup_longitude"], "float") == canon(expected["pickup_longitude"], "float")
        assert canon(actual["pickup_latitude"], "float") == canon(expected["pickup_latitude"], "float")
        assert canon(actual["tax_rate"], "decimal") == canon(expected["tax_rate"], "decimal")
        assert canon(actual["resource_cost"], "money") == canon(expected["resource_cost"], "money")
        assert actual["tipped"] == expected["tipped"]
        assert actual["supplier_key"] == expected["supplier_key"]
