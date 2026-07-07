#!/usr/bin/env python3
"""Build minimal catalog snapshot ``.bak`` for a SQL Server version matrix.

Creates a tiny database (one heap table) on the target engine and backs it up
for cross-version catalog object-id comparison (Guess G21, G14).

Usage::

    FIXTURE_DBA_PASSWORD=... python -m tools.make_catalog_fixture --engine 2012
    FIXTURE_DBA_PASSWORD=... python -m tools.make_catalog_fixture --engine 2022

Output: ``tests/fixtures/catalog_ss{engine}.bak``

For MSSQLBAK v1 header inspection (G01), also run on SQL Server 2012 with
``--compressed`` to produce ``tests/fixtures/mssqlbak_v1_inspect.bak``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent

ENGINES = ("2012", "2016", "2019", "2022")


def _db_name(engine: str) -> str:
    return f"CatalogSS{engine}"


def build_sql(engine: str, *, backup_compression: bool = False) -> str:
    db = _db_name(engine)
    compression = " WITH (DATA_COMPRESSION = PAGE)" if backup_compression else ""
    return f"""
USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE dbo.cat_probe (
  id int NOT NULL PRIMARY KEY CLUSTERED,
  payload varchar(100) NOT NULL
){compression};
GO
INSERT INTO dbo.cat_probe (id, payload) VALUES (1, N'alpha'), (2, N'beta'), (3, N'gamma');
GO
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate catalog version-matrix .bak")
    parser.add_argument("--engine", choices=ENGINES, required=True)
    parser.add_argument(
        "--compressed",
        action="store_true",
        help="PAGE-compress cat_probe (for mssqlbak_v1_inspect.bak on 2012)",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    db = _db_name(args.engine)
    if args.out is not None:
        out = args.out
    elif args.compressed and args.engine == "2012":
        out = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022"))) / "mssqlbak_v1_inspect.bak"
    else:
        out = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022"))) / f"catalog_ss{args.engine}.bak"
    from tools.make_fixture import generate_fixture

    return generate_fixture(
        db,
        build_sql(args.engine, backup_compression=args.compressed),
        out,
    )


if __name__ == "__main__":
    sys.exit(main())
