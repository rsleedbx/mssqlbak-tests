"""Regression test: nvarchar(max) values whose first UTF-16LE byte is 0x21.

Characters in several Unicode scripts begin with byte 0x21 in UTF-16LE
(little-endian):
    U+0021  !   ASCII exclamation        bytes: 21 00
    U+0421  С   Cyrillic capital Es      bytes: 21 04
    U+0921  ड   Devanagari DDA           bytes: 21 09
    U+0C21  డ   Telugu DDA               bytes: 21 0C
    U+7121  無  CJK unified ideograph    bytes: 21 71

rows.py previously stripped the leading 0x21 byte from any inline nvarchar(max)
cell, treating it as a SQL Server type-marker.  That left an odd byte count
which caused _decode_nchar to return None instead of the correct string.

The fix guards on cell parity: a genuine 0x21 prefix produces odd total length
(1 prefix + even UTF-16LE payload); an even total means 0x21 IS the first data
byte and must not be stripped.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_nvarchar_max_u21_fixture import EXPECTED, ROW_COUNT, TABLE


def _rows(fixture: Path) -> dict[int, dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return {r["id"]: r for r in read_table_rows(store, tbl)}


def test_nvarchar_max_u21_row_count(fixture_bak_nvarchar_max_u21: Path) -> None:
    rows = _rows(fixture_bak_nvarchar_max_u21)
    assert len(rows) == ROW_COUNT


def test_nvarchar_max_u21_values(fixture_bak_nvarchar_max_u21: Path) -> None:
    """Every nvarchar(max) value whose first UTF-16LE byte is 0x21 must decode
    correctly — not as None — and match the expected Python string exactly."""
    rows = _rows(fixture_bak_nvarchar_max_u21)
    for row_id, expected in EXPECTED.items():
        actual = rows[row_id]["val"]
        assert actual == expected, (
            f"row id={row_id}: expected {expected!r}, got {actual!r}\n"
            f"(None result indicates the 0x21-strip regression has re-appeared)"
        )


def test_nvarchar_max_u21_no_spurious_nones(fixture_bak_nvarchar_max_u21: Path) -> None:
    """No non-null value should decode as None (the hallmark of the bug)."""
    rows = _rows(fixture_bak_nvarchar_max_u21)
    spurious_nones = [
        row_id
        for row_id, expected in EXPECTED.items()
        if expected is not None and rows[row_id]["val"] is None
    ]
    assert not spurious_nones, (
        f"Rows decoded as None (should be non-null): ids={spurious_nones}\n"
        "This is the 0x21-first-byte nvarchar(max) regression."
    )
