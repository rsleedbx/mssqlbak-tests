"""PFOR exception-path coverage for columnstore INT segments.

``pfor_columnstore_full.bak`` — two identical-data tables on a single row group:

  pfor_plain     DATA_COMPRESSION = COLUMNSTORE
  pfor_archive   DATA_COMPRESSION = COLUMNSTORE_ARCHIVE

Each has a monotonic ``id`` join key plus five engineered INT columns, every one a
different Patched-Frame-Of-Reference (PFOR) scenario.  Monotonic columns (as used
by every other fixture) value-encode to an exception-free frame and never exercise
the bit-pack exception walk; these columns deliberately inject large outliers so
that — if SQL Server uses PFOR — the encoder must store exceptions.

  Column         Majority                Outlier injection                  Knob
  -------------- ----------------------- ---------------------------------- -----------------------
  v_none         n % 1000                none                               CONTROL (must stay clean)
  v_sparse       n % 65536               every SPARSE_EVERY-th row = 2e9    sparse exception list
  v_deep         n % 1024                single row (n = DEEP_ROW) = 2e9    first-exception boundary
  v_compulsory   n % 8                   every COMPULSORY_EVERY-th = 1e9    compulsory exceptions
  v_dense        n % 32                  every DENSE_EVERY-th = 1e9+(n%7)   dense (~9%) list / NewPFD

The decode order within a row group is not guaranteed, so every check joins
decoded rows back to expected values on ``id`` (which is monotonic and
exception-free, hence a reliable key).

Each test is parametrized over ``sequential`` and ``random`` (INSERT ORDER BY
NEWID()).  A test that passes [sequential] but fails [random] pinpoints a
non-sequential segment decode bug.

Honesty caveat: SQL Server may dictionary-encode (enc_type=2) the low-cardinality
columns instead of bit-packing them, in which case those columns never produce a
PFOR exception.  The value assertions still hold either way — they verify the
decoder reproduces the inserted values regardless of which encoding the engine
chose.  Inspect ``encoding_type`` via ``tools/capture_verifier_sidecar.py`` to see
which columns actually took the bit-pack path.

Fixture generation::

    python -m tools.fixture_run --fixture-dir <dir> pfor-columnstore
    python -m tools.fixture_run --fixture-dir <dir> pfor-columnstore-random
    python -m tools.fixture_run all-versions --suite pfor-columnstore
    python -m tools.fixture_run all-versions --suite pfor-columnstore-random
"""
from __future__ import annotations

import functools
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_pfor_columnstore_fixture import (
    COMPULSORY_EVERY,
    COMPULSORY_OUTLIER,
    DEFAULT_ROWS,
    DENSE_EVERY,
    DENSE_OUTLIER_BASE,
    SPARSE_EVERY,
    SPARSE_OUTLIER,
)

_ROWS = DEFAULT_ROWS
_DEEP_ROW = _ROWS // 2 + 1  # matches _insert_block(): rows // 2 + 1

_TABLES = ("pfor_plain", "pfor_archive")


# ---------------------------------------------------------------------------
# Combined sequential + random fixture (Part II)
# ---------------------------------------------------------------------------

@pytest.fixture(
    params=["sequential", "random"],
    ids=["sequential", "random"],
)
def fixture_bak_pfor(
    request: pytest.FixtureRequest,
    fixture_bak_pfor_columnstore: Path,
    fixture_bak_pfor_columnstore_random: Path,
) -> Path:
    """Parametrized over sequential and random-order variants.

    A test that passes [sequential] but fails [random] pinpoints a
    non-sequential segment decode bug in the PFOR bit-pack decoder.
    """
    if request.param == "random":
        return fixture_bak_pfor_columnstore_random
    return fixture_bak_pfor_columnstore


# ---------------------------------------------------------------------------
# Expected value formulas — must mirror make_pfor_columnstore_fixture._insert_block
# ---------------------------------------------------------------------------

def _expected_none(n: int) -> int:
    return n % 1000


def _expected_sparse(n: int) -> int:
    return SPARSE_OUTLIER if n % SPARSE_EVERY == 0 else n % 65536


def _expected_deep(n: int) -> int:
    return SPARSE_OUTLIER if n == _DEEP_ROW else n % 1024


def _expected_compulsory(n: int) -> int:
    return COMPULSORY_OUTLIER if n % COMPULSORY_EVERY == 0 else n % 8


def _expected_dense(n: int) -> int:
    return DENSE_OUTLIER_BASE + (n % 7) if n % DENSE_EVERY == 0 else n % 32


_EXPECTED = {
    "v_none": _expected_none,
    "v_sparse": _expected_sparse,
    "v_deep": _expected_deep,
    "v_compulsory": _expected_compulsory,
    "v_dense": _expected_dense,
}


