"""Level-1 ghost records coverage tests (Gap H-2).

``ghost_records_full.bak`` — a heap table where 200 rows were deleted
immediately before the backup, leaving their ghost records (status bit 0x20)
physically on the pages.

Gap H-2 context: SQL Server's ghost record cleanup runs asynchronously.  A
backup taken before cleanup captures live rows and ghost records on the same
pages.  A heap scanner that does not check the ghost-record status bit
over-counts rows.  This matches the failure already observed in
``dirtycoverage_temporal_update`` but isolates it from temporal-table
complexity.

Schema: dbo.ghost_heap  (heap; no clustered index)
    id   INT          NOT NULL
    val  VARCHAR(100) NOT NULL

Data pattern (id range 1 .. TOTAL_ROWS):
    id 1 .. LIVE_ROW_COUNT   → live rows (present in backup, should be returned)
    id LIVE_ROW_COUNT+1 .. TOTAL_ROWS → ghost records (deleted, must be skipped)

Ghost records are guaranteed present via DBCC TRACEON(661, -1) during fixture
generation; the .bak file freezes their state permanently.

Fixture generation::

    python -m tools.fixture_run all-versions --suite ghost-records
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_ghost_records_fixture import (
    DELETED_ROWS,
    LIVE_ROW_COUNT,
    TOTAL_ROWS,
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
def test_ghost_heap_is_heap(fixture_bak_ghost_records: Path) -> None:
    """ghost_heap has no clustered index — classify_table must see it as a heap."""
    store = _store(fixture_bak_ghost_records)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    result = classify_table(tables["ghost_heap"])
    assert result.supported, f"expected supported heap, got: {result.reason}"


# ---------------------------------------------------------------------------
# Row count — primary correctness gate
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_ghost_heap_row_count(fixture_bak_ghost_records: Path) -> None:
    """ghost_heap must return exactly LIVE_ROW_COUNT rows.

    Ghost records (deleted before backup) must be skipped.
    A scanner that counts ghost records will return TOTAL_ROWS instead.
    """
    rows = _rows(fixture_bak_ghost_records, "ghost_heap")
    assert len(rows) == LIVE_ROW_COUNT, (
        f"expected {LIVE_ROW_COUNT:,} live rows, got {len(rows):,} "
        f"(TOTAL_ROWS={TOTAL_ROWS:,}, DELETED_ROWS={DELETED_ROWS:,}; "
        f"ghost records may be counted as live)"
    )


# ---------------------------------------------------------------------------
# Content — verify correct rows are returned (live, not ghost)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_ghost_heap_no_deleted_ids(fixture_bak_ghost_records: Path) -> None:
    """No deleted row (id > LIVE_ROW_COUNT) should appear in the results.

    Ghost records have id values LIVE_ROW_COUNT+1 .. TOTAL_ROWS.  If the
    parser returns any of these the ghost-record status bit is not being
    checked.
    """
    rows = _rows(fixture_bak_ghost_records, "ghost_heap")
    ghost_ids = [r["id"] for r in rows if r["id"] > LIVE_ROW_COUNT]
    assert not ghost_ids, (
        f"{len(ghost_ids)} ghost-record ids leaked into results: "
        f"first={ghost_ids[:5]} "
        f"(ids > {LIVE_ROW_COUNT} were deleted before backup)"
    )


@pytest.mark.fixture
def test_ghost_heap_all_live_ids_present(fixture_bak_ghost_records: Path) -> None:
    """Every live row (id 1 .. LIVE_ROW_COUNT) must be returned."""
    rows = _rows(fixture_bak_ghost_records, "ghost_heap")
    returned_ids = {r["id"] for r in rows}
    missing = [i for i in range(1, LIVE_ROW_COUNT + 1) if i not in returned_ids]
    assert not missing, (
        f"{len(missing)} live ids missing from results: first={missing[:5]}"
    )


@pytest.mark.fixture
def test_ghost_heap_val_content(fixture_bak_ghost_records: Path) -> None:
    """val for each live row must equal 'row_<id>'."""
    rows = _rows(fixture_bak_ghost_records, "ghost_heap")
    bad = [
        (r["id"], repr(r.get("val")))
        for r in rows
        if r.get("val") != f"row_{r['id']}"
    ]
    assert not bad, (
        f"val content wrong for {len(bad)} rows: first={bad[:3]}"
    )
