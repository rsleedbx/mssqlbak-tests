#!/usr/bin/env python3
"""Search for the 'hello' string in all possible decodings of tde_full_compressed.bak.

Try:
1. Raw file bytes
2. After backup-level decryption (before XPRESS)
3. In each record payload directly
4. In each record payload TDE-decrypted
5. In each record payload after trying 'plain XPRESS' decompression variants
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import (
    _iter_inner_records, _CHUNK0_DESC_OFFSET, _aes_cbc_decrypt
)
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"

TARGET = b"hello"


def find_all(data: bytes, target: bytes, label: str) -> None:
    idx = 0
    found = []
    while True:
        pos = data.find(target, idx)
        if pos < 0:
            break
        found.append(pos)
        idx = pos + 1
    if found:
        print(f"  [{label}] FOUND at {[f'{p:#x}' for p in found[:5]]}")
    else:
        print(f"  [{label}] not found")


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)
    data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()

    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)

    # Get DEK
    loc = _find_dek_descriptor(data, tde_key.cert_thumbprint, scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800)
    dek = _parse_plaintextkeyblob(_rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0]:loc[0]+loc[1]])))
    print(f"DEK: {dek.hex()}")

    print(f"\n=== Searching for {TARGET!r} ===")
    find_all(data, TARGET, "raw file")

    from mssqlbak.backupenc.stream import decrypt_backup
    synth = decrypt_backup(data, priv_key)
    find_all(synth, TARGET, "after backup-level decrypt (synthesized)")

    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    all_payloads = b"".join(p for _, p in records)
    find_all(all_payloads, TARGET, "concatenated record payloads")

    # TDE-decrypt each payload (trying page-by-page if 8192-aligned)
    import xpress_lz77
    print(f"\n=== Trying XPRESS decompress of each record, search for 'hello' ===")
    for i, (sig, payload) in enumerate(records):
        try:
            decomp = xpress_lz77.lz77_huffman_decompress_py(payload, 65536)
            if TARGET in decomp:
                print(f"  record {i}: 'hello' in decomp! at {decomp.find(TARGET):#x}")
        except Exception:
            pass

    # Search for UTF-16LE version of "hello"
    hello_utf16 = "hello".encode("utf-16-le")
    print(f"\nSearching for UTF-16LE 'hello' ({hello_utf16.hex()}):")
    find_all(data, hello_utf16, "raw file")
    find_all(all_payloads, hello_utf16, "concatenated payloads")
    for i, (sig, payload) in enumerate(records):
        try:
            decomp = xpress_lz77.lz77_huffman_decompress_py(payload, 65536)
            if hello_utf16 in decomp:
                print(f"  record {i}: UTF-16 'hello' in decomp! at {decomp.find(hello_utf16):#x}")
        except Exception:
            pass

    # Now check tde_full.bak (works) to see where "hello" is
    tde_full = FIXTURE_DIR / "tde_full.bak"
    if tde_full.exists():
        tde_full_data = tde_full.read_bytes()
        tde_full_synth = decrypt_backup(tde_full_data, priv_key)
        print(f"\n=== tde_full.bak: searching for 'hello' ===")
        find_all(tde_full_data, TARGET, "raw file")
        find_all(tde_full_synth, TARGET, "after backup-level decrypt")
        find_all(tde_full_synth, hello_utf16, "UTF-16LE after decrypt")

        # Get DEK for tde_full.bak
        tde_full_hdr = parse_enc_header(tde_full_data)
        tde_full_aes = extract_aes_key(tde_full_hdr.rsa_blob, priv_key)
        tde_full_is_comp = bool(tde_full_hdr.flags & FLAG_COMPRESSED)
        tde_full_records = list(_iter_inner_records(tde_full_data, tde_full_aes, _CHUNK0_DESC_OFFSET, tde_full_is_comp))
        tde_full_payloads = b"".join(p for _, p in tde_full_records)
        find_all(tde_full_payloads, TARGET, "raw MTF payloads")
        find_all(tde_full_payloads, hello_utf16, "raw MTF payloads UTF-16LE")

        # Where is it in the raw MTF? And what does that page look like?
        idx = tde_full_payloads.find(hello_utf16)
        if idx >= 0:
            page_start = (idx // 8192) * 8192
            page = tde_full_payloads[page_start:page_start + 8192]
            print(f"\n  Found UTF-16 'hello' in raw MTF at offset {idx:#x}")
            print(f"  In page starting at {page_start:#x}")
            print(f"  Page header: m_hv={page[0]} m_type={page[1]}")
            pid, fid = struct.unpack_from("<IH", page, 32)
            print(f"  page_id={pid} file_id={fid}")

    print("\n=== Checking tde_page_full.bak for reference ===")
    tde_page_bak = FIXTURE_DIR / "tde_page_full.bak"
    # tde_page_full.bak uses a different cert, so "hello" in it with a different TDE key
    tde_page_data = tde_page_bak.read_bytes()
    find_all(tde_page_data, TARGET, "raw tde_page_full")
    find_all(tde_page_data, hello_utf16, "raw tde_page_full UTF-16LE")


if __name__ == "__main__":
    main()
