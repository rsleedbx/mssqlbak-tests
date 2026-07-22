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
Exported via :func:`tools.fixture_cert.export_cert_to_pfx`, which runs the classic
``BACKUP CERTIFICATE … TO FILE … WITH PRIVATE KEY (…)`` SQL, copies the ``.cer``
and ``.pvk`` from the container, and combines them into a PKCS#12 ``.pfx``.
This approach works on every SQL Server version.

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
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_cert import export_cert_to_pfx  # noqa: E402
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

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PLAIN   = FIXTURE_DIR / "enc_bak_plain.bak"
OUT_AES128  = FIXTURE_DIR / "enc_bak_aes128_full.bak"
OUT_AES256  = FIXTURE_DIR / "enc_bak_aes256_full.bak"
OUT_AES256C = FIXTURE_DIR / "enc_bak_aes256_compressed.bak"
OUT_PFX     = FIXTURE_DIR / "enc_bak_cert.pfx"

_ALL_OUTPUTS = (OUT_PLAIN, OUT_AES128, OUT_AES256, OUT_AES256C, OUT_PFX)


# ---------------------------------------------------------------------------
# SQL statements
# ---------------------------------------------------------------------------

def build_stmts() -> list[str]:
    """SQL statements that produce the four backup outputs.

    Certificate export is handled separately via :func:`export_cert_to_pfx`
    (which runs BACKUP CERTIFICATE as its own step).
    """
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
    ]


def build_cleanup_stmts() -> list[str]:
    """SQL statements to drop the database and certificate after cert export."""
    return [
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

    load_and_backup_stmts(container, user, password, build_stmts())

    size = _copy_out(container, CONTAINER_PLAIN_BAK, OUT_PLAIN)
    print(f"wrote {OUT_PLAIN} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES128_BAK, OUT_AES128)
    print(f"wrote {OUT_AES128} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES256_BAK, OUT_AES256)
    print(f"wrote {OUT_AES256} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_AES256C_BAK, OUT_AES256C)
    print(f"wrote {OUT_AES256C} ({size:,} bytes)", file=sys.stderr)

    # Export certificate before cleanup so the CERT_NAME still exists in master.
    export_cert_to_pfx(
        container, user, password,
        cert_name=CERT_NAME,
        out_pfx=OUT_PFX,
        pvk_password=CERT_PASSWORD,
        pfx_password=CERT_PASSWORD,
        cert_alias=b"Enc_Bak_Cert",
    )

    load_and_backup_stmts(container, user, password, build_cleanup_stmts())

    print(f"\nCertificate password: {CERT_PASSWORD!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
