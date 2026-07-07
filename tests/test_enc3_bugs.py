"""Regression tests for the enc=3 CCI dictionary decoder (docs/260618-2-enc3-bugs.md).

The K-1 fixture (tabletype_cci_large_full.bak, 1,200 rows) produces real enc=3
compressed segments for string and binary column types.  Three bugs in
_decode_enc3 / _parse_dict_strings used to make five types decode to wrong values;
all three are now fixed and these tests guard against regression.

Bugs fixed (formerly tracked here as xfail)
-------------------------------------------
  E3A — Wrong ``as_bytes`` flag for DECIMAL / DATETIMEOFFSET / UNIQUEIDENTIFIER
        Binary dictionary entries were mis-parsed as Latin-1 text strings.

  E3B — Fixed-length BINARY dictionary returned empty list
        _parse_dict_strings walked offset tables designed for variable-length data;
        fixed-width binary(8) has no offset table, so the walk produced no entries,
        causing every non-NULL row to decode as None.

  E3C — Compact RLE null vector confused NULL rows with empty-string rows
        The null flag for the ``null`` structural row was not detected, so the row was
        looked up in the dictionary and returned '' (the dictionary entry for index 0,
        which is the empty string).

The remaining enc=3 binary crash on a 1,200-entry UNIQUEIDENTIFIER dictionary
(Bug K3C, ``cci_uuid``) is tracked in tests/test_cci_types_large_coverage.py.

Running
-------
    pytest tests/test_enc3_bugs.py -v
    pytest -k "enc3" -q
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.tabletypematrix import LABEL_ID, ORG_CASES, table_name

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TABLE_NAME = table_name(next(o for o in ORG_CASES if o.name == "column"))  # "tt_column"
_ID_TO_LABEL = {v: k for k, v in LABEL_ID.items()}  # {1: "low", 2: "high", ...}

# Reference values for the five bug types (from tools/typematrix.py).
_REF: dict[str, dict[str, Any]] = {
    "decimal_38_10": {
        "low":  Decimal("-9999999999999999999999999999.9999999999"),
        "high": Decimal("9999999999999999999999999999.9999999999"),
        "mid":  Decimal("1054018882445449168662432969"),
        "null": None,
    },
    "datetimeoffset_7": {
        # Only the low/null rows are checked here; mid has a non-UTC offset
        # which is harder to express compactly.
        "low":  __import__("datetime").datetime(1, 1, 1, 0, 0,
                    tzinfo=__import__("datetime").timezone.utc),
        "null": None,
    },
    "uniqueidentifier": {
        "low":  uuid.UUID("00000000-0000-0000-0000-000000000000"),
        "high": uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
        "null": None,
    },
    "binary_8": {
        "low":  b"\x00" * 8,
        "high": b"\xff" * 8,
        "null": None,
    },
    "nvarchar_50": {
        "low":  "",
        "high": "N" * 50,
        "null": None,
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_col(fixture: Path, col_name: str) -> dict[str, Any]:
    """Return {label: decoded_value} for *col_name* in tt_column.

    Only structural rows (id 1-4) are returned; filler rows are ignored.
    """
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == _TABLE_NAME), None)
    if table is None:
        pytest.fail(f"Table {_TABLE_NAME!r} not found in fixture")

    result: dict[str, Any] = {}
    for row in read_table_rows(store, table):
        row_id: int = row["id"]
        label = _ID_TO_LABEL.get(row_id)
        if label is None:
            continue  # filler row — skip
        if col_name in row:
            result[label] = row[col_name]
    return result


def _assert_col(
    fixture: Path,
    type_name: str,
    *,
    labels: list[str] | None = None,
) -> None:
    """Assert that *type_name* decodes to its reference values for *labels*."""
    col_name = f"c_{type_name}"
    decoded = _read_col(fixture, col_name)
    ref = _REF[type_name]
    for label in (labels or list(ref.keys())):
        if label not in ref:
            continue
        expected = ref[label]
        actual = decoded.get(label, "<MISSING>")
        if expected is None:
            assert actual is None, (
                f"c_{type_name} label={label!r}: expected None, got {actual!r}"
            )
        else:
            assert actual == expected, (
                f"c_{type_name} label={label!r}: expected {expected!r}, got {actual!r}"
            )


# ---------------------------------------------------------------------------
# Bug E3A — DECIMAL
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_e3a_decimal_low(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3A: decimal_38_10 low row should decode to a Decimal, not a str."""
    _assert_col(fixture_bak_tabletype_cci_large, "decimal_38_10", labels=["low"])


