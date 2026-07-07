#!/usr/bin/env python3
"""Generate ``alias_types_full.bak`` — user-defined alias scalar types.

AdventureWorks defines scalar alias types such as ``Flag`` and ``NameStyle``
over ``bit``.  Cell-level comparison must canonicalize those columns as their
underlying system type, not as the alias type name.
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

DB_NAME = "AliasTypes"
TABLE = "alias_probe"

EXPECTED_ROWS: dict[int, dict[str, object]] = {
    1: {
        "is_active": True,
        "name_style": False,
        "random_flag_123": True,
        "float_alias": 1.5,
        "money_alias": "12.3400",
        "display_name": "Alice",
        "account_number": 1001,
        "external_id": "11111111-1111-1111-1111-111111111111",
    },
    2: {
        "is_active": False,
        "name_style": True,
        "random_flag_123": False,
        "float_alias": 2.25,
        "money_alias": "0.0100",
        "display_name": "Bob",
        "account_number": 1002,
        "external_id": "22222222-2222-2222-2222-222222222222",
    },
    3: {
        "is_active": None,
        "name_style": None,
        "random_flag_123": None,
        "float_alias": None,
        "money_alias": None,
        "display_name": "Null Flags",
        "account_number": 1003,
        "external_id": "33333333-3333-3333-3333-333333333333",
    },
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "alias_types_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    rows = []
    for row_id, expected in EXPECTED_ROWS.items():
        is_active = _bit_sql(expected["is_active"])
        name_style = _bit_sql(expected["name_style"])
        random_flag_123 = _bit_sql(expected["random_flag_123"])
        float_alias = _num_sql(expected["float_alias"])
        money_alias = _num_sql(expected["money_alias"])
        display_name = _str_sql(expected["display_name"])
        account_number = expected["account_number"]
        external_id = _str_sql(expected["external_id"])
        rows.append(
            f"({row_id}, {is_active}, {name_style}, {random_flag_123}, "
            f"{float_alias}, {money_alias}, {display_name}, {account_number}, "
            f"CONVERT(uniqueidentifier, {external_id}))"
        )

    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        "CREATE TYPE dbo.Flag FROM bit NULL",
        "CREATE TYPE dbo.NameStyle FROM bit NULL",
        "CREATE TYPE dbo.RandomFlag123 FROM bit NULL",
        "CREATE TYPE dbo.FloatAlias FROM float NULL",
        "CREATE TYPE dbo.MoneyAlias FROM money NULL",
        "CREATE TYPE dbo.PersonName FROM nvarchar(50) NULL",
        "CREATE TYPE dbo.AccountNumber FROM int NULL",
        "CREATE TYPE dbo.ExternalId FROM uniqueidentifier NULL",
        f"""CREATE TABLE dbo.{TABLE} (
    id             INT                  NOT NULL PRIMARY KEY CLUSTERED,
    is_active      dbo.Flag             NULL,
    name_style     dbo.NameStyle        NULL,
    random_flag_123 dbo.RandomFlag123   NULL,
    float_alias     dbo.FloatAlias      NULL,
    money_alias     dbo.MoneyAlias      NULL,
    display_name   dbo.PersonName       NULL,
    account_number dbo.AccountNumber    NULL,
    external_id    dbo.ExternalId       NULL
)""",
        f"""INSERT INTO dbo.{TABLE}
    (
        id,
        is_active,
        name_style,
        random_flag_123,
        float_alias,
        money_alias,
        display_name,
        account_number,
        external_id
    )
VALUES
    {", ".join(rows)}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def _bit_sql(value: object) -> str:
    if value is None:
        return "NULL"
    return "1" if value else "0"


def _str_sql(value: object) -> str:
    if value is None:
        return "NULL"
    return "N'" + str(value).replace("'", "''") + "'"


def _num_sql(value: object) -> str:
    if value is None:
        return "NULL"
    return str(value)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {len(EXPECTED_ROWS)} alias-type rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
