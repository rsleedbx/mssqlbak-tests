"""Gap C-7: Ordered CCI (SS2022+ ORDER clause) — coverage tests.

SQL Server 2022 introduced the ORDER clause for CREATE CLUSTERED COLUMNSTORE
INDEX.  An ordered CCI pre-sorts rows by the specified key columns before
compression.  The on-disk segment format is identical to a regular CCI; only
the row ordering within each rowgroup and the segment min/max metadata differ.

mssqlbak must:
  1. Return all rows from both the ordered and regular CCI tables.
  2. Return correct column values regardless of the ORDER clause.
  3. Not crash or misread the potentially tighter min/max metadata.

Fixture (SS2022+): two tables each with 1,200 rows:
  - dbo.ordered_cci  — CCI with ORDER (id)
  - dbo.regular_cci  — CCI without ORDER (baseline comparison)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_ordered_cci_fixture import (
    ROW_COUNT,
    TABLE_ORDERED,
    TABLE_REGULAR,
)


def _get_rows(fixture: Path, table_name: str) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == table_name), None)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in fixture")
    return list(read_table_rows(store, tbl))


@pytest.mark.parametrize("table", [TABLE_ORDERED, TABLE_REGULAR])
def test_ordered_cci_row_count(fixture_bak_ordered_cci, table):
    """All 1,200 rows must be returned from both the ordered and regular CCI."""
    rows = _get_rows(fixture_bak_ordered_cci, table)
    assert len(rows) == ROW_COUNT, f"{table}: expected {ROW_COUNT} rows, got {len(rows)}"


@pytest.mark.parametrize("table", [TABLE_ORDERED, TABLE_REGULAR])
def test_ordered_cci_no_duplicates(fixture_bak_ordered_cci, table):
    """No duplicate IDs from either table."""
    rows = _get_rows(fixture_bak_ordered_cci, table)
    ids = [r["id"] for r in rows]
    dups = sorted(set(x for x in ids if ids.count(x) > 1))
    assert not dups, f"{table}: duplicate IDs: {dups}"


@pytest.mark.parametrize("table", [TABLE_ORDERED, TABLE_REGULAR])
def test_ordered_cci_all_ids_present(fixture_bak_ordered_cci, table):
    """IDs 1..1200 must all be present in both tables."""
    rows = _get_rows(fixture_bak_ordered_cci, table)
    ids = {r["id"] for r in rows}
    expected = set(range(1, ROW_COUNT + 1))
    missing = expected - ids
    assert not missing, f"{table}: missing IDs: {sorted(missing)[:20]}"


@pytest.mark.parametrize("table", [TABLE_ORDERED, TABLE_REGULAR])
def test_ordered_cci_spot_check(fixture_bak_ordered_cci, table):
    """Spot-check id=1: val = 1*7 = 7, grp = (0 % 10) + 1 = 1."""
    rows = _get_rows(fixture_bak_ordered_cci, table)
    rows_by_id = {r["id"]: r for r in rows}
    row = rows_by_id.get(1)
    assert row is not None, f"{table}: id=1 missing"
    assert row["val"] == 7, f"{table}: id=1 val expected 7, got {row['val']}"
    assert row["grp"] == 1, f"{table}: id=1 grp expected 1, got {row['grp']}"