@pytest.mark.fixture
def test_e3a_decimal_high(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3A: decimal_38_10 high row should decode to a Decimal, not a str."""
    _assert_col(fixture_bak_tabletype_cci_large, "decimal_38_10", labels=["high"])


@pytest.mark.fixture
def test_e3a_decimal_null(fixture_bak_tabletype_cci_large: Path) -> None:
    """Null row for decimal_38_10 is None even with Bug E3A present (null bit is detected)."""
    _assert_col(fixture_bak_tabletype_cci_large, "decimal_38_10", labels=["null"])


@pytest.mark.fixture
def test_e3a_decimal_returned_type_is_not_decimal(fixture_bak_tabletype_cci_large: Path) -> None:
    """Regression (E3A): decoder returns a Decimal (not str) for enc=3 segments."""
    col = _read_col(fixture_bak_tabletype_cci_large, "c_decimal_38_10")
    low_val = col.get("low")
    assert isinstance(low_val, Decimal), (
        f"Bug E3A active: c_decimal_38_10 low decoded as {type(low_val).__name__!r} "
        f"(value={low_val!r}); expected Decimal"
    )


# ---------------------------------------------------------------------------
# Bug E3A — DATETIMEOFFSET
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_e3a_datetimeoffset_low(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3A: datetimeoffset_7 low row should decode to datetime(tzinfo=utc), not str."""
    _assert_col(fixture_bak_tabletype_cci_large, "datetimeoffset_7", labels=["low"])


@pytest.mark.fixture
def test_e3a_datetimeoffset_null(fixture_bak_tabletype_cci_large: Path) -> None:
    """Null row for datetimeoffset_7 is None even with Bug E3A present (null bit is detected)."""
    _assert_col(fixture_bak_tabletype_cci_large, "datetimeoffset_7", labels=["null"])


@pytest.mark.fixture
def test_e3a_datetimeoffset_returned_type_is_not_datetime(
    fixture_bak_tabletype_cci_large: Path,
) -> None:
    """Regression (E3A): decoder returns a datetime (not str) for datetimeoffset enc=3."""
    import datetime

    col = _read_col(fixture_bak_tabletype_cci_large, "c_datetimeoffset_7")
    low_val = col.get("low")
    assert isinstance(low_val, datetime.datetime), (
        f"Bug E3A active: c_datetimeoffset_7 low decoded as {type(low_val).__name__!r} "
        f"(value={low_val!r}); expected datetime"
    )


# ---------------------------------------------------------------------------
# Bug E3A — UNIQUEIDENTIFIER
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_e3a_uniqueidentifier_low(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3A: uniqueidentifier low row should decode to UUID('00000000-…'), not ''."""
    _assert_col(fixture_bak_tabletype_cci_large, "uniqueidentifier", labels=["low"])


@pytest.mark.fixture
def test_e3a_uniqueidentifier_high(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3A: uniqueidentifier high row should decode to UUID('ffffffff-…'), not str."""
    _assert_col(fixture_bak_tabletype_cci_large, "uniqueidentifier", labels=["high"])


@pytest.mark.fixture
def test_e3a_uniqueidentifier_null(fixture_bak_tabletype_cci_large: Path) -> None:
    """Null row for uniqueidentifier is None even with Bug E3A present (null bit is detected)."""
    _assert_col(fixture_bak_tabletype_cci_large, "uniqueidentifier", labels=["null"])


@pytest.mark.fixture
def test_e3a_uniqueidentifier_returned_type_is_not_uuid(
    fixture_bak_tabletype_cci_large: Path,
) -> None:
    """Regression (E3A): decoder returns a UUID (not '') for the all-zeros UUID in enc=3."""
    col = _read_col(fixture_bak_tabletype_cci_large, "c_uniqueidentifier")
    low_val = col.get("low")
    assert isinstance(low_val, uuid.UUID), (
        f"Bug E3A active: c_uniqueidentifier low decoded as {type(low_val).__name__!r} "
        f"(value={low_val!r}); expected UUID"
    )


# ---------------------------------------------------------------------------
# Bug E3B — BINARY(8)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_e3b_binary8_low_is_not_none(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3B: binary_8 low row should decode to b'\\x00'*8, not None."""
    _assert_col(fixture_bak_tabletype_cci_large, "binary_8", labels=["low"])


@pytest.mark.fixture
def test_e3b_binary8_high_is_not_none(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3B: binary_8 high row should decode to b'\\xff'*8, not None."""
    _assert_col(fixture_bak_tabletype_cci_large, "binary_8", labels=["high"])


@pytest.mark.fixture
def test_e3b_binary8_null_is_none(fixture_bak_tabletype_cci_large: Path) -> None:
    """Null row for binary_8 is None — correctly decoded regardless of Bug E3B."""
    _assert_col(fixture_bak_tabletype_cci_large, "binary_8", labels=["null"])


@pytest.mark.fixture
def test_e3b_binary8_empty_dictionary_causes_all_rows_none(
    fixture_bak_tabletype_cci_large: Path,
) -> None:
    """Regression (E3B): no non-NULL binary_8 structural row decodes as None.

    The fixed-width BINARY dictionary is now populated, so every non-NULL row
    decodes to its bytes rather than collapsing to None.
    """
    col = _read_col(fixture_bak_tabletype_cci_large, "c_binary_8")
    non_null_rows = {label: val for label, val in col.items() if label != "null"}
    none_rows = {label for label, val in non_null_rows.items() if val is None}
    assert not none_rows, (
        f"Bug E3B regressed: c_binary_8 non-NULL rows decoded as None: {sorted(none_rows)!r}. "
        "The fixed-width dictionary walk produced no entries."
    )


# ---------------------------------------------------------------------------
# Bug E3C — NVARCHAR(50)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_e3c_nvarchar_null_row_is_none(fixture_bak_tabletype_cci_large: Path) -> None:
    """Bug E3C: nvarchar_50 null row should be None, not '' (empty string)."""
    _assert_col(fixture_bak_tabletype_cci_large, "nvarchar_50", labels=["null"])


@pytest.mark.fixture
def test_e3c_nvarchar_null_returns_empty_string_not_none(
    fixture_bak_tabletype_cci_large: Path,
) -> None:
    """Regression (E3C): the null structural row decodes as None, not '' (empty string)."""
    col = _read_col(fixture_bak_tabletype_cci_large, "c_nvarchar_50")
    null_val = col.get("null")
    assert null_val is None, (
        f"Bug E3C regressed: c_nvarchar_50 null row decoded as {null_val!r} "
        "(expected None — compact RLE null flag was missed)"
    )


@pytest.mark.fixture
def test_e3c_nvarchar_non_null_rows_still_correct(
    fixture_bak_tabletype_cci_large: Path,
) -> None:
    """Bug E3C is null-specific: low/high nvarchar_50 rows decode correctly."""
    _assert_col(fixture_bak_tabletype_cci_large, "nvarchar_50", labels=["low", "high"])
