#!/usr/bin/env python3
"""One-shot diagnostic: confirm byte offsets for log record fields.

Reads dirtycoverage_uncommitted.bak, locates the log tail, walks every
opening sector, decodes records and prints field-by-field annotations to
confirm:
  1. xact_id byte range within BEGIN_XACT / COMMIT_XACT / ABORT_XACT records
  2. page_id and slot_id byte range within LOP_INSERT_ROWS records

Run from the repo root:
    python tools/probe_log_records.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

BAK = Path("tests/fixtures_2022/dirtycoverage_uncommitted.bak")
SECTOR = 512
BLOCK  = 4096

# Known LOP codes (per community reverse-engineering)
LOP_NAMES = {
    0x00: "LOP_NOP",
    0x01: "LOP_BEGIN_XACT",
    0x02: "LOP_COMMIT_XACT",
    0x03: "LOP_ABORT_XACT",
    0x04: "LOP_INSERT_ROWS",
    0x05: "LOP_DELETE_ROWS",
    0x06: "LOP_MODIFY_ROW",
    0x07: "LOP_MODIFY_COLUMNS",
    0x09: "LOP_SET_FREE_SPACE",
    0x0a: "LOP_SET_BITS",
    0x0b: "LOP_TRUNCATE",
    0x0c: "LOP_END_CKPT",
    0x0f: "LOP_XACT_CKPT",
    0x13: "LOP_PREP_XACT",
    0x17: "LOP_BEGIN_CKPT",
    0x1f: "LOP_AUDIT",
    0x22: "LOP_LOCK_HEAP",
    0x27: "LOP_UNDO_INSERT",
}


def hexrow(data: bytes, offset: int, length: int = 16) -> str:
    chunk = data[offset:offset + length]
    h = " ".join(f"{b:02x}" for b in chunk)
    a = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    return f"  {offset:04x}: {h:<47}  {a}"


def find_log_range(data: bytes) -> tuple[int, int]:
    """Return (log_start, log_end) offsets."""
    apad = data.find(b"APAD")
    if apad < 0:
        return 0, 0
    # First BLOCK-aligned position after APAD
    log_start = ((apad + BLOCK) // BLOCK) * BLOCK
    msls = data.rfind(b"MSLS")
    log_end = msls if msls > log_start else len(data)
    return log_start, log_end


def iter_opening_sectors(data: bytes, start: int, end: int):
    """Yield (abs_offset, sector_bytes) for every opening sector (0x50)."""
    pos = start
    while pos + SECTOR <= end:
        status = data[pos]
        if status == 0x50:
            yield pos, data[pos:pos + SECTOR]
        pos += SECTOR


def print_hex_block(label: str, data: bytes, base: int, length: int = 64) -> None:
    print(f"\n  [{label}] base=0x{base:x}")
    for i in range(0, min(length, len(data) - base), 16):
        print(hexrow(data, base + i))


def probe() -> None:
    data = Path(BAK).read_bytes()
    log_start, log_end = find_log_range(data)
    print(f"Log tail range: 0x{log_start:x} – 0x{log_end:x}  "
          f"({(log_end - log_start) // 1024} KB)")

    sectors_seen = 0
    records_seen: dict[int, list[int]] = {}  # lop → [abs offsets]

    for sec_off, sec in iter_opening_sectors(data, log_start, log_end):
        sectors_seen += 1
        # Opening sector header: 0x48 bytes; log records start at +0x48
        rec_off = sec_off + 0x48
        rec_end = sec_off + SECTOR

        while rec_off + 4 < rec_end:
            # Attempt record: length at +0, lop at +0x0f, lcx at +0x0e
            rec_len_raw = struct.unpack_from("<H", data, rec_off)[0]
            if rec_len_raw < 4 or rec_len_raw > 8000:
                break
            lop = data[rec_off + 0x0f]
            records_seen.setdefault(lop, []).append(rec_off)
            rec_off += rec_len_raw
            # 4-byte align
            if rec_off % 4:
                rec_off += 4 - (rec_off % 4)

    print(f"\nSectors (0x50): {sectors_seen}")
    print("\nLOP codes found:")
    for lop, offsets in sorted(records_seen.items()):
        name = LOP_NAMES.get(lop, f"LOP_0x{lop:02x}")
        print(f"  0x{lop:02x}  {name:<25}  count={len(offsets)}, "
              f"first=0x{offsets[0]:x}")

    # ------------------------------------------------------------------
    # Pinpoint BEGIN_XACT record structure
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("BEGIN_XACT (LOP 0x01) — scanning for xact_id field")
    for abs_off in (records_seen.get(0x01) or [])[:3]:
        rel = abs_off - log_start
        rec_len = struct.unpack_from("<H", data, abs_off)[0]
        print(f"\n  BEGIN_XACT at 0x{abs_off:x} (log+0x{rel:x}), len={rec_len}")
        for i in range(0, min(rec_len, 80), 16):
            print(hexrow(data, abs_off + i))
        # xact_id candidates: 6 bytes whose value looks like a counter
        # Try offset +14 (after standard 14-byte log-record preamble)
        for candidate_off in [14, 20, 28, 38, 46]:
            candidate = data[abs_off + candidate_off:abs_off + candidate_off + 6]
            print(f"    +{candidate_off:02d}: {candidate.hex()}  "
                  f"(as uint48_le={int.from_bytes(candidate, 'little')})")

    # ------------------------------------------------------------------
    # Pinpoint COMMIT_XACT record structure
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("COMMIT_XACT (LOP 0x02) — scanning for xact_id field")
    for abs_off in (records_seen.get(0x02) or [])[:3]:
        rel = abs_off - log_start
        rec_len = struct.unpack_from("<H", data, abs_off)[0]
        print(f"\n  COMMIT_XACT at 0x{abs_off:x} (log+0x{rel:x}), len={rec_len}")
        for i in range(0, min(rec_len, 64), 16):
            print(hexrow(data, abs_off + i))
        for candidate_off in [14, 20, 28, 38, 46]:
            candidate = data[abs_off + candidate_off:abs_off + candidate_off + 6]
            print(f"    +{candidate_off:02d}: {candidate.hex()}  "
                  f"(as uint48_le={int.from_bytes(candidate, 'little')})")

    # ------------------------------------------------------------------
    # Pinpoint INSERT_ROWS record structure — page_id and slot_id
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("INSERT_ROWS (LOP 0x04) — scanning for page_id and slot_id")
    insert_offsets = records_seen.get(0x04) or []
    print(f"  Total INSERT records: {len(insert_offsets)}")
    for abs_off in insert_offsets[:5]:
        rel = abs_off - log_start
        rec_len = struct.unpack_from("<H", data, abs_off)[0]
        print(f"\n  INSERT_ROWS at 0x{abs_off:x} (log+0x{rel:x}), len={rec_len}")
        for i in range(0, min(rec_len, 96), 16):
            print(hexrow(data, abs_off + i))
        # page_id candidates — look for values that are plausible page numbers
        # (small int < 100000) at various offsets
        for candidate_off in [16, 20, 24, 28, 32, 36]:
            val4 = struct.unpack_from("<I", data, abs_off + candidate_off)[0]
            val2 = struct.unpack_from("<H", data, abs_off + candidate_off)[0]
            print(f"    +{candidate_off:02d}: uint32={val4:>10}  uint16={val2:>6}")

    # ------------------------------------------------------------------
    # Cross-check: if we can see the same xact_id in BEGIN and INSERT
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Cross-check: look for consistent 6-byte value across BEGIN + INSERT records")
    begin_offs = records_seen.get(0x01) or []
    if begin_offs and insert_offsets:
        # Try each candidate offset for xact_id
        for xid_off in [14, 20, 28, 38, 46]:
            begin_xid = data[begin_offs[0] + xid_off: begin_offs[0] + xid_off + 6]
            # Search for this pattern in INSERT records
            matches = 0
            for ins_off in insert_offsets:
                rec_len = struct.unpack_from("<H", data, ins_off)[0]
                raw = data[ins_off:ins_off + rec_len]
                if begin_xid in raw:
                    matches += 1
            print(f"  BEGIN xact_id candidate @+{xid_off:02d}: {begin_xid.hex()} "
                  f"→ found in {matches}/{len(insert_offsets)} INSERT records")


if __name__ == "__main__":
    if not BAK.exists():
        print(f"fixture not found: {BAK}", file=sys.stderr)
        sys.exit(1)
    probe()
