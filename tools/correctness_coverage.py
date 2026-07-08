#!/usr/bin/env python3
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

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
import functools
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import time
from pathlib import Path
from typing import Any, Generator

import pyarrow.compute as pc

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak
from mssqlbak.pages import PageStore
from mssqlbak.sink import InMemorySink
from mssqlbak.confidence import ConfidenceCheck, ConfidenceReport, Severity, analyze_bak
from tools import value_verify
from tools.known_gaps import expected_skipped_tables, gap_reason, version_from_fixture_dir

# Data compression constants from SQL Server sys.partitions
_COMP_COLUMNSTORE = frozenset({3, 4})  # COLUMNSTORE and COLUMNSTORE_ARCHIVE


def _catalog_table_types(bak_path: Path) -> dict[str, str]:
    """Return {fqn: 'rowstore'|'columnstore'|'memory-optimized'} via catalog read."""
    try:
        store = PageStore.from_bak(str(bak_path))
        schema = recover_schema(store)
    except Exception:
        return {}
    result: dict[str, str] = {}
    for t in schema.tables:
        if t.is_memory_optimized:
            ttype = "memory-optimized"
        elif t.compression in _COMP_COLUMNSTORE:
            ttype = "columnstore"
        else:
            ttype = "rowstore"
        result[f"{t.schema}.{t.name}"] = ttype
    return result

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = REPO_ROOT / "docs" / "correctness_coverage.md"


@contextmanager
def _local_http_server(directory: Path) -> Generator[int, None, None]:
    """Spin up a local HTTP server rooted at *directory* and yield its port.

    Uses an ephemeral port (OS chooses) so multiple concurrent runs never
    conflict.  The server runs in a daemon thread and is shut down cleanly
    when the context exits.
    """
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(directory),
    )
    # silence the default request log lines that would pollute stderr
    handler.log_message = lambda *_: None  # type: ignore[method-assign]
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield port
        finally:
            httpd.shutdown()

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
# Extraction + comparison
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


def _minmax_equal(act: Any, gt_str: str | None, sql_type: str) -> bool:
    """Lightweight min/max check — mirrors test_stats._minmax_equal."""
    from decimal import Decimal, InvalidOperation
    import datetime

    if gt_str is None:
        return True
    if sql_type.lower() in _MINMAX_SKIP_TYPES:
        return True

    s = gt_str.strip()

    def parse_gt(typ: str) -> Any:
        try:
            if typ in ("int", "bigint", "smallint", "tinyint"):
                return int(s)
            if typ == "bit":
                return bool(int(s))
            if typ in ("decimal", "numeric", "money", "smallmoney"):
                return Decimal(s)
            if typ in ("float", "real"):
                return float(s)
            if typ == "date":
                return datetime.date.fromisoformat(s)
            if typ == "datetime2":
                return datetime.datetime.strptime(s[:26], "%Y-%m-%d %H:%M:%S.%f")
            if typ == "time":
                return datetime.time.fromisoformat(s[:15])
            if typ == "uniqueidentifier":
                return s.upper()
            if typ == "binary":
                return bytes.fromhex(s[2:]) if s.startswith("0x") else bytes.fromhex(s)
            if typ == "timestamp":
                return int(s, 16)
        except (ValueError, InvalidOperation, OverflowError):
            pass
        return None

    def norm_act(typ: str) -> Any:
        if act is None:
            return None
        try:
            if typ in ("int", "bigint", "smallint", "tinyint"):
                return int(act)
            if typ == "bit":
                return bool(act)
            if typ in ("decimal", "numeric", "money", "smallmoney"):
                return Decimal(str(act))
            if typ in ("float", "real"):
                return float(act)
            if typ == "time":
                if isinstance(act, str):
                    return datetime.time.fromisoformat(act[:15])
                return act
            if typ == "date":
                if isinstance(act, str):
                    return datetime.date.fromisoformat(act)
                return act
            if typ == "datetime2":
                if isinstance(act, str):
                    return datetime.datetime.strptime(act[:26], "%Y-%m-%d %H:%M:%S.%f")
                return act
            if typ == "uniqueidentifier":
                return str(act).upper()
            if typ == "binary":
                if isinstance(act, (bytes, bytearray)):
                    return bytes(act)
                return act
            if typ == "timestamp":
                if isinstance(act, (bytes, bytearray)):
                    return int.from_bytes(act, "big")
                return act
        except (ValueError, TypeError):
            pass
        return act

    typ = sql_type.lower()
    gt = parse_gt(typ)
    if gt is None:
        return True
    a = norm_act(typ)
    if typ in ("float", "real"):
        try:
            if a is None or gt == 0.0:
                return a == gt
            return abs(float(a) - float(gt)) / max(abs(float(gt)), 1e-300) < 1e-5
        except (TypeError, ZeroDivisionError):
            return a == gt
    if typ in ("char", "nchar"):
        return str(a).rstrip() == str(gt).rstrip() if a is not None else str(gt).rstrip() == ""
    # timestamp/rowversion: PAGE/ROW-compressed rows may be extracted as
    # little-endian even though the logical value is big-endian. Accept either.
    if typ == "timestamp":
        if isinstance(act, (bytes, bytearray)) and isinstance(gt, int):
            return int.from_bytes(act, "big") == gt or int.from_bytes(act, "little") == gt
    return a == gt


