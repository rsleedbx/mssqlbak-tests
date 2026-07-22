"""Comparison engine: min/max helpers, node-stats builders, table comparison."""

from __future__ import annotations

import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

import pyarrow as pa
import pyarrow.compute as pc

from .config import NodeStats, _MINMAX_SKIP_TYPES


def _minmax_equal(act: Any, gt_str: str | None, sql_type: str) -> bool:
    """Lightweight min/max check — mirrors test_stats._minmax_equal."""
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


def _parse_time_str(s: str) -> datetime.time | None:
    """Parse an ISO-8601 time string (e.g. '07:00:00.0000000') to datetime.time."""
    try:
        return datetime.time.fromisoformat(s[:15])
    except (ValueError, TypeError):
        return None


def _parse_date_str(s: str) -> datetime.date | None:
    """Parse an ISO-8601 date string to datetime.date."""
    try:
        return datetime.date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_datetime_str(s: str) -> datetime.datetime | None:
    """Parse an ISO-8601 datetime string to datetime.datetime."""
    try:
        return datetime.datetime.strptime(s[:26], "%Y-%m-%d %H:%M:%S.%f")
    except (ValueError, TypeError):
        try:
            return datetime.datetime.fromisoformat(s[:19])
        except (ValueError, TypeError):
            return None


def _arrow_minmax_equal(act: Any, exp: Any) -> bool:
    """Compare two native Python min/max values with float tolerance.

    Handles the write-fidelity edge where one side is a string (extractor
    representation for time columns, which have no native Arrow/Delta type)
    and the other is a native temporal value returned by the pg_dir reader.
    """
    if act is None and exp is None:
        return True
    if act is None or exp is None:
        return False

    # Normalize temporal-vs-string pairs so that string-encoded time/date/datetime
    # values (emitted by the extractor for TIME columns) compare equal to the native
    # temporal objects reconstructed by the pg_dir reader.
    if isinstance(act, datetime.time) and isinstance(exp, str):
        parsed = _parse_time_str(exp)
        return parsed is not None and act == parsed
    if isinstance(exp, datetime.time) and isinstance(act, str):
        parsed = _parse_time_str(act)
        return parsed is not None and exp == parsed
    if isinstance(act, datetime.datetime) and isinstance(exp, str):
        parsed = _parse_datetime_str(exp)
        return parsed is not None and act == parsed
    if isinstance(exp, datetime.datetime) and isinstance(act, str):
        parsed = _parse_datetime_str(act)
        return parsed is not None and exp == parsed
    if isinstance(act, datetime.date) and isinstance(exp, str):
        parsed = _parse_date_str(exp)
        return parsed is not None and act == parsed
    if isinstance(exp, datetime.date) and isinstance(act, str):
        parsed = _parse_date_str(act)
        return parsed is not None and exp == parsed

    try:
        fa, fe = float(act), float(exp)
        if fe == 0.0:
            return fa == fe
        return abs(fa - fe) / max(abs(fe), 1e-300) < 1e-5
    except (TypeError, ValueError):
        pass
    return act == exp


def _node_stats_from_ground_truth(
    ground_truth: dict[str, Any],
) -> tuple[NodeStats, int, int]:
    """Build GT node from stats.json. Returns (node, total_src_rows, total_src_cols)."""
    node: NodeStats = {}
    total_src_rows = 0
    total_src_cols = 0
    for tbl_info in ground_truth.get("tables", []):
        schema_name = tbl_info["schema"]
        table_name = tbl_info["name"]
        fqn = f"{schema_name}.{table_name}"
        columns = tbl_info.get("columns", [])
        expected_rows = tbl_info["row_count"]
        total_src_rows += expected_rows
        total_src_cols += len(columns)
        node[fqn] = {
            "kind": "ground_truth",
            "expected_rows": expected_rows,
            "col_count": len(columns),
            "col_names": [c["name"] for c in columns],
            "gt_columns": columns,
        }
    return node, total_src_rows, total_src_cols


def _node_stats_from_arrow_table(fqn: str, tbl: pa.Table) -> dict[str, Any]:
    """Compute stats for a single Arrow table — one entry from _node_stats_from_arrow.

    Separating this from the bulk helper lets the streaming sink compute stats
    in ``close()`` and immediately release the raw batches.
    """
    null_counts: dict[str, int] = {}
    min_vals: dict[str, Any] = {}
    max_vals: dict[str, Any] = {}
    for col_name in tbl.schema.names:
        col = tbl.column(col_name)
        null_counts[col_name] = col.null_count if col.null_count is not None else 0
        min_vals[col_name], max_vals[col_name] = _minmax_from_col(col)
    return {
        "kind": "arrow",
        "row_count": len(tbl),
        "null_counts": null_counts,
        "min_vals": min_vals,
        "max_vals": max_vals,
        "col_count": len(tbl.schema.names),
        "col_names": list(tbl.schema.names),
    }


_UNSCORED_PREFIX = "ground-truth parquet missing"


