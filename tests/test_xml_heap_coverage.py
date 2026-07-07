"""Level-1 xml-heap LOB regression-guard tests (Gap 10).

``xmlheap_full.bak`` — a heap table (no clustered index) with four LOB
columns: large ``xml NOT NULL``, small ``xml NOT NULL``, ``varchar(MAX)``, and
``varbinary(MAX)``.

Gap 10 context: SQL Server 2008R2–2014 used a different byte layout for LOB
pointers stored in heap data pages when the column type is ``xml``.  SQL
Server 2016+ changed this layout; mssqlbak correctly reads the modern format.
This fixture documents the expected behaviour for SS2016+ so any future fix
for the pre-2016 LOB pointer format can be verified not to break the modern
path.

Schema: dbo.xml_heap (heap; no clustered index)
    id             INT IDENTITY
    event_time     DATETIME2(3)
    event_type     NVARCHAR(100)
    xml_event      XML NOT NULL    — large (~9 KB) → LOB pages
    xml_small      XML NOT NULL    — small (~200 B) → typically inline
    text_payload   VARCHAR(MAX)    — ~500 bytes, NULL on even IDs
    bin_payload    VARBINARY(MAX)  — ~200 bytes, NULL on even IDs

Fixture generation::

    python -m tools.fixture_run --fixture-dir <dir> xml-heap
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows

_ROW_COUNT = 200


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(_store(path)).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_xml_heap_is_heap(fixture_bak_xml_heap: Path) -> None:
    """xml_heap has no clustered index — verify classify_table sees it as a heap.

    Heaps are walked via the IAM chain; the result must be 'supported' with
    alloc_units that have no root_page (B-tree root is 0:0 for heaps).
    """
    tables = _tables(fixture_bak_xml_heap)
    result = classify_table(tables["xml_heap"])
    assert result.supported, f"expected supported heap, got: {result.reason}"


@pytest.mark.fixture
def test_xml_heap_row_count(fixture_bak_xml_heap: Path) -> None:
    """xml_heap contains exactly 200 rows."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    assert len(rows) == _ROW_COUNT, (
        f"expected {_ROW_COUNT} rows, got {len(rows)}"
    )


# ---------------------------------------------------------------------------
# xml columns (Gap 10 core: LOB pointer in heap page must be followed)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_xml_heap_large_xml_non_null(fixture_bak_xml_heap: Path) -> None:
    """xml_event is non-NULL for all 200 rows.

    A large XML value (~9 KB) forces LOB page allocation even on a heap.
    If the heap LOB pointer format is misread mssqlbak raises an exception or
    returns None/empty bytes — either will fail here.
    """
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    nulls = [r["id"] for r in rows if r.get("xml_event") is None]
    assert not nulls, f"xml_event NULL for {len(nulls)} rows: first ids={nulls[:5]}"


@pytest.mark.fixture
def test_xml_heap_large_xml_contains_tag(fixture_bak_xml_heap: Path) -> None:
    """xml_event decodes to a string containing the expected root element tag."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    bad = []
    for r in rows:
        val = r.get("xml_event")
        if not isinstance(val, str) or "<event " not in val:
            bad.append(r["id"])
    assert not bad, (
        f"xml_event missing '<event ' tag for {len(bad)} rows: first ids={bad[:5]}"
    )


@pytest.mark.fixture
def test_xml_heap_small_xml_non_null(fixture_bak_xml_heap: Path) -> None:
    """xml_small is non-NULL for all 200 rows (inline-stored XML on heap)."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    nulls = [r["id"] for r in rows if r.get("xml_small") is None]
    assert not nulls, f"xml_small NULL for {len(nulls)} rows"


# ---------------------------------------------------------------------------
# varchar(MAX) / varbinary(MAX) columns
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_xml_heap_text_payload_nulls(fixture_bak_xml_heap: Path) -> None:
    """text_payload is NULL for even IDs and non-NULL for odd IDs."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    by_id = {r["id"]: r for r in rows}
    for rid, r in by_id.items():
        expected_null = rid % 2 == 0
        is_null = r["text_payload"] is None
        assert is_null == expected_null, (
            f"id={rid}: text_payload {'should' if expected_null else 'should not'} be NULL"
        )


@pytest.mark.fixture
def test_xml_heap_bin_payload_nulls(fixture_bak_xml_heap: Path) -> None:
    """bin_payload is NULL for even IDs and non-NULL for odd IDs."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    by_id = {r["id"]: r for r in rows}
    for rid, r in by_id.items():
        expected_null = rid % 2 == 0
        is_null = r["bin_payload"] is None
        assert is_null == expected_null, (
            f"id={rid}: bin_payload {'should' if expected_null else 'should not'} be NULL"
        )


@pytest.mark.fixture
def test_xml_heap_text_payload_length(fixture_bak_xml_heap: Path) -> None:
    """Non-NULL text_payload values are exactly 500 bytes."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    bad = [
        r["id"] for r in rows
        if r["text_payload"] is not None and len(r["text_payload"]) != 500
    ]
    assert not bad, (
        f"text_payload wrong length for ids={bad[:5]}"
    )


@pytest.mark.fixture
def test_xml_heap_bin_payload_length(fixture_bak_xml_heap: Path) -> None:
    """Non-NULL bin_payload values are exactly 200 bytes."""
    rows = _rows(fixture_bak_xml_heap, "xml_heap")
    bad = [
        r["id"] for r in rows
        if r["bin_payload"] is not None and len(r["bin_payload"]) != 200
    ]
    assert not bad, (
        f"bin_payload wrong length for ids={bad[:5]}"
    )
