"""Orchestration: extraction, per-case runners, and ProcessPoolExecutor dispatch."""

from __future__ import annotations

import faulthandler
import gc
import json
import logging
import os
import re
import shutil
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

import pyarrow as pa

from mssqlbak.confidence import ConfidenceCheck, ConfidenceReport, analyze_bak
from mssqlbak.extract import extract_bak
from mssqlbak.sink import MultiSink
from tools import value_verify
from tools.known_gaps import expected_skipped_tables

from .compare import (
    _apply_precomputed_cell_results,
    _compare_tables,
    _node_stats_from_arrow_table,
    _node_stats_from_ground_truth,
)
from .config import NodeStats
from .reports import _write_edge_json
from .resources import ResourceMonitor
from .sinks import SINKS, SinkSpec, _TimingSink

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Streaming stats sink
# ---------------------------------------------------------------------------


class _StreamingStatsSink:
    """Accumulate batches per-table, flush on table boundary, release immediately.

    Replaces ``InMemorySink`` for the mssql→arrow edge.  Peak memory is
    bounded by the largest single table rather than the entire database.

    Sink protocol (mirrors InMemorySink):
    - ``open_table`` / ``write_batch`` / ``close()`` cycle once per **rowgroup**
      (not per table).  For columnstore a single table emits multiple such
      cycles with the same fqn.  ``close()`` is therefore treated as a rowgroup
      boundary only; the table boundary is detected by an fqn *change* in
      ``open_table`` or by ``finish()``.

    At each table boundary the accumulated batches are materialised into a
    single Arrow Table, stats are computed (and optional cell verification is
    run), then the Arrow Table and batches are freed before the next table
    starts accumulating.
    """

    def __init__(
        self,
        cells_dir: Path | None,
        want_cells: bool,
        manifest_by_fqn: dict[str, Any],
        verify_level: str = "digest",
    ) -> None:
        self._cells_dir = cells_dir
        self._want_cells = want_cells
        self._manifest_by_fqn = manifest_by_fqn
        self._verify_level = verify_level
        # Current fqn being accumulated (persists across close() calls for the
        # same table so consecutive rowgroup cycles accumulate correctly).
        self._current_fqn: str | None = None
        self._batches_by_fqn: dict[str, list[pa.RecordBatch]] = {}
        self._schemas_by_fqn: dict[str, pa.Schema] = {}
        self.arrow_node: NodeStats = {}
        self.verify_results: dict[str, Any] = {}  # fqn -> TableVerifyResult
        self.verify_s: float = 0.0  # cumulative time inside verify_table calls

    def open_table(
        self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None
    ) -> None:
        if qualified_name != self._current_fqn and self._current_fqn is not None:
            # fqn changed → the previous table is complete; materialise + release.
            self._flush_fqn(self._current_fqn)
        self._current_fqn = qualified_name
        self._schemas_by_fqn.setdefault(qualified_name, schema)
        self._batches_by_fqn.setdefault(qualified_name, [])

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        if self._current_fqn is not None:
            self._batches_by_fqn[self._current_fqn].append(batch)

    def close(self) -> None:
        """Rowgroup boundary — do not flush; more batches may arrive for this fqn."""

    def finish(self) -> None:
        """End of extraction — flush the last (current) table."""
        if self._current_fqn is not None:
            self._flush_fqn(self._current_fqn)

    def _flush_fqn(self, fqn: str) -> None:
        """Materialise, compute stats, optionally verify, then discard batches."""
        batches = self._batches_by_fqn.pop(fqn, [])
        schema = self._schemas_by_fqn.pop(fqn, None)
        if not batches:
            return
        tbl = pa.Table.from_batches(batches, schema=schema)
        if len(tbl) > 0:
            self.arrow_node[fqn] = _node_stats_from_arrow_table(fqn, tbl)
            if self._want_cells and self._cells_dir is not None:
                entry = self._manifest_by_fqn.get(fqn)
                if entry is not None:
                    t_v = time.perf_counter()
                    try:
                        vr = value_verify.verify_table(
                            tbl, self._cells_dir, entry, level=self._verify_level
                        )
                        self.verify_results[fqn] = vr
                    except Exception as exc:
                        vr2 = value_verify.TableVerifyResult(fqn=fqn, mode="full")
                        vr2.error = str(exc)
                        self.verify_results[fqn] = vr2
                    finally:
                        self.verify_s += time.perf_counter() - t_v
        del tbl


