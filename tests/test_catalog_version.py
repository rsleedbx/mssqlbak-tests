"""Catalog version-matrix fixture tests (G21)."""

from __future__ import annotations

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tests.conftest import FIXTURE_BAK_CATALOG_SS


@pytest.mark.fixture
@pytest.mark.parametrize("year", ("2012", "2016", "2019", "2022"))
def test_catalog_probe_table_recovered(year: str) -> None:
    path = FIXTURE_BAK_CATALOG_SS[year]
    if not path.exists():
        pytest.skip(f"{path.name} missing; run python -m tools.make_catalog_fixture --engine {year}")
    store = PageStore.from_bak(path)
    table = next((t for t in recover_schema(store).tables if t.name == "cat_probe"), None)
    assert table is not None
    rows = list(read_table_rows(store, table))
    assert len(rows) == 3
