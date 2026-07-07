"""Coverage tests for ``cci_lob_full.bak`` — CCI tables with VARCHAR(MAX),
NVARCHAR(MAX), and VARBINARY(MAX) columns (Gap C-6).

Each table has four structural rows (ids 1-4):

    id=1  low   — empty value
    id=2  mid   — moderate-length value (fits 1-byte-length format)
    id=3  high  — long value (≥ 128 chars / bytes, triggers varint encoding)
    id=4  null  — NULL sentinel

The key discriminating case is ``NVARCHAR(MAX)`` with values ≥ 128 chars (id=2
and id=3).  At that length, the CCI dictionary uses the varint-prefix + 0x21
separator format with a UTF-16LE payload.  Bug C-6: the decoder previously
decoded that payload as cp1252, producing a doubled-length string with
interleaved NUL bytes.

Generate the fixture::

    python -m tools.fixture_run cci-lob
    python -m tools.fixture_run all-versions --suite cci-lob
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_lob_fixture import (
    ROWS_PER_TABLE,
    STRUCTURAL_IDS,
    TABLE_DEFS,
)

_ID_TO_LABEL = {v: k for k, v in STRUCTURAL_IDS.items()}


def _read_table(
    fixture: Path, table_name: str
) -> tuple[int, dict[str, Any]]:
    """Return (total_row_count, {label: decoded_val}) for the ``val`` column.

    Only structural rows (ids in STRUCTURAL_IDS) are included in the dict;
    filler rows are counted but not checked.
    """
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == table_name), None)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in {fixture.name}")

    by_label: dict[str, Any] = {}
    count = 0
    for row in read_table_rows(store, tbl):
        count += 1
        row_id: int = row["id"]
        if row_id in _ID_TO_LABEL:
            by_label[_ID_TO_LABEL[row_id]] = row.get("val")
    return count, by_label


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_database_present(fixture_bak_cci_lob: Path) -> None:
    """Fixture opens without error and contains the expected tables."""
    store = PageStore.from_bak(fixture_bak_cci_lob)
    schema = recover_schema(store)
    names = {t.name for t in schema.tables}
    for td in TABLE_DEFS:
        assert td.name in names, (
            f"Table {td.name!r} not found in {fixture_bak_cci_lob.name}; "
            f"available: {sorted(names)}"
        )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_row_count(fixture_bak_cci_lob: Path, td: Any) -> None:
    """Total row count matches the expected 1,200 rows per table."""
    count, _ = _read_table(fixture_bak_cci_lob, td.name)
    assert count == ROWS_PER_TABLE, (
        f"{td.name}: expected {ROWS_PER_TABLE} rows, got {count}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_null_row(fixture_bak_cci_lob: Path, td: Any) -> None:
    """The NULL structural row (id=4) decodes as None."""
    _, by_label = _read_table(fixture_bak_cci_lob, td.name)
    assert "null" in by_label, f"{td.name}: NULL row (id=4) not found"
    assert by_label["null"] is None, (
        f"{td.name}: NULL row decoded as {by_label['null']!r}, expected None"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_low_row(fixture_bak_cci_lob: Path, td: Any) -> None:
    """The empty-value structural row (id=1) decodes correctly."""
    _, by_label = _read_table(fixture_bak_cci_lob, td.name)
    assert "low" in by_label, f"{td.name}: low row (id=1) not found"
    assert by_label["low"] == td.low, (
        f"{td.name}: low row decoded as {by_label['low']!r}, expected {td.low!r}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_mid_row(fixture_bak_cci_lob: Path, td: Any) -> None:
    """The moderate-length structural row (id=2) decodes correctly.

    For NVARCHAR(MAX) with 200 chars (400 bytes UTF-16LE) this is the first
    value that needs the varint length prefix (1-byte-length max = 127 chars =
    254 bytes).  Bug C-6: decoded as cp1252 → 400-char string with NUL bytes.
    """
    _, by_label = _read_table(fixture_bak_cci_lob, td.name)
    assert "mid" in by_label, f"{td.name}: mid row (id=2) not found"
    actual = by_label["mid"]
    assert actual == td.mid, (
        f"{td.name}: mid row decoded as {repr(actual)[:80]!r}, "
        f"expected {repr(td.mid)[:80]!r}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_high_row(fixture_bak_cci_lob: Path, td: Any) -> None:
    """The long structural row (id=3) decodes correctly.

    For NVARCHAR(MAX) with 500 chars (1,000 bytes UTF-16LE) this is the main
    C-6 discriminating case.  Bug C-6: cp1252 decode → 1,000-char string with
    interleaved NUL bytes.
    """
    _, by_label = _read_table(fixture_bak_cci_lob, td.name)
    assert "high" in by_label, f"{td.name}: high row (id=3) not found"
    actual = by_label["high"]
    assert actual == td.high, (
        f"{td.name}: high row decoded as {repr(actual)[:80]!r}, "
        f"expected {repr(td.high)[:80]!r}"
    )
