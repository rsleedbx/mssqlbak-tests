"""Layout-coverage tests — PK position and column-count boundary fixtures (L01–L03)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.layoutmatrix import (
    COL_COUNT_CASES,
    all_pk_cases,
    expected_col_count_rows,
    expected_pk_rows,
)


def _normalize(value: Any) -> Any:
    """Coerce parser output to match matrix canonical types."""
    if isinstance(value, bytes):
        return value
    if isinstance(value, str) and value is not None:
        return value.rstrip() if len(value) > 1 and value.endswith(" ") else value
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else value
    return value


def _rows_match(expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> bool:
    if len(expected) != len(actual):
        return False
    for exp, got in zip(sorted(expected, key=lambda r: str(r.get("pk_col", r.get("id")))),
                        sorted(actual, key=lambda r: str(r.get("pk_col", r.get("id"))))):
        for key, exp_val in exp.items():
            if key not in got:
                return False
            gv = _normalize(got[key])
            ev = _normalize(exp_val)
            if isinstance(ev, UUID):
                ev = str(ev)
            if isinstance(gv, UUID):
                gv = str(gv)
            if gv != ev:
                return False
    return True


@pytest.mark.fixture
def test_all_layout_tables_recovered(fixture_bak_layout) -> None:
    store = PageStore.from_bak(fixture_bak_layout)
    names = {t.name for t in recover_schema(store).tables}
    expected = {c.table_name for c in all_pk_cases()} | {c.table_name for c in COL_COUNT_CASES}
    assert expected <= names, f"missing layout tables: {expected - names}"


@pytest.mark.fixture
@pytest.mark.parametrize("case", all_pk_cases(), ids=lambda c: c.table_name)
def test_pk_position_rows(fixture_bak_layout, case) -> None:
    store = PageStore.from_bak(fixture_bak_layout)
    table = next(t for t in recover_schema(store).tables if t.name == case.table_name)
    rows = list(read_table_rows(store, table))
    expected = expected_pk_rows(case)
    assert _rows_match(expected, rows), f"{case.table_name}: {rows!r} != {expected!r}"


@pytest.mark.fixture
@pytest.mark.parametrize("case", COL_COUNT_CASES, ids=lambda c: c.table_name)
def test_column_count_rows(fixture_bak_layout, case) -> None:
    store = PageStore.from_bak(fixture_bak_layout)
    table = next(t for t in recover_schema(store).tables if t.name == case.table_name)
    rows = list(read_table_rows(store, table))
    expected = expected_col_count_rows(case)
    actual = [{"id": r["id"], **{k: r[k] for k in r if k.startswith("c")}} for r in rows]
    assert sorted(actual, key=lambda r: r["id"]) == expected
