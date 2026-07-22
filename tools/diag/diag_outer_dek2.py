#!/usr/bin/env python3
"""Verify the DEK at 0x218 in tde_full_compressed.bak outer header.
Try RSA-decryption (byte-reversed) to get a PLAINTEXTKEYBLOB, extract DEK,
then attempt to use it on the inner records."""
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
from mssqlbak.tde.dek import _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob, _find_dek_descriptor
from mssqlbak.tde.keys import load_tde_key
from mssqlbak.tde.page import decrypt_page
from mssqlbak.compressed._detect import _kraft_complete

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


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
    print(f"EncHeader RSA blob ends at: {rsa_blob_end:#x} = {rsa_blob_end}")

    # --- Try _find_dek_descriptor with custom scan range ---
    thumb = tde_key.cert_thumbprint
    result = _find_dek_descriptor(data, thumb, scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800)
    if result is None:
        print("ERROR: DEK not found in outer header with custom range!")
        return

    ct_start, ct_len = result
    print(f"DEK found: ct_start={ct_start:#x} ct_len={ct_len}")

    blob_le = bytes(data[ct_start : ct_start + ct_len])
    print(f"RSA ciphertext (first 16 bytes, LE): {blob_le[:16].hex()}")

    plaintext = _rsa_decrypt_pkcs1v15(priv_key, blob_le)
    if plaintext is None:
        print("ERROR: RSA decryption failed (byte-reversed)!")
        # Try without reversing
        from cryptography.hazmat.primitives.asymmetric import padding as _pad
        plaintext2 = priv_key.decrypt(blob_le, _pad.PKCS1v15())
        print(f"RSA decrypt (NOT reversed): {len(plaintext2)} bytes → {plaintext2[:16].hex()}")
        return

    print(f"RSA-decrypted (byte-reversed): {len(plaintext)} bytes → {plaintext[:16].hex()}")
    print(f"bType={plaintext[0]:#x} bVersion={plaintext[1]:#x}")

    try:
        dek = _parse_plaintextkeyblob(plaintext)
        print(f"DEK extracted: {len(dek)} bytes → {dek.hex()}")
    except ValueError as e:
        print(f"ERROR parsing PLAINTEXTKEYBLOB: {e}")
        return

    # --- Now try using this DEK on the inner records ---
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    print(f"\nInner records: {len(records)}")

    # For each record payload, try TDE-decrypt treating as 8192-byte page blocks
    print("\n--- Trying TDE page-decrypt on record payloads ---")
    valid_pages = 0
    for i, (sig, payload) in enumerate(records[:10]):
        # TDE-encrypted pages are 8192 bytes each
        # What if payload is concatenated TDE-encrypted pages?
        # payload size = comp_size, which varies. Not always a multiple of 8192.
        # But: maybe the payload is a single TDE-encrypted XPRESS chunk (not a SQL page)?
        n_pages = len(payload) // 8192
        if n_pages > 0 and len(payload) % 8192 == 0:
            print(f"  [{i}] payload={len(payload)} bytes = {n_pages} SQL pages")
            # Try TDE-decrypt first page
            pg = payload[:8192]
            m_header_version = pg[0]
            m_type = pg[1]
            page_id, file_id = struct.unpack_from("<IH", pg, 32)
            print(f"       page[0]: m_header_version={m_header_version} m_type={m_type} pid={page_id} fid={file_id}")
        else:
            # payload is NOT a multiple of 8192; not raw SQL pages
            # Try treating it as XPRESS-compressed data that was TDE-encrypted
            # But TDE works on 8192-byte blocks...
            print(f"  [{i}] payload={len(payload)} bytes (not SQL-page-aligned)")
            # Check if the payload looks like XPRESS (check Kraft sum)
            ks_ok = _kraft_complete(payload, 0) if len(payload) >= 256 else False
            print(f"       kraft_ok={ks_ok}")

    # --- Try inner content as if it's a raw TDE-page MSSQLBAK ---
    # For tde_page_full.bak (TDE without backup-level enc), the raw file works.
    # After backup-level decryption of tde_full_compressed.bak, what do we get?
    print("\n--- Synthesized plaintext analysis ---")
    from mssqlbak.backupenc.stream import decrypt_backup
    synthesized = decrypt_backup(data, priv_key)
    print(f"synthesized: {len(synthesized)} bytes, magic: {synthesized[:8]!r}")
    print(f"synthesized flags: {struct.unpack_from('<I', synthesized, 12)[0]:#x}")

    # Try iter_decompressed_chunks on the synthesized container
    from mssqlbak.compressed._detect import iter_decompressed_chunks
    print("\n--- iter_decompressed_chunks on synthesized ---")
    try:
        chunks = list(iter_decompressed_chunks(synthesized))
        print(f"  decompressed {len(chunks)} chunks")
        for i, ch in enumerate(chunks[:3]):
            print(f"  [{i}]: {len(ch)} bytes, first8: {ch[:8].hex()}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # --- Key question: can _find_dek_descriptor find DEK in the synthesized plaintext? ---
    # (The synthesized plaintext should NOT have the DEK since it's from the outer header)
    result2 = _find_dek_descriptor(synthesized, thumb, scan_start=0, scan_end=len(synthesized))
    print(f"\n_find_dek_descriptor in synthesized (full scan): {result2}")

    # --- Try to treat synthesized as TDE backup and iterate pages ---
    from mssqlbak.mtf import _is_tde_encrypted_mtf
    is_tde = _is_tde_encrypted_mtf(synthesized)
    print(f"\n_is_tde_encrypted_mtf(synthesized) = {is_tde}")

    # Try using the DEK we found to decrypt pages from synthesized
    print("\n--- Try decrypt_page on record 0 decompressed output ---")
    if len(records) > 0:
        import xpress_lz77
        sig0, p0 = records[0]
        try:
            decomp = xpress_lz77.lz77_huffman_decompress_py(p0, 65536)
            print(f"  record 0 'decompressed': {len(decomp)} bytes")
            for page_idx in range(8):  # 8 pages per chunk
                off = page_idx * 8192
                pg = decomp[off:off+8192]
                m_hv = pg[0]
                m_t = pg[1]
                pid, fid = struct.unpack_from("<IH", pg, 32)
                print(f"  page[{page_idx}]: m_hv={m_hv} m_type={m_t} pid={pid} fid={fid}")
                if m_hv == 1 and m_t in (15, 13):
                    print(f"    ^^ VALID PAGE HEADER (file/boot)")
        except Exception as e:
            print(f"  decomp failed: {e}")


if __name__ == "__main__":
    main()
