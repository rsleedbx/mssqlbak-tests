#!/usr/bin/env python3
"""Diagnose the 193 escape-prefixed Huffman handles in tpcxbb pr_review_content.

For each handle that produces b"" after decoding, prints:
  - handle index k and page id
  - bit span (end - start)
  - raw hex of the first 8 bytes in swapped-bitstream at bos[k]
  - first symbol (cl, sym) at bos[k]
  - first symbol at bos[k] + max_len  (after 1 skip)
  - first symbol at bos[k] + 2*max_len (after 2 skips)
  - LP-pool bytes at rhs[k][0] (to check Hypothesis C)

Also prints the same fields for 5 known-good handles, for comparison.
"""
from __future__ import annotations

import array
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (  # type: ignore[attr-defined]
    _bootstrap,
    _collect_blobs,
    _deinterleave_column_lob,
    _read_column_segments,
    _COLUMN_LOB_CHUNK,
    _COLUMN_LOB_PREAMBLE,
    _COLUMN_LOB_SEP,
    _unwrap_archive_blob,
)
from mssqlbak.columnstore.decode.dict_xvelocity import (
    _build_huff_table,
    _V4_EA_OFF_IN_HDR,
    _V4_ENTRY_COUNT_OFF,
    _V4_MAX_ENTRIES,
    _V4_PAGE_COUNT_OFF,
    _V4_PAGE_GAP_BASE,
    _V4_PAGE_HDR_SZ,
    _V4_RH_OFF,
    _V4_RH_SZ,
    _V4_STB_OFF_IN_HDR,
    _V4_UNCOMPRESSED_HDR_SZ,
)
from mssqlbak.columnstore.assembly.reader import _read_dict_blob_ids
from mssqlbak.pages import PageStore

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_realworld"
    / "tpcxbb_1gb.bak"
)
TABLE = "product_reviews"
COL_NAME = "pr_review_content"
_XVELOCITY_V4_VERSION = 4
_U32 = struct.Struct("<I")


