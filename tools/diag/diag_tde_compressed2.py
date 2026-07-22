#!/usr/bin/env python3
"""Deep probe: check Kraft sum for record 0, look at synthesized container structure,
and find where the DEK thumbprint actually is in the decompressed MTF stream."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.descriptor import parse_enc_header
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import (
    _iter_inner_records, _CHUNK0_DESC_OFFSET, _FLAG_COMPRESSED,
    decrypt_backup,
)
from mssqlbak.compressed._detect import _kraft_complete, _V2, _is_record_header, _next_header
from mssqlbak import xpress as _xp

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
BAK = FIXTURE_DIR / "tde_full_compressed.bak"
PASSWORD = "TdeFullCert!Fixture2024"


def hexdump(data: bytes, base: int = 0, limit: int = 128) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def kraft_sum(buf: bytes, off: int = 0, n_bytes: int = 256) -> int:
    """Return the Kraft sum (should equal 2**MAX_CODEWORD_LEN for valid table)."""
    remainder = 1 << _xp.MAX_CODEWORD_LEN
    for i in range(n_bytes):
        b = buf[off + i]
        for nib in (b & 0xF, b >> 4):
            if nib:
                remainder -= 1 << (_xp.MAX_CODEWORD_LEN - nib)
    return (1 << _xp.MAX_CODEWORD_LEN) - remainder


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())
    data = BAK.read_bytes()

    print(f"MAX_CODEWORD_LEN = {_xp.MAX_CODEWORD_LEN}")
    expected_kraft = 1 << _xp.MAX_CODEWORD_LEN
    print(f"Expected Kraft sum for valid table = 2^{_xp.MAX_CODEWORD_LEN} = {expected_kraft}")

    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & _FLAG_COMPRESSED)
    records = list(_iter_inner_records(data, aes_key, _CHUNK0_DESC_OFFSET, is_compressed))

    print(f"\nKraft sum for first 5 records:")
    for i, (sig, payload) in enumerate(records[:5]):
        ks = kraft_sum(payload, 0, 256)
        print(f"  [{i}] kraft_sum={ks}  expected={expected_kraft}  ok={ks==expected_kraft}")

    # Decompress all records and concatenate to get the raw MTF stream
    print("\n--- Decompressing all records to reconstruct raw MTF stream ---")
    import xpress_lz77 as xp_lz77
    mtf_chunks: list[bytes] = []
    total_decomp = 0
    for i, (sig, payload) in enumerate(records):
        comp_size = sig >> 16
        try:
            chunk = xp_lz77.lz77_huffman_decompress_py(payload, 65536)
            mtf_chunks.append(chunk)
            total_decomp += len(chunk)
            if i < 5:
                print(f"  [{i}] decomp={len(chunk)} bytes  first8: {chunk[:8].hex()}")
        except Exception as e:
            print(f"  [{i}] FAILED: {e}")

    print(f"\nTotal decompressed MTF: {total_decomp:,} bytes ({len(mtf_chunks)} chunks)")
    raw_mtf = b"".join(mtf_chunks)

    # Check for TAPE/SSET signatures in raw MTF
    print("\n--- MTF block type markers in decompressed stream ---")
    from mssqlbak.compressed import _MTF_BLOCK_TYPES
    for off in range(0, min(len(raw_mtf), 4 * 65536), 4):
        btype = raw_mtf[off:off+4]
        if btype in _MTF_BLOCK_TYPES:
            print(f"  {off:#x}: {btype!r}")

    # Search for TDE thumbprint in the decompressed MTF
    from mssqlbak.tde.keys import load_tde_key
    tde_key = load_tde_key(PFX, PASSWORD)
    thumb = bytes(tde_key.cert_thumbprint)
    print(f"\nThumbprint ({len(thumb)} bytes): {thumb.hex()}")

    idx = raw_mtf.find(thumb)
    if idx >= 0:
        print(f"Thumbprint found in raw MTF at offset {idx:#x}")
        hexdump(raw_mtf[max(0,idx-8):idx+len(thumb)+20], base=max(0,idx-8))
    else:
        print("Thumbprint NOT found in decompressed MTF")
        # Try individual chunks
        for i, chunk in enumerate(mtf_chunks):
            cidx = chunk.find(thumb)
            if cidx >= 0:
                print(f"  Found in chunk {i} at offset {cidx:#x}")
                hexdump(chunk[max(0,cidx-8):cidx+len(thumb)+20])
                break

    # Now try extract_dek on the raw_mtf directly
    print("\n--- extract_dek on raw decompressed MTF ---")
    from mssqlbak.tde.dek import extract_dek
    try:
        dek = extract_dek(raw_mtf, tde_key)
        print(f"  DEK extracted: {dek.hex()}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # Check scan range constants
    from mssqlbak.tde.dek import _DEK_SCAN_START, _DEK_SCAN_END
    print(f"\nDEK scan range: {_DEK_SCAN_START:#x} - {_DEK_SCAN_END:#x}")
    if len(raw_mtf) > _DEK_SCAN_START:
        print(f"raw_mtf length {len(raw_mtf):#x} covers start")
        # Check if thumbprint is in scan range
        if idx >= 0:
            in_range = _DEK_SCAN_START <= idx < _DEK_SCAN_END
            print(f"Thumbprint at {idx:#x} in scan range: {in_range}")
    else:
        print(f"raw_mtf length {len(raw_mtf):#x} is BELOW scan start {_DEK_SCAN_START:#x}!")


if __name__ == "__main__":
    main()
