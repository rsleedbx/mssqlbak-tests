"""Tests for MTF/VDI checkpoint-block gap bridging in _walk_image_pages.

SQL Server periodically inserts MTF/VDI checkpoint blocks into the backup data
stream.  Before the fix these non-SQL blocks caused _walk_image_pages to stop
early, silently truncating the page image.  BaseballData.bak was the reproducer:
8 gaps of 1–6 pages cut off 23 of 25 table definitions and all their data.

All tests here build synthetic BAK bytes in memory — no SQL Server or fixture
file required.  The helpers construct the minimal page-header fields that
_walk_image_pages and _find_image_start inspect.
"""
from __future__ import annotations

import os
import struct
from pathlib import Path

import pytest

from mssqlbak.mtf import (
    PAGE_SIZE,
    _MTF_GAP_SCAN_PAGES,
    _walk_image_pages,
    extract_mdf_files,
)

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))

# ---------------------------------------------------------------------------
# Synthetic-BAK helpers
# ---------------------------------------------------------------------------

_PAGE_LOC_S = struct.Struct("<IH")  # (page_id, file_id) at offset 32 in every page


def _sql_page(page_id: int, file_id: int = 1, m_type: int = 1) -> bytes:
    """Minimal valid SQL Server page: hv=1, given m_type, locator at offset 32."""
    page = bytearray(PAGE_SIZE)
    page[0] = 1        # m_headerVersion == 1
    page[1] = m_type   # m_type
    _PAGE_LOC_S.pack_into(page, 32, page_id, file_id)
    return bytes(page)


def _file_header(file_id: int = 1) -> bytes:
    """SQL Server file-header page (m_type=15, page_id=0)."""
    return _sql_page(0, file_id, m_type=15)


def _checkpoint_block(n: int = 1) -> bytes:
    """Non-SQL VDI/MTF checkpoint block: n × PAGE_SIZE mirroring real BAK bytes.

    Each page has hv=0x80 (rejected by the hv==1 guard in the gap scan) and a
    non-zero locator (pid=14811136, fid=0) taken from the actual BaseballData.bak
    checkpoint block.  The non-zero pid is critical: pages with (pid=0, fid=0)
    are swallowed by the blank-locator fast-path in _walk_image_pages before the
    gap-scan code is reached, so they would not exercise the bridging logic.
    """
    block = bytearray(n * PAGE_SIZE)
    for i in range(n):
        off = i * PAGE_SIZE
        block[off] = 0x80   # hv != 1 — never a valid SQL page
        _PAGE_LOC_S.pack_into(block, off + 32, 14_811_136, 0)  # fid=0 ∉ known_files
    return bytes(block)


def _zero_pages(n: int = 1) -> bytes:
    """Unallocated (zero-filled) pages — skipped by the blank-locator check."""
    return bytes(n * PAGE_SIZE)


def _hv80_page_with_known_fid(page_id: int = 78531, file_id: int = 1) -> bytes:
    """A non-SQL block that carries a *known* file_id in its locator bytes.

    This simulates the BaseballData.bak pattern where hv=0x80 but file_id=1
    appears at skip=5, just before the true SQL resumption at skip=6.  Without
    the hv==1 guard the old code would have accepted this as a valid page.
    """
    page = bytearray(PAGE_SIZE)
    page[0] = 0x80  # hv != 1 — must be rejected
    _PAGE_LOC_S.pack_into(page, 32, page_id, file_id)
    return bytes(page)


def _pages(*page_ids: int, file_id: int = 1) -> bytes:
    return b"".join(_sql_page(pid, file_id) for pid in page_ids)


# A minimal BAK starts with a file-header page (pid=0, fid=1) so that
# _find_image_start locates offset 0, then the page at offset 0+PAGE_SIZE
# must have pid=1, fid=1 (the two-page anchor check).
def _minimal_bak(*blocks: bytes) -> bytes:
    return b"".join(blocks)


# ---------------------------------------------------------------------------
# Unit tests: _walk_image_pages (private, direct)
# ---------------------------------------------------------------------------


