"""Sink performance benchmark: delta-rs vs pg_dump over all .bak fixtures.

Fast fixtures (tests/fixtures/*.bak):
    pytest tests/test_sink_perf.py -v -s

Real-world samples (tests/fixtures_realworld/*.bak) — add --samples flag:
    pytest tests/test_sink_perf.py -v -s --samples

Both together:
    pytest tests/test_sink_perf.py -v -s --samples --run-all

Produces a timing table comparing DeltaSink and PgDumpSink.
Skipped / unsupported tables are noted but do not fail the test.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

from mssqlbak.extract import extract_bak
from mssqlbak.sink import DeltaSink
from pgdump.pg_sink import PgDumpSink

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))
_SAMPLES_DIR = Path(os.environ.get("SAMPLE_DIR", str(Path(__file__).parent / "fixtures_realworld")))

# Individual stripe files require PageStore.from_stripe([stripe1, stripe2]); they cannot be
# opened as standalone backups.  Their combined behaviour is tested in test_striped_backup.py.
# striped_single.bak is the single-file equivalent and is included in _FAST_BAKS.
_STRIPE_ONLY = frozenset({"striped_full_1.bak", "striped_full_2.bak"})

# Fixtures whose extraction is designed to raise, so they cannot be benchmarked:
#   tde_full — Transparent Data Encryption; extract raises EncryptedBackupError.
#   corrupt_metadata_confidence_full — deliberately malformed backup; catalog
#     recovery fails by design (see test_corrupt_metadata_confidence_coverage.py).
_UNEXTRACTABLE_BY_DESIGN = frozenset({
    "tde_full.bak",
    "corrupt_metadata_confidence_full.bak",
})
_EXCLUDED_FAST = _STRIPE_ONLY | _UNEXTRACTABLE_BY_DESIGN
_FAST_BAKS   = [p for p in sorted(_FIXTURE_DIR.glob("*.bak")) if p.name not in _EXCLUDED_FAST]
_SAMPLE_BAKS = sorted(_SAMPLES_DIR.glob("*.bak"))


# ---------------------------------------------------------------------------
# Result accumulator — one entry per (fixture, sink)
# ---------------------------------------------------------------------------

@dataclass
class _BenchRow:
    fixture: str
    sink: str
    rows: int
    tables: int
    skipped: int
    elapsed_s: float
    bak_mb: float


_RESULTS: list[_BenchRow] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_delta(bak: Path, tmp_path: Path) -> _BenchRow:
    sink = DeltaSink(tmp_path / "delta")
    t0 = time.perf_counter()
    report = extract_bak(bak, sink)
    elapsed = time.perf_counter() - t0
    return _BenchRow(
        fixture=bak.name,
        sink="delta-rs",
        rows=report.total_rows,
        tables=len(report.extracted),
        skipped=len(report.skipped),
        elapsed_s=elapsed,
        bak_mb=bak.stat().st_size / 1_048_576,
    )


def _run_pg(bak: Path, tmp_path: Path) -> _BenchRow:
    out = tmp_path / "dump.sql"
    sink = PgDumpSink(out)
    t0 = time.perf_counter()
    try:
        report = extract_bak(bak, sink)
    finally:
        sink.finish()
    elapsed = time.perf_counter() - t0
    return _BenchRow(
        fixture=bak.name,
        sink="pg-dump",
        rows=report.total_rows,
        tables=len(report.extracted),
        skipped=len(report.skipped),
        elapsed_s=elapsed,
        bak_mb=bak.stat().st_size / 1_048_576,
    )


# ---------------------------------------------------------------------------
# Report fixture — prints after all tests in this module complete
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _print_report() -> None:  # type: ignore[return]
    """Print consolidated timing table once all benchmark tests have run."""
    yield  # type: ignore[misc]

    if not _RESULTS:
        return

    _print_table(_RESULTS, "Sink performance: delta-rs vs pg-dump")


def _print_table(results: list[_BenchRow], title: str) -> None:
    # Group by fixture name
    by_fixture: dict[str, dict[str, _BenchRow]] = {}
    for r in results:
        by_fixture.setdefault(r.fixture, {})[r.sink] = r

    fw = max(len(r.fixture) for r in results)
    header = (
        f"\n{'Fixture':<{fw}}  {'MB':>6}  {'tables':>6}  {'skipped':>7}  "
        f"{'rows':>9}  {'delta-rs':>9}  {'pg-dump':>8}  {'faster':>7}"
    )
    sep = "-" * len(header)
    print(f"\n{sep}")
    print(title)
    print(sep)
    print(header)
    print(sep)

    for fixture in sorted(by_fixture):
        row = by_fixture[fixture]
        dr = row.get("delta-rs")
        pg = row.get("pg-dump")

        anchor = dr or pg
        assert anchor is not None
        rows  = anchor.rows
        tabs  = anchor.tables
        skips = anchor.skipped
        mb    = anchor.bak_mb

        dr_s = f"{dr.elapsed_s:.2f}s" if dr else "—"
        pg_s = f"{pg.elapsed_s:.2f}s" if pg else "—"

        if dr and pg and dr.elapsed_s > 0:
            ratio = pg.elapsed_s / dr.elapsed_s
            faster = f"pg {ratio:.1f}×" if ratio > 1 else f"dr {1/ratio:.1f}×"
        else:
            faster = "—"

        print(
            f"{fixture:<{fw}}  {mb:>6.0f}  {tabs:>6}  {skips:>7}  "
            f"{rows:>9,}  {dr_s:>9}  {pg_s:>8}  {faster:>7}"
        )

    print(sep)

    dr_rows = [r for r in results if r.sink == "delta-rs"]
    pg_rows = [r for r in results if r.sink == "pg-dump"]
    if dr_rows and pg_rows:
        total_dr   = sum(r.elapsed_s for r in dr_rows)
        total_pg   = sum(r.elapsed_s for r in pg_rows)
        total_rows = sum(r.rows for r in dr_rows)
        total_mb   = sum(r.bak_mb for r in dr_rows)
        ratio = total_pg / total_dr if total_dr > 0 else float("nan")
        print(
            f"\nTotal  {total_mb:.0f} MB  "
            f"delta-rs={total_dr:.1f}s  pg-dump={total_pg:.1f}s  "
            f"rows={total_rows:,}  pg/delta={ratio:.2f}×"
        )
    print(sep + "\n")


# ---------------------------------------------------------------------------
# Fast fixture tests  (always run)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bak", _FAST_BAKS, ids=lambda p: p.stem)
def test_delta_sink(bak: Path, tmp_path: Path) -> None:
    """Extract every fast fixture through DeltaSink and record timing."""
    row = _run_delta(bak, tmp_path)
    _RESULTS.append(row)
    assert row.elapsed_s >= 0


@pytest.mark.parametrize("bak", _FAST_BAKS, ids=lambda p: p.stem)
def test_pg_sink(bak: Path, tmp_path: Path) -> None:
    """Extract every fast fixture through PgDumpSink and record timing."""
    row = _run_pg(bak, tmp_path)
    _RESULTS.append(row)
    assert row.elapsed_s >= 0


# ---------------------------------------------------------------------------
# Real-world sample tests  (opt-in via --samples)
# ---------------------------------------------------------------------------

@pytest.mark.samples
@pytest.mark.parametrize("bak", _SAMPLE_BAKS, ids=lambda p: p.stem)
def test_delta_sink_samples(bak: Path, tmp_path: Path) -> None:
    """Extract every real-world sample through DeltaSink and record timing."""
    row = _run_delta(bak, tmp_path)
    _RESULTS.append(row)
    assert row.elapsed_s >= 0


@pytest.mark.samples
@pytest.mark.parametrize("bak", _SAMPLE_BAKS, ids=lambda p: p.stem)
def test_pg_sink_samples(bak: Path, tmp_path: Path) -> None:
    """Extract every real-world sample through PgDumpSink and record timing."""
    row = _run_pg(bak, tmp_path)
    _RESULTS.append(row)
    assert row.elapsed_s >= 0
