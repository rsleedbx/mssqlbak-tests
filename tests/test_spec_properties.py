"""Property and fuzz tests on committed fixture record bytes."""

from __future__ import annotations

import struct

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.records import decode_record
from mssqlbak.rows import _record_columns, _data_pages
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
def test_null_bitmap_size_matches_ncol(fixture_bak) -> None:
    """Null bitmap byte length == (ncol + 7) // 8 for FixedVar records."""
    store = PageStore.from_bak(fixture_bak)
    table = next(t for t in recover_schema(store).tables if t.name == "t_int")
    rec_cols = _record_columns(table)
    ncol = len(rec_cols)
    for pid, fid in _data_pages(store, table):
        page = store.page(pid, fid)
        for slot in range(page.header.slot_cnt):
            raw = page.record(slot)
            fixed_end = struct.unpack_from("<H", raw, 2)[0]
            ncol_rec = struct.unpack_from("<H", raw, fixed_end)[0]
            assert ncol_rec == ncol
            null_bytes = (ncol_rec + 7) // 8
            null_start = fixed_end + 2
            # Record must be long enough to hold the null bitmap.
            assert len(raw) >= null_start + null_bytes


@pytest.mark.fixture
def test_var_offsets_monotonic(fixture_bak) -> None:
    """Variable-column end offsets are non-decreasing in type-matrix tables."""
    store = PageStore.from_bak(fixture_bak)
    for case in TYPE_CASES:
        if case.auto:
            continue
        table = next(t for t in recover_schema(store).tables if t.name == f"t_{case.name}")
        for pid, fid in _data_pages(store, table):
            page = store.page(pid, fid)
            for slot in range(page.header.slot_cnt):
                raw = page.record(slot)
                fixed_end = struct.unpack_from("<H", raw, 2)[0]
                ncol = struct.unpack_from("<H", raw, fixed_end)[0]
                null_bm = (ncol + 7) // 8
                nvar_off = fixed_end + 2 + null_bm
                nvar = struct.unpack_from("<H", raw, nvar_off)[0]
                if nvar == 0:
                    continue
                var_start = nvar_off + 2
                prev = 0
                for j in range(nvar):
                    end = struct.unpack_from("<H", raw, var_start + j * 2)[0]
                    assert end >= prev, f"{case.name} slot {slot} var {j}"
                    prev = end


@pytest.mark.fixture
def test_single_bit_flip_does_not_silently_pass_verifier(fixture_bak) -> None:
    """Flipping one bit in a known row must change decode output or raise."""
    store = PageStore.from_bak(fixture_bak)
    table = next(t for t in recover_schema(store).tables if t.name == "t_int")
    rec_cols = _record_columns(table)
    for pid, fid in _data_pages(store, table):
        page = store.page(pid, fid)
        if not page.header.slot_cnt:
            continue
        raw = bytearray(page.record(0))
        good = decode_record(bytes(raw), rec_cols)
        # Flip a bit in the fixed region (past status bytes).
        if len(raw) > 10:
            raw[8] ^= 0x01
        try:
            bad = decode_record(bytes(raw), rec_cols)
        except Exception:
            return  # raised — acceptable
        assert bad != good, "single-bit flip produced identical decode"
        return
    pytest.skip("no data rows in t_int")
