#!/usr/bin/env python3
"""Diagnostic: verify whether the backup-level AES key for tde_full_compressed.bak is correct.

Tests:
1. Does lz77_huffman_decompress_py always succeed (even on random data)?
2. Compare decrypt_backup output for tde_full.bak vs tde_full_compressed.bak.
3. Verify AES key correctness by checking the PLAINTEXTKEYBLOB signature.
4. Check what happens with the raw chunk at 0x2000 when we decrypt it with
   the AES key, then manually try Huffman-decompression.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_aes_key_verify.py
"""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

import xpress_lz77
from mssqlbak.backupenc.descriptor import parse_enc_header, FLAG_COMPRESSED, _HDR_RSA_OFF, _HDR_RSALEN_OFF
from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx
from mssqlbak.backupenc.stream import _iter_inner_records, _CHUNK0_DESC_OFFSET, _aes_cbc_decrypt
from mssqlbak.compressed._detect import _kraft_complete

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def main() -> None:
    pfx_bytes = PFX.read_bytes()
    priv_key = load_private_key_from_pfx(pfx_bytes, PASSWORD.encode())

    print("=== Test 1: Does lz77_huffman always succeed? ===")
    random_bytes = os.urandom(1432)
    try:
        decomp = xpress_lz77.lz77_huffman_decompress_py(random_bytes, 65536)
        print(f"  random 1432 bytes → lz77_huffman: {len(decomp)} bytes output")
    except Exception as ex:
        print(f"  random 1432 bytes → lz77_huffman: {type(ex).__name__}: {ex}")

    all_ff = b"\xff" * 1432
    try:
        decomp = xpress_lz77.lz77_huffman_decompress_py(all_ff, 65536)
        print(f"  all-0xFF 1432 bytes → lz77_huffman: {len(decomp)} bytes output")
    except Exception as ex:
        print(f"  all-0xFF → lz77_huffman: {type(ex).__name__}: {ex}")

    print("\n=== Test 2: PLAINTEXTKEYBLOB signature in RSA decrypted blob ===")
    for name, pfx_path, pw in [
        ("tde_full.bak", PFX, PASSWORD),
        ("tde_full_compressed.bak", PFX, PASSWORD),
    ]:
        data = (FIXTURE_DIR / name).read_bytes()
        hdr = parse_enc_header(data)
        rsa_blob = hdr.rsa_blob
        rsa_len = struct.unpack_from("<I", data, _HDR_RSALEN_OFF)[0]
        print(f"\n  {name}:")
        print(f"    rsa_len={rsa_len} (0x{rsa_len:x})  rsa_blob_end={_HDR_RSA_OFF+rsa_len:#x}")
        # Decrypt RSA blob
        ct_be = bytes(reversed(rsa_blob))
        try:
            from cryptography.hazmat.primitives.asymmetric import padding as _padding
            plaintext = priv_key.decrypt(ct_be, _padding.PKCS1v15())
            print(f"    RSA plaintext: {plaintext[:16].hex()}")
            # PLAINTEXTKEYBLOB: 08 02 00 00 XX 66 00 00 KK 00 00 00 ...
            if len(plaintext) >= 12:
                b_type = plaintext[0]
                b_ver = plaintext[1]
                alg_id = struct.unpack_from("<I", plaintext, 4)[0]
                key_size = struct.unpack_from("<I", plaintext, 8)[0]
                print(f"    bType={b_type:#04x} (0x08=PLAINTEXTKEYBLOB) bVersion={b_ver:#04x}")
                print(f"    algId={alg_id:#010x} (0x00006610=AES_256, 0x0000660e=AES_128)")
                print(f"    keySize={key_size} bytes")
                aes_key = plaintext[12:12+key_size]
                print(f"    AES key: {aes_key.hex()}")
        except Exception as ex:
            print(f"    RSA decrypt error: {ex}")

    print("\n=== Test 3: Manual chunk 0 decrypt and check ===")
    data = (FIXTURE_DIR / "tde_full_compressed.bak").read_bytes()
    hdr = parse_enc_header(data)
    aes_key = extract_aes_key(hdr.rsa_blob, priv_key)
    is_compressed = bool(hdr.flags & FLAG_COMPRESSED)
    print(f"  AES key: {aes_key.hex()}")
    print(f"  is_compressed: {is_compressed}")

    # Manually read the descriptor at 0x2000
    off = 0x2000
    raw = data[off:off+28]
    sig_val = struct.unpack_from("<I", raw, 0)[0]
    f1 = raw[4:12]
    ff = raw[12:20]
    bsz = struct.unpack_from("<I", raw, 20)[0]
    nonce = raw[24:28]
    print(f"\n  Descriptor at 0x2000:")
    print(f"    sig={sig_val:#010x}  comp_size={sig_val>>16}  bsz={bsz}  bsz%16={bsz%16}")
    print(f"    f1={f1.hex()}  ff={ff.hex()}")
    iv = f1 + ff
    print(f"    iv={iv.hex()}")
    ct = data[off+28:off+28+bsz]
    pt = _aes_cbc_decrypt(aes_key, iv, ct)
    comp_size = sig_val >> 16
    payload = pt[:comp_size]
    print(f"\n  Decrypted payload[0:32]: {payload[:32].hex()}")
    kc = _kraft_complete(payload, 0)
    print(f"  _kraft_complete(payload, 0) = {kc}")

    # Check if the payload starts with a valid Huffman table by computing nibble stats
    nibbles = []
    for b in payload[:256]:
        nibbles.append(b & 0xF)
        nibbles.append(b >> 4)
    from collections import Counter
    nc = Counter(nibbles)
    print(f"\n  Huffman table nibble distribution (first 256 bytes = 512 nibbles):")
    print(f"    len 0 (unused): {nc[0]}  len 1: {nc[1]}  len 2: {nc[2]}")
    print(f"    len 3: {nc[3]}  len 4: {nc[4]}  len 5: {nc[5]}  len 6: {nc[6]}")
    print(f"    len 7: {nc[7]}  len 8: {nc[8]}  len 9: {nc[9]}")
    print(f"    len 10: {nc[10]}  len 11: {nc[11]}  len 12: {nc[12]}")
    print(f"    len 13: {nc[13]}  len 14: {nc[14]}  len 15: {nc[15]}")

    # Compute actual Kraft sum
    MAX_LEN = 15
    kraft_sum = 0.0
    for nib in nibbles:
        if nib > 0:
            kraft_sum += 2 ** (-nib)
    print(f"\n  Kraft sum (should be 1.0 for valid table): {kraft_sum:.6f}")

    # Compare with working enc_bak record
    print("\n=== Test 4: Compare with enc_bak_aes256_compressed record 0 ===")
    enc_data = (FIXTURE_DIR / "enc_bak_aes256_compressed.bak").read_bytes()
    enc_hdr = parse_enc_header(enc_data)
    enc_priv = load_private_key_from_pfx(
        (FIXTURE_DIR / "enc_bak_cert.pfx").read_bytes(), b"EncBakCert!Fixture2024"
    )
    enc_aes = extract_aes_key(enc_hdr.rsa_blob, enc_priv)
    enc_records = list(_iter_inner_records(enc_data, enc_aes, _CHUNK0_DESC_OFFSET, True))
    if enc_records:
        _, enc_payload = enc_records[0]
        enc_nibbles = []
        for b in enc_payload[:256]:
            enc_nibbles.append(b & 0xF)
            enc_nibbles.append(b >> 4)
        enc_kraft = sum(2**(-n) for n in enc_nibbles if n > 0)
        print(f"  enc_bak record 0: kraft sum = {enc_kraft:.6f}")
        print(f"  enc_bak payload[0:32]: {enc_payload[:32].hex()}")


if __name__ == "__main__":
    main()
