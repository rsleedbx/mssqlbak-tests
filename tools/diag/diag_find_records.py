#!/usr/bin/env python3
"""Trace exactly where _iter_inner_records finds records in tde_full_compressed.bak
by adding offset tracking to a local copy of the iterator."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import (
    _aes_cbc_decrypt,
    _CHUNK_DESC_SIZE,
    _SFMB_MAGIC,
    _SFMB_BLOCK_SIZE,
    _AES_BLOCK,
    _CHUNK0_DESC_OFFSET,
)
from mssqlbak.tde.keys import load_tde_key
from mssqlbak.compressed._detect import _kraft_complete

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def hexdump(data: bytes, base: int = 0, limit: int = 48) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def trace_iter(data: bytes, aes_key: bytes, is_compressed: bool) -> None:
    """Like _iter_inner_records but prints where it goes."""
    pos = _CHUNK0_DESC_OFFSET
    total = len(data)
    record_count = 0
    max_print = 60  # print up to 60 records

    print(f"  Starting at pos={pos:#x}, total={total:#x}")

    while pos + _CHUNK_DESC_SIZE <= total:
        if bytes(data[pos : pos + 4]) == _SFMB_MAGIC:
            print(f"  pos={pos:#x}: SFMB, skip to {pos + _SFMB_BLOCK_SIZE:#x}")
            pos += _SFMB_BLOCK_SIZE
            continue

        raw = bytes(data[pos : pos + _CHUNK_DESC_SIZE])
        sig_val = struct.unpack_from("<I", raw, 0)[0]
        f1 = raw[4:12]
        ff = raw[12:20]
        bsz = struct.unpack_from("<I", raw, 20)[0]
        comp_size = sig_val >> 16

        if bsz == 0 or bsz % _AES_BLOCK != 0:
            align = (pos + _SFMB_BLOCK_SIZE) & ~(_SFMB_BLOCK_SIZE - 1)
            print(f"  pos={pos:#x}: invalid bsz={bsz} (sig={sig_val:#x}), scan for SFMB from {align:#x}")
            found = False
            checked = 0
            while align + 4 <= total:
                if bytes(data[align : align + 4]) == _SFMB_MAGIC:
                    print(f"  → SFMB found at {align:#x}")
                    pos = align
                    found = True
                    break
                align += _SFMB_BLOCK_SIZE
                checked += 1
                if checked > 1000:
                    print(f"  → checked {checked} positions, no SFMB found, giving up")
                    return
            if not found:
                print(f"  → No SFMB found, ending")
                break
            continue

        ct_end = pos + _CHUNK_DESC_SIZE + bsz
        if ct_end > total:
            print(f"  pos={pos:#x}: ct_end={ct_end:#x} > total, ending")
            break

        ct = bytes(data[pos + _CHUNK_DESC_SIZE : ct_end])
        iv = f1 + ff
        pt = _aes_cbc_decrypt(aes_key, iv, ct)

        if is_compressed:
            payload = pt[:comp_size] if comp_size > 0 else pt
        else:
            payload = pt[:comp_size] if comp_size > 0 else pt

        ks_valid = _kraft_complete(payload, 0) if len(payload) >= 256 else False

        if record_count < max_print:
            print(f"  pos={pos:#x}: record {record_count}  sig={sig_val:#010x}  bsz={bsz:6,}  "
                  f"comp={comp_size:6,}  payload={len(payload):6,}  kraft_ok={ks_valid}")
        elif record_count == max_print:
            print(f"  ... (more records) ...")

        record_count += 1
        pos = ct_end

    print(f"  Total records found: {record_count}")


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)
    thumb = tde_key.cert_thumbprint

    # Process tde_full_compressed.bak
    bak = FIXTURE_DIR / "tde_full_compressed.bak"
    data = bak.read_bytes()
    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)

    print(f"=== tde_full_compressed.bak ===")
    print(f"flags={hdr.flags:#x} is_compressed={is_compressed}")

    # Show bytes at 0x1e0 more carefully
    print(f"\nRaw bytes at 0x1e0 (first chunk desc candidate):")
    hexdump(data[0x1e0:0x1e0+28], base=0x1e0, limit=28)

    print(f"\nTracing _iter_inner_records:")
    trace_iter(data, aes_key, is_compressed)

    # Now, the key question: is the thumbprint in the FIRST valid record?
    # After finding first SFMB and skipping, what are the first few record payloads?
    print(f"\nSearching for thumbprint in entire file (unrestricted):")
    idx = 0
    while True:
        idx = data.find(thumb, idx)
        if idx < 0:
            print(f"  Thumbprint not found after position {idx}")
            break
        print(f"  Found thumbprint at offset {idx:#x}:")
        hexdump(data[max(0, idx-8):idx+28], base=max(0, idx-8), limit=36)
        idx += 1

    # Also check: what does the compressed MSSQLBAK container look like BEFORE the SFMB?
    # The bytes at 0x1b0-0x1e0 contain interesting structure
    print(f"\nBytes 0x140-0x260 (extended header region):")
    hexdump(data[0x140:0x260], base=0x140, limit=0x120)


if __name__ == "__main__":
    main()
