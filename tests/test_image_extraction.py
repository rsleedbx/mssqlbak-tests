"""Unit tests for MDF image bounding and page-density safety.

These guard the two real-database fixes (found against AdventureWorks) without a
large committed .bak: the image walk must step over blank/uninitialised interior
pages, and PageStore must reject a misaligned (sparse-layout) read loudly rather
than return wrong bytes.
"""
from __future__ import annotations

import struct

import pytest

from mssqlbak import mtf
from mssqlbak.pages import PageStore

P = mtf.PAGE_SIZE


def _page(page_id: int, file_id: int = 1, *, header_version: int = 1, m_type: int = 1) -> bytes:
    """Build a minimal 8 KB page with a given locator at offset 32."""
    buf = bytearray(P)
    buf[0] = header_version
    buf[1] = m_type
    struct.pack_into("<IH", buf, 32, page_id, file_id)
    return bytes(buf)


def _blank_but_nonzero() -> bytes:
    """An interior page with a blank locator (0/0) that is not all-zero."""
    buf = bytearray(P)
    buf[100] = 0xAB  # some leftover byte => not _ZERO_PAGE, locator still 0/0
    return bytes(buf)


def test_walk_skips_blanks_and_stops_at_framing() -> None:
    # file-header anchor (page 0 type 15) + page 1, a blank interior page at
    # index 2, real pages 3 and 4, then a framing page that ends the image.
    image = (
        _page(0, m_type=15)
        + _page(1)
        + _blank_but_nonzero()
        + _page(3)
        + _page(4)
    )
    framing = _page(999, file_id=7, header_version=83, m_type=77)
    buf = image + framing
    start = mtf._find_image_start(buf)
    assert start == 0
    # blank locator (index 2) skipped, framing (file_id 7, not a known file) ends it
    walked = list(mtf._walk_image_pages(buf, start))
    assert [(fid, pid) for fid, pid, _, _ in walked] == [(1, 0), (1, 1), (1, 3), (1, 4)]


def test_walk_spans_secondary_file() -> None:
    # File 1 (header + page 1), then a secondary file 3 introduced by its own
    # file-header page (m_type 15, page 0), then a framing block that ends it.
    buf = (
        _page(0, m_type=15)
        + _page(1)
        + _page(0, file_id=3, m_type=15)
        + _page(7, file_id=3)
        + _page(999, file_id=9, header_version=83, m_type=77)
    )
    start = mtf._find_image_start(buf)
    walked = [(fid, pid) for fid, pid, _, _ in mtf._walk_image_pages(buf, start)]
    assert walked == [(1, 0), (1, 1), (3, 0), (3, 7)]


def test_walk_places_pages_by_id_across_gaps() -> None:
    # A backup stream that omits an unallocated extent: page-id jumps 1 -> 5.
    # The assembled image must place each page at page_id * PAGE_SIZE, so the
    # gap (pages 2..4) is zero-filled and page 5 is addressable at its own id.
    buf = _page(0, m_type=15) + _page(1) + _page(5) + _page(99, file_id=7)
    start = mtf._find_image_start(buf)
    file1 = {pid: page for fid, pid, page, _ in mtf._walk_image_pages(buf, start) if fid == 1}
    image = mtf.assemble_image(file1)
    store = PageStore.from_pages(image)
    assert store.page_count == 6  # pages 0..5
    assert store.page(0).header.page_id == 0
    assert store.page(1).header.page_id == 1
    assert store.page(5).header.page_id == 5
    assert image[2 * P : 3 * P] == bytes(P)  # gap page is zero-filled


def test_pagestore_rejects_misaligned_sparse_read() -> None:
    # index 2 holds a page whose own id is 99 (sparse layout): reading page 2
    # must fail loudly instead of returning page 99's bytes.
    buf = _page(0, m_type=15) + _page(1) + _page(99)
    store = PageStore.from_pages(buf)
    assert store.page(1).header.page_id == 1
    with pytest.raises(ValueError, match="sparse"):
        store.page(2)


def test_pagestore_allows_aligned_and_blank_pages() -> None:
    buf = _page(0, m_type=15) + _page(1) + _blank_but_nonzero()
    store = PageStore.from_pages(buf)
    assert store.page(1).header.page_id == 1
    # a blank (0/0) slot carries no locator, so it is not treated as misaligned
    assert store.page(2).header.page_id == 0


# ── assemble_files: keep real files, drop mis-decode phantoms ──────────────────

def test_assemble_keeps_file_with_header_page() -> None:
    pages = {0: _page(0, m_type=15), 1: _page(1)}
    assert set(mtf.assemble_files({1: pages})) == {1}


def test_assemble_keeps_headerless_real_file() -> None:
    # No file-header page (page 0 is an ordinary data page), but many pages and a
    # bounded image -> a real primary file whose header was not surfaced
    # (WideWorldImporters-Full_old).
    pages = {i: _page(i, m_type=1) for i in range(mtf._MIN_HEADERLESS_PAGES)}
    assert set(mtf.assemble_files({1: pages})) == {1}


def test_assemble_drops_few_page_phantom() -> None:
    # A mis-decode spawns a handful of pages under a garbage file id.
    pages = {i: _page(i, file_id=62706) for i in range(4)}
    assert mtf.assemble_files({62706: pages}) == {}


def test_assemble_drops_absurd_image_phantom() -> None:
    # Enough pages to pass the count gate, but one absurd page id would force an
    # image far larger than the cap -> dropped.
    huge = (mtf._MAX_HEADERLESS_IMAGE_BYTES // P) + 10
    pages = {i: _page(i, file_id=5) for i in range(mtf._MIN_HEADERLESS_PAGES)}
    pages[huge] = _page(0, file_id=5)
    assert mtf.assemble_files({5: pages}) == {}


def test_assemble_drops_file_id_zero() -> None:
    pages = {0: _page(0, file_id=0, m_type=15), 1: _page(1, file_id=0)}
    assert mtf.assemble_files({0: pages}) == {}


def test_recover_schema_without_primary_file_degrades_gracefully() -> None:
    # A store with only a secondary file (no file_id=1) cannot hold the catalog;
    # recovery must raise a clear CatalogError, not a raw IndexError.
    from mssqlbak.catalog import CatalogError, recover_schema

    store = PageStore({3: bytes(2 * P)})
    with pytest.raises(CatalogError, match="no primary data file"):
        recover_schema(store)
