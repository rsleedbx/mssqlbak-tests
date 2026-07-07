"""Tests for the MDF page layer (header, slot array, page accessor)."""
from __future__ import annotations

import struct

import pytest

from mssqlbak.pages import AnyPageStore, HEADER_SIZE, PAGE_SIZE, Page, PageHeader, PageStore, restore_torn_page

# Page header offsets and flags (mirrors mssqlbak.pages internals).
_H_FLAG_BITS = 4   # uint16  m_flagBits
_H_TORN_BITS = 60  # uint32  m_tornBits
_FLAG_TORN_PAGE_DETECTION = 0x100
_FLAG_CHECKSUM = 0x200

_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _blank_page() -> bytearray:
    """Return a zero-filled 8 KB bytearray."""
    return bytearray(PAGE_SIZE)


def _set_flag_bits(page: bytearray, flags: int) -> None:
    _U16.pack_into(page, _H_FLAG_BITS, flags)


def _make_torn_page(
    sector_data: dict[int, int],
) -> tuple[bytes, bytes]:
    """Return *(torn_page, expected_restored)* for a TORN_PAGE_DETECTION page.

    *sector_data* maps sector index (1–15) to the desired *true* value of the
    last byte of that sector.  The torn page has those bytes overwritten with
    an arbitrary write signature and the original bits saved in ``m_tornBits``.
    ``restore_torn_page(torn_page)`` must return ``expected_restored``.

    Note: ``restore_torn_page`` does **not** clear ``m_tornBits`` after use, so
    ``expected_restored`` retains the ``m_tornBits`` value from ``torn_page``.
    """
    pre_write = _blank_page()
    _set_flag_bits(pre_write, _FLAG_TORN_PAGE_DETECTION)

    for sector, byte_val in sector_data.items():
        pre_write[sector * 512 + 511] = byte_val & 0xFF

    # Build the torn page: save real low-2-bits in m_tornBits, overwrite with sig.
    torn = bytearray(pre_write)
    tornbits = 0
    for sector in range(1, 16):
        off = sector * 512 + 511
        real_pair = pre_write[off] & 0x3
        tornbits |= real_pair << (2 * sector)
        sig = 0x1 if sector % 2 else 0x2
        torn[off] = (torn[off] & 0xFC) | sig
    _U32.pack_into(torn, _H_TORN_BITS, tornbits)

    # Expected result: pre_write bytes at sector boundaries, m_tornBits still set.
    expected = bytearray(pre_write)
    _U32.pack_into(expected, _H_TORN_BITS, tornbits)
    return bytes(torn), bytes(expected)


@pytest.fixture
def store(fixture_bak) -> AnyPageStore:
    return PageStore.from_bak(fixture_bak)


def _first_data_page(store: AnyPageStore) -> Page:
    """Return the first allocated data page (m_type == 1) with at least one slot."""
    for pid in range(store.page_count):
        page = store.page(pid)
        if page.header.m_type == 1 and page.header.slot_cnt > 0:
            return page
    pytest.skip("no data page with slots found in fixture")


@pytest.mark.fixture
def test_boot_page_type(store: PageStore) -> None:
    assert store.page(9).header.m_type == 13


@pytest.mark.fixture
def test_file_header_page(store: PageStore) -> None:
    h = store.page(0).header
    assert h.m_type == 15
    assert h.page_id == 0
    assert h.file_id == 1


@pytest.mark.fixture
def test_page_id_file_id_round_trip(store: PageStore) -> None:
    checked = 0
    for pid in range(store.page_count):
        page = store.page(pid)
        # Skip unallocated/zero pages, which carry no real header.
        if page.raw == b"\x00" * PAGE_SIZE:
            continue
        assert page.header.page_id == pid
        assert page.header.file_id == 1
        checked += 1
    assert checked > 0


@pytest.mark.fixture
def test_slot_array_in_bounds(store: PageStore) -> None:
    page = _first_data_page(store)
    h = page.header
    slots = page.slot_array()
    assert len(slots) == h.slot_cnt
    for off in slots:
        assert HEADER_SIZE <= off < PAGE_SIZE
        # Records live in the used area, below free_data (the start of free space).
        assert off <= h.free_data


@pytest.mark.fixture
def test_record_non_empty(store: PageStore) -> None:
    page = _first_data_page(store)
    for slot in range(len(page.slot_array())):
        assert len(page.record(slot)) > 0


@pytest.mark.fixture
def test_header_is_frozen_dataclass(store: PageStore) -> None:
    h = store.page(9).header
    assert isinstance(h, PageHeader)
    with pytest.raises(AttributeError):
        h.m_type = 1  # type: ignore[misc]


def test_absent_file_id_raises() -> None:
    # from_pages builds a single-file (file 1) store, so file 2 is not present.
    store = PageStore.from_pages(b"\x00" * PAGE_SIZE)
    with pytest.raises((ValueError, IndexError)):
        store.page(0, file_id=2)


def test_multi_file_store_indexes_each_file() -> None:
    img1 = bytearray(PAGE_SIZE)
    struct.pack_into("<IH", img1, 32, 0, 1)
    img3 = bytearray(PAGE_SIZE)
    struct.pack_into("<IH", img3, 32, 0, 3)
    store = PageStore({1: bytes(img1), 3: bytes(img3)})
    assert store.available_files == frozenset({1, 3})
    assert store.page(0, file_id=1).header.file_id == 1
    assert store.page(0, file_id=3).header.file_id == 3
    assert store.page_count_for(3) == 1


