#!/usr/bin/env python3
"""Diagnostic: test plain LZ77 decompression on tde_full_compressed.bak records.

SQL Server uses plain LZ77 (not Huffman) when backing up TDE databases with COMPRESSION.
The sig_lo first byte 0x71 (vs 0x31 for Huffman) likely signals this format.

Run from repo root:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_plain_lz77.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

import xpress_lz77
from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _iter_inner_records, _CHUNK0_DESC_OFFSET
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key
from mssqlbak.tde.page import decrypt_page as _decrypt_page

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"
BAK = FIXTURE_DIR / "tde_full_compressed.bak"
TARGET = "hello".encode("utf-16-le")


def find_bytes(buf: bytes, pattern: bytes, label: str) -> bool:
    idx = buf.find(pattern)
    if idx >= 0:
        print(f"  [FOUND] {label!r} at {idx:#x}")
        return True
    print(f"  [----]  {label!r} not found")
    return False


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)
    data = BAK.read_bytes()

    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    print(f"is_compressed={is_compressed}  rsa_blob_end={rsa_blob_end:#x}")

    loc = _find_dek_descriptor(
        data, tde_key.cert_thumbprint,
        scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800,
    )
    dek = _parse_plaintextkeyblob(
        _rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0] : loc[0] + loc[1]]))
    )
    print(f"DEK: {dek.hex()}")

    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"Total records: {len(records)}\n")

    # ------------------------------------------------------------------
    # Strategy 1: plain LZ77 on each record
    # ------------------------------------------------------------------
    print("=== Strategy 1: lz77_plain_decompress_py per record ===")
    plain_all: list[bytes] = []
    for i, (sig, payload) in enumerate(records):
        try:
            decomp = xpress_lz77.lz77_plain_decompress_py(payload)
            plain_all.append(decomp)
            if TARGET in decomp:
                print(f"  record {i}: sig={sig:#010x} payload={len(payload)}  FOUND 'hello' at {decomp.find(TARGET):#x}")
        except Exception as ex:
            plain_all.append(b"")
            if i < 5:
                print(f"  record {i}: sig={sig:#010x} payload={len(payload)}  ERROR: {str(ex)[:80]}")

    all_plain = b"".join(plain_all)
    print(f"  Total decompressed: {len(all_plain)} bytes")
    find_bytes(all_plain, TARGET, "all plain-LZ77 decompressed")

    # ------------------------------------------------------------------
    # Strategy 2: TDE-decrypt each 8192-byte page from payloads, then search
    # ------------------------------------------------------------------
    print("\n=== Strategy 2: TDE page-decrypt each record payload (8192-byte pages) ===")
    tde_pages: list[bytes] = []
    for i, (sig, payload) in enumerate(records):
        n_pages = len(payload) // 8192
        for j in range(n_pages):
            page = payload[j * 8192 : (j + 1) * 8192]
            try:
                pid, fid = struct.unpack_from("<IH", page, 32)
                plain_page = _decrypt_page(page, dek, pid, fid)
                tde_pages.append(plain_page)
                if TARGET in plain_page:
                    print(f"  record {i} page {j}: FOUND 'hello'  page_id={pid} file_id={fid}")
            except Exception:
                tde_pages.append(page)

    all_tde = b"".join(tde_pages)
    print(f"  Total TDE-decrypted: {len(all_tde)} bytes")
    find_bytes(all_tde, TARGET, "TDE-decrypted payloads")

    # ------------------------------------------------------------------
    # Strategy 3: plain LZ77 then TDE-decrypt 8192-byte pages
    # ------------------------------------------------------------------
    print("\n=== Strategy 3: plain LZ77 -> TDE page-decrypt ===")
    s3_pages: list[bytes] = []
    for i, decomp in enumerate(plain_all):
        if not decomp:
            continue
        n_pages = len(decomp) // 8192
        for j in range(n_pages):
            page = decomp[j * 8192 : (j + 1) * 8192]
            try:
                pid, fid = struct.unpack_from("<IH", page, 32)
                plain_page = _decrypt_page(page, dek, pid, fid)
                s3_pages.append(plain_page)
            except Exception:
                s3_pages.append(page)

    all_s3 = b"".join(s3_pages)
    print(f"  Total: {len(all_s3)} bytes")
    find_bytes(all_s3, TARGET, "plain-LZ77 then TDE-decrypted pages")

    # ------------------------------------------------------------------
    # Strategy 4: show first 32 bytes of each of first 5 record payloads
    # and their plain-LZ77 output (for manual inspection)
    # ------------------------------------------------------------------
    print("\n=== Record payload first bytes (raw and plain-LZ77) ===")
    for i, (sig, payload) in enumerate(records[:6]):
        print(f"  record {i}: sig={sig:#010x} payload_len={len(payload)}")
        print(f"    raw[0:32]:   {payload[:32].hex()}")
        try:
            decomp = xpress_lz77.lz77_plain_decompress_py(payload)
            print(f"    plain[0:32]: {decomp[:32].hex()}  (total {len(decomp)} B)")
        except Exception as ex:
            print(f"    plain: ERROR {str(ex)[:80]}")


if __name__ == "__main__":
    main()
