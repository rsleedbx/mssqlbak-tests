"""F1 diagnostic coverage — cci_varbinary_micro_full.bak.

Three tables designed to make the XPRESS-decompressed Format C blob for
VARBINARY(16) manually inspectable (docs/260619-1-varbinary-bak.md §F1):

  cci_varbinary_micro        — 7 hand-chosen rows (M1/M2/M3 probes)
  cci_varbinary_micro_nullonly — 21 rows: 1 non-null + 20 NULLs
  cci_varbinary_micro_1byte  — 20 rows, all 1-byte values, no NULLs

## Expected decoder behaviour

All three tables decode correctly.  These tiny segments use the **uncompressed**
enc=5 Format B layout with a variable-width `[pool][reverse-order u16 index]`
value region (decoded via `_enc5_formatc_varlen`), and — for the single-distinct
`_nullonly` table — a tiny xVelocity v4 enc=3 dictionary whose only entry is
stored inline (1-byte-length-prefixed) rather than in a Huffman page.  Earlier
the variable-width values were mis-routed to the fixed-width Format B decoder and
the inline v4 dictionary entry was missed, so every value returned NULL.

Fixture generation::

    python -m tools.fixture_run cci-varbinary-micro
    python -m tools.fixture_run all-versions --suite cci-varbinary-micro
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_varbinary_micro_fixture import (
    MICRO_ROWS,
    NULLONLY_NON_NULL_ID,
    NULLONLY_NULL_IDS,
    ONEBYTE_ROWS,
)


def _rows(path: Path, table: str) -> list[dict]:
    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# cci_varbinary_micro — structural
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_micro_row_count(fixture_bak_cci_varbinary_micro: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro")
    assert len(rows) == len(MICRO_ROWS)


@pytest.mark.fixture
def test_micro_ids_present(fixture_bak_cci_varbinary_micro: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro")
    assert {r["id"] for r in rows} == set(MICRO_ROWS)


@pytest.mark.fixture
def test_micro_null_row_is_none(fixture_bak_cci_varbinary_micro: Path) -> None:
    """id=3 is the NULL sentinel; its val must be None."""
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro")
    row = next(r for r in rows if r["id"] == 3)
    assert row["val"] is None


# ---------------------------------------------------------------------------
# cci_varbinary_micro — value correctness (xfail if K3B fires)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
@pytest.mark.parametrize("rid", [rid for rid, (_, v) in MICRO_ROWS.items() if v is not None])
def test_micro_value(rid: int, fixture_bak_cci_varbinary_micro: Path) -> None:
    """Non-null rows must decode to the exact bytes inserted."""
    expected = MICRO_ROWS[rid][1]
    # parametrize only feeds non-null rids; narrow the type for the checker.
    assert expected is not None
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro")
    row = next(r for r in rows if r["id"] == rid)
    val = row["val"]
    assert isinstance(val, (bytes, bytearray)), f"id={rid}: expected bytes, got {type(val)}"
    assert bytes(val) == expected, (
        f"id={rid}: expected {expected.hex()!r}, got {bytes(val).hex()!r}"
    )


# ---------------------------------------------------------------------------
# cci_varbinary_micro_nullonly — structural
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_nullonly_row_count(fixture_bak_cci_varbinary_micro: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_nullonly")
    expected = 1 + len(NULLONLY_NULL_IDS)
    assert len(rows) == expected


@pytest.mark.fixture
def test_nullonly_null_rows(fixture_bak_cci_varbinary_micro: Path) -> None:
    """All 20 NULL rows must return val=None."""
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_nullonly")
    row_map = {r["id"]: r for r in rows}
    non_none = [rid for rid in NULLONLY_NULL_IDS if row_map.get(rid, {}).get("val") is not None]
    assert not non_none, f"expected None for ids {NULLONLY_NULL_IDS}, got non-None for: {non_none}"


@pytest.mark.fixture
def test_nullonly_nonnull_value(fixture_bak_cci_varbinary_micro: Path) -> None:
    """The single non-null row (id=1, val=0x01) must decode to b'\\x01'."""
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_nullonly")
    row = next(r for r in rows if r["id"] == NULLONLY_NON_NULL_ID)
    assert bytes(row["val"]) == b"\x01"


# ---------------------------------------------------------------------------
# cci_varbinary_micro_1byte — structural + value (no NULLs → K3B cannot fire)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_1byte_row_count(fixture_bak_cci_varbinary_micro: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_1byte")
    assert len(rows) == ONEBYTE_ROWS


@pytest.mark.fixture
def test_1byte_ids_present(fixture_bak_cci_varbinary_micro: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_1byte")
    assert {r["id"] for r in rows} == set(range(1, ONEBYTE_ROWS + 1))


@pytest.mark.fixture
def test_1byte_no_nulls(fixture_bak_cci_varbinary_micro: Path) -> None:
    """No NULLs inserted → all rows must have a non-None val."""
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_1byte")
    nulls = [r["id"] for r in rows if r["val"] is None]
    assert not nulls, f"unexpected None values at ids: {nulls}"


@pytest.mark.fixture
@pytest.mark.parametrize("rid", range(1, ONEBYTE_ROWS + 1))
def test_1byte_value(rid: int, fixture_bak_cci_varbinary_micro: Path) -> None:
    """CAST(n AS VARBINARY(16)) of the BIGINT seed must decode to 8 big-endian bytes."""
    rows = _rows(fixture_bak_cci_varbinary_micro, "cci_varbinary_micro_1byte")
    row = next(r for r in rows if r["id"] == rid)
    val = row["val"]
    assert isinstance(val, (bytes, bytearray)), f"id={rid}: expected bytes, got {type(val)}"
    # CAST(<bigint> AS VARBINARY(16)) keeps the full 8-byte big-endian width.
    expected = rid.to_bytes(8, "big")
    assert bytes(val) == expected, f"id={rid}: expected {expected.hex()}, got {bytes(val).hex()}"
