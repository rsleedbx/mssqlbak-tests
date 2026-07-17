#!/usr/bin/env python3
"""Phase 0 TDE spike: prove per-page DEK extraction and AES-CBC IV derivation.

## Purpose

This diagnostic script is the GO/NO-GO gate for the TDE page-decryption feature.
Given:
    - tde_page_full.bak   (database-TDE backup, no backup-level encryption)
    - tde_page_plain.bak  (identical data, TDE disabled — known plaintext)
    - tde_page_cert.pfx   (certificate + private key, password below)

It:
    1.  Parses the MSSQLBAK container of each backup to locate raw pages.
    2.  RSA-decrypts the DEK from the plaintext boot page of the TDE backup.
    3.  Attempts to AES-CBC-decrypt a TDE data page using various IV candidates
        and verifies the output byte-exact against the corresponding plaintext page.
    4.  Reports the winning IV recipe or exits non-zero if none matched.

## Exit codes

    0 — IV recipe found; prints the recipe as a Python snippet to stdout.
    1 — No IV recipe matched (TDE decryption is not yet implemented).
    2 — Input files missing (run: python -m tools.fixture_run tde-page first).

## Usage

    python -m tools.diag._diag_tde_spike \\
        --tde tests/fixtures_2022/tde_page_full.bak \\
        --plain tests/fixtures_2022/tde_page_plain.bak \\
        --pfx tests/fixtures_2022/tde_page_cert.pfx \\
        --password 'TdePageCert!Fixture2024'

The script is read-only and safe to re-run.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

PAGE_SIZE = 8192

# Offset of the page-id / file-id pair in the page header (same layout used
# by mssqlbak.mtf and mssqlbak.compressed.stream).
_OFF_HEADER_VERSION = 1   # m_headerVersion: must be 1 for valid pages
_OFF_TYPE           = 0   # m_type: page type
_OFF_PAGE_ID        = 4   # m_pageId (int32) + m_fileId (int16) = 6 bytes
_OFF_PAGE_ID_STRUCT = struct.Struct("<IH")  # page_id (uint32) + file_id (uint16)

# The first 96 bytes of each compressed chunk carry a page header; TDE
# encrypts the payload but leaves these fields readable so SQL Server can
# identify the page.  The region mssqlbak can safely use as plaintext for
# verification starts just after the header.
_HEADER_CLEAR_BYTES = 96   # conservative; real header is shorter but safe

# Boot page coordinates.
_BOOT_FILE_ID = 1
_BOOT_PAGE_ID = 9   # page 9, file 1 is the SQL Server boot page (dbi_dbid etc.)

# DEK blob is stored in the boot page (page 9 of file 1).  The DEK blob
# starts with a 2-byte length followed by the RSA-encrypted DEK bytes.
# SQL Server 2017+ stores the encrypted DEK starting around offset 512 in
# the boot page after a recognizable header; we scan for it.
_DEK_BLOB_SCAN_START  = 256    # first candidate offset in boot page payload
_DEK_BLOB_SCAN_END    = 4000   # upper bound; DEK is always in the first 4 KB

# Certificate thumbprint size (SHA-1, 20 bytes).
_THUMBPRINT_SIZE = 20

# AES-128 key size in bytes.
_AES_KEY_SIZE = 16


def _iter_pages_from_bak(bak_path: Path) -> dict[tuple[int, int], bytes]:
    """Return {(file_id, page_id): page_bytes} for all pages in a .bak.

    Uses the mssqlbak page reading infrastructure to support both compressed
    (MSSQLBAK-magic) and uncompressed (MTF) backups.
    """
    from mssqlbak.pages import PageStore
    store = PageStore.from_bak(bak_path)
    pages: dict[tuple[int, int], bytes] = {}
    # Collect all catalog pages (low page IDs).
    for (file_id, page_id), page_bytes in store._index._catalog.items():  # type: ignore[union-attr]
        pages[(file_id, page_id)] = bytes(page_bytes)
    # Collect chunk pages.
    try:
        for chunk_key in store._index._by_file.get(1, []):  # type: ignore[union-attr]
            pass
    except Exception:
        pass
    return pages


def _load_all_pages(bak_path: Path) -> dict[tuple[int, int], bytes]:
    """Load every page from *bak_path*, keyed by (file_id, page_id)."""
    import mmap
    import struct as _st

    from mssqlbak.compressed.stream import _iter_chunks_with_pages, _MSSQLBAK_MAGIC
    from mssqlbak.mtf import _find_image_start, PAGE_SIZE as _PS

    data = bak_path.read_bytes()
    pages: dict[tuple[int, int], bytes] = {}

    if data[:8] == _MSSQLBAK_MAGIC:
        # Compressed MSSQLBAK container.
        from mssqlbak.bak_io import LocalBakReader
        reader = LocalBakReader(bak_path)
        mm = reader._mm  # type: ignore[attr-defined]
        for _data_off, _read_len, page_iter in _iter_chunks_with_pages(
            mm,  # type: ignore[arg-type]
        ):
            for file_id, page_id, page_bytes in page_iter:
                pages[(file_id, page_id)] = bytes(page_bytes)
        return pages
    else:
        # Uncompressed MTF.
        mm = mmap.mmap(-1, len(data))
        mm.write(data)
        mm.seek(0)
        try:
            img_start = _find_image_start(mm)
        except Exception as e:
            print(f"ERROR: could not locate MDF image in {bak_path}: {e}", file=sys.stderr)
            return {}
        off = img_start
        while off + PAGE_SIZE <= len(data):
            page = data[off : off + PAGE_SIZE]
            if len(page) < PAGE_SIZE:
                break
            page_id_b = page[_OFF_PAGE_ID : _OFF_PAGE_ID + 6]
            if len(page_id_b) < 6:
                off += PAGE_SIZE
                continue
            page_id, file_id = _OFF_PAGE_ID_STRUCT.unpack(page_id_b)
            if file_id == 1 and page_id > 0:
                pages[(file_id, page_id)] = page
            off += PAGE_SIZE
        return pages


def _load_raw_pages_from_mtf(bak_path: Path) -> dict[tuple[int, int], bytes]:
    """Extract raw (possibly encrypted) pages from an MTF or MSSQLBAK backup.

    For the TDE backup we cannot use PageStore.from_bak (it raises
    EncryptedBackupError); instead, we parse the MTF structure manually
    to get raw bytes, which will be ciphertext for TDE pages.
    """
    import mmap as _mmap

    data = bak_path.read_bytes()

    from mssqlbak.compressed.stream import _MSSQLBAK_MAGIC
    if data[:8] == _MSSQLBAK_MAGIC:
        # For a TDE backup in MSSQLBAK container format the chunks are
        # already parsed but the page bytes are ciphertext.
        # Use the raw chunk iterator which does NOT check page validity.
        from mssqlbak.compressed.stream import _iter_chunks_with_pages
        mm = _mmap.mmap(-1, len(data))
        mm.write(data)
        mm.seek(0)
        pages: dict[tuple[int, int], bytes] = {}
        try:
            from mssqlbak.bak_io import LocalBakReader
            reader = LocalBakReader(bak_path)
            _mm = reader._mm  # type: ignore[attr-defined]
            for _data_off, _read_len, page_iter in _iter_chunks_with_pages(_mm):  # type: ignore[arg-type]
                for file_id, page_id, page_bytes in page_iter:
                    pages[(file_id, page_id)] = bytes(page_bytes)
        except Exception:
            pass
        # Also manually scan for the boot page (page 0/1, page 9/1) which
        # SQL Server stores in the catalog region (always plaintext).
        from mssqlbak.chunk_index import ChunkIndex
        from mssqlbak.bak_io import LocalBakReader as _LBR
        try:
            from mssqlbak.compressed.stream import build_chunk_index
            _reader = _LBR(bak_path)
            _mm2 = _reader._mm  # type: ignore[attr-defined]
            idx = build_chunk_index(_reader)
            for (fid, pid), pb in idx._catalog.items():  # type: ignore[union-attr]
                pages[(fid, pid)] = bytes(pb)
        except Exception:
            pass
        return pages
    else:
        # MTF: scan linearly for pages.
        pages = {}
        off = 0
        # Skip MTF headers — scan for 8KB page-looking blocks.
        while off + PAGE_SIZE <= len(data):
            block = data[off : off + PAGE_SIZE]
            page_id_b = block[_OFF_PAGE_ID : _OFF_PAGE_ID + 6]
            if len(page_id_b) >= 6:
                page_id, file_id = _OFF_PAGE_ID_STRUCT.unpack(page_id_b)
                if 1 <= file_id <= 4 and page_id < 100000:
                    pages[(file_id, page_id)] = block
            off += PAGE_SIZE
        return pages


def _find_boot_page(pages: dict[tuple[int, int], bytes]) -> bytes | None:
    """Return the plaintext boot page (file=1, page=9) from *pages*."""
    return pages.get((1, 9)) or pages.get((1, 1))


def _scan_dek_blob(boot_page: bytes) -> bytes | None:
    """Scan the boot page for the encrypted DEK blob.

    SQL Server stores the DEK as an RSA-encrypted blob in the boot page.
    The exact offset varies by version (typically 0x4A0–0x700 range).
    We look for a 2-byte little-endian length field followed by that many
    high-entropy bytes (the RSA ciphertext).  RSA-1024 produces 128 bytes;
    RSA-2048 produces 256 bytes.
    """
    _CANDIDATE_DEK_SIZES = (128, 256)
    for size in _CANDIDATE_DEK_SIZES:
        for off in range(_DEK_BLOB_SCAN_START, _DEK_BLOB_SCAN_END - size - 2):
            length_bytes = boot_page[off : off + 2]
            if len(length_bytes) < 2:
                continue
            length = struct.unpack_from("<H", length_bytes)[0]
            if length != size:
                continue
            blob = boot_page[off + 2 : off + 2 + size]
            if len(blob) < size:
                continue
            # Heuristic: RSA ciphertext has high byte diversity (low zero count).
            zero_count = blob.count(0)
            if zero_count < size // 4:   # at most 25% zeros in RSA ciphertext
                return blob
    return None


def _load_pfx(pfx_path: Path, password: str) -> object:
    """Load an RSA private key from a PKCS#12 PFX file.

    Returns the private key object from the ``cryptography`` library.
    """
    from cryptography.hazmat.primitives.serialization import pkcs12
    pfx_data = pfx_path.read_bytes()
    pk12 = pkcs12.load_pkcs12(pfx_data, password.encode())
    return pk12.key


def _rsa_decrypt(private_key: object, ciphertext: bytes) -> bytes:
    """RSA-OAEP decrypt *ciphertext* using *private_key*.

    SQL Server uses OAEP with SHA-1 for DEK encryption.
    Falls back to PKCS1v15 if OAEP fails.
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    try:
        return private_key.decrypt(  # type: ignore[union-attr]
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )
    except Exception:
        pass
    try:
        return private_key.decrypt(  # type: ignore[union-attr]
            ciphertext,
            padding.PKCS1v15(),
        )
    except Exception as e:
        raise ValueError(f"RSA decrypt failed with both OAEP and PKCS1v15: {e}") from e


