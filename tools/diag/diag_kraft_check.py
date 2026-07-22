#!/usr/bin/env python3
"""Diagnostic: test _kraft_complete on the synthesized inner MSSQLBAK from decrypt_backup.

Tests whether the XPRESS records in the synthesized inner MSSQLBAK container
produced by _build_inner_mssqlbak pass _kraft_complete, and whether _iter_pages
yields any SQL pages.

Also tests iter_mtf_descriptor_blocks on the synthesized plaintext to see if
the DEK extraction code path would work.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_kraft_check.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import _HDR_RSA_OFF
from mssqlbak.backupenc.keys import load_private_key_from_pfx
from mssqlbak.backupenc.stream import decrypt_backup
from mssqlbak.compressed._detect import _kraft_complete, _is_record_header, _V2, MSSQLBAK_MAGIC
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)

    data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()

    print("=== Step 1: decrypt_backup → synthesized inner MSSQLBAK ===")
    inner = decrypt_backup(data, priv_key)
    print(f"  inner[0:8] = {inner[:8]!r}  (expect b'MSSQLBAK')")
    inner_flags = struct.unpack_from("<I", inner, 12)[0]
    print(f"  inner flags = {inner_flags:#010x}")
    print(f"  inner size = {len(inner)} bytes")

    print("\n=== Step 2: _is_record_header at H=0x1DC ===")
    ok = _is_record_header(inner, 0x1DC, _V2)
    print(f"  _is_record_header(inner, 0x1DC, _V2) = {ok}")
    if not ok:
        # show kraft check
        kc = _kraft_complete(inner, 0x1DC + _V2.huffman_off)
        print(f"  _kraft_complete at H+{_V2.huffman_off} = {kc}")
        # Show zero check
        z_off = 0x1DC + _V2.zero_off
        z_bytes = inner[z_off:z_off + 4]
        print(f"  zero check at H+{_V2.zero_off}: {z_bytes.hex()} (need 00000000)")
        # Show tag check
        t_off = 0x1DC + _V2.tag_off
        tag = struct.unpack_from("<I", inner, t_off)[0]
        print(f"  tag at H+{_V2.tag_off}: {tag:#010x}  >> 16 = {tag >> 16}")
        # Show first bytes of inner at 0x1DC
        print(f"  inner[0x1DC:0x1FC] = {inner[0x1DC:0x1FC].hex()}")
        print(f"  inner[0x1FC:0x21C] = {inner[0x1FC:0x21C].hex()}")

    print("\n=== Step 3: scan for first valid record header ===")
    from mssqlbak.compressed._detect import _next_header, _BOOTSTRAP_SCAN_LIMIT
    h = _next_header(inner, 0, _V2, scan_limit=_BOOTSTRAP_SCAN_LIMIT)
    print(f"  first valid header at: {h}")
    if h is not None:
        t_off = h + _V2.tag_off
        tag = struct.unpack_from("<I", inner, t_off)[0]
        comp = tag >> 16
        print(f"  comp_size = {comp}")
        kc2 = _kraft_complete(inner, h + _V2.huffman_off)
        print(f"  _kraft_complete = {kc2}")

    print("\n=== Step 4: _iter_pages on synthesized inner ===")
    from mssqlbak.compressed.stream import _iter_pages
    pages: list[tuple[int, int, bytes]] = []
    try:
        for fid, pid, page in _iter_pages(inner):
            pages.append((fid, pid, page))
    except Exception as ex:
        print(f"  ERROR in _iter_pages: {ex}")
    print(f"  Pages yielded: {len(pages)}")
    if pages:
        fid, pid, page = pages[0]
        print(f"  First page: file_id={fid} page_id={pid} m_type={page[1]}")

    print("\n=== Step 5: iter_mtf_descriptor_blocks on synthesized inner ===")
    try:
        from mssqlbak.compressed.stream import iter_mtf_descriptor_blocks
        blocks = list(iter_mtf_descriptor_blocks(inner))
        print(f"  MTF descriptor blocks found: {len(blocks)}")
        for bt, bb in blocks[:3]:
            print(f"    type={bt!r} size={len(bb)}")
    except Exception as ex:
        print(f"  ERROR: {ex}")

    print("\n=== Step 6: extract DEK from outer MSSQLBAK header directly ===")
    from mssqlbak.backupenc.descriptor import parse_enc_header
    hdr = parse_enc_header(data)
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    print(f"  rsa_blob_end = {rsa_blob_end:#x}")
    try:
        loc = _find_dek_descriptor(
            data, tde_key.cert_thumbprint,
            scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800,
        )
        dek = _parse_plaintextkeyblob(
            _rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0]:loc[0] + loc[1]]))
        )
        print(f"  DEK: {dek.hex()}")
    except Exception as ex:
        print(f"  ERROR extracting DEK: {ex}")

    print("\n=== Step 7: extract_mdf_files full run ===")
    from mssqlbak.mtf import extract_mdf_files
    try:
        images = extract_mdf_files(
            FIXTURE_DIR / "tde_full_compressed.bak",
            tde_key=tde_key,
        )
        print(f"  extract_mdf_files succeeded: {list(images.keys())}")
        for fid, img in images.items():
            print(f"  file_id={fid}: image size={len(img)} bytes")
    except Exception as ex:
        print(f"  ERROR: {type(ex).__name__}: {ex}")


if __name__ == "__main__":
    main()
