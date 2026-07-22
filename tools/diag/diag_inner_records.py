#!/usr/bin/env python3
"""Try to figure out what the inner records of tde_full_compressed.bak contain.

Known facts:
- DEK = 8894e9c1b0cbb3f08ed7852653adfcad (AES-128 from outer header)
- Records have invalid XPRESS Huffman tables (not standard LZ77+Huffman)
- Record sizes vary (263-24708 bytes), not 8192-aligned

Hypotheses to test:
A) Inner records are TDE-AES-CBC-encrypted XPRESS chunks
   → Try AES-decrypt with DEK + various IVs → check Kraft sum
B) Inner records are TDE-AES-CBC-encrypted raw SQL pages (split)
   → Try concatenating all records, then searching for file-header page signature
C) Records are actually XPRESS but with a different format
   → Check if there's a different record header structure
D) Try treating synthesized container as a TDE backup directly with _collect_pages_by_file_tde
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
    _iter_inner_records, _CHUNK0_DESC_OFFSET, _aes_cbc_decrypt,
)
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key
from mssqlbak.compressed._detect import _kraft_complete

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"

PAGE_SIZE = 8192
_PAGE_TYPE_FILE_HEADER = 15


def hexdump(data: bytes, base: int = 0, limit: int = 64) -> None:
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
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)

    # Get DEK from outer header
    thumb = tde_key.cert_thumbprint
    loc = _find_dek_descriptor(data, thumb, scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800)
    ct_start, ct_len = loc
    dek = _parse_plaintextkeyblob(
        _rsa_decrypt_pkcs1v15(priv_key, bytes(data[ct_start : ct_start + ct_len]))
    )
    print(f"DEK: {dek.hex()} ({len(dek)} bytes)")

    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"Records: {len(records)}, total payload: {sum(len(p) for _, p in records):,} bytes")

    # === Hypothesis A: AES-CBC-decrypt payload with DEK ===
    print("\n=== Hypothesis A: AES-decrypt record 0 payload with DEK ===")
    sig0, p0 = records[0]
    # Try all-zeros IV
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    for iv_desc, iv in [
        ("all-zeros", b"\x00" * 16),
        ("record_idx_0", struct.pack("<I", 0) + b"\x00" * 12),
        ("record_idx_1", struct.pack("<I", 1) + b"\x00" * 12),
    ]:
        padded = p0 + b"\x00" * (16 - len(p0) % 16) if len(p0) % 16 else p0
        c = Cipher(algorithms.AES(dek), modes.CBC(iv), backend=default_backend())
        dec = c.decryptor().update(padded)
        ks = _kraft_complete(dec, 0) if len(dec) >= 256 else False
        print(f"  IV={iv_desc}: first8={dec[:8].hex()}  kraft_ok={ks}")

    # === Hypothesis B: Concatenate all payloads, search for file-header page ===
    print("\n=== Hypothesis B: Concatenate all payloads, search for file-header page ===")
    all_payloads = b"".join(p for _, p in records)
    print(f"  Total concatenated: {len(all_payloads):,} bytes")

    # Search for file-header page signature (m_headerVersion=1, m_type=15, page_id=0, file_id=1)
    found_fhp = False
    for off in range(0, len(all_payloads) - PAGE_SIZE + 1):
        pg = all_payloads[off:off + PAGE_SIZE]
        if pg[0] == 1 and pg[1] == _PAGE_TYPE_FILE_HEADER:
            pid, fid = struct.unpack_from("<IH", pg, 32)
            if pid == 0 and fid == 1:
                print(f"  File-header page found at offset {off:#x}!")
                hexdump(pg[:32])
                found_fhp = True
                break
    if not found_fhp:
        print(f"  No file-header page found in concatenated payloads")
        # Check first few pages for any valid-looking header
        for off in range(0, min(65536, len(all_payloads) - PAGE_SIZE + 1), PAGE_SIZE):
            pg = all_payloads[off:off + PAGE_SIZE]
            m_hv, m_type = pg[0], pg[1]
            pid, fid = struct.unpack_from("<IH", pg, 32)
            if m_hv == 1 and 1 <= m_type <= 20:
                print(f"  Valid-ish page at {off:#x}: m_hv={m_hv} m_type={m_type} pid={pid} fid={fid}")

    # === Hypothesis C: Try treating synthesized as raw TDE MTF ===
    print("\n=== Hypothesis C: synthesized as TDE-encrypted raw MTF? ===")
    from mssqlbak.backupenc.stream import decrypt_backup
    synth = decrypt_backup(data, priv_key)
    print(f"  synthesized: {len(synth):,} bytes  flags={struct.unpack_from('<I', synth, 12)[0]:#x}")

    # Does synthesized have a file-header page?
    print("\n  Scanning synthesized for file-header page (m_type=15, pid=0, fid=1):")
    for off in range(0, min(len(synth) - PAGE_SIZE + 1, 4 * 1024 * 1024), 512):
        pg = synth[off:off + PAGE_SIZE]
        if pg[0] == 1 and pg[1] == 15:
            pid, fid = struct.unpack_from("<IH", pg, 32)
            if pid == 0 and fid == 1:
                print(f"    Found at {off:#x}!")
                break
    else:
        print(f"    None found in first 4 MB of synthesized")

    # === Hypothesis D: Treat synthesized as TDE-page-encrypted backup ===
    # This checks if iter_pages would find any valid pages even with TDE-encrypted inner records
    print("\n=== Hypothesis D: _is_tde_encrypted_mtf on synthesized variants ===")
    from mssqlbak.mtf import _is_tde_encrypted_mtf
    print(f"  _is_tde_encrypted_mtf(synthesized): {_is_tde_encrypted_mtf(synth)}")

    # Try scanning for TDE file-header page in synthesized
    from mssqlbak.tde.dek import find_tde_data_start
    try:
        ds = find_tde_data_start(synth, dek)
        print(f"  find_tde_data_start: {ds:#x}")
    except ValueError as e:
        print(f"  find_tde_data_start: FAILED - {e}")

    # Try _collect_pages_by_file_tde on synthesized
    from mssqlbak.mtf import _collect_pages_by_file_tde
    print("\n  Trying _collect_pages_by_file_tde on synthesized starting at 0x2000:")
    try:
        pbf = _collect_pages_by_file_tde(synth, dek, 0x2000)
        print(f"  pages_by_file: {dict((k, len(v)) for k, v in pbf.items())}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # === Final check: use tde_page_full.bak to understand TDE backup structure ===
    tde_page_bak = FIXTURE_DIR / "tde_page_full.bak"
    if tde_page_bak.exists():
        tde_page_data = tde_page_bak.read_bytes()
        print(f"\n=== tde_page_full.bak structure ===")
        print(f"  size: {len(tde_page_data):,} bytes")
        print(f"  magic: {tde_page_data[:8]!r}")
        print(f"  is_tde_encrypted_mtf: {_is_tde_encrypted_mtf(tde_page_data)}")
        # Where is the DEK in this file?
        tde_page_loc = _find_dek_descriptor(tde_page_data, thumb)
        if tde_page_loc:
            print(f"  DEK at: ct_start={tde_page_loc[0]:#x}")
        else:
            print(f"  DEK not found with default range")


if __name__ == "__main__":
    main()