def _minmax_from_col(col: Any) -> tuple[Any, Any]:
    """Return (min, max) for an Arrow column using vectorized compute.

    Falls back to None/None for types unsupported by pc.min/pc.max (e.g.
    large_list, struct) and for BCE dates that overflow Python datetime.
    """
    try:
        min_v = pc.min(col).as_py()  # type: ignore[attr-defined]
        max_v = pc.max(col).as_py()  # type: ignore[attr-defined]
        return min_v, max_v
    except (ValueError, OverflowError):
        return None, None
    except Exception:  # ArrowNotImplementedError etc.
        return None, None


def _run_one(
    bak_path: Path,
    stats_path: Path,
    bak_url: str | None = None,
) -> dict[str, Any]:
    """Extract and compare one .bak; return a structured result dict."""
    ground_truth: dict[str, Any] = json.loads(stats_path.read_text())
    expected_skips = expected_skipped_tables(bak_path.stem)
    # Resolve siblings / diff-base paths locally first so the chain is always
    # complete, then optionally remap each path to its HTTP URL.
    _local_input = _resolve_bak_input(bak_path)
    if bak_url is not None:
        # Map each resolved local path to an HTTP URL served by the local
        # server.  The server root is the fixture directory, so the URL is
        # always http://host:port/<filename>.bak.
        _base_url = bak_url.rsplit("/", 1)[0]  # strip the bak filename
        if isinstance(_local_input, list):
            bak_input: str | Path | list[str] = [
                f"{_base_url}/{p.name}" for p in _local_input
            ]
        else:
            bak_input = bak_url  # single file — the URL already passed in
    else:
        bak_input = _local_input
    # Row-level cell verification runs only when a <bak>.cells/ sidecar exists
    # (produced by the ground-truth capture step). Inert otherwise.
    cells_dir = value_verify.cells_dir_for(bak_path)
    want_cells = cells_dir.exists()
    arrow_tables: dict[str, Any] = {}

    table_types = _catalog_table_types(bak_path)

    sink = InMemorySink()
    t0 = time.perf_counter()
    extract_bak(bak_input, sink)
    extract_s = round(time.perf_counter() - t0, 3)

    extracted: dict[str, dict[str, Any]] = {}
    for fqn in sink.table_names:
        tbl = sink.to_arrow_table(fqn)
        # Skip tables that produced no rows — equivalent to Delta's behaviour
        # where an empty table creates no directory and is absent from extracted,
        # allowing the downstream comparison to treat it as a known gap (xtp_skip).
        if len(tbl) == 0:
            continue
        null_counts: dict[str, int] = {}
        min_vals: dict[str, Any] = {}
        max_vals: dict[str, Any] = {}
        for col_name in tbl.schema.names:
            col = tbl.column(col_name)
            null_counts[col_name] = col.null_count if col.null_count is not None else 0
            min_vals[col_name], max_vals[col_name] = _minmax_from_col(col)
        extracted[fqn] = {
            "row_count": len(tbl),
            "null_counts": null_counts,
            "min_vals": min_vals,
            "max_vals": max_vals,
            "col_count": len(tbl.schema.names),
        }
        if want_cells:
            arrow_tables[fqn] = tbl

    tables_out: list[dict[str, Any]] = []
    total_src_rows = 0
    total_src_cols = 0

    for tbl_info in ground_truth.get("tables", []):
        schema = tbl_info["schema"]
        name = tbl_info["name"]
        expected_rows = tbl_info["row_count"]
        fqn = f"{schema}.{name}"
        columns = tbl_info.get("columns", [])

        total_src_rows += expected_rows
        n_gt_cols = len(columns)
        total_src_cols += n_gt_cols

        act = extracted.get(fqn)
        row_ok = act is not None and act["row_count"] == expected_rows
        missing_tbl = act is None and expected_rows > 0
        # Most memory-optimized tables are scored normally through the XTP CFP
        # decoder. A few real-world backups expose metadata without recoverable
        # CFP data blocks; those table-level known gaps are expected absent.
        xtp_skip = missing_tbl and fqn in expected_skips

        null_ok = null_total = 0
        minmax_ok = minmax_total = 0
        col_count_ok = act is not None and act["col_count"] >= n_gt_cols
        col_names = [col_info["name"] for col_info in columns]
        bad_columns: set[str] = set()
        if missing_tbl and expected_rows > 0 and not xtp_skip:
            bad_columns.update(col_names)

        for col_info in columns:
            col_name = col_info["name"]
            sql_type = col_info.get("sql_type", "")
            expected_nulls = col_info.get("null_count")
            gt_min = col_info.get("min_val")
            gt_max = col_info.get("max_val")

            if expected_nulls is not None and act is not None:
                null_total += 1
                if act["null_counts"].get(col_name) == expected_nulls:
                    null_ok += 1
                else:
                    bad_columns.add(col_name)

            # Min/max: only when ground truth is non-None and type is not skipped.
            if (
                gt_min is not None or gt_max is not None
            ) and sql_type.lower() not in _MINMAX_SKIP_TYPES:
                if act is not None:
                    if gt_min is not None:
                        minmax_total += 1
                        if _minmax_equal(act["min_vals"].get(col_name), gt_min, sql_type):
                            minmax_ok += 1
                        else:
                            bad_columns.add(col_name)
                    if gt_max is not None:
                        minmax_total += 1
                        if _minmax_equal(act["max_vals"].get(col_name), gt_max, sql_type):
                            minmax_ok += 1
                        else:
                            bad_columns.add(col_name)

        tables_out.append(
            {
                "fqn": fqn,
                "table_type": table_types.get(fqn, "rowstore"),
                "expected_rows": expected_rows,
                "row_ok": row_ok,
                "missing": missing_tbl,
                "xtp_skip": xtp_skip,
                "null_ok": null_ok,
                "null_total": null_total,
                "minmax_ok": minmax_ok,
                "minmax_total": minmax_total,
                "n_gt_cols": n_gt_cols,
                "col_count_ok": col_count_ok,
                "column_ok": n_gt_cols - len(bad_columns),
                "column_total": n_gt_cols,
                "_column_names": col_names,
                "_bad_columns": sorted(bad_columns),
            }
        )

    if want_cells:
        try:
            vres = value_verify.verify_bak(arrow_tables, cells_dir)
        except Exception as exc:  # capture/parse error → mark every table
            vres = {}
            for t in tables_out:
                t["value_error"] = str(exc)
        for t in tables_out:
            if t["xtp_skip"]:
                continue
            vr = vres.get(t["fqn"])
            if t.get("value_error"):
                t["_bad_columns"] = t["_column_names"]
                t["column_ok"] = 0
                continue
            if vr is None:
                continue
            t["value_mode"] = vr.mode
            t["value_ok"] = vr.cells_ok
            t["value_total"] = vr.cells_total
            t["value_bad"] = sorted(vr.col_mismatches) + [
                f"digest:{c}" for c in vr.digest_mismatches
            ]
            t["value_missing_keys"] = vr.missing_keys
            t["value_pass"] = vr.ok
            bad_columns = set(t.get("_bad_columns", []))
            bad_columns.update(vr.col_mismatches)
            bad_columns.update(vr.digest_mismatches)
            if vr.missing_keys:
                bad_columns.update(t.get("_column_names", []))
            t["_bad_columns"] = sorted(bad_columns)
            t["column_ok"] = max(0, t["n_gt_cols"] - len(bad_columns))

    return {
        "bak": bak_path.name,
        "sql_version": ground_truth.get("sql_version", ""),
        "bak_size_mb": ground_truth.get("bak_size_mb", 0),
        "extract_s": extract_s,
        "tables": tables_out,
        "total_src_rows": total_src_rows,
        "total_src_cols": total_src_cols,
    }


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


