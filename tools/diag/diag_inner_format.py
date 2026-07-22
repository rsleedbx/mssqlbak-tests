#!/usr/bin/env python3
"""Diagnostic: compare inner record content for tde_full.bak vs tde_full_compressed.bak.

For tde_full.bak (TDE + enc, no compression):
  - After backup-level decryption the payload should be raw MTF blocks.
  - TDE pages = 8192 bytes each, with 96-byte plaintext header + 8096 encrypted bytes.

For tde_full_compressed.bak (TDE + enc + compression):
  - After backup-level decryption the payload should be MSSQLBAK compressed stream.
  - But is the compressed stream using plain/Huffman XPRESS, or something else?

This script examines both files at the entropy / header level to classify record types.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_inner_format.py
"""
from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _iter_inner_records, _CHUNK0_DESC_OFFSET
from mssqlbak.tde.dek import _find_dek_descriptor, _rsa_decrypt_pkcs1v15, _parse_plaintextkeyblob
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def byte_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    ent = 0.0
    for c in counts:
        if c:
            p = c / n
            ent -= p * math.log2(p)
    return ent


def classify_bytes(data: bytes) -> str:
    ent = byte_entropy(data[:256])
    if ent > 7.5:
        return f"AES-random (entropy={ent:.2f})"
    if data[:2] == b'\xff\xff':
        return f"Huffman-XPRESS (starts with 0xffff, entropy={ent:.2f})"
    if len(data) >= 96:
        hv, pt = data[0], data[1]
        if hv in (1, 2, 9) and pt in (0, 1, 2, 3, 4, 10, 11, 15):
            return f"SQL page header? m_hv={hv} m_type={pt} entropy={ent:.2f}"
    return f"unknown (entropy={ent:.2f}, first4={data[:4].hex()})"


def extract_dek(data: bytes, priv_key, tde_key) -> bytes:
    hdr = parse_enc_header(data)
    rsa_blob_end = _HDR_RSA_OFF + len(hdr.rsa_blob)
    loc = _find_dek_descriptor(
        data, tde_key.cert_thumbprint,
        scan_start=rsa_blob_end, scan_end=rsa_blob_end + 0x800,
    )
    return _parse_plaintextkeyblob(
        _rsa_decrypt_pkcs1v15(priv_key, bytes(data[loc[0] : loc[0] + loc[1]]))
    )


def probe_bak(label: str, bak_path: Path, priv_key, tde_key) -> None:
    print(f"\n{'='*60}")
    print(f" {label}: {bak_path.name}")
    print(f"{'='*60}")

    data = bak_path.read_bytes()
    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    print(f"  backup-level compressed={is_compressed}  flags={hdr.flags:#010x}")

    try:
        dek = extract_dek(data, priv_key, tde_key)
        print(f"  DEK: {dek.hex()}")
    except Exception as ex:
        print(f"  DEK: not found ({ex})")

    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))
    total_payload = sum(len(p) for _, p in records)
    print(f"  Records: {len(records)}  total payload bytes: {total_payload}")

    print(f"\n  First 8 records:")
    for i, (sig, payload) in enumerate(records[:8]):
        sig_lo = sig & 0xFFFF
        sig_hi = (sig >> 16) & 0xFFFF
        cl = classify_bytes(payload)
        print(f"    [{i}] sig={sig:#010x}  sig_lo={sig_lo:#06x}  comp_size={sig_hi:#06x}  payload_len={len(payload)}  {cl}")

    # Look for 8192-byte aligned data blocks (TDE pages)
    aligned_pages = 0
    for _, payload in records:
        aligned_pages += len(payload) // 8192
    print(f"\n  8192-aligned page blocks across all records: {aligned_pages}")

    # Check if the concat of all payloads looks like a MSSQLBAK stream
    all_payload = b"".join(p for _, p in records)
    # MSSQLBAK V1 magic: check first 8 bytes
    print(f"  concat payload[0:16]: {all_payload[:16].hex()}")
    ent_head = byte_entropy(all_payload[:512])
    ent_mid = byte_entropy(all_payload[len(all_payload)//2 : len(all_payload)//2 + 512]) if len(all_payload) > 512 else 0
    print(f"  entropy head={ent_head:.2f}  mid={ent_mid:.2f}")

    # Look for the MSSQLBAK V1 or V2 header magic
    for magic, name in [(b'\x78\xd2\x00\x00', 'MSSQLBAK-V1'), (b'\x78\xd2\x01\x00', 'MSSQLBAK-V2')]:
        idx = all_payload.find(magic)
        if idx >= 0:
            print(f"  Found {name} magic at concat payload offset {idx:#x}")

    # Look for SQL page file-header marker (m_type=15, pageId=0, fileId=1)
    for offset in range(0, min(len(all_payload), 200000), 8192):
        page = all_payload[offset : offset + 8192]
        if len(page) < 96:
            break
        m_hv, m_type = page[0], page[1]
        if m_type == 15:
            pid, fid = struct.unpack_from("<IH", page, 32)
            print(f"  File-header page at concat offset {offset:#x}: m_hv={m_hv} m_type={m_type} page_id={pid} file_id={fid}")


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    tde_key = load_tde_key(PFX, PASSWORD)

    probe_bak("tde_full (TDE+enc, NO compression)",
              FIXTURE_DIR / "tde_full.bak", priv_key, tde_key)

    probe_bak("tde_full_compressed (TDE+enc+COMPRESSION)",
              FIXTURE_DIR / "tde_full_compressed.bak", priv_key, tde_key)


if __name__ == "__main__":
    main()
