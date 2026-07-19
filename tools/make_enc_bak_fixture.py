#!/usr/bin/env python3
"""Generate backup-level encrypted .bak fixtures for decryption reverse-engineering.

## Purpose

These fixtures support the backup-level `WITH ENCRYPTION` decryption feature (the
``mssqlbak/backupenc/`` stage).  Unlike TDE page fixtures, backup-level encryption
wraps the **entire MSSQLBAK stream** in AES; the MSSQLBAK container header (magic +
encryption descriptor) is plaintext but every XPRESS record chunk is AES-CBC
encrypted.

## Outputs (per SQL Server version)

    enc_bak_plain.bak               — same database, no encryption (known-plaintext)
    enc_bak_aes128_full.bak         — BACKUP … WITH ENCRYPTION (ALGORITHM=AES_128)
    enc_bak_aes256_full.bak         — BACKUP … WITH ENCRYPTION (ALGORITHM=AES_256)
    enc_bak_aes256_compressed.bak   — WITH ENCRYPTION + COMPRESSION (MSSQLBAK + enc)
    enc_bak_cert.pfx                — PKCS#12 certificate + private key (PFX)

Note: ``TRIPLE_DES_3KEY`` is deprecated in SQL Server 2022+ so it is omitted
from the default fixture; add a separate fixture if needed for regression coverage.

## Certificate

Created with ``CREATE CERTIFICATE … WITH SUBJECT = …`` (server-generated RSA key).
Exported via the classic ``BACKUP CERTIFICATE … TO FILE … WITH PRIVATE KEY (…)``
syntax (DER .cer + MS PVK file), then combined into a PKCS#12 .pfx in Python using
the same ``_pvk_read`` / ``_make_pfx_from_cer_and_pvk`` helpers as the TDE page
fixture.  This approach works on every SQL Server version.

## Certificate password

    ENC_BAK_CERT_PASSWORD  (see constant below)

The password is in plain text here because it protects only a throwaway test
fixture private key — never a production certificate.

## Usage

    python -m tools.fixture_run enc-bak
    python -m tools.fixture_run all-versions --suite enc-bak
"""
from __future__ import annotations

import argparse
import os
import struct
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
)

DB_NAME = "Enc_Bak_Fixture"
CERT_NAME = "Enc_Bak_Cert"
CERT_PASSWORD = "EncBakCert!Fixture2024"

CONTAINER_PLAIN_BAK   = f"/tmp/{DB_NAME}_plain.bak"
CONTAINER_AES128_BAK  = f"/tmp/{DB_NAME}_aes128.bak"
CONTAINER_AES256_BAK  = f"/tmp/{DB_NAME}_aes256.bak"
CONTAINER_AES256C_BAK = f"/tmp/{DB_NAME}_aes256_comp.bak"
CONTAINER_CER         = f"/tmp/{DB_NAME}_cert.cer"
CONTAINER_PVK         = f"/tmp/{DB_NAME}_cert.pvk"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PLAIN   = FIXTURE_DIR / "enc_bak_plain.bak"
OUT_AES128  = FIXTURE_DIR / "enc_bak_aes128_full.bak"
OUT_AES256  = FIXTURE_DIR / "enc_bak_aes256_full.bak"
OUT_AES256C = FIXTURE_DIR / "enc_bak_aes256_compressed.bak"
OUT_PFX     = FIXTURE_DIR / "enc_bak_cert.pfx"

_ALL_OUTPUTS = (OUT_PLAIN, OUT_AES128, OUT_AES256, OUT_AES256C, OUT_PFX)


# ---------------------------------------------------------------------------
# PVK → PFX helpers (same logic as make_tde_page_fixture.py)
# ---------------------------------------------------------------------------

