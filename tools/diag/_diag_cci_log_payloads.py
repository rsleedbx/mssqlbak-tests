#!/usr/bin/env python3
"""Dump INSERT/DELETE log-record payloads (by target page) for dirty_cci, to tell
bitmap-B-tree inserts (tiny 2-int CD records) apart from data-row inserts.

Scans OPEN log blocks across the full APAD..MSLS span with a relaxed filter and
also tallies the LCX context byte distribution, to catch records the production
scanner (LCX=0x02 only) skips.
"""
from __future__ import annotations

import mmap as _mmap
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture  # noqa: E402

import mssqlbak.logtail as L  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"


def main() -> None:
    bak = fixture(VERSION, NAME)
    with open(bak, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            msls = mm.rfind(L._MSLS)
            first_apad = mm.find(L._APAD)
            start = (first_apad + L._BLOCK_SIZE) & ~(L._BLOCK_SIZE - 1)

            ins_by_page: dict[int, list[tuple[int, int, bytes]]] = defaultdict(list)
            del_by_page: dict[int, list[tuple[int, int, bytes]]] = defaultdict(list)
            lcx_at_insert: Counter[int] = Counter()

            for block_start in range(start, msls, L._BLOCK_SIZE):
                btype = mm[block_start]
                if btype not in L._OPEN_BLOCK_TYPES:
                    continue
                block = mm[block_start : block_start + L._BLOCK_SIZE]
                pos = L._BLOCK_HDR
                while pos + L._MIN_RECORD <= L._BLOCK_SIZE:
                    tx_type = block[pos + L._OFF_TX_TYPE]
                    lcx = block[pos + L._OFF_LCX]
                    sub = block[pos + L._OFF_SUBTYPE]
                    is_dml = sub == L._SUB_DML
                    if is_dml and tx_type in (L._DISCRIM_INSERT, L._DISCRIM_DELETE):
                        page_id = struct.unpack_from("<I", block, pos + L._OFF_PAGE_ID)[0]
                        slot_id = struct.unpack_from("<H", block, pos + L._OFF_SLOT_ID)[0]
                        if page_id != 0:
                            lcx_at_insert[lcx] += 1
                            if tx_type == L._DISCRIM_INSERT and pos + L._OFF_INSERT_ROW_LEN + 2 <= L._BLOCK_SIZE:
                                rlen = struct.unpack_from("<H", block, pos + L._OFF_INSERT_ROW_LEN)[0]
                                payload = L._read_log_payload(mm, block_start, pos + L._OFF_INSERT_ROW_DATA, min(rlen, 48))
                                ins_by_page[page_id].append((slot_id, rlen, payload))
                            elif tx_type == L._DISCRIM_DELETE and pos + L._OFF_DELETE_ROW_LEN + 2 <= L._BLOCK_SIZE:
                                rlen = struct.unpack_from("<H", block, pos + L._OFF_DELETE_ROW_LEN)[0]
                                payload = L._read_log_payload(mm, block_start, pos + L._OFF_DELETE_ROW_DATA, min(rlen, 48))
                                del_by_page[page_id].append((slot_id, rlen, payload))
                    pos += L._SCAN_STEP

            print(f"== LCX byte distribution at INSERT/DELETE records: {dict(lcx_at_insert)}")
            print("\n== INSERT records by page (page: count, sample row_len, sample payload) ==")
            for pg in sorted(ins_by_page):
                recs = ins_by_page[pg]
                lens = Counter(r[1] for r in recs)
                s = recs[0]
                print(f"  page {pg}: {len(recs)} recs  row_lens={dict(lens)}")
                print(f"      slot={s[0]} row_len={s[1]} payload={s[2].hex()}")
            print("\n== DELETE records by page ==")
            for pg in sorted(del_by_page):
                recs = del_by_page[pg]
                lens = Counter(r[1] for r in recs)
                s = recs[0]
                print(f"  page {pg}: {len(recs)} recs  row_lens={dict(lens)}")
                print(f"      slot={s[0]} row_len={s[1]} payload={s[2].hex()}")
        finally:
            mm.close()


if __name__ == "__main__":
    main()
