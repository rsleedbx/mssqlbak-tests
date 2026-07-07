#!/usr/bin/env python3
"""Generate ``vector_full.bak`` — VECTOR column type (Gap D-5, SS2025 only).

## Purpose

The VECTOR type (SS2025) stores a fixed-dimension array of float32 values in a
proprietary binary format: a 4-byte header (type=0x53, number_of_dimensions in
little-endian uint16, element_type=0x03 for float32) followed by the packed
float32 array.  Cannot be used in sql_variant or as a key column.

Failure mode: unknown binary header → garbage or crash when mssqlbak
encounters a VECTOR column in a SS2025 .bak file.

mssqlbak should surface the raw bytes (or a list of floats) without crashing.

## Schema and data

``dbo.vec_tbl`` — 10-row table with a VECTOR(3) column plus known float values.

    id    INT NOT NULL PRIMARY KEY
    name  VARCHAR(20) NOT NULL
    v     VECTOR(3) NOT NULL    — 3-dimensional float32 vector

Known vectors (id 1–5):
  1: [1.0, 2.0, 3.0]
  2: [0.0, 0.0, 0.0]
  3: [-1.5, 2.5, -3.5]
  4: [1.0e10, -1.0e10, 3.14]
  5: [0.1, 0.2, 0.3]

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE``
  - ``ROW_COUNT``
  - ``KNOWN_VECTORS``  — list of (id, [f0, f1, f2]) tuples for the first 5 rows

Usage (SS2025 only):
    python -m tools.fixture_run vector
    python -m tools.fixture_run all-versions --suite vector --version 2025
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
    seed_sql,
    skip_if_server_older_than,
)

DB_NAME = "VectorFixture"
TABLE = "vec_tbl"
ROW_COUNT = 10

# Known vectors for first ROW_COUNT rows: (id, [x, y, z])
KNOWN_VECTORS = [
    (1, [1.0, 2.0, 3.0]),
    (2, [0.0, 0.0, 0.0]),
    (3, [-1.5, 2.5, -3.5]),
    (4, [1.0e10, -1.0e10, 3.14]),
    (5, [0.1, 0.2, 0.3]),
    (6, [100.0, 200.0, 300.0]),
    (7, [-0.001, 0.001, 0.0]),
    (8, [1.0, 1.0, 1.0]),
    (9, [42.0, 43.0, 44.0]),
    (10, [3.14159, 2.71828, 1.41421]),
]

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2025")))
OUT_PATH = FIXTURE_DIR / "vector_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _vec_literal(floats: list[float]) -> str:
    """Return a SQL VECTOR literal string like '[1.0, 2.0, 3.0]'."""
    return "[" + ", ".join(repr(f) for f in floats) + "]"


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id    INT          NOT NULL PRIMARY KEY CLUSTERED,
    name  VARCHAR(20)  NOT NULL,
    v     VECTOR(3)    NOT NULL
)""",
    ]
    # Insert known vectors as individual VALUES rows
    for row_id, floats in KNOWN_VECTORS:
        vec_lit = _vec_literal(floats)
        stmts.append(
            f"INSERT INTO dbo.{TABLE} (id, name, v) VALUES ({row_id}, 'pt_{row_id}', '{vec_lit}')"
        )
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_server_older_than(2025):
        return 0

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} VECTOR(3) rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
