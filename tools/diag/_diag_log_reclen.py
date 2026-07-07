#!/usr/bin/env python3
"""Reverse-engineer the log-record LENGTH field so records can be walked exactly
(instead of mssqlbak's 8-byte sliding scan).  Phase 0a foundation.

Strategy: take the first OPEN log block, find candidate record starts via the
generic header signature (non-zero 6-byte xact_id at +0x10, plausible LCX/subtype),
compute inter-record strides, and report which 1/2/4-byte header field equals the
stride.
"""
from __future__ import annotations

import mmap as _mmap
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture, hexdump  # noqa: E402

import mssqlbak.logtail as L  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"


def _looks_like_record(block: bytes, pos: int) -> bool:
    """Generic, LCX-agnostic record-start heuristic: non-zero 6-byte xact_id."""
    if pos + L._MIN_RECORD > len(block):
        return False
    xact = block[pos + L._OFF_XACT_ID : pos + L._OFF_XACT_ID + 6]
    if xact == b"\x00\x00\x00\x00\x00\x00":
        return False
    # LCX is a small context code; subtype a small selector.  Keep permissive.
    return block[pos + L._OFF_LCX] != 0


def main() -> None:
    bak = fixture(VERSION, NAME)
    with open(bak, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            start, end = L.find_log_range(mm)
            # First OPEN block in the window.
            block_start = start
            while block_start < end and mm[block_start] not in L._OPEN_BLOCK_TYPES:
                block_start += L._BLOCK_SIZE
            block = mm[block_start : block_start + L._BLOCK_SIZE]
            print(f"OPEN block at file offset {block_start:,} (type=0x{block[0]:02x})")
            print("block header [0x00:0x48]:")
            hexdump(block[:0x48])

            # Find candidate record starts by sliding; record their positions.
            starts = [
                pos
                for pos in range(L._BLOCK_HDR, L._BLOCK_SIZE - L._MIN_RECORD, L._SCAN_STEP)
                if _looks_like_record(block, pos)
            ]
            print(f"\ncandidate record starts ({len(starts)}): {starts[:24]}")

            # Inter-start strides (only meaningful where starts are dense/sequential).
            print("\n-- per-record header dump + stride to next candidate --")
            for i, pos in enumerate(starts[:12]):
                nxt = starts[i + 1] if i + 1 < len(starts) else None
                stride = (nxt - pos) if nxt is not None else None
                lcx = block[pos + L._OFF_LCX]
                sub = block[pos + L._OFF_SUBTYPE]
                disc = block[pos + L._OFF_TX_TYPE]
                # candidate length fields
                u16_00 = struct.unpack_from("<H", block, pos + 0x00)[0]
                u16_02 = struct.unpack_from("<H", block, pos + 0x02)[0]
                u16_04 = struct.unpack_from("<H", block, pos + 0x04)[0]
                u16_0c = struct.unpack_from("<H", block, pos + 0x0C)[0]
                print(
                    f"pos=0x{pos:04x} stride={stride} "
                    f"lcx=0x{lcx:02x} sub=0x{sub:02x} disc=0x{disc:02x} | "
                    f"u16@0={u16_00} @2={u16_02} @4={u16_04} @0xc={u16_0c}"
                )
        finally:
            mm.close()


if __name__ == "__main__":
    main()