def _run_case(
    bak_path: Path,
    stats_path: Path | None,
    bak_url: str | None = None,
) -> dict[str, Any]:
    """Run one correctness/confidence case and record full wall time."""
    t0 = time.perf_counter()
    result = (
        _run_confidence_only(bak_path)
        if stats_path is None
        else _run_one(bak_path, stats_path, bak_url)
    )
    result["wall_s"] = round(time.perf_counter() - t0, 3)
    return result


def _run_logged_case(
    bak_path: Path,
    stats_path: Path | None,
    bak_url: str | None = None,
) -> dict[str, Any]:
    """Worker entrypoint that logs when the case actually starts."""
    label = bak_url if bak_url is not None else bak_path.name
    print(f"  processing {label} …", file=sys.stderr, flush=True)
    return _run_case(bak_path, stats_path, bak_url)


def _run_cases(
    cases: list[tuple[Path, Path | None]],
    *,
    threads: int,
    http_port: int | None = None,
) -> list[dict[str, Any]]:
    """Run selected cases, preserving input order even when threaded.

    When *http_port* is set each ``.bak`` is rewritten to
    ``http://127.0.0.1:{http_port}/{bak_path.name}`` and that URL is passed
    to extraction so the full remote-reader / LazyPageStore path is exercised.
    """
    if threads < 1:
        raise ValueError("--threads must be >= 1")
    if not cases:
        return []

    def _url(bak_path: Path) -> str | None:
        return f"http://127.0.0.1:{http_port}/{bak_path.name}" if http_port else None

    if threads == 1:
        serial_results: list[dict[str, Any]] = []
        for bak_path, stats_path in cases:
            try:
                serial_results.append(_run_logged_case(bak_path, stats_path, _url(bak_path)))
            except Exception as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)
        return serial_results

    max_workers = min(threads, len(cases))
    results: list[dict[str, Any] | None] = [None] * len(cases)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_run_logged_case, bak_path, stats_path, _url(bak_path)): (idx, bak_path)
            for idx, (bak_path, stats_path) in enumerate(cases)
        }
        for future in as_completed(futures):
            idx, bak_path = futures[future]
            try:
                results[idx] = future.result()
                print(f"  finished {bak_path.name}", file=sys.stderr)
            except Exception as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)

    return [result for result in results if result is not None]


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _fmt_count(ok: int, total: int) -> str:
    if total == 0:
        return "—"
    if ok == total:
        return f"**{ok}/{total}**"
    return f"{ok}/{total} ⚠"


