#!/usr/bin/env python3
"""Brute-force scan the WHOLE .bak (every 8-byte-aligned offset) for DML log-record
signatures, independent of find_log_range / block-type detection.

Tells us how many committed-style DELETE/INSERT records actually exist in the
file and in which byte ranges, to see whether find_log_range under-captures.
"""
from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture  # noqa: E402

import mssqlbak.logtail as L  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"


def main() -> None:
    data = fixture(VERSION, NAME).read_bytes()
    n = len(data)
    ins = 0
    dele = 0
    del_offsets: list[int] = []
    ins_pages: Counter[int] = Counter()
    del_pages: Counter[int] = Counter()
    # DML record signature: byte[+0x0e]=LCX(0x02), byte[+0x0f]=SUBTYPE(0x04),
    # byte[+0x16]=discriminant (0x02 insert / 0x03 delete), page_id!=0.
    for pos in range(0, n - 0x48, 8):
        if data[pos + L._OFF_LCX] != L._LCX_XACT:
            continue
        if data[pos + L._OFF_SUBTYPE] != L._SUB_DML:
            continue
        disc = data[pos + L._OFF_TX_TYPE]
        if disc not in (L._DISCRIM_INSERT, L._DISCRIM_DELETE):
            continue
        page_id = struct.unpack_from("<I", data, pos + L._OFF_PAGE_ID)[0]
        if page_id == 0 or page_id > 0x00FFFFFF:
            continue
        # row_len sanity (INSERT at +0x40, DELETE at +0x40 too)
        rlen = struct.unpack_from("<H", data, pos + L._OFF_INSERT_ROW_LEN)[0]
        if not (0 < rlen <= 8096):
            continue
        if disc == L._DISCRIM_INSERT:
            ins += 1
            ins_pages[page_id] += 1
        else:
            dele += 1
            del_pages[page_id] += 1
            del_offsets.append(pos)

    print(f"file size: {n:,} bytes")
    print(f"INSERT-sig records: {ins}")
    print(f"DELETE-sig records: {dele}")
    print(f"INSERT pages (top): {ins_pages.most_common(10)}")
    print(f"DELETE pages (top): {del_pages.most_common(10)}")
    if del_offsets:
        print(f"DELETE offset range: [{del_offsets[0]:,} .. {del_offsets[-1]:,}]")
        # bucket delete offsets into 64KB bins to see clustering
        bins: Counter[int] = Counter()
        for o in del_offsets:
            bins[o // 65536] += 1
        print(f"DELETE 64KB-bin histogram (bin#: count): {sorted(bins.items())}")
    try:
        import mmap as _mmap
        with open(fixture(VERSION, NAME), "rb") as fh:
            mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
            s, e = L.find_log_range(mm)
            mm.close()
        print(f"\nfind_log_range window: [{s:,} .. {e:,}] ({(e-s)//4096} blocks)")
    except Exception as exc:  # noqa: BLE001
        print(f"find_log_range: {exc}")


if __name__ == "__main__":
    main()
