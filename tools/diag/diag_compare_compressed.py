#!/usr/bin/env python3
"""Compare enc_bak_aes256_compressed.bak (known-good) with tde_full_compressed.bak.

Specifically look at:
1. Flags, record sig patterns
2. Kraft sums of the first record payloads
3. Whether record 0 XPRESS-decompresses to valid MTF
4. What the bsz values are (actual AES block sizes)
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import (
    _iter_inner_records,
    _CHUNK0_DESC_OFFSET,
    _aes_cbc_decrypt,
    _CHUNK_DESC_SIZE,
    _SFMB_MAGIC,
    _SFMB_BLOCK_SIZE,
    _AES_BLOCK,
)
from mssqlbak.compressed._detect import _kraft_complete
from mssqlbak import xpress as _xp

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"


def hexdump(data: bytes, base: int = 0, limit: int = 64) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def kraft_sum(buf: bytes, off: int = 0, n_bytes: int = 256) -> int:
    remainder = 1 << _xp.MAX_CODEWORD_LEN
    for i in range(n_bytes):
        b = buf[off + i]
        for nib in (b & 0xF, b >> 4):
            if nib:
                remainder -= 1 << (_xp.MAX_CODEWORD_LEN - nib)
    return (1 << _xp.MAX_CODEWORD_LEN) - remainder


def probe_bak(name: str, bak_path: Path, pfx_path: Path, password: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    pfx_bytes = pfx_path.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, password.encode())
    data = bak_path.read_bytes()

    hdr = parse_enc_header(data)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)

    print(f"  flags={hdr.flags:#x}  is_compressed={is_compressed}")

    # Manually inspect the first few descriptors + their raw bsz values
    pos = _CHUNK0_DESC_OFFSET
    print(f"\n  First 5 raw chunk descriptors (pos starts at {pos:#x}):")
    for i in range(5):
        while pos + 4 <= len(data) and bytes(data[pos:pos+4]) == _SFMB_MAGIC:
            print(f"    [{i}] SFMB at {pos:#x}, skipping")
            pos += _SFMB_BLOCK_SIZE
        if pos + _CHUNK_DESC_SIZE > len(data):
            print(f"    [{i}] out of bounds")
            break
        raw = bytes(data[pos : pos + _CHUNK_DESC_SIZE])
        sig_val = struct.unpack_from("<I", raw, 0)[0]
        f1 = raw[4:12]
        ff = raw[12:20]
        bsz = struct.unpack_from("<I", raw, 20)[0]
        comp_size = sig_val >> 16
        sig_lo = sig_val & 0xFFFF
        print(f"    [{i}] @{pos:#x}  sig={sig_val:#010x}  "
              f"comp_size={comp_size:6,}  sig_lo={sig_lo:#06x}  bsz={bsz:6,}")
        if bsz == 0 or bsz % _AES_BLOCK != 0:
            print(f"    [{i}] bsz invalid, stopping")
            break
        # AES-decrypt payload
        iv = f1 + ff
        ct = bytes(data[pos + _CHUNK_DESC_SIZE : pos + _CHUNK_DESC_SIZE + bsz])
        pt = _aes_cbc_decrypt(aes_key, iv, ct)
        payload = pt[:comp_size] if comp_size else pt
        ks = kraft_sum(payload, 0, min(256, len(payload)))
        is_kraft = ks == (1 << _xp.MAX_CODEWORD_LEN)
        print(f"         payload_len={len(payload):6,}  kraft_sum={ks:9,}  "
              f"valid_huffman={is_kraft}")
        # First 8 bytes of payload
        print(f"         payload[:8]: {payload[:8].hex()}")
        # Try decompression
        try:
            import xpress_lz77
            out = xpress_lz77.lz77_huffman_decompress_py(payload, 65536)
            print(f"         decomp→65536: OK  first8: {out[:8].hex()}")
            # Check if it looks like MTF
            is_mtf = out[:4] in (b"TAPE", b"SSET", b"VOLB", b"DIRB", b"FILB")
            print(f"         looks_like_mtf_header: {is_mtf}")
        except Exception as e:
            print(f"         decomp→65536: FAILED {e}")
        pos = pos + _CHUNK_DESC_SIZE + bsz

    # How many total records?
    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"\n  Total inner records: {len(records)}")
    total_payload = sum(len(p) for _, p in records)
    total_bsz_estimate = sum(((len(p) + 15) & ~15) for _, p in records)
    print(f"  Total payload bytes: {total_payload:,}")

    # Check thumbprint in raw MTF (for enc-only case)
    if not is_compressed:
        raw_mtf = b"".join(p for _, p in records)
        print(f"  enc-only: raw MTF {len(raw_mtf):,} bytes")


def main() -> None:
    cases = [
        (
            "enc_bak_aes256_compressed.bak (enc+compressed, no TDE)",
            FIXTURE_DIR / "enc_bak_aes256_compressed.bak",
            FIXTURE_DIR / "enc_bak_cert.pfx",
            "EncBakCert!Fixture2024",
        ),
        (
            "tde_full.bak (enc-only + TDE, no compression)",
            FIXTURE_DIR / "tde_full.bak",
            FIXTURE_DIR / "tde_full_cert.pfx",
            "TdeFullCert!Fixture2024",
        ),
        (
            "tde_full_compressed.bak (enc+compressed + TDE)",
            FIXTURE_DIR / "tde_full_compressed.bak",
            FIXTURE_DIR / "tde_full_cert.pfx",
            "TdeFullCert!Fixture2024",
        ),
    ]

    for name, bak, pfx, pw in cases:
        if not bak.exists():
            print(f"\nSKIP (not found): {bak.name}")
            continue
        probe_bak(name, bak, pfx, pw)


if __name__ == "__main__":
    main()
