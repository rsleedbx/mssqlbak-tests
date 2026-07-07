"""Gap C-5: NCCI on heap coverage tests.

A NONCLUSTERED COLUMNSTORE INDEX on a heap uses a RID (file:page:slot) locator
rather than a clustered-key pointer.  mssqlbak reads from the heap IAM chain,
not the NCCI.  The RID-locator column stored alongside each NCCI segment value
must not contaminate data extraction.

Fixture: dbo.ncci_heap — 400 rows (id INT, val INT, name VARCHAR(30)) with
an NCCI on (id, val).  Rows are compressed with REORGANIZE.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_ncci_heap_fixture import (
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


def test_ncci_heap_row_count(fixture_bak_ncci_heap):
    """All heap rows must be returned, not just NCCI segment rows."""
    rows = _get_rows(fixture_bak_ncci_heap)
    assert len(rows) == ROW_COUNT, f"expected {ROW_COUNT} rows, got {len(rows)}"


def test_ncci_heap_column_names(fixture_bak_ncci_heap):
    """Row dicts must contain only the declared columns (no spurious RID column)."""
    rows = _get_rows(fixture_bak_ncci_heap)
    assert rows, "no rows"
    cols = set(rows[0].keys())
    assert "id" in cols
    assert "val" in cols
    assert "name" in cols
    extra = cols - {"id", "val", "name"}
    assert not extra, f"unexpected extra columns: {extra}"


def test_ncci_heap_no_duplicates(fixture_bak_ncci_heap):
    """No row should be emitted more than once."""
    rows = _get_rows(fixture_bak_ncci_heap)
    ids = [r["id"] for r in rows]
    dups = sorted(set(x for x in ids if ids.count(x) > 1))
    assert not dups, f"duplicate IDs: {dups}"


def test_ncci_heap_spot_check(fixture_bak_ncci_heap):
    """Spot-check row id=1: val = 1 * 13 = 13, name = 'row_1'."""
    rows = _get_rows(fixture_bak_ncci_heap)
    rows_by_id = {r["id"]: r for r in rows}
    row = rows_by_id.get(1)
    assert row is not None, "id=1 missing"
    assert row["val"] == 13, f"id=1 val expected 13, got {row['val']}"
    assert row["name"] == "row_1", f"id=1 name expected 'row_1', got {row['name']!r}"
