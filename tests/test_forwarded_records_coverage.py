"""Level-1 forwarded records coverage tests (Gap H-1).

``forwarded_records_full.bak`` — a heap table whose rows were widened by UPDATE,
causing SQL Server to forward them to new page locations while leaving forwarding
stubs (record type ``0x04``) in the original slots.

Gap H-1 context: forwarding stubs on heap pages are the most likely cause of
the silent row-count errors observed on real-world heaps in the corpus.  A
heap scanner that counts stubs **and** real rows double-counts; one that reads
stub bytes as row data produces garbage values; one that skips forwarded targets
under-counts.

Schema:
    dbo.fwd_heap    — heap (no clustered index); forwarding stubs on odd IDs
    dbo.fwd_control — identical rows but clustered; always extracts correctly

Data pattern (id range 1 .. ROW_COUNT):
    Even IDs  → val = REPLICATE('x', SHORT_VAL_LEN)  — stay in original slot
    Odd IDs   → val = REPLICATE('y', LONG_VAL_LEN)   — forwarded to new page

Fixture generation::

    python -m tools.fixture_run all-versions --suite forwarded-records
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_forwarded_records_fixture import (
    LONG_VAL_LEN,
    ROW_COUNT,
    SHORT_VAL_LEN,
)


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_fwd_heap_is_heap(fixture_bak_forwarded_records: Path) -> None:
    """fwd_heap has no clustered index — classify_table must see it as a heap."""
    store = _store(fixture_bak_forwarded_records)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    result = classify_table(tables["fwd_heap"])
    assert result.supported, f"expected supported heap, got: {result.reason}"


@pytest.mark.fixture
def test_fwd_control_is_clustered(fixture_bak_forwarded_records: Path) -> None:
    """fwd_control has a clustered index — classify_table must see it as supported."""
    store = _store(fixture_bak_forwarded_records)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    result = classify_table(tables["fwd_control"])
    assert result.supported, f"expected supported clustered, got: {result.reason}"


# ---------------------------------------------------------------------------
# Row count — primary correctness gate
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_fwd_heap_row_count(fixture_bak_forwarded_records: Path) -> None:
    """fwd_heap must return exactly ROW_COUNT rows.

    A scanner that double-counts stubs + real rows will return ~1.5 × ROW_COUNT.
    One that skips forwarded targets will return ~0.5 × ROW_COUNT.
    """
    rows = _rows(fixture_bak_forwarded_records, "fwd_heap")
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT:,} rows, got {len(rows):,} "
        f"(forwarding stubs may be double-counted or skipped)"
    )


@pytest.mark.fixture
def test_fwd_control_row_count(fixture_bak_forwarded_records: Path) -> None:
    """fwd_control (clustered) must also return ROW_COUNT rows."""
    rows = _rows(fixture_bak_forwarded_records, "fwd_control")
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT:,} rows, got {len(rows):,}"
    )


# ---------------------------------------------------------------------------
# Val values — verify forwarding pointers are followed correctly
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_fwd_heap_short_val_length(fixture_bak_forwarded_records: Path) -> None:
    """Even-id rows retain their short val (SHORT_VAL_LEN chars, in-place)."""
    rows = _rows(fixture_bak_forwarded_records, "fwd_heap")
    by_id = {r["id"]: r for r in rows}
    bad = [
        (id_, len(r.get("val") or ""))
        for id_, r in by_id.items()
        if id_ % 2 == 0
        and (r.get("val") is None or len(r["val"]) != SHORT_VAL_LEN)
    ]
    assert not bad, (
        f"even-id rows (in-place) wrong val length for {len(bad)} ids: "
        f"first={bad[:3]}"
    )


@pytest.mark.fixture
def test_fwd_heap_long_val_length(fixture_bak_forwarded_records: Path) -> None:
    """Odd-id rows have their forwarded long val (LONG_VAL_LEN chars).

    These rows have forwarding stubs in their original slots.  The parser must
    follow the 6-byte RID pointer to the actual row on the overflow page and
    return the correct LONG_VAL_LEN-char string.
    """
    rows = _rows(fixture_bak_forwarded_records, "fwd_heap")
    by_id = {r["id"]: r for r in rows}
    bad = [
        (id_, len(r.get("val") or ""))
        for id_, r in by_id.items()
        if id_ % 2 == 1
        and (r.get("val") is None or len(r["val"]) != LONG_VAL_LEN)
    ]
    assert not bad, (
        f"odd-id rows (forwarded) wrong val length for {len(bad)} ids: "
        f"first={bad[:3]} "
        f"(stub followed but wrong value, or forwarded row not reached)"
    )


@pytest.mark.fixture
def test_fwd_heap_short_val_content(fixture_bak_forwarded_records: Path) -> None:
    """Even-id in-place rows contain the expected 'x' fill character."""
    rows = _rows(fixture_bak_forwarded_records, "fwd_heap")
    bad = [
        r["id"]
        for r in rows
        if r["id"] % 2 == 0
        and r.get("val") is not None
        and r["val"] != "x" * SHORT_VAL_LEN
    ]
    assert not bad, (
        f"even-id rows wrong val content for {len(bad)} ids: first={bad[:5]}"
    )


@pytest.mark.fixture
def test_fwd_heap_long_val_content(fixture_bak_forwarded_records: Path) -> None:
    """Odd-id forwarded rows contain the expected 'y' fill character."""
    rows = _rows(fixture_bak_forwarded_records, "fwd_heap")
    bad = [
        r["id"]
        for r in rows
        if r["id"] % 2 == 1
        and r.get("val") is not None
        and r["val"] != "y" * LONG_VAL_LEN
    ]
    assert not bad, (
        f"odd-id forwarded rows wrong val content for {len(bad)} ids: first={bad[:5]}"
    )


# ---------------------------------------------------------------------------
# Cross-check: heap vs control table
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_fwd_heap_matches_control(fixture_bak_forwarded_records: Path) -> None:
    """Every row in fwd_heap matches the corresponding row in fwd_control.

    This is the definitive correctness check: if forwarding stubs are handled
    correctly both tables must produce identical (id, val) pairs.
    """
    heap = {r["id"]: r["val"] for r in _rows(fixture_bak_forwarded_records, "fwd_heap")}
    ctrl = {r["id"]: r["val"] for r in _rows(fixture_bak_forwarded_records, "fwd_control")}

    missing = sorted(set(ctrl) - set(heap))
    extra = sorted(set(heap) - set(ctrl))
    mismatches = [
        (id_, heap[id_][:20] if heap.get(id_) else None, ctrl[id_][:20])
        for id_ in sorted(set(heap) & set(ctrl))
        if heap[id_] != ctrl[id_]
    ]

    assert not missing and not extra and not mismatches, (
        f"heap vs control mismatch: "
        f"missing={missing[:5]}, extra={extra[:5]}, value_diff={mismatches[:3]}"
    )
