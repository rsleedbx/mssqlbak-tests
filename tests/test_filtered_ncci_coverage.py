"""Gap C-4: Filtered NCCI coverage tests.

A filtered NONCLUSTERED COLUMNSTORE INDEX covers only the rows matching its
WHERE predicate.  mssqlbak reads from the base table (clustered index or heap)
and must return all rows regardless of the NCCI filter.

The fixture has:
  - dbo.filtered_ncci_base: clustered table, 400 rows, NCCI WHERE active=1 (200 rows)
  - dbo.filtered_ncci_heap: heap table, 400 rows, NCCI WHERE active=1 (200 rows)

Both must return 400 rows (not 200).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_filtered_ncci_fixture import (
    ROW_COUNT,
    TABLE_CLUSTERED,
    TABLE_HEAP,
)


def _get_rows(fixture: Path, table_name: str) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == table_name), None)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in fixture")
    return list(read_table_rows(store, tbl))


@pytest.mark.parametrize("table", [TABLE_CLUSTERED, TABLE_HEAP])
def test_filtered_ncci_all_rows_returned(fixture_bak_filtered_ncci, table):
    """All base-table rows must be present despite the NCCI covering only half."""
    rows = _get_rows(fixture_bak_filtered_ncci, table)
    assert len(rows) == ROW_COUNT, (
        f"{table}: expected {ROW_COUNT} rows but got {len(rows)}; "
        "NCCI filter may be capping row count"
    )


@pytest.mark.parametrize("table", [TABLE_CLUSTERED, TABLE_HEAP])
def test_filtered_ncci_active_column_values(fixture_bak_filtered_ncci, table):
    """Both active=0 and active=1 rows must be present (not just the NCCI subset)."""
    rows = _get_rows(fixture_bak_filtered_ncci, table)
    active_vals = {bool(r["active"]) for r in rows}
    assert True in active_vals, f"{table}: active=1 rows missing"
    assert False in active_vals, f"{table}: active=0 rows missing (NCCI filter applied to base)"


@pytest.mark.parametrize("table", [TABLE_CLUSTERED, TABLE_HEAP])
def test_filtered_ncci_no_duplicates(fixture_bak_filtered_ncci, table):
    """No row should be returned twice."""
    rows = _get_rows(fixture_bak_filtered_ncci, table)
    ids = [r["id"] for r in rows]
    dups = sorted(set(x for x in ids if ids.count(x) > 1))
    assert not dups, f"{table}: duplicate IDs — {dups}"


def test_filtered_ncci_spot_check_values(fixture_bak_filtered_ncci):
    """Spot-check specific rows: id=1 (active=1) and id=201 (active=0)."""
    rows = _get_rows(fixture_bak_filtered_ncci, TABLE_CLUSTERED)
    rows_by_id = {r["id"]: r for r in rows}
    row1 = rows_by_id.get(1)
    assert row1 is not None, "id=1 missing"
    assert row1["val"] == 7, f"id=1 val expected 7, got {row1['val']}"
    assert bool(row1["active"]) is True
    row201 = rows_by_id.get(201)
    assert row201 is not None, "id=201 missing"
    assert bool(row201["active"]) is False
