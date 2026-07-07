#!/usr/bin/env python3
"""Generate ``native_json_full.bak`` — native JSON column type (Gap D-6, SS2025 only).

## Purpose

The native JSON type (SS2025) stores UTF-8 binary JSON, not an nvarchar string.
It uses ``Latin1_General_100_BIN2_UTF8`` collation internally.  Stored as a
variable-length column in the row.

Failure mode: decoded as UCS-2 nvarchar → corrupt bytes for any non-ASCII
content.  mssqlbak should decode native JSON columns as UTF-8 strings.

## Schema and data

``dbo.json_docs`` — 10-row table with a native JSON column.

    id    INT NOT NULL PRIMARY KEY
    doc   JSON NOT NULL    -- native JSON (SS2025)
    name  VARCHAR(30) NOT NULL

Known documents contain ASCII-only JSON and JSON with multi-byte Unicode (café,
日本語, 😀) to exercise the UTF-8 decoder path.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE``
  - ``ROW_COUNT``
  - ``KNOWN_DOCS``  — list of (id, expected_str) for spot-check rows

Usage (SS2025 only):
    python -m tools.fixture_run native-json
    python -m tools.fixture_run all-versions --suite native-json --version 2025
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

DB_NAME = "NativeJson"
TABLE = "json_docs"
ROW_COUNT = 10

# Each entry: (id, json_string_for_sql_insert, expected_python_str_after_decode)
# We store the expected string as the "doc" field exactly as inserted.
KNOWN_DOCS: list[tuple[int, str, str]] = [
    (1, '{"id":1,"name":"Alice","score":100}', '{"id":1,"name":"Alice","score":100}'),
    (2, '{"id":2,"name":"caf\\u00e9","note":"utf8"}', '{"id":2,"name":"caf\u00e9","note":"utf8"}'),
    (3, '{"id":3,"chars":"\\u65e5\\u672c\\u8a9e"}', '{"id":3,"chars":"\u65e5\u672c\u8a9e"}'),
    (4, '{"id":4,"emoji":"\\ud83d\\ude00"}', '{"id":4,"emoji":"\U0001f600"}'),
    (5, '{"id":5,"arr":[1,2,3],"nested":{"x":42}}', '{"id":5,"arr":[1,2,3],"nested":{"x":42}}'),
    (6, '{"id":6,"v":null}', '{"id":6,"v":null}'),
    (7, '{"id":7,"t":true,"f":false}', '{"id":7,"t":true,"f":false}'),
    (8, '{"id":8,"pi":3.14159}', '{"id":8,"pi":3.14159}'),
    (9, '{"id":9,"long":"' + 'x' * 200 + '"}', '{"id":9,"long":"' + 'x' * 200 + '"}'),
    (10, '{"id":10,"empty":{}}', '{"id":10,"empty":{}}'),
]

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2025")))
OUT_PATH = FIXTURE_DIR / "native_json_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


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
    doc   JSON         NOT NULL,
    name  VARCHAR(30)  NOT NULL
)""",
    ]
    # Insert each known document
    for row_id, json_str, _ in KNOWN_DOCS:
        # Escape single quotes in json_str for SQL
        escaped = json_str.replace("'", "''")
        stmts.append(
            f"INSERT INTO dbo.{TABLE} (id, doc, name)"
            f" VALUES ({row_id}, N'{escaped}', 'row_{row_id}')"
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
    print(f"inserting {ROW_COUNT} native JSON rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
