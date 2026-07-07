#!/usr/bin/env python3
"""Generate ``realworld_numeric_digest_full.bak`` — real-world numeric digest cells."""
from __future__ import annotations

import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import TypedDict

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
    skip_if_exists,
)

DB_NAME = "RealworldNumericDigest"
ROW_COUNT = 1_200
TABLES = ("numeric_rowstore", "numeric_ncci", "numeric_cci")


class ExpectedRow(TypedDict):
    pickup_longitude: float
    pickup_latitude: float
    tax_rate: Decimal
    resource_cost: Decimal
    tipped: bool
    supplier_key: int


EXPECTED_ROWS: dict[int, ExpectedRow] = {
    n: {
        "pickup_longitude": -74.0 + n * 0.0001,
        "pickup_latitude": 40.0 + n * 0.0001,
        "tax_rate": Decimal(n % 25).scaleb(-4),
        "resource_cost": Decimal(n * 12500).scaleb(-4),
        "tipped": bool(n % 2),
        "supplier_key": n % 97,
    }
    for n in range(1, ROW_COUNT + 1)
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "realworld_numeric_digest_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    stmts = [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        *seed_sql(ROW_COUNT),
    ]
    for table in TABLES:
        stmts.extend(_table_stmts(table))
    stmts.extend(
        [
            "USE [master]",
            f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
        ]
    )
    return stmts


def _table_stmts(table: str) -> list[str]:
    create = f"""CREATE TABLE dbo.{table} (
    id               INT          NOT NULL,
    pickup_longitude FLOAT        NOT NULL,
    pickup_latitude  FLOAT        NOT NULL,
    tax_rate         DECIMAL(9,4) NOT NULL,
    resource_cost    MONEY        NOT NULL,
    tipped           BIT          NOT NULL,
    supplier_key     INT          NOT NULL
)"""
    insert = f"""INSERT INTO dbo.{table}
    (id, pickup_longitude, pickup_latitude, tax_rate, resource_cost, tipped, supplier_key)
SELECT
    n,
    CAST(-74.0 + CAST(n AS FLOAT) * 0.0001 AS FLOAT),
    CAST(40.0 + CAST(n AS FLOAT) * 0.0001 AS FLOAT),
    CONVERT(DECIMAL(9,4), CAST(n % 25 AS DECIMAL(9,4)) * 0.0001),
    CONVERT(MONEY, CAST(n AS DECIMAL(19,4)) * 1.25),
    CAST(n % 2 AS BIT),
    CAST(n % 97 AS INT)
FROM (SELECT pk + 1 AS n FROM fkr__seed WHERE pk < {ROW_COUNT}) AS s"""
    if table == "numeric_rowstore":
        return [
            create,
            f"ALTER TABLE dbo.{table} ADD CONSTRAINT pk_{table} PRIMARY KEY CLUSTERED (id)",
            insert,
        ]
    if table == "numeric_ncci":
        return [
            create,
            f"ALTER TABLE dbo.{table} ADD CONSTRAINT pk_{table} PRIMARY KEY CLUSTERED (id)",
            insert,
            f"CREATE NONCLUSTERED COLUMNSTORE INDEX ncci_{table} ON dbo.{table} "
            "(pickup_longitude, pickup_latitude, tax_rate, resource_cost, tipped, supplier_key)",
        ]
    return [
        create,
        insert,
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{table} ON dbo.{table}",
        f"ALTER INDEX cci_{table} ON dbo.{table} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} rows into {len(TABLES)} numeric digest tables")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
