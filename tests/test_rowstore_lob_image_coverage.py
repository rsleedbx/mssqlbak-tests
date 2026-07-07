"""Rowstore LOB and image cell coverage."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_rowstore_lob_image_fixture import (
    EXPECTED_BIN_SHA256,
    EXPECTED_IMAGE_SHA256,
    EXPECTED_TEXT_SHA256,
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


def test_rowstore_lob_image_row_count(fixture_bak_rowstore_lob_image: Path) -> None:
    rows = _rows(fixture_bak_rowstore_lob_image)
    assert len(rows) == ROW_COUNT


def test_rowstore_lob_image_binary_hashes(fixture_bak_rowstore_lob_image: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_rowstore_lob_image)}
    for row_id, expected_hash in EXPECTED_IMAGE_SHA256.items():
        value = rows_by_id[row_id]["photo_image"]
        assert isinstance(value, (bytes, bytearray))
        assert _sha256(bytes(value)) == expected_hash

    for row_id, expected_hash in EXPECTED_BIN_SHA256.items():
        value = rows_by_id[row_id]["photo_varbinary"]
        assert isinstance(value, (bytes, bytearray))
        assert _sha256(bytes(value)) == expected_hash


def test_rowstore_lob_image_text_hashes(fixture_bak_rowstore_lob_image: Path) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_rowstore_lob_image)}
    for row_id, expected_hash in EXPECTED_TEXT_SHA256.items():
        assert _sha256(rows_by_id[row_id]["text_payload"].encode("utf-8")) == expected_hash

    for row_id, expected_hash in EXPECTED_WIDE_SHA256.items():
        assert _sha256(rows_by_id[row_id]["wide_payload"].encode("utf-16-le")) == expected_hash


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