# ---------------------------------------------------------------------------
# Helpers (cached: decoding 200k rows per call is the expensive part)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _rows_by_id(path: Path, table: str) -> dict[int, dict]:
    store: AnyPageStore = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return {r["id"]: r for r in read_table_rows(store, tbl, schema.obj_to_name)}


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(PageStore.from_bak(path)).tables}


def _column_mismatches(
    by_id: dict[int, dict], col: str, fn
) -> list[tuple[int, object, int]]:
    """Return up to 10 (id, got, expected) tuples where decoded != expected."""
    out: list[tuple[int, object, int]] = []
    for n in range(1, _ROWS + 1):
        exp = fn(n)
        got = by_id[n][col]
        if got != exp:
            out.append((n, got, exp))
            if len(out) >= 10:
                break
    return out


# ---------------------------------------------------------------------------
# Classify + row count
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("table", _TABLES)
def test_pfor_classify_supported(
    fixture_bak_pfor: Path, table: str
) -> None:
    """Both CCI tables classify as supported."""
    result = classify_table(_tables(fixture_bak_pfor)[table])
    assert result.supported, f"{table}: expected supported, got: {result.reason}"


@pytest.mark.fixture
@pytest.mark.parametrize("table", _TABLES)
def test_pfor_row_count(fixture_bak_pfor: Path, table: str) -> None:
    """Each table contains exactly DEFAULT_ROWS rows with unique ids 1..N."""
    by_id = _rows_by_id(fixture_bak_pfor, table)
    assert len(by_id) == _ROWS, f"{table}: expected {_ROWS:,} rows, got {len(by_id):,}"
    assert min(by_id) == 1 and max(by_id) == _ROWS, (
        f"{table}: id range {min(by_id)}..{max(by_id)}, expected 1..{_ROWS}"
    )


# ---------------------------------------------------------------------------
# Per-column value correctness — the actual PFOR exercise
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("table", _TABLES)
@pytest.mark.parametrize("col", list(_EXPECTED))
def test_pfor_column_values(
    fixture_bak_pfor: Path, table: str, col: str
) -> None:
    """Every decoded value matches the inserted value.

    For the outlier columns this fails iff the decoder mishandles PFOR
    exceptions (e.g. reads the b-bit placeholder/offset literally instead of
    following the patch).  ``v_none`` is the control: if it fails too, the bug
    is not exception-specific.
    """
    by_id = _rows_by_id(fixture_bak_pfor, table)
    mismatches = _column_mismatches(by_id, col, _EXPECTED[col])
    assert not mismatches, (
        f"{table}.{col}: {len(mismatches)}+ mismatches "
        f"(first: id/got/expected = {mismatches})"
    )


# ---------------------------------------------------------------------------
# Targeted boundary + sanity checks
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("table", _TABLES)
def test_pfor_deep_single_outlier(
    fixture_bak_pfor: Path, table: str
) -> None:
    """The lone deep outlier (id = DEEP_ROW) decodes to the large value, and its
    immediate neighbours stay in the small majority range.

    This pins the 'correct until the first exception, then diverges' symptom: if
    the exception walk is broken, the deep row and/or everything after it is wrong.
    """
    by_id = _rows_by_id(fixture_bak_pfor, table)
    assert by_id[_DEEP_ROW]["v_deep"] == SPARSE_OUTLIER, (
        f"{table}: deep outlier at id={_DEEP_ROW} decoded "
        f"{by_id[_DEEP_ROW]['v_deep']}, expected {SPARSE_OUTLIER}"
    )
    for neighbour in (_DEEP_ROW - 1, _DEEP_ROW + 1):
        assert by_id[neighbour]["v_deep"] == neighbour % 1024, (
            f"{table}: neighbour id={neighbour} v_deep="
            f"{by_id[neighbour]['v_deep']}, expected {neighbour % 1024}"
        )


@pytest.mark.fixture
@pytest.mark.parametrize("table", _TABLES)
def test_pfor_fixture_actually_contains_outliers(
    fixture_bak_pfor: Path, table: str
) -> None:
    """Guard against a silently exception-free fixture.

    If the generator regressed and produced no outliers, the value tests above
    would pass vacuously while exercising nothing.  Assert the outliers exist.
    """
    by_id = _rows_by_id(fixture_bak_pfor, table)
    assert any(by_id[n]["v_sparse"] == SPARSE_OUTLIER for n in range(1, _ROWS + 1)), (
        f"{table}: no v_sparse outliers present — fixture is exception-free"
    )
    assert by_id[_DEEP_ROW]["v_deep"] == SPARSE_OUTLIER
    assert any(
        by_id[n]["v_compulsory"] == COMPULSORY_OUTLIER for n in range(1, _ROWS + 1)
    ), f"{table}: no v_compulsory outliers present"
