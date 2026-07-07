"""LOB inline-root link-count tests (Guess G30)."""

from __future__ import annotations

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.lobmatrix import LOB_LINKS_EXPECTED_LEN, LOB_LINKS_TABLE


@pytest.mark.fixture
def test_lob_links_table_recovered(fixture_bak) -> None:
    store = PageStore.from_bak(fixture_bak)
    names = {t.name for t in recover_schema(store).tables}
    if LOB_LINKS_TABLE not in names:
        pytest.skip("lob_links table missing; regen typecoverage_full.bak")
    table = next(t for t in recover_schema(store).tables if t.name == LOB_LINKS_TABLE)
    rows = {r["id"]: r["v"] for r in read_table_rows(store, table)}
    for row_id, expected_len in LOB_LINKS_EXPECTED_LEN.items():
        assert row_id in rows
        val = rows[row_id]
        assert isinstance(val, (str, bytes))
        assert len(val) == expected_len, f"id={row_id}: len={len(val)} expected {expected_len}"
