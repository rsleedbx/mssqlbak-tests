"""CCI one-table-per-type coverage tests (Gap K-3).

Validates that the CCI segment decoder correctly handles five types that either
lack large-row-group coverage entirely or need testing with a realistic mix of
distinct non-null values:

  CHAR(20)        — fixed-stride dictionary, 26+ distinct values
  VARBINARY(16)   — variable-length binary pool (first compressed-segment coverage
                    for this type family — not present in the K-1 type matrix)
  BIT             — boolean bitpack, ~50/50 TRUE/FALSE split
  BINARY(16)      — fixed-width binary pool (E3B — fixed)
  UNIQUEIDENTIFIER— fixed 16-byte pool, enc=5 Format C (K3C false-ARCHIVE crash — fixed)

Each table has 1,200 rows: 3 structural rows (low id=1, high id=2, null id=3)
plus 1,197 non-null filler rows (id 7–1,203).  A REORGANIZE flushes all rows
into a compressed segment before backup.

Running
-------
    pytest tests/test_cci_types_large_coverage.py -v
    pytest -k "cci_types_large" -q
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_types_large_fixture import (
    DB_NAME,
    ROWS_PER_TABLE,
    STRUCTURAL_IDS,
    TABLE_DEFS,
    TableDef,
)

# ---------------------------------------------------------------------------
# Known-bug xfail sets
# ---------------------------------------------------------------------------

# Tables for which the CCI segment decoder returns wrong values or crashes.
# Bugs from K-1 (docs/260618-2-enc3-bugs.md): E3A, E3B.
# New bugs revealed by K-3 (varied non-null fillers, one-table-per-type):
#
#   K3A — CHAR(20) structural rows return '' (empty) instead of the actual string.
#          Likely a dictionary index vs entry-length bug when 26+ distinct char
#          values are present and the structural 'L' value shares a dictionary
#          slot that resolves to an empty prefix.
#
#   K3B — VARBINARY(16) and BIT return None for ALL non-null rows when the null
#          bit-vector is sparse (only 1 NULL out of 1,200 rows).  The null-bit
#          polarity is inverted: 0=null is read as 1=null, so all 1,199 non-null
#          rows appear as NULL.
#
#   K3C — UNIQUEIDENTIFIER (FIXED): formerly crashed with ValueError "bytes_le is
#          not a 16-char string".  Root cause was NOT E3A as_bytes — the enc=5
#          segment is Format C (h92=0, u16@38 == n_rows), but the Format-C-priority
#          pre-check only covered BINARY/VARBINARY, so UNIQUEIDENTIFIER fell through
#          to the ARCHIVE type-2 heuristic which misfired (a 0xFFFF byte in the XPRESS
#          stream + a coincidental n_rows u32 + a 16-divisible pool) and produced
#          variable-width garbage that crashed _decode_uuid.  Adding UNIQUEIDENTIFIER
#          to the Format-C-priority set fixes it.
# All K-3 tables now decode correctly via the enc=5 Format C path; no xfail tables remain.
_XFAIL_TABLES: frozenset[str] = frozenset()

# No table crashes the decoder any more.
_CRASH_TABLES: frozenset[str] = frozenset()

_XFAIL_REASON: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_structural(fixture: Path, table_name: str) -> dict[str, Any]:
    """Return {label: decoded_value} for the 3 structural rows of *table_name*.

    Only rows with id in STRUCTURAL_IDS values are considered; filler rows
    (id 7–1,203) are ignored.
    """
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        pytest.fail(f"Table {table_name!r} not found in fixture (DB: {DB_NAME})")

    id_to_label = {v: k for k, v in STRUCTURAL_IDS.items()}
    result: dict[str, Any] = {}
    count = 0
    for row in read_table_rows(store, table):
        count += 1
        row_id = row["id"]
        label = id_to_label.get(row_id)
        if label is not None:
            result[label] = row.get("val")

    # Attach total count for the row-count test
    result["__count__"] = count
    return result


# ---------------------------------------------------------------------------
# Row count tests (one per table)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_row_count(
    fixture_bak_cci_types_large: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """Each table must have exactly ROWS_PER_TABLE (1,200) rows after REORGANIZE.

    All types decode without crashing.  (cci_uuid formerly crashed here — Bug K3C,
    now fixed by routing enc=5 Format C UNIQUEIDENTIFIER away from the ARCHIVE path.)
    """
    if td.name in _CRASH_TABLES:
        request.applymarker(pytest.mark.xfail(
            strict=False,
            reason=_XFAIL_REASON[td.name],
        ))
    decoded = _read_structural(fixture_bak_cci_types_large, td.name)
    count = decoded["__count__"]
    assert count == ROWS_PER_TABLE, (
        f"{td.name}: expected {ROWS_PER_TABLE} rows, got {count}"
    )


# ---------------------------------------------------------------------------
# Structural row tests (low / high / null) for passing types
# ---------------------------------------------------------------------------

def _assert_structural(
    fixture: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """Check low/high/null structural rows for *td*, applying xfail where known buggy."""
    xfail = td.name in _XFAIL_TABLES
    if xfail:
        request.applymarker(pytest.mark.xfail(
            strict=False,
            reason=_XFAIL_REASON[td.name],
        ))

    decoded = _read_structural(fixture, td.name)

    # null row
    null_val = decoded.get("null")
    assert null_val is None, (
        f"{td.name} null row: expected None, got {null_val!r}"
    )

    # low row
    low_val = decoded.get("low")
    assert low_val == td.low, (
        f"{td.name} low row: expected {td.low!r}, got {low_val!r}"
    )

    # high row
    high_val = decoded.get("high")
    assert high_val == td.high, (
        f"{td.name} high row: expected {td.high!r}, got {high_val!r}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_structural_rows(
    fixture_bak_cci_types_large: Path,
    td: TableDef,
    request: pytest.FixtureRequest,
) -> None:
    """Structural rows (low/high/null) must decode to their reference values.

    All K-3 types (cci_char, cci_varbinary, cci_binary, cci_bit, cci_uuid) now pass;
    the former E3B (cci_binary) and K3C (cci_uuid) bugs are fixed.
    """
    _assert_structural(fixture_bak_cci_types_large, td, request)


# ---------------------------------------------------------------------------
# Type-specific sanity tests for the passing types
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_k3a_char_null_row_is_correct_none(fixture_bak_cci_types_large: Path) -> None:
    """Prove K3A is a dictionary/value bug, NOT a null-polarity bug.

    cci_char's null sentinel (id=3) returns None correctly, while structural
    non-null rows (id=1 and id=2) return '' (Bug K3A).  This distinguishes K3A
    from Bug K3B where ALL rows (including non-null ones) return None.
    """
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_char"), None)
    if table is None:
        pytest.fail("cci_char not found")

    null_row_val: Any = "sentinel_not_found"
    for row in read_table_rows(store, table):
        if row["id"] == STRUCTURAL_IDS["null"]:
            null_row_val = row.get("val")
            break

    assert null_row_val == "sentinel_not_found" or null_row_val is None, (
        f"cci_char null row (id={STRUCTURAL_IDS['null']}): "
        f"expected None, got {null_row_val!r}"
    )
    if null_row_val == "sentinel_not_found":
        pytest.fail(f"cci_char: null sentinel row (id={STRUCTURAL_IDS['null']}) not found in segment")
    # If we reach here, null_row_val is None — correct.


@pytest.mark.fixture
def test_k3b_varbinary_none_count_equals_all_rows(fixture_bak_cci_types_large: Path) -> None:
    """Regression guard (formerly K3B): exactly 1 of 1,200 cci_varbinary rows is None.

    With 1 NULL in 1,200 rows the correct state is exactly 1 None (the null
    sentinel).  Previously the enc=5 Format C VARBINARY pool failed to decode and
    every row returned None; the variable-length pool fix restores correct values.
    """
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_varbinary"), None)
    if table is None:
        pytest.fail("cci_varbinary not found")

    total = none_count = 0
    for row in read_table_rows(store, table):
        total += 1
        if row.get("val") is None:
            none_count += 1

    # Bug K3B active: none_count == 1200.  Correct: none_count == 1.
    assert none_count == 1, (
        f"Bug K3B: cci_varbinary has {none_count}/{total} None values "
        f"(expected 1 — only the null sentinel row)"
    )


@pytest.mark.fixture
def test_k3b_bit_none_count_equals_all_rows(fixture_bak_cci_types_large: Path) -> None:
    """Regression guard (formerly K3B): exactly 1 of 1,200 cci_bit rows is None."""
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_bit"), None)
    if table is None:
        pytest.fail("cci_bit not found")

    total = none_count = 0
    for row in read_table_rows(store, table):
        total += 1
        if row.get("val") is None:
            none_count += 1

    # Bug K3B active: none_count == 1200.  Correct: none_count == 1.
    assert none_count == 1, (
        f"Bug K3B: cci_bit has {none_count}/{total} None values "
        f"(expected 1 — only the null sentinel row)"
    )


@pytest.mark.fixture
def test_cci_char_filler_rows_non_null(fixture_bak_cci_types_large: Path) -> None:
    """Spot-check that a sample of cci_char filler rows are non-null strings."""
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_char"), None)
    if table is None:
        pytest.fail("cci_char not found")

    filler_vals: list[Any] = []
    for row in read_table_rows(store, table):
        if row["id"] >= 7:
            filler_vals.append(row.get("val"))
            if len(filler_vals) >= 26:
                break

    non_null = [v for v in filler_vals if v is not None]
    assert len(non_null) >= 20, (
        f"cci_char: expected ≥20 non-null filler values in first 26 checked, "
        f"got {len(non_null)}; multi-entry char dictionary may be broken"
    )
    assert all(isinstance(v, str) for v in non_null), (
        f"cci_char: filler values should be str, got types: "
        f"{[type(v).__name__ for v in non_null[:5]]!r}"
    )


@pytest.mark.fixture
def test_cci_varbinary_filler_rows_are_bytes(fixture_bak_cci_types_large: Path) -> None:
    """Regression guard (formerly K3B): cci_varbinary filler rows decode to bytes."""
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_varbinary"), None)
    if table is None:
        pytest.fail("cci_varbinary not found")

    filler_vals: list[Any] = []
    for row in read_table_rows(store, table):
        if row["id"] >= 7:
            filler_vals.append(row.get("val"))
            if len(filler_vals) >= 10:
                break

    non_null = [v for v in filler_vals if v is not None]
    assert len(non_null) >= 8, (
        f"Bug K3B active: cci_varbinary filler rows return None (null-polarity inversion); "
        f"got {len(non_null)} non-null out of {len(filler_vals)} checked"
    )
    assert all(isinstance(v, bytes) for v in non_null), (
        f"cci_varbinary: filler values should be bytes, got types: "
        f"{[type(v).__name__ for v in non_null[:5]]!r}"
    )


@pytest.mark.fixture
def test_cci_bit_filler_has_both_values(fixture_bak_cci_types_large: Path) -> None:
    """Regression guard (formerly K3B): cci_bit filler rows include True and False."""
    store = PageStore.from_bak(fixture_bak_cci_types_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == "cci_bit"), None)
    if table is None:
        pytest.fail("cci_bit not found")

    trues = falses = nones = 0
    for row in read_table_rows(store, table):
        if row["id"] >= 7:
            val = row.get("val")
            if val is True:
                trues += 1
            elif val is False:
                falses += 1
            else:
                nones += 1
            if trues >= 10 and falses >= 10:
                break

    assert trues >= 10, (
        f"Bug K3B active: cci_bit expected ≥10 True filler rows, got {trues} "
        f"(None={nones}, False={falses}); null-polarity inversion makes all non-null appear NULL"
    )
    assert falses >= 10, (
        f"cci_bit: expected ≥10 False filler rows, got {falses}"
    )
