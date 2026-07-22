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
import traceback
from concurrent.futures import BrokenExecutor, FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

import pyarrow as pa

from mssqlbak.confidence import ConfidenceCheck, ConfidenceReport, analyze_bak
from mssqlbak.extract import extract_bak
from mssqlbak.sink import MultiSink
from mssqlbak.sinks.async_writer_sink import AsyncWriterSink
from tools import value_verify
from tools.enc_cert_resolver import CertInfo, resolve_cert
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
from .sinks import SINKS, SinkSpec, _TimingSink, _READBACK_ERROR

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
                    self.verify_results[fqn] = _verify_one(
                        tbl, self._cells_dir, entry, self._verify_level
                    )
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


# Safety margin applied on top of the observed hwm_rss_mb when calibrating from a
# prior .resources.json.  15% absorbs run-to-run peak variance (different data
# paths, GC timing, Arrow pool watermarks) without being so large that calibration
# reverts to the heuristic for fixtures just below a budget boundary.
_PEAK_SAFETY_MARGIN = 1.15


def _estimate_peak_mb(
    bak_path: Path,
    stats_path: Path | None,
    prior_peaks: dict[str, float] | None = None,
) -> float:
    """Estimate peak resident MB for one fixture (used by the budget scheduler).

    When *prior_peaks* is supplied (populated from the prior run's
    ``<out>.resources.json`` by ``_parse_prior_peaks``), the observed
    ``hwm_rss_mb`` (OS high-water mark) is used with a 15% safety margin.
    This replaces the conservative ``bak_size × 25`` heuristic for known
    fixtures and makes it safe to raise ``--mem-budget-gb`` beyond the default.

    Falls back to ``bak_size × 25`` for new fixtures with no prior observation.
    Calibrated against 2017 observed peaks:
    - Process baseline + Rust overhead alone accounts for ~160 MB regardless of
      data volume, so the floor is set to 400 MB to cover the majority of
      fixtures without constraining scheduling too tightly.
    - Large columnstore fixtures can reach ~25× bak_size (e.g. 41 MB bak →
      924 MB peak), so a multiplier of 25 is used above the floor.
    - Uses ``bak_size_mb`` from the stats JSON when available.
    """
    if prior_peaks:
        hwm = prior_peaks.get(bak_path.name)
        if hwm and hwm > 0:
            return max(hwm * _PEAK_SAFETY_MARGIN, 400.0)
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
# Per-fixture helpers
# ---------------------------------------------------------------------------


def _error_result(bak_path: Path, exc: BaseException) -> dict[str, Any]:
    """Build a minimal result dict for a fixture that failed or crashed.

    Keeps the fixture visible in the rendered report as an explicit failure row
    rather than silently disappearing from the results list.
    """
    return {
        "bak": bak_path.name,
        "sql_version": "",
        "bak_size_mb": 0,
        "extract_s": 0,
        "tables": [],
        "edges": {},
        "total_src_rows": 0,
        "total_src_cols": 0,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "crashed": True,
    }


# Fixtures known to raise EncryptedBackupError by design (backup-level TDE
# without a recoverable certificate).  Once tde_full is regenerated with
# a saved cert, it moves out of this set — see enc_cert_resolver.py.
_BACKUP_LEVEL_TDE_FIXTURES: frozenset[str] = frozenset()


def _expected_encrypted_skip_result(bak_path: Path, exc: BaseException) -> dict[str, Any]:
    """Build a result dict for a fixture that is expected to be unreadable.

    ``tde_full.bak`` uses backup-level WITH ENCRYPTION and is intentionally
    unrestorable.  It verifies that mssqlbak raises EncryptedBackupError rather
    than crashing.  Recording it as an expected skip (not a crash) keeps the
    overall pass rate meaningful.
    """
    return {
        "bak": bak_path.name,
        "sql_version": "",
        "bak_size_mb": 0,
        "extract_s": 0,
        "tables": [],
        "edges": {},
        "total_src_rows": 0,
        "total_src_cols": 0,
        "error": f"expected-skip (backup-level TDE): {exc}",
        "traceback": "",
        "crashed": False,
        "expected_skip": True,
    }


