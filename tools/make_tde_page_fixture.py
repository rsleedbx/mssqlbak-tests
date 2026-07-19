#!/usr/bin/env python3
"""Generate ``tde_page_full.bak`` — database-TDE (page-level) decryption fixture.

## Purpose

This fixture supports the TDE page decryption feature (Phase 2 of the TDE plan).
Unlike ``tde_full.bak`` (Gap F-1), this backup is NOT encrypted at the backup
level — the MSSQLBAK container and MTF framing are plaintext, but the individual
database pages are encrypted with AES-128 via SQL Server's Transparent Data
Encryption (TDE).  That means mssqlbak can parse the backup structure, read the
(plaintext) boot page to locate the encrypted DEK, and then AES-CBC-decrypt each
data page using the certificate private key.

## Certificate strategy

SQL Server creates the certificate natively (``CREATE CERTIFICATE … WITH SUBJECT``).
The private key is exported using the **classic** ``BACKUP CERTIFICATE … TO FILE …
WITH PRIVATE KEY (FILE = …, ENCRYPTION BY PASSWORD = …)`` syntax — no
``FORMAT = 'PFX'`` and no ``ALGORITHM`` clause, so it works on every SQL Server
version without version-dependent syntax differences.

The exported ``.pvk`` file is parsed by Python (``_pvk_read``) to extract the
RSA private key, which is then combined with the exported ``.cer`` (public cert)
to produce the final PKCS#12 ``.pfx`` file that mssqlbak uses for decryption.

## Outputs

    tde_page_full.bak      — database backup, backup-level NOT encrypted
    tde_page_cert.pfx      — PKCS#12 certificate + private key (password below)
    tde_page_plain.bak     — identical database, TDE disabled (plaintext pages)
                             used by the Phase 0 spike for known-plaintext attack

## Certificate password

    TDE_PAGE_CERT_PASSWORD  (see CERT_PASSWORD constant below)

This password is in plain text in this file because it protects only a test
fixture private key — not production data.  The fixture is intentionally
throwaway and the certificate is never trusted for anything else.

## Setup steps

    1.  SQL: Create Master Key in master (if absent).
    2.  SQL: Create self-signed certificate TDE_Page_Cert.
    3.  SQL: Create the test database with a small known table.
    4.  SQL: Backup the database WITHOUT TDE enabled → tde_page_plain.bak.
    5.  SQL: Create the Database Encryption Key (AES_128 via TDE_Page_Cert).
    6.  SQL: ALTER DATABASE SET ENCRYPTION ON; wait for state=3.
    7.  SQL: Backup the database WITHOUT backup-level encryption → tde_page_full.bak.
    8.  SQL: BACKUP CERTIFICATE → .cer (public) + .pvk (password-encrypted private key).
    9.  Python: copy .cer and .pvk from container; parse .pvk; write .pfx locally.
   10.  SQL: Drop the database and certificate.

Usage:
    python -m tools.fixture_run tde-page
    python -m tools.fixture_run all-versions --suite tde-page
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

import subprocess

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
)

DB_NAME = "TDE_Page_Fixture"
CERT_NAME = "TDE_Page_Cert"
CERT_PASSWORD = "TdePageCert!Fixture2024"
CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
CONTAINER_PLAIN_BAK = f"/tmp/{DB_NAME}_plain.bak"
CONTAINER_CER = f"/tmp/{DB_NAME}_cert.cer"   # public certificate (DER)
CONTAINER_PVK = f"/tmp/{DB_NAME}_cert.pvk"   # password-encrypted private key

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_BAK = FIXTURE_DIR / "tde_page_full.bak"
OUT_PLAIN_BAK = FIXTURE_DIR / "tde_page_plain.bak"
OUT_PFX = FIXTURE_DIR / "tde_page_cert.pfx"

# Encryption state: 3 = encryption complete.
_WAIT_SQL = (
    "WHILE (SELECT TOP 1 encryption_state "
    "FROM sys.dm_database_encryption_keys "
    f"WHERE database_id = DB_ID('{DB_NAME}')) != 3 "
    "WAITFOR DELAY '00:00:02'"
)


def _pvk_read(pvk_bytes: bytes, password: str):
    """Parse a Microsoft PVK file and return an RSA private key object.

    Supports PVK encryption types:
      0x00000000  unencrypted PRIVATEKEYBLOB
      0x00000001  RC4-based (SHA-1 key derivation from salt + password)
      0x80000001  "strong" (SHA-1 derived 3-key-3DES)

    The returned object is a
    ``cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey``.
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateNumbers,
        RSAPublicNumbers,
    )
    from cryptography.hazmat.backends import default_backend

    # ------------------------------------------------------------------ header
    if len(pvk_bytes) < 24:
        raise ValueError("PVK file too short")
    magic, version, _key_spec, enc_type, cb_salt, cb_blob = struct.unpack_from(
        "<IIIIII", pvk_bytes, 0
    )
    if magic != 0xB0B5F11E:
        raise ValueError(f"Bad PVK magic: {magic:#010x}")
    if version != 0:
        raise ValueError(f"Unsupported PVK version: {version}")

    salt = pvk_bytes[24 : 24 + cb_salt]
    enc_blob = pvk_bytes[24 + cb_salt : 24 + cb_salt + cb_blob]

    # ----------------------------------------------------------- decrypt blob
    if enc_type == 0x00000000:
        blob = enc_blob

    elif enc_type == 0x00000001:
        # RC4, key = SHA-1(salt || password_ascii)[:16]
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

        pw_bytes = password.encode("ascii")
        digest = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        digest.update(salt)
        digest.update(pw_bytes)
        rc4_key = digest.finalize()[:16]

        cipher = Cipher(algorithms.ARC4(rc4_key), mode=None, backend=default_backend())
        dec = cipher.decryptor()
        # The 8-byte BLOBHEADER is stored plaintext; only the RSA key material
        # (bytes 8+) is RC4-encrypted.
        _BLOB_HEADER_LEN = 8
        blob = enc_blob[:_BLOB_HEADER_LEN] + (
            dec.update(enc_blob[_BLOB_HEADER_LEN:]) + dec.finalize()
        )

    elif enc_type == 0x80000001:
        # "Strong" PVK: SHA-1 derived 24-byte 3DES key.
        # Key derivation follows the same recipe as PFX / PKCS#12 on Windows:
        #   hash1 = SHA-1(salt || password_unicode)
        #   hash2 = SHA-1(0x36*64 XOR pad || hash1)  (inner)
        #   key   = (hash1 || hash2)[:24]
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        pw_bytes = password.encode("utf-16-le")
        # Derive via SHA-1 twice
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

    # ----------------------------------------------- parse PRIVATEKEYBLOB
    # BLOBHEADER (8 bytes)
    if len(blob) < 20:
        raise ValueError("Decrypted PVK blob too short (wrong password?)")
    b_type = blob[0]
    if b_type != 0x07:
        raise ValueError(
            f"Expected PRIVATEKEYBLOB (0x07), got {b_type:#x} "
            "(PVK password may be wrong)"
        )

    # RSAPUBKEY (12 bytes) at offset 8
    rsa_magic = blob[8:12]
    if rsa_magic != b"RSA2":
        raise ValueError(f"Expected RSA2 magic, got {rsa_magic!r}")
    bit_len, pub_exp = struct.unpack_from("<II", blob, 12)

    full = bit_len // 8    # byte size of modulus / private exponent
    half = bit_len // 16   # byte size of primes / CRT exponents

    def _le(off: int, length: int) -> int:
        return int.from_bytes(blob[off : off + length], "little")

    base = 20  # past BLOBHEADER (8) + RSAPUBKEY (12)
    n  = _le(base,          full); base += full
    p  = _le(base,          half); base += half
    q  = _le(base,          half); base += half
    dp = _le(base,          half); base += half
    dq = _le(base,          half); base += half
    qi = _le(base,          half); base += half
    d  = _le(base,          full)

    pub = RSAPublicNumbers(pub_exp, n)
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
    cert = x509.load_der_x509_certificate(cer_bytes)

    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=b"TDE_Page_Cert",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(pfx_password.encode()),
    )
    out_pfx.parent.mkdir(parents=True, exist_ok=True)
    out_pfx.write_bytes(pfx_bytes)


