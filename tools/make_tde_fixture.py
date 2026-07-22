#!/usr/bin/env python3
"""Generate ``tde_full.bak`` and ``tde_full_compressed.bak`` — double-encrypted fixtures.

## Purpose

These fixtures cover the case of a TDE-enabled database that is also backed up
with backup-level ``WITH ENCRYPTION``.  Decrypting them requires **chained
decryption**: first unwrap the backup-level AES layer using the certificate's
RSA private key, then decrypt the TDE database pages using the Database
Encryption Key (DEK) that is also protected by the same certificate.

Both fixtures use the **same** certificate (``TDE_Fixture_Cert``), so a single
PFX file is sufficient for both decryption layers.

## Outputs

    tde_full.bak            — TDE + WITH ENCRYPTION (AES_128, no COMPRESSION)
    tde_full_compressed.bak — TDE + WITH ENCRYPTION (AES_256) + COMPRESSION
                              (MAXTRANSFERSIZE=65537 forces real compression on
                              a TDE database per SQL Server 2016+ behaviour)
    tde_full_cert.pfx       — PKCS#12 certificate + private key (one cert,
                              both decryption layers)

## Certificate

The same ``TDE_Fixture_Cert`` protects both layers:
- the DEK (``CREATE DATABASE ENCRYPTION KEY … ENCRYPTION BY SERVER CERTIFICATE``)
- the backup-level AES key (``BACKUP DATABASE … WITH ENCRYPTION (SERVER CERTIFICATE = …)``)

Exported via :func:`tools.fixture_cert.export_cert_to_pfx` before cleanup.

## Certificate password

    TDE_FULL_CERT_PASSWORD  (see constant below)

Intentionally plain-text — protects only a throwaway test fixture key.

## Setup steps

    1.  Create Master Key in master (if absent).
    2.  Create self-signed certificate TDE_Fixture_Cert.
    3.  Create the test database with a small known table.
    4.  Create Database Encryption Key (AES_128, protected by TDE_Fixture_Cert).
    5.  ALTER DATABASE SET ENCRYPTION ON; wait for state=3.
    6.  BACKUP DATABASE … WITH ENCRYPTION (AES_128) → tde_full.bak.
    7.  BACKUP DATABASE … WITH ENCRYPTION (AES_256) + COMPRESSION,
        MAXTRANSFERSIZE=65537 → tde_full_compressed.bak.
    8.  Export TDE_Fixture_Cert to tde_full_cert.pfx via fixture_cert.
    9.  Drop the database and certificate.

Usage:
    python -m tools.fixture_run tde
    python -m tools.fixture_run all-versions --suite tde
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

DB_NAME = "TDE_Fixture"
CERT_NAME = "TDE_Fixture_Cert"
TDE_FULL_CERT_PASSWORD = "TdeFullCert!Fixture2024"

CONTAINER_BAK            = f"/tmp/{DB_NAME}_full.bak"
CONTAINER_COMPRESSED_BAK = f"/tmp/{DB_NAME}_full_compressed.bak"

FIXTURE_DIR             = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH                = FIXTURE_DIR / "tde_full.bak"
OUT_COMPRESSED_PATH     = FIXTURE_DIR / "tde_full_compressed.bak"
OUT_PFX                 = FIXTURE_DIR / "tde_full_cert.pfx"

_ALL_OUTPUTS = (OUT_PATH, OUT_COMPRESSED_PATH, OUT_PFX)

# Encryption state: 3 = encryption complete.
_WAIT_SQL = (
    "WHILE (SELECT TOP 1 encryption_state "
    "FROM sys.dm_database_encryption_keys "
    f"WHERE database_id = DB_ID('{DB_NAME}')) != 3 "
    "WAITFOR DELAY '00:00:02'"
)


def build_stmts() -> list[str]:
    """SQL statements that set up TDE and produce the two backup outputs.

    Certificate export is handled separately via :func:`export_cert_to_pfx`
    (which runs BACKUP CERTIFICATE as its own step before cleanup).
    """
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
        # Self-signed certificate.  Protects both the DEK and the backup-level key.
        f"CREATE CERTIFICATE [{CERT_NAME}] WITH SUBJECT = 'TDE Fixture Self-Signed Cert'",
        # Create the test database with a small deterministic table.
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "CREATE TABLE probe (id INT PRIMARY KEY, val VARCHAR(40))",
        "INSERT INTO probe VALUES (1, 'hello')",
        # Database Encryption Key — AES_128 is sufficient for a test fixture.
        f"CREATE DATABASE ENCRYPTION KEY WITH ALGORITHM = AES_128 ENCRYPTION BY SERVER CERTIFICATE [{CERT_NAME}]",
        # Enable TDE — starts the background encryption process.
        f"ALTER DATABASE [{DB_NAME}] SET ENCRYPTION ON",
        # Wait for background encryption to reach state 3 (fully encrypted).
        "USE [master]",
        _WAIT_SQL,
        # Step A: backup-level encrypted, no compression.
        # Same cert protects both layers (DEK + backup AES key).
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' "
            f"WITH FORMAT, INIT, COPY_ONLY, "
            f"ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = [{CERT_NAME}])"
        ),
        # Step B: backup-level encrypted + compressed.
        # MAXTRANSFERSIZE=65537 is required to force real XPRESS compression on a
        # TDE database; SQL Server 2016+ silently skips compression without it.
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_COMPRESSED_BAK}' "
            f"WITH FORMAT, INIT, COPY_ONLY, COMPRESSION, MAXTRANSFERSIZE = 65537, "
            f"ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = [{CERT_NAME}])"
        ),
        # Certificate export and cleanup are handled in main() below.
    ]


def build_cleanup_stmts() -> list[str]:
    """SQL statements to drop the database and certificate after cert export."""
    return [
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE",
        f"DROP DATABASE [{DB_NAME}]",
        f"DROP CERTIFICATE [{CERT_NAME}]",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak files")
    args = p.parse_args()

    if not args.force and all(o.exists() for o in _ALL_OUTPUTS):
        print(
            f"skip (all outputs exist): {', '.join(o.name for o in _ALL_OUTPUTS)}",
            file=sys.stderr,
        )
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    print("TDE setup may take 30–60 s while background encryption runs...", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())

    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)

    size = _copy_out(container, CONTAINER_COMPRESSED_BAK, OUT_COMPRESSED_PATH)
    print(f"wrote {OUT_COMPRESSED_PATH} ({size:,} bytes)", file=sys.stderr)

    # Export the certificate before dropping it.  Same PFX decrypts both backups.
    export_cert_to_pfx(
        container, user, password,
        cert_name=CERT_NAME,
        out_pfx=OUT_PFX,
        pvk_password=TDE_FULL_CERT_PASSWORD,
        pfx_password=TDE_FULL_CERT_PASSWORD,
        cert_alias=b"TDE_Fixture_Cert",
    )

    load_and_backup_stmts(container, user, password, build_cleanup_stmts())

    print(f"\nCertificate password: {TDE_FULL_CERT_PASSWORD!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
