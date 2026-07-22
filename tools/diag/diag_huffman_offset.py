#!/usr/bin/env python3
"""Diagnostic: find the actual XPRESS Huffman table offset in TDE+compressed records.

The standard MSSQLBAK V2 layout expects huffman_off=32 (Huffman table 32 bytes into
the record header). This script checks whether a different offset works, and also
tries standard decompression libraries on the full inner MSSQLBAK.

Also tries the working reference (enc_bak_aes256_compressed) to confirm baseline.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_huffman_offset.py
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

import xpress_lz77
from mssqlbak.backupenc.keys import load_private_key_from_pfx
from mssqlbak.backupenc.stream import decrypt_backup, _iter_inner_records, _CHUNK0_DESC_OFFSET
from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED
from mssqlbak.backupenc.keys import extract_aes_key
from mssqlbak.compressed._detect import _kraft_complete

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"

ENC_BAK_PFX = FIXTURE_DIR / "enc_bak_cert.pfx"
ENC_BAK_PASSWORD = b"EncBakCert!Fixture2024"


def scan_kraft(payload: bytes, max_offset: int = 64) -> list[int]:
    """Find all offsets in [0, max_offset) where _kraft_complete passes."""
    hits = []
    for off in range(0, min(max_offset, len(payload) - 256)):
        if _kraft_complete(payload, off):
            hits.append(off)
    return hits


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())

    print("=== Baseline: enc_bak_aes256_compressed.bak ===")
    enc_data = (FIXTURE_DIR / "enc_bak_aes256_compressed.bak").read_bytes()
    enc_priv = load_private_key_from_pfx(ENC_BAK_PFX.read_bytes(), ENC_BAK_PASSWORD)
    enc_hdr = parse_enc_header(enc_data)
    enc_aes = extract_aes_key(enc_hdr.rsa_blob, enc_priv)
    enc_compressed = bool(enc_hdr.flags & FLAG_COMPRESSED)
    enc_records = list(_iter_inner_records(enc_data, enc_aes, _CHUNK0_DESC_OFFSET, enc_compressed))
    print(f"  Records: {len(enc_records)}")
    for i, (sig, payload) in enumerate(enc_records[:3]):
        hits = scan_kraft(payload, 64)
        print(f"  record {i}: payload={len(payload)}  kraft hits at offsets {hits}")

    print("\n=== tde_full_compressed.bak ===")
    tde_data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()
    tde_hdr = parse_enc_header(tde_data)
    tde_aes = extract_aes_key(tde_hdr.rsa_blob, priv_key)
    tde_compressed = bool(tde_hdr.flags & FLAG_COMPRESSED)
    tde_records = list(_iter_inner_records(tde_data, tde_aes, _CHUNK0_DESC_OFFSET, tde_compressed))
    print(f"  Records: {len(tde_records)}")
    print(f"  Scanning first 5 records for Kraft-complete Huffman table offset:")
    for i, (sig, payload) in enumerate(tde_records[:5]):
        hits = scan_kraft(payload, 64)
        print(f"  record {i}: sig={sig:#010x} payload={len(payload)}  kraft hits at offsets {hits}")

    # Try various decompression methods on record 0's payload
    print("\n=== Trying decompression methods on record 0's payload ===")
    _, payload0 = tde_records[0]
    print(f"  payload[0:16] = {payload0[:16].hex()}")

    # 1. XPRESS Huffman (standard)
    for offset in [0, 4, 8]:
        try:
            decomp = xpress_lz77.lz77_huffman_decompress_py(payload0[offset:], 65536)
            print(f"  lz77_huffman (offset={offset}): OK, {len(decomp)} bytes")
        except Exception as ex:
            print(f"  lz77_huffman (offset={offset}): {type(ex).__name__}: {str(ex)[:60]}")

    # 2. Plain LZ77
    try:
        decomp = xpress_lz77.lz77_plain_decompress_py(payload0)
        print(f"  lz77_plain: OK, {len(decomp)} bytes, first={decomp[:8].hex()}")
    except Exception as ex:
        print(f"  lz77_plain: {type(ex).__name__}: {str(ex)[:60]}")

    # 3. zlib (deflate)
    for wbits in [-15, 15, 31]:
        try:
            decomp = zlib.decompress(payload0, wbits)
            print(f"  zlib(wbits={wbits}): OK, {len(decomp)} bytes")
        except Exception:
            pass

    # 4. Try Rust native XPRESS decompressor
    try:
        decomp = xpress_lz77.xpress_lz77(payload0, 65536)
        print(f"  xpress_lz77.xpress_lz77: OK, {len(decomp)} bytes, first={decomp[:8].hex()}")
    except Exception as ex:
        print(f"  xpress_lz77.xpress_lz77: {type(ex).__name__}: {str(ex)[:60]}")

    # 5. Check if decrypt_backup + _iter_pages on the synthesized inner gives pages
    print("\n=== Try decrypt_backup + _iter_pages (enc path) ===")
    inner = decrypt_backup(tde_data, priv_key)
    inner_flags = struct.unpack_from("<I", inner, 12)[0]
    print(f"  inner flags = {inner_flags:#x}")

    # Scan ALL offsets in inner for Kraft-complete records
    print("\n=== Scanning inner MSSQLBAK for any valid XPRESS record header ===")
    from mssqlbak.compressed._detect import _V2, _is_record_header
    hits_v2 = []
    for h in range(0, min(len(inner), 0x10000), 4):
        if _is_record_header(inner, h, _V2):
            hits_v2.append(h)
            if len(hits_v2) >= 5:
                break
    print(f"  V2 record headers found at: {[f'{h:#x}' for h in hits_v2]}")

    from mssqlbak.compressed._detect import _V1
    hits_v1 = []
    for h in range(0, min(len(inner), 0x10000), 4):
        if _is_record_header(inner, h, _V1):
            hits_v1.append(h)
            if len(hits_v1) >= 5:
                break
    print(f"  V1 record headers found at: {[f'{h:#x}' for h in hits_v1]}")

    # Show the raw bytes of the inner at the expected record position
    print(f"\n  inner[0x1DC:0x1FC] = {inner[0x1DC:0x1FC].hex()}")
    print(f"  inner[0x1FC:0x200] = {inner[0x1FC:0x200].hex()}  (first 4 bytes of payload)")


if __name__ == "__main__":
    main()
