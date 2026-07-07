"""Alias scalar type cell coverage.

AdventureWorks uses alias types such as ``Flag`` and ``NameStyle`` over
``bit``.  The decoded value and the cell canonicalization layer must treat
those aliases like their underlying system types.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon
from tools.make_alias_types_fixture import (
    EXPECTED_ROWS,
    TABLE,
)


def _rows(fixture: Path) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return list(read_table_rows(store, tbl))


def test_alias_types_row_count(fixture_bak_alias_types: Path) -> None:
    rows = _rows(fixture_bak_alias_types)
    assert len(rows) == len(EXPECTED_ROWS)


def test_alias_bit_values(fixture_bak_alias_types: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_alias_types)}
    for row_id, expected in EXPECTED_ROWS.items():
        row = rows_by_id[row_id]
        assert row["is_active"] is expected["is_active"]
        assert row["name_style"] is expected["name_style"]
        assert row["random_flag_123"] is expected["random_flag_123"]


def test_alias_scalar_values(fixture_bak_alias_types: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_alias_types)}
    for row_id, expected in EXPECTED_ROWS.items():
        row = rows_by_id[row_id]
        assert row["display_name"] == expected["display_name"]
        assert row["account_number"] == expected["account_number"]
        assert str(row["external_id"]).lower() == expected["external_id"]
        assert row["float_alias"] == expected["float_alias"]
        assert str(row["money_alias"]) == str(expected["money_alias"])


@pytest.mark.parametrize(
    ("column", "sql_type"),
    [
        ("is_active", "Flag"),
        ("name_style", "NameStyle"),
            ("random_flag_123", "bit"),
    ],
)
def test_alias_bit_canon_matches_bit(
    fixture_bak_alias_types: Path,
    column: str,
    sql_type: str,
) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_alias_types)}
    for row_id, expected in EXPECTED_ROWS.items():
        expected_canon = canon(expected[column], "bit")
        actual_canon = canon(rows_by_id[row_id][column], sql_type)
        assert actual_canon == expected_canon


def test_unknown_alias_names_use_base_type_canonicalization(
    fixture_bak_alias_types: Path,
) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_alias_types)}

    assert canon(rows_by_id[1]["random_flag_123"], "bit") == "1"
    assert canon(rows_by_id[2]["random_flag_123"], "bit") == "0"
    assert canon(rows_by_id[1]["float_alias"], "float") == "1.5"
    assert canon(rows_by_id[2]["money_alias"], "money") == "0.0100"
