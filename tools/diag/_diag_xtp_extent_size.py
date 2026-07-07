#!/usr/bin/env python3
"""Diagnose the v2 XPRESS overlap at the SOH seq-9839 extent boundary.

For v2 MSSQLBAK records, the next-header chain points four bytes before the end
of the Huffman stream.  This script compares the stale `next_h + 2` slice with
the full `comp_size` stream for the chunk containing SOH seq 9839.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak import xpress  # noqa: E402
from mssqlbak.compressed import (  # noqa: E402
    _layout_for,
    _next_header,
    _is_record_header,
    EXTENT_PAGES,
    PAGE_SIZE,
)

BAK = Path("tests/fixtures_realworld/AdventureWorks2016_EXT.bak")
TARGET_CHUNK = 34  # 0-based index within seg#1; but here we count all chunks


def main() -> None:
    buf = BAK.read_bytes()
    layout = _layout_for(buf)
    h = _next_header(buf, 0, layout)
    idx = 0
    # We want the Nth *non-page* chunk in the region; simpler: find the chunk
    # whose decompressed bytes contain the bad record header pattern for seq 9839.
    needle = struct.pack("<III", 179, 0x8000000A, 9839)  # size, flags, seq
    while h is not None and h + layout.huffman_off < len(buf):
        if not _is_record_header(buf, h, layout):
            h = _next_header(buf, h + 1, layout)
            continue
        tag_off = h + layout.tag_off
        comp_size = struct.unpack("<I", buf[tag_off : tag_off + 4])[0] >> 16
        data = h + layout.huffman_off
        next_h = h + layout.next_base + comp_size
        if next_h > len(buf):
            h = _next_header(buf, h + 1, layout)
            continue
        stream_end = data + comp_size
        if stream_end > len(buf):
            h = _next_header(buf, h + 1, layout)
            continue
        stale_chunk = bytes(buf[data : next_h + 2])
        chunk = bytes(buf[data:stream_end])
        comp_end = len(chunk)
        try:
            approx = xpress.decompress_until_input(chunk, 0, comp_end)
        except Exception:  # noqa: BLE001
            approx = b""
        rounded = xpress.decompress_chunk(chunk, 0, comp_end, EXTENT_PAGES * PAGE_SIZE)
        if rounded and needle in rounded:
            rel = rounded.find(needle)
            stale = xpress.decompress_chunk(
                stale_chunk,
                0,
                len(stale_chunk) - 2,
                EXTENT_PAGES * PAGE_SIZE,
            )
            print(f"chunk#{idx}: comp_size={comp_size} stale_len={len(stale_chunk)} "
                  f"full_len={len(chunk)} approx_len={len(approx)} "
                  f"rounded_len={len(rounded) if rounded else 0}")
            print(f"  needle(seq9839 hdr) at rel {rel} in rounded")
            if stale:
                first = next(
                    (i for i in range(min(len(stale), len(rounded))) if stale[i] != rounded[i]),
                    -1,
                )
                print(f"  first divergence stale vs full at byte {first}")
                if first >= 0:
                    print(f"  stale [{first}:{first+48}] = {stale[first:first+48].hex()}")
                    print(f"  full  [{first}:{first+48}] = {rounded[first:first+48].hex()}")
            return
        if _is_record_header(buf, next_h, layout):
            h = next_h
        else:
            h = _next_header(buf, next_h, layout)
        idx += 1
    print("chunk with seq 9839 header not found")


if __name__ == "__main__":
    main()
