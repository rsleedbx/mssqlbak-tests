"""Row-size and LOB-page boundary coverage tests.

``rowboundary_full.bak`` exercises three critical byte-count thresholds in the
SQL Server storage engine that the mssqlbak parser must handle correctly:

  rb_overflow  — the 8060-byte in-row / ROW_OVERFLOW_DATA boundary
  rb_lob       — the 8096-byte single-LOB-page / two-LOB-page boundary
  rb_page_fill — data-page slot-array capacity (72 rows per page for CHAR(100))

## rb_overflow and Bug B-3

SQL Server moves variable-length column data to a ROW_OVERFLOW_DATA page when
the total row exceeds 8060 bytes, leaving a 24-byte pointer in-row.  Bug B-3
(fixed): ``stitch_lob`` previously returned the 24-byte pointer bytes as the
column value.  The fix follows the ROW_OVERFLOW pointer (struct_type=2) to the
overflow page and returns the actual column bytes.

Overflow fires for rows with ``LEN(a)+LEN(b) > VAR_LIMIT`` (8043 bytes;
overhead = 17 bytes because the null-bitmap section has a 2-byte column-count
prefix).  SQL Server keeps column ``a`` in-row and overflows only column ``b``
(the last/longest variable column):

    id=1 (a+b=8039) — in-row (−4), both columns decode correctly
    id=2 (a+b=8040) — in-row (−3), both columns decode correctly
    id=3 (a+b=8041) — in-row (−2), both columns decode correctly
    id=4 (a+b=8042) — in-row (−1), both columns decode correctly
    id=5 (a+b=8043) — in-row (at limit), both columns decode correctly
    id=6 (a+b=8044) — ROW_OVERFLOW (+1): a=4000, b=4044 — both correct
    id=7 (a+b=8045) — ROW_OVERFLOW (+2): a=4000, b=4045 — both correct
    id=8 (a+b=8046) — ROW_OVERFLOW (+3): a=4000, b=4046 — both correct
    id=9 (a+b=8047) — ROW_OVERFLOW (+4): a=4000, b=4047 — both correct

## rb_lob and LOB page boundary

LOB pages hold 8096 bytes of data (8192 - 96 byte header).  A VARBINARY(MAX)
value at exactly 8096 bytes fills one page; 8097 bytes needs two pages.

All rb_lob rows are expected to decode correctly.  Failures here indicate a bug
in the multi-page LOB stitcher.

## rb_page_fill and slot-array capacity

Fixed-width CHAR(100) rows (109 bytes each) pack 72 rows per data page.  The
fixture inserts 216 rows (exactly 3 full pages).  All rows should decode correctly.

Fixture generation::

    python -m tools.fixture_run row-boundary
    python -m tools.fixture_run all-versions --suite row-boundary
"""
from __future__ import annotations

from pathlib import Path

import pytest
import deltalake

from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_rowboundary_fixture import (
    LOB_ROW_SIZES,
    OVERFLOW_ROWS,
    PAGE_FILL_ROWS,
    ROWS_PER_PAGE,
    VAR_LIMIT,
    _OVERFLOW_ROW_DEFS,
)


def _rows(path: Path, table: str) -> list[dict]:
    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# rb_overflow — structural checks
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_rb_overflow_row_count(fixture_bak_rowboundary: Path) -> None:
    """rb_overflow must contain exactly one row per defined boundary id."""
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    assert len(rows) == len(_OVERFLOW_ROW_DEFS)


@pytest.mark.fixture
def test_rb_overflow_ids_present(fixture_bak_rowboundary: Path) -> None:
    """Every expected id (1–5) must appear in rb_overflow."""
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    ids = {r["id"] for r in rows}
    assert ids == set(_OVERFLOW_ROW_DEFS)


