"""Gap C-12: CCI + rowstore B-tree NC indexes on same table — coverage tests.

A table can have a CLUSTERED COLUMNSTORE INDEX as primary storage and one or
more regular B-tree NONCLUSTERED indexes alongside it.  The B-tree NC index
pages have a different on-disk format from CCI segment pages.

mssqlbak must read only from the CCI segments and must not:
  - Mis-route B-tree NC index pages through the CCI segment decoder.
  - Count B-tree index entries as extra CCI rows (double-count).
  - Miss any CCI rows because it avoids pages shared with NC indexes.

Fixture: dbo.cci_with_btree — 1,200 rows (id, code, name, val) with:
  - INDEX cci CLUSTERED COLUMNSTORE
  - NONCLUSTERED INDEX ix_code ON (code)
  - NONCLUSTERED INDEX ix_name ON (name)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_btree_nci_fixture import (
    ROW_COUNT,
    TABLE,
)


def _get_rows(fixture: Path) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return list(read_table_rows(store, tbl))


def test_cci_btree_nci_row_count(fixture_bak_cci_btree_nci):
    """All 1,200 CCI rows must be returned, no more, no less."""
    rows = _get_rows(fixture_bak_cci_btree_nci)
    assert len(rows) == ROW_COUNT, f"expected {ROW_COUNT} rows, got {len(rows)}"


def test_cci_btree_nci_column_names(fixture_bak_cci_btree_nci):
    """Row dicts must contain exactly the declared columns (no NC key leakage)."""
    rows = _get_rows(fixture_bak_cci_btree_nci)
    assert rows, "no rows"
    expected = {"id", "code", "name", "val"}
    actual = set(rows[0].keys())
    assert actual == expected, f"unexpected columns: {actual.symmetric_difference(expected)}"


def test_cci_btree_nci_no_duplicates(fixture_bak_cci_btree_nci):
    """No row should appear twice (B-tree NC pages must not add phantom rows)."""
    rows = _get_rows(fixture_bak_cci_btree_nci)
    ids = [r["id"] for r in rows]
    dups = sorted(set(x for x in ids if ids.count(x) > 1))
    assert not dups, f"duplicate IDs: {dups}"


def test_cci_btree_nci_spot_check(fixture_bak_cci_btree_nci):
    """Spot-check row id=1: code = 1 % 100 = 1, val = 1*5 = 5."""
    rows = _get_rows(fixture_bak_cci_btree_nci)
    rows_by_id = {r["id"]: r for r in rows}
    row = rows_by_id.get(1)
    assert row is not None, "id=1 missing"
    assert row["code"] == 1, f"id=1 code expected 1, got {row['code']}"
    assert row["val"] == 5, f"id=1 val expected 5, got {row['val']}"
    assert row["name"] == "item_1", f"id=1 name expected 'item_1', got {row['name']!r}"
