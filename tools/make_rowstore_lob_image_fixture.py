#!/usr/bin/env python3
"""Generate ``rowstore_lob_image_full.bak`` — rowstore LOB/image cells."""
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

DB_NAME = "RowstoreLobImageCells"
TABLE = "lob_image_probe"
ROW_COUNT = 3


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


_IMAGE_BYTES: dict[int, bytes] = {
    1: bytes.fromhex("ab") * 4096,
    2: bytes.fromhex("cd") * 8192,
}
_BIN_BYTES: dict[int, bytes] = {
    1: bytes.fromhex("ef") * 9000,
    2: bytes.fromhex("01234567") * 2048,
}
_TEXT_VALUES: dict[int, str] = {
    1: "alpha-" + ("x" * 9000),
    2: "beta-" + ("yz" * 4096),
}
_WIDE_VALUES: dict[int, str] = {
    1: "wide-" + (chr(0x03A9) * 1024),
    2: "wide-" + (chr(0x263A) * 1024),
}

EXPECTED_IMAGE_SHA256 = {row_id: _sha256(value) for row_id, value in _IMAGE_BYTES.items()}
EXPECTED_BIN_SHA256 = {row_id: _sha256(value) for row_id, value in _BIN_BYTES.items()}
EXPECTED_TEXT_SHA256 = {
    row_id: _sha256(value.encode("utf-8"))
    for row_id, value in _TEXT_VALUES.items()
}
EXPECTED_WIDE_SHA256 = {
    row_id: _sha256(value.encode("utf-16-le"))
    for row_id, value in _WIDE_VALUES.items()
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "rowstore_lob_image_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id              INT            NOT NULL PRIMARY KEY CLUSTERED,
    photo_image     IMAGE          NULL,
    photo_varbinary VARBINARY(MAX) NULL,
    text_payload    VARCHAR(MAX)   NULL,
    wide_payload    NVARCHAR(MAX)  NULL
)""",
        f"""INSERT INTO dbo.{TABLE}
    (id, photo_image, photo_varbinary, text_payload, wide_payload)
VALUES
    (1,
     CONVERT(IMAGE, CONVERT(VARBINARY(MAX), REPLICATE(CAST('AB' AS VARCHAR(MAX)), 4096), 2)),
     CONVERT(VARBINARY(MAX), REPLICATE(CAST('EF' AS VARCHAR(MAX)), 9000), 2),
     'alpha-' + REPLICATE(CAST('x' AS VARCHAR(MAX)), 9000),
     N'wide-' + REPLICATE(CAST(NCHAR(0x03A9) AS NVARCHAR(MAX)), 1024)),
    (2,
     CONVERT(IMAGE, CONVERT(VARBINARY(MAX), REPLICATE(CAST('CD' AS VARCHAR(MAX)), 8192), 2)),
     CONVERT(VARBINARY(MAX), REPLICATE(CAST('01234567' AS VARCHAR(MAX)), 2048), 2),
     'beta-' + REPLICATE(CAST('yz' AS VARCHAR(MAX)), 4096),
     N'wide-' + REPLICATE(CAST(NCHAR(0x263A) AS NVARCHAR(MAX)), 1024)),
    (3, NULL, NULL, NULL, NULL)""",
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
    print(f"inserting {ROW_COUNT} rowstore LOB/image rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
