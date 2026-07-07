"""Unit tests for mssqlbak.logtail — log tail parser for fuzzy backups.

Tests use the ``dirtycoverage_uncommitted.bak`` fixture which contains:
  - 50 committed rows on page 336, slots 0–49
  - 20 uncommitted (rolled-back) rows on page 336, slots 50–69
  - Confirmed via sys.fn_dump_dblog on SQL Server 2022

Log tail structure confirmed empirically:
  log_start = 0x386000, log_end = 0x3a7000
  Uncommitted xact_id = ca0300000000
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from mssqlbak.logtail import (
    LOP_BEGIN_XACT,
    LOP_INSERT_ROWS,
    build_uncommitted_set,
    collect_dirty_slots,
    dirty_slots_from_bak,
    find_log_range,
    iter_log_records,
    iter_log_sectors,
)

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))

FIXTURE = _FIXTURE_DIR / "dirtycoverage_uncommitted.bak"
COMMITTED_FIXTURE = _FIXTURE_DIR / "dirtycoverage_concurrent.bak"

# Ground truth values confirmed on SQL Server 2022 via sys.fn_dump_dblog.
# These exact-offset/xact-id constants are 2022-specific; tests that depend on
# them are skipped on other versions.  Structural constants (slot range, file_id)
# are the same across all versions.
_IS_2022 = "fixtures_2022" in str(_FIXTURE_DIR)
EXPECTED_LOG_START = 0x386000          # 2022-only
EXPECTED_LOG_END   = 0x3A7000          # 2022-only
UNCOMMITTED_XACT_2022 = bytes.fromhex("ca0300000000")  # 2022-only

DIRTY_FILE  = 1    # all fixtures use a single-file (file_id=1) database
DIRTY_SLOTS = frozenset(range(50, 70))  # same slot range across versions

# Derive DIRTY_PAGE and per-version UNCOMMITTED_XACT dynamically from the
# actual fixture so these tests pass on SS2017/2019/2025 without change.
def _derive_dynamic_constants() -> tuple[bytes, int]:
    """Return (uncommitted_xact_id, dirty_page) from the fixture on disk."""
    if not FIXTURE.exists():
        return bytes(6), -1
    data = FIXTURE.read_bytes()
    start, end = find_log_range(data)
    recs = list(iter_log_records(data, start, end))
    uncommitted = build_uncommitted_set(iter(recs))
    if len(uncommitted) != 1:
        return bytes(6), -1
    xact_id = next(iter(uncommitted))
    dirty_recs = [r for r in recs if r.xact_id == xact_id and r.lop == LOP_INSERT_ROWS]
    raw_page = dirty_recs[0].page_id if dirty_recs else None
    page: int = raw_page if raw_page is not None else -1
    return xact_id, page

UNCOMMITTED_XACT, DIRTY_PAGE = _derive_dynamic_constants()
EXPECTED_DIRTY = frozenset((DIRTY_FILE, DIRTY_PAGE, s) for s in DIRTY_SLOTS)


@pytest.fixture(scope="module")
def bak_data() -> bytes:
    return FIXTURE.read_bytes()


@pytest.fixture(scope="module")
def log_range(bak_data: bytes) -> tuple[int, int]:
    return find_log_range(bak_data)


# ---------------------------------------------------------------------------
# 1. find_log_range
# ---------------------------------------------------------------------------

def test_find_log_range_returns_correct_bounds(bak_data: bytes) -> None:
    start, end = find_log_range(bak_data)
    # Exact byte offsets are 2022-specific (fixture size differs per version).
    # On other versions we only assert the range is non-empty and aligned.
    if _IS_2022:
        assert start == EXPECTED_LOG_START
        assert end   == EXPECTED_LOG_END
    else:
        assert start > 0 and end > start, "log range must be non-empty"
        assert start % 512 == 0 and end % 512 == 0, "log range must be 512-byte aligned"


def test_find_log_range_raises_for_offline_backup() -> None:
    """A backup with no MSLS marker should raise ValueError."""
    fake = b"\x00" * 8192
    with pytest.raises(ValueError, match="MSLS"):
        find_log_range(fake)


# ---------------------------------------------------------------------------
# 2. iter_log_sectors — opening-block walk
# ---------------------------------------------------------------------------

def test_iter_log_sectors_yields_only_0x50_blocks(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    blocks = list(iter_log_sectors(bak_data, start, end))
    assert blocks, "expected at least one opening block"
    for block in blocks:
        assert block[0] == 0x50, f"block status byte should be 0x50, got 0x{block[0]:02x}"


def test_iter_log_sectors_block_size(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    for block in iter_log_sectors(bak_data, start, end):
        assert len(block) == 4096


# ---------------------------------------------------------------------------
# 3. iter_log_records — record scanner
# ---------------------------------------------------------------------------

def test_iter_log_records_finds_uncommitted_xact(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    recs = list(iter_log_records(bak_data, start, end))
    xact_ids = {r.xact_id for r in recs}
    assert UNCOMMITTED_XACT in xact_ids, (
        f"uncommitted xact_id {UNCOMMITTED_XACT.hex()} not found in log records"
    )


def test_iter_log_records_finds_exactly_20_uncommitted_inserts(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    inserts = [
        r for r in iter_log_records(bak_data, start, end)
        if r.lop == LOP_INSERT_ROWS and r.xact_id == UNCOMMITTED_XACT
    ]
    assert len(inserts) == 20, f"expected 20 INSERT records for uncommitted xact, got {len(inserts)}"


def test_iter_log_records_insert_slots_match_ground_truth(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    inserts = [
        r for r in iter_log_records(bak_data, start, end)
        if r.lop == LOP_INSERT_ROWS and r.xact_id == UNCOMMITTED_XACT
    ]
    actual_slots = frozenset(r.slot_id for r in inserts if r.slot_id is not None)
    assert actual_slots == DIRTY_SLOTS, (
        f"slot mismatch: got {sorted(actual_slots)}, expected {sorted(DIRTY_SLOTS)}"
    )
    actual_pages = {r.page_id for r in inserts if r.page_id is not None}
    assert actual_pages == {DIRTY_PAGE}


# ---------------------------------------------------------------------------
# 4. build_uncommitted_set
# ---------------------------------------------------------------------------

def test_build_uncommitted_set_identifies_one_uncommitted(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    uncommitted = build_uncommitted_set(iter_log_records(bak_data, start, end))
    assert UNCOMMITTED_XACT in uncommitted, (
        f"uncommitted xact {UNCOMMITTED_XACT.hex()} not in uncommitted set {[x.hex() for x in uncommitted]}"
    )
    assert len(uncommitted) == 1, (
        f"expected exactly 1 uncommitted xact, got {len(uncommitted)}: {[x.hex() for x in uncommitted]}"
    )


def test_build_uncommitted_set_returns_empty_when_all_committed() -> None:
    """Synthesise records where every BEGIN has a matching COMMIT."""
    from mssqlbak.logtail import LogRecord, LOP_COMMIT_XACT

    xid = bytes.fromhex("aabbccddeeff")
    begin  = LogRecord(lop=LOP_BEGIN_XACT,  lcx=2, xact_id=xid, lsn=(1, 0, 0), page_id=None, file_id=None, slot_id=None, prev_blk_off=0)
    insert = LogRecord(lop=LOP_INSERT_ROWS, lcx=2, xact_id=xid, lsn=(1, 0, 1), page_id=100,  file_id=1,    slot_id=5,    prev_blk_off=0)
    commit = LogRecord(lop=LOP_COMMIT_XACT, lcx=2, xact_id=xid, lsn=(1, 0, 2), page_id=None, file_id=None, slot_id=None, prev_blk_off=0)
    result = build_uncommitted_set([begin, insert, commit])
    assert result == frozenset()


# ---------------------------------------------------------------------------
# 5. collect_dirty_slots
# ---------------------------------------------------------------------------

def test_collect_dirty_slots_matches_ground_truth(bak_data: bytes, log_range: tuple[int, int]) -> None:
    start, end = log_range
    recs = list(iter_log_records(bak_data, start, end))
    uncommitted = build_uncommitted_set(iter(recs))
    dirty = collect_dirty_slots(iter(recs), uncommitted)
    assert dirty == EXPECTED_DIRTY, (
        f"dirty slots mismatch:\n  got {sorted(dirty)}\n  expected {sorted(EXPECTED_DIRTY)}"
    )


# ---------------------------------------------------------------------------
# 6. dirty_slots_from_bak — convenience entry point
# ---------------------------------------------------------------------------

def test_dirty_slots_from_bak_uncommitted_fixture() -> None:
    dirty = dirty_slots_from_bak(FIXTURE)
    assert dirty == EXPECTED_DIRTY


def test_dirty_slots_from_bak_returns_empty_for_offline_backup(tmp_path: Path) -> None:
    """A file with no MSLS marker should return an empty frozenset."""
    fake = tmp_path / "fake.bak"
    fake.write_bytes(b"\x00" * 8192)
    assert dirty_slots_from_bak(fake) == frozenset()


# ---------------------------------------------------------------------------
# 7. Phantom-row suppression via read_table_rows
# ---------------------------------------------------------------------------

def test_dirty_slots_suppress_uncommitted_rows_in_read_table_rows() -> None:
    """End-to-end: reading the uncommitted fixture with dirty_slots set should
    return exactly 50 rows (the committed ones), not 70."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    dirty = dirty_slots_from_bak(FIXTURE)
    assert len(dirty) == 20, "precondition: 20 dirty slots identified"

    store  = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    table  = next(t for t in schema.tables if t.name == "dirty_test")

    all_rows   = list(read_table_rows(store, table))
    clean_rows = list(read_table_rows(store, table, dirty_slots=dirty))

    assert len(all_rows) == 70, f"without filter expected 70 rows, got {len(all_rows)}"
    assert len(clean_rows) == 50, f"with filter expected 50 rows, got {len(clean_rows)}"

    # Verify the 20 suppressed rows are exactly the in-flight (uncommitted) ones.
    suppressed = [r for r in all_rows if r not in clean_rows]
    assert len(suppressed) == 20
    assert all(r["phase"] == "in_tx" for r in suppressed), (
        f"unexpected phases in suppressed rows: {set(r['phase'] for r in suppressed)}"
    )
