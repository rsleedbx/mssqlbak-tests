#!/usr/bin/env python3
"""Diagnostic: dump raw bytes from the chunk-descriptor region of each fixture.

Compares the 0x1DC–0x260 region for:
  enc_bak_aes256_compressed.bak  (working, flags=0x07)
  tde_full.bak                   (TDE+enc, flags=0x05)
  tde_full_compressed.bak        (TDE+enc+COMPRESSION, flags=0x2F)

to understand how the descriptor layout differs for the TDE+compressed case.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_raw_region.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"

TARGETS = [
    ("enc_bak_aes256_compressed.bak", 0x1DC, 0x260),
    ("tde_full.bak",                   0x1DC, 0x260),
    ("tde_full_compressed.bak",        0x1A0, 0x280),  # wider window, start earlier
]


def hexdump(data: bytes, start_offset: int, width: int = 16) -> None:
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"    {start_offset + i:#06x}: {hex_part:<{width*3-1}}  {asc_part}")


def show_region(name: str, dump_start: int, dump_end: int) -> None:
    path = FIXTURE_DIR / name
    if not path.exists():
        print(f"  {name}: NOT FOUND")
        return

    data = path.read_bytes()
    region = data[dump_start:dump_end]

    print(f"\n{'='*64}")
    print(f"  {name}  (total size {len(data)} bytes)")
    print(f"  Hex dump [{dump_start:#06x} – {dump_end:#06x}]:")
    hexdump(region, dump_start)

    # Parse as chunk descriptors starting at 0x1E0 to show interpretation
    desc_start = 0x1E0
    if desc_start >= dump_start and desc_start + 28 <= dump_end:
        print(f"\n  Interpreting as 28-byte chunk descriptor at {desc_start:#06x}:")
        raw = data[desc_start:desc_start + 28]
        sig_val = struct.unpack_from("<I", raw, 0)[0]
        f1 = raw[4:12].hex()
        ff = raw[12:20].hex()
        bsz = struct.unpack_from("<I", raw, 20)[0]
        nonce = raw[24:28].hex()
        print(f"    sig={sig_val:#010x}  comp_size={sig_val >> 16}  sig_lo={sig_val & 0xFFFF:#06x}")
        print(f"    f1={f1}  ff={ff}  bsz={bsz} (0x{bsz:08x})  nonce={nonce}")
        print(f"    bsz % 16 == {bsz % 16}")


def main() -> None:
    for name, start, end in TARGETS:
        show_region(name, start, end)


if __name__ == "__main__":
    main()
