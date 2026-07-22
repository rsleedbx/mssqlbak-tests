#!/usr/bin/env python3
"""Dump the raw header region of tde_full_compressed.bak and find the first
SFMB block and real chunk descriptors to understand the actual file layout."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
BAKS = {
    "enc_bak_aes256.bak": (FIXTURE_DIR / "enc_bak_aes256.bak", FIXTURE_DIR / "enc_bak_cert.pfx", "EncBakCert!Fixture2024"),
    "enc_bak_aes256_compressed.bak": (FIXTURE_DIR / "enc_bak_aes256_compressed.bak", FIXTURE_DIR / "enc_bak_cert.pfx", "EncBakCert!Fixture2024"),
    "tde_full.bak": (FIXTURE_DIR / "tde_full.bak", FIXTURE_DIR / "tde_full_cert.pfx", "TdeFullCert!Fixture2024"),
    "tde_full_compressed.bak": (FIXTURE_DIR / "tde_full_compressed.bak", FIXTURE_DIR / "tde_full_cert.pfx", "TdeFullCert!Fixture2024"),
}

_SFMB = b"\xff\xff\xff\xff"
_AES_BLOCK = 16


def hexdump(data: bytes, base: int = 0, limit: int = 128) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def scan_sfmb(data: bytes) -> list[int]:
    """Find all SFMB (0xFFFFFFFF) block offsets."""
    offsets = []
    pos = 0
    while pos + 4 <= len(data):
        if bytes(data[pos:pos+4]) == _SFMB:
            offsets.append(pos)
            pos += 4096  # SFMB is a 4096-byte block
        else:
            pos += 4
    return offsets


def main() -> None:
    for name, (bak, pfx, pw) in BAKS.items():
        if not bak.exists():
            print(f"\nSKIP: {name}")
            continue
        data = bak.read_bytes()
        print(f"\n{'='*60}")
        print(f"  {name}  ({len(data):,} bytes)")

        # Raw bytes 0x00-0x50 (magic, flags, thumbprint start)
        print(f"\n  [0x000-0x040] header:")
        hexdump(data[:0x40], base=0, limit=0x40)

        # Bytes around 0x180-0x210 (near CHUNK0_DESC_OFFSET=0x1E0)
        print(f"\n  [0x180-0x230] near desc offset 0x1e0:")
        hexdump(data[0x180:0x230], base=0x180, limit=0x80)

        # Find first SFMB block
        sfmb_offsets = []
        for i in range(0, min(len(data), 512 * 1024), 4):
            if bytes(data[i:i+4]) == _SFMB:
                sfmb_offsets.append(i)
                if len(sfmb_offsets) >= 3:
                    break

        print(f"\n  First few SFMB block offsets: {[f'{x:#x}' for x in sfmb_offsets[:5]]}")

        if sfmb_offsets:
            first_sfmb = sfmb_offsets[0]
            after_sfmb = first_sfmb + 4096
            print(f"\n  [+28 after first SFMB at {first_sfmb:#x}] = {after_sfmb+28:#x}:")
            hexdump(data[first_sfmb-4:first_sfmb+128], base=first_sfmb-4, limit=132)

            # Parse as chunk descriptor
            pos = after_sfmb
            if pos + 28 <= len(data):
                raw = bytes(data[pos : pos + 28])
                sig_val = struct.unpack_from("<I", raw, 0)[0]
                bsz = struct.unpack_from("<I", raw, 20)[0]
                comp_size = sig_val >> 16
                print(f"\n  First desc after SFMB at {pos:#x}: sig={sig_val:#x}  bsz={bsz}  comp_size={comp_size}  bsz_valid={bsz>0 and bsz%_AES_BLOCK==0}")

        print()


if __name__ == "__main__":
    main()