def build_stmts() -> list[str]:
    """SQL statements that set up the TDE fixture in the correct order."""
    return [
        # Tear down any leftover database from a prior run.
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        "USE [master]",
        # Drop old cert if present (allows --force re-runs).
        f"""IF EXISTS (SELECT 1 FROM sys.certificates WHERE name = '{CERT_NAME}')
    DROP CERTIFICATE [{CERT_NAME}]""",
        # Master key: required before creating a certificate.
        """IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'TdeMasterKey!2024'""",
        # Self-signed certificate.  SQL Server owns the key pair.
        f"CREATE CERTIFICATE [{CERT_NAME}] WITH SUBJECT = 'TDE Page Fixture Cert'",
        # Create the test database with a small deterministic table.
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "CREATE TABLE probe (id INT PRIMARY KEY, val VARCHAR(40))",
        "INSERT INTO probe VALUES (1, 'hello')",
        "INSERT INTO probe VALUES (2, 'world')",
        "INSERT INTO probe VALUES (3, 'tde_test')",
        # --- Step A: plain (no-TDE) backup for the Phase 0 known-plaintext spike.
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_PLAIN_BAK}' "
            "WITH FORMAT, INIT, COPY_ONLY"
        ),
        # --- Step B: enable TDE (database-level, not backup-level).
        "USE [master]",
        (
            f"USE [{DB_NAME}]; "
            f"CREATE DATABASE ENCRYPTION KEY "
            f"WITH ALGORITHM = AES_128 "
            f"ENCRYPTION BY SERVER CERTIFICATE [{CERT_NAME}]"
        ),
        f"ALTER DATABASE [{DB_NAME}] SET ENCRYPTION ON",
        # Wait for background encryption to reach state 3 (fully encrypted).
        "USE [master]",
        _WAIT_SQL,
        # --- Step C: TDE backup WITHOUT backup-level encryption.
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' "
            "WITH FORMAT, INIT, COPY_ONLY"
        ),
        # --- Step D: export certificate + private key.
        # Classic (pre-PFX) BACKUP CERTIFICATE format — works on all SQL Server
        # versions without any ALGORITHM clause.  Produces a DER-encoded .cer and
        # a password-encrypted Microsoft PVK file.
        (
            f"BACKUP CERTIFICATE [{CERT_NAME}] "
            f"TO FILE = N'{CONTAINER_CER}' "
            f"WITH PRIVATE KEY ("
            f"    FILE = N'{CONTAINER_PVK}', "
            f"    ENCRYPTION BY PASSWORD = N'{CERT_PASSWORD}'"
            f")"
        ),
        # Cleanup: drop the database and certificate.
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE",
        f"DROP DATABASE [{DB_NAME}]",
        f"DROP CERTIFICATE [{CERT_NAME}]",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    args = p.parse_args()

    if not args.force and OUT_BAK.exists() and OUT_PLAIN_BAK.exists() and OUT_PFX.exists():
        print(
            f"skip (all outputs exist): {OUT_BAK.name}, {OUT_PLAIN_BAK.name}, {OUT_PFX.name}",
            file=sys.stderr,
        )
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    print(
        "TDE setup may take 30–90 s while background encryption runs...",
        file=sys.stderr,
    )

    # Remove stale .cer/.pvk files left by a previous failed run so that
    # "BACKUP CERTIFICATE … TO FILE" does not fail with "file already exists".
    for container_path in (CONTAINER_CER, CONTAINER_PVK):
        subprocess.run(
            ["podman", "exec", container, "rm", "-f", container_path],
            check=False,
        )

    load_and_backup_stmts(container, user, password, build_stmts())

    size_bak = _copy_out(container, CONTAINER_BAK, OUT_BAK)
    print(f"wrote {OUT_BAK} ({size_bak:,} bytes)", file=sys.stderr)

    size_plain = _copy_out(container, CONTAINER_PLAIN_BAK, OUT_PLAIN_BAK)
    print(f"wrote {OUT_PLAIN_BAK} ({size_plain:,} bytes)", file=sys.stderr)

    # Fetch the certificate files from the container and combine into a PFX.
    tmp_cer = FIXTURE_DIR / "_tmp_cert.cer"
    tmp_pvk = FIXTURE_DIR / "_tmp_cert.pvk"
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
    print(
        f"\nCertificate password: {CERT_PASSWORD!r}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
