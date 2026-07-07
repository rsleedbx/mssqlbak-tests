#!/usr/bin/env python3
"""Generate ``rowstore_hash_pii_full.bak`` — binary/hash PII-shaped cells."""
from __future__ import annotations

import argparse
import hashlib
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

DB_NAME = "RowstoreHashPii"
TABLE = "hash_pii_probe"
ROW_COUNT = 4

_HASH_BYTES: dict[int, bytes] = {
    1: bytes.fromhex("00" * 32),
    2: bytes.fromhex("ff" * 32),
    3: hashlib.sha256("CorrectHorseBatteryStaple".encode("utf-16-le")).digest(),
}
_SSN_BYTES: dict[int, bytes] = {
    1: bytes.fromhex("00112233445566778899aabbccddeeff"),
    2: bytes.fromhex("ffeeddccbbaa99887766554433221100"),
    3: hashlib.sha256(b"111-22-3333").digest()[:16],
}
_CREDIT_BYTES: dict[int, bytes] = {
    1: bytes.fromhex("0123456789abcdef" * 4),
    2: bytes.fromhex("fedcba9876543210" * 4),
    3: hashlib.sha256(b"4111111111111111").digest(),
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


EXPECTED_HASH_SHA256 = {
    row_id: _sha256(value)
    for row_id, value in _HASH_BYTES.items()
}
EXPECTED_SSN_SHA256 = {
    row_id: _sha256(value)
    for row_id, value in _SSN_BYTES.items()
}
EXPECTED_CREDIT_SHA256 = {
    row_id: _sha256(value)
    for row_id, value in _CREDIT_BYTES.items()
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "rowstore_hash_pii_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    return [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id                 INT            NOT NULL PRIMARY KEY CLUSTERED,
    hashed_password    BINARY(32)     NULL,
    ssn_cipher         VARBINARY(16)  NULL,
    credit_card_cipher VARBINARY(MAX) NULL
)""",
        f"""INSERT INTO dbo.{TABLE}
    (id, hashed_password, ssn_cipher, credit_card_cipher)
VALUES
    (1,
     0x{'00' * 32},
     0x00112233445566778899AABBCCDDEEFF,
     0x{'0123456789ABCDEF' * 4}),
    (2,
     0x{'FF' * 32},
     0xFFEEDDCCBBAA99887766554433221100,
     0x{'FEDCBA9876543210' * 4}),
    (3,
     HASHBYTES('SHA2_256', CAST(N'CorrectHorseBatteryStaple' AS NVARCHAR(100))),
     SUBSTRING(HASHBYTES('SHA2_256', CAST('111-22-3333' AS VARCHAR(20))), 1, 16),
     HASHBYTES('SHA2_256', CAST('4111111111111111' AS VARCHAR(20)))),
    (4, NULL, NULL, NULL)""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} rowstore binary/hash rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