def _value_ok(t: dict[str, Any]) -> bool:
    """True unless row-level cell verification ran for this table and failed.

    Returns True when no ``.cells/`` sidecar scored the table, so this is inert
    until ground-truth capture has produced cells.
    """
    if t.get("value_error"):
        return False
    if "value_pass" not in t:
        return True
    return bool(t["value_pass"])


def _table_ok(t: dict[str, Any]) -> bool:
    return (
        (t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"])
        and t["null_ok"] == t["null_total"]
        and t["minmax_ok"] == t["minmax_total"]
        # col_count only meaningful for non-empty tables (mssqlbak skips empty tables)
        and (t["col_count_ok"] or t["expected_rows"] == 0 or t["xtp_skip"])
        and _value_ok(t)
    )


def _cells_note(t: dict[str, Any]) -> str:
    """Compact per-table cell-verification note (empty when unscored)."""
    if t.get("value_error"):
        return f"cells: ERROR ({t['value_error']})"
    if "value_pass" not in t:
        return ""
    ok, total = t.get("value_ok", 0), t.get("value_total", 0)
    if t["value_pass"]:
        return f"cells **{ok}/{total}** ✓" if total else "cells digest ✓"
    parts: list[str] = []
    if total:
        parts.append(f"cells {ok}/{total}")
    if t.get("value_bad"):
        parts.append("bad: " + ", ".join(t["value_bad"]))
    if t.get("value_missing_keys"):
        parts.append(f"{t['value_missing_keys']} missing keys")
    return "cells ✗ (" + "; ".join(parts) + ")"


def _cells_summary(tables: list[dict[str, Any]]) -> str:
    """Fixture-level cell verification summary for the top table."""
    if any(t.get("value_error") for t in tables):
        n = sum(1 for t in tables if t.get("value_error"))
        return f"ERROR ({n} table{'s' if n != 1 else ''})"

    scored = [t for t in tables if "value_pass" in t]
    if not scored:
        if tables and all(t.get("expected_rows", 0) == 0 for t in tables):
            return "empty"
        return "—"

    ok = sum(t.get("value_ok", 0) for t in scored)
    total = sum(t.get("value_total", 0) for t in scored)
    all_pass = all(bool(t["value_pass"]) for t in scored)
    if all_pass:
        return f"**{ok}/{total}**" if total else "digest"
    return f"{ok}/{total} ⚠" if total else "digest ⚠"


def _confidence_status(r: dict[str, Any]) -> str | None:
    confidence = r.get("confidence")
    if not isinstance(confidence, dict):
        return None
    status = confidence.get("status")
    return str(status) if status else None


def _constraint_summary_line(r: dict[str, Any]) -> str:
    """Short inline constraint summary from the confidence dict (no-verifier rows)."""
    confidence = r.get("confidence")
    if not isinstance(confidence, dict):
        return ""
    checks = confidence.get("checks", [])
    if not checks:
        return ""
    n_pass = sum(1 for c in checks if c.get("severity") == Severity.PASS.value)
    n_fail = sum(1 for c in checks if c.get("severity") == Severity.FAIL.value)
    n_total = sum(1 for c in checks)
    fail_by_type: dict[str, int] = {}
    for c in checks:
        if c.get("severity") == Severity.FAIL.value:
            name = c.get("name", "?")
            fail_by_type[name] = fail_by_type.get(name, 0) + 1
    detail = ", ".join(f"{nm}: {cnt}F" for nm, cnt in sorted(fail_by_type.items()))
    detail_str = f"  [{detail}]" if detail else ""
    return f"constraints: {n_total} total · {n_pass} pass · {n_fail} fail{detail_str}"


def _confidence_summary(r: dict[str, Any]) -> str:
    confidence = r.get("confidence")
    if not isinstance(confidence, dict):
        return ""
    status = confidence.get("status", "unknown")
    checks = confidence.get("checks", [])
    bad = [
        f"{c.get('name')}: {c.get('message')}"
        for c in checks
        if c.get("severity") in {"warn", "fail"}
    ]
    if bad:
        return f"confidence {status} ({'; '.join(bad)})"
    return f"confidence {status}"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _ver_year(sql_version: str) -> str:
    """Extract the SQL Server version year (e.g. '2022') from a sql_version string."""
    import re as _re
    m = _re.search(r"(20\d{2})", sql_version)
    return m.group(1) if m else ""


def _render(
    results: list[dict[str, Any]],
    fixture_dir: Path | None = None,
    bak_paths: list[Path] | None = None,
    show_fixture_dir: bool = True,
) -> str:
    lines: list[str] = []
    version = version_from_fixture_dir(fixture_dir)

    # Always render in alphabetical order by .bak filename
    results = sorted(results, key=lambda r: r["bak"].lower())

    n_pass = n_xfail = n_fail = 0
    table_ok = table_total = 0
    column_ok = column_total = 0
    # Per-category failure counters (tables as the unit, matching column key)
    row_fail = null_fail = mm_fail = col_fail = cells_fail = 0
    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        has_tables = bool(r["tables"])
        confidence_status = _confidence_status(r)
        table_ok += sum(1 for t in r["tables"] if _table_ok(t))
        table_total += len(r["tables"])
        column_ok += sum(int(t.get("column_ok", t.get("n_gt_cols", 0))) for t in r["tables"])
        column_total += sum(int(t.get("column_total", t.get("n_gt_cols", 0))) for t in r["tables"])

        # Count tables failing each category (mirror _table_ok exclusion rules)
        for t in r["tables"]:
            if not (t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"]):
                row_fail += 1
            if t["null_ok"] < t["null_total"]:
                null_fail += 1
            if t["minmax_ok"] < t["minmax_total"]:
                mm_fail += 1
            if not (t.get("col_count_ok", True) or t["expected_rows"] == 0 or t["xtp_skip"]):
                col_fail += 1
            if not _value_ok(t):
                cells_fail += 1

        row_all_ok = all(
            t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"] for t in r["tables"]
        )
        null_all_ok = all(t["null_ok"] == t["null_total"] for t in r["tables"])
        minmax_all_ok = all(t["minmax_ok"] == t["minmax_total"] for t in r["tables"])
        value_all_ok = all(_value_ok(t) for t in r["tables"])
        all_ok = row_all_ok and null_all_ok and minmax_all_ok and value_all_ok

        if is_xfail:
            n_xfail += 1
        elif confidence_status == "fail":
            n_fail += 1
        elif all_ok or not has_tables:
            n_pass += 1
        else:
            n_fail += 1

    def _fail_label(n: int, label: str) -> str:
        return f"**{label}:** {n} fail" if n else f"**{label}:** ✓"

    category_line = " · ".join([
        _fail_label(row_fail, "Row count"),
        _fail_label(null_fail, "Null count"),
        _fail_label(mm_fail, "Min/max"),
        _fail_label(col_fail, "Col count"),
        _fail_label(cells_fail, "Cells"),
    ])

    header = (
        "# Correctness coverage\n\n"
        "Per-backup comparison of mssqlbak extraction against SQL Server ground truth.\n"
        "Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by\n"
        "`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.\n"
        f"**Generated** by `python -m tools.correctness_coverage"
        f"{f' --fixture-dir {_display_path(fixture_dir)}' if fixture_dir and show_fixture_dir else ''}"
        f"{''.join(f' {_display_path(path)}' for path in (bak_paths or []))}`.\n\n"
        f"**{n_pass + n_xfail + n_fail} fixtures · {n_pass} pass · {n_xfail} xfail (known gap) · {n_fail} fail**\n\n"
        f"**Tables:** {table_ok}/{table_total} pass · **Columns:** {column_ok}/{column_total} pass\n\n"
        f"{category_line}\n\n"
        "Column key:\n\n"
        "| Column | Meaning |\n"
        "|--------|----------|\n"
        "| Source rows | Total rows in all non-empty tables per SQL Server ground truth |\n"
        "| Source cols | Total columns tracked across all non-empty tables |\n"
        "| Row count | `matched/total` tables with correct row count |\n"
        "| Null count | `matched/total` columns with correct null count |\n"
        "| Min/max | `matched/total` comparable min/max checks; `sql_variant` and `uniqueidentifier` skipped (non-lexicographic ordering) |\n"
        "| Col count | `matched/total` tables with ≥ expected column count |\n"
        "| Cells | Row-level cell verification across tables with `<backup>.bak.cells/_manifest.json` |\n"
        "| Status | ✓ = all match · ~ = xfail (known gap) · ✗ = mismatch |\n\n"
        "Memory-optimized (In-Memory OLTP / XTP) tables store their data in XTP "
        "checkpoint file pairs (CFPs) rather than 8 KB pages.  mssqlbak decodes "
        "their rows from compact and WAL-style CFP blocks embedded in the backup, "
        "so they are scored normally against ground truth.\n"
    )
    lines.append(header)
    lines.append("## Summary\n")
    lines.append(
        "| Backup | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |"
    )
    lines.append(
        "|--------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|"
    )

    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        tables = r["tables"]
        src_rows = r["total_src_rows"]
        src_cols = r["total_src_cols"]

        if not tables:
            conf = _confidence_status(r)
            constraint_note = _constraint_summary_line(r)
            if conf is None:
                status = "✓"
                note = constraint_note or "—"
            else:
                status = "✗" if conf == "fail" else ("~" if conf == "warn" else "✓")
                base_note = _confidence_summary(r)
                note = f"{base_note} · {constraint_note}" if constraint_note else base_note
            lines.append(f"| `{r['bak']}` | — | — | — | — | — | — | {note} | {status} |")
            continue

        row_ok_n = sum(1 for t in tables if t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"])
        row_total = len(tables)
        null_ok_n = sum(t["null_ok"] for t in tables)
        null_total_n = sum(t["null_total"] for t in tables)
        mm_ok_n = sum(t["minmax_ok"] for t in tables)
        mm_total_n = sum(t["minmax_total"] for t in tables)
        col_ok_n = sum(
            1 for t in tables if t["col_count_ok"] or t["expected_rows"] == 0 or t["xtp_skip"]
        )

        row_s = _fmt_count(row_ok_n, row_total)
        null_s = _fmt_count(null_ok_n, null_total_n)
        mm_s = _fmt_count(mm_ok_n, mm_total_n)
        col_s = _fmt_count(col_ok_n, row_total)
        cells_s = _cells_summary(tables)

        # Highlight mismatches with table names (XTP skips are expected, not bad).
        bad_rows = [
            t["fqn"]
            for t in tables
            if not t["row_ok"] and t["expected_rows"] != 0 and not t["xtp_skip"]
        ]
        if bad_rows:
            row_s = row_s + f" ⚠ ({', '.join(f'`{f}`' for f in bad_rows)})"

        all_ok = (
            row_ok_n == row_total
            and null_ok_n == null_total_n
            and mm_ok_n == mm_total_n
            and col_ok_n == row_total
            and all(_value_ok(t) for t in tables)
        )
        status = "~" if is_xfail else ("✓" if all_ok else "✗")

        lines.append(
            f"| `{r['bak']}` | {src_rows:,} | {src_cols:,} | {row_s} | {null_s} | {mm_s} | {col_s} | {cells_s} | {status} |"
        )

    lines.append("\n## Per-fixture detail\n")

    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        tables = r["tables"]

        if not tables:
            conf = _confidence_status(r)
            if conf is None:
                status = "✓ pass"
            else:
                status = f"confidence {conf}"
        else:
            status = "~ xfail" if is_xfail else ("✓ pass" if _all_ok(r) else "✗ fail")

        sql_ver = r["sql_version"][:80] if r["sql_version"] else ""
        year = _ver_year(r.get("sql_version", ""))
        year_part = f"{year} — " if year else ""
        lines.append(f"### `{r['bak']}` — {year_part}{status}\n")
        lines.append(f"_SQL Server {sql_ver} · {r['bak_size_mb']} MB_\n")

        if not tables:
            summary = _confidence_summary(r)
            if summary:
                lines.append(f"_{summary}._\n")
            else:
                lines.append("_No non-empty tables._\n")
            continue

        lines.append(
            "| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |"
        )
        lines.append(
            "|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|"
        )
        for t in tables:
            if t["xtp_skip"]:
                row_s = col_s = "—"
            else:
                row_s = "✓" if t["row_ok"] else ("—" if t["expected_rows"] == 0 else "✗")
                col_s = "—" if t["expected_rows"] == 0 else "✓" if t["col_count_ok"] else "✗"
            null_s = _fmt_count(t["null_ok"], t["null_total"])
            mm_s = _fmt_count(t["minmax_ok"], t["minmax_total"])
            ttype = t.get("table_type", "rowstore")
            note = ""
            if t["xtp_skip"]:
                note = "memory-optimized (XTP) — data in checkpoint files, expected absent"
            elif t["missing"]:
                note = "missing from output"
            cells_note = _cells_note(t)
            if cells_note:
                note = f"{note}; {cells_note}" if note else cells_note
            lines.append(
                f"| `{t['fqn']}` | {ttype} | {t['expected_rows']:,} | {row_s} | {null_s} | {mm_s} | {col_s} | {note} |"
            )
        lines.append("")

    import datetime

    # Wall timings — isolated to one table so timing jitter does not
    # cause every per-fixture section to appear modified in git diff.
    timing_rows = sorted(
        [r for r in results if r.get("wall_s") is not None],
        key=lambda r: r["bak"].lower(),
    )
    if timing_rows:
        lines.append("\n## Extraction timings\n")
        lines.append("| Backup | Wall time |")
        lines.append("|--------|-------------|")
        for r in timing_rows:
            lines.append(f"| `{r['bak']}` | {r['wall_s']}s |")

    ts = datetime.date.today().isoformat()
    lines.append("\n---\n")
    lines.append(
        f"_Generated {ts} · {n_pass + n_xfail + n_fail} fixtures · {n_pass} pass · {n_xfail} xfail · {n_fail} fail_"
    )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


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
            m = re.match(r"^\|\s*`([^`]+\.bak)`\s*\|\s*([\d.]+)s\s*\|", line)
            if m:
                timings[m.group(1)] = float(m.group(2))
    return timings


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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        "--http",
        action="store_true",
        help=(
            "serve the fixture directory over a local HTTP server and pass each "
            ".bak as an http:// URL to extraction, exercising the remote-reader / "
            "LazyPageStore path.  Output doc gets an '_http' suffix to avoid "
            "overwriting the local-file run."
        ),
    )
    args = parser.parse_args(argv)

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

    try:
        cases = _select_cases(fixture_dir, bak_paths or None)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    if args.threads < 1:
        parser.error("--threads must be >= 1")

    # Sort longest-first using timings from the previous run of this doc so
    # the slowest fixtures start immediately and minimise overall wall time.
    prior_timings = _parse_prior_timings(out_path)
    if prior_timings:
        cases = _sort_cases_longest_first(cases, prior_timings)

    print(
        f"==> {len(cases)} fixtures to process in {fixture_dir} "
        f"(threads={args.threads}{', http' if args.http else ''})",
        file=sys.stderr,
    )

    if args.http:
        with _local_http_server(fixture_dir) as http_port:
            results = _run_cases(cases, threads=args.threads, http_port=http_port)
    else:
        results = _run_cases(cases, threads=args.threads)

    doc = _render(
        results,
        fixture_dir=fixture_dir,
        bak_paths=bak_paths,
        show_fixture_dir=args.fixture_dir is not None or not bak_paths,
    )

    if args.no_write:
        sys.stdout.write(doc)
    else:
        out_path.write_text(doc)
        n_pass = sum(1 for r in results if _all_ok(r))
        print(f"==> wrote {out_path}  ({n_pass}/{len(results)} pass)", file=sys.stderr)
    return 0


def _all_ok(r: dict[str, Any]) -> bool:
    tables = r["tables"]
    if not tables:
        return True
    return all(_table_ok(t) for t in tables)


if __name__ == "__main__":
    sys.exit(main())