def test_page_id_out_of_range_raises() -> None:
    store = PageStore.from_pages(b"\x00" * PAGE_SIZE)
    with pytest.raises((ValueError, IndexError)):
        store.page(1)
    with pytest.raises((ValueError, IndexError)):
        store.page(-1)


def test_from_pages_rejects_unaligned() -> None:
    with pytest.raises(ValueError):
        PageStore.from_pages(b"\x00" * (PAGE_SIZE + 3))


# ---------------------------------------------------------------------------
# restore_torn_page — TORN_PAGE_DETECTION reversal (regression: 2ed478b)
#
# SQL Server 2000-era databases (and any database with PAGE_VERIFY set to
# TORN_PAGE_DETECTION) overwrite the low 2 bits of the last byte of each
# 512-byte sector with an alternating signature, saving the displaced bits in
# the m_tornBits header field.  Before the fix, mssqlbak never reversed this,
# causing slot offsets and fixed-length column bytes that landed on a sector
# boundary to decode one bit too high — dropping 9,303 rows from
# CreditBackup100.bak.  restore_torn_page() must be tested without a live
# fixture since CreditBackup100 is a 500 MB real-world download.
# ---------------------------------------------------------------------------

def test_restore_torn_page_no_op_for_unprotected() -> None:
    """Pages with no protection flag are returned unchanged."""
    page = _blank_page()
    _set_flag_bits(page, 0x000)  # neither TORN nor CHECKSUM
    page[511] = 0xAB
    result = restore_torn_page(bytes(page))
    assert result[511] == 0xAB


def test_restore_torn_page_no_op_for_checksum() -> None:
    """Pages with CHECKSUM protection are returned unchanged."""
    page = _blank_page()
    _set_flag_bits(page, _FLAG_CHECKSUM)
    page[511] = 0xCD
    result = restore_torn_page(bytes(page))
    assert result[511] == 0xCD


def test_restore_torn_page_no_op_for_short_page() -> None:
    """Pages shorter than PAGE_SIZE are returned unchanged (guard against truncation)."""
    page = bytes(PAGE_SIZE - 1)
    assert restore_torn_page(page) is page


def test_restore_torn_page_single_sector() -> None:
    """Sector 1 last byte has its low 2 bits restored from m_tornBits."""
    # Sector 1 last byte = 0xFC (low 2 bits = 0b00)
    torn, expected = _make_torn_page({1: 0xFC})
    assert restore_torn_page(torn) == expected


def test_restore_torn_page_all_bit_patterns() -> None:
    """All four possible 2-bit patterns (00 01 10 11) are restored correctly.

    Uses sectors 1, 5, 10, 15 to cover each pattern independently.
    """
    # byte values whose low 2 bits are 00, 01, 10, 11
    sector_data = {
        1:  0xA4,  # low 2 = 00
        5:  0xA5,  # low 2 = 01
        10: 0xA6,  # low 2 = 10
        15: 0xA7,  # low 2 = 11
    }
    torn, expected = _make_torn_page(sector_data)
    assert restore_torn_page(torn) == expected


def test_restore_torn_page_all_fifteen_sectors() -> None:
    """All 15 sectors (1–15) have their displaced bits restored in one call."""
    sector_data = {s: (0x40 | s) for s in range(1, 16)}
    torn, expected = _make_torn_page(sector_data)
    assert restore_torn_page(torn) == expected


def test_restore_torn_page_sector_0_untouched() -> None:
    """Sector 0 (the header sector) last byte is never modified by restore."""
    page = _blank_page()
    _set_flag_bits(page, _FLAG_TORN_PAGE_DETECTION)
    page[511] = 0xFF  # last byte of sector 0
    result = restore_torn_page(bytes(page))
    assert result[511] == 0xFF, "sector 0 last byte must be untouched"


def test_restore_torn_page_non_sector_bytes_untouched() -> None:
    """Bytes that are not the last byte of a sector are never modified."""
    torn, _ = _make_torn_page({3: 0xAB})
    restored = restore_torn_page(torn)
    # Check a mid-sector byte in sector 3 that is NOT the last byte
    mid = 3 * 512 + 256
    assert restored[mid] == torn[mid], "mid-sector bytes must not be altered"


def test_restore_torn_page_idempotent_on_original() -> None:
    """Applying restore to an already-correct page with m_tornBits=0 is a no-op.

    When m_tornBits is all zeros, the 2-bit pairs are all 0b00, so restore
    merely sets the low 2 bits of each sector boundary byte to zero.  This
    verifies the function is not accidentally destructive on clean pages.
    """
    page = _blank_page()
    _set_flag_bits(page, _FLAG_TORN_PAGE_DETECTION)
    # Set some distinguishable bytes at non-sector-boundary positions only.
    page[100] = 0xBE
    page[200] = 0xEF
    result = restore_torn_page(bytes(page))
    assert result[100] == 0xBE
    assert result[200] == 0xEF


def test_restore_torn_page_returns_bytes_not_bytearray() -> None:
    """restore_torn_page always returns bytes, regardless of input type."""
    torn, _ = _make_torn_page({1: 0x55})
    result = restore_torn_page(torn)
    assert isinstance(result, bytes)