# ---------------------------------------------------------------------------
# Memory helpers
# ---------------------------------------------------------------------------


def _release_arrow_memory() -> None:
    """Return freed Arrow / jemalloc pages to the OS immediately.

    Call between table processing steps and after each sink readback to keep
    resident set from ratcheting up across a long run.
    """
    gc.collect()
    try:
        pa.default_memory_pool().release_unused()
    except Exception:
        pass
    try:
        pa.jemalloc_memory_pool().release_unused()
    except Exception:
        pass
    try:
        pa.jemalloc_set_decay_ms(0)
    except Exception:
        pass


def _estimate_peak_mb(bak_path: Path, stats_path: Path | None) -> float:
    """Estimate peak resident MB for one fixture (used by the budget scheduler).

    Calibrated against 2017 observed peaks:
    - Process baseline + Rust overhead alone accounts for ~160 MB regardless of
      data volume, so the floor is set to 400 MB to cover the majority of
      fixtures without constraining scheduling too tightly.
    - Large columnstore fixtures can reach ~25× bak_size (e.g. 41 MB bak →
      924 MB peak), so a multiplier of 25 is used above the floor.
    - Uses ``bak_size_mb`` from the stats JSON when available.
    """
    try:
        if stats_path is not None and stats_path.exists():
            gt = json.loads(stats_path.read_text())
            size_mb: float = gt.get("bak_size_mb") or 0.0
            if size_mb > 0:
                return max(size_mb * 25.0, 400.0)
    except Exception:
        pass
    try:
        return max(bak_path.stat().st_size / (1024 * 1024) * 25.0, 400.0)
    except Exception:
        return 600.0


# ---------------------------------------------------------------------------
# Catalog helpers
# ---------------------------------------------------------------------------



def _resolve_bak_input(bak_path: Path) -> Path | list[Path]:
    stem = bak_path.stem
    m = re.match(r"^(.+)_(\d)$", stem)
    if m:
        prefix = m.group(1)
        siblings = sorted(
            bak_path.parent.glob(f"{prefix}_?.bak"),
            key=lambda p: int(re.search(r"_(\d)$", p.stem).group(1)),  # type: ignore[union-attr]
        )
        if len(siblings) > 1:
            return siblings
    full_stem = re.sub(r"_diff(_.+)?$", "_full", stem)
    if full_stem != stem:
        full_path = bak_path.parent / f"{full_stem}.bak"
        if full_path.exists():
            return [full_path, bak_path]
    return bak_path


# ---------------------------------------------------------------------------
# Core per-fixture runner
# ---------------------------------------------------------------------------


