"""Dump every LOP_MODIFY_ROW record for the uncommitted xact, with its
row_start / undo_size / redo_size / undo_data, to see whether the old label
('original_N' in UTF-16LE) appears in any record's undo section.

If it does -> the before-image is present but dropped (fixable).
If it doesn't -> the old variable-column data is not in the log (inherent).
"""
from __future__ import annotations

import struct
import sys

from mssqlbak import logtail as L


def main() -> int:
    bak = sys.argv[1]
    with open(bak, "rb") as f:
        data = f.read()
    log_start, log_end = L.find_log_range(data)
    all_recs = list(L.iter_log_records(data, log_start, log_end))
    uncommitted = L.build_uncommitted_set(all_recs)
    print(f"log_region=({log_start},{log_end}) uncommitted={[x.hex() for x in uncommitted]}")

    needle = b"o\x00r\x00i\x00g\x00i\x00n\x00a\x00l\x00"
    OFF = L._OFF_XACT_ID
    hits = 0
    for block_start in range(log_start, log_end, L._BLOCK_SIZE):
        if data[block_start] not in L._OPEN_BLOCK_TYPES:
            continue
        block = data[block_start:block_start + L._BLOCK_SIZE]
        pos = L._BLOCK_HDR
        while pos + 0x4C <= L._BLOCK_SIZE:
            lcx = block[pos + L._OFF_LCX]
            tx = block[pos + L._OFF_TX_TYPE]
            sub = block[pos + L._OFF_SUBTYPE]
            xid = bytes(block[pos + OFF:pos + OFF + 6])
            if lcx == L._LCX_XACT and xid in uncommitted and tx in (L._TX_MODIFY, 0x06):
                row_start = struct.unpack_from("<H", block, pos + 0x38)[0]
                undo_size = struct.unpack_from("<H", block, pos + 0x3a)[0]
                redo_size = struct.unpack_from("<H", block, pos + 0x42)[0]
                page_id = struct.unpack_from("<I", block, pos + L._OFF_PAGE_ID)[0]
                slot = struct.unpack_from("<H", block, pos + L._OFF_SLOT_ID)[0]
                undo = L._read_log_payload(data, block_start, pos + 0x4C, min(undo_size, 80))
                tag = "  <<< has 'original'" if needle in undo else ""
                redo_off = pos + 0x4C + ((undo_size + 3) & ~3)
                redo = L._read_log_payload(data, block_start, redo_off, min(redo_size, 80))
                rtag = "  redo-has-'modified'" if b"m\x00o\x00d\x00i\x00f\x00i\x00e\x00d" in redo else ""
                print(f"pg={page_id} slot={slot} tx={tx:#x} sub={sub:#x} "
                      f"row_start={row_start} undo_sz={undo_size} redo_sz={redo_size}{tag}{rtag}")
                if needle in undo or undo_size > 8:
                    print(f"    undo={undo!r}")
                hits += 1
            pos += L._SCAN_STEP
    print(f"\n{hits} MODIFY/temporal records for uncommitted xact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
