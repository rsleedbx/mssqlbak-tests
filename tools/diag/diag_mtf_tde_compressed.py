#!/usr/bin/env python3
"""Diagnostic: verify end-to-end extraction for tde_full_compressed.bak via mtf.py.

Tests the full chained decryption path:
  1. Outer backup-level AES-256-CBC decryption (backup cert RSA key).
  2. Inner DEK-AES-128-CBC decryption (same IV as outer; DEK from outer header).
  3. XPRESS decompression.
  4. MDF page assembly.

Expected: pages extracted and at least one data row recoverable.

Run:
    mssqlbak-tests/.venv/bin/python mssqlbak-tests/tools/diag/diag_mtf_tde_compressed.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]  # mssqlbak-core
sys.path.insert(0, str(_REPO))
# Also add mssqlbak library from sibling mssqlbak repo if present
_MSSQLBAK_LIB = _REPO.parent / "mssqlbak"
if _MSSQLBAK_LIB.is_dir():
    sys.path.insert(0, str(_MSSQLBAK_LIB.parent))

FIXTURE_DIR = _REPO.parent / "mssqlbak-tests" / "tests" / "fixtures_2022"
BAK = FIXTURE_DIR / "tde_full_compressed.bak"
PFX = FIXTURE_DIR / "tde_full_cert.pfx"
PFX_PASSWORD = "TDE_FULL_CERT_PASSWORD"


def main() -> int:
    if not BAK.exists():
        print(f"SKIP: fixture not found: {BAK}", file=sys.stderr)
        return 0
    if not PFX.exists():
        print(f"SKIP: cert not found: {PFX}", file=sys.stderr)
        return 0

    from mssqlbak.tde.keys import load_tde_key
    from mssqlbak.mtf import extract_mdf_images

    tde_key = load_tde_key(PFX, PFX_PASSWORD)
    print(f"Loaded TDE key — thumbprint: {tde_key.cert_thumbprint.hex() if tde_key.cert_thumbprint else 'None'}")

    data = BAK.read_bytes()
    print(f"Fixture size: {len(data):,} bytes")

    images = extract_mdf_images(data, tde_key=tde_key)
    print(f"Assembled {len(images)} file image(s):")
    total_pages = 0
    for fid, pages in images.items():
        print(f"  file_id={fid}: {len(pages)} pages")
        total_pages += len(pages)

    if total_pages == 0:
        print("FAIL: no pages extracted", file=sys.stderr)
        return 1

    print(f"PASS: {total_pages} total pages across {len(images)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
