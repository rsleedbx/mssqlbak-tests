#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Probe the large_dirty log tail for the checkpoint record and ATT.

Phase 0 revealed that:
- xdes_id / XDE slots are not persisted in BAK page images (all zero)
- 8 dirty rows have INSERT records that predate the captured log window
- The Active Transaction Table (ATT) in the checkpoint record is the only
  mechanism that could identify those rows as uncommitted

This script scans the log tail for all LCX byte values to find the checkpoint
record, then attempts to locate the ATT containing the uncommitted xact_ids.

Usage:
    .venv/bin/python tools/diag/diag_xde_slots.py [version]

    version  2017 | 2019 | 2022 (default) | 2025
"""
from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import fixture, hexdump

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from mssqlbak.logtail import (
    find_log_range,
    iter_log_sectors,
    _BLOCK_HDR,
    _BLOCK_SIZE,
    iter_log_records,
    _iter_cont_records,
    build_uncommitted_set,
)

# Known LCX values from the spec
_KNOWN_LCX = {
    0x00: "LCX_NULL",
    0x02: "LCX_HEAP/BTREE",
    0x04: "LCX_HEADER (DML)",
    0x0A: "LCX_CHECKPOINT?",
    0x0B: "LCX_XACT_CKPT?",
    0x18: "LCX_CKPT_BEGIN?",
}

# Confirmed operation subtypes for LCX_NULL (0x00)
_LCX0_SUBTYPES = {
    0x80: "LOP_BEGIN_XACT",
    0x81: "LOP_COMMIT_XACT",
    0x82: "LOP_ABORT_XACT",
}

_OFF_LCX     = 0x0E  # byte offset of LCX within a log record (relative to record start)
_OFF_SUBTYPE = 0x0F  # byte offset of SUBTYPE within a log record
_OFF_XACT_ID = 0x10  # 6 bytes
_STEP        = 8     # records are 8-byte aligned


def _scan_all_lcx(data: bytes, start: int, end: int) -> Counter:
    """Raw byte scan for all (LCX, SUBTYPE) combos at every 8-byte-aligned position."""
    ops: Counter = Counter()
    for block in iter_log_sectors(data, start, end):
        blen = len(block)
        for pos in range(_BLOCK_HDR, blen - _OFF_SUBTYPE, _STEP):
            lcx = block[pos + _OFF_LCX]
            sub = block[pos + _OFF_SUBTYPE]
            ops[(lcx, sub)] += 1
    return ops


def _find_candidate_ckpt_blocks(
    data: bytes, start: int, end: int, target_xact_ids: list[bytes]
) -> list[dict]:
    """Find log blocks that contain one of the target xact_ids at a non-DML position.

    Log records for checkpoint / ATT operations carry the system xact_id at
    the same offset (+0x10) as DML records but with a different LCX value.
    This heuristic scans for any 8-byte-aligned position that:
    - has LCX != 0x00 and LCX != 0x04 (i.e., not a recognised DML/TX record)
    - carries one of the known uncommitted xact_ids at offset +0x10
    """
    candidates = []
    for block_idx, block in enumerate(iter_log_sectors(data, start, end)):
        blen = len(block)
        for pos in range(_BLOCK_HDR, blen - 0x16, _STEP):
            lcx = block[pos + _OFF_LCX]
            if lcx in (0x00, 0x04):
                continue
            xid = bytes(block[pos + _OFF_XACT_ID: pos + _OFF_XACT_ID + 6])
            if xid in (bytes(t) for t in target_xact_ids):
                sub = block[pos + _OFF_SUBTYPE]
                candidates.append({
                    "block_idx": block_idx,
                    "pos": pos,
                    "lcx": lcx,
                    "sub": sub,
                    "xid": xid.hex(),
                    "context": bytes(block[pos: pos + 32]),
                })
    return candidates


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "2022"
    bak_path = fixture(version, "dirtycoverage_large_dirty.bak")
    print(f"Fixture: {bak_path}")

    data = bak_path.read_bytes()
    start, end = find_log_range(data)
    print(f"Log tail: {start:#010x}–{end:#010x} ({end - start} bytes)")

    # Build uncommitted set
    recs = list(iter_log_records(data, start, end))
    cont_recs = list(_iter_cont_records(data, start, end))
    all_recs = recs + cont_recs
    uncommitted = build_uncommitted_set(all_recs)
    print(f"Uncommitted xact_ids: {[x.hex() for x in sorted(uncommitted)]}")

    # ── 1. Raw LCX histogram ──────────────────────────────────────────────────
    print("\n=== All (LCX, SUBTYPE) combinations at 8-byte-aligned positions ===")
    ops = _scan_all_lcx(data, start, end)
    for (lcx, sub), cnt in sorted(ops.most_common(40)):
        label = _KNOWN_LCX.get(lcx, "?")
        known_sub = _LCX0_SUBTYPES.get(sub, "") if lcx == 0x00 else ""
        print(f"  LCX=0x{lcx:02x} SUB=0x{sub:02x}  cnt={cnt:<8}  {label} {known_sub}")

    # ── 2. Search for unknown LCX positions that carry known uncommitted xid ──
    print("\n=== Non-DML log positions carrying a known uncommitted xact_id ===")
    candidates = _find_candidate_ckpt_blocks(data, start, end, list(uncommitted))
    print(f"Found {len(candidates)} candidate positions")
    for c in candidates[:20]:
        print(f"  block[{c['block_idx']:4d}] pos={c['pos']:#06x}  "
              f"LCX=0x{c['lcx']:02x} SUB=0x{c['sub']:02x}  xid={c['xid']}")
        hexdump(c["context"], base=c["pos"], indent="    ")

    # ── 3. Look for the word 'CKPT' in the log tail ───────────────────────────
    print("\n=== Searching for 'CKPT' ASCII in log tail ===")
    offset = start
    found_ckpt = []
    while True:
        pos = data.find(b"CKPT", offset, end)
        if pos == -1:
            break
        found_ckpt.append(pos)
        offset = pos + 4
    print(f"Found {len(found_ckpt)} occurrences of 'CKPT'")
    for pos in found_ckpt[:5]:
        hexdump(data[max(0, pos-16): pos+48], base=pos-16, indent="  ")

    # ── 4. Look for known uncommitted xact_ids anywhere in the log ────────────
    print("\n=== Raw search for uncommitted xact_id bytes in log tail ===")
    for xid in sorted(uncommitted):
        count = 0
        off = start
        positions = []
        while True:
            pos = data.find(xid, off, end)
            if pos == -1:
                break
            count += 1
            positions.append(pos)
            off = pos + 1
        print(f"  xact_id {xid.hex()}: {count} occurrences in log tail")
        if positions:
            # Show context of first non-DML occurrence (approximately)
            for p in positions[:2]:
                surrounding = data[max(start, p-32): p+32]
                print(f"    at {p:#010x}:")
                hexdump(surrounding, base=max(start, p-32), indent="      ")


if __name__ == "__main__":
    main()
