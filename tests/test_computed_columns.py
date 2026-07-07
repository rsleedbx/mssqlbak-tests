"""Computed-column handling: non-persisted excluded, persisted included.

A non-persisted computed column appears in syscolpars but has no sysrscols row
(no physical storage); it must be dropped from the record layout, otherwise it
shifts every later column's offset.  A persisted computed column is stored and
must be surfaced with its correct value.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.computedmatrix import CASES, expected_rows, stored_columns, table_name


@pytest.mark.fixture
def test_computed_columns_layout_and_rows(fixture_bak_computed: Path) -> None:
    store = PageStore.from_bak(fixture_bak_computed)
    by_name = {t.name: t for t in recover_schema(store).tables}
    for case in CASES:
        table = by_name[table_name(case)]
        got_cols = [c.name for c in table.columns]
        assert got_cols == stored_columns(case), (
            f"{table.name}: column layout mismatch (computed column not handled)"
        )
        rows = [{k: r[k] for k in stored_columns(case)} for r in read_table_rows(store, table)]
        assert rows == expected_rows(case), table.name


@pytest.mark.fixture
def test_nonpersisted_computed_column_dropped(fixture_bak_computed: Path) -> None:
    """The non-persisted computed column 'total' must not appear at all."""
    store = PageStore.from_bak(fixture_bak_computed)
    by_name = {t.name: t for t in recover_schema(store).tables}
    nonpersisted = by_name["comp_nonpersisted"]
    assert "total" not in {c.name for c in nonpersisted.columns}
    # the persisted variant keeps it
    persisted = by_name["comp_persisted"]
    assert "total" in {c.name for c in persisted.columns}
