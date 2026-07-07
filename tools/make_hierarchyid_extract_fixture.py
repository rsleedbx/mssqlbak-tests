#!/usr/bin/env python3
"""Generate ``hierarchyid_extract_full.bak`` — hierarchyid column extraction (Gap D-4).

## Purpose

``hierarchyid`` is a variable-length bit-packed binary (1–892 bytes) that
encodes a path like ``/``, ``/1/``, ``/1/2/``, ``/1/2/3/``.  It is declared
as an opaque CLR type and stored as raw bytes in the record.

SQL Server's built-in ``hierarchyid`` methods (``ToString()``, ``GetLevel()``)
decode the internal byte format.  mssqlbak should surface the raw bytes
(``bytes`` object in Python) without crashing; it must not try to interpret the
bit-packed layout as a scalar numeric type.

Failure modes:
  - Decoded as text → garbled bytes.
  - Decoded as an integer → wrong value.
  - Error raised because the type code is unrecognised.
  - Truncated (wrong length computed).

## Schema and data

``dbo.org`` — (id INT PK, node hierarchyid NOT NULL, path AS node.ToString() PERSISTED)

Known nodes and their expected byte representations:

  id  path       GetLevel()
  1   /           0  (root, 1 byte: 0x58)
  2   /1/         1
  3   /2/         1
  4   /1/1/       2
  5   /1/2/       2
  6   /1/1/1/     3

The ``path`` column (persisted computed string) is included so the test can
verify the correct row by human-readable path string, independent of raw bytes.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``    — database name used in the backup
  - ``TABLE``      — table name
  - ``ROW_COUNT``  — total rows inserted (6)
  - ``KNOWN_PATHS``— list of (id, path_string) tuples

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run hierarchyid-extract
    python -m tools.fixture_run all-versions --suite hierarchyid-extract

Direct (set env vars manually):
    python -m tools.make_hierarchyid_extract_fixture
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
)

DB_NAME = "HierarchyidExtract"
TABLE = "org"
ROW_COUNT = 6

# (id, human-readable path string as returned by hierarchyid.ToString())
KNOWN_PATHS = [
    (1, "/"),
    (2, "/1/"),
    (3, "/2/"),
    (4, "/1/1/"),
    (5, "/1/2/"),
    (6, "/1/1/1/"),
]

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "hierarchyid_extract_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return statements that create and populate the hierarchyid table."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id   INT          NOT NULL PRIMARY KEY CLUSTERED,
    node hierarchyid  NOT NULL,
    path AS node.ToString() PERSISTED
)""",
        f"""INSERT INTO dbo.{TABLE} (id, node) VALUES
    (1, hierarchyid::GetRoot()),
    (2, hierarchyid::Parse('/1/')),
    (3, hierarchyid::Parse('/2/')),
    (4, hierarchyid::Parse('/1/1/')),
    (5, hierarchyid::Parse('/1/2/')),
    (6, hierarchyid::Parse('/1/1/1/'))""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} hierarchyid rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
