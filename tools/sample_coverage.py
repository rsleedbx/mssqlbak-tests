#!/usr/bin/env python3
"""Generate ``docs/SAMPLE_COVERAGE.md`` — extractability across the real corpus.

Promotes the throwaway survey from ``docs/SAMPLE_TESTING_PLAN.md`` into a
committed tool.  For every **downloaded** sample ``.bak`` (the corpus is
git-ignored and fetched by ``tools.fetch_sample_baks``) it records the container
type, whether metadata parses, the user-table count, and the
``classify_table`` supported/skip histogram, plus wall-clock time.

The dominant cost is decompressing the whole file in ``PageStore.from_bak``, so
the survey runs **ascending by size** and rewrites the doc **after each file** —
an interrupted run still leaves a usable partial snapshot.  Progress is logged
via :func:`mssqlbak.enable_logging` (the same per-phase output as CLI ``-v``).

Usage::

    python -m tools.sample_coverage                     # survey + full extraction (default)
    python -m tools.sample_coverage --no-perf           # metadata only (faster)
    python -m tools.sample_coverage --max-mb 130        # skip files larger than 130 MB
    python -m tools.sample_coverage WideWorldImporters  # only matching names

Regenerate the committed snapshot with a full (slow) run; the large compressed
files take minutes each — see the perf note in ``SAMPLE_TESTING_PLAN.md``.
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak import enable_logging  # noqa: E402
from mssqlbak._log import logger  # noqa: E402
from mssqlbak.bacpac import BacpacInfo, is_bacpac  # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.inspect import classify_table  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.reader import read_bak_metadata  # noqa: E402
from tools.fetch_sample_baks import DEST_DIR, build_manifest  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "SAMPLE_COVERAGE.md"

_MSSQLBAK_MAGIC = b"MSSQLBAK"


@dataclass
class Outcome:
    """One sample's survey result (``error`` set means the survey itself failed)."""

    filename: str
    size_mb: float
    container: str = "?"
    metadata_ok: bool = False
    tables: int = 0
    supported: int = 0
    skips: Counter[str] = field(default_factory=Counter)
    elapsed_s: float = 0.0
    error: str | None = None
    sql_version: str = ""
    # Populated only when --perf is set
    rows: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    extract_elapsed_s: float = 0.0
    extract_error: str | None = None


_SS_VERSION: dict[int, str] = {
    8:  "2000",
    9:  "2005",
    10: "2008/R2",
    11: "2012",
    12: "2014",
    13: "2016",
    14: "2017",
    15: "2019",
    16: "2022",
    17: "2025",
}


def _ss_version(v: int) -> str:
    return _SS_VERSION.get(v, f"v{v}" if v else "—")


def _container(path: Path) -> str:
    with path.open("rb") as f:
        return "compressed" if f.read(len(_MSSQLBAK_MAGIC)) == _MSSQLBAK_MAGIC else "MTF"


def _skip_key(reason: str) -> str:
    """Normalise a ``classify_table`` reason into a stable histogram bucket."""
    head = (reason or "?").split(":", 1)[0].strip()
    if head == "compressed":
        return "compressed→columnstore" if "columnstore" in reason else "compressed→row/page"
    return head


def survey_one_bacpac(path: Path, *, perf: bool = False) -> Outcome:
    """Survey a single .bacpac file."""
    size_mb = path.stat().st_size / (1024 * 1024)
    out = Outcome(filename=path.name, size_mb=size_mb, container="BACPAC", metadata_ok=True)
    t0 = time.perf_counter()
    logger.info("survey (bacpac) %s (%.0f MB)", path.name, size_mb)
    try:
        with BacpacInfo(path) as bp:
            all_tables = bp.tables
            tables_with_data = [t for t in all_tables if bp.bcp_files(t)]
            tables_empty = len(all_tables) - len(tables_with_data)
            out.tables = len(all_tables)   # total tables in schema
            out.supported = len(tables_with_data)  # tables with extractable BCP data
            if tables_empty:
                out.skips["no-data"] = tables_empty
    except Exception as exc:  # noqa: BLE001
        out.error = f"{type(exc).__name__}: {exc}"
    out.elapsed_s = time.perf_counter() - t0

    if perf and out.error is None:
        _run_extraction_bacpac(path, out)

    return out


