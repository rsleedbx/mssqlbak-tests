"""Single-chunk enc=5 ARCHIVE coverage (TODO-F1 — FIXED 2026-06-17).

``archive_single_chunk_full.bak`` — one small ARCHIVE ``CHAR(10)`` table
(``TOTAL_ROWS`` ~ 5000) whose compressed column blob fits in a single
chunk (no XPRESS wrapper: cmp_sz=0).  Every other enc=5 fixture uses
≥ 35,000-row tables whose blobs span multiple chunks, so this path was
previously not reachable.

The fix in ``mssqlbak/columnstore.py``: ARCHIVE type-2 detection scans the
raw blob for the ``0xFFFF`` chunk delimiter at a u16-aligned offset past the
96-byte enc=5 header, followed by ``n_block == n_rows``.  When found, the
blob is routed to ``_decode_enc5_archive`` instead of falling through to the
Format C compressed path.

The CHAR(10) ``code`` column is NULL every ``CODE_NULL_EVERY``-th row.
Each test is parametrized over ``sequential`` and ``random`` (INSERT ORDER BY
NEWID()).

Fixture generation::

    python -m tools.fixture_run all-versions --suite archive-single-chunk
    python -m tools.fixture_run all-versions --suite archive-single-chunk-random
"""
from __future__ import annotations

import functools
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_archive_single_chunk_fixture import (
    CODE_NULL_COUNT,
    CODE_NULL_EVERY,
    TOTAL_ROWS,
)

_TABLE = "archive_single_chunk"


# ---------------------------------------------------------------------------
# Combined sequential + random fixture (Part II)
# ---------------------------------------------------------------------------

@pytest.fixture(
    params=["sequential", "random"],
    ids=["sequential", "random"],
)
def fixture_bak_single_chunk(
    request: pytest.FixtureRequest,
    fixture_bak_archive_single_chunk: Path,
    fixture_bak_archive_single_chunk_random: Path,
) -> Path:
    """Parametrized over sequential and random-order variants.

    A test that passes [sequential] but fails [random] pinpoints a
    non-sequential segment decode bug in the single-chunk enc=5 path.
    """
    if request.param == "random":
        return fixture_bak_archive_single_chunk_random
    return fixture_bak_archive_single_chunk


@functools.lru_cache(maxsize=None)
def _rows_by_id(path: Path) -> dict[int, dict]:
    store: AnyPageStore = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == _TABLE)
    return {r["id"]: r for r in read_table_rows(store, tbl, schema.obj_to_name)}


def _table(path: Path):
    return next(t for t in recover_schema(PageStore.from_bak(path)).tables if t.name == _TABLE)


# ---------------------------------------------------------------------------
# Classify + row count
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_single_chunk_classify_supported(
    fixture_bak_single_chunk: Path,
) -> None:
    """The small ARCHIVE CCI table classifies as supported."""
    result = classify_table(_table(fixture_bak_single_chunk))
    assert result.supported, f"expected supported, got: {result.reason}"


@pytest.mark.fixture
def test_single_chunk_row_count(fixture_bak_single_chunk: Path) -> None:
    """Table contains exactly TOTAL_ROWS rows with ids 1..N."""
    by_id = _rows_by_id(fixture_bak_single_chunk)
    assert len(by_id) == TOTAL_ROWS, f"expected {TOTAL_ROWS:,} rows, got {len(by_id):,}"
    assert min(by_id) == 1 and max(by_id) == TOTAL_ROWS


# ---------------------------------------------------------------------------
# enc=5 null decoding on the single-chunk path
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_single_chunk_code_null_count(
    fixture_bak_single_chunk: Path,
) -> None:
    """code has exactly CODE_NULL_COUNT NULLs (every CODE_NULL_EVERY-th row).

    This is the single-chunk enc=5 null-decode check — the path no ≥35,000-row
    fixture reaches.
    """
    by_id = _rows_by_id(fixture_bak_single_chunk)
    n = sum(1 for r in by_id.values() if r["code"] is None)
    assert n == CODE_NULL_COUNT, (
        f"code: expected {CODE_NULL_COUNT} NULLs, got {n} (single-chunk enc=5)"
    )


@pytest.mark.fixture
def test_single_chunk_null_positions(
    fixture_bak_single_chunk: Path,
) -> None:
    """NULLs land exactly on the multiples of CODE_NULL_EVERY."""
    by_id = _rows_by_id(fixture_bak_single_chunk)
    for n in range(1, TOTAL_ROWS + 1):
        is_null = by_id[n]["code"] is None
        should_be_null = n % CODE_NULL_EVERY == 0
        assert is_null == should_be_null, (
            f"id={n}: code is_null={is_null}, expected {should_be_null}"
        )


@pytest.mark.fixture
def test_single_chunk_non_null_values(
    fixture_bak_single_chunk: Path,
) -> None:
    """Non-null code values round-trip: CAST(n AS CHAR(10)) rstrips to str(id)."""
    by_id = _rows_by_id(fixture_bak_single_chunk)
    for sample_id in (1, 2, 51, 4999, TOTAL_ROWS - 1):
        if sample_id % CODE_NULL_EVERY == 0:
            continue
        r = by_id[sample_id]
        assert r["code"] is not None, f"id={sample_id}: code unexpectedly NULL"
        assert r["code"].rstrip() == str(sample_id), (
            f"id={sample_id}: code {r['code']!r} != {str(sample_id)!r}"
        )
