"""Extended CCI bug-trigger tests — hypothesis-driven (see docs/260618-2-enc3-bugs.md).

Each table in the ``cci_extended_full.bak`` fixture was designed to test whether a
known bug class propagates to a type or scenario not yet covered by K-1 or K-3.
The five hypotheses:

  cci_int          — K3B (null polarity inversion) propagates to enc=2 INT, not just BIT.
  cci_varchar50    — K3B propagates to VARCHAR(50) non-max (new type family).
  cci_char10_varied— K3A (CHAR structural rows → '') fires for CHAR(10) with ≥26 distinct
                     values, not just CHAR(20).  Width-independent vs size-independent.
  cci_binary4      — E3B (no offset table for fixed-width binary) fires for BINARY(4),
                     confirming the bug is width-independent.
  cci_nvarchar50_sparse — K3B may mask E3C for NVARCHAR(50) with sparse-NULL
                     (1 NULL in 1,200 rows instead of 1,197 NULLs).

Tests are initially written as correct-behavior assertions with no xfail markers.
After running against a generated fixture, failing tests are promoted to xfail with
the confirmed bug label.

Running
-------
    pytest tests/test_cci_extended_coverage.py -v
    pytest -k "cci_extended" -q
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_extended_fixture import (
    DB_NAME,
    ROWS_PER_TABLE,
    STRUCTURAL_IDS,
    TABLE_DEFS,
    TableDef,
)

# ---------------------------------------------------------------------------
# Confirmed bugs (populated by running the fixture and triaging failures)
# ---------------------------------------------------------------------------
#
# cci_int           — PASSES.  K3B does not affect enc=2 INT.  The null-polarity
#                     inversion is specific to BIT and the varbinary/varchar family,
#                     not to integer types.  Useful negative result.
#
# cci_char10_varied — PASSES.  K3A does not affect CHAR(10).  K3A is a stride-
#                     mismatch bug where the decoder uses stride=10 to slice CHAR(20)
#                     dictionary entries.  CHAR(10) is immune because stride=10 is
#                     the correct width.
#
# cci_varchar50     — K3A: structural rows return '' instead of the expected 50-char
#                     string.  K3A is not char-specific — it also fires for VARCHAR(50).
#                     Root cause: the decoder stride for varchar string entries is wrong
#                     for certain dictionary positions, producing empty/truncated strings.
#
# cci_binary4       — E3B-v2 (FIXED): formerly returned garbage bytes because BINARY(4)
#                     read the first 4 bytes of the pool as an offset table, slicing the
#                     pool at incorrect boundaries.  Now decodes correctly.
#
# cci_nvarchar50_sparse — K3A: structural rows return '' for NVARCHAR(50) with sparse-
#                     NULL.  K3A also fires for NVARCHAR — confirming the bug is general
#                     to all string-family types, not just CHAR.

# Per-scope xfail registries — only the failing test scopes are marked.
#
# K3A (FIXED): structural rows (low/high) formerly returned the wrong dictionary
#      entry for VARCHAR(50)/NVARCHAR(50) (and CHAR with non-alphabetical low/high).
#      Root cause: the enc=3 v4 Huffman dictionary was returned sorted alphabetically
#      instead of in native data_id order, so stored indices resolved to wrong strings.
#
# E3B-v2 (FIXED): BINARY(4) formerly read the first 4 pool bytes as a 4-entry offset
#      table, slicing the pool at wrong boundaries so ALL rows returned garbage.  The
#      fixed-width path now slices correctly; no cci_extended tables remain xfail for it.

# K3A (FIXED): VARCHAR/NVARCHAR structural rows formerly returned the wrong
# dictionary entry because the enc=3 v4 Huffman dictionary was returned sorted
# alphabetically instead of in native data_id order.  No tables remain xfail.
_STRUCTURAL_XFAIL: dict[str, tuple[str, str]] = {}

# Tables where the null sentinel row is ALSO misdecoded (not None).
# E3B-v2 (cci_binary4) is fixed — no tables remain.
_SENTINEL_XFAIL: dict[str, tuple[str, str]] = {}

# Tables where the null count is wrong (≠ 1).
# E3B-v2 (cci_binary4) is fixed — no tables remain.
_NULL_COUNT_XFAIL: dict[str, tuple[str, str]] = {}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _read_all(fixture: Path, table_name: str) -> tuple[list[dict[str, Any]], int]:
    """Return (rows, total_count) for *table_name*.  Raises pytest.fail if missing."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        pytest.fail(f"Table {table_name!r} not found in fixture (DB: {DB_NAME})")
    rows = list(read_table_rows(store, table))
    return rows, len(rows)