def _verify_one(
    tbl: "pa.Table",
    cells_dir: Path,
    entry: dict[str, Any],
    level: str,
) -> "value_verify.TableVerifyResult":
    """Run verify_table for one table, converting exceptions to error results.

    Centralises the try/except/log pattern shared by _StreamingStatsSink._flush_fqn
    and the readback verify loop so both callers get identical error semantics.
    """
    fqn: str = entry.get("fqn", "")
    try:
        return value_verify.verify_table(tbl, cells_dir, entry, level=level)
    except Exception as exc:
        log.exception("verify_table failed for %s", fqn)
        vr = value_verify.TableVerifyResult(fqn=fqn, mode="full")
        vr.error = f"{exc}\n{traceback.format_exc()}"
        return vr


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

    _cert_info: CertInfo | None = resolve_cert(bak_path)

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

    if active_specs and outdir is not None:
        base = outdir / stem
        for spec in active_specs:
            sink_root = base / spec.name
            shutil.rmtree(sink_root, ignore_errors=True)
            sink_root.mkdir(parents=True, exist_ok=True)
            real_sink = spec.make(sink_root)
            tsink = _TimingSink(real_sink)
            timing_sinks.append(tsink)

    # Overlap decode with the real I/O sinks (delta, pg_dir) by driving ONLY them
    # on a background writer thread.  The stats/verify sink stays synchronous on
    # the main thread: its digest builds zero-copy numpy views over Arrow buffers,
    # which is unsafe to run concurrently with the main-thread Rust decode
    # recycling those buffers.  We therefore pass async_writes=False so
    # extract_bak does not wrap the whole MultiSink, and wrap the I/O sinks here.
    combined_sink: Any
    if timing_sinks:
        io_sink: Any = MultiSink(*timing_sinks) if len(timing_sinks) > 1 else timing_sinks[0]
        combined_sink = MultiSink(streaming_sink, AsyncWriterSink(io_sink))
    else:
        combined_sink = streaming_sink

    # --- Extract once; streaming_sink processes each table in close() ---
    _extract_kwargs: dict[str, Any] = {}
    if _cert_info is not None:
        if _cert_info.kind == "backup":
            _extract_kwargs["backup_cert"] = _cert_info.tde_key
        elif _cert_info.kind == "backup_tde":
            # Double-encrypted: same key serves backup-level AND TDE layers.
            _extract_kwargs["backup_cert"] = _cert_info.tde_key
            _extract_kwargs["tde_key"] = _cert_info.tde_key
        else:
            _extract_kwargs["tde_key"] = _cert_info.tde_key
    mon.snapshot("before_extract")
    t0 = time.perf_counter()
    extract_report = extract_bak(bak_input, combined_sink, async_writes=False, **_extract_kwargs)
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
        _readback_infra_error: str | None = None
        while True:
            t_r = time.perf_counter()
            try:
                fqn, sink_tbl = next(_it)
            except StopIteration:
                break
            _read += time.perf_counter() - t_r

            # Sentinel: the iterator encountered a fatal infra error (e.g.
            # missing sink output directory or toc.dat).  Record the error
            # and stop reading — do not score as a data mismatch.
            if sink_tbl is _READBACK_ERROR:
                _readback_infra_error = (
                    f"sink output missing or unreadable at {sink_root}"
                )
                log.error(
                    "Sink readback infra error for %s/%s: %s",
                    bak_path.stem, spec.name, _readback_infra_error,
                )
                break

            assert isinstance(sink_tbl, pa.Table)  # narrow type for mypy
            if len(sink_tbl) > 0:
                t_s = time.perf_counter()
                sink_node[fqn] = _node_stats_from_arrow_table(fqn, sink_tbl)
                _stats += time.perf_counter() - t_s

                if want_cells and manifest_by_fqn:
                    entry = manifest_by_fqn.get(fqn)
                    if entry is not None:
                        t_v = time.perf_counter()
                        sink_verify_results[fqn] = _verify_one(
                            sink_tbl, cells_dir, entry, verify_level
                        )
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
            "readback_error": _readback_infra_error,
        }
        edges[f"{spec.name}_arrow"] = {
            "tables": sink_arrow_tables,
            "write_s": write_s.get(spec.name),
            "readback_s": readback_s[spec.name],
            "readback_error": _readback_infra_error,
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

    # --- Metadata validation (when sidecar is present) ----------------------
    validations: dict[str, Any] = {}
    metadata_sidecar = bak_path.with_suffix(bak_path.suffix + ".metadata.json")
    if metadata_sidecar.exists():
        try:
            import json as _json
            from tools.correctness_coverage.metadata_verify import build_recovered_metadata
            from tools.correctness_coverage.validators import get_validators

            _meta_gt = _json.loads(metadata_sidecar.read_text())
            _bak_local_input = _resolve_bak_input(bak_path)
            _meta_kwargs: dict[str, Any] = {}
            if _cert_info is not None:
                if _cert_info.kind == "backup":
                    _meta_kwargs["backup_cert"] = _cert_info.tde_key
                elif _cert_info.kind == "backup_tde":
                    _meta_kwargs["backup_cert"] = _cert_info.tde_key
                    _meta_kwargs["tde_key"] = _cert_info.tde_key
                else:
                    _meta_kwargs["tde_key"] = _cert_info.tde_key
            _rm = build_recovered_metadata(_bak_local_input, **_meta_kwargs)
            _validators = get_validators()
            for _cat_name, _spec in _validators.items():
                try:
                    _vr = _spec.run(_meta_gt, _rm)
                except Exception as _exc:
                    import traceback as _tb
                    from tools.correctness_coverage.metadata_verify import ValidationResult as _VR
                    _vr = _VR(
                        category=_cat_name,
                        error=f"{_exc}\n{_tb.format_exc()}",
                    )
                validations[_cat_name] = _vr.to_dict()
        except Exception:
            log.exception("Metadata validation failed for %s", bak_path.name)

    # Persist validations alongside edge JSONs for --assemble-only support.
    if validations and reports_dir is not None and run_id:
        _write_edge_json(reports_dir, stem, run_id, "_validations", {"validations": validations})

    mon.snapshot("done")

    result: dict[str, Any] = {
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
    if validations:
        result["validations"] = validations
    return result


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
    _cert_info = resolve_cert(bak_path)
    _analyze_kwargs: dict[str, Any] = {}
    if _cert_info is not None:
        if _cert_info.kind == "backup":
            _analyze_kwargs["backup_cert"] = _cert_info.tde_key
        elif _cert_info.kind == "backup_tde":
            _analyze_kwargs["backup_cert"] = _cert_info.tde_key
            _analyze_kwargs["tde_key"] = _cert_info.tde_key
        else:
            _analyze_kwargs["tde_key"] = _cert_info.tde_key
    report = analyze_bak(bak_path, **_analyze_kwargs)
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
    try:
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
    except Exception as _enc_exc:
        from mssqlbak.errors import EncryptedBackupError
        if (
            isinstance(_enc_exc, EncryptedBackupError)
            and bak_path.stem in _BACKUP_LEVEL_TDE_FIXTURES
        ):
            # Expected: tde_full.bak is a backup-level TDE fixture that must
            # raise EncryptedBackupError — record as expected skip, not crash.
            result = _expected_encrypted_skip_result(bak_path, _enc_exc)
        else:
            raise
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
    """Worker entrypoint that logs when the case actually starts.

    Any exception that escapes this function is pickled by
    ``ProcessPoolExecutor`` before being sent back to the parent process.
    delta-rs ``_internal.*`` exception classes are defined in a Rust
    extension and cannot be pickled, causing the parent to see a
    ``PicklingError`` instead of the real error.  We therefore catch *all*
    exceptions here, verify they can be pickled, and convert the
    unpicklable ones to a structured ``_error_result`` so the parent
    always receives a plain ``dict``.
    """
    import pickle as _pickle

    label = bak_url if bak_url is not None else bak_path.name
    print(f"  processing {label} …", file=sys.stderr, flush=True)
    try:
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
    except Exception as exc:
        log.exception("ERROR processing %s: %s", bak_path.name, exc)
        # Verify the exception can survive the pickling round-trip back to
        # the parent.  If it cannot, wrap it in a plain RuntimeError so the
        # parent still receives a useful error message rather than a cryptic
        # PicklingError that masks the real failure.
        try:
            _pickle.dumps(exc)
        except Exception:
            exc = RuntimeError(
                f"{type(exc).__name__}: {exc}\n"
                f"(original exception could not be pickled)"
            )
        return _error_result(bak_path, exc)


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
    prior_peaks: dict[str, float] | None = None,
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
                log.exception("ERROR processing %s: %s", bak_path.name, exc)
                serial_results.append(_error_result(bak_path, exc))
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
        pool_broken: bool = False

        def _fill() -> None:
            nonlocal reserved_mb, pool_broken
            if pool_broken:
                return
            while queue and len(active) < max_workers:
                # Scan the full queue for the first fixture whose estimate fits
                # inside the remaining budget.  This avoids one large fixture
                # blocking all smaller ones that come later in the queue.
                # NOTE: fixtures whose estimate exceeds the entire budget can
                # only be admitted via the solo fallback below (when active is
                # empty), so admission order can deviate from longest-first for
                # over-budget giants.  Raise --mem-budget-gb to reduce solo
                # serialisation; calibrated estimates from prior_peaks make this
                # safe by using observed hwm_rss_mb rather than bak_size * 25.
                chosen_i: int | None = None
                chosen_est: float = 0.0
                for i, (_, (bp, sp)) in enumerate(queue):
                    est_i = _estimate_peak_mb(bp, sp, prior_peaks)
                    if reserved_mb + est_i <= mem_budget_mb:
                        chosen_i, chosen_est = i, est_i
                        break
                if chosen_i is None:
                    if not active:
                        # Nothing fits even alone; admit the head anyway so
                        # progress is always guaranteed (solo run).
                        chosen_i = 0
                        chosen_est = _estimate_peak_mb(
                            queue[0][1][0], queue[0][1][1], prior_peaks
                        )
                    else:
                        break  # wait for a running worker to finish
                qidx, (bak_path, stats_path) = queue.pop(chosen_i)
                reserved_mb += chosen_est
                try:
                    fut = executor.submit(
                        _run_logged_case, bak_path, stats_path, _url(bak_path), **kw
                    )
                except BrokenExecutor as exc:
                    pool_broken = True
                    log.error(
                        "Worker pool broken: %s — %s queued fixture(s) will not run", exc, len(queue) + 1
                    )
                    # Record the just-dequeued fixture as an error result.
                    results[qidx] = _error_result(bak_path, exc)
                    # Mark all remaining queued fixtures too.
                    while queue:
                        qi, (bp, _) = queue.pop(0)
                        results[qi] = _error_result(bp, exc)
                    return
                active[fut] = (qidx, bak_path, chosen_est)

        _fill()

        while active:
            try:
                done, _ = wait(list(active), return_when=FIRST_COMPLETED)
            except BrokenExecutor as exc:
                pool_broken = True
                log.error("Worker pool broken during wait: %s", exc)
                for fut2, (idx2, bp2, est2) in list(active.items()):
                    reserved_mb = max(0.0, reserved_mb - est2)
                    if results[idx2] is None:
                        results[idx2] = _error_result(bp2, exc)
                active.clear()
                break
            for fut in done:
                idx, bak_path, est_mb = active.pop(fut)
                reserved_mb = max(0.0, reserved_mb - est_mb)
                try:
                    results[idx] = fut.result()
                    print(f"  finished {bak_path.name}", file=sys.stderr)
                except Exception as exc:
                    log.exception("ERROR processing %s: %s", bak_path.name, exc)
                    results[idx] = _error_result(bak_path, exc)
            _fill()

    # Replace any remaining None slots (e.g. from a broken pool race) with error results.
    for i, (bak_path, _) in enumerate(cases):
        if results[i] is None:
            results[i] = _error_result(bak_path, RuntimeError("fixture never ran"))
    return [r for r in results if r is not None]
