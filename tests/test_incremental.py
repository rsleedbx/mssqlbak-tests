"""Full + 6 differential (incremental) backup chain — merge and correctness tests.

The ``IncrementalCoverage`` fixture chain consists of:

- ``incrementalcoverage_full.bak``   — 10 seed rows (batch=0), taken as a
  normal (non-COPY_ONLY) full backup so it can serve as a differential base.
- ``incrementalcoverage_diff_01.bak`` … ``incrementalcoverage_diff_06.bak``
  — each differential is cumulative: diff_N captures all changes since the full.

Change log per diff:
  diff 01: insert 5 rows (batch=1)
  diff 02: insert 5 rows (batch=2)  + UPDATE id=3
  diff 03: insert 5 rows (batch=3)  + UPDATE id=7
  diff 04: insert 5 rows (batch=4)  + UPDATE id=12
  diff 05: insert 5 rows (batch=5)  + UPDATE id=18
  diff 06: insert 5 rows (batch=6)  + UPDATE id=24

After diff N: total rows = 10 + N*5.

Key property tested: ``PageStore.from_diff_bak(diff_N, full)`` reconstructs the
exact state at step N without chaining — because SQL Server differentials are
cumulative, the latest diff already contains every prior modification.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rows_for(store: AnyPageStore) -> list[dict]:
    tables = {t.name: t for t in recover_schema(store).tables}
    return list(read_table_rows(store, tables["sync_batch"]))


# Per-diff metadata that drives parametrize fixtures.
# (diff_index 1-based, expected_total_rows, updated_id_or_None)
_DIFF_META = [
    (1, 15, None),
    (2, 20, 3),
    (3, 25, 7),
    (4, 30, 12),
    (5, 35, 18),
    (6, 40, 24),
]

# All updated row ids visible in diff_06 (cumulative).
_ALL_UPDATED_IDS = {m[2] for m in _DIFF_META if m[2] is not None}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_full_baseline(fixture_bak_incremental: tuple[Path, list[Path]]) -> None:
    """Full backup alone has exactly 10 seed rows, all from batch 0.

    No diff pages have been applied; the table should be in its initial state.
    """
    full, _ = fixture_bak_incremental
    rows = _rows_for(PageStore.from_bak(full))

    assert len(rows) == 10, f"expected 10 seed rows, got {len(rows)}"
    batches = {r["batch"] for r in rows}
    assert batches == {0}, f"expected all batch=0, got {batches}"
    actions = {r["action"] for r in rows}
    assert actions == {"insert"}, f"expected all action='insert', got {actions}"


@pytest.mark.fixture
@pytest.mark.parametrize("n,expected_rows,updated_id", _DIFF_META,
                         ids=[f"diff{m[0]:02d}" for m in _DIFF_META])
def test_diff_row_count(
    n: int,
    expected_rows: int,
    updated_id: int | None,
    fixture_bak_incremental: tuple[Path, list[Path]],
) -> None:
    """After merging diff_N onto the full, the table has exactly 10 + N*5 rows.

    Each differential backup is cumulative relative to the full, so applying
    diff_N directly (without chaining earlier diffs) yields the complete state.
    """
    full, diffs = fixture_bak_incremental
    store = PageStore.from_diff_bak(diffs[n - 1], full)
    rows = _rows_for(store)

    assert len(rows) == expected_rows, (
        f"diff_{n:02d}: expected {expected_rows} rows, got {len(rows)}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("n,expected_rows,updated_id",
                         [(m[0], m[1], m[2]) for m in _DIFF_META if m[2] is not None],
                         ids=[f"diff{m[0]:02d}" for m in _DIFF_META if m[2] is not None])
def test_diff_updated_value_visible(
    n: int,
    expected_rows: int,
    updated_id: int,
    fixture_bak_incremental: tuple[Path, list[Path]],
) -> None:
    """The row modified in diff_N has action='update' after the merge.

    This confirms that updated pages are correctly taken from the differential
    rather than the (stale) full backup.
    """
    full, diffs = fixture_bak_incremental
    store = PageStore.from_diff_bak(diffs[n - 1], full)
    rows_by_id = {r["id"]: r for r in _rows_for(store)}

    assert updated_id in rows_by_id, f"id={updated_id} not found after diff_{n:02d}"
    row = rows_by_id[updated_id]
    assert row["action"] == "update", (
        f"id={updated_id} after diff_{n:02d}: expected action='update', "
        f"got {row['action']!r}"
    )
    assert f"diff {n:02d}" in row["val"], (
        f"id={updated_id}: val {row['val']!r} does not reference diff {n:02d}"
    )


@pytest.mark.fixture
def test_diffs_are_cumulative(fixture_bak_incremental: tuple[Path, list[Path]]) -> None:
    """diff_06 alone (merged with the full) contains every prior modification.

    SQL Server differentials are cumulative: each diff captures all changes
    since the full backup.  A consumer only needs to store the latest diff per
    full — earlier diffs are redundant.

    Verified by asserting that diff_06 has:
    - 40 total rows (10 seed + 6*5 inserts)
    - All 5 updated rows (ids 3, 7, 12, 18, 24) with action='update'
    """
    full, diffs = fixture_bak_incremental
    store = PageStore.from_diff_bak(diffs[5], full)  # diff_06
    rows = _rows_for(store)
    rows_by_id = {r["id"]: r for r in rows}

    assert len(rows) == 40, f"diff_06: expected 40 rows, got {len(rows)}"

    for uid in _ALL_UPDATED_IDS:
        assert uid in rows_by_id, f"id={uid} missing from diff_06 merge"
        assert rows_by_id[uid]["action"] == "update", (
            f"id={uid}: expected action='update' in diff_06, "
            f"got {rows_by_id[uid]['action']!r}"
        )

    # Verify all 6 insert batches are present
    batches_seen = {r["batch"] for r in rows}
    assert batches_seen == set(range(7)), (
        f"expected batches 0–6, got {sorted(batches_seen)}"
    )


@pytest.mark.fixture
def test_full_not_affected_by_diffs(fixture_bak_incremental: tuple[Path, list[Path]]) -> None:
    """Reading the full backup after all diffs are merged still returns only 10 rows.

    Merging does not mutate the underlying file; the full backup remains the
    unchanged base for any future merge.
    """
    full, _ = fixture_bak_incremental
    rows = _rows_for(PageStore.from_bak(full))
    assert len(rows) == 10, (
        f"full should still have 10 rows after diffs were applied elsewhere, "
        f"got {len(rows)}"
    )
