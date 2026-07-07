#!/usr/bin/env python3
"""Generate ``surrogate_pairs_full.bak`` — nvarchar with UTF-16 surrogate pairs (Gap G-2).

## Purpose

``nvarchar`` stores text as **UTF-16 little-endian**.  Code points > U+FFFF
(supplementary characters) occupy **4 bytes** — two UTF-16 code units forming
a surrogate pair (high surrogate U+D800–U+DBFF, low surrogate U+DC00–U+DFFF).

A UTF-16 decoder that treats every 2-byte unit as a complete code point will
split each surrogate pair into two broken code units, producing corrupt strings.
Python's ``bytes.decode("utf-16-le")`` correctly handles surrogates.

## Schema and data

``dbo.sc_tbl`` — (id INT PRIMARY KEY, s NVARCHAR(40))

id 1 — U+20000 (𠀀, rare CJK Unified Ideograph extension B, 4-byte UTF-16)
id 2 — U+1F600 (😀, grinning face emoji, 4-byte UTF-16)
id 3 — U+1F1EC + U+1F1E7 (🇬🇧, flag emoji, two surrogate pairs = 8 bytes)
id 4 — N'normal ascii string' (no surrogates — control row)
id 5 — NULL

## Exported constants (imported by the coverage test)

  - ``DB_NAME``         — database name used in the backup
  - ``ROW_COUNT``       — total rows inserted (5)
  - ``EXPECTED_VALUES`` — dict[id, expected Python str] for non-null rows

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run surrogate-pairs
    python -m tools.fixture_run all-versions --suite surrogate-pairs

Direct (set env vars manually):
    python -m tools.make_surrogate_pairs_fixture
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

DB_NAME = "SurrogatePairs"
ROW_COUNT = 5

# Expected decoded Python strings per id (None = SQL NULL).
EXPECTED_VALUES: dict[int, str | None] = {
    1: "\U00020000",          # 𠀀 rare CJK (U+20000)
    2: "\U0001F600",          # 😀 grinning face
    3: "\U0001F1EC\U0001F1E7",  # 🇬🇧 GB flag (two surrogate pairs)
    4: "normal ascii string",
    5: None,
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "surrogate_pairs_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _nchar_literal(s: str | None) -> str:
    """Return a T-SQL N'...' literal for the given Python string, or NULL."""
    if s is None:
        return "NULL"
    # Escape single quotes; SQL Server N'...' literals accept UTF-16 surrogates
    escaped = s.replace("'", "''")
    return f"N'{escaped}'"


def build_stmts() -> list[str]:
    """Return statements that create and populate the surrogate-pairs table."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        """CREATE TABLE dbo.sc_tbl (
    id INT NOT NULL PRIMARY KEY CLUSTERED,
    s  NVARCHAR(40) COLLATE Latin1_General_100_CI_AS_SC NULL
)""",
    ]
    for row_id, val in EXPECTED_VALUES.items():
        stmts.append(
            f"INSERT INTO dbo.sc_tbl (id, s) VALUES ({row_id}, {_nchar_literal(val)})"
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

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} rows with surrogate-pair nvarchar values …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
