"""Shared constants, paths, and type aliases for the correctness_coverage package."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

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
# NodeStats type alias and TypedDicts
# ---------------------------------------------------------------------------

# {fqn: per-table stats dict}
# GT node entries have kind="ground_truth"; Arrow node entries have kind="arrow".
NodeStats = dict[str, dict[str, Any]]


class ArrowNodeEntry(TypedDict, total=False):
    """Per-table stats computed from an extracted or read-back Arrow table."""

    kind: str           # always "arrow"
    row_count: int
    null_counts: dict[str, int]
    min_vals: dict[str, Any]
    max_vals: dict[str, Any]
    col_count: int
    col_names: list[str]


class GTNodeEntry(TypedDict, total=False):
    """Per-table stats loaded from a .bak.stats.json ground-truth file."""

    kind: str           # always "ground_truth"
    expected_rows: int
    col_count: int
    col_names: list[str]
    gt_columns: list[dict[str, Any]]


class EdgeResult(TypedDict, total=False):
    """One pipeline-edge comparison result (e.g. mssql→arrow or arrow→delta)."""

    tables: list[dict[str, Any]]
    write_s: float | None
    readback_s: float | None


class MetadataGTEntry(TypedDict, total=False):
    """Shape of a single ``ValidationResult.to_dict()`` entry in ``validations``."""

    category: str
    n_ok: int
    n_total: int
    missing: list[str]
    extra: list[str]
    mismatched: list[dict[str, Any]]
    error: str | None
    unscored: bool
    ok: bool


class FixtureResult(TypedDict, total=False):
    """Top-level result dict returned by _run_one / _run_case for one .bak file.

    Crashed fixtures populate only ``bak``, ``error``, ``traceback``, ``crashed``,
    ``tables``, and ``edges`` (empty); all timing/resource fields are absent.
    """

    bak: str
    sql_version: str
    bak_size_mb: float
    extract_s: float
    wall_s: float
    write_s: dict[str, float]
    readback_s: dict[str, float]
    read_s: dict[str, float]
    stats_s: dict[str, float]
    verify_s: dict[str, float]
    phases: dict[str, float]
    catalog_s: float
    data_decode_net_s: float
    tables: list[dict[str, Any]]
    edges: dict[str, EdgeResult]
    total_src_rows: int
    total_src_cols: int
    resources: dict[str, Any]
    confidence: dict[str, Any]
    run_id: str
    source_mode: str
    # Metadata validation results: {category_name: ValidationResult.to_dict()}.
    # Present only when a <bak>.metadata.json sidecar exists; absent (not "unscored")
    # when the sidecar is missing, so existing data pass rates are unaffected.
    validations: dict[str, MetadataGTEntry]
    # Set only when the fixture crashed/errored before producing a result.
    error: str
    traceback: str
    crashed: bool
