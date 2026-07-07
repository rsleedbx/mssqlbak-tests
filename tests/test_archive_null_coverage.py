"""Level-1 ARCHIVE columnstore null-encoding tests (Gap 5).

``archivenull_full.bak`` — 50,000-row CCI table with ``DATA_COMPRESSION =
COLUMNSTORE_ARCHIVE``.  CHAR(10) columns in ARCHIVE-compressed columnstore
row groups are stored with ``cmprlevel=4`` and ``enc_type=5`` (the multi-
sub-block string format).  mssqlbak currently returns 0 NULLs for enc_type=5
segments instead of the correct count.

Schema:
    dbo.archive_null
        id    INT       — 1–50,000
        code  CHAR(10)  — NULL every 500th row → 100 NULLs
        zip   CHAR(10)  — NULL every 1,000th row → 50 NULLs

These tests act as a regression gate:
* If they FAIL (0 NULLs returned) the enc_type=5 null-decoding bug is
  confirmed in this controlled fixture.
* Once Gap 5 is fixed, the tests should PASS, proving the fix is correct.

Fixture generation::

    python -m tools.fixture_run --fixture-dir <dir> archive-null
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(_store(path)).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# Expected null counts encoded in the fixture generation script.
_CODE_NULL_EVERY = 500
_ZIP_NULL_EVERY = 1_000
_TOTAL_ROWS = 50_000
_EXPECTED_CODE_NULLS = _TOTAL_ROWS // _CODE_NULL_EVERY   # 100
_EXPECTED_ZIP_NULLS = _TOTAL_ROWS // _ZIP_NULL_EVERY     # 50


# ---------------------------------------------------------------------------
# Structure / classify
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_archive_null_classify_supported(fixture_bak_archive_null: Path) -> None:
    """archive_null is a CCI table — classified as supported."""
    tables = _tables(fixture_bak_archive_null)
    result = classify_table(tables["archive_null"])
    assert result.supported, f"expected supported, got: {result.reason}"


@pytest.mark.fixture
def test_archive_null_row_count(fixture_bak_archive_null: Path) -> None:
    """archive_null contains exactly 50,000 rows."""
    rows = _rows(fixture_bak_archive_null, "archive_null")
    assert len(rows) == _TOTAL_ROWS, (
        f"expected {_TOTAL_ROWS:,} rows, got {len(rows):,}"
    )


# ---------------------------------------------------------------------------
# Null counts (Gap 5 core assertions)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_archive_null_code_null_count(fixture_bak_archive_null: Path) -> None:
    """code column: exactly 100 NULLs (every 500th row).

    Gap 5: if enc_type=5 null encoding is not decoded correctly mssqlbak
    returns 0 NULLs.  This test catches that regression.
    """
    rows = _rows(fixture_bak_archive_null, "archive_null")
    null_count = sum(1 for r in rows if r["code"] is None)
    assert null_count == _EXPECTED_CODE_NULLS, (
        f"code: expected {_EXPECTED_CODE_NULLS} NULLs, got {null_count} "
        "(Gap-5 bug: enc_type=5 null encoding not decoded)"
    )


@pytest.mark.fixture
def test_archive_null_zip_null_count(fixture_bak_archive_null: Path) -> None:
    """zip column: exactly 50 NULLs (every 1,000th row).

    Gap 5: same enc_type=5 null-decoding bug as for code.
    """
    rows = _rows(fixture_bak_archive_null, "archive_null")
    null_count = sum(1 for r in rows if r["zip"] is None)
    assert null_count == _EXPECTED_ZIP_NULLS, (
        f"zip: expected {_EXPECTED_ZIP_NULLS} NULLs, got {null_count} "
        "(Gap-5 bug: enc_type=5 null encoding not decoded)"
    )


@pytest.mark.fixture
def test_archive_null_code_null_positions(fixture_bak_archive_null: Path) -> None:
    """NULLs in code land on the correct row IDs (multiples of 500)."""
    rows = _rows(fixture_bak_archive_null, "archive_null")
    null_ids = {r["id"] for r in rows if r["code"] is None}
    expected_ids = {i * _CODE_NULL_EVERY for i in range(1, _EXPECTED_CODE_NULLS + 1)}
    assert null_ids == expected_ids, (
        f"null positions wrong: extra={null_ids - expected_ids}, "
        f"missing={expected_ids - null_ids}"
    )


# ---------------------------------------------------------------------------
# Non-null value spot-checks
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_archive_null_non_null_values(fixture_bak_archive_null: Path) -> None:
    """Non-null code and zip values decode correctly.

    SQL Server stores CAST(n AS CHAR(10)) which right-pads with spaces to 10
    characters.  After rstrip the value equals the integer string.
    """
    rows = _rows(fixture_bak_archive_null, "archive_null")
    by_id = {r["id"]: r for r in rows}
    for sample_id in (1, 100, 999, 1001, 49999):
        r = by_id[sample_id]
        assert r["code"] is not None, f"id={sample_id}: code unexpectedly NULL"
        assert r["code"].rstrip() == str(sample_id), (
            f"id={sample_id}: code {r['code']!r} != {str(sample_id)!r}"
        )
        assert r["zip"] is not None, f"id={sample_id}: zip unexpectedly NULL"
        assert r["zip"].rstrip() == str(sample_id), (
            f"id={sample_id}: zip {r['zip']!r} != {str(sample_id)!r}"
        )
