#!/usr/bin/env python3
"""Generate ``float_extreme_full.bak`` — rowstore float/real boundary values."""
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

DB_NAME = "FloatExtremeCells"
TABLE = "float_extreme"

EXPECTED_ROWS: dict[int, dict[str, float]] = {
    1: {"f64": 1.7976931348623157e308, "f32": 3.4028235e38},
    2: {"f64": -1.7976931348623157e308, "f32": -3.4028235e38},
    3: {"f64": 2.2250738585072014e-308, "f32": 1.17549435e-38},
    4: {"f64": 0.0, "f32": 0.0},
    5: {"f64": 0.1, "f32": 0.1},
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "float_extreme_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    rows = ",\n    ".join(
        f"({row_id}, CAST({_float_sql(row['f64'])} AS FLOAT), CAST({_float_sql(row['f32'])} AS REAL))"
        for row_id, row in EXPECTED_ROWS.items()
    )
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id  INT NOT NULL PRIMARY KEY CLUSTERED,
    f64 FLOAT NULL,
    f32 REAL NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, f64, f32) VALUES
    {rows}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def _float_sql(value: float) -> str:
    return format(value, ".17E")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {len(EXPECTED_ROWS)} float extreme rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
