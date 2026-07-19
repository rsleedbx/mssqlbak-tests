"""Generate ``docs/correctness_coverage.md``.

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is stored in ``tests/fixtures/<name>.bak.stats.json`` and
collected by ``python -m tools.fixture_run register-bak <name>.bak``.

Usage::

    python -m tools.correctness_coverage            # regenerate the doc
    python -m tools.correctness_coverage --no-write # print to stdout only
    python -m tools.correctness_coverage tests/fixtures_realworld/BaseballData.bak --no-write
    python -m tools.correctness_coverage tests/fixtures_realworld/BaseballData.bak tests/fixtures_realworld/Chinook-id-pk.bak --no-write

``--threads`` uses worker processes. Higher values can reduce wall time on large
fixture sets. Extraction is done entirely in memory (no temporary Delta I/O).
"""

from __future__ import annotations

# Public API and backward-compatibility re-exports
from .cli import main
from .compare import _minmax_equal
from .config import NodeStats
from .discovery import _select_cases
from .render import _all_ok, _render
from .runner import _resolve_bak_input, _run_case, _run_cases, _run_logged_case, _run_one
from .sinks import SINKS, SinkSpec

__all__ = [
    "main",
    "SinkSpec",
    "SINKS",
    "NodeStats",
    "_all_ok",
    "_minmax_equal",
    "_render",
    "_resolve_bak_input",
    "_run_case",
    "_run_cases",
    "_run_logged_case",
    "_run_one",
    "_select_cases",
]