def _try_aes_cbc(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """AES-CBC decrypt *ciphertext* with *key* and *iv*."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend(),
    )
    dec = cipher.decryptor()
    return dec.update(ciphertext) + dec.finalize()


def _page_id_iv(page_id: int, file_id: int) -> bytes:
    """IV = page_id (4B LE) + file_id (2B LE) + 10 zero bytes."""
    return struct.pack("<IH", page_id, file_id) + b"\x00" * 10


def _derive_iv_candidates(
    page_id: int, file_id: int, enc_page: bytes
) -> list[tuple[str, bytes]]:
    """Return a list of (description, 16-byte IV) candidates to try."""
    candidates: list[tuple[str, bytes]] = []

    # Candidate 1: zeros
    candidates.append(("zeros", b"\x00" * 16))

    # Candidate 2: page_id little-endian as first 4 bytes
    candidates.append(("page_id_le_padded", struct.pack("<I", page_id) + b"\x00" * 12))

    # Candidate 3: page_id + file_id little-endian
    candidates.append(("page_id+file_id_le", _page_id_iv(page_id, file_id)))

    # Candidate 4: page_id big-endian
    candidates.append(("page_id_be_padded", struct.pack(">I", page_id) + b"\x00" * 12))

    # Candidate 5: first 16 bytes of the (encrypted) page header
    # (SQL Server sometimes uses a portion of the page record as tweak)
    candidates.append(("enc_page_header_16", enc_page[:16]))

    # Candidate 6: bytes 4-20 (after m_type/m_headerVersion)
    candidates.append(("enc_page_bytes_4_20", enc_page[4:20]))

    # Candidate 7: page_id (uint64 little-endian) + zeros
    candidates.append((
        "page_id_u64_le",
        struct.pack("<Q", page_id) + b"\x00" * 8,
    ))

    # Candidate 8: (file_id << 32 | page_id) as 8-byte little-endian + zeros
    combined = (file_id << 32) | page_id
    candidates.append((
        "file_id<<32|page_id_u64",
        struct.pack("<Q", combined) + b"\x00" * 8,
    ))

    # Candidate 9: XTS-style sector number (page index in file)
    sector = page_id
    candidates.append((
        "xts_sector_u128_le",
        struct.pack("<QQ", sector, 0),
    ))

    # Candidate 10: first 16 bytes of page as-is (for AES-XTS which doesn't use CBC IV)
    candidates.append(("enc_page_first16_direct", enc_page[:16]))

    # Candidate 11: page_id in network byte order (big-endian) 8 bytes + zeros
    candidates.append((
        "page_id_u64_be",
        struct.pack(">Q", page_id) + b"\x00" * 8,
    ))

    return candidates


def _pages_match(decrypted: bytes, plaintext: bytes) -> bool:
    """Return True if the decrypted page matches the plaintext beyond header."""
    # Skip the first 96 bytes (page header — format varies) and compare the rest.
    return decrypted[_HEADER_CLEAR_BYTES:] == plaintext[_HEADER_CLEAR_BYTES:]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tde",     required=False, help="TDE backup (tde_page_full.bak)")
    p.add_argument("--plain",   required=False, help="Plain backup (tde_page_plain.bak)")
    p.add_argument("--pfx",     required=False, help="Certificate PFX (tde_page_cert.pfx)")
    p.add_argument("--password", default="TdePageCert!Fixture2024",
                   help="PFX private key password")
    p.add_argument("--fixture-dir",
                   default=str(_REPO_ROOT / "tests" / "fixtures_2022"),
                   help="Directory containing the fixture files")
    args = p.parse_args()

    fixture_dir = Path(args.fixture_dir)
    tde_path   = Path(args.tde)   if args.tde   else fixture_dir / "tde_page_full.bak"
    plain_path = Path(args.plain) if args.plain else fixture_dir / "tde_page_plain.bak"
    pfx_path   = Path(args.pfx)   if args.pfx   else fixture_dir / "tde_page_cert.pfx"

    missing = [p for p in (tde_path, plain_path, pfx_path) if not p.exists()]
    if missing:
        print("ERROR: missing input files:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print(
            "\nGenerate them with:\n"
            "  python -m tools.fixture_run tde-page\n"
            "or for a specific version:\n"
            "  FIXTURE_DIR=tests/fixtures_2022 python -m tools.make_tde_page_fixture",
            file=sys.stderr,
        )
        return 2

    # --- Step 1: load certificate private key.
    print(f"Loading PFX from {pfx_path} ...", file=sys.stderr)
    try:
        private_key = _load_pfx(pfx_path, args.password)
        print("  OK: certificate private key loaded", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: could not load PFX: {e}", file=sys.stderr)
        return 1

    # --- Step 2: load the TDE pages (raw ciphertext including catalog pages).
    print(f"\nLoading TDE backup pages from {tde_path} ...", file=sys.stderr)
    tde_pages = _load_raw_pages_from_mtf(tde_path)
    print(f"  loaded {len(tde_pages)} pages from TDE backup", file=sys.stderr)

    # --- Step 3: load the plaintext pages for comparison.
    print(f"\nLoading plaintext backup pages from {plain_path} ...", file=sys.stderr)
    try:
        plain_pages = _load_all_pages(plain_path)
    except Exception:
        # Try raw approach as fallback.
        plain_pages = _load_raw_pages_from_mtf(plain_path)
    print(f"  loaded {len(plain_pages)} pages from plain backup", file=sys.stderr)

    # --- Step 4: locate the boot page (plaintext even in TDE backup).
    boot_page = _find_boot_page(tde_pages)
    if boot_page is None:
        # Try alternate page IDs.
        for pid in range(0, 15):
            bp = tde_pages.get((1, pid))
            if bp is not None:
                boot_page = bp
                print(f"  found boot-like page at (1, {pid})", file=sys.stderr)
                break
    if boot_page is None:
        print("ERROR: could not locate boot page in TDE backup", file=sys.stderr)
        return 1
    print("  OK: boot page located", file=sys.stderr)

    # --- Step 5: scan for DEK blob and RSA-decrypt it.
    print("\nScanning boot page for encrypted DEK blob ...", file=sys.stderr)
    dek_blob = _scan_dek_blob(boot_page)
    if dek_blob is None:
        print("ERROR: could not find DEK blob in boot page (offset scan failed)", file=sys.stderr)
        print("  Boot page hex (first 512 bytes):", file=sys.stderr)
        for i in range(0, min(512, len(boot_page)), 16):
            print(f"  {i:04x}: {boot_page[i:i+16].hex(' ')}", file=sys.stderr)
        return 1
    print(f"  found DEK blob candidate ({len(dek_blob)} bytes)", file=sys.stderr)

    print("Attempting RSA decrypt of DEK blob ...", file=sys.stderr)
    try:
        dek_raw = _rsa_decrypt(private_key, dek_blob)
        print(f"  RSA decrypt succeeded: {len(dek_raw)} bytes", file=sys.stderr)
        print(f"  DEK raw hex: {dek_raw[:32].hex()}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: RSA decrypt failed: {e}", file=sys.stderr)
        print(
            "\n  The DEK blob scan may have located the wrong blob.",
            "  Inspect the boot page hex dump above to identify the correct offset.",
            file=sys.stderr,
        )
        return 1

    # AES-128 DEK is typically the last 16 bytes of the decrypted buffer.
    dek = dek_raw[-_AES_KEY_SIZE:] if len(dek_raw) >= _AES_KEY_SIZE else dek_raw
    if len(dek) < _AES_KEY_SIZE:
        print(f"ERROR: DEK too short ({len(dek)} bytes, need {_AES_KEY_SIZE})", file=sys.stderr)
        return 1
    print(f"  AES-128 DEK (last {_AES_KEY_SIZE} bytes): {dek.hex()}", file=sys.stderr)

    # --- Step 6: find a data page present in both backups and try IVs.
    # Look for pages that exist in both and are non-trivial (not the boot page).
    common_keys = set(tde_pages) & set(plain_pages)
    data_pages = [
        k for k in sorted(common_keys)
        if k[1] > 9 and k[0] == 1   # file 1, beyond the first few system pages
    ]
    if not data_pages:
        # Relax to any common page.
        data_pages = sorted(common_keys)
    print(f"\nFound {len(data_pages)} candidate data pages for IV derivation", file=sys.stderr)

    winning_recipe: str | None = None
    winning_page: tuple[int, int] | None = None

    for (file_id, page_id) in data_pages[:20]:  # try first 20 candidates
        enc_page   = tde_pages[(file_id, page_id)]
        plain_page = plain_pages[(file_id, page_id)]

        if enc_page == plain_page:
            # Page is identical — it might be in the catalog (plaintext in TDE backup too).
            continue

        iv_candidates = _derive_iv_candidates(page_id, file_id, enc_page)
        for iv_desc, iv in iv_candidates:
            try:
                # AES-CBC: decrypt full page.
                # TDE does NOT encrypt the 96-byte page header; it encrypts
                # the payload starting at byte 96 in 16-byte AES blocks.
                payload_start = 96
                if len(enc_page) < payload_start + 16:
                    continue
                enc_payload = enc_page[payload_start:]
                # Pad to block boundary if needed.
                pad = len(enc_payload) % 16
                if pad:
                    enc_payload = enc_payload[:len(enc_payload) - pad]
                dec_payload = _try_aes_cbc(dek, iv, enc_payload)
                decrypted = enc_page[:payload_start] + dec_payload
                if _pages_match(decrypted, plain_page):
                    winning_recipe = iv_desc
                    winning_page = (file_id, page_id)
                    print(
                        f"\n*** SUCCESS *** page ({file_id},{page_id}): "
                        f"IV recipe = {iv_desc!r}",
                        file=sys.stderr,
                    )
                    break
                # Also try full-page encryption (no header skip).
                enc_full = enc_page
                pad2 = len(enc_full) % 16
                if pad2:
                    enc_full = enc_full[:len(enc_full) - pad2]
                dec_full = _try_aes_cbc(dek, iv, enc_full)
                if _pages_match(dec_full, plain_page):
                    winning_recipe = f"{iv_desc}_full_page"
                    winning_page = (file_id, page_id)
                    print(
                        f"\n*** SUCCESS (full-page) *** page ({file_id},{page_id}): "
                        f"IV recipe = {winning_recipe!r}",
                        file=sys.stderr,
                    )
                    break
            except Exception:
                continue
        if winning_recipe:
            break

    if winning_recipe is None:
        print("\nFAIL: no IV recipe matched any data page.", file=sys.stderr)
        print(
            "Next steps:\n"
            "  1. Dump the boot page with: python -m tools.diag._diag_tde_spike --dump-boot\n"
            "  2. Inspect the DEK blob offset in the boot page hex dump above.\n"
            "  3. Try AES-XTS mode (used by some SQL Server versions) instead of CBC.\n"
            "  4. Check whether SQL Server uses a tweak derived from LSN or alloc unit id.\n"
            "  5. File a TDE-spike issue with the boot page hex dump attached.",
            file=sys.stderr,
        )
        return 1

    print(f"\nResult: IV recipe = {winning_recipe!r}", file=sys.stderr)
    print(f"        Page: file_id={winning_page[0]}, page_id={winning_page[1]}", file=sys.stderr)

    # Emit a Python snippet documenting the recipe for use in mssqlbak/tde/page.py.
    snippet = f"""
# TDE per-page IV derivation recipe (discovered by _diag_tde_spike.py)
# Winning recipe: {winning_recipe!r}
# Winning page:   file_id={winning_page[0]}, page_id={winning_page[1]}
import struct

def _tde_iv(page_id: int, file_id: int, page_bytes: bytes) -> bytes:
    \"\"\"Return the 16-byte IV for AES-CBC TDE decryption of this page.\"\"\"
"""
    if winning_recipe == "zeros":
        snippet += "    return b'\\x00' * 16\n"
    elif winning_recipe == "page_id+file_id_le":
        snippet += "    return struct.pack('<IH', page_id, file_id) + b'\\x00' * 10\n"
    elif winning_recipe == "page_id_le_padded":
        snippet += "    return struct.pack('<I', page_id) + b'\\x00' * 12\n"
    elif winning_recipe == "xts_sector_u128_le":
        snippet += "    return struct.pack('<QQ', page_id, 0)\n"
    else:
        snippet += f"    # TODO: implement {winning_recipe!r}\n    raise NotImplementedError\n"

    print(snippet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
