#!/usr/bin/env python3
"""Generate ``tde_full.bak`` — Transparent Data Encryption detect-and-fail fixture (Gap F-1).

## Purpose

Gap F-1 verifies that mssqlbak detects a TDE-encrypted backup and raises a clean
:exc:`mssqlbak.errors.EncryptedBackupError` instead of crashing or emitting
garbage values.

TDE encrypts every database page with AES before writing to disk.  A backup of
a TDE-enabled database contains ciphertext where page data should be; mssqlbak
cannot read those pages without the Database Encryption Key (DEK) and the
server certificate that protects it.

## Setup steps (executed via sqlcmd)

    1. Create a Master Key in master (if not already present).
    2. Create a self-signed certificate for TDE.
    3. Create the test database.
    4. Create a Database Encryption Key on the test database.
    5. Enable TDE:  ALTER DATABASE … SET ENCRYPTION ON.
    6. Wait until sys.dm_database_encryption_keys reports state=3 (encrypted).
    7. Backup to disk.

The certificate and master key are NOT backed up — this fixture is
intentionally unrestorable.  The test only needs to verify that mssqlbak
raises the right error, not that it can decrypt anything.

## Exported constants

    DB_NAME     — database name ("TDE_Fixture")
    CONTAINER_BAK — path inside container where the bak lands

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

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "TDE_Fixture"
CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "tde_full.bak"

# Encryption state: 3 = encryption complete.
_WAIT_SQL = (
    "WHILE (SELECT TOP 1 encryption_state "
    "FROM sys.dm_database_encryption_keys "
    f"WHERE database_id = DB_ID('{DB_NAME}')) != 3 "
    "WAITFOR DELAY '00:00:02'"
)


def build_stmts() -> list[str]:
    """SQL statements that set up TDE and produce the backup.

    Each string is a single batch (no GO needed — executed as separate
    sqlcmd commands through fixture_utils._run_sql / mssql_python).
    """
    return [
        # Tear down any leftover database from a prior run.
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        # Master key: required before creating a certificate.
        # OPEN is a no-op if already exists and correct; CREATE uses IF NOT EXISTS.
        """USE [master]""",
        """IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'TdeMasterKey!2024'""",
        # Certificate used to protect the DEK.
        """IF NOT EXISTS (SELECT 1 FROM sys.certificates WHERE name = 'TDE_Fixture_Cert')
    CREATE CERTIFICATE TDE_Fixture_Cert WITH SUBJECT = 'TDE Fixture Self-Signed Cert'""",
        # Create the test database (minimal — just one tiny table).
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "CREATE TABLE probe (id INT PRIMARY KEY, val VARCHAR(40))",
        "INSERT INTO probe VALUES (1, 'hello')",
        # Database Encryption Key — AES_128 is sufficient for a test fixture.
        "CREATE DATABASE ENCRYPTION KEY WITH ALGORITHM = AES_128 ENCRYPTION BY SERVER CERTIFICATE TDE_Fixture_Cert",
        # Enable TDE — starts the background encryption process.
        f"ALTER DATABASE [{DB_NAME}] SET ENCRYPTION ON",
        # Wait for background encryption to reach state 3 (fully encrypted).
        # This runs in master context so DB_ID() resolves correctly.
        "USE [master]",
        _WAIT_SQL,
        # Backup with encryption: this makes the backup file actually contain
        # encrypted page data (AES_128) rather than decrypted plaintext.
        # Without the certificate mssqlbak cannot read any page in this backup.
        (
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' "
            "WITH FORMAT, INIT, COPY_ONLY, "
            "ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = TDE_Fixture_Cert)"
        ),
        # Cleanup: drop the database so future runs start fresh.
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE",
        f"DROP DATABASE [{DB_NAME}]",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    print("TDE setup may take 30–60 s while background encryption runs...", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
