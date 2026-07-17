"""Case discovery: scan fixture directories, parse timings, sort and select cases."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _parse_prior_timings(out_path: Path) -> dict[str, float]:
    """Extract ``bak_name -> wall_seconds`` from an existing coverage doc.

    Scans the ``## Extraction timings`` table in a previously generated
    markdown file so the current run can schedule the slowest fixtures first,
    minimising overall wall time when ``--threads > 1``.

    Returns an empty dict when the file is absent or has no timing table.
    """
    if not out_path.is_file():
        return {}
    timings: dict[str, float] = {}
    in_table = False
    for line in out_path.read_text().splitlines():
        if line.startswith("## Extraction timings"):
            in_table = True
            continue
        if in_table:
            if line.startswith("#"):
                break
            # Match table rows like: | `Foo.bak` | 123.45s |
            # Match 3-column rows (Extract | Verify | Wall) capturing Wall,
            # and fall back to legacy 1-column rows (Wall only).
            m = re.match(
                r"^\|\s*`([^`]+\.bak)`\s*\|(?:\s*[\d.]+s\s*\|){0,2}\s*([\d.]+)s\s*\|",
                line,
            )
            if m:
                timings[m.group(1)] = float(m.group(2))
    return timings


def _parse_prior_peaks(res_path: Path) -> dict[str, float]:
    """Return ``{bak_name -> observed peak MB}`` from a prior ``.resources.json``.

    Prefers ``hwm_rss_mb`` (OS ``ru_maxrss`` high-water mark — the true peak)
    and falls back to ``peak_rss_mb`` (sampled maximum, may under-count).
    Returns an empty dict when the file is absent or unreadable.

    The result is used by ``_estimate_peak_mb`` to calibrate the memory-budget
    scheduler: calibrated estimates replace the conservative ``bak_size × 25``
    heuristic so that raising ``--mem-budget-gb`` is safe even for large fixtures
    whose heuristic estimate would otherwise under- or over-shoot.
    """
    if not res_path.is_file():
        return {}
    try:
        data = json.loads(res_path.read_text())
    except (OSError, ValueError):
        return {}
    peaks: dict[str, float] = {}
    for f in data.get("fixtures", []):
        name = f.get("bak")
        hwm = f.get("hwm_rss_mb") or f.get("peak_rss_mb")
        if name and hwm:
            peaks[name] = float(hwm)
    return peaks


def _sort_cases_longest_first(
    cases: list[tuple[Path, Path | None]],
    timings: dict[str, float],
) -> list[tuple[Path, Path | None]]:
    """Stable-sort cases so longest-running fixtures are scheduled first.

    Fixtures with no prior timing data are placed after known fixtures,
    preserving their original relative order via a secondary sort key.
    """
    _NO_TIMING = 0.0
    indexed = list(enumerate(cases))
    indexed.sort(key=lambda t: (-timings.get(t[1][0].name, _NO_TIMING), t[0]))
    return [c for _, c in indexed]


def _discover_cases(fixture_dir: Path) -> list[tuple[Path, Path | None]]:
    """Return (bak, stats_json) pairs found under fixture_dir (recursive)."""
    seen_prefixes: set[str] = set()
    cases = []
    for bak_path in sorted(fixture_dir.glob("**/*.bak")):
        if not bak_path.is_file():
            continue
        m = re.match(r"^(.+)_(\d)$", bak_path.stem)
        if m:
            prefix = m.group(1)
            digit = int(m.group(2))
            if prefix in seen_prefixes:
                continue
            lower = any((bak_path.parent / f"{prefix}_{d}.bak").exists() for d in range(1, digit))
            if lower:
                continue
            seen_prefixes.add(prefix)
        stats_path = bak_path.with_name(f"{bak_path.name}.stats.json")
        if not stats_path.is_file():
            stats_path = None
        cases.append((bak_path, stats_path))
    return cases


def _select_cases(
    fixture_dir: Path,
    bak_paths: Path | list[Path] | None,
) -> list[tuple[Path, Path | None]]:
    """Return all fixture cases, or the requested ``.bak`` cases."""
    if bak_paths is None:
        return _discover_cases(fixture_dir)

    if isinstance(bak_paths, Path):
        selected = [bak_paths]
    else:
        selected = bak_paths

    cases: list[tuple[Path, Path | None]] = []
    for bak_path in selected:
        bak_path = bak_path.resolve()
        if bak_path.suffix.lower() != ".bak":
            raise ValueError(f"fixture input must be a .bak file: {bak_path}")
        if not bak_path.is_file():
            raise FileNotFoundError(f"backup file not found: {bak_path}")

        stats_path = bak_path.with_name(f"{bak_path.name}.stats.json")
        if not stats_path.is_file():
            stats_path = None
        cases.append((bak_path, stats_path))
    return cases
