"""Gap D-3: rowversion / timestamp column extraction tests.

``rowversion`` is a fixed 8-byte big-endian binary auto-incremented on every
row modification.  mssqlbak should surface it as a ``bytes`` object of length 8.

Fixture: dbo.rv_tbl — 100 rows (id INT, label VARCHAR(30), rv rowversion).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_rowversion_extract_fixture import (
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


def test_rowversion_row_count(fixture_bak_rowversion_extract):
    """All 100 rows must be returned."""
    rows = _get_rows(fixture_bak_rowversion_extract)
    assert len(rows) == ROW_COUNT, f"expected {ROW_COUNT} rows, got {len(rows)}"


def test_rowversion_is_bytes(fixture_bak_rowversion_extract):
    """The rv column must be returned as bytes, not int or str."""
    rows = _get_rows(fixture_bak_rowversion_extract)
    non_bytes = [(r["id"], type(r["rv"])) for r in rows if not isinstance(r["rv"], (bytes, bytearray))]
    assert not non_bytes, f"rv not bytes for ids: {non_bytes[:5]}"


def test_rowversion_length_8(fixture_bak_rowversion_extract):
    """Each rowversion value must be exactly 8 bytes."""
    rows = _get_rows(fixture_bak_rowversion_extract)
    wrong_len = [(r["id"], len(r["rv"])) for r in rows if len(bytes(r["rv"])) != 8]
    assert not wrong_len, f"rv wrong length for ids: {wrong_len[:5]}"


def test_rowversion_distinct(fixture_bak_rowversion_extract):
    """Each rowversion value must be unique (DB timestamp increments per INSERT)."""
    rows = _get_rows(fixture_bak_rowversion_extract)
    rvs = [bytes(r["rv"]) for r in rows]
    assert len(rvs) == len(set(rvs)), "rowversion values are not all distinct"


def test_rowversion_monotonically_increasing(fixture_bak_rowversion_extract):
    """Rows inserted in id order should have monotonically increasing rowversion values."""
    rows = _get_rows(fixture_bak_rowversion_extract)
    rows_sorted = sorted(rows, key=lambda r: r["id"])
    rvs = [bytes(r["rv"]) for r in rows_sorted]
    for i in range(1, len(rvs)):
        assert rvs[i] > rvs[i - 1], (
            f"rowversion not increasing between id={rows_sorted[i-1]['id']} "
            f"({rvs[i-1].hex()}) and id={rows_sorted[i]['id']} ({rvs[i].hex()})"
        )
