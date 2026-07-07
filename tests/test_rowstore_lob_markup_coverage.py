from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_rowstore_lob_markup_fixture import (
    EXPECTED_HTML_SHA256,
    EXPECTED_JSON_SHA256,
    EXPECTED_WIDE_SHA256,
    ROW_COUNT,
    TABLE,
)


def _rows(fixture: Path) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return list(read_table_rows(store, tbl))


def test_rowstore_lob_markup_row_count(fixture_bak_rowstore_lob_markup: Path) -> None:
    rows = _rows(fixture_bak_rowstore_lob_markup)
    assert len(rows) == ROW_COUNT


def test_rowstore_lob_markup_hashes(fixture_bak_rowstore_lob_markup: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_rowstore_lob_markup)}

    for row_id, expected_hash in EXPECTED_HTML_SHA256.items():
        assert _sha256(rows_by_id[row_id]["html_body"].encode("utf-8")) == expected_hash

    for row_id, expected_hash in EXPECTED_WIDE_SHA256.items():
        assert _sha256(rows_by_id[row_id]["wide_body"].encode("utf-16-le")) == expected_hash

    for row_id, expected_hash in EXPECTED_JSON_SHA256.items():
        assert _sha256(rows_by_id[row_id]["json_body"].encode("utf-8")) == expected_hash

    assert rows_by_id[4]["html_body"] == ""
    assert rows_by_id[4]["wide_body"] == ""
    assert rows_by_id[4]["json_body"] == ""
    assert rows_by_id[5]["html_body"] is None
    assert rows_by_id[5]["wide_body"] is None
    assert rows_by_id[5]["json_body"] is None


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
