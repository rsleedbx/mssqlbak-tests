"""Record-layer coverage tests.

Exercises the record-type dispatch path (forwarded heap records, ghost records,
uniquifier columns) and sparse columns using the ``compressioncoverage_full``
fixture, which contains tables specifically built to materialise these on-disk
shapes:

* ``fwd_heap``        — two rows; row a=25 is grown by UPDATE past the page
                        boundary, leaving a forwarding stub and a forwarded
                        record elsewhere.
* ``ghost_heap``      — 500 rows inserted, 250 deleted; deleted slots remain as
                        ghost records until background cleanup, so the reader
                        must silently skip ghosts.
* ``uniquifier_none`` — 1 000 rows on a non-unique clustered index (low-cardinality
                        key ``code`` with only 50 distinct values), so SQL Server
                        appends a 4-byte uniquifier to duplicate keys.  Stored
                        without compression.
* ``uniquifier_row``  — same non-unique CI, stored with ROW compression.
* ``sparse_cols``     — four columns (id, a, b, c); a/b/c are SPARSE, so their
                        non-NULL values live in a trailing sparse vector rather
                        than the normal fixed/variable regions.
* ``cs_probe``        — ``id`` (int PK) + ``a`` (int SPARSE) + ``b`` (varchar
                        SPARSE) + ``cs`` (xml COLUMN_SET).  Verifies that the
                        column_set xml aggregate is synthesised from the decoded
                        sparse values.

Expected row counts come from ``tools/compressionmatrix.py`` construction
logic (ROW_COUNT=1000, ghost_heap inserts 500 then deletes even IDs → 250 live).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows


# ---------------------------------------------------------------------------
# Shared fixture load (cached once per session via the conftest fixture)
# ---------------------------------------------------------------------------

def _tables(path: Path) -> dict:
    store = PageStore.from_bak(path)
    return {t.name: t for t in recover_schema(store).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = PageStore.from_bak(path)
    schema = {t.name: t for t in recover_schema(store).tables}
    return list(read_table_rows(store, schema[table]))


# ---------------------------------------------------------------------------
# Forwarded heap records
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_fwd_heap_row_count(fixture_bak_datacompression: Path) -> None:
    """Forwarded records are emitted; the heap yields both rows."""
    rows = _rows(fixture_bak_datacompression, "fwd_heap")
    assert len(rows) == 2


@pytest.mark.fixture
def test_fwd_heap_row_values(fixture_bak_datacompression: Path) -> None:
    """Both rows decode correctly — the forwarded one (a=25, grown to 5000 B)
    and the ordinary one (a=28, 4000 B), regardless of which slot forwarded."""
    rows = _rows(fixture_bak_datacompression, "fwd_heap")
    by_a = {r["a"]: r for r in rows}
    assert set(by_a) == {25, 28}
    assert by_a[25]["b"] == "A" * 5000
    assert by_a[28]["b"] == "B" * 4000


@pytest.mark.fixture
def test_fwd_heap_classify_supported(fixture_bak_datacompression: Path) -> None:
    tables = _tables(fixture_bak_datacompression)
    assert classify_table(tables["fwd_heap"]).supported


# ---------------------------------------------------------------------------
# Ghost records
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_ghost_heap_row_count(fixture_bak_datacompression: Path) -> None:
    """Ghost (deleted) records are skipped; only the 250 surviving rows are
    returned.  The 250 deleted even-id rows must not appear."""
    rows = _rows(fixture_bak_datacompression, "ghost_heap")
    assert len(rows) == 250


@pytest.mark.fixture
def test_ghost_heap_only_odd_ids(fixture_bak_datacompression: Path) -> None:
    """All surviving rows have odd IDs — the even-id rows were deleted and
    left as ghosts."""
    rows = _rows(fixture_bak_datacompression, "ghost_heap")
    assert all(r["id"] % 2 == 1 for r in rows)


@pytest.mark.fixture
def test_ghost_heap_id_range(fixture_bak_datacompression: Path) -> None:
    """Surviving IDs span 1–499 (odd only), covering the full original range."""
    ids = {r["id"] for r in _rows(fixture_bak_datacompression, "ghost_heap")}
    assert min(ids) == 1
    assert max(ids) == 499
    assert 2 not in ids   # first deleted row absent
    assert 499 in ids     # last odd row present


# ---------------------------------------------------------------------------
# Uniquifier column (non-unique clustered index)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_uniquifier_none_row_count(fixture_bak_datacompression: Path) -> None:
    """All 200 rows survive on a non-unique clustered index (uncompressed)."""
    rows = _rows(fixture_bak_datacompression, "uniquifier_none")
    assert len(rows) == 200


@pytest.mark.fixture
def test_uniquifier_none_code_values(fixture_bak_datacompression: Path) -> None:
    """code = id % 50 for every row; 50 distinct code values, 4 rows each."""
    rows = _rows(fixture_bak_datacompression, "uniquifier_none")
    from collections import Counter
    code_counts = Counter(r["code"] for r in rows)
    assert set(code_counts) == set(range(50))
    assert all(v == 4 for v in code_counts.values())


@pytest.mark.fixture
def test_uniquifier_row_row_count(fixture_bak_datacompression: Path) -> None:
    """ROW-compressed non-unique CI: all 200 rows survive."""
    rows = _rows(fixture_bak_datacompression, "uniquifier_row")
    assert len(rows) == 200


@pytest.mark.fixture
def test_uniquifier_row_matches_none(fixture_bak_datacompression: Path) -> None:
    """ROW-compressed and uncompressed non-unique CIs hold identical data."""
    store = PageStore.from_bak(fixture_bak_datacompression)
    tables = {t.name: t for t in recover_schema(store).tables}
    none_rows = {r["id"]: r for r in read_table_rows(store, tables["uniquifier_none"])}
    row_rows  = {r["id"]: r for r in read_table_rows(store, tables["uniquifier_row"])}
    assert none_rows == row_rows


# ---------------------------------------------------------------------------
# Sparse columns
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_cols_classify_supported(fixture_bak_datacompression: Path) -> None:
    """Sparse tables are classified as supported now that the sparse vector
    decode is implemented.

    The classifier detects SPARSE columns via syscolpars.status bit 24
    (0x01000000) and the row reader correctly parses the trailing sparse vector
    for non-NULL values while returning None for absent (NULL) sparse columns.
    """
    tables = _tables(fixture_bak_datacompression)
    sup = classify_table(tables["sparse_cols"])
    assert sup.supported


@pytest.mark.fixture
def test_sparse_cols_is_sparse_flag(fixture_bak_datacompression: Path) -> None:
    """All three SPARSE columns carry ``is_sparse=True``; the non-sparse ``id``
    column carries ``is_sparse=False``."""
    tables = _tables(fixture_bak_datacompression)
    cols = {c.name: c for c in tables["sparse_cols"].columns}
    assert not cols["id"].is_sparse
    assert cols["a"].is_sparse
    assert cols["b"].is_sparse
    assert cols["c"].is_sparse


@pytest.mark.fixture
def test_sparse_cols_non_null_values_readable(fixture_bak_datacompression: Path) -> None:
    """Sparse vector decode: non-NULL values are correctly returned.

    Every 10th row has non-NULL sparse values: a=id (int), b='sparse{id}'
    (varchar), c=id.xxxx (decimal).  Rows not divisible by 10 have all sparse
    columns NULL.  Total: 200 rows, 20 non-null, 180 all-null.
    """
    rows = _rows(fixture_bak_datacompression, "sparse_cols")
    assert len(rows) == 200
    non_null = [r for r in rows if r.get("a") is not None]
    assert len(non_null) == 20, f"expected 20 rows with non-NULL a, got {len(non_null)}"
    null_rows = [r for r in rows if r.get("a") is None]
    assert len(null_rows) == 180
    for r in non_null:
        assert r["a"] == r["id"], f"id={r['id']}: a={r['a']}"
        assert r["b"] == f"sparse{r['id']}", f"id={r['id']}: b={r['b']!r}"


# ---------------------------------------------------------------------------
# COLUMN_SET xml aggregate
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_cs_probe_schema(fixture_bak_datacompression: Path) -> None:
    """cs_probe schema: a/b are sparse, cs is the column_set xml aggregate.

    The column_set column has no physical storage slot; it appears in the
    schema output with ``is_column_set=True`` (syscolpars.status bit 25 =
    0x02000000) and ``is_sparse=False``.
    """
    tables = _tables(fixture_bak_datacompression)
    assert "cs_probe" in tables, "cs_probe table not found in fixture"
    cols = {c.name: c for c in tables["cs_probe"].columns}
    assert not cols["id"].is_sparse
    assert not cols["id"].is_column_set
    assert cols["a"].is_sparse
    assert not cols["a"].is_column_set
    assert cols["b"].is_sparse
    assert not cols["b"].is_column_set
    assert cols["cs"].is_column_set
    assert not cols["cs"].is_sparse


@pytest.mark.fixture
def test_cs_probe_column_set_synthesis(fixture_bak_datacompression: Path) -> None:
    """Column_set xml is synthesised correctly from sparse-vector values.

    Expected data (inserted by compressionmatrix.py or setup script)::

        id=1: a=42, b='hello'  → cs='<a>42</a><b>hello</b>'
        id=2: a=99, b=NULL     → cs='<a>99</a>'
        id=3: a=NULL, b='world'→ cs='<b>world</b>'
        id=4: a=NULL, b=NULL   → cs=NULL
    """
    rows = {r["id"]: r for r in _rows(fixture_bak_datacompression, "cs_probe")}
    assert set(rows) == {1, 2, 3, 4}
    assert rows[1]["cs"] == "<a>42</a><b>hello</b>"
    assert rows[2]["cs"] == "<a>99</a>"
    assert rows[3]["cs"] == "<b>world</b>"
    assert rows[4]["cs"] is None
