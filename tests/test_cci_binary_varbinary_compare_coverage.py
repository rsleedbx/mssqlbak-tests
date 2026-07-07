"""F4 diagnostic coverage — cci_binary_varbinary_compare_full.bak.

BINARY(8) and VARBINARY(8) in the same row group with identical inserted values
(1,200 rows).  Side-by-side blob comparison resolves Format C mysteries M1 and
M2 (docs/260619-1-varbinary-bak.md §F4).

## Expected decoder behaviour

Both columns are in a regular CCI (enc=3), not ARCHIVE (enc=5):

  bin8 (BINARY(8))    — Bug E3B fires: BINARY offset-table absent in enc=3 →
                        all non-null rows return None.  Value tests are xfail.

  vb8 (VARBINARY(8))  — Bug K3B fires: sparse-NULL (1/1200) polarity inversion →
                        all rows return None.  Value tests are xfail.

Structural tests (row count, NULL sentinel) are expected to pass.

Fixture generation::

    python -m tools.fixture_run cci-binary-varbinary-compare
    python -m tools.fixture_run all-versions --suite cci-binary-varbinary-compare
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_binary_varbinary_compare_fixture import (
    FILLER_COUNT,
    FILLER_START,
    ROWS_PER_TABLE,
    STRUCTURAL_IDS,
)

_NULL_ID = STRUCTURAL_IDS["null"]
_LOW_ID = STRUCTURAL_IDS["low"]
_HIGH_ID = STRUCTURAL_IDS["high"]


def _rows(path: Path) -> list[dict]:
    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == "cci_binary_varbinary_compare")
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Structural
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_row_count(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    assert len(rows) == ROWS_PER_TABLE


@pytest.mark.fixture
def test_ids_cover_expected_range(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    ids = {r["id"] for r in rows}
    structural = set(STRUCTURAL_IDS.values())
    filler = set(range(FILLER_START, FILLER_START + FILLER_COUNT))
    assert structural <= ids
    assert filler <= ids


@pytest.mark.fixture
def test_null_sentinel_bin8_is_none(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=3 bin8 must be NULL."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _NULL_ID)
    assert row["bin8"] is None


@pytest.mark.fixture
def test_null_sentinel_vb8_is_none(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=3 vb8 must be NULL."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _NULL_ID)
    assert row["vb8"] is None


# ---------------------------------------------------------------------------
# bin8 value tests — xfail (Bug E3B: BINARY offset-table absent in enc=3)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_bin8_low_value(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=1 bin8 must be 0x0000000000000001 (LOW)."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _LOW_ID)
    assert bytes(row["bin8"]) == b"\x00\x00\x00\x00\x00\x00\x00\x01"


@pytest.mark.fixture
def test_bin8_high_value(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=2 bin8 must be 0xFFFFFFFFFFFFFFFF (HIGH)."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _HIGH_ID)
    assert bytes(row["bin8"]) == b"\xff" * 8


@pytest.mark.fixture
def test_bin8_filler_none_count(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """Bug E3B proof: all BINARY filler rows return None instead of bytes."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    filler_rows = [r for r in rows if r["id"] >= FILLER_START]
    none_count = sum(1 for r in filler_rows if r["bin8"] is None)
    assert none_count == 0, (
        f"Bug E3B: {none_count}/{len(filler_rows)} filler bin8 rows returned None"
    )


# ---------------------------------------------------------------------------
# vb8 value tests — xfail (Bug K3B: sparse-NULL polarity inversion)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_vb8_low_value(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=1 vb8 must be 0x0000000000000001 (LOW)."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _LOW_ID)
    assert bytes(row["vb8"]) == b"\x00\x00\x00\x00\x00\x00\x00\x01"


@pytest.mark.fixture
def test_vb8_high_value(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """id=2 vb8 must be 0xFFFFFFFFFFFFFFFF (HIGH)."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    row = next(r for r in rows if r["id"] == _HIGH_ID)
    assert bytes(row["vb8"]) == b"\xff" * 8


@pytest.mark.fixture
def test_vb8_filler_none_count(fixture_bak_cci_binary_varbinary_compare: Path) -> None:
    """Bug K3B proof: all VARBINARY filler rows return None (polarity inverted)."""
    rows = _rows(fixture_bak_cci_binary_varbinary_compare)
    filler_rows = [r for r in rows if r["id"] >= FILLER_START]
    none_count = sum(1 for r in filler_rows if r["vb8"] is None)
    assert none_count == 0, (
        f"Bug K3B: {none_count}/{len(filler_rows)} filler vb8 rows returned None"
    )
