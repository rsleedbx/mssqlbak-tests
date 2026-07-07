"""Schema recovery against the known reference fixture."""
from __future__ import annotations

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
def test_recovers_all_user_tables(fixture_bak) -> None:
    schema = recover_schema(PageStore.from_bak(fixture_bak))
    names = {t.name for t in schema.tables}
    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            # Cases with fallback_xtype are version-specific types (e.g. SS2025
            # native JSON) that aren't present in the SS2022 typecoverage fixture.
            continue
        assert f"t_{case.name}" in names


@pytest.mark.fixture
def test_table_columns_in_order(fixture_bak) -> None:
    schema = recover_schema(PageStore.from_bak(fixture_bak))
    t = next(t for t in schema.tables if t.name == "t_int")
    assert [c.name for c in t.columns] == ["id", "label", "v"]


@pytest.mark.fixture
def test_int_column_metadata(fixture_bak) -> None:
    schema = recover_schema(PageStore.from_bak(fixture_bak))
    t = next(t for t in schema.tables if t.name == "t_int")
    assert len(t.columns) == 3
    by_name = {c.name: c for c in t.columns}
    # id int IDENTITY PK, NOT NULL, fixed at leaf offset 4
    assert by_name["id"].type_id == 56  # int
    assert by_name["id"].nullable is False
    assert by_name["id"].is_variable is False
    assert by_name["id"].leaf_offset == 4
    # label varchar(8) NOT NULL, variable
    assert by_name["label"].type_id == 167  # varchar
    assert by_name["label"].is_variable is True
    assert by_name["label"].nullable is False
    # v int NULL, fixed at leaf offset 8 (after id)
    assert by_name["v"].type_id == 56
    assert by_name["v"].nullable is True
    assert by_name["v"].is_variable is False
    assert by_name["v"].leaf_offset == 8


@pytest.mark.fixture
def test_v_column_type_matches_case(fixture_bak) -> None:
    # Each t_<case> table's ``v`` column must carry the expected system type id.
    expected = {
        "t_tinyint": 48,
        "t_smallint": 52,
        "t_int": 56,
        "t_bigint": 127,
        "t_bit": 104,
        "t_decimal_38_10": 106,
        "t_money": 60,
        "t_real": 59,
        "t_float": 62,
        "t_date": 40,
        "t_datetime2_7": 42,
        "t_char_10": 175,  # char
        "t_varchar_max": 167,  # varchar(max)
        "t_nvarchar_50": 231,  # nvarchar
        "t_varbinary_max": 165,  # varbinary(max)
        "t_uniqueidentifier": 36,
    }
    schema = recover_schema(PageStore.from_bak(fixture_bak))
    by_name = {t.name: t for t in schema.tables}
    for table_name, xtype in expected.items():
        v = next(c for c in by_name[table_name].columns if c.name == "v")
        assert v.type_id == xtype, (table_name, v.type_id, xtype)


@pytest.mark.fixture
def test_tables_have_in_row_alloc_unit(fixture_bak) -> None:
    from mssqlbak.catalog import ALLOC_IN_ROW

    schema = recover_schema(PageStore.from_bak(fixture_bak))
    t = next(t for t in schema.tables if t.name == "t_int")
    assert any(au.unit_type == ALLOC_IN_ROW for au in t.alloc_units)
    in_row = next(au for au in t.alloc_units if au.unit_type == ALLOC_IN_ROW)
    assert in_row.first_page[1] == 1  # file id 1
    assert in_row.first_page[0] > 0
