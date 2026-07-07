"""Gap C-11: Non-persisted computed columns in CCI — coverage tests.

A CCI table may have non-persisted computed columns added via ALTER TABLE after
the CCI is established.  SQL Server prohibits persisted computed columns on CCI
tables entirely.  Non-persisted computed columns have no segment storage; they
are computed at query time from stored values.

mssqlbak must not crash trying to find a segment for `val_label` (non-persisted),
and must correctly return the stored columns (id, val, grp).

Fixture: dbo.cci_computed — 1,200 rows.
  - id, val, grp  — stored in CCI segments
  - val_label AS ('lbl_' + CAST(val AS VARCHAR(10)))  — NOT stored (non-persisted)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_computed_fixture import (
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


def test_cci_computed_row_count(fixture_bak_cci_computed):
    """All 1,200 rows must be returned from the CCI segments."""
    rows = _get_rows(fixture_bak_cci_computed)
    assert len(rows) == ROW_COUNT, f"expected {ROW_COUNT} rows, got {len(rows)}"


def test_cci_computed_stored_columns_correct(fixture_bak_cci_computed):
    """Stored columns (id, val, grp) must be present in every row."""
    rows = _get_rows(fixture_bak_cci_computed)
    for r in rows:
        assert "id" in r, f"id missing from row {r}"
        assert "val" in r, f"val missing from row {r}"
        assert "grp" in r, f"grp missing from row {r}"


def test_cci_computed_no_duplicates(fixture_bak_cci_computed):
    """No duplicate rows."""
    rows = _get_rows(fixture_bak_cci_computed)
    ids = [r["id"] for r in rows]
    dups = sorted(set(x for x in ids if ids.count(x) > 1))
    assert not dups, f"duplicate IDs: {dups}"


def test_cci_computed_spot_check(fixture_bak_cci_computed):
    """Spot-check id=1: val = 1*3 = 3, grp = (0 % 10) + 1 = 1."""
    rows = _get_rows(fixture_bak_cci_computed)
    rows_by_id = {r["id"]: r for r in rows}
    row = rows_by_id.get(1)
    assert row is not None, "id=1 missing"
    assert row["val"] == 3, f"id=1 val expected 3, got {row['val']}"
    assert row["grp"] == 1, f"id=1 grp expected 1, got {row['grp']}"
