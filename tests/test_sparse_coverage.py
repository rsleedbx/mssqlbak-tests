"""Level-1 sparse columns + column set coverage tests (Gap D-1).

``sparse_full.bak`` — a heap/clustered table with 4 SPARSE columns and one
XML COLUMN_SET column across 10,000 rows with varying sparsity patterns.

Gap D-1 context: sparse columns replace the standard per-column layout with a
**sparse vector** record appended to the row.  A parser that walks only the
fixed-length block + variable-length block + NULL bitmap will misread every
column after the first sparse one, producing silently wrong values.

Schema: dbo.sparse_wide
    id  INT PRIMARY KEY CLUSTERED
    a   INT           SPARSE NULL  — non-NULL when id % 2 = 0; a = id * 7
    b   VARCHAR(20)   SPARSE NULL  — non-NULL when id % 3 = 0; b = 'str_<id>'
    c   DATETIME2(3)  SPARSE NULL  — non-NULL when id % 4 = 0
    d   DECIMAL(10,2) SPARSE NULL  — always NULL
    cs  XML COLUMN_SET FOR ALL_SPARSE_COLUMNS

Fixture generation::

    python -m tools.fixture_run all-versions --suite sparse
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_sparse_fixture import (
    A_NON_NULL,
    A_VALUE_FN,
    B_NON_NULL,
    B_VALUE_FN,
    C_NON_NULL,
    C_VALUE_FN,
    ROW_COUNT,
)


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _schema(path: Path):
    return recover_schema(_store(path))


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_table_supported(fixture_bak_sparse: Path) -> None:
    """sparse_wide should be classified as supported (clustered index)."""
    schema = _schema(fixture_bak_sparse)
    tables = {t.name: t for t in schema.tables}
    result = classify_table(tables["sparse_wide"])
    assert result.supported, f"expected supported, got: {result.reason}"


# ---------------------------------------------------------------------------
# Row count
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_row_count(fixture_bak_sparse: Path) -> None:
    """sparse_wide must return exactly ROW_COUNT rows.

    A parser that double-counts the sparse vector or misreads the slot array
    will produce a wrong count.
    """
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT:,} rows, got {len(rows):,}"
    )


# ---------------------------------------------------------------------------
# Column a — INT SPARSE, non-NULL when id % 2 = 0
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_a_null_pattern(fixture_bak_sparse: Path) -> None:
    """Column a is NULL exactly when id % 2 != 0."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        r["id"]
        for r in rows
        if (r.get("a") is None) != (not A_NON_NULL(r["id"]))
    ]
    assert not wrong, (
        f"column a null-pattern wrong for {len(wrong)} ids: first={wrong[:5]}"
    )


@pytest.mark.fixture
def test_sparse_a_values(fixture_bak_sparse: Path) -> None:
    """Non-NULL values of column a equal id * 7."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        (r["id"], r["a"])
        for r in rows
        if A_NON_NULL(r["id"]) and r.get("a") != A_VALUE_FN(r["id"])
    ]
    assert not wrong, (
        f"column a wrong value for {len(wrong)} rows: first={wrong[:3]}"
    )


# ---------------------------------------------------------------------------
# Column b — VARCHAR(20) SPARSE, non-NULL when id % 3 = 0
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_b_null_pattern(fixture_bak_sparse: Path) -> None:
    """Column b is NULL exactly when id % 3 != 0."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        r["id"]
        for r in rows
        if (r.get("b") is None) != (not B_NON_NULL(r["id"]))
    ]
    assert not wrong, (
        f"column b null-pattern wrong for {len(wrong)} ids: first={wrong[:5]}"
    )


@pytest.mark.fixture
def test_sparse_b_values(fixture_bak_sparse: Path) -> None:
    """Non-NULL values of column b equal 'str_<id>'."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        (r["id"], repr(r.get("b")))
        for r in rows
        if B_NON_NULL(r["id"]) and r.get("b") != B_VALUE_FN(r["id"])
    ]
    assert not wrong, (
        f"column b wrong value for {len(wrong)} rows: first={wrong[:3]}"
    )


# ---------------------------------------------------------------------------
# Column c — DATETIME2(3) SPARSE, non-NULL when id % 4 = 0
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_c_null_pattern(fixture_bak_sparse: Path) -> None:
    """Column c is NULL exactly when id % 4 != 0."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        r["id"]
        for r in rows
        if (r.get("c") is None) != (not C_NON_NULL(r["id"]))
    ]
    assert not wrong, (
        f"column c null-pattern wrong for {len(wrong)} ids: first={wrong[:5]}"
    )


@pytest.mark.fixture
def test_sparse_c_non_null_is_datetime(fixture_bak_sparse: Path) -> None:
    """Non-NULL values of column c decode to a non-None datetime-like value."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    wrong = [
        r["id"]
        for r in rows
        if C_NON_NULL(r["id"]) and r.get("c") is None
    ]
    assert not wrong, (
        f"column c unexpectedly NULL for {len(wrong)} ids: first={wrong[:5]}"
    )


# ---------------------------------------------------------------------------
# Column d — DECIMAL(10,2) SPARSE, always NULL
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_d_always_null(fixture_bak_sparse: Path) -> None:
    """Column d is NULL for every row (no sparse bytes written at all)."""
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    non_null = [r["id"] for r in rows if r.get("d") is not None]
    assert not non_null, (
        f"column d expected always NULL, got non-NULL for {len(non_null)} ids: "
        f"first={non_null[:5]}"
    )


# ---------------------------------------------------------------------------
# Column cs — XML COLUMN_SET (ISO 8601 datetime format regression)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_sparse_cs_datetime_iso8601(fixture_bak_sparse: Path) -> None:
    """The cs COLUMN_SET XML must render DATETIME2 values with an ISO 8601 T separator.

    Regression for the rows.py column_set fix (commit 57e9219): datetime/date/time
    values inside column_set XML were previously serialized with a space separator
    ('2020-01-05 00:00:00') instead of the SQL Server standard ISO 8601 form
    ('2020-01-05T00:00:00').  A regression would make every datetime-containing
    column_set value fail to match SQL Server's own XML output.
    """
    rows = _rows(fixture_bak_sparse, "sparse_wide")
    by_id = {r["id"]: r for r in rows}

    # id=4 has both a and c non-NULL; id=8 has both a and c non-NULL.
    # Pick a small set of ids where C_NON_NULL is True to verify the format.
    probe_ids = [id_ for id_ in range(1, min(40, ROW_COUNT) + 1) if C_NON_NULL(id_)][:5]

    bad: list[tuple[int, str]] = []
    for id_ in probe_ids:
        row = by_id.get(id_)
        if row is None:
            continue
        cs = row.get("cs")
        if cs is None:
            bad.append((id_, "cs is None (expected XML string)"))
            continue
        expected_dt = C_VALUE_FN(id_).isoformat()   # e.g. '2020-01-05T00:00:00'
        expected_fragment = f"<c>{expected_dt}</c>"
        if expected_fragment not in cs:
            bad.append((id_, f"expected {expected_fragment!r} in cs={cs!r}"))

    assert not bad, (
        f"column cs datetime ISO 8601 format wrong for {len(bad)} rows "
        f"(T-separator regression):\n" + "\n".join(f"  id={i}: {msg}" for i, msg in bad)
    )
