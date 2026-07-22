#!/usr/bin/env python3
"""Analyze record types in tde_full_compressed.bak.
Focus on the sig_lo field difference: 0x?071 vs 0x?871 records.
Check if 0x?871 records have valid XPRESS Huffman tables and MTF content."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _iter_inner_records, _CHUNK0_DESC_OFFSET
from mssqlbak.compressed._detect import _kraft_complete
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def hexdump(data: bytes, base: int = 0, limit: int = 48) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)
    data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()

    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)

    # Get DEK
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    loc = _find_dek_descriptor(data, tde_key.cert_thumbprint, scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800)
    dek = _parse_plaintextkeyblob(_rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0]:loc[0]+loc[1]])))
    print(f"DEK: {dek.hex()}")

    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))

    import xpress_lz77

    print(f"\n=== All 53 records: sig_lo, kraft, decomp analysis ===")
    mtf_tags = {b"TAPE", b"SSET", b"VOLB", b"DIRB", b"FILB", b"CFIL", b"ESPB", b"ESET", b"EOTM", b"SFMB"}

    for i, (sig, payload) in enumerate(records):
        sig_lo = sig & 0xFFFF
        comp_size = sig >> 16
        kraft = _kraft_complete(payload, 0) if len(payload) >= 256 else False

        # Try XPRESS decompress
        try:
            decomp = xpress_lz77.lz77_huffman_decompress_py(payload, 65536)
            first8 = decomp[:8].hex()
            is_mtf = bytes(decomp[:4]) in mtf_tags
        except Exception:
            first8 = "ERROR"
            is_mtf = False

        # For 0x?871 records, try with different expected sizes
        is_871 = (sig_lo & 0xFF) == 0x71 and ((sig_lo >> 8) & 0xF0) == 0x80
        is_071 = (sig_lo & 0xFF) == 0x71 and ((sig_lo >> 8) & 0xF0) != 0x80

        print(f"  [{i:2d}] sig_lo={sig_lo:#06x}  comp={comp_size:6,}  "
              f"kraft={kraft}  first8={first8}  mtf={is_mtf}")

        if kraft:
            print(f"        ^^ VALID XPRESS: trying decomp")
            try:
                d = xpress_lz77.lz77_huffman_decompress_py(payload, 65536)
                print(f"        decomp={len(d)} bytes, first8={d[:8].hex()}")
                print(f"        MTF block type: {d[:4]!r}  (in mtf_tags: {bytes(d[:4]) in mtf_tags})")
                hexdump(d[:32], limit=32)
            except Exception as e:
                print(f"        FAILED: {e}")

    # Show distribution of sig_lo values
    from collections import Counter
    sig_los = Counter(sig & 0xFFFF for sig, _ in records)
    print(f"\n=== sig_lo distribution ===")
    for sl, count in sorted(sig_los.items()):
        print(f"  {sl:#06x}: {count}")

    # Focus on records with valid XPRESS (kraft=True)
    valid_kraft = [(i, sig, p) for i, (sig, p) in enumerate(records) if _kraft_complete(p, 0)]
    print(f"\n=== Records with valid Kraft sum: {len(valid_kraft)} ===")
    for i, sig, p in valid_kraft[:10]:
        comp_size = sig >> 16
        sig_lo = sig & 0xFFFF
        decomp = xpress_lz77.lz77_huffman_decompress_py(p, 65536)
        print(f"  [{i:2d}] sig_lo={sig_lo:#06x} comp={comp_size} first_decomp8={decomp[:8].hex()}")
        hexdump(decomp[:64], limit=64)


if __name__ == "__main__":
    main()