def _run_extraction_bacpac(path: Path, out: Outcome) -> None:
    import tempfile  # noqa: PLC0415

    from mssqlbak.bacpac import extract_bacpac  # noqa: PLC0415
    from mssqlbak.sink import DeltaSink  # noqa: PLC0415

    logger.info("perf extract (bacpac) %s", path.name)
    t0 = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            report = extract_bacpac(path, DeltaSink(tmp))
        out.rows = report.total_rows
        out.bytes_in = report.total_bytes_in
        out.bytes_out = report.total_bytes_out
        out.extract_elapsed_s = time.perf_counter() - t0
    except Exception as exc:  # noqa: BLE001
        out.extract_error = f"{type(exc).__name__}: {exc}"
        out.extract_elapsed_s = time.perf_counter() - t0


def survey_one(path: Path, *, perf: bool = False) -> Outcome:
    size_mb = path.stat().st_size / (1024 * 1024)
    out = Outcome(filename=path.name, size_mb=size_mb)
    t0 = time.perf_counter()
    logger.info("survey %s (%.0f MB)", path.name, size_mb)
    try:
        out.container = _container(path)
        try:
            meta = read_bak_metadata(path)
            out.metadata_ok = True
            if meta.first_set and meta.first_set.software_version:
                out.sql_version = _ss_version(meta.first_set.software_version)
            elif meta.media.media_date:
                # SSET block not parsed (e.g. non-standard 1024-byte block MTF);
                # fall back to the media date year from the TAPE block as a proxy.
                out.sql_version = f"~{meta.media.media_date.year}"
        except Exception:  # noqa: BLE001 — metadata gap is itself a recorded finding
            out.metadata_ok = False

        store = PageStore.from_bak(path)
        available = store.available_files
        tables = recover_schema(store).tables
        out.tables = len(tables)
        for table in tables:
            support = classify_table(table, available)
            if support.supported:
                out.supported += 1
            else:
                out.skips[_skip_key(support.reason or "?")] += 1
    except Exception as exc:  # noqa: BLE001 — keep surveying the rest of the corpus
        out.error = f"{type(exc).__name__}: {exc}"
    out.elapsed_s = time.perf_counter() - t0

    if perf and out.error is None:
        _run_extraction(path, out)

    return out


def _run_extraction(path: Path, out: Outcome) -> None:
    import tempfile  # noqa: PLC0415

    from mssqlbak import extract_bak_to_delta  # noqa: PLC0415

    logger.info("perf extract %s", path.name)
    t0 = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            report = extract_bak_to_delta(path, tmp)
        out.rows = report.total_rows
        out.bytes_in = report.total_bytes_in
        out.bytes_out = report.total_bytes_out
        out.extract_elapsed_s = time.perf_counter() - t0
    except Exception as exc:  # noqa: BLE001
        out.extract_error = f"{type(exc).__name__}: {exc}"
        out.extract_elapsed_s = time.perf_counter() - t0


