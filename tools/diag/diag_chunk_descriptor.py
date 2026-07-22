#!/usr/bin/env python3
"""Diagnostic: dump raw chunk descriptors from tde_full_compressed.bak.

Shows the 28-byte descriptor for each inner record (sig, f1, ff, bsz, nonce)
and validates that AES-CBC decryption produces expected output for a known
working fixture (enc_bak_aes256_compressed.bak) vs the TDE+compressed one.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_chunk_descriptor.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _CHUNK0_DESC_OFFSET, _SFMB_BLOCK_SIZE, _CHUNK_DESC_SIZE, _aes_cbc_decrypt
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"

_SFMB_MAGIC = b"SFMB"


def dump_descriptors(label: str, bak_path: Path, priv_key, max_records: int = 5) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}: {bak_path.name}")
    print(f"{'='*60}")

    data = bak_path.read_bytes()
    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    print(f"  flags={hdr.flags:#010x}  is_compressed={is_compressed}")
    print(f"  AES key: {aes_key.hex()}")

    pos = _CHUNK0_DESC_OFFSET
    n = 0
    while pos + _CHUNK_DESC_SIZE <= len(data) and n < max_records:
        if bytes(data[pos:pos + 4]) == _SFMB_MAGIC:
            print(f"  [SFMB at {pos:#x}]")
            pos += _SFMB_BLOCK_SIZE
            continue

        raw = bytes(data[pos:pos + _CHUNK_DESC_SIZE])
        sig_val = struct.unpack_from("<I", raw, 0)[0]
        f1 = raw[4:12]
        ff = raw[12:20]
        bsz = struct.unpack_from("<I", raw, 20)[0]
        nonce_bytes = raw[24:28]

        if bsz == 0 or bsz % 16 != 0:
            print(f"  record {n}: TERMINATOR at {pos:#x}  bsz={bsz}  sig={sig_val:#010x}")
            break

        ct = bytes(data[pos + _CHUNK_DESC_SIZE:pos + _CHUNK_DESC_SIZE + bsz])
        iv = f1 + ff
        pt = _aes_cbc_decrypt(aes_key, iv, ct)
        comp_size = sig_val >> 16

        print(f"\n  record {n} at offset {pos:#x}:")
        print(f"    sig={sig_val:#010x}  comp_size={comp_size}  bsz={bsz}")
        print(f"    f1={f1.hex()}  ff={ff.hex()}  nonce={nonce_bytes.hex()}")
        print(f"    iv={iv.hex()}")
        if comp_size > 0 and is_compressed:
            payload = pt[:comp_size]
        elif not is_compressed:
            payload = pt if comp_size == 0 else pt[:comp_size]
        else:
            payload = pt
        print(f"    payload[0:32] (after AES-CBC): {payload[:32].hex()}")
        if len(payload) >= 256:
            # Try Kraft check on first 256 bytes as Huffman table
            from mssqlbak.compressed._detect import _kraft_complete
            kc = _kraft_complete(payload, 0)
            print(f"    _kraft_complete(payload, 0) = {kc}")

        n += 1
        pos += _CHUNK_DESC_SIZE + bsz


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())

    enc_bak_pfx = load_private_key_from_pfx(
        (FIXTURE_DIR / "enc_bak_cert.pfx").read_bytes(),
        b"EncBakCert!Fixture2024",
    )

    # Use enc_bak_aes256_compressed.bak as a working reference
    working = FIXTURE_DIR / "enc_bak_aes256_compressed.bak"
    if working.exists():
        dump_descriptors("enc_bak_aes256_compressed (WORKING reference)", working, enc_bak_pfx)

    dump_descriptors("tde_full_compressed (TDE+enc+COMPRESSION)", FIXTURE_DIR / "tde_full_compressed.bak", priv_key)
    dump_descriptors("tde_full (TDE+enc, no compression)", FIXTURE_DIR / "tde_full.bak", priv_key)


if __name__ == "__main__":
    main()
