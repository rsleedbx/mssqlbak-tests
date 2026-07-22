#!/usr/bin/env python3
"""Verify that the TDE DEK descriptor is in the outer MSSQLBAK header of
tde_full_compressed.bak (before backup-level decryption), and try to extract
the DEK by scanning the raw file bytes directly."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from mssqlbak.backupenc.keys import load_private_key_from_pfx
from mssqlbak.tde.dek import _find_dek_descriptor, extract_dek
from mssqlbak.tde.keys import load_tde_key

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PASSWORD = "TdeFullCert!Fixture2024"


def hexdump(data: bytes, base: int = 0, limit: int = 128) -> None:
    for off in range(0, min(limit, len(data)), 16):
        chunk = data[off : off + 16]
        hexb = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {base + off:06x}: {hexb:<47}  {asc}")


def try_extract_dek_from(buf: bytes, label: str, tde_key: object) -> None:
    thumb = tde_key.cert_thumbprint
    print(f"\n--- {label} ---")
    print(f"  buffer size: {len(buf):,}")
    # Manual thumbprint search
    idx = buf.find(thumb)
    if idx >= 0:
        print(f"  Thumbprint found at offset {idx:#x}")
        hexdump(buf[max(0,idx-8):idx+len(thumb)+32], base=max(0,idx-8))
    else:
        print(f"  Thumbprint NOT found in buffer")

    # Use _find_dek_descriptor with NO range restriction
    loc = _find_dek_descriptor(buf, thumb)
    if loc is not None:
        print(f"  _find_dek_descriptor: found at {loc:#x}")
    else:
        print(f"  _find_dek_descriptor: not found")

    # Try extract_dek with default range
    try:
        dek = extract_dek(buf, tde_key)
        print(f"  extract_dek: SUCCESS → {dek.hex()}")
    except Exception as e:
        print(f"  extract_dek: FAILED → {e}")


def main() -> None:
    tde_key = load_tde_key(PFX, PASSWORD)
    thumb = tde_key.cert_thumbprint
    print(f"TDE thumbprint: {thumb.hex()}")
    print(f"TDE priv_key:   {type(tde_key.private_key).__name__}")

    for name in ("tde_full.bak", "tde_full_compressed.bak"):
        bak = FIXTURE_DIR / name
        if not bak.exists():
            print(f"\nSKIP: {name}")
            continue
        data = bak.read_bytes()
        print(f"\n{'='*60}")
        print(f"  {name}  ({len(data):,} bytes)")

        # Search the raw file bytes for the thumbprint
        try_extract_dek_from(data, "raw file (before backup-level decryption)", tde_key)

        # For tde_full_compressed.bak: also try on just the first 0x400 bytes (header region)
        if "compressed" in name:
            try_extract_dek_from(data[:0x400], "first 0x400 bytes only", tde_key)

            # Show bytes around the thumbprint in context
            idx = data.find(thumb)
            if idx >= 0:
                print(f"\n  Context around thumbprint (offset {idx:#x}):")
                hexdump(data[max(0,idx-28):idx+len(thumb)+40], base=max(0,idx-28))

                # Parse DEK structure manually
                pre = idx - 4
                thumb_len = int.from_bytes(data[pre:pre+4], "little")
                after_thumb = idx + len(thumb)
                ciphertext_len = int.from_bytes(data[after_thumb:after_thumb+4], "little")
                print(f"\n  Parsed DEK structure:")
                print(f"    thumb_len prefix: {thumb_len}")
                print(f"    thumbprint: {data[idx:idx+20].hex()}")
                print(f"    ciphertext_len: {ciphertext_len}")
                if ciphertext_len <= 512:
                    ct = data[after_thumb+4:after_thumb+4+ciphertext_len]
                    print(f"    ciphertext ({len(ct)} bytes): {ct[:16].hex()}...")
                    # Try to RSA-decrypt
                    priv_key = load_private_key_from_pfx(PFX.read_bytes(), PASSWORD.encode())
                    try:
                        from cryptography.hazmat.primitives.asymmetric import padding as _pad
                        plaintext = priv_key.decrypt(ct, _pad.PKCS1v15())
                        print(f"    RSA-decrypted ({len(plaintext)} bytes): {plaintext[:32].hex()}")
                    except Exception as e:
                        print(f"    RSA decrypt FAILED: {e}")


if __name__ == "__main__":
    main()