def _pvk_read(pvk_bytes: bytes, password: str):
    """Parse a Microsoft PVK file and return an RSA private key object."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers
    from cryptography.hazmat.backends import default_backend

    if len(pvk_bytes) < 24:
        raise ValueError("PVK file too short")
    magic, version, _key_spec, enc_type, cb_salt, cb_blob = struct.unpack_from(
        "<IIIIII", pvk_bytes, 0
    )
    if magic != 0xB0B5F11E:
        raise ValueError(f"Bad PVK magic: {magic:#010x}")
    if version != 0:
        raise ValueError(f"Unsupported PVK version: {version}")

    salt     = pvk_bytes[24 : 24 + cb_salt]
    enc_blob = pvk_bytes[24 + cb_salt : 24 + cb_salt + cb_blob]

    if enc_type == 0x00000000:
        blob = enc_blob

    elif enc_type == 0x00000001:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
        pw_bytes = password.encode("ascii")
        d = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d.update(salt)
        d.update(pw_bytes)
        rc4_key = d.finalize()[:16]
        cipher = Cipher(algorithms.ARC4(rc4_key), mode=None, backend=default_backend())
        dec = cipher.decryptor()
        _BLOB_HEADER_LEN = 8
        blob = enc_blob[:_BLOB_HEADER_LEN] + (
            dec.update(enc_blob[_BLOB_HEADER_LEN:]) + dec.finalize()
        )

    elif enc_type == 0x80000001:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        pw_bytes = password.encode("utf-16-le")
        d1 = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d1.update(salt)
        d1.update(pw_bytes)
        h1 = d1.finalize()
        d2 = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d2.update(bytes([x ^ 0x36 for x in h1]))
        d2.update(pw_bytes)
        h2 = d2.finalize()
        key3des = (h1 + h2)[:24]
        iv = b"\x00" * 8
        cipher = Cipher(algorithms.TripleDES(key3des), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        blob = dec.update(enc_blob) + dec.finalize()

    else:
        raise ValueError(f"Unsupported PVK encryption type: {enc_type:#010x}")

    if len(blob) < 20:
        raise ValueError("Decrypted PVK blob too short (wrong password?)")
    if blob[0] != 0x07:
        raise ValueError(f"Expected PRIVATEKEYBLOB (0x07), got {blob[0]:#x}")
    if blob[8:12] != b"RSA2":
        raise ValueError(f"Expected RSA2 magic, got {blob[8:12]!r}")
    bit_len, pub_exp = struct.unpack_from("<II", blob, 12)
    full = bit_len // 8
    half = bit_len // 16

    def _le(off: int, length: int) -> int:
        return int.from_bytes(blob[off : off + length], "little")

    base = 20
    n  = _le(base, full);  base += full
    p  = _le(base, half);  base += half
    q  = _le(base, half);  base += half
    dp = _le(base, half);  base += half
    dq = _le(base, half);  base += half
    qi = _le(base, half);  base += half
    d  = _le(base, full)

    pub  = RSAPublicNumbers(pub_exp, n)
    priv = RSAPrivateNumbers(p, q, d, dp, dq, qi, pub)
    return priv.private_key(backend=default_backend())


def _make_pfx_from_cer_and_pvk(
    cer_bytes: bytes,
    pvk_bytes: bytes,
    pvk_password: str,
    pfx_password: str,
    out_pfx: Path,
) -> None:
    """Parse SQL Server's exported .cer + .pvk and write a PKCS#12 .pfx file."""
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, pkcs12

    private_key = _pvk_read(pvk_bytes, pvk_password)
    cert        = x509.load_der_x509_certificate(cer_bytes)

    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=b"Enc_Bak_Cert",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(pfx_password.encode()),
    )
    out_pfx.parent.mkdir(parents=True, exist_ok=True)
    out_pfx.write_bytes(pfx_bytes)


# ---------------------------------------------------------------------------
# SQL statements
# ---------------------------------------------------------------------------