def _run_one(
    bak_path: Path,
    stats_path: Path,
    bak_url: str | None = None,
    *,
    sink_names: list[str] | None = None,
    outdir: Path | None = None,
    reports_dir: Path | None = None,
    run_id: str = "",
    source_mode: str = "local",
    verify_level: str = "digest",
) -> dict[str, Any]:
    """Extract one .bak, fan out to sinks, read each back, compute all edges.

    Memory profile (Phase 1):
    - Peak during extraction ≈ one table's batches (streaming sink flushes in
      close() and frees all batches before the next table starts).
    - Peak during sink readback ≈ one table (iter_tables yields one at a time).
    - Arrow pages are returned to the OS between tables via _release_arrow_memory().
    """
    mon = ResourceMonitor()
    mon.snapshot("start")  # true process baseline before any bak I/O

    ground_truth: dict[str, Any] = json.loads(stats_path.read_text())
    expected_skips = expected_skipped_tables(bak_path.stem)

    _local_input = _resolve_bak_input(bak_path)
    if bak_url is not None:
        _base_url = bak_url.rsplit("/", 1)[0]
        if isinstance(_local_input, list):
            bak_input: str | Path | list[str] | list[Path] = [
                f"{_base_url}/{p.name}" for p in _local_input
            ]
        else:
            bak_input = bak_url
    else:
        bak_input = _local_input

    cells_dir = value_verify.cells_dir_for(bak_path)
    want_cells = cells_dir.exists() and verify_level != "none"
    stem = bak_path.stem

    gt_node, total_src_rows, total_src_cols = _node_stats_from_ground_truth(ground_truth)

    # Load the cell-verification manifest once upfront so verify_table can be
    # called per-table without re-reading _manifest.json on each call.
    manifest_by_fqn: dict[str, Any] = {}
    if want_cells:
        try:
            manifest = value_verify.load_manifest(cells_dir)
            manifest_by_fqn = {e["fqn"]: e for e in manifest.get("tables", [])}
        except Exception:
            pass

    # --- Prepare sinks ---
    active_sinks: list[str] = list(sink_names or [])
    active_specs: list[SinkSpec] = [SINKS[n] for n in active_sinks]
    timing_sinks: list[_TimingSink] = []
    base: Path | None = None

    streaming_sink = _StreamingStatsSink(
        cells_dir if want_cells else None,
        want_cells,
        manifest_by_fqn,
        verify_level=verify_level,
    )
    all_sinks: list[Any] = [streaming_sink]

    if active_specs and outdir is not None:
        base = outdir / stem
        for spec in active_specs:
            sink_root = base / spec.name
            shutil.rmtree(sink_root, ignore_errors=True)
            sink_root.mkdir(parents=True, exist_ok=True)
            real_sink = spec.make(sink_root)
            tsink = _TimingSink(real_sink)
            timing_sinks.append(tsink)
            all_sinks.append(tsink)

    # extract_bak automatically wraps non-ResumableSinks in AsyncWriterSink on
    # the serial decode path so sink writes overlap Rust/xpress_lz77 decode.
    combined_sink: Any = MultiSink(*all_sinks) if len(all_sinks) > 1 else streaming_sink

    # --- Extract once; streaming_sink processes each table in close() ---
    mon.snapshot("before_extract")
    t0 = time.perf_counter()
    extract_report = extract_bak(bak_input, combined_sink)
    extract_s = round(time.perf_counter() - t0, 3)
    mon.snapshot("after_extract")

    # Table-type labels come from the extract pass; no separate catalog read needed.
    table_types = extract_report.table_types

    write_s: dict[str, float] = {
        spec.name: tsink.elapsed_s for spec, tsink in zip(active_specs, timing_sinks)
    }
    _phases = dict(extract_report.phase_timings)
    _catalog_s = round(
        _phases.get("schema_recover_s", 0.0)
        + _phases.get("lsn_s", 0.0)
        + _phases.get("catalog_recover_s", 0.0)
        + _phases.get("constraints_s", 0.0),
        3,
    )
    # With the async writer, sink writes run on a background thread that overlaps
    # the decode loop, so data_decode_s no longer includes sink write or arrow
    # verify time (they are drained in sink_finish_s instead).  Report the raw
    # data_decode_s as the net decode figure.
    _arrow_verify_s = round(streaming_sink.verify_s, 3)
    _sink_write_total = sum(write_s.values())
    data_decode_net_s = round(_phases.get("data_decode_s", 0.0), 3)

    # streaming_sink has per-table stats; all raw batches already freed.
    arrow_node = streaming_sink.arrow_node
    arrow_verify_results = streaming_sink.verify_results
    fqn_list = list(arrow_node.keys())

    _release_arrow_memory()

    # --- mssql→arrow edge (always computed) ---
    mssql_arrow_tables = _compare_tables(
        gt_node,
        arrow_node,
        table_types=table_types,
        expected_skips=expected_skips,
        normalize_col=lambda col: col,
    )
    if want_cells and arrow_verify_results:
        _apply_precomputed_cell_results(mssql_arrow_tables, arrow_verify_results)

    edges: dict[str, dict[str, Any]] = {
        "mssql_arrow": {"tables": mssql_arrow_tables, "write_s": None, "readback_s": None},
    }

    # --- Read each sink back one table at a time and compute its edges ---
    # Record the verify time that ran during extraction (hidden inside extract_s).
    verify_s: dict[str, float] = {"mssql_arrow": round(streaming_sink.verify_s, 3)}
    readback_s: dict[str, float] = {}
    read_s: dict[str, float] = {}    # time spent inside iter_tables (pure I/O + decode)
    stats_s: dict[str, float] = {}   # time spent in _node_stats_from_arrow_table
    for spec, tsink in zip(active_specs, timing_sinks):
        if base is None:
            continue
        sink_root = base / spec.name
        sink_node: NodeStats = {}
        sink_verify_results: dict[str, Any] = {}

        _read = _stats = _verify = 0.0
        t_rb = time.perf_counter()
        _it = spec.iter_tables(sink_root, fqn_list)
        while True:
            t_r = time.perf_counter()
            try:
                fqn, sink_tbl = next(_it)
            except StopIteration:
                break
            _read += time.perf_counter() - t_r

            if len(sink_tbl) > 0:
                t_s = time.perf_counter()
                sink_node[fqn] = _node_stats_from_arrow_table(fqn, sink_tbl)
                _stats += time.perf_counter() - t_s

                if want_cells and manifest_by_fqn:
                    entry = manifest_by_fqn.get(fqn)
                    if entry is not None:
                        t_v = time.perf_counter()
                        try:
                            vr = value_verify.verify_table(
                                sink_tbl, cells_dir, entry, level=verify_level
                            )
                            sink_verify_results[fqn] = vr
                        except Exception as exc:
                            vr2 = value_verify.TableVerifyResult(fqn=fqn, mode="full")
                            vr2.error = str(exc)
                            sink_verify_results[fqn] = vr2
                        finally:
                            _verify += time.perf_counter() - t_v

            del sink_tbl
            _release_arrow_memory()

        readback_s[spec.name] = round(time.perf_counter() - t_rb, 3)
        read_s[spec.name] = round(_read, 3)
        stats_s[spec.name] = round(_stats, 3)
        verify_s[spec.name] = round(_verify, 3)
        mon.snapshot(f"after_readback_{spec.name}")

        # arrow → sink (write fidelity)
        arrow_sink_tables = _compare_tables(
            arrow_node,
            sink_node,
            table_types=table_types,
            expected_skips=frozenset(),
            normalize_col=spec.normalize_col,
        )

        # sink → arrow (end-to-end vs GT)
        sink_arrow_tables = _compare_tables(
            gt_node,
            sink_node,
            table_types=table_types,
            expected_skips=expected_skips,
            normalize_col=spec.normalize_col,
        )
        if want_cells and sink_verify_results:
            _apply_precomputed_cell_results(sink_arrow_tables, sink_verify_results)

        edges[f"arrow_{spec.name}"] = {
            "tables": arrow_sink_tables,
            "write_s": write_s.get(spec.name),
            "readback_s": readback_s[spec.name],
        }
        edges[f"{spec.name}_arrow"] = {
            "tables": sink_arrow_tables,
            "write_s": write_s.get(spec.name),
            "readback_s": readback_s[spec.name],
        }

    _release_arrow_memory()

    # --- Write per-edge JSON reports ---
    if reports_dir is not None and run_id:
        meta: dict[str, Any] = {
            "run_id": run_id,
            "source_mode": source_mode,
            "bak": bak_path.name,
            "sql_version": ground_truth.get("sql_version", ""),
            "bak_size_mb": ground_truth.get("bak_size_mb", 0),
            "total_src_rows": total_src_rows,
            "total_src_cols": total_src_cols,
            "extract_s": extract_s,
            "write_s": write_s,
            "readback_s": readback_s,
        }
        for edge_name, edge_data in edges.items():
            payload = {**meta, "edge": edge_name, "tables": edge_data["tables"]}
            _write_edge_json(reports_dir, stem, run_id, edge_name, payload)

    mon.snapshot("done")

    return {
        "bak": bak_path.name,
        "sql_version": ground_truth.get("sql_version", ""),
        "bak_size_mb": ground_truth.get("bak_size_mb", 0),
        "extract_s": extract_s,
        "write_s": write_s,
        "readback_s": readback_s,
        "read_s": read_s,
        "stats_s": stats_s,
        "verify_s": verify_s,
        "phases": _phases,
        "catalog_s": _catalog_s,
        "data_decode_net_s": data_decode_net_s,
        "run_id": run_id,
        "source_mode": source_mode,
        "tables": mssql_arrow_tables,
        "edges": edges,
        "total_src_rows": total_src_rows,
        "total_src_cols": total_src_cols,
        "resources": mon.to_dict(),
    }


