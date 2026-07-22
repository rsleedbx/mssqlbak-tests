#!/usr/bin/env python3
"""Diagnostic: find where actual chunk descriptors live in tde_full_compressed.bak.

When _iter_inner_records hits a bad bsz at 0x1E0 it jumps to the next SFMB.
This script shows:
  1. Where SFMB blocks live in each fixture
  2. Where the first valid chunk descriptor is
  3. The actual chunk descriptor layout offsets past the DEK blob

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_chunk_location.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"

_SFMB_MAGIC = b"SFMB"
_MSSQLBAK_MAGIC = b"MSSQLBAK"
_CHUNK_DESC_SIZE = 28
_SFMB_BLOCK_SIZE = 0x1000


def find_sfmb_blocks(data: bytes) -> list[int]:
    offsets = []
    pos = 0
    while pos + 4 <= len(data):
        if data[pos:pos + 4] == _SFMB_MAGIC:
            offsets.append(pos)
        pos += _SFMB_BLOCK_SIZE
    return offsets


def find_first_valid_descriptor(data: bytes, start: int, max_search: int = 0x10000) -> int | None:
    """Scan for first 28-byte chunk descriptor with bsz > 0 and bsz % 16 == 0."""
    end = min(start + max_search, len(data) - _CHUNK_DESC_SIZE)
    for pos in range(start, end, 4):
        if data[pos:pos + 4] == _SFMB_MAGIC:
            continue
        bsz_raw = struct.unpack_from("<I", data, pos + 20)[0]
        if bsz_raw > 0 and bsz_raw % 16 == 0 and bsz_raw < 0x100000:
            sig_val = struct.unpack_from("<I", data, pos)[0]
            # basic sanity: comp_size in upper 16 bits should be plausible
            comp = sig_val >> 16
            if 32 <= comp <= 0xFFFF:
                return pos
    return None


def hexdump_region(data: bytes, start: int, length: int = 32) -> None:
    chunk = data[start:start + length]
    for i in range(0, len(chunk), 16):
        row = chunk[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in row)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
        print(f"  {start + i:#06x}: {hex_part:<47}  {asc_part}")


def analyze(name: str) -> None:
    path = FIXTURE_DIR / name
    if not path.exists():
        print(f"{name}: NOT FOUND")
        return

    data = path.read_bytes()
    flags = struct.unpack_from("<I", data, 12)[0]
    print(f"\n{'='*60}")
    print(f"  {name}  flags={flags:#010x}  size={len(data)}")

    sfmbs = find_sfmb_blocks(data)
    print(f"  SFMB blocks at: {[f'{o:#x}' for o in sfmbs[:10]]}")

    first_valid = find_first_valid_descriptor(data, 0x1DC, max_search=0x8000)
    if first_valid is not None:
        sig_val = struct.unpack_from("<I", data, first_valid)[0]
        bsz = struct.unpack_from("<I", data, first_valid + 20)[0]
        print(f"  First valid descriptor at {first_valid:#x}:")
        print(f"    sig={sig_val:#010x}  comp_size={sig_val >> 16}  bsz={bsz}")
        hexdump_region(data, first_valid, 32)
    else:
        print("  No valid descriptor found in first 0x8000 bytes")

    # Also show what's at 0x2000 (first possible SFMB after 0x1E0)
    pos2000 = data[0x2000:0x2010]
    print(f"  At 0x2000: {pos2000.hex()}")
    if data[0x2000:0x2004] == _SFMB_MAGIC:
        print(f"  → SFMB block at 0x2000!")
        # Show descriptor after SFMB
        after_sfmb = 0x2000 + _SFMB_BLOCK_SIZE
        print(f"  After SFMB (0x{after_sfmb:x}):")
        hexdump_region(data, after_sfmb, 32)
        sig_val = struct.unpack_from("<I", data, after_sfmb)[0]
        bsz = struct.unpack_from("<I", data, after_sfmb + 20)[0]
        print(f"    sig={sig_val:#010x}  comp_size={sig_val >> 16}  bsz={bsz}  bsz%16={bsz%16}")


def main() -> None:
    for name in [
        "enc_bak_aes256_compressed.bak",
        "tde_full.bak",
        "tde_full_compressed.bak",
    ]:
        analyze(name)


if __name__ == "__main__":
    main()
