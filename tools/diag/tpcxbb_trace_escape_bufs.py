#!/usr/bin/env python3
"""Trace the decoded raw buffer for escape-prefix handles in tpcxbb pr_review_content.

Shows what _huff_decode_page_py produces (bytes) for the first few escape
handles (those with leading cl==0), and what _split_v4_record does with them.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (  # type: ignore[attr-defined]
    _bootstrap,
    _collect_blobs,
    _deinterleave_column_lob,
    _COLUMN_LOB_CHUNK,
    _COLUMN_LOB_PREAMBLE,
    _COLUMN_LOB_SEP,
    _unwrap_archive_blob,
)
from mssqlbak.columnstore.decode.dict_xvelocity import (
    _build_huff_table,
    _huff_decode_page_py,
    _split_v4_record,
    _V4_CHAR_OFFSET,
    _V4_EA_OFF_IN_HDR,
    _V4_ENTRY_COUNT_OFF,
    _V4_PAGE_COUNT_OFF,
    _V4_PAGE_GAP_BASE,
    _V4_PAGE_HDR_SZ,
    _V4_RH_OFF,
    _V4_RH_SZ,
    _V4_STB_OFF_IN_HDR,
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


def main() -> None:
    print(f"Loading {FIXTURE.name} ...")
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    tbl = next((t for t in schema.tables if t.name.lower() == TABLE.lower()), None)
    if tbl is None:
        print(f"Table {TABLE!r} not found.")
        sys.exit(1)

    col = next((c for c in tbl.columns if c.name.lower() == COL_NAME.lower()), None)
    if col is None:
        print(f"Column {COL_NAME!r} not found.")
        sys.exit(1)

    rowset_ids = {au.rowset_id for au in tbl.alloc_units}
    seg_col_id = col.colid + 1  # CCI adds a hidden row_id as seg col_id=1

    dict_blob_ids = _read_dict_blob_ids(store, boot, rowset_ids)

    seen_blobs: dict[int, str] = {}
    for (hobt, cid, did), bid in dict_blob_ids.items():
        if cid == seg_col_id and bid not in seen_blobs:
            seen_blobs[bid] = f"hobt={hobt} col_id={cid} dict_id={did}"

    print(f"Found {len(seen_blobs)} dict blob(s) for {COL_NAME!r}")

    for blob_id, info in seen_blobs.items():
        raw_blob = all_blobs.get(blob_id)
        if raw_blob is None:
            print(f"  blob_id={blob_id} not found in all_blobs")
            continue
        print(f"\nTracing blob_id={blob_id} ({info})  size={len(raw_blob)}")
        trace_blob(raw_blob)


def trace_blob(raw_blob: bytes) -> None:
    raw = _unwrap_archive_blob(raw_blob)
    deint = _deinterleave_column_lob(raw)

    if len(deint) < 4 or _U32.unpack_from(deint, 0)[0] != _XVELOCITY_V4_VERSION:
        print(f"  Not a V4 dict (version={_U32.unpack_from(deint,0)[0] if len(deint)>=4 else '?'})")
        return

    n_data_ids = _U32.unpack_from(deint, _V4_ENTRY_COUNT_OFF)[0] + 1
    page_count = _U32.unpack_from(deint, _V4_PAGE_COUNT_OFF)[0]
    print(f"  n_data_ids={n_data_ids} page_count={page_count}")

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

    page_raw_pos = _deint_to_raw(rh_end + page_count * 4 + _V4_PAGE_GAP_BASE)

    escape_samples: list[tuple[int, bytes]] = []  # (k, decoded_buf)
    normal_samples: list[tuple[int, bytes]] = []

    for pid in range(page_count):
        ps = _raw_to_deint(page_raw_pos)
        ks = by_page.get(pid, [])

        if ps + _V4_STB_OFF_IN_HDR + 4 > len(deint):
            page_raw_pos += page_raw_len[pid]
            continue

        stb = _U32.unpack_from(deint, ps + _V4_STB_OFF_IN_HDR)[0]
        if stb == 0:
            page_raw_pos += page_raw_len[pid]
            continue

        ea_off = ps + _V4_EA_OFF_IN_HDR
        if ea_off + 128 > len(deint):
            page_raw_pos += page_raw_len[pid]
            continue

        encode_array = deint[ea_off : ea_off + 128]
        cbuf_raw = _deint_to_raw(ps + _V4_PAGE_HDR_SZ)
        if cbuf_raw > len(raw):
            page_raw_pos += page_raw_len[pid]
            continue

        tab, max_len, _ = _build_huff_table(encode_array)
        if tab is None:
            page_raw_pos += page_raw_len[pid]
            continue

        bos = [rhs[k][0] for k in ks]

        # Use _huff_decode_page_py with my escape fix (current code)
        py_result_tuple = _huff_decode_page_py(raw, cbuf_raw, tab, max_len, bos, stb)
        if py_result_tuple is None:
            page_raw_pos += page_raw_len[pid]
            continue
        py_results, escape_idx_set, _extra, _eors = py_result_tuple

        n_bits_needed = stb
        n_bytes = (n_bits_needed + 7) // 8 + 4
        end_off = min(cbuf_raw + n_bytes, len(raw))
        swapped = bytearray(raw[cbuf_raw:end_off])
        for i in range(0, len(swapped) - 1, 2):
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        swapped.extend(b"\x00\x00\x00\x00")

        for idx, (k, buf_bytes) in enumerate(zip(ks, py_results)):
            is_escape = idx in escape_idx_set

            if is_escape and len(escape_samples) < 5:
                escape_samples.append((k, buf_bytes))
            elif not is_escape and len(normal_samples) < 2:
                normal_samples.append((k, buf_bytes))

        page_raw_pos += page_raw_len[pid]

        if len(escape_samples) >= 5 and len(normal_samples) >= 2:
            break

    print("\n=== ESCAPE-PREFIX HANDLE DECODED BUFFERS ===")
    for k, r in escape_samples:
        off = _V4_CHAR_OFFSET
        decoded0 = r[0] - off if r else None
        print(f"\n  k={k}: len(r)={len(r)} r[0]={r[0] if r else 'empty'} decoded0={decoded0}")
        print(f"  r[:16] hex: {r[:16].hex(' ')}")
        chars16 = [chr(b-off) if 32 <= b-off <= 127 else repr(chr(b-off)) for b in r[:16]]
        print(f"  r[:16] chars: {chars16}")
        # Show what each case in _split_v4_record would give (with escape fix)
        strings = _split_v4_record(r, from_python_fallback=True, is_escape=True)
        print(f"  _split_v4_record(is_escape=True): {[s[:80] for s in strings]!r}")
        print(f"  total string lengths: {[len(s) for s in strings]}")

        # Also show what force-chunked would give (skip case 1)
        if decoded0 is not None and decoded0 >= 0x80:
            pos = 0
            chunks: list[str] = []
            while pos < len(r):
                slen = r[pos] - off
                pos += 1
                if slen <= 0 or pos + slen > len(r):
                    break
                chunks.append("".join(chr(b - off) for b in r[pos : pos + slen]))
                pos += slen
            joined = "".join(chunks)
            print(f"  force-chunked: {len(chunks)} chunks, total len={len(joined)}")
            print(f"  force-chunked result: {joined[:120]!r}...")

        # Also show what non-overhead (flat) would give
        flat = "".join(chr(b - off) for b in r[1:] if 32 <= b - off <= 127)
        print(f"  flat (skip r[0]): len={len(flat)} preview={flat[:80]!r}")

    print("\n=== NORMAL HANDLE DECODED BUFFERS (for comparison) ===")
    for k, r in normal_samples:
        off = _V4_CHAR_OFFSET
        decoded0 = r[0] - off if r else None
        print(f"\n  k={k}: len(r)={len(r)} r[0]={r[0] if r else 'empty'} decoded0={decoded0}")
        print(f"  r[:16] hex: {r[:16].hex(' ')}")
        strings = _split_v4_record(r, from_python_fallback=True)
        print(f"  _split_v4_record result: {[s[:80] for s in strings]!r}")
        print(f"  total string lengths: {[len(s) for s in strings]}")


if __name__ == "__main__":
    main()
