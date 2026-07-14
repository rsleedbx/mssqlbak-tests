"""Shared constants, paths, and type aliases for the correctness_coverage package."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Full Rust backtraces so Rust panics (PanicException) print the call chain to
# stderr rather than just the panic message.
os.environ.setdefault("RUST_BACKTRACE", "1")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# This file lives at tools/correctness_coverage/config.py; three .parent calls
# reach mssqlbak-tests/ (the project root used for docs/, tests/, etc.).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = REPO_ROOT / "docs" / "correctness_coverage.md"

_DEFAULT_REPORTS_DIR = REPO_ROOT / "docs" / "correctness_reports"
_DEFAULT_OUTDIR = REPO_ROOT.parent / "outdir"  # git-ignored; sits beside mssqlbak-tests/

# ---------------------------------------------------------------------------
# SQL Server compression constants (from sys.partitions)
# ---------------------------------------------------------------------------

_COMP_COLUMNSTORE = frozenset({3, 4})  # COLUMNSTORE and COLUMNSTORE_ARCHIVE

# ---------------------------------------------------------------------------
# Min/max comparison skip list
# ---------------------------------------------------------------------------

# Types skipped for min/max comparison (collation, truncation, or format issues).
# Must stay in sync with _MINMAX_SKIP_TYPES in tests/test_stats.py.
_MINMAX_SKIP_TYPES: frozenset[str] = frozenset(
    {
        "sql_variant",
        # uniqueidentifier: SQL Server sorts GUIDs by bytes [10-15], [8-9], [6-7],
        # [4-5], [0-3] — not lexicographic order.  The MIN/MAX returned by SQL Server
        # differs from pyarrow's lexicographic MIN/MAX of the string representation.
        "uniqueidentifier",
    }
)

# ---------------------------------------------------------------------------
# NodeStats type alias
# ---------------------------------------------------------------------------

# {fqn: per-table stats dict}
# GT node entries have kind="ground_truth"; Arrow node entries have kind="arrow".
NodeStats = dict[str, dict[str, Any]]