# ---------------------------------------------------------------------------
# Confidence-only path (no stats.json)
# ---------------------------------------------------------------------------


def _confidence_check_to_dict(check: ConfidenceCheck) -> dict[str, Any]:
    return {
        "name": check.name,
        "severity": check.severity.value,
        "message": check.message,
        "table": check.table,
        "evidence": check.evidence,
    }


def _confidence_report_to_dict(report: ConfidenceReport) -> dict[str, Any]:
    return {
        "status": report.status.value,
        "checks": [_confidence_check_to_dict(check) for check in report.checks],
    }


def _run_confidence_only(bak_path: Path) -> dict[str, Any]:
    report = analyze_bak(bak_path)
    return {
        "bak": bak_path.name,
        "sql_version": "",
        "bak_size_mb": round(bak_path.stat().st_size / (1024 * 1024), 3),
        "extract_s": 0,
        "tables": [],
        "total_src_rows": 0,
        "total_src_cols": 0,
        "confidence": _confidence_report_to_dict(report),
    }


# ---------------------------------------------------------------------------
# Case runners
# ---------------------------------------------------------------------------


def _run_case(
    bak_path: Path,
    stats_path: Path | None,
    bak_url: str | None = None,
    *,
    sink_names: list[str] | None = None,
    outdir: Path | None = None,
    reports_dir: Path | None = None,
    run_id: str = "",
    source_mode: str = "local",
    verify_level: str = "digest",
) -> dict[str, Any]:
    """Run one correctness/confidence case and record full wall time.

    Set MSSQLBAK_FAULTHANDLER=1 in the environment to enable periodic stack
    dumps every 60 s (via :mod:`faulthandler`). Useful for locating hangs:
    the traceback identifies which function is spinning.

    Set MSSQLBAK_LOG_LEVEL=INFO (or DEBUG) to get per-table extraction logs
    from :mod:`mssqlbak.extract`; the last logged table before a hang is the
    culprit.
    """
    if os.environ.get("MSSQLBAK_FAULTHANDLER"):
        faulthandler.dump_traceback_later(60, repeat=True, file=sys.stderr)

    if os.environ.get("MSSQLBAK_LOG_LEVEL"):
        logging.basicConfig(
            level=os.environ["MSSQLBAK_LOG_LEVEL"].upper(),
            format="%(name)s %(levelname)s %(message)s",
            stream=sys.stderr,
        )

    t0 = time.perf_counter()
    result = (
        _run_confidence_only(bak_path)
        if stats_path is None
        else _run_one(
            bak_path,
            stats_path,
            bak_url,
            sink_names=sink_names,
            outdir=outdir,
            reports_dir=reports_dir,
            run_id=run_id,
            source_mode=source_mode,
            verify_level=verify_level,
        )
    )
    result["wall_s"] = round(time.perf_counter() - t0, 3)

    if os.environ.get("MSSQLBAK_FAULTHANDLER"):
        faulthandler.cancel_dump_traceback_later()

    return result