def build_stmts() -> list[str]:
    """SQL statements that produce all five outputs."""
    return [
        # ── tear-down from previous run ──────────────────────────────────────
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        "USE [master]",
        f"""IF EXISTS (SELECT 1 FROM sys.certificates WHERE name = '{CERT_NAME}')
    DROP CERTIFICATE [{CERT_NAME}]""",
        # ── master key (prerequisite for certificate) ─────────────────────────
        """IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys
                   WHERE name = '##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'EncBakMasterKey!2024'""",
        # ── server certificate ────────────────────────────────────────────────
        f"CREATE CERTIFICATE [{CERT_NAME}] WITH SUBJECT = 'Enc Bak Fixture Cert'",
        # ── create test database with known-value rows ────────────────────────
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "CREATE TABLE probe (id INT PRIMARY KEY, val VARCHAR(40))",
        "INSERT INTO probe VALUES (1, 'alpha')",
        "INSERT INTO probe VALUES (2, 'beta')",
        "INSERT INTO probe VALUES (3, 'gamma')",
        # ── Step A: plaintext backup (known-plaintext reference) ──────────────
        "USE [master]",
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_PLAIN_BAK}' "
            "WITH FORMAT, INIT, COPY_ONLY"
        ),
        # ── Step B: AES_128 encrypted backup ─────────────────────────────────
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_AES128_BAK}' "
            f"WITH FORMAT, INIT, COPY_ONLY, "
            f"ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = [{CERT_NAME}])"
        ),
        # ── Step C: AES_256 encrypted backup ─────────────────────────────────
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_AES256_BAK}' "
            f"WITH FORMAT, INIT, COPY_ONLY, "
            f"ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = [{CERT_NAME}])"
        ),
        # ── Step D: AES_256 encrypted + compressed backup ────────────────────
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_AES256C_BAK}' "
            f"WITH FORMAT, INIT, COPY_ONLY, COMPRESSION, "
            f"ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = [{CERT_NAME}])"
        ),
        # ── Step E: export certificate (DER .cer + password-encrypted .pvk) ──
        (
            f"BACKUP CERTIFICATE [{CERT_NAME}] "
            f"TO FILE = N'{CONTAINER_CER}' "
            f"WITH PRIVATE KEY ("
            f"    FILE = N'{CONTAINER_PVK}', "
            f"    ENCRYPTION BY PASSWORD = N'{CERT_PASSWORD}'"
            f")"
        ),
        # ── cleanup ───────────────────────────────────────────────────────────
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE",
        f"DROP DATABASE [{DB_NAME}]",
        f"DROP CERTIFICATE [{CERT_NAME}]",
    ]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    args = p.parse_args()

    if not args.force and all(o.exists() for o in _ALL_OUTPUTS):
        print(
            f"skip (all outputs exist): {', '.join(o.name for o in _ALL_OUTPUTS)}",
            file=sys.stderr,
        )
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)

    for container_path in (CONTAINER_CER, CONTAINER_PVK):
        subprocess.run(
            ["podman", "exec", container, "rm", "-f", container_path],
            check=False,
        )

    load_and_backup_stmts(container, user, password, build_stmts())

    size = _copy_out(container, CONTAINER_PLAIN_BAK, OUT_PLAIN)
    print(f"wrote {OUT_PLAIN} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES128_BAK, OUT_AES128)
    print(f"wrote {OUT_AES128} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES256_BAK, OUT_AES256)
    print(f"wrote {OUT_AES256} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES256C_BAK, OUT_AES256C)
    print(f"wrote {OUT_AES256C} ({size:,} bytes)", file=sys.stderr)

    tmp_cer = FIXTURE_DIR / "_tmp_enc_bak_cert.cer"
    tmp_pvk = FIXTURE_DIR / "_tmp_enc_bak_cert.pvk"
    try:
        _copy_out(container, CONTAINER_CER, tmp_cer)
        _copy_out(container, CONTAINER_PVK, tmp_pvk)

        _make_pfx_from_cer_and_pvk(
            tmp_cer.read_bytes(),
            tmp_pvk.read_bytes(),
            pvk_password=CERT_PASSWORD,
            pfx_password=CERT_PASSWORD,
            out_pfx=OUT_PFX,
        )
    finally:
        tmp_cer.unlink(missing_ok=True)
        tmp_pvk.unlink(missing_ok=True)

    print(f"wrote {OUT_PFX} ({OUT_PFX.stat().st_size:,} bytes)", file=sys.stderr)
    print(f"\nCertificate password: {CERT_PASSWORD!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