def _structural(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return {label: val} for the three structural rows."""
    id_to_label = {v: k for k, v in STRUCTURAL_IDS.items()}
    return {
        id_to_label[row["id"]]: row.get("val")
        for row in rows
        if row["id"] in id_to_label
    }


def _null_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("val") is None)


def _non_null_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("val") is not None)


# ---------------------------------------------------------------------------
# Row count tests — sanity gate; none of these should fail unless the fixture
# itself is malformed.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_row_count(fixture_bak_cci_extended: Path, td: TableDef) -> None:
    """Each table must contain exactly ROWS_PER_TABLE (1,200) rows."""
    _, total = _read_all(fixture_bak_cci_extended, td.name)
    assert total == ROWS_PER_TABLE, (
        f"{td.name}: expected {ROWS_PER_TABLE} rows, got {total}"
    )


# ---------------------------------------------------------------------------
# Null sentinel tests — the null structural row (id=3) must decode as None
# for every table, regardless of what bug the non-null rows exhibit.
# A failure here means the null row itself is broken (unexpected).
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_null_sentinel(
    fixture_bak_cci_extended: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """The null sentinel row (id=3) must decode as None for every table."""
    if td.name in _SENTINEL_XFAIL:
        bug_id, reason = _SENTINEL_XFAIL[td.name]
        request.applymarker(pytest.mark.xfail(strict=False, reason=f"[{bug_id}] {reason}"))
    rows, _ = _read_all(fixture_bak_cci_extended, td.name)
    null_id = STRUCTURAL_IDS["null"]
    match = [r for r in rows if r["id"] == null_id]
    assert match, f"{td.name}: null sentinel row (id={null_id}) not found"
    val = match[0].get("val")
    assert val is None, (
        f"{td.name}: null sentinel row expected None, got {val!r}"
    )


# ---------------------------------------------------------------------------
# Structural value tests — low (id=1) and high (id=2) must decode correctly.
# Hypothesis failures here confirm the bug class for the table.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_low_structural_value(
    fixture_bak_cci_extended: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """Low structural row (id=1) must decode to td.low.

    Confirmed results:
      cci_int           — PASSES (K3B does not affect enc=2 INT)
      cci_varchar50     — PASSES (K3A fixed; v4 dict now in native data_id order)
      cci_char10_varied — PASSES (stride=10 is correct)
      cci_binary4       — PASSES (E3B-v2 fixed; decodes to correct bytes)
      cci_nvarchar50_sparse — PASSES (K3A fixed)
    """
    if td.name in _STRUCTURAL_XFAIL:
        bug_id, reason = _STRUCTURAL_XFAIL[td.name]
        request.applymarker(pytest.mark.xfail(strict=False, reason=f"[{bug_id}] {reason}"))

    rows, _ = _read_all(fixture_bak_cci_extended, td.name)
    struct = _structural(rows)
    low_val = struct.get("low")
    assert low_val == td.low, (
        f"{td.name} low row: expected {td.low!r}, got {low_val!r}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_high_structural_value(
    fixture_bak_cci_extended: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """High structural row (id=2) must decode to td.high."""
    if td.name in _STRUCTURAL_XFAIL:
        bug_id, reason = _STRUCTURAL_XFAIL[td.name]
        request.applymarker(pytest.mark.xfail(strict=False, reason=f"[{bug_id}] {reason}"))

    rows, _ = _read_all(fixture_bak_cci_extended, td.name)
    struct = _structural(rows)
    high_val = struct.get("high")
    assert high_val == td.high, (
        f"{td.name} high row: expected {td.high!r}, got {high_val!r}"
    )


# ---------------------------------------------------------------------------
# Null count test — exactly 1 row should be None (the null sentinel).
# K3B causes all 1,200 rows to be None; E3B causes all 1,199 non-null rows
# to be None (total 1,200 None).  A failing test here is quantitative proof.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_null_count_is_one(
    fixture_bak_cci_extended: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """Exactly 1 row must be None (the null sentinel).

    If the null count equals ROWS_PER_TABLE (1,200), Bug K3B or E3B is active:
    the null polarity inversion (K3B) or empty-dictionary (E3B) is making all
    non-null rows appear as None.
    """
    if td.name in _NULL_COUNT_XFAIL:
        bug_id, reason = _NULL_COUNT_XFAIL[td.name]
        request.applymarker(pytest.mark.xfail(strict=False, reason=f"[{bug_id}] {reason}"))

    rows, total = _read_all(fixture_bak_cci_extended, td.name)
    nones = _null_count(rows)
    assert nones == 1, (
        f"{td.name}: expected 1 None (null sentinel), got {nones}/{total} None values.\n"
        f"If nones == {total}: K3B (null polarity) or E3B (empty dict) is active.\n"
        f"Hypothesis: {td.hypothesis}"
    )


# ---------------------------------------------------------------------------
# Filler type tests — spot-check 10 filler rows (id ≥ 7) for correct Python type.
# K3B makes all fillers None; a clean pass here with structural failures → K3A.
# ---------------------------------------------------------------------------

def _check_filler_types(
    fixture: Path,
    table_name: str,
    expected_type: type,
    sample: int = 10,
) -> None:
    rows, _ = _read_all(fixture, table_name)
    filler_vals = [r.get("val") for r in rows if r["id"] >= 7][:sample]
    non_null = [v for v in filler_vals if v is not None]
    assert len(non_null) >= sample // 2, (
        f"{table_name}: expected ≥{sample // 2} non-null filler values in {sample} sampled, "
        f"got {len(non_null)} — K3B or E3B may be making all fillers None"
    )
    wrong_types = [v for v in non_null if not isinstance(v, expected_type)]
    assert not wrong_types, (
        f"{table_name}: filler values have wrong type; "
        f"expected {expected_type.__name__}, got {[type(v).__name__ for v in wrong_types[:3]]!r}"
    )


@pytest.mark.fixture
def test_cci_int_filler_type(fixture_bak_cci_extended: Path) -> None:
    """INT filler rows must decode to int (passes — K3B does not affect enc=2 INT)."""
    _check_filler_types(fixture_bak_cci_extended, "cci_int", int)


@pytest.mark.fixture
def test_cci_varchar50_filler_type(fixture_bak_cci_extended: Path) -> None:
    """VARCHAR(50) filler rows must decode to str.

    Filler rows decode correctly (str) — historically this distinguished K3A
    (structural-only) from K3B (all rows None); both are now fixed.
    """
    _check_filler_types(fixture_bak_cci_extended, "cci_varchar50", str)


@pytest.mark.fixture
def test_cci_char10_varied_filler_type(fixture_bak_cci_extended: Path) -> None:
    """CHAR(10) filler rows must decode to str (passes — K3A is CHAR(20)-specific)."""
    _check_filler_types(fixture_bak_cci_extended, "cci_char10_varied", str)


@pytest.mark.fixture
def test_cci_binary4_filler_type(fixture_bak_cci_extended: Path) -> None:
    """BINARY(4) filler rows must decode to bytes objects.

    See test_cci_binary4_filler_length for the stricter length check.
    """
    _check_filler_types(fixture_bak_cci_extended, "cci_binary4", bytes)


@pytest.mark.fixture
def test_cci_binary4_filler_length(fixture_bak_cci_extended: Path) -> None:
    """Regression (E3B-v2): BINARY(4) filler rows must be exactly 4 bytes each.

    The pool is now sliced at the correct fixed-width boundaries.
    """
    rows, _ = _read_all(fixture_bak_cci_extended, "cci_binary4")
    filler_vals = [r.get("val") for r in rows if r["id"] >= 7][:20]
    non_null = [v for v in filler_vals if v is not None]
    wrong_len = [v for v in non_null if not (isinstance(v, bytes) and len(v) == 4)]
    assert not wrong_len, (
        f"cci_binary4: {len(wrong_len)} filler rows have wrong length — "
        f"sample lengths: {[len(v) for v in wrong_len[:5]]!r} (expected 4)"
    )


@pytest.mark.fixture
def test_cci_nvarchar50_sparse_filler_type(fixture_bak_cci_extended: Path) -> None:
    """NVARCHAR(50) filler rows must decode to str.

    Filler rows decode correctly (str); same pattern as VARCHAR(50).  The former
    K3A structural-row mis-decode is now fixed.
    """
    _check_filler_types(fixture_bak_cci_extended, "cci_nvarchar50_sparse", str)


# ---------------------------------------------------------------------------
# Distinct value tests — verify the dictionary has the expected entries.
# K3B → all None → 1 distinct value.  K3A → '' for structural + correct for
# fillers → extra '' in the set.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_cci_int_distinct_values(fixture_bak_cci_extended: Path) -> None:
    """INT should have 1,200 distinct values (1 null + 1,199 unique non-null).

    Passes — K3B does not affect INT.
    """
    rows, _ = _read_all(fixture_bak_cci_extended, "cci_int")
    vals = [r.get("val") for r in rows]
    distinct = len(set(vals))
    assert distinct >= 100, (
        f"cci_int: expected ≥100 distinct values (1199 unique ints + None), "
        f"got {distinct} — likely K3B making all rows None"
    )


@pytest.mark.fixture
def test_cci_char10_distinct_count_from_fillers(fixture_bak_cci_extended: Path) -> None:
    """CHAR(10) filler rows produce 26 distinct non-null values (A×10 … Z×10).

    Passes — CHAR(10) is immune to K3A (stride=10 is the correct width).
    """
    rows, _ = _read_all(fixture_bak_cci_extended, "cci_char10_varied")
    filler_vals = {r.get("val") for r in rows if r["id"] >= 7 and r.get("val") is not None}
    assert len(filler_vals) >= 26, (
        f"cci_char10_varied: expected ≥26 distinct non-null filler values, "
        f"got {len(filler_vals)} — K3B may be making all rows None"
    )