def _run_logged_case(
    bak_path: Path,
    stats_path: Path | None,
    bak_url: str | None = None,
    *,
    sink_names: list[str] | None = None,
    outdir: Path | None = None,
    reports_dir: Path | None = None,
    run_id: str = "",
    source_mode: str = "local",
    verify_level: str = "digest",
) -> dict[str, Any]:
    """Worker entrypoint that logs when the case actually starts."""
    label = bak_url if bak_url is not None else bak_path.name
    print(f"  processing {label} …", file=sys.stderr, flush=True)
    return _run_case(
        bak_path,
        stats_path,
        bak_url,
        sink_names=sink_names,
        outdir=outdir,
        reports_dir=reports_dir,
        run_id=run_id,
        source_mode=source_mode,
        verify_level=verify_level,
    )


# ---------------------------------------------------------------------------
# Parallel dispatcher with memory-budget admission control
# ---------------------------------------------------------------------------


def _run_cases(
    cases: list[tuple[Path, Path | None]],
    *,
    threads: int,
    mem_budget_mb: float = 8 * 1024,
    http_port: int | None = None,
    sink_names: list[str] | None = None,
    outdir: Path | None = None,
    reports_dir: Path | None = None,
    run_id: str = "",
    source_mode: str = "local",
    verify_level: str = "digest",
) -> list[dict[str, Any]]:
    """Run selected cases, preserving input order even when threaded.

    When *http_port* is set each ``.bak`` is rewritten to
    ``http://127.0.0.1:{http_port}/{bak_path.name}`` and that URL is passed
    to extraction so the full remote-reader / LazyPageStore path is exercised.

    The *mem_budget_mb* budget gates how many fixtures run concurrently:
    estimated fixture peaks are summed; a new worker is admitted only when the
    sum stays under the budget (or no other worker is running, so progress is
    always guaranteed).  ``--threads`` remains a hard upper bound on workers.

    Each worker process handles exactly one fixture (``max_tasks_per_child=1``)
    so that any fragmented jemalloc arenas are fully freed between fixtures.
    """
    if threads < 1:
        raise ValueError("--threads must be >= 1")
    if not cases:
        return []

    def _url(bak_path: Path) -> str | None:
        return f"http://127.0.0.1:{http_port}/{bak_path.name}" if http_port else None

    kw: dict[str, Any] = dict(
        sink_names=sink_names,
        outdir=outdir,
        reports_dir=reports_dir,
        run_id=run_id,
        source_mode=source_mode,
        verify_level=verify_level,
    )

    if threads == 1:
        serial_results: list[dict[str, Any]] = []
        for bak_path, stats_path in cases:
            try:
                serial_results.append(_run_logged_case(bak_path, stats_path, _url(bak_path), **kw))
                _release_arrow_memory()
            except Exception as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)
        return serial_results

    max_workers = min(threads, len(cases))
    results: list[dict[str, Any] | None] = [None] * len(cases)

    # Allocator env vars: encourage glibc malloc (and jemalloc fallback) to
    # return freed pages to the OS promptly.
    os.environ.setdefault("MALLOC_MMAP_THRESHOLD_", "131072")
    os.environ.setdefault("MALLOC_TRIM_THRESHOLD_", "131072")

    executor_kw: dict[str, Any] = {"max_workers": max_workers}
    try:
        # max_tasks_per_child is Python 3.11+; recycles worker processes so
        # that fragmented jemalloc arenas are freed between fixtures.
        executor_kw["max_tasks_per_child"] = 1
        with ProcessPoolExecutor(**executor_kw) as _test:
            pass
    except TypeError:
        executor_kw.pop("max_tasks_per_child", None)

    with ProcessPoolExecutor(**executor_kw) as executor:
        active: dict[Any, tuple[int, Path, float]] = {}  # future → (idx, path, est_mb)
        queue = list(enumerate(cases))
        reserved_mb: float = 0.0

        def _fill() -> None:
            nonlocal reserved_mb
            while queue and len(active) < max_workers:
                # Scan the full queue for the first fixture whose estimate fits
                # inside the remaining budget.  This avoids one large fixture
                # blocking all smaller ones that come later in the queue.
                chosen_i: int | None = None
                chosen_est: float = 0.0
                for i, (_, (bp, sp)) in enumerate(queue):
                    est_i = _estimate_peak_mb(bp, sp)
                    if reserved_mb + est_i <= mem_budget_mb:
                        chosen_i, chosen_est = i, est_i
                        break
                if chosen_i is None:
                    if not active:
                        # Nothing fits even alone; admit the head anyway so
                        # progress is always guaranteed (solo run).
                        chosen_i = 0
                        chosen_est = _estimate_peak_mb(
                            queue[0][1][0], queue[0][1][1]
                        )
                    else:
                        break  # wait for a running worker to finish
                qidx, (bak_path, stats_path) = queue.pop(chosen_i)
                reserved_mb += chosen_est
                fut = executor.submit(
                    _run_logged_case, bak_path, stats_path, _url(bak_path), **kw
                )
                active[fut] = (qidx, bak_path, chosen_est)

        _fill()

        while active:
            done, _ = wait(list(active), return_when=FIRST_COMPLETED)
            for fut in done:
                idx, bak_path, est_mb = active.pop(fut)
                reserved_mb = max(0.0, reserved_mb - est_mb)
                try:
                    results[idx] = fut.result()
                    print(f"  finished {bak_path.name}", file=sys.stderr)
                except Exception as exc:
                    print(f"  ERROR: {exc}", file=sys.stderr)
            _fill()

    return [result for result in results if result is not None]