def _present_samples(patterns: list[str], max_mb: float | None) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    manifest_names = {s.filename for s in build_manifest()}

    # Files from the fetch manifest (.bak and .bacpac)
    for sample in build_manifest():
        p = DEST_DIR / sample.filename
        if not (p.exists() and p.stat().st_size > 0):
            continue
        if (DEST_DIR / f"{sample.filename}.part").exists():
            continue  # mid-download
        if patterns and not any(pat.lower() in sample.filename.lower() for pat in patterns):
            continue
        if max_mb is not None and p.stat().st_size / (1024 * 1024) > max_mb:
            continue
        paths.append(p)
        seen.add(p)

    # .bacpac files present in DEST_DIR but NOT in the fetch manifest
    for p in sorted(DEST_DIR.glob("*.bacpac")):
        if p in seen or p.name in manifest_names:
            continue
        if not (p.exists() and p.stat().st_size > 0):
            continue
        if patterns and not any(pat.lower() in p.name.lower() for pat in patterns):
            continue
        if max_mb is not None and p.stat().st_size / (1024 * 1024) > max_mb:
            continue
        paths.append(p)
        seen.add(p)

    return sorted(paths, key=lambda p: p.stat().st_size)


def _fmt_bytes(b: int) -> str:
    for unit, divisor in (("GB", 1_073_741_824), ("MB", 1_048_576), ("KB", 1_024)):
        if b >= divisor:
            return f"{b / divisor:.1f} {unit}"
    return f"{b} B"


def _fmt_rate(b_per_s: float) -> str:
    if b_per_s >= 1_000_000:
        return f"{b_per_s / 1_000_000:.1f} MB/s"
    if b_per_s >= 1_000:
        return f"{b_per_s / 1_000:.1f} KB/s"
    return f"{b_per_s:.0f} B/s"


