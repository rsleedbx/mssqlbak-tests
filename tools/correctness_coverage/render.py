"""Markdown rendering: per-fixture rows, summary table, timing sections."""

from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any

from mssqlbak.confidence import Severity
from tools.known_gaps import gap_reason, version_from_fixture_dir

from .config import REPO_ROOT


def _fmt_count(ok: int, total: int) -> str:
    if total == 0:
        return "—"
    if ok == total:
        return f"**{ok}/{total}**"
    return f"{ok}/{total} ⚠"


def _value_ok(t: dict[str, Any]) -> bool:
    """True unless row-level cell verification ran for this table and failed.

    Returns True when no ``.cells/`` sidecar scored the table, so this is inert
    until ground-truth capture has produced cells.  Also returns True for
    un-scored tables (GT parquet not yet captured) so they don't count as fails.
    """
    if t.get("value_error"):
        return False
    if t.get("value_unscored"):
        return True
    if "value_pass" not in t:
        return True
    return bool(t["value_pass"])


def _table_ok(t: dict[str, Any]) -> bool:
    # col_count is a free pass only when the table is genuinely absent (missing)
    # or an XTP skip.  For 0-row tables that ARE present, col_count_ok reflects
    # the actual schema comparison and must not be bypassed.
    _col_ok = t["col_count_ok"] or t["missing"] or t["xtp_skip"]
    return (
        (t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"])
        and t["null_ok"] == t["null_total"]
        and t["minmax_ok"] == t["minmax_total"]
        and _col_ok
        and _value_ok(t)
    )


def _cells_note(t: dict[str, Any]) -> str:
    """Compact per-table cell-verification note (empty when unscored)."""
    if t.get("value_error"):
        return f"cells: ERROR ({t['value_error']})"
    if t.get("value_unscored"):
        return ""
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
    m = re.search(r"(20\d{2})", sql_version)
    return m.group(1) if m else ""


_EDGE_LABEL: dict[str, str] = {
    "mssql_arrow": "mssql→arrow",
    "arrow_delta": "arrow→delta",
    "delta_arrow": "delta→arrow",
    "arrow_pg_dir": "arrow→pg_dir",
    "pg_dir_arrow": "pg_dir→arrow",
}


def _edge_label(edge: str) -> str:
    return _EDGE_LABEL.get(edge, edge.replace("_", "→"))


def _edge_tables_ok(tables: list[dict[str, Any]]) -> bool:
    return all(_table_ok(t) for t in tables)


def _render_edge_table_rows(lines: list[str], tables: list[dict[str, Any]]) -> None:
    """Append a per-table detail markdown table for one edge."""
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
            # col_count: show real result for present tables (incl. 0-row); "—" only
            # when the table is fully absent (missing) so there's nothing to compare.
            col_s = "—" if t["missing"] else ("✓" if t["col_count_ok"] else "✗")
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


def _edge_tables_ok(tables: list[dict[str, Any]]) -> bool:
    """True when all tables in a single edge pass every check."""
    return all(_table_ok(t) for t in tables)


def _edge_has_infra_error(edge: dict[str, Any]) -> bool:
    """True when the edge has a recorded infra error (missing sink output, etc.)."""
    return bool(edge.get("readback_error"))


def _all_ok(r: dict[str, Any]) -> bool:
    """True when every pipeline edge passes all data checks.

    Edges with infra errors (missing sink output, etc.) are excluded from the
    data-pass/fail rollup — they are shown separately as infrastructure issues.

    Metadata validation results are shown in the report's Metadata section
    but intentionally excluded from this rollup so the data pass rate stays
    stable while metadata validators are being tuned.
    """
    edges: dict[str, dict[str, Any]] = r.get("edges", {})
    if not edges:
        # Fall back to the legacy flat tables list for assembled-only results.
        tables = r["tables"]
        if not tables:
            return True
        return all(_table_ok(t) for t in tables)
    return all(
        _edge_has_infra_error(edge) or _edge_tables_ok(edge["tables"])
        for edge in edges.values()
    )


def _meta_pass_line(results: list[dict[str, Any]]) -> str:
    """Build the 'Metadata: X/Y categories pass' summary line."""
    from tools.correctness_coverage.validators import get_validators
    all_cats = list(get_validators())
    cat_ok: dict[str, int] = {c: 0 for c in all_cats}
    cat_scored: dict[str, int] = {c: 0 for c in all_cats}
    for r in results:
        for cat, v in r.get("validations", {}).items():
            if v.get("unscored"):
                continue
            cat_scored[cat] = cat_scored.get(cat, 0) + 1
            if v.get("ok"):
                cat_ok[cat] = cat_ok.get(cat, 0) + 1
    scored = [(c, cat_ok[c], cat_scored[c]) for c in all_cats if cat_scored.get(c, 0) > 0]
    if not scored:
        return ""
    total_ok = sum(ok for _, ok, _ in scored)
    total = sum(n for _, _, n in scored)
    parts = [f"{c}: {ok}/{n}" for c, ok, n in scored]
    return f"**Metadata:** {total_ok}/{total} fixture-categories pass ({', '.join(parts)})"


def _render(
    results: list[dict[str, Any]],
    fixture_dir: Path | None = None,
    bak_paths: list[Path] | None = None,
    show_fixture_dir: bool = True,
    sink_names: list[str] | None = None,
) -> str:
    lines: list[str] = []
    version = version_from_fixture_dir(fixture_dir)
    active_sinks = list(sink_names or [])

    # Always render in alphabetical order by .bak filename
    results = sorted(results, key=lambda r: r["bak"].lower())

    n_pass = n_xfail = n_fail = 0
    table_ok = table_total = 0
    column_ok = column_total = 0
    # Per-category failure counters summed across all edges (tables as the unit)
    row_fail = null_fail = mm_fail = col_fail = cells_fail = 0
    # Per-edge fail counts for the Edges scoreboard {edge_name: fail_count}
    edge_fail_counts: dict[str, int] = {}
    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        has_tables = bool(r["tables"]) or bool(r.get("edges"))
        confidence_status = _confidence_status(r)

        # Collect all edge table lists: prefer r["edges"] when present
        edges_dict: dict[str, dict[str, Any]] = r.get("edges", {})
        if edges_dict:
            all_edge_tables = {k: v["tables"] for k, v in edges_dict.items()}
        else:
            all_edge_tables = {"mssql_arrow": r["tables"]} if r["tables"] else {}

        for edge_name, etables in all_edge_tables.items():
            edge_data = edges_dict.get(edge_name, {})
            if _edge_has_infra_error(edge_data):
                # Infra error: the sink output was missing or unreadable.
                # Record it as an edge-level infra fail (not a data fail) and
                # skip all per-table category counters for this edge.
                edge_fail_counts[edge_name] = edge_fail_counts.get(edge_name, 0) + 1
                continue

            table_ok += sum(1 for t in etables if _table_ok(t))
            table_total += len(etables)
            column_ok += sum(int(t.get("column_ok", t.get("n_gt_cols", 0))) for t in etables)
            column_total += sum(int(t.get("column_total", t.get("n_gt_cols", 0))) for t in etables)

            edge_has_fail = False
            for t in etables:
                if not (t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"]):
                    row_fail += 1
                    edge_has_fail = True
                if t["null_ok"] < t["null_total"]:
                    null_fail += 1
                    edge_has_fail = True
                if t["minmax_ok"] < t["minmax_total"]:
                    mm_fail += 1
                    edge_has_fail = True
                if not (t.get("col_count_ok", True) or t["missing"] or t["xtp_skip"]):
                    col_fail += 1
                    edge_has_fail = True
                if not _value_ok(t):
                    cells_fail += 1
                    edge_has_fail = True
            if edge_has_fail:
                edge_fail_counts[edge_name] = edge_fail_counts.get(edge_name, 0) + 1

        all_ok = _all_ok(r)

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

    category_line = " · ".join(
        [
            _fail_label(row_fail, "Row count"),
            _fail_label(null_fail, "Null count"),
            _fail_label(mm_fail, "Min/max"),
            _fail_label(col_fail, "Col count"),
            _fail_label(cells_fail, "Cells"),
        ]
    )

    # Build the per-edge scoreboard from whatever edges appeared across all results.
    # Use a stable display order: extract canonical edge names from the first result
    # that has edges, falling back to the known default order.
    _seen_edges: list[str] = []
    for _r in results:
        for _e in _r.get("edges", {}):
            if _e not in _seen_edges:
                _seen_edges.append(_e)
    if not _seen_edges:
        _seen_edges = ["mssql_arrow"]
    edges_scoreboard_parts = []
    for _e in _seen_edges:
        _label = _edge_label(_e)
        _n_fail = edge_fail_counts.get(_e, 0)
        edges_scoreboard_parts.append(f"{_label} {'✓' if _n_fail == 0 else f'{_n_fail} fail'}")
    edges_scoreboard = "**Edges:** " + " · ".join(edges_scoreboard_parts)

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
        f"{edges_scoreboard}\n\n"
        "Column key:\n\n"
        "| Column | Meaning |\n"
        "|--------|----------|\n"
        "| Stage | Pipeline edge being compared (e.g. mssql→arrow = extraction correctness) |\n"
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
    meta_line = _meta_pass_line(results)
    if meta_line:
        header = header + f"\n{meta_line}\n"
    lines.append(header)
    lines.append("## Summary\n")
    lines.append(
        "| Backup | Stage | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |"
    )
    lines.append(
        "|--------|-------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|"
    )

    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        src_rows = r["total_src_rows"]
        src_cols = r["total_src_cols"]
        edges: dict[str, dict[str, Any]] = r.get("edges", {})

        if not r["tables"] and not edges:
            conf = _confidence_status(r)
            constraint_note = _constraint_summary_line(r)
            if conf is None:
                status = "✓"
                note = constraint_note or "—"
            else:
                status = "✗" if conf == "fail" else ("~" if conf == "warn" else "✓")
                base_note = _confidence_summary(r)
                note = f"{base_note} · {constraint_note}" if constraint_note else base_note
            lines.append(f"| `{r['bak']}` | — | — | — | — | — | — | — | {note} | {status} |")
            continue

        # Emit one summary row per edge (or just mssql_arrow if no sinks).
        edge_order = ["mssql_arrow"] + [e for e in edges if e != "mssql_arrow"]
        for edge_name in edge_order:
            if edge_name not in edges:
                continue
            edge_data = edges[edge_name]
            tables = edge_data["tables"]
            stage = _edge_label(edge_name)

            # Infra error: show a special row instead of comparing data counts.
            if _edge_has_infra_error(edge_data):
                err_msg = edge_data.get("readback_error", "sink output missing or unreadable")
                lines.append(
                    f"| `{r['bak']}` | {stage} | {src_rows:,} | {src_cols:,}"
                    f" | — | — | — | — | — | ⚡ infra ({err_msg}) |"
                )
                continue

            row_ok_n = sum(
                1 for t in tables if t["row_ok"] or t["expected_rows"] == 0 or t["xtp_skip"]
            )
            row_total = len(tables)
            null_ok_n = sum(t["null_ok"] for t in tables)
            null_total_n = sum(t["null_total"] for t in tables)
            mm_ok_n = sum(t["minmax_ok"] for t in tables)
            mm_total_n = sum(t["minmax_total"] for t in tables)
            col_ok_n = sum(
                1 for t in tables if t["col_count_ok"] or t["missing"] or t["xtp_skip"]
            )

            row_s = _fmt_count(row_ok_n, row_total)
            null_s = _fmt_count(null_ok_n, null_total_n)
            mm_s = _fmt_count(mm_ok_n, mm_total_n)
            col_s = _fmt_count(col_ok_n, row_total)
            cells_s = (
                _cells_summary(tables)
                if edge_name.endswith("_arrow")
                else "—"
            )

            bad_rows = [
                t["fqn"]
                for t in tables
                if not t["row_ok"] and t["expected_rows"] != 0 and not t["xtp_skip"]
            ]
            if bad_rows:
                row_s = row_s + f" ⚠ ({', '.join(f'`{f}`' for f in bad_rows)})"

            edge_all_ok = (
                row_ok_n == row_total
                and null_ok_n == null_total_n
                and mm_ok_n == mm_total_n
                and col_ok_n == row_total
                and all(_value_ok(t) for t in tables)
            )
            # xfail only applies to GT edges
            is_gt_edge = not edge_name.startswith("arrow_")
            status = "~" if (is_xfail and is_gt_edge) else ("✓" if edge_all_ok else "✗")

            lines.append(
                f"| `{r['bak']}` | {stage} | {src_rows:,} | {src_cols:,} | {row_s} | {null_s} | {mm_s} | {col_s} | {cells_s} | {status} |"
            )

    lines.append("\n## Per-fixture detail\n")

    for r in results:
        stem = Path(r["bak"]).stem
        is_xfail = gap_reason(stem, version) is not None
        tables = r["tables"]
        edges = r.get("edges", {})

        if not tables and not edges:
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

        if not tables and not edges:
            summary = _confidence_summary(r)
            if summary:
                lines.append(f"_{summary}._\n")
            else:
                lines.append("_No non-empty tables._\n")
            continue

        edge_order = ["mssql_arrow"] + [e for e in edges if e != "mssql_arrow"]
        for edge_name in edge_order:
            if edge_name not in edges:
                continue
            edge_data = edges[edge_name]
            lines.append(f"#### Stage: {_edge_label(edge_name)}\n")
            if _edge_has_infra_error(edge_data):
                err_msg = edge_data.get("readback_error", "sink output missing or unreadable")
                lines.append(
                    f"_Infrastructure error: {err_msg}. "
                    f"This is a sink write/readback failure, not a data mismatch._\n"
                )
            else:
                _render_edge_table_rows(lines, edge_data["tables"])

    # --- Metadata validation section ----------------------------------------
    meta_results = [r for r in results if r.get("validations")]
    if meta_results:
        lines.append("\n## Metadata validation\n")
        lines.append(
            "Metadata ground truth is collected from the live SQL Server restore into "
            "`<bak>.metadata.json` by `python -m tools.fixture_run register-metadata-all`. "
            "Only fixtures with a sidecar are scored here; others show `—` (unscored).\n"
        )
        try:
            from tools.correctness_coverage.validators import get_validators
            all_cats = list(get_validators())
        except Exception:
            all_cats = ["constraints", "indexes", "extended_properties", "modules",
                        "schema_objects", "security", "statistics", "plan_guides", "query_store"]
        cat_cols = " | ".join(all_cats)
        sep_cols = " | ".join(":---------:" for _ in all_cats)
        lines.append(f"| Backup | {cat_cols} |")
        lines.append(f"|--------|{sep_cols}|")
        for r in sorted(meta_results, key=lambda x: x["bak"].lower()):
            validations = r.get("validations", {})
            cols = []
            for cat in all_cats:
                v = validations.get(cat)
                if v is None:
                    cols.append("—")
                elif v.get("unscored"):
                    cols.append("—")
                elif v.get("error"):
                    cols.append("💥")
                elif v.get("ok"):
                    cols.append("✓")
                else:
                    n_ok = v.get("n_ok", 0)
                    n_total = v.get("n_total", 0)
                    cols.append(f"{n_ok}/{n_total} ⚠")
            lines.append(f"| `{r['bak']}` | {' | '.join(cols)} |")

        # Per-fixture details for any failing categories
        failing_meta = [
            r for r in meta_results
            if any(
                not v.get("ok") and not v.get("unscored")
                for v in r.get("validations", {}).values()
            )
        ]
        if failing_meta:
            lines.append("\n### Metadata failures detail\n")
            for r in sorted(failing_meta, key=lambda x: x["bak"].lower()):
                validations = r.get("validations", {})
                lines.append(f"#### `{r['bak']}`\n")
                for cat, v in validations.items():
                    if v.get("ok") or v.get("unscored"):
                        continue
                    lines.append(f"**{cat}**")
                    if v.get("error"):
                        lines.append(f"  - error: `{v['error'][:200]}`")
                    for key in ("missing", "extra"):
                        items = v.get(key, [])
                        if items:
                            lines.append(f"  - {key}: {', '.join(f'`{i}`' for i in items[:10])}"
                                         + (" …" if len(items) > 10 else ""))
                    for mm in (v.get("mismatched") or [])[:5]:
                        if "expected" in mm:
                            lines.append(f"  - mismatch `{mm.get('key', '?')}`: "
                                         f"expected `{mm.get('expected')}` "
                                         f"got `{mm.get('recovered')}`")
                        elif "missing_count" in mm:
                            lines.append(f"  - mismatch `{mm.get('key', '?')}`: "
                                         f"missing {mm['missing_count']}, "
                                         f"extra {mm['extra_count']}")
                        else:
                            lines.append(f"  - mismatch `{mm.get('key', '?')}`: {mm}")
                    lines.append("")

    # Wall timings — isolated to one table so timing jitter does not
    # cause every per-fixture section to appear modified in git diff.
    timing_rows = sorted(
        [r for r in results if r.get("wall_s") is not None],
        key=lambda r: r["bak"].lower(),
    )
    if timing_rows:
        lines.append("\n## Extraction timings\n")
        lines.append("| Backup | Extract | Verify | Wall time |")
        lines.append("|--------|---------|--------|-----------|")
        for r in timing_rows:
            wall = r["wall_s"]
            extract = r.get("extract_s", 0) or 0
            verify = round(max(0.0, wall - extract), 3)
            lines.append(f"| `{r['bak']}` | {extract}s | {verify}s | {wall}s |")
        lines.append(
            "\n_Verify = wall − extract (Arrow conversion, ground-truth compare, "
            "cell verification, and confidence analysis). "
            "See **Sink read breakdown** below for the per-phase split._"
        )

    # Extract phase breakdown — per-phase timers from _extract_bak_inner.
    phase_rows = [r for r in timing_rows if r.get("phases")]
    if phase_rows:
        lines.append("\n## Extract phase breakdown\n")
        lines.append(
            "| Backup | pagestore | schema | catalog | constraints | logtail | xtp"
            " | data decode (net) | sink write | arrow verify | sink finish |"
        )
        lines.append(
            "|--------|----------:|-------:|--------:|------------:|--------:|---:"
            "|------------------:|-----------:|-------------:|------------:|"
        )
        for r in phase_rows:
            ph: dict[str, Any] = r.get("phases") or {}
            ph_ws: dict[str, Any] = r.get("write_s") or {}
            vs: dict[str, Any] = r.get("verify_s") or {}

            def _fs(key: str) -> str:
                v = ph.get(key)
                return f"{v}s" if v is not None else "—"

            sink_write_total = round(sum(ph_ws.values()), 3)
            arrow_verify = vs.get("mssql_arrow")
            ddn = r.get("data_decode_net_s")
            lines.append(
                f"| `{r['bak']}` "
                f"| {_fs('pagestore_build_s')} "
                f"| {_fs('schema_recover_s')} "
                f"| {_fs('catalog_recover_s')} "
                f"| {_fs('constraints_s')} "
                f"| {_fs('logtail_s')} "
                f"| {_fs('xtp_s')} "
                f"| {f'{ddn}s' if ddn is not None else '—'} "
                f"| {f'{sink_write_total}s' if ph_ws else '—'} "
                f"| {f'{arrow_verify}s' if arrow_verify is not None else '—'} "
                f"| {_fs('sink_finish_s')} |"
            )
        lines.append(
            "\n_data decode (net) = data\\_decode\\_s (raw loop wall; sink writes and arrow verify "
            "overlap decode on a background writer thread and are drained in sink finish). "
            "catalog = recover\\_catalog\\_objects (indexes/FKs/constraints, pg\\_dir only). "
            "arrow verify = cell verification run inside extraction (_StreamingStatsSink). "
            "verify=digest: per-column SHA-256 aggregate hash — fast, no GT parquet read, catches "
            "multiset-level corruption; also runs key-ordered digest (catches row transposition) when "
            "ordered\\_digest is present in the manifest (populated by backfill\\_ordered\\_digest). "
            "Mismatches show as digest:col (multiset) or order:col (transposition). "
            "verify=full: exhaustive keyed row compare — also catches value-preserving row misalignment._"
        )

    # Sink write timings — only when sinks were active
    sink_timing_rows = [r for r in timing_rows if r.get("write_s") or r.get("readback_s")]
    if sink_timing_rows and active_sinks:
        lines.append("\n## Sink write timings\n")
        write_cols = " | ".join(f"{s} write | {s} read" for s in active_sinks)
        sep_cols = " | ".join("-------:| ------:" for _ in active_sinks)
        lines.append(f"| Backup | {write_cols} |")
        lines.append(f"|--------|{sep_cols}|")
        for r in sink_timing_rows:
            sink_ws: dict[str, Any] = r.get("write_s") or {}
            sink_rs: dict[str, Any] = r.get("readback_s") or {}
            cols = []
            for s in active_sinks:
                w = sink_ws.get(s)
                rb = sink_rs.get(s)
                cols.append(f"{w}s" if w is not None else "—")
                cols.append(f"{rb}s" if rb is not None else "—")
            lines.append(f"| `{r['bak']}` | {' | '.join(cols)} |")
        lines.append(
            "\n_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._"
        )

    # Sink read breakdown — read / stats / verify sub-timers per sink,
    # plus the mssql→arrow (extraction-phase) verify time.
    breakdown_rows = [
        r for r in timing_rows
        if r.get("read_s") or r.get("stats_s") or r.get("verify_s")
    ]
    if breakdown_rows and active_sinks:
        lines.append("\n## Sink read breakdown\n")
        # Build column headers: mssql→arrow verify, then per-sink read/stats/verify.
        hdr_parts = ["arrow verify"]
        sep_parts = ["-------:"]
        for s in active_sinks:
            hdr_parts += [f"{s} read", f"{s} stats", f"{s} verify"]
            sep_parts += ["-------:", "-------:", "-------:"]
        lines.append(f"| Backup | {' | '.join(hdr_parts)} |")
        lines.append(f"|--------| {' | '.join(sep_parts)}|")
        for r in breakdown_rows:
            bd_rs: dict[str, Any] = r.get("read_s") or {}
            bd_ss: dict[str, Any] = r.get("stats_s") or {}
            bd_vs: dict[str, Any] = r.get("verify_s") or {}
            arrow_v = bd_vs.get("mssql_arrow")
            cols = [f"{arrow_v}s" if arrow_v is not None else "—"]
            for s in active_sinks:
                rd = bd_rs.get(s)
                st = bd_ss.get(s)
                vv = bd_vs.get(s)
                cols.append(f"{rd}s" if rd is not None else "—")
                cols.append(f"{st}s" if st is not None else "—")
                cols.append(f"{vv}s" if vv is not None else "—")
            lines.append(f"| `{r['bak']}` | {' | '.join(cols)} |")
        lines.append(
            "\n_arrow verify = cell verification folded into extract_s. "
            "Sink read = pure I/O + decode. Stats = min/max/null compute. "
            "Sink verify = cell verification on the round-tripped data. "
            "Remainder of readback_s is GC / other._"
        )

    ts = datetime.date.today().isoformat()
    lines.append("\n---\n")
    lines.append(
        f"_Generated {ts} · {n_pass + n_xfail + n_fail} fixtures · {n_pass} pass · {n_xfail} xfail · {n_fail} fail_"
    )

    return "\n".join(lines) + "\n"
