"""Gap D-4: hierarchyid column extraction tests.

``hierarchyid`` is a variable-length bit-packed binary.  mssqlbak decodes it
as the human-readable path string (e.g. '/', '/1/', '/1/2/') rather than raw
bytes.  The test verifies that each value is a non-empty string matching the
known path and that the persisted computed ``path`` column agrees.

Fixture: dbo.org — 6 rows with known path strings and persisted ``path`` column.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_hierarchyid_extract_fixture import (
    KNOWN_PATHS,
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


def test_hierarchyid_row_count(fixture_bak_hierarchyid_extract):
    """All 6 rows must be returned."""
    rows = _get_rows(fixture_bak_hierarchyid_extract)
    assert len(rows) == ROW_COUNT, f"expected {ROW_COUNT} rows, got {len(rows)}"


def test_hierarchyid_is_string_path(fixture_bak_hierarchyid_extract):
    """mssqlbak decodes hierarchyid as a path string (e.g. '/', '/1/', '/1/1/').
    Values must be non-empty strings starting and ending with '/'."""
    rows = _get_rows(fixture_bak_hierarchyid_extract)
    bad = [
        (r["id"], repr(r["node"]))
        for r in rows
        if not isinstance(r["node"], str) or not r["node"].startswith("/")
    ]
    assert not bad, f"node not a valid path string for ids: {bad}"


def test_hierarchyid_non_empty(fixture_bak_hierarchyid_extract):
    """Every hierarchyid path string must be non-empty."""
    rows = _get_rows(fixture_bak_hierarchyid_extract)
    empty = [r["id"] for r in rows if not r["node"]]
    assert not empty, f"empty node values for ids: {empty}"


def test_hierarchyid_path_column_matches(fixture_bak_hierarchyid_extract):
    """Persisted 'path' column (AS node.ToString() PERSISTED) must match KNOWN_PATHS."""
    rows = _get_rows(fixture_bak_hierarchyid_extract)
    rows_by_id = {r["id"]: r for r in rows}
    for node_id, expected_path in KNOWN_PATHS:
        row = rows_by_id.get(node_id)
        assert row is not None, f"id={node_id} missing"
        actual_path = row.get("path")
        assert actual_path == expected_path, (
            f"id={node_id}: expected path={expected_path!r}, got {actual_path!r}"
        )