def build_report(outcomes: list[Outcome], missing: list[str], skipped_big: list[str]) -> str:
    surveyed = [o for o in outcomes if o.error is None]
    total_tables = sum(o.tables for o in surveyed)
    total_supported = sum(o.supported for o in surveyed)
    clean = sum(1 for o in surveyed if o.tables and o.supported == o.tables)

    lines: list[str] = [
        "# Sample-corpus coverage",
        "",
        "Extractability of the real Microsoft `sql-server-samples` corpus "
        "(`tests/fixtures_realworld/`, git-ignored). **Generated** by "
        "`python -m tools.sample_coverage`; see "
        "[SAMPLE_TESTING_PLAN.md](SAMPLE_TESTING_PLAN.md) for method and roadmap, "
        "and [ROBUSTNESS_COVERAGE.md](ROBUSTNESS_COVERAGE.md) for the skip "
        "contract on the committed fixtures.",
        "",
        f"**Surveyed {len(surveyed)} downloaded sample(s):** {total_supported} of "
        f"{total_tables} user tables supported; {clean} database(s) fully "
        "supported (every table extractable, 0 skips).",
        "",
        "Each row reflects `classify_table` (metadata-only extractability), not "
        "value correctness — see [ENGINE_VALIDATION.md](ENGINE_VALIDATION.md).",
        "",
        "| Sample | SS Version | MB | Container | Metadata | Tables | Supported | Skips | Time |",
        "|--------|:----------:|---:|-----------|:--------:|-------:|----------:|-------|-----:|",
    ]
    for o in outcomes:
        if o.error is not None:
            lines.append(
                f"| `{o.filename}` | — | {o.size_mb:.0f} | {o.container} | — | — | — | "
                f"**survey error:** {o.error} | {o.elapsed_s:.0f}s |"
            )
            continue
        meta = "ok" if o.metadata_ok else "FAIL"
        skips = (
            ", ".join(f"{k} ×{n}" for k, n in sorted(o.skips.items()))
            if o.skips else "—"
        )
        supported = (
            f"**{o.supported}**" if o.tables and o.supported == o.tables else str(o.supported)
        )
        ver = o.sql_version or "—"
        lines.append(
            f"| `{o.filename}` | {ver} | {o.size_mb:.0f} | {o.container} | {meta} | "
            f"{o.tables} | {supported} | {skips} | {o.elapsed_s:.0f}s |"
        )
    lines.append("")

    # Perf section — only emitted when at least one outcome has extraction data.
    perf_outcomes = [o for o in outcomes if o.rows > 0 or o.extract_error is not None]
    if perf_outcomes:
        lines += [
            "## Extraction performance",
            "",
            "Measured by `--perf` (full row extraction into a temp Delta directory). "
            "**Bytes in** = uncompressed page bytes read (pages × 8 KiB); "
            "**bytes out** = in-memory Arrow batch bytes before Delta compression.",
            "",
            "| Sample | Rows in | Rows out | In bytes | Out bytes | "
            "In rows/s | Out rows/s | In MB/s | Out MB/s | Time |",
            "|--------|--------:|---------:|---------:|----------:|"
            "----------:|-----------:|--------:|---------:|-----:|",
        ]
        for o in perf_outcomes:
            if o.extract_error is not None:
                lines.append(
                    f"| `{o.filename}` | — | — | — | — | — | — | — | — | "
                    f"**error:** {o.extract_error} |"
                )
                continue
            t = o.extract_elapsed_s or 1e-9
            rows_per_s = o.rows / t
            bin_per_s  = o.bytes_in  / t
            bout_per_s = o.bytes_out / t
            lines.append(
                f"| `{o.filename}` "
                f"| {o.rows:,} "
                f"| {o.rows:,} "
                f"| {_fmt_bytes(o.bytes_in)} "
                f"| {_fmt_bytes(o.bytes_out)} "
                f"| {rows_per_s:,.0f} "
                f"| {rows_per_s:,.0f} "
                f"| {_fmt_rate(bin_per_s)} "
                f"| {_fmt_rate(bout_per_s)} "
                f"| {o.extract_elapsed_s:.0f}s |"
            )
        lines.append("")
    if skipped_big:
        lines += [
            "## Downloaded but not surveyed (over size cap)",
            "",
            "Run `python -m tools.sample_coverage` without `--max-mb` to include:",
            "",
            *[f"- `{n}`" for n in skipped_big],
            "",
        ]
    if missing:
        lines += [
            "## Not downloaded",
            "",
            "Fetch with `python -m tools.fetch_sample_baks`:",
            "",
            *[f"- `{n}`" for n in missing],
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("patterns", nargs="*", help="only survey samples matching these substrings")
    ap.add_argument("--max-mb", type=float, default=None, help="skip files larger than this")
    ap.add_argument("--quiet", action="store_true", help="suppress per-phase progress logging")
    ap.add_argument("--list", action="store_true", help="print files that would be surveyed and exit")
    ap.add_argument("--no-perf", dest="perf", action="store_false",
                    help="skip full extraction; only survey metadata (faster)")
    ap.set_defaults(perf=True)
    args = ap.parse_args()
    if not args.quiet:
        enable_logging()

    present = _present_samples(args.patterns, args.max_mb)

    if args.list:
        for p in present:
            print(f"{p.stat().st_size / (1024 * 1024):7.1f} MB  {p.name}")
        print(f"\n{len(present)} file(s)")
        return 0
    present_names = {p.name for p in present}
    all_present = {
        s.filename for s in build_manifest()
        if (DEST_DIR / s.filename).exists() and (DEST_DIR / s.filename).stat().st_size > 0
    }
    skipped_big = sorted(all_present - present_names - {
        n for n in all_present
        if args.patterns and not any(p.lower() in n.lower() for p in args.patterns)
    })
    missing = sorted(
        s.filename for s in build_manifest()
        if not (DEST_DIR / s.filename).exists()
    )

    outcomes: list[Outcome] = []
    for path in present:
        if is_bacpac(path):
            outcomes.append(survey_one_bacpac(path, perf=args.perf))
        else:
            outcomes.append(survey_one(path, perf=args.perf))
        # Rewrite after each file so an interrupted run leaves a usable snapshot.
        DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        DOC_PATH.write_text(build_report(outcomes, missing, skipped_big))
    if not present:
        DOC_PATH.write_text(build_report([], missing, skipped_big))
    logger.info("wrote %s (%d sample(s))", DOC_PATH, len(outcomes))
    print(f"wrote {DOC_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
