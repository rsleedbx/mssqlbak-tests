#!/usr/bin/env python3
"""Generate ``heapcoverage_large.bak`` — clustered + heap table pair.

## Purpose (FIXTURE_GAPS.md Gap 1)

Real-world samples (``EmployeeCaseStudySampleDB2012.bak``,
``IndexInternals2008.bak``) expose an IAM traversal bug that drops rows from
heap tables when more than one IAM interval is present.  The existing
``tt_heap`` fixture has 4 rows (one page, one IAM interval) so the bug is
never triggered.

This fixture creates two tables with identical data:

  - ``dbo.heap_clustered``  — clustered index (control; always passes)
  - ``dbo.heap_plain``      — true heap (no index; triggers the bug at scale)

A passing test verifies row counts match; any divergence isolates the IAM
traversal bug immediately.

## Scaling

``--rows N`` controls table size.  Defaults:

  - ``1_000``   in ``all-versions`` suite (fast, still tests multi-page)
  - ``50_000``  recommended for reproducing the IAM bug (multiple extents)
  - ``80_000``  matches the real-world sample that exposed the bug

## Template notes (for future generators)

This script is the reference implementation of the next-gen fixture style.
Follow this pattern for all new generators:

  1. Import ONLY from ``tools.fixture_utils`` — not from ``tools.make_fixture``
     or other generator scripts.
  2. ``DB_NAME`` is a module-level constant; output path is computed by
     ``_out_path(rows)`` using ``FIXTURE_DIR`` (set by ``fixture_run``).
  3. ``build_sql()`` is a pure function; it receives all parameters explicitly
     and returns a SQL string.  No side effects.
  4. ``main()`` uses argparse, calls ``skip_if_exists`` first, then
     ``fixture_credentials()``.  Exit via ``return 0 / return 1``.
  5. Register the command in ``fixture_run.py`` (``_COMMANDS`` +
     ``_ALL_VERSIONS_SUITE``).

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run heap-scale
    python -m tools.fixture_run --fixture-dir tests/fixtures_2017 heap-scale --rows 50000

Direct (set env vars manually):
    python -m tools.make_heap_scale_fixture --rows 50000
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
    skip_if_exists,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_NAME = "HeapScaleCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"


FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

# Row count used by the all-versions suite.  Small enough to be fast but
# large enough to span multiple pages (> 1 page at ~200 bytes/row).
DEFAULT_ROWS = 1_000


def _out_path(rows: int) -> Path:
    """Return the output BAK path for *rows* rows.

    Default row count → ``heapcoverage_large.bak`` (stable name, used by tests).
    Any other count   → ``heapcoverage_large_{rows}.bak`` (avoids overwriting).
    """
    if rows == DEFAULT_ROWS:
        return FIXTURE_DIR / "heapcoverage_large.bak"
    return FIXTURE_DIR / f"heapcoverage_large_{rows}.bak"


# ---------------------------------------------------------------------------
# SQL builder  (pure function — no side effects)
# ---------------------------------------------------------------------------

def build_stmts(rows: int) -> list[str]:
    """Return DDL + DML + BACKUP statements for *rows* rows per table.

    Uses fkr__seed integer table (INSERT-SELECT doubling) instead of a
    cross-join CTE.  No GO separators — each element is one T-SQL statement
    ready for execute_statements().
    """
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
  ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(rows)
    stmts += [
        # Control table: clustered index (always extracts correctly)
        """CREATE TABLE dbo.heap_clustered (
    id    INT          NOT NULL PRIMARY KEY CLUSTERED,
    val   BIGINT       NOT NULL,
    label NVARCHAR(60) NOT NULL
)""",
        # Test table: true heap (no index) — triggers IAM traversal bug at scale
        """CREATE TABLE dbo.heap_plain (
    id    INT          NOT NULL,
    val   BIGINT       NOT NULL,
    label NVARCHAR(60) NOT NULL
)""",
        f"""INSERT INTO dbo.heap_clustered (id, val, label)
SELECT
    CAST(pk + 1 AS INT),
    CAST(pk + 1 AS BIGINT) * 7919,
    N'row_' + CAST(pk + 1 AS NVARCHAR(20)) + N'_' + REPLICATE(N'x', 20)
FROM fkr__seed
WHERE pk < {rows}""",
        f"""INSERT INTO dbo.heap_plain (id, val, label)
SELECT
    CAST(pk + 1 AS INT),
    CAST(pk + 1 AS BIGINT) * 7919,
    N'row_' + CAST(pk + 1 AS NVARCHAR(20)) + N'_' + REPLICATE(N'x', 20)
FROM fkr__seed
WHERE pk < {rows}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate heapcoverage_large.bak — clustered + heap table pair "
            "for IAM traversal testing."
        )
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        metavar="N",
        help=(
            f"rows per table (default: {DEFAULT_ROWS:,}). "
            "Use ≥50 000 to trigger the IAM scale bug; "
            "80 000 matches the real-world samples that exposed it."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "output .bak path (default: FIXTURE_DIR/heapcoverage_large.bak "
            "for --rows 1000, FIXTURE_DIR/heapcoverage_large_N.bak otherwise)"
        ),
    )
    args = parser.parse_args()

    out = args.out or _out_path(args.rows)

    if skip_if_exists(out):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"seeding {args.rows:,} rows per table …")

    load_and_backup_stmts(container, user, password, build_stmts(args.rows))
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
