#!/usr/bin/env python3
"""Probe the decrypted plaintext of tde_full_compressed.bak to find where
XPRESS record headers and the DEK descriptor actually live.

Writes findings to stdout so the agent can read the terminal output file.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO.parent / "mssqlbak-tests"))

from mssqlbak.backupenc.descriptor import parse_enc_header
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import (
    _iter_inner_records,
    _CHUNK0_DESC_OFFSET,
    _FLAG_COMPRESSED,
)
from mssqlbak.compressed._detect import (
    _layout_for,
    _next_header,
    _is_record_header,
    _kraft_complete,
    _V2,
    MSSQLBAK_MAGIC,
)

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
BAK = FIXTURE_DIR / "tde_full_compressed.bak"
PASSWORD = "TdeFullCert!Fixture2024"

CHUNK_DECOMP_SIZE = 65536  # standard XPRESS output size per chunk


def hexdump(data: bytes, base: int = 0, limit: int = 256) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    data = BAK.read_bytes()

    print(f"=== {BAK.name} ===")
    print(f"raw file size: {len(data):,}")
    print(f"flags byte: {struct.unpack_from('<I', data, 12)[0]:#010x}")

    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    print(f"AES key: {aes_key.hex()}")
    print(f"hdr.flags: {hdr.flags:#x}  is_compressed={bool(hdr.flags & _FLAG_COMPRESSED)}")

    is_compressed = bool(hdr.flags & _FLAG_COMPRESSED)
    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"\n{len(records)} inner records:")
    for i, (sig, payload) in enumerate(records[:10]):
        comp_size = sig >> 16
        kraft = _kraft_complete(payload, 0)
        print(
            f"  [{i:2d}] sig={sig:#010x}  comp_size={comp_size:,}"
            f"  payload_len={len(payload):,}  kraft_complete={kraft}"
        )
        if kraft:
            print(f"       payload[:32]: {payload[:32].hex()}")

    # Try decompressing record 0 directly with xpress
    print("\n--- Attempting XPRESS decompression of record 0 ---")
    _, r0 = records[0]
    try:
        import xpress_lz77 as xp
        decomp = xp.lz77_huffman_decompress_py(r0, CHUNK_DECOMP_SIZE)
        print(f"  decompressed: {len(decomp)} bytes")
        hexdump(decomp[:128], limit=128)
    except Exception as e:
        print(f"  FAILED: {e}")

    # Build synthesized plaintext and probe for record headers
    from mssqlbak.backupenc.stream import decrypt_backup
    plaintext = decrypt_backup(data, priv_key)
    print(f"\n=== synthesized plaintext: {len(plaintext):,} bytes ===")
    print(f"  magic: {plaintext[:8]!r}")
    layout = _layout_for(plaintext)
    print(f"  layout: {layout}")

    # Scan without scan_limit (Python fallback) up to full plaintext
    print("\n--- Scanning for record headers (Python fallback, no limit) ---")
    found: list[int] = []
    for h in range(0, min(len(plaintext) - 512, len(plaintext))):
        if _is_record_header(plaintext, h, layout):
            found.append(h)
            if len(found) >= 5:
                break
    if found:
        for h in found:
            print(f"  header at {h:#x}")
            hexdump(plaintext[h : h + 64], base=h, limit=64)
    else:
        print("  NO record headers found in entire plaintext")

    # Show header region 0x1D0-0x220
    print("\n--- Plaintext bytes 0x1D0-0x220 (expected record header region) ---")
    hexdump(plaintext[0x1D0:0x220], base=0x1D0)

    # Show the raw record 0 payload layout
    print("\n--- Raw record 0 payload (first 64 bytes) ---")
    sig0, p0 = records[0]
    hexdump(p0[:64])

    # Check if record payloads are decompressable as XPRESS
    # with different expected output sizes
    print("\n--- Trying various decomp sizes for record 0 ---")
    try:
        import xpress_lz77 as xp
        for sz in [512, 1024, 4096, 8192, 16384, 32768, 65536, 65537, 131072]:
            try:
                out = xp.lz77_huffman_decompress_py(p0, sz)
                print(f"  sz={sz:,}: OK → {len(out)} bytes  first16: {out[:16].hex()}")
            except Exception as ex:
                print(f"  sz={sz:,}: FAILED - {str(ex)[:60]}")
    except ImportError:
        print("  xpress_lz77 not available")


if __name__ == "__main__":
    main()