def _apply_verify_result_to_table(t: dict[str, Any], vr: Any) -> None:
    """Apply one TableVerifyResult to a per-table row dict in-place.

    Distinguishes hard verification errors from un-scored tables (no GT parquet
    available) so the latter don't count as correctness failures in the report.
    """
    err = getattr(vr, "error", None)
    if err:
        if err.startswith(_UNSCORED_PREFIX):
            # GT parquet not yet captured — table is un-scored, not failed.
            t["value_unscored"] = True
        else:
            t["value_error"] = err
            t["_bad_columns"] = t["_column_names"]
            t["column_ok"] = 0
        return
    t["value_mode"] = vr.mode
    t["value_ok"] = vr.cells_ok
    t["value_total"] = vr.cells_total
    t["value_bad"] = (
        sorted(vr.col_mismatches)
        + [f"digest:{c}" for c in vr.digest_mismatches]
        + [f"order:{c}" for c in vr.order_mismatches]
    )
    t["value_missing_keys"] = vr.missing_keys
    t["value_pass"] = vr.ok
    bad_columns = set(t.get("_bad_columns", []))
    bad_columns.update(vr.col_mismatches)
    bad_columns.update(vr.digest_mismatches)
    bad_columns.update(vr.order_mismatches)
    if vr.missing_keys:
        bad_columns.update(t.get("_column_names", []))
    t["_bad_columns"] = sorted(bad_columns)
    t["column_ok"] = max(0, t["n_gt_cols"] - len(bad_columns))


def _apply_precomputed_cell_results(
    tables_out: list[dict[str, Any]],
    verify_results: dict[str, Any],
) -> None:
    """Apply pre-computed TableVerifyResult objects to tables_out in-place."""
    for t in tables_out:
        if t["xtp_skip"]:
            continue
        if t.get("value_error"):
            t["_bad_columns"] = t["_column_names"]
            t["column_ok"] = 0
            continue
        vr = verify_results.get(t["fqn"])
        if vr is None:
            continue
        _apply_verify_result_to_table(t, vr)


def _compare_tables(
    expected_node: NodeStats,
    actual_node: NodeStats,
    *,
    table_types: dict[str, str],
    expected_skips: frozenset[str],
    normalize_col: Callable[[str], str],
) -> list[dict[str, Any]]:
    """Compare expected vs actual nodes; return per-table diff rows.

    When expected is a GT node (kind="ground_truth"), uses SQL-string min/max
    parsing and xtp_skip logic.  When expected is an Arrow node (kind="arrow"),
    compares native Python values directly (write-fidelity edges).
    """
    tables_out: list[dict[str, Any]] = []

    for fqn, exp in expected_node.items():
        exp_kind: str = exp["kind"]
        col_names: list[str] = exp["col_names"]
        n_gt_cols: int = exp["col_count"]

        if exp_kind == "ground_truth":
            expected_rows: int = exp["expected_rows"]
            columns: list[dict[str, Any]] = exp["gt_columns"]
        else:
            expected_rows = exp["row_count"]
            columns = [
                {
                    "name": cn,
                    "sql_type": "",
                    "null_count": exp["null_counts"].get(cn),
                    "min_val": exp["min_vals"].get(cn),
                    "max_val": exp["max_vals"].get(cn),
                }
                for cn in col_names
            ]

        act = actual_node.get(fqn)
        row_ok = act is not None and act["row_count"] == expected_rows
        missing_tbl = act is None and expected_rows > 0
        xtp_skip = (exp_kind == "ground_truth") and missing_tbl and (fqn in expected_skips)

        null_ok = null_total = 0
        minmax_ok = minmax_total = 0
        col_count_ok = act is not None and act["col_count"] >= n_gt_cols
        bad_columns: set[str] = set()
        if missing_tbl and expected_rows > 0 and not xtp_skip:
            bad_columns.update(col_names)

        # For empty tables that are present in the actual output, verify that the
        # column names round-tripped correctly.  We only check this when the table
        # is present (act is not None) and has 0 rows — non-empty tables get their
        # columns validated through the null/min-max per-column loop below.
        if act is not None and expected_rows == 0 and act["row_count"] == 0:
            act_col_names = [normalize_col(c) for c in act["col_names"]]
            exp_col_names = [normalize_col(c) for c in col_names]
            for c_exp, c_act in zip(exp_col_names, act_col_names):
                if c_exp != c_act:
                    bad_columns.add(c_exp)
            # Flag any extra-missing columns
            if len(act_col_names) != len(exp_col_names):
                bad_columns.update(
                    set(exp_col_names) - set(act_col_names)
                )

        for col_info in columns:
            col_name: str = col_info["name"]
            sql_type: str = col_info.get("sql_type", "")
            exp_null = col_info.get("null_count")
            exp_min = col_info.get("min_val")
            exp_max = col_info.get("max_val")
            act_col = normalize_col(col_name)

            if exp_null is not None and act is not None:
                null_total += 1
                if act["null_counts"].get(act_col) == exp_null:
                    null_ok += 1
                else:
                    bad_columns.add(col_name)

            if exp_kind == "ground_truth":
                if sql_type.lower() in _MINMAX_SKIP_TYPES:
                    continue
                if (exp_min is not None or exp_max is not None) and act is not None:
                    if exp_min is not None:
                        minmax_total += 1
                        if _minmax_equal(act["min_vals"].get(act_col), exp_min, sql_type):
                            minmax_ok += 1
                        else:
                            bad_columns.add(col_name)
                    if exp_max is not None:
                        minmax_total += 1
                        if _minmax_equal(act["max_vals"].get(act_col), exp_max, sql_type):
                            minmax_ok += 1
                        else:
                            bad_columns.add(col_name)
            else:
                if exp_min is not None and act is not None:
                    minmax_total += 1
                    if _arrow_minmax_equal(act["min_vals"].get(act_col), exp_min):
                        minmax_ok += 1
                    else:
                        bad_columns.add(col_name)
                if exp_max is not None and act is not None:
                    minmax_total += 1
                    if _arrow_minmax_equal(act["max_vals"].get(act_col), exp_max):
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

    return tables_out