# ---------------------------------------------------------------------------
# rb_overflow — in-row rows (ids 1, 2, 3): EXPECTED TO PASS
# Parser reads the variable data directly from the data page.
# ---------------------------------------------------------------------------


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(r for r in _OVERFLOW_ROW_DEFS if r not in OVERFLOW_ROWS))
def test_rb_inrow_a_value(rid: int, fixture_bak_rowboundary: Path) -> None:
    """In-row rows: column 'a' must decode to REPLICATE('A', a_len)."""
    a_len, _ = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    got = repr(row["a"])
    assert row["a"] == "A" * a_len, (
        f"id={rid}: expected 'A'×{a_len}, got {got}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(r for r in _OVERFLOW_ROW_DEFS if r not in OVERFLOW_ROWS))
def test_rb_inrow_b_value(rid: int, fixture_bak_rowboundary: Path) -> None:
    """In-row rows: column 'b' must decode to REPLICATE('B', b_len)."""
    _, b_len = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    got = repr(row["b"])
    assert row["b"] == "B" * b_len, (
        f"id={rid}: expected 'B'×{b_len}, got {got}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(r for r in _OVERFLOW_ROW_DEFS if r not in OVERFLOW_ROWS))
def test_rb_inrow_total_length(rid: int, fixture_bak_rowboundary: Path) -> None:
    """In-row rows: LEN(a)+LEN(b) must be ≤ VAR_LIMIT and equal the defined size."""
    a_len, b_len = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    total = len(row["a"]) + len(row["b"])
    assert total == a_len + b_len, f"id={rid}: length mismatch"
    assert total <= VAR_LIMIT, f"id={rid}: expected in-row total ≤ {VAR_LIMIT}"


# ---------------------------------------------------------------------------
# rb_overflow — ROW_OVERFLOW rows (ids 6–9): Bug B-3 FIXED
#
# The ROW_OVERFLOW_DATA pointer (struct_type=2, 24 bytes) is now correctly
# followed to the overflow page; all overflow columns decode to their expected
# REPLICATE values.
# ---------------------------------------------------------------------------


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(OVERFLOW_ROWS))
def test_rb_overflow_a_value(rid: int, fixture_bak_rowboundary: Path) -> None:
    """Overflow rows: column 'a' stays in-row and must decode correctly.

    SQL Server keeps 'a' (4000 bytes) in-row and overflows only 'b'.
    This test verifies that the parser correctly reads the in-row portion
    even for rows that have an overflow pointer in the variable section.
    """
    a_len, _ = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    a_val = row["a"]
    a_type = type(a_val).__name__
    a_len_actual = len(a_val) if isinstance(a_val, (str, bytes)) else "N/A"
    assert a_val == "A" * a_len, (
        f"id={rid}: expected 'A'×{a_len}, got type={a_type} len={a_len_actual}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(OVERFLOW_ROWS))
def test_rb_overflow_b_value(rid: int, fixture_bak_rowboundary: Path) -> None:
    """Overflow rows: column 'b' must decode to REPLICATE('B', b_len)."""
    _, b_len = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    b_val = row["b"]
    b_type = type(b_val).__name__
    b_len_actual = len(b_val) if isinstance(b_val, (str, bytes)) else "N/A"
    assert b_val == "B" * b_len, (
        f"id={rid}: expected 'B'×{b_len}, got type={b_type} len={b_len_actual}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("rid", sorted(OVERFLOW_ROWS))
def test_rb_overflow_b_length(rid: int, fixture_bak_rowboundary: Path) -> None:
    """Overflow rows: LEN(b) must equal the defined b_len."""
    _, b_len = _OVERFLOW_ROW_DEFS[rid]
    rows = _rows(fixture_bak_rowboundary, "rb_overflow")
    row = next(r for r in rows if r["id"] == rid)
    actual_b = row["b"]
    actual_len = len(actual_b) if isinstance(actual_b, (str, bytes)) else -1
    assert actual_len == b_len, (
        f"id={rid}: expected len(b)={b_len}, got {actual_len}"
    )


# ---------------------------------------------------------------------------
# rb_lob — LOB single-page / two-page boundary: EXPECTED TO PASS
# All five blob sizes should decode correctly with the existing LOB stitcher.
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_rb_lob_row_count(fixture_bak_rowboundary: Path) -> None:
    """rb_lob must contain exactly one row per defined blob size."""
    rows = _rows(fixture_bak_rowboundary, "rb_lob")
    assert len(rows) == len(LOB_ROW_SIZES)


@pytest.mark.fixture
def test_rb_lob_ids_present(fixture_bak_rowboundary: Path) -> None:
    """Every expected id (1–5) must appear in rb_lob."""
    rows = _rows(fixture_bak_rowboundary, "rb_lob")
    ids = {r["id"] for r in rows}
    assert ids == set(LOB_ROW_SIZES)


@pytest.mark.fixture
@pytest.mark.parametrize("rid,expected_len", sorted(LOB_ROW_SIZES.items()))
def test_rb_lob_value_length(rid: int, expected_len: int, fixture_bak_rowboundary: Path) -> None:
    """rb_lob: decoded blob length must match the inserted byte count.

    id=1 (8094): one LOB page, not full.
    id=2 (8095): one LOB page, one byte short of full.
    id=3 (8096): exactly one LOB page.
    id=4 (8097): two LOB pages needed (+1 byte).
    id=5 (8098): two LOB pages needed (+2 bytes).
    """
    rows = _rows(fixture_bak_rowboundary, "rb_lob")
    row = next(r for r in rows if r["id"] == rid)
    val = row["val"]
    assert isinstance(val, (bytes, bytearray)), (
        f"id={rid}: expected bytes, got {type(val)}"
    )
    assert len(val) == expected_len, (
        f"id={rid}: expected {expected_len} bytes, got {len(val)}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("rid,expected_len", sorted(LOB_ROW_SIZES.items()))
def test_rb_lob_value_content(rid: int, expected_len: int, fixture_bak_rowboundary: Path) -> None:
    """rb_lob: decoded blob must consist entirely of 0x41 ('A') bytes."""
    rows = _rows(fixture_bak_rowboundary, "rb_lob")
    row = next(r for r in rows if r["id"] == rid)
    val = row["val"]
    if not isinstance(val, (bytes, bytearray)):
        pytest.fail(f"id={rid}: expected bytes, got {type(val)}")
    unique_bytes = set(val)
    assert unique_bytes == {0x41}, (
        f"id={rid}: expected all 0x41 bytes, got unique bytes: {unique_bytes!r}"
    )


@pytest.mark.fixture
def test_rb_lob_delta_extraction_stitches_max_lob(
    fixture_bak_rowboundary: Path, tmp_path: Path
) -> None:
    """Delta extraction must not leak varbinary(max) LOB root-pointer bytes."""
    extract_bak_to_delta(fixture_bak_rowboundary, tmp_path / "delta")
    dt = deltalake.DeltaTable(str(tmp_path / "delta" / "dbo" / "rb_lob"))
    rows = {r["id"]: r["val"] for r in dt.to_pyarrow_table().to_pylist()}
    assert set(rows) == set(LOB_ROW_SIZES)
    for rid, expected_len in sorted(LOB_ROW_SIZES.items()):
        val = rows[rid]
        assert isinstance(val, (bytes, bytearray))
        assert len(val) == expected_len
        assert set(val) == {0x41}


# ---------------------------------------------------------------------------
# rb_page_fill — slot-array capacity: EXPECTED TO PASS
# 216 fixed-width rows across 3 full data pages.
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_rb_page_fill_total_count(fixture_bak_rowboundary: Path) -> None:
    """rb_page_fill: all 216 rows must be readable (3 pages × 72 rows/page)."""
    rows = _rows(fixture_bak_rowboundary, "rb_page_fill")
    assert len(rows) == PAGE_FILL_ROWS, (
        f"expected {PAGE_FILL_ROWS} rows ({ROWS_PER_PAGE}/page × 3 pages), "
        f"got {len(rows)}"
    )


@pytest.mark.fixture
def test_rb_page_fill_ids_sequential(fixture_bak_rowboundary: Path) -> None:
    """rb_page_fill: ids must cover 1 .. PAGE_FILL_ROWS without gaps or duplicates."""
    rows = _rows(fixture_bak_rowboundary, "rb_page_fill")
    ids = sorted(r["id"] for r in rows)
    assert ids == list(range(1, PAGE_FILL_ROWS + 1)), (
        f"non-sequential ids: first gap at "
        f"{next((i for i, v in enumerate(ids, 1) if v != i), 'none')}"
    )


@pytest.mark.fixture
def test_rb_page_fill_val_content(fixture_bak_rowboundary: Path) -> None:
    """rb_page_fill: every row's val must be REPLICATE('X', 100)."""
    rows = _rows(fixture_bak_rowboundary, "rb_page_fill")
    expected = "X" * 100
    bad = [r["id"] for r in rows if r["val"] != expected]
    assert not bad, f"{len(bad)} rows have wrong val: ids {bad[:5]}…"


@pytest.mark.fixture
def test_rb_page_fill_last_row(fixture_bak_rowboundary: Path) -> None:
    """rb_page_fill: the last row (id=216, last slot on page 3) must be correct."""
    rows = _rows(fixture_bak_rowboundary, "rb_page_fill")
    last = next((r for r in rows if r["id"] == PAGE_FILL_ROWS), None)
    assert last is not None, f"row id={PAGE_FILL_ROWS} not found"
    assert last["val"] == "X" * 100


@pytest.mark.fixture
def test_rb_page_fill_page_boundary_rows(fixture_bak_rowboundary: Path) -> None:
    """rb_page_fill: rows at page-boundary positions (72, 73, 144, 145) must decode."""
    boundary_ids = {ROWS_PER_PAGE, ROWS_PER_PAGE + 1, ROWS_PER_PAGE * 2, ROWS_PER_PAGE * 2 + 1}
    rows = _rows(fixture_bak_rowboundary, "rb_page_fill")
    row_map = {r["id"]: r for r in rows}
    missing = boundary_ids - set(row_map)
    assert not missing, f"page-boundary rows not found: {missing}"
    bad = [rid for rid in boundary_ids if row_map[rid]["val"] != "X" * 100]
    assert not bad, f"wrong val at page-boundary ids: {bad}"
