#!/usr/bin/env python3
"""Generate ``xtp_rich_full.bak`` — richer memory-optimized table coverage."""
from __future__ import annotations

import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "XtpRich"
FIXED_TABLE = "xtp_rich_fixed"
MIXED_TABLE = "xtp_rich_mixed"

FIXED_EXPECTED: dict[int, tuple[int, int, Decimal]] = {
    1: (100, 1, Decimal("12.3400")),
    2: (200, 0, Decimal("-56.7800")),
    3: (999_999_999_999, 255, Decimal("0.0000")),
}

MIXED_EXPECTED: dict[int, tuple[str | None, str | None]] = {
    1: ("Alfa", "short note"),
    2: (None, None),
    3: ("Omega", "wide memory optimized row"),
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "xtp_rich_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    fixed_rows = ",\n    ".join(
        f"({id_}, {score}, {flag}, CONVERT(MONEY, {amount}), "
        f"CONVERT(UNIQUEIDENTIFIER, '{_guid_for(id_)}'))"
        for id_, (score, flag, amount) in FIXED_EXPECTED.items()
    )
    mixed_rows = []
    for id_, (label, note) in MIXED_EXPECTED.items():
        label_sql = f"N'{label}'" if label is not None else "NULL"
        note_sql = f"N'{note}'" if note is not None else "NULL"
        mixed_rows.append(f"({id_}, {label_sql}, {note_sql})")

    return [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_XTP] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'xtp_rich_data',
    FILENAME = N'/var/opt/mssql/data/xtp_rich_data'
) TO FILEGROUP [FG_XTP]""",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{FIXED_TABLE} (
    id     INT              NOT NULL,
    score  BIGINT           NOT NULL,
    flag   TINYINT          NOT NULL,
    amount MONEY            NOT NULL,
    row_id UNIQUEIDENTIFIER NOT NULL,
    CONSTRAINT pk_{FIXED_TABLE} PRIMARY KEY NONCLUSTERED (id),
    INDEX ix_{FIXED_TABLE}_score NONCLUSTERED (score)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.{FIXED_TABLE} (id, score, flag, amount, row_id) VALUES\n    {fixed_rows}",
        f"""CREATE TABLE dbo.{MIXED_TABLE} (
    id    INT           NOT NULL,
    label NVARCHAR(32)  NULL,
    note  NVARCHAR(128) NULL,
    CONSTRAINT pk_{MIXED_TABLE} PRIMARY KEY NONCLUSTERED (id),
    INDEX ix_{MIXED_TABLE}_label NONCLUSTERED (label)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.{MIXED_TABLE} (id, label, note) VALUES\n    " + ",\n    ".join(mixed_rows),
        "CHECKPOINT",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def _guid_for(id_: int) -> str:
    return f"00000000-0000-0000-0000-{id_:012d}"


def main(force: bool = False) -> int:
    if skip_if_exists(OUT_PATH, force=force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"creating XTP rich fixture: {len(FIXED_EXPECTED)} fixed rows, {len(MIXED_EXPECTED)} mixed rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
