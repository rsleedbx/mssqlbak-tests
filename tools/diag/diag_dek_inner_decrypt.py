#!/usr/bin/env python3
"""Diagnostic: try DEK-AES-CBC decrypt on the backup-level-decrypted inner records.

The hypothesis: tde_full_compressed.bak inner records are doubly encrypted:
  1. backup-level AES-256 CBC (outer, using backup cert RSA key) 
  2. TDE DEK AES-128 CBC (inner, using the per-database encryption key)

After outer decryption the payload is still AES-CBC encrypted with the DEK.
We need to DEK-decrypt it (with some IV) to get valid XPRESS data.

We try several candidate IVs:
  - All-zeros
  - f1 + ff from chunk descriptor (same as outer IV)
  - record index counter (0x00...00|index)
  - pack('<IH', page_id, file_id) + zeros  (TDE page IV format)
  - nonce from chunk descriptor

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_dek_inner_decrypt.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

import xpress_lz77
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _iter_inner_records, _CHUNK0_DESC_OFFSET, _aes_cbc_decrypt
from mssqlbak.compressed._detect import _kraft_complete
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def aes_cbc_decrypt(key: bytes, iv: bytes, ct: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = cipher.decryptor()
    return d.update(ct) + d.finalize()


def try_dek_decrypt_and_kraft(payload: bytes, dek: bytes, iv: bytes, label: str) -> bool:
    """Try DEK-AES-CBC decrypt with IV and check Kraft completeness."""
    if len(payload) % 16 != 0:
        padded = payload + b"\x00" * (16 - len(payload) % 16)
    else:
        padded = payload
    try:
        pt = aes_cbc_decrypt(dek, iv, padded[:len(payload) - len(payload) % 16] if len(payload) % 16 else padded)
    except Exception as ex:
        print(f"    {label}: AES error: {ex}")
        return False
    kc = _kraft_complete(pt, 0)
    if kc:
        print(f"    *** {label}: KRAFT COMPLETE! ***")
        print(f"    pt[0:32] = {pt[:32].hex()}")
        return True
    else:
        kraft_sum = sum(2 ** -(nib) for b in pt[:256] for nib in [b & 0xF, b >> 4] if nib)
        print(f"    {label}: kraft_sum={kraft_sum:.3f}")
    return False


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)

    data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()
    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)

    # Get DEK from outer header
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    loc = _find_dek_descriptor(
        data, tde_key.cert_thumbprint,
        scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800,
    )
    dek = _parse_plaintextkeyblob(
        _rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0]:loc[0] + loc[1]]))
    )
    print(f"DEK: {dek.hex()} ({len(dek)} bytes)")

    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"Records: {len(records)}")

    # Also manually read descriptor at 0x2000 to get nonce
    desc_off = 0x2000
    raw = data[desc_off:desc_off + 28]
    sig_val = struct.unpack_from("<I", raw, 0)[0]
    f1_bytes = raw[4:12]
    ff_bytes = raw[12:20]
    nonce_bytes = raw[24:28]
    bsz = struct.unpack_from("<I", raw, 20)[0]
    print(f"\nDescriptor at 0x2000: sig={sig_val:#010x} comp_size={sig_val>>16} bsz={bsz}")
    print(f"  f1={f1_bytes.hex()}  ff={ff_bytes.hex()}  nonce={nonce_bytes.hex()}")

    _, payload0 = records[0]
    print(f"\nPayload length: {len(payload0)} bytes")
    print(f"Payload[0:16]: {payload0[:16].hex()}")

    print("\n=== Testing DEK-AES-128-CBC with various IVs ===")

    ivs = [
        (b"\x00" * 16, "all-zeros"),
        (f1_bytes + ff_bytes, "f1+ff (same as outer IV)"),
        (b"\x00" * 12 + b"\x00\x00\x00\x01", "counter=1"),
        (b"\x00" * 12 + b"\x00\x00\x00\x00", "counter=0"),
        (nonce_bytes + b"\x00" * 12, "nonce+zeros"),
        (nonce_bytes * 4, "nonce×4"),
        # TDE page format: pack('<IH', page_id=0, file_id=1) + zeros
        (struct.pack("<IH", 0, 1) + b"\x00" * 10, "TDE page(0,1)"),
        (struct.pack("<IH", 1, 1) + b"\x00" * 10, "TDE page(1,1)"),
        # f1 only (8 bytes of f1_bytes + 8 zeros)
        (f1_bytes + b"\x00" * 8, "f1+zeros"),
        # ff only
        (b"\x00" * 8 + ff_bytes, "zeros+ff"),
        # Record index counter
        (struct.pack("<Q", 0) + b"\x00" * 8, "record_idx=0"),
        (struct.pack("<Q", 1) + b"\x00" * 8, "record_idx=1"),
    ]

    found = False
    for iv, label in ivs:
        if len(iv) != 16:
            continue
        found |= try_dek_decrypt_and_kraft(payload0, dek, iv, label)

    if not found:
        print("\n  No IV worked for record 0. Trying record 1...")
        _, payload1 = records[1]
        for iv, label in ivs[:4]:
            try_dek_decrypt_and_kraft(payload1, dek, iv, f"rec1/{label}")

    print("\n=== Scan all offsets in payload for XPRESS Huffman table ===")
    for off in range(0, min(len(payload0) - 256, 256)):
        if _kraft_complete(payload0, off):
            print(f"  FOUND Kraft-complete at offset {off}: {payload0[off:off+8].hex()}")
            break
    else:
        print("  No Kraft-complete offset found in [0, 256)")


if __name__ == "__main__":
    main()
