"""F2+F3+F5 diagnostic coverage — cci_varbinary_probe_full.bak.

Three tables probing different aspects of Format C (enc=3) VARBINARY encoding
(docs/260619-1-varbinary-bak.md §F2, §F3, §F5):

  cci_varbinary_maxwidth       (F2) — VARBINARY(16), all values 16 bytes wide,
                                       1,200 rows.  Tests whether item_size tracks
                                       observed value width or max_length.
  cci_varbinary_narrowmax      (F3) — VARBINARY(4), 1,200 rows.  If item_size=4
                                       here vs item_size=8 in max_length=16 fixture,
                                       item_size follows max_length not value width.
  cci_varbinary_small_rowgroup (F5) — VARBINARY(16), 128 rows, no NULLs.
                                       Pool = 128×8 = 1,024 bytes; index = 256 bytes.
                                       Trivially detectable pool/index boundary (M3).

## Expected decoder behaviour

cci_varbinary_maxwidth (1 NULL in 1,200 rows — sparse):
  Bug K3B fires → all rows return None.  Value tests are xfail.

cci_varbinary_narrowmax (1 NULL in 1,200 rows — sparse):
  Bug K3B fires → all rows return None.  Value tests are xfail.

cci_varbinary_small_rowgroup (0 NULLs):
  K3B cannot fire.  Value tests should PASS.

Fixture generation::

    python -m tools.fixture_run cci-varbinary-probe
    python -m tools.fixture_run all-versions --suite cci-varbinary-probe
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_varbinary_probe_fixture import (
    MAXWIDTH_ROWS,
    MAXWIDTH_STRUCTURAL_IDS,
    NARROWMAX_ROWS,
    NARROWMAX_STRUCTURAL_IDS,
    SMALLRG_ROWS,
)


def _rows(path: Path, table: str) -> list[dict]:
    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ===========================================================================
# cci_varbinary_maxwidth (F2)
# ===========================================================================


@pytest.mark.fixture
def test_maxwidth_row_count(fixture_bak_cci_varbinary_probe: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_maxwidth")
    assert len(rows) == MAXWIDTH_ROWS


@pytest.mark.fixture
def test_maxwidth_null_sentinel(fixture_bak_cci_varbinary_probe: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_maxwidth")
    row = next(r for r in rows if r["id"] == MAXWIDTH_STRUCTURAL_IDS["null"])
    assert row["val"] is None


@pytest.mark.fixture
def test_maxwidth_low_value(fixture_bak_cci_varbinary_probe: Path) -> None:
    """id=1 (LOW) must decode to the 16-byte low value."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_maxwidth")
    row = next(r for r in rows if r["id"] == MAXWIDTH_STRUCTURAL_IDS["low"])
    expected = b"\x00" * 15 + b"\x01"
    assert bytes(row["val"]) == expected


@pytest.mark.fixture
def test_maxwidth_high_value(fixture_bak_cci_varbinary_probe: Path) -> None:
    """id=2 (HIGH) must decode to b'\\xff' × 16."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_maxwidth")
    row = next(r for r in rows if r["id"] == MAXWIDTH_STRUCTURAL_IDS["high"])
    assert bytes(row["val"]) == b"\xff" * 16


@pytest.mark.fixture
def test_maxwidth_filler_none_count(fixture_bak_cci_varbinary_probe: Path) -> None:
    """Bug K3B proof: filler rows must not all be None after fix."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_maxwidth")
    filler = [r for r in rows if r["id"] >= 7]
    none_count = sum(1 for r in filler if r["val"] is None)
    assert none_count == 0, f"Bug K3B: {none_count}/{len(filler)} filler rows returned None"


# ===========================================================================
# cci_varbinary_narrowmax (F3)
# ===========================================================================


@pytest.mark.fixture
def test_narrowmax_row_count(fixture_bak_cci_varbinary_probe: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_narrowmax")
    assert len(rows) == NARROWMAX_ROWS


@pytest.mark.fixture
def test_narrowmax_null_sentinel(fixture_bak_cci_varbinary_probe: Path) -> None:
    """id=3 (NULL sentinel) must return None [Bug K3B: currently returns garbage for VARBINARY(4)]."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_narrowmax")
    row = next(r for r in rows if r["id"] == NARROWMAX_STRUCTURAL_IDS["null"])
    assert row["val"] is None


@pytest.mark.fixture
def test_narrowmax_low_value(fixture_bak_cci_varbinary_probe: Path) -> None:
    """id=1 (LOW) of VARBINARY(4) must decode to b'\\x01'."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_narrowmax")
    row = next(r for r in rows if r["id"] == NARROWMAX_STRUCTURAL_IDS["low"])
    assert bytes(row["val"]) == b"\x01"


@pytest.mark.fixture
def test_narrowmax_high_value(fixture_bak_cci_varbinary_probe: Path) -> None:
    """id=2 (HIGH) of VARBINARY(4) must decode to b'\\xff\\xff\\xff\\xff'."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_narrowmax")
    row = next(r for r in rows if r["id"] == NARROWMAX_STRUCTURAL_IDS["high"])
    assert bytes(row["val"]) == b"\xff\xff\xff\xff"


# ===========================================================================
# cci_varbinary_small_rowgroup (F5) — no NULLs, K3B cannot fire
# ===========================================================================


@pytest.mark.fixture
def test_smallrg_row_count(fixture_bak_cci_varbinary_probe: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_small_rowgroup")
    assert len(rows) == SMALLRG_ROWS


@pytest.mark.fixture
def test_smallrg_ids_sequential(fixture_bak_cci_varbinary_probe: Path) -> None:
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_small_rowgroup")
    ids = sorted(r["id"] for r in rows)
    assert ids == list(range(1, SMALLRG_ROWS + 1))


@pytest.mark.fixture
def test_smallrg_no_nulls(fixture_bak_cci_varbinary_probe: Path) -> None:
    """No NULLs inserted → all rows must have a non-None val."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_small_rowgroup")
    nulls = [r["id"] for r in rows if r["val"] is None]
    assert not nulls, f"unexpected None values at ids: {nulls}"


@pytest.mark.fixture
@pytest.mark.parametrize("rid", [1, 2, 64, 127, 128])
def test_smallrg_value(rid: int, fixture_bak_cci_varbinary_probe: Path) -> None:
    """CAST(n AS VARBINARY(16)) must decode to the captured 8-byte value for n."""
    rows = _rows(fixture_bak_cci_varbinary_probe, "cci_varbinary_small_rowgroup")
    row = next(r for r in rows if r["id"] == rid)
    val = row["val"]
    assert isinstance(val, (bytes, bytearray)), f"id={rid}: expected bytes, got {type(val)}"
    expected = rid.to_bytes(8, "big")
    assert bytes(val) == expected, (
        f"id={rid}: expected {expected.hex()}, got {bytes(val).hex()}"
    )