def _deint_to_raw(off: int) -> int:
    return _COLUMN_LOB_PREAMBLE + off + (off // _COLUMN_LOB_CHUNK) * _COLUMN_LOB_SEP


def _raw_to_deint(roff: int) -> int:
    x = roff - _COLUMN_LOB_PREAMBLE
    return x - (x // (_COLUMN_LOB_CHUNK + _COLUMN_LOB_SEP)) * _COLUMN_LOB_SEP


def _read_sym(swapped: bytearray, bit_pos: int, max_len: int, mask: int) -> tuple[int, int]:
    """Return (cl, sym) for the symbol at bit_pos in the swapped byte array."""
    if bit_pos < 0 or bit_pos + max_len > len(swapped) * 8:
        return (-1, -1)
    byte_i = bit_pos >> 3
    bit_off = bit_pos & 7
    word = (
        (swapped[byte_i] << 24)
        | (swapped[byte_i + 1] << 16)
        | (swapped[byte_i + 2] << 8)
        | swapped[byte_i + 3]
    )
    idx = (word >> (32 - max_len - bit_off)) & mask
    return idx, 0  # return table index; caller applies table[idx]


def _read_table_entry(
    swapped: bytearray, bit_pos: int, max_len: int, mask: int,
    tab: "array.array[int]",
) -> tuple[int, int]:
    """Return (cl, sym) from the Huffman table at bit_pos."""
    if bit_pos < 0:
        return -1, -1
    byte_i = bit_pos >> 3
    bit_off = bit_pos & 7
    if byte_i + 3 >= len(swapped):
        return -1, -1
    word = (
        (swapped[byte_i] << 24)
        | (swapped[byte_i + 1] << 16)
        | (swapped[byte_i + 2] << 8)
        | swapped[byte_i + 3]
    )
    idx = (word >> (32 - max_len - bit_off)) & mask
    entry = tab[idx]
    cl = entry & 0xFF
    sym = entry >> 8
    return cl, sym


def _hexbytes(data: bytes | bytearray, n: int = 8) -> str:
    return data[:n].hex(" ")


def analyze_blob(label: str, raw_blob: bytes) -> None:
    """Full handle-level analysis of one V4 Huffman dictionary blob."""
    raw = _unwrap_archive_blob(raw_blob)
    deint = _deinterleave_column_lob(raw)

    if len(deint) < 4 or _U32.unpack_from(deint, 0)[0] != _XVELOCITY_V4_VERSION:
        print(f"  {label}: not a V4 dict (version={_U32.unpack_from(deint, 0)[0] if len(deint) >= 4 else '?'})")
        return

    n_data_ids = _U32.unpack_from(deint, _V4_ENTRY_COUNT_OFF)[0] + 1
    page_count = _U32.unpack_from(deint, _V4_PAGE_COUNT_OFF)[0]
    if n_data_ids > _V4_MAX_ENTRIES or page_count == 0 or page_count > 64:
        print(f"  {label}: bad header n_data_ids={n_data_ids} page_count={page_count}")
        return

    n_handles = 0
    while n_handles < n_data_ids and _V4_RH_OFF + n_handles * _V4_RH_SZ + 8 <= len(deint):
        if _U32.unpack_from(deint, _V4_RH_OFF + n_handles * _V4_RH_SZ + 4)[0] >= page_count:
            break
        n_handles += 1

    rhs = [struct.unpack_from("<II", deint, _V4_RH_OFF + k * _V4_RH_SZ) for k in range(n_handles)]
    rh_end = _V4_RH_OFF + n_handles * _V4_RH_SZ
    page_raw_len = [_U32.unpack_from(deint, rh_end + i * 4)[0] for i in range(page_count)]

    by_page: dict[int, list[int]] = {}
    for k in range(n_handles):
        by_page.setdefault(rhs[k][1], []).append(k)

    print(
        f"\n{'='*70}\n{label}: n_data_ids={n_data_ids} n_handles={n_handles}"
        f" page_count={page_count} raw={len(raw)} deint={len(deint)}"
    )

    bad_ks: list[tuple[int, int, int]] = []   # (k, page_id, bit_span)
    good_ks: list[tuple[int, int, int]] = []

    page_raw_pos = _deint_to_raw(rh_end + page_count * 4 + _V4_PAGE_GAP_BASE)

    for pid in range(page_count):
        ps = _raw_to_deint(page_raw_pos)
        if ps + _V4_STB_OFF_IN_HDR + 4 > len(deint):
            print(f"  page {pid}: header OOB")
            page_raw_pos += page_raw_len[pid]
            continue

        stb = _U32.unpack_from(deint, ps + _V4_STB_OFF_IN_HDR)[0]
        ks = by_page.get(pid, [])

        if stb == 0:
            print(f"  page {pid}: stb=0 (uncompressed LP pool), {len(ks)} handles — skipping Huffman analysis")
            page_raw_pos += page_raw_len[pid]
            continue

        ea_off = ps + _V4_EA_OFF_IN_HDR
        if ea_off + 128 > len(deint):
            print(f"  page {pid}: encode_array OOB")
            page_raw_pos += page_raw_len[pid]
            continue

        encode_array = deint[ea_off : ea_off + 128]
        cbuf_raw = _deint_to_raw(ps + _V4_PAGE_HDR_SZ)

        tab, max_len, _ = _build_huff_table(encode_array)
        if tab is None:
            print(f"  page {pid}: stb={stb} max_len=? tab=None (empty encode_array)")
            page_raw_pos += page_raw_len[pid]
            continue

        mask = (1 << max_len) - 1

        # Pre-swap bytes for bit-level inspection
        n_bits = stb
        n_bytes = (n_bits + 7) // 8 + 4
        raw_slice = raw[cbuf_raw : cbuf_raw + n_bytes]
        swapped = bytearray(raw_slice)
        for i in range(0, len(swapped) - 1, 2):
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        swapped.extend(b"\x00\x00\x00\x00")

        ends = [rhs[ks[i + 1]][0] if i + 1 < len(ks) else stb for i in range(len(ks))]

        print(f"\n  page {pid}: stb={stb} max_len={max_len} cbuf_raw={cbuf_raw} handles={len(ks)}")

        # Decode each handle to find bad ones
        for k, end in zip(ks, ends):
            start = rhs[k][0]
            bit_span = end - start

            # Simulate _huff_decode_page_py for this handle
            buf = bytearray()
            bit_pos = start
            while bit_pos < end:
                cl, sym = _read_table_entry(swapped, bit_pos, max_len, mask, tab)
                if cl == 0:
                    if not buf:
                        bit_pos += max_len
                        continue
                    break
                buf.append(sym)
                bit_pos += cl

            result = bytes(buf)

            if not result:
                bad_ks.append((k, pid, bit_span))
            else:
                good_ks.append((k, pid, bit_span))

        # Detailed output for bad handles on this page
        bad_on_page = [(k, pid, bs) for k, p, bs in bad_ks if p == pid]
        print(f"  bad handles on this page: {len(bad_on_page)}")

        # LP pool base for Hypothesis C check
        lp_pool_raw_base = _deint_to_raw(ps + _V4_UNCOMPRESSED_HDR_SZ)

        tab_nn = tab  # tab is not None here (guarded above)
        def _sym_at(bit: int) -> str:
            if bit >= stb:
                return "PAST_END"
            cl, sym = _read_table_entry(swapped, bit, max_len, mask, tab_nn)
            if cl == 0:
                return f"UNUSED(idx={bit})"
            return f"cl={cl} sym={sym}(chr={chr(sym-2)!r} if printable)"

        def _lp_bytes(k_idx: int) -> str:
            bo = rhs[k_idx][0]
            raw_pos = lp_pool_raw_base + bo
            if raw_pos >= len(raw):
                return f"OOB(raw_pos={raw_pos} > raw_len={len(raw)})"
            ln = raw[raw_pos]
            end_pos = raw_pos + 1 + ln
            if end_pos > len(raw):
                return f"len={ln} OOB"
            content = raw[raw_pos + 1 : end_pos]
            try:
                text = content.decode("latin-1")
                return f"len={ln} text={text[:60]!r}"
            except Exception:
                return f"len={ln} hex={content[:20].hex()}"

        # Print details for first 20 bad and last 5 bad handles
        sample_bad = bad_on_page[:10] + (bad_on_page[-5:] if len(bad_on_page) > 10 else [])
        for k, pid2, bit_span in sample_bad:
            start = rhs[k][0]
            print(
                f"\n    [BAD k={k} pid={pid2}]"
                f" start={start} end={start+bit_span} span={bit_span}"
            )
            # Raw hex at start (swapped)
            byte_i = start >> 3
            hex_preview = _hexbytes(swapped[byte_i : byte_i + 8])
            print(f"      swapped_hex@byte{byte_i}: {hex_preview}")
            print(f"      sym@+0:   {_sym_at(start)}")
            print(f"      sym@+{max_len}:  {_sym_at(start + max_len)}")
            print(f"      sym@+{2*max_len}: {_sym_at(start + 2*max_len)}")
            print(f"      LP@rhs[k][0]={rhs[k][0]}: {_lp_bytes(k)}")

        # Print details for first 5 good handles
        good_on_page = [(k, p, bs) for k, p, bs in good_ks if p == pid][:5]
        print(f"\n  --- 5 good handles on page {pid} (for comparison) ---")
        for k, pid2, bit_span in good_on_page:
            start = rhs[k][0]
            print(
                f"\n    [GOOD k={k} pid={pid2}]"
                f" start={start} end={start+bit_span} span={bit_span}"
            )
            byte_i = start >> 3
            hex_preview = _hexbytes(swapped[byte_i : byte_i + 8])
            print(f"      swapped_hex@byte{byte_i}: {hex_preview}")
            print(f"      sym@+0:   {_sym_at(start)}")
            print(f"      sym@+{max_len}:  {_sym_at(start + max_len)}")

        page_raw_pos += page_raw_len[pid]

    print(f"\n{'='*70}")
    print(f"SUMMARY: {label}: bad={len(bad_ks)} good={len(good_ks)} of {n_handles} handles")
    if bad_ks:
        spans = [bs for _, _, bs in bad_ks]
        print(f"  bad spans: min={min(spans)} max={max(spans)} median={sorted(spans)[len(spans)//2]}")
        unique_pages = {p for _, p, _ in bad_ks}
        print(f"  bad handles on pages: {sorted(unique_pages)}")


def main() -> None:
    print(f"Loading {FIXTURE.name} ...")
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    # Find product_reviews table
    tbl = next((t for t in schema.tables if t.name.lower() == TABLE.lower()), None)
    if tbl is None:
        print(f"Table {TABLE!r} not found. Available: {[t.name for t in schema.tables]}")
        sys.exit(1)

    # Find pr_review_content column_id
    col = next((c for c in tbl.columns if c.name.lower() == COL_NAME.lower()), None)
    if col is None:
        print(f"Column {COL_NAME!r} not found in {TABLE}. Available: {[c.name for c in tbl.columns]}")
        sys.exit(1)
    print(f"Found {TABLE}.{COL_NAME}: colid={col.colid} type_id={col.type_id}")

    rowset_ids = {au.rowset_id for au in tbl.alloc_units}
    segs = _read_column_segments(store, boot, rowset_ids)

    # CCI adds a hidden row_id as segment col_id=1, shifting all schema columns by +1.
    seg_col_id = col.colid + 1
    col_segs = [s for s in segs if s.col_id == seg_col_id]
    print(f"  {len(col_segs)} segment(s) for seg_col_id={seg_col_id}")
    for s in col_segs:
        print(f"    hobt={s.hobt_id} seg_id={s.seg_id} enc={s.enc_type} blob={s.blob_id} prim={s.prim_dict} sec={s.sec_dict} n_rows={s.n_rows}")

    dict_bids = _read_dict_blob_ids(store, boot, rowset_ids)

    # Find all dict blob IDs for this column
    seen_blobs: dict[int, str] = {}
    for (hobt, cid, dict_id), bid in dict_bids.items():
        if cid == seg_col_id and bid not in seen_blobs:
            seen_blobs[bid] = f"hobt={hobt} col_id={cid} dict_id={dict_id}"

    print(f"  {len(seen_blobs)} distinct dict blob(s):")
    for bid, info in seen_blobs.items():
        raw_b = all_blobs.get(bid, b"")
        print(f"    blob_id={bid} size={len(raw_b)} ({info})")

    for bid, info in seen_blobs.items():
        raw_b = all_blobs.get(bid, b"")
        if raw_b:
            analyze_blob(f"blob_{bid}", raw_b)


if __name__ == "__main__":
    main()
