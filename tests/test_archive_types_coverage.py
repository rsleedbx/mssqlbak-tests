"""ARCHIVE columnstore enc=5 type coverage tests (TODO-T1).

``archive_columnstore_types_full.bak`` — 35,000-row CCI tables (ARCHIVE compressed),
one table per SQL type, with exactly **70 NULLs** per ``val`` column (every 500th row).

Tables and their encoding types:
    archive_char10      — CHAR(10)           enc=5  col_width=10   FIXED ✓
    archive_binary10    — BINARY(10)         enc=5  col_width=10   FIXED ✓
    archive_nchar10     — NCHAR(10)          enc=5  col_width=20   FIXED ✓
    archive_nvarchar20  — NVARCHAR(20)       enc=3  variable        FIXED ✓
    archive_uuid        — UNIQUEIDENTIFIER   enc=5  col_width=16   FIXED ✓
    archive_varbinary20 — VARBINARY(20)      enc=5  variable        FIXED ✓
    archive_varchar20   — VARCHAR(20)        enc=5  variable        FIXED ✓

Bugs A+B (2026-06-16): fixed enc=5 off-by-one for CHAR/BINARY/NCHAR.
Bugs C/D/E/F (2026-06-16): fixed by correcting LOB fragment assembly in
_read_large_root_data (bsz capping).
Bugs G/H (2026-06-16): fixed by replacing fixed-stride pool decoder with a
byte-offset pool map that handles variable-length pool entries.

Fixture generation::

    python -m tools.fixture_run --fixture-dir <dir> archive-columnstore-types
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows

_EXPECTED_NULLS = 70
_EXPECTED_ROWS = 35_000


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _null_count(path: Path, table: str) -> tuple[int, int]:
    """Return ``(row_count, null_count)`` for the ``val`` column of *table*."""
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    rows = list(read_table_rows(store, tbl, schema.obj_to_name))
    return len(rows), sum(1 for r in rows if r["val"] is None)


# ---------------------------------------------------------------------------
# Fixed-width ASCII/binary/Unicode types — FIXED by Bug A+B (2026-06-16)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_archive_char10_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """CHAR(10) ARCHIVE enc=5: exactly 70 NULLs across all SS versions."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_char10")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


@pytest.mark.fixture
def test_archive_binary10_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """BINARY(10) ARCHIVE enc=5: exactly 70 NULLs across all SS versions."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_binary10")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


@pytest.mark.fixture
def test_archive_nchar10_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """NCHAR(10) ARCHIVE enc=5: exactly 70 NULLs (col_width=20, UTF-16LE)."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_nchar10")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


# ---------------------------------------------------------------------------
# Broken types — known bugs documented here; remove xfail when each is fixed
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_archive_nvarchar20_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """NVARCHAR(20) ARCHIVE enc=3: exactly 70 NULLs (xfail — Bug E)."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_nvarchar20")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


@pytest.mark.fixture
def test_archive_uuid_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """UNIQUEIDENTIFIER ARCHIVE enc=5: exactly 70 NULLs (xfail — Bug F)."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_uuid")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


@pytest.mark.fixture
def test_archive_varbinary20_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """VARBINARY(20) ARCHIVE enc=5: exactly 70 NULLs (xfail — Bug G)."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_varbinary20")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS


@pytest.mark.fixture
def test_archive_varchar20_null_count(
    fixture_bak_archive_columnstore_types: Path,
) -> None:
    """VARCHAR(20) ARCHIVE enc=5: exactly 70 NULLs (xfail — Bug H)."""
    n, nulls = _null_count(fixture_bak_archive_columnstore_types, "archive_varchar20")
    assert n == _EXPECTED_ROWS
    assert nulls == _EXPECTED_NULLS
