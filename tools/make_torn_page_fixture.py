#!/usr/bin/env python3
"""Generate ``torn_page_full.bak`` — PAGE_VERIFY TORN_PAGE_DETECTION regression fixture.

## Purpose

SQL Server databases configured with ``PAGE_VERIFY TORN_PAGE_DETECTION``
(the SQL Server 2000 default, preserved until pages are rewritten) protect
against partial writes by overwriting the low 2 bits of the last byte of each
512-byte sector with an alternating signature and saving the displaced bits in
the 4-byte ``m_tornBits`` page header field.

Before commit ``2ed478b``, mssqlbak never reversed this substitution.  The low
2 bits of 15 slot-array entries and fixed-length column bytes per page were one
bit too high, causing misaligned record offsets that silently dropped rows.  On
``CreditBackup100.bak`` (a 500 MB financial sample database) the bug suppressed
9,303 rows (1,647,271 returned vs. 1,656,574 correct).

This fixture creates a small database with ``PAGE_VERIFY TORN_PAGE_DETECTION``
and verifies that ``mssqlbak.pages.restore_torn_page`` is applied so that no
rows are lost and all values are extracted correctly.

## Table schema

    CREATE TABLE dbo.tpd_probe (
        id     INT          NOT NULL PRIMARY KEY CLUSTERED,
        label  VARCHAR(40)  NULL,
        score  INT          NULL
    )

Rows are inserted AFTER setting ``PAGE_VERIFY TORN_PAGE_DETECTION`` so the data
pages land on disk (and in the backup image) with the torn-page signature active.

## Exported constants

  - ``DB_NAME``    — database name
  - ``TABLE``      — table name ("tpd_probe")
  - ``ROW_COUNT``  — number of rows inserted
  - ``LABEL_FN``   — callable(id) → expected label (or None if NULL)
  - ``SCORE_FN``   — callable(id) → expected score (or None if NULL)

Usage:
    python -m tools.fixture_run torn-page
    python -m tools.fixture_run all-versions --suite torn-page
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import os

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "TornPageFixture"
TABLE = "tpd_probe"
ROW_COUNT = 300

# Resolved at import time so that all-versions subprocesses pick up FIXTURE_DIR.
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
_OUT_PATH = _FIXTURE_DIR / "torn_page_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def LABEL_FN(id_: int) -> str | None:  # noqa: N802
    """Expected label for row *id_*; None for every 7th row (NULL probe)."""
    if id_ % 7 == 0:
        return None
    return f"Label-{id_:04d}"


def SCORE_FN(id_: int) -> int | None:  # noqa: N802
    """Expected score for row *id_*; None for every 11th row (NULL probe)."""
    if id_ % 11 == 0:
        return None
    return id_ * id_


def build_stmts() -> list[str]:
    """Return T-SQL statements that create and back up the fixture database."""
    # Build VALUES list for 300 rows.
    values_parts: list[str] = []
    for i in range(1, ROW_COUNT + 1):
        lbl = f"N'Label-{i:04d}'" if i % 7 != 0 else "NULL"
        scr = str(i * i) if i % 11 != 0 else "NULL"
        values_parts.append(f"({i}, {lbl}, {scr})")
    values_clause = ",\n    ".join(values_parts)

    container_bak = f"/tmp/{DB_NAME}_full.bak"
    return [
        # Drop and recreate the database to guarantee a clean slate.
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        # Switch to TORN_PAGE_DETECTION *before* creating tables or inserting
        # rows so that all subsequent data-page writes carry the TPD signature.
        f"ALTER DATABASE [{DB_NAME}] SET PAGE_VERIFY TORN_PAGE_DETECTION WITH NO_WAIT",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id     INT         NOT NULL PRIMARY KEY CLUSTERED,
    label  VARCHAR(40) NULL,
    score  INT         NULL
)""",
        f"INSERT INTO dbo.{TABLE} (id, label, score) VALUES\n    {values_clause}",
        # CHECKPOINT flushes dirty data pages to disk with the TPD signature
        # so the backup image captures pages that have been through the
        # torn-page write path.
        "CHECKPOINT",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{container_bak}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main(force: bool = False) -> int:
    if skip_if_exists(_OUT_PATH, force=force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"creating torn-page fixture: {ROW_COUNT} rows with PAGE_VERIFY TORN_PAGE_DETECTION")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, _OUT_PATH)
    print(f"wrote {_OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
