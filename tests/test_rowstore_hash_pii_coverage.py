from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_rowstore_hash_pii_fixture import (
    EXPECTED_CREDIT_SHA256,
    EXPECTED_HASH_SHA256,
    EXPECTED_SSN_SHA256,
    ROW_COUNT,
    TABLE,
)


def _rows(fixture: Path) -> dict[int, dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in fixture")
    return {int(row["id"]): row for row in read_table_rows(store, tbl)}


def test_rowstore_hash_pii_row_count(fixture_bak_rowstore_hash_pii: Path) -> None:
    assert len(_rows(fixture_bak_rowstore_hash_pii)) == ROW_COUNT


def test_rowstore_hash_pii_hashes(fixture_bak_rowstore_hash_pii: Path) -> None:
    rows = _rows(fixture_bak_rowstore_hash_pii)

    for row_id, expected_hash in EXPECTED_HASH_SHA256.items():
        value = rows[row_id]["hashed_password"]
        assert isinstance(value, (bytes, bytearray))
        assert _sha256(bytes(value)) == expected_hash

    for row_id, expected_hash in EXPECTED_SSN_SHA256.items():
        value = rows[row_id]["ssn_cipher"]
        assert isinstance(value, (bytes, bytearray))
        assert _sha256(bytes(value)) == expected_hash

    for row_id, expected_hash in EXPECTED_CREDIT_SHA256.items():
        value = rows[row_id]["credit_card_cipher"]
        assert isinstance(value, (bytes, bytearray))
        assert _sha256(bytes(value)) == expected_hash

    assert rows[4]["hashed_password"] is None
    assert rows[4]["ssn_cipher"] is None
    assert rows[4]["credit_card_cipher"] is None


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