class TestWalkImagePagesGapBridging:
    """Direct unit tests for the gap-bridging path in _walk_image_pages."""

    def _pids(self, buf: bytes) -> list[int]:
        return [pid for _fid, pid, _page in _walk_image_pages(buf, 0)]

    def test_clean_stream_all_pages_yielded(self) -> None:
        """Baseline: no gaps → all pages come out in order."""
        buf = _file_header() + _pages(1, 2, 3, 4, 5)
        assert self._pids(buf) == [0, 1, 2, 3, 4, 5]

    def test_single_gap_one_checkpoint_page(self) -> None:
        """One-page checkpoint block mid-stream is skipped; SQL resumes."""
        buf = (
            _file_header()
            + _pages(1, 2)
            + _checkpoint_block(1)
            + _pages(3, 4)
        )
        assert self._pids(buf) == [0, 1, 2, 3, 4]

    def test_single_gap_two_checkpoint_pages(self) -> None:
        """Two-page gap (the BaseballData.bak gap-1 size) is bridged."""
        buf = (
            _file_header()
            + _pages(1, 2)
            + _checkpoint_block(2)
            + _pages(3, 4)
        )
        assert self._pids(buf) == [0, 1, 2, 3, 4]

    def test_single_gap_max_allowed(self) -> None:
        """Gap of exactly _MTF_GAP_SCAN_PAGES checkpoint pages is the boundary case.

        With N checkpoint pages the gap scan visits skip=1..N; the SQL
        resumption at skip=N falls on the last scan position, so it is found.
        """
        # _MTF_GAP_SCAN_PAGES = 10 checkpoint pages → SQL at skip=10 → bridged
        buf = (
            _file_header()
            + _pages(1)
            + _checkpoint_block(_MTF_GAP_SCAN_PAGES)
            + _pages(2)
        )
        pids = self._pids(buf)
        assert 2 in pids

    def test_single_gap_one_beyond_cap_stops_stream(self) -> None:
        """Gap of _MTF_GAP_SCAN_PAGES + 1 checkpoint pages falls outside the window.

        The SQL resumption would be at skip = _MTF_GAP_SCAN_PAGES + 1, one
        past the last scan position.  The stream terminates cleanly.
        """
        # _MTF_GAP_SCAN_PAGES + 1 = 11 checkpoint pages → SQL at skip=11 → not bridged
        buf = (
            _file_header()
            + _pages(1)
            + _checkpoint_block(_MTF_GAP_SCAN_PAGES + 1)
            + _pages(2)
        )
        pids = self._pids(buf)
        # Stream stops at the gap — page 2 is NOT yielded.
        assert 2 not in pids
        assert 1 in pids

    def test_hv80_false_positive_within_gap_is_skipped(self) -> None:
        """Reproduces BaseballData.bak gap at offset 53698048.

        Layout inside the gap (positions are skip values from the gap trigger):
          skip=1: checkpoint page (hv=0x80, fid=0) — continues scan
          skip=2: hv=0x80 page with fid=1 — tricky false positive; rejected by
                  the hv==1 guard (old code would have accepted it, corrupting the image)
          skip=3: real SQL resumption (hv=0x01, pid=10, fid=1)

        The gap trigger itself is at the start; the hv=0x80/fid=1 page is
        encountered during the scan, not before the gap begins.
        """
        gap = (
            _checkpoint_block(1)                         # gap trigger (skip=1 in scan)
            + _hv80_page_with_known_fid(page_id=78531)  # false-positive (skip=2 in scan)
            + _sql_page(10)                              # real SQL (skip=3 in scan)
        )
        buf = _file_header() + _pages(1) + gap + _pages(11)
        pids = self._pids(buf)
        # Gap is bridged; pages 10 and 11 are present.
        assert 10 in pids
        assert 11 in pids

    def test_zero_pages_within_gap_bridged(self) -> None:
        """Zero pages inside the gap (hv=0x00) are transparently skipped."""
        buf = (
            _file_header()
            + _pages(1)
            + _checkpoint_block(1)   # first non-SQL at skip=1
            + _zero_pages(2)         # two zeros at skip=2,3 (hv check sees 0x00 → skip)
            + _pages(5)              # real SQL at skip=4
        )
        pids = self._pids(buf)
        assert 5 in pids

    def test_multiple_gaps_all_bridged(self) -> None:
        """Multiple checkpoint blocks at different positions are all bridged.

        Mirrors the real BaseballData.bak behaviour (8 gaps interspersed).
        """
        buf = (
            _file_header()
            + _pages(1, 2)
            + _checkpoint_block(1)   # gap 1
            + _pages(3, 4, 5)
            + _checkpoint_block(2)   # gap 2
            + _pages(6, 7)
            + _checkpoint_block(1)   # gap 3
            + _pages(8)
        )
        assert self._pids(buf) == [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def test_all_pages_after_last_gap_are_yielded(self) -> None:
        """After bridging a gap, the full tail of SQL pages is read."""
        tail_count = 50
        buf = (
            _file_header()
            + _pages(1)
            + _checkpoint_block(2)
            + b"".join(_sql_page(i + 100) for i in range(tail_count))
        )
        pids = self._pids(buf)
        for i in range(tail_count):
            assert (i + 100) in pids, f"page {i + 100} missing after gap"

    def test_stream_ends_cleanly_with_no_false_extra_pages(self) -> None:
        """A checkpoint block at the very end (no valid SQL follows) stops cleanly."""
        buf = _file_header() + _pages(1, 2) + _checkpoint_block(3)
        pids = self._pids(buf)
        assert pids == [0, 1, 2]

    def test_new_file_header_in_gap_registers_secondary_file(self) -> None:
        """A file-header for a new file_id discovered during the gap scan is registered."""
        secondary_fh = _sql_page(0, file_id=2, m_type=15)
        secondary_page = _sql_page(1, file_id=2)
        buf = (
            _file_header(file_id=1)   # primary
            + _pages(1, 2)
            + _checkpoint_block(1)    # gap
            + secondary_fh            # new file_id=2 file-header inside the gap scan
            + secondary_page
        )
        results = list(_walk_image_pages(buf, 0))
        fid_pid = [(fid, pid) for fid, pid, _ in results]
        assert (2, 0) in fid_pid
        assert (2, 1) in fid_pid


# ---------------------------------------------------------------------------
# Integration tests: extract_mdf_files with synthetic BAK bytes on disk
# ---------------------------------------------------------------------------


class TestExtractMdfFilesGapBridging:
    """Integration tests through the full extract_mdf_files path.

    We write the synthetic BAK to a real temp file so the mmap path is
    exercised, then verify that the assembled image contains pages on both
    sides of the checkpoint block.
    """

    def _write_bak(self, tmp_path: Path, *blocks: bytes) -> Path:
        bak = tmp_path / "synthetic.bak"
        bak.write_bytes(b"".join(blocks))
        return bak

    def test_single_gap_pages_in_assembled_image(self, tmp_path: Path) -> None:
        """Pages from both sides of a checkpoint gap appear in the image."""
        bak = self._write_bak(
            tmp_path,
            _file_header(),    # page 0 — file-header (also _find_image_start anchor)
            _sql_page(1),      # page 1 — anchor page 2 required by _find_image_start
            _sql_page(2),
            _checkpoint_block(2),
            _sql_page(3),
            _sql_page(4),
        )
        images = extract_mdf_files(bak)
        img = images[1]
        assert len(img) >= 5 * PAGE_SIZE, "image too small — post-gap pages missing"
        # Page 3 should be readable at its expected offset.
        p3 = img[3 * PAGE_SIZE : 4 * PAGE_SIZE]
        pid, fid = _PAGE_LOC_S.unpack_from(p3, 32)
        assert pid == 3 and fid == 1

    def test_multiple_gaps_all_pages_present(self, tmp_path: Path) -> None:
        """All pages appear in the image when multiple checkpoint blocks interrupt the stream."""
        bak = self._write_bak(
            tmp_path,
            _file_header(),
            _sql_page(1),
            _sql_page(2),
            _checkpoint_block(1),
            _sql_page(3),
            _checkpoint_block(2),
            _sql_page(4),
        )
        images = extract_mdf_files(bak)
        img = images[1]
        for expected_pid in (0, 1, 2, 3, 4):
            p = img[expected_pid * PAGE_SIZE : (expected_pid + 1) * PAGE_SIZE]
            pid, fid = _PAGE_LOC_S.unpack_from(p, 32)
            assert pid == expected_pid, f"page {expected_pid} missing from image"
            assert fid == 1

    def test_hv80_false_positive_not_in_image(self, tmp_path: Path) -> None:
        """The hv=0x80 false-positive page discovered *during* the gap scan is not stored.

        Layout:
          sql(0=file-header), sql(1), sql(2)
          checkpoint_block(1)          ← gap trigger (hv=0x80, fid=0 → not known)
          hv80_page(pid=78531, fid=1)  ← skip=1 in gap scan: hv≠1, skipped
          sql(10)                       ← skip=2: hv=1, fid=1 → resumption
          sql(11)

        The gap scan jumps to sql(10), skipping over the hv=0x80 page entirely.
        page_id=78531 must therefore be zero-filled in the assembled image.
        """
        bak = self._write_bak(
            tmp_path,
            _file_header(),
            _sql_page(1),
            _sql_page(2),
            _checkpoint_block(1),                     # triggers gap scan
            _hv80_page_with_known_fid(page_id=78531), # false positive at skip=1
            _sql_page(10),                            # real resumption at skip=2
            _sql_page(11),
        )
        images = extract_mdf_files(bak)
        img = images[1]
        # page_id=78531 must NOT appear in the assembled image.
        if len(img) > 78531 * PAGE_SIZE:
            p = img[78531 * PAGE_SIZE : 78532 * PAGE_SIZE]
            assert p == bytes(PAGE_SIZE), "hv=0x80 false-positive was erroneously stored"
        # page_id=10 and 11 MUST be present (gap was bridged correctly).
        for expected_pid in (10, 11):
            p = img[expected_pid * PAGE_SIZE : (expected_pid + 1) * PAGE_SIZE]
            pid, fid = _PAGE_LOC_S.unpack_from(p, 32)
            assert pid == expected_pid and fid == 1


# ---------------------------------------------------------------------------
# Real-world smoke test (opt-in, requires tests/fixtures_realworld/)
# ---------------------------------------------------------------------------

_BASEBALL_BAK = Path(os.environ.get("SAMPLE_DIR", str(Path(__file__).parent / "fixtures_realworld"))) / "BaseballData.bak"
_BASEBALL_TABLE_COUNT = 25
_BASEBALL_TOTAL_ROWS = 493_104


@pytest.mark.samples
def test_baseball_all_25_tables_extracted(tmp_path: Path) -> None:
    """BaseballData.bak: all 25 tables extract with 0 skipped.

    This is the original reproducer for the MTF checkpoint-block gap bug.
    Before the fix 23 of 25 tables failed with either:
      - DeltaError: At least one column must be defined  (0-column tables)
      - ValueError: page_id N out of range               (out-of-image pages)

    Pass ``--samples`` to include this test.
    """
    if not _BASEBALL_BAK.exists():
        pytest.skip(f"BaseballData.bak not present at {_BASEBALL_BAK}")

    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore

    store = PageStore.from_bak(_BASEBALL_BAK)
    schema = recover_schema(store)

    zero_col = [t.name for t in schema.tables if len(t.columns) == 0]
    assert not zero_col, f"Tables with 0 columns (checkpoint gap bug): {zero_col}"
    assert len(schema.tables) == _BASEBALL_TABLE_COUNT, (
        f"Expected {_BASEBALL_TABLE_COUNT} tables, got {len(schema.tables)}"
    )
