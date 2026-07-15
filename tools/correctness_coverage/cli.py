"""CLI entry point: argument parsing and top-level orchestration."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from .config import (
    FIXTURES,
    OUT_PATH,
    REPO_ROOT,
    _DEFAULT_OUTDIR,
    _DEFAULT_REPORTS_DIR,
)
from .discovery import _parse_prior_timings, _select_cases, _sort_cases_longest_first
from .http_server import _local_http_server
from .render import _all_ok, _render
from .reports import _assemble_from_disk
from .runner import _run_cases
from .sinks import SINKS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate ``docs/correctness_coverage.md``.\n\n"
            "Per-backup comparison of mssqlbak extraction against SQL Server ground truth.\n"
            "Ground truth is stored in ``tests/fixtures/<name>.bak.stats.json`` and\n"
            "collected by ``python -m tools.fixture_run register-bak <name>.bak``.\n\n"
            "Usage::\n\n"
            "    python -m tools.correctness_coverage            # regenerate the doc\n"
            "    python -m tools.correctness_coverage --no-write # print to stdout only\n"
            "    python -m tools.correctness_coverage tests/fixtures_realworld/BaseballData.bak --no-write\n"
            "    python -m tools.correctness_coverage tests/fixtures_realworld/BaseballData.bak tests/fixtures_realworld/Chinook-id-pk.bak --no-write\n\n"
            "``--threads`` uses worker processes. Higher values can reduce wall time on large\n"
            "fixture sets. Extraction is done entirely in memory (no temporary Delta I/O).\n"
        )
    )
    parser.add_argument(
        "baks",
        nargs="*",
        type=Path,
        help="optional .bak file(s) to process instead of scanning the fixture directory",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print to stdout instead of writing the file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write markdown to this path instead of the default docs path",
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=None,
        help=(
            "directory to scan for .bak / .stats.json pairs "
            f"(default: {FIXTURES}; use tests/fixtures_realworld for the sample suite)"
        ),
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help=(
            "number of backups to process concurrently in worker processes "
            "(default: 4; use 1 for serial; higher values increase CPU and temp-file I/O)"
        ),
    )
    parser.add_argument(
        "--mem-budget-gb",
        type=float,
        default=8.0,
        metavar="GB",
        help=(
            "soft resident-memory budget for concurrent workers in GB (default: 8). "
            "The scheduler sums estimated per-fixture peaks and admits a new worker "
            "only when the sum stays under this limit. At least one fixture always "
            "runs so progress is never blocked. Use --threads to cap parallelism "
            "independently of the budget."
        ),
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help=(
            "serve the fixture directory over a local HTTP server and pass each "
            ".bak as an http:// URL to extraction, exercising the remote-reader / "
            "LazyPageStore path.  Output doc gets an '_http' suffix to avoid "
            "overwriting the local-file run."
        ),
    )
    parser.add_argument(
        "--sinks",
        default="delta,pg_dir",
        help=(
            "comma-separated list of sinks to fan out to (default: delta,pg_dir). "
            f"Valid choices: {', '.join(sorted(SINKS))}. Use empty string to skip sinks."
        ),
    )
    parser.add_argument(
        "--verify",
        default="digest",
        choices=["full", "digest", "none"],
        help=(
            "verification depth for each edge (arrow, delta, pg_dir). "
            "'digest' (default): per-column SHA-256 aggregate hash — fast, catches "
            "any multiset-level value corruption; no GT parquet read, no per-row "
            "alignment. "
            "'full': exhaustive keyed row-level compare — also catches value-preserving "
            "row misalignment; ~3–10x slower. "
            "'none': skip cell verification entirely (row/null/min-max aggregates still "
            "run). Use to profile read/write hot paths."
        ),
    )
    parser.add_argument(
        "--no-cell-verify",
        action="store_true",
        help="back-compat alias for --verify none",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=_DEFAULT_OUTDIR,
        help=(
            "root directory for sink output (default: ./outdir beside mssqlbak-tests/). "
            "Per-fixture data lands under <outdir>/<bak-stem>/<sink>/."
        ),
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=_DEFAULT_REPORTS_DIR,
        help=(
            "root directory for tracked per-edge JSON reports "
            f"(default: {_DEFAULT_REPORTS_DIR}). "
            "History accretes; existing runs are never deleted."
        ),
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help=(
            "skip extraction; rebuild the .md purely from the latest on-disk JSON "
            "reports under --reports-dir. Useful for regenerating after editing."
        ),
    )
    args = parser.parse_args(argv)

    # Parse and validate --sinks
    raw_sinks = [s.strip() for s in args.sinks.split(",") if s.strip()]
    invalid = [s for s in raw_sinks if s not in SINKS]
    if invalid:
        parser.error(f"unknown sinks: {', '.join(invalid)}. Valid: {', '.join(sorted(SINKS))}")
    sink_names: list[str] = raw_sinks

    bak_paths: list[Path] = [path.resolve() for path in args.baks]
    fixture_dir: Path = (
        args.fixture_dir.resolve()
        if args.fixture_dir
        else bak_paths[0].parent
        if bak_paths
        else FIXTURES
    )
    if args.output is not None:
        out_path = args.output.resolve()
    elif bak_paths:
        stem = bak_paths[0].stem if len(bak_paths) == 1 else "selected"
        out_path = REPO_ROOT / "docs" / f"correctness_coverage_{stem}.md"
    elif args.fixture_dir is None:
        out_path = OUT_PATH
    else:
        out_path = REPO_ROOT / "docs" / f"correctness_coverage_{fixture_dir.name}.md"

    # --http: append _http before the .md extension so the HTTP run does not
    # overwrite the local-file run's document.
    if args.http and args.output is None:
        out_path = out_path.with_name(out_path.stem + "_http" + out_path.suffix)

    source_mode = "http" if args.http else "local"
    reports_dir: Path = args.reports_dir.resolve()
    outdir: Path = args.outdir.resolve()

    if args.assemble_only:
        print("==> assembling from on-disk reports …", file=sys.stderr)
        results = _assemble_from_disk(reports_dir, fixture_dir, source_mode)
        doc = _render(
            results,
            fixture_dir=fixture_dir,
            bak_paths=bak_paths,
            show_fixture_dir=args.fixture_dir is not None or not bak_paths,
            sink_names=sink_names,
        )
        if args.no_write:
            sys.stdout.write(doc)
        else:
            out_path.write_text(doc)
            print(f"==> wrote {out_path}", file=sys.stderr)
        return 0

    try:
        cases = _select_cases(fixture_dir, bak_paths or None)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    if args.threads < 1:
        parser.error("--threads must be >= 1")
    if args.mem_budget_gb <= 0:
        parser.error("--mem-budget-gb must be > 0")

    # Sort longest-first using timings from the previous run of this doc so
    # the slowest fixtures start immediately and minimise overall wall time.
    prior_timings = _parse_prior_timings(out_path)
    if prior_timings:
        cases = _sort_cases_longest_first(cases, prior_timings)

    # One run_id per invocation so all edge JSONs for this run share the timestamp.
    run_id_suffix = "_http" if args.http else ""
    run_id = datetime.datetime.now().strftime("%Y%m%dT%H%M%S") + run_id_suffix

    mem_budget_mb: float = args.mem_budget_gb * 1024

    verify_level = "none" if args.no_cell_verify else args.verify

    print(
        f"==> {len(cases)} fixtures to process in {fixture_dir} "
        f"(threads={args.threads}, mem_budget={args.mem_budget_gb:.1f}GB"
        f"{', http' if args.http else ''}"
        f"{f', sinks={sink_names}' if sink_names else ''}"
        f", verify={verify_level})",
        file=sys.stderr,
    )

    common_kw: dict[str, Any] = dict(
        sink_names=sink_names,
        outdir=outdir if sink_names else None,
        reports_dir=reports_dir if sink_names else None,
        run_id=run_id,
        source_mode=source_mode,
        verify_level=verify_level,
    )

    if args.http:
        with _local_http_server(fixture_dir) as http_port:
            results = _run_cases(
                cases, threads=args.threads, mem_budget_mb=mem_budget_mb,
                http_port=http_port, **common_kw,
            )
    else:
        results = _run_cases(
            cases, threads=args.threads, mem_budget_mb=mem_budget_mb, **common_kw,
        )

    doc = _render(
        results,
        fixture_dir=fixture_dir,
        bak_paths=bak_paths,
        show_fixture_dir=args.fixture_dir is not None or not bak_paths,
        sink_names=sink_names,
    )

    if args.no_write:
        sys.stdout.write(doc)
    else:
        out_path.write_text(doc)
        n_pass = sum(1 for r in results if _all_ok(r))
        print(f"==> wrote {out_path}  ({n_pass}/{len(results)} pass)", file=sys.stderr)

    # Emit per-fixture resource snapshots alongside the markdown document so
    # memory hotspots can be diagnosed without re-running.
    resource_records = [r["resources"] for r in results if r.get("resources")]
    if resource_records:
        res_path = out_path.with_suffix(".resources.json")
        res_payload: dict[str, Any] = {
            "run_id": run_id,
            "source_mode": source_mode,
            "mem_budget_gb": args.mem_budget_gb,
            "threads": args.threads,
            "fixtures": [
                {
                    "bak": r.get("bak"),
                    "bak_size_mb": r.get("bak_size_mb"),
                    "total_src_rows": r.get("total_src_rows"),
                    "wall_s": r.get("wall_s"),
                    "extract_s": r.get("extract_s"),
                    "catalog_s": r.get("catalog_s"),
                    "data_decode_net_s": r.get("data_decode_net_s"),
                    "phases": r.get("phases"),
                    "write_s": r.get("write_s"),
                    "readback_s": r.get("readback_s"),
                    "read_s": r.get("read_s"),
                    "stats_s": r.get("stats_s"),
                    "verify_s": r.get("verify_s"),
                    **r["resources"],
                }
                for r in results
                if r.get("resources")
            ],
        }
        if args.no_write:
            sys.stdout.write("\n--- resources ---\n")
            sys.stdout.write(json.dumps(res_payload, indent=2))
            sys.stdout.write("\n")
        else:
            res_path.write_text(json.dumps(res_payload, indent=2))
            print(f"==> wrote {res_path}", file=sys.stderr)

    return 0
