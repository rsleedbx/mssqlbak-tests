"""Typed XML cell coverage.

This fixture uses an XML schema collection so the XML payload is stored as typed
binary XML, unlike the existing untyped XML fixtures.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon, column_digest
from tools.make_typed_xml_fixture import (
    EXPECTED_DIGEST,
    EXPECTED_SNIPPETS,
    ROW_COUNT,
    TABLE,
)

EXPECTED_XML_SENTINELS: dict[int, tuple[str, ...]] = {
    4: ("<empty",),
    5: ("line1", "line2"),
    6: ("<squareFeet>21000</squareFeet>",),
    7: ("Primary Bank", "Reserve"),
    8: ("<asBoolean>true</asBoolean>", "<asDecimal>3.14</asDecimal>"),
}


def _rows(fixture: Path) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return list(read_table_rows(store, tbl))


def test_typed_xml_row_count(fixture_bak_typed_xml: Path) -> None:
    rows = _rows(fixture_bak_typed_xml)
    assert len(rows) == ROW_COUNT


def test_typed_xml_values_contain_expected_content(fixture_bak_typed_xml: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_typed_xml)}
    for row_id, snippets in EXPECTED_SNIPPETS.items():
        doc = rows_by_id[row_id]["doc"]
        assert isinstance(doc, str)
        for snippet in snippets:
            assert snippet in doc


def test_typed_xml_serialization_sentinels(fixture_bak_typed_xml: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_typed_xml)}
    for row_id, snippets in EXPECTED_XML_SENTINELS.items():
        doc = rows_by_id[row_id]["doc"]
        assert isinstance(doc, str)
        for snippet in snippets:
            assert snippet in doc


def test_typed_xml_digest_is_stable(fixture_bak_typed_xml: Path) -> None:
    rows = sorted(_rows(fixture_bak_typed_xml), key=lambda r: r["id"])
    digest = column_digest(canon(r["doc"], "xml") for r in rows)
    assert digest == EXPECTED_DIGEST
