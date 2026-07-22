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
    8.  Python: call :func:`tools.fixture_cert.export_cert_to_pfx` — runs BACKUP
        CERTIFICATE inside the container, copies ``.cer`` and ``.pvk`` out, and
        writes the combined PKCS#12 ``.pfx`` file.
    9.  SQL: Drop the database and certificate.

Usage:
    python -m tools.fixture_run tde-page
    python -m tools.fixture_run all-versions --suite tde-page
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

DB_NAME = "TDE_Page_Fixture"
CERT_NAME = "TDE_Page_Cert"
CERT_PASSWORD = "TdePageCert!Fixture2024"
CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
CONTAINER_PLAIN_BAK = f"/tmp/{DB_NAME}_plain.bak"

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
        # Certificate export is handled by export_cert_to_pfx() in main(),
        # which runs BACKUP CERTIFICATE before the cleanup below.
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

    load_and_backup_stmts(container, user, password, build_stmts())

    size_bak = _copy_out(container, CONTAINER_BAK, OUT_BAK)
    print(f"wrote {OUT_BAK} ({size_bak:,} bytes)", file=sys.stderr)

    size_plain = _copy_out(container, CONTAINER_PLAIN_BAK, OUT_PLAIN_BAK)
    print(f"wrote {OUT_PLAIN_BAK} ({size_plain:,} bytes)", file=sys.stderr)

    # Export certificate before dropping it.
    export_cert_to_pfx(
        container, user, password,
        cert_name=CERT_NAME,
        out_pfx=OUT_PFX,
        pvk_password=CERT_PASSWORD,
        pfx_password=CERT_PASSWORD,
        cert_alias=b"TDE_Page_Cert",
    )

    load_and_backup_stmts(container, user, password, build_cleanup_stmts())

    print(f"\nCertificate password: {CERT_PASSWORD!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
