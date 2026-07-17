"""Compare mssqlbak extraction against ground-truth statistics.

Ground-truth ``.stats.json`` files are produced by::

    python -m tools.fixture_run register-bak tests/fixtures/<name>.bak

Each stats file records per-table row counts, per-column null counts, and
per-column min/max values as observed by a real SQL Server instance.  This
test verifies that mssqlbak extracts the same counts — catching skipped rows,
mishandled NULLs, and schema drift.

The test is automatically skipped for any ``.bak`` that has no corresponding
``.stats.json`` yet.  Add stats files incrementally as you register fixtures.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pytest

from mssqlbak import extract_bak_to_delta
from tests.fixture_companions import resolve_bak_input as _resolve_bak_input
from tools.known_gaps import expected_skipped_tables, gap_reason, version_from_fixture_dir

# Respect FIXTURE_DIR env var so the same test can run against any version's
# fixture set (e.g. FIXTURE_DIR=tests/fixtures_2017 pytest tests/test_stats.py).
# Falls back to tests/fixtures/ (the shared, non-version-specific set).
FIXTURES = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures")))

# SQL Server version of the active fixture set, used to resolve version-scoped
# known gaps (a gap may pass on some versions; see tools/known_gaps.py).
_VERSION = version_from_fixture_dir(FIXTURES)


# ---------------------------------------------------------------------------
# Companion-file resolution for striped / differential backups
# ---------------------------------------------------------------------------
# _resolve_bak_input is imported at module top from tests.fixture_companions
# (shared SSOT with tests/test_value_correctness.py).


# ---------------------------------------------------------------------------
# Discover parameterized cases
# ---------------------------------------------------------------------------

def _stats_cases() -> list[tuple[Path, Path]]:
    """Return (bak, stats_json) pairs for all registered fixtures.

    Stripe companions share the same data so only the first stripe file is
    tested (the full list is resolved at runtime by _resolve_bak_input).
    """
    seen_stripe_prefixes: set[str] = set()
    cases = []
    for stats_path in sorted(FIXTURES.glob("**/*.bak.stats.json")):
        bak_path = stats_path.parent / stats_path.name.removesuffix(".stats.json")
        if not bak_path.is_file():
            continue
        # Deduplicate stripe companions: only keep the first (lowest) stripe.
        m = re.match(r"^(.+)_(\d)$", bak_path.stem)
        if m:
            prefix = m.group(1)
            digit = int(m.group(2))
            if prefix in seen_stripe_prefixes:
                continue  # already captured via a lower-numbered stripe
            # Check whether a lower-numbered companion exists; skip if so.
            lower = any(
                (bak_path.parent / f"{prefix}_{d}.bak").exists()
                for d in range(1, digit)
            )
            if lower:
                continue
            seen_stripe_prefixes.add(prefix)
        cases.append((bak_path, stats_path))
    return cases


_CASES = _stats_cases()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_table_stats(delta_path: Path) -> dict[str, dict[str, Any]]:
    """Read extracted Delta tables and compute row counts, null counts, and min/max.

    Returns a dict keyed by ``schema.table`` (e.g. ``"dbo.tt_cluster"``) with::

        {
            "row_count": int,
            "null_counts": {col_name: int},
            "min_vals":   {col_name: Any},  # Python native type from PyArrow
            "max_vals":   {col_name: Any},
        }

    The sink writes tables as ``<output>/<schema>/<table>/``.
    """
    import deltalake

    result: dict[str, dict[str, Any]] = {}
    # Walk two levels: schema_dir / table_dir
    for schema_dir in sorted(delta_path.iterdir()):
        if not schema_dir.is_dir():
            continue
        for tbl_dir in sorted(schema_dir.iterdir()):
            if not tbl_dir.is_dir():
                continue
            try:
                dt = deltalake.DeltaTable(str(tbl_dir))
            except Exception:
                continue
            tbl = dt.to_pyarrow_table()
            null_counts: dict[str, int] = {}
            min_vals: dict[str, Any] = {}
            max_vals: dict[str, Any] = {}
            for col_name in tbl.schema.names:
                col = tbl.column(col_name)
                null_counts[col_name] = col.null_count if col.null_count is not None else 0
                # Use to_pylist() + Python min/max: pyarrow.compute.min/max are
                # dynamically registered and not typed in pyright's stubs.
                vals = col.drop_null().to_pylist()
                if vals:
                    min_vals[col_name] = min(vals)
                    max_vals[col_name] = max(vals)
                else:
                    min_vals[col_name] = None
                    max_vals[col_name] = None
            fqn = f"{schema_dir.name}.{tbl_dir.name}"
            result[fqn] = {
                "row_count": len(tbl),
                "null_counts": null_counts,
                "min_vals": min_vals,
                "max_vals": max_vals,
            }
    return result


# ---------------------------------------------------------------------------
# Min/max comparison helpers
# ---------------------------------------------------------------------------

# Types where min/max comparison is skipped: their SQL Server string
# representation is ambiguous or format-dependent enough that a reliable
# round-trip comparison cannot be done cheaply.
_MINMAX_SKIP_TYPES: frozenset[str] = frozenset({
    # sql_variant wraps a heterogeneous per-row base type.  Python's str()
    # converts temporal values to ISO format ('1900-01-01 00:00:00') while SQL
    # Server's CAST-to-NVARCHAR gives the legacy format ('Jan  1 1900 12:00AM'),
    # so the two string representations disagree for any row storing a datetime
    # value.  All other types that can appear inside a variant (int, float,
    # string) do agree, but we cannot skip only the temporal rows.
    "sql_variant",
    # uniqueidentifier: SQL Server sorts GUIDs by bytes [10-15], [8-9], [6-7],
    # [4-5], [0-3] — not lexicographic order.  The MIN/MAX returned by SQL Server
    # differs from pyarrow's lexicographic MIN/MAX of the string representation.
    "uniqueidentifier",
    # xml: SQL Server serializes empty elements as self-closing (<tag/>) while
    # Python re-serializes them as paired tags (<tag></tag>).  The resulting
    # strings differ without any data loss.  Additionally, SQL Server's XML type
    # may normalise floating-point attribute values differently from Python.
    "xml",
    # geography / geometry: SQL Server's binary MIN/MAX comparison uses a
    # spatial-specific ordering that differs from Python's lexicographic bytes
    # comparison of the WKT representation.
    "geography",
    "geometry",
    # varchar / nvarchar / char / nchar / text / ntext: the GT was generated by
    # register_bak.py using MIN(col COLLATE Latin1_General_100_BIN2).  However,
    # SQL Server does NOT apply the COLLATE override to the aggregate's internal
    # comparison — it uses the column's native collation (typically CI_AS for
    # user databases) to determine which row holds the minimum value.  As a result
    # the GT min/max reflects CI_AS ordering (case-insensitive, brackets sort
    # before letters) while Python's min() uses Unicode code-point order.  The
    # discrepancy produces false test failures for any column where the CI_AS
    # minimum differs from the BIN2 minimum.
    # TODO: fix register_bak.py to use a subquery that forces BIN2 ordering
    #       before MIN/MAX, then regenerate all stats.json and remove this skip.
    "varchar",
    "nvarchar",
    "char",
    "nchar",
    "text",
    "ntext",
    # varbinary / image: the GT is MIN(CONVERT(VARBINARY(250), col)) — SQL Server
    # truncates each value to 250 bytes BEFORE finding the MIN.  Python finds the
    # minimum of full-length byte values.  MIN-before-truncate ≠ truncate-then-MIN
    # when different rows are minimum at different lengths.
    # TODO: fix register_bak.py to capture full-length varbinary min/max, then
    #       regenerate stats.json and remove this skip.
    "varbinary",
    "image",
    # json / vector (SQL Server 2025+): MIN/MAX is not supported on these types;
    # register_bak.py captures the min/max by casting the whole column value to
    # NVARCHAR(MAX) (whole-document, not a per-property aggregate).  The
    # document-string ordering is not semantically meaningful — SQL Server's native
    # binary form may serialize differently than the pure-Python parser output — so
    # these types are captured in the GT for completeness but never compared here.
    "json",
    "vector",
})


def _parse_gt_str(s: str, sql_type: str) -> Any:
    """Parse a SQL Server CAST-to-NVARCHAR ground-truth string to a Python value.

    Returns ``None`` if parsing fails or the type is not handled.
    """
    if s is None:
        return None
    typ = sql_type.lower()
    s = s.strip()

    try:
        if typ in ("int", "bigint", "smallint", "tinyint"):
            return int(s)
        if typ == "bit":
            return bool(int(s))
        if typ in ("decimal", "numeric", "money", "smallmoney"):
            return Decimal(s)
        if typ in ("float", "real"):
            # SQL Server: "-1.7e+308" / "-3.4e+038" — normalize exponent width
            return float(s)
        if typ == "date":
            import datetime
            return datetime.date.fromisoformat(s)
        if typ == "datetime2":
            import datetime
            # "0001-01-01 00:00:00.0000000" — up to 7 decimal places
            s = s[:26]  # trim to microsecond precision
            return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
        if typ in ("datetime", "smalldatetime"):
            import datetime
            # GT is now CONVERT(..., 120): 'YYYY-MM-DD HH:MM:SS' (ISO ODBC canonical)
            return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        if typ == "datetimeoffset":
            import datetime
            import re as _re
            # GT format: '0001-01-01 00:00:00.0000000 +00:00'
            # Normalize: truncate 7-digit fraction to 6, remove space before tz offset.
            s2 = _re.sub(r"\.(\d{7})", lambda m: "." + m.group(1)[:6], s)
            s2 = s2.replace(" +", "+").replace(" -", "-")
            return datetime.datetime.fromisoformat(s2)
        if typ == "time":
            import datetime
            # "00:00:00.0000000" — up to 7 decimal places; fromisoformat
            # handles up to 6, so truncate the 7th fractional digit.
            s = s[:15]  # "HH:MM:SS.ffffff"
            return datetime.time.fromisoformat(s)
        if typ in ("char", "nchar"):
            return s.rstrip()  # GT uses RTRIM; strip any residual trailing spaces
        if typ in ("varchar", "nvarchar", "text", "ntext"):
            return s  # binary-ordered GT string, compare directly
        if typ in ("varbinary", "image"):
            # GT is '0x' + uppercase hex digits (SQL Server CONVERT style 1)
            return s  # returned as-is; _normalize_py_val converts bytes to same format
        if typ in ("xml", "geometry", "geography", "hierarchyid"):
            # GT is the text representation (XML markup, OGC WKT / AsTextZM, /1/2/ path).
            # mssqlbak extracts these as pa.string() in the same format, so compare directly.
            return s
        if typ == "uniqueidentifier":
            return s.upper()
        if typ in ("binary",):
            # "0x0102..." → bytes
            return bytes.fromhex(s[2:]) if s.startswith("0x") else bytes.fromhex(s)
        if typ == "timestamp":
            # "0x00000000000007EB" → int (for both-endian comparison in _minmax_equal)
            return int(s, 16)
    except (ValueError, InvalidOperation, OverflowError):
        pass
    return None


def _normalize_py_val(val: Any, sql_type: str) -> Any:
    """Normalise a Python/PyArrow value for comparison against a parsed GT value."""
    if val is None:
        return None
    typ = sql_type.lower()

    if typ == "bit":
        return bool(val)
    if typ in ("int", "bigint", "smallint", "tinyint"):
        return int(val)
    if typ in ("decimal", "numeric"):
        try:
            return Decimal(str(val))
        except InvalidOperation:
            return val
    if typ in ("money", "smallmoney"):
        try:
            return Decimal(str(val))
        except InvalidOperation:
            return val
    if typ in ("float", "real"):
        return float(val)
    if typ == "time":
        import datetime
        if isinstance(val, str):
            try:
                return datetime.time.fromisoformat(val[:15])
            except ValueError:
                return val
        return val
    if typ == "date":
        import datetime
        if isinstance(val, str):
            try:
                return datetime.date.fromisoformat(val)
            except ValueError:
                return val
        return val
    if typ == "datetime2":
        import datetime
        if isinstance(val, str):
            try:
                return datetime.datetime.strptime(val[:26], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                return val
        return val
    if typ in ("datetime", "smalldatetime"):
        import datetime
        # GT is CONVERT(..., 120) which truncates to seconds; match that precision.
        if isinstance(val, datetime.datetime):
            return val.replace(microsecond=0)
        if isinstance(val, str):
            try:
                return datetime.datetime.strptime(val[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return val
        return val
    if typ in ("char", "nchar"):
        # SQL uses RTRIM; strip residual trailing spaces from the extracted value too.
        return str(val).rstrip()
    if typ in ("varchar", "nvarchar", "text", "ntext"):
        return str(val) if val is not None else None
    if typ in ("varbinary", "image"):
        # GT is '0x' + uppercase hex (SQL Server CONVERT style 1); match that format.
        if isinstance(val, (bytes, bytearray)):
            return "0x" + bytes(val).hex().upper()
        return str(val)
    if typ == "uniqueidentifier":
        return str(val).upper()
    if typ == "binary":
        # bytes object from PyArrow
        if isinstance(val, (bytes, bytearray)):
            return bytes(val)
        return val
    if typ == "timestamp":
        # Return bytes unchanged; _minmax_equal tries both byte orders.
        return val
    return val


def _minmax_equal(py_val: Any, gt_str: str | None, sql_type: str) -> bool:
    """Return True if extracted value matches the SQL Server ground truth string.

    Returns True (skip) when ground truth is None or the type is in
    ``_MINMAX_SKIP_TYPES``.
    """
    if gt_str is None:
        return True  # no ground truth → nothing to check
    if sql_type.lower() in _MINMAX_SKIP_TYPES:
        return True

    gt = _parse_gt_str(gt_str, sql_type)
    if gt is None:
        return True  # unparseable ground truth → skip

    act = _normalize_py_val(py_val, sql_type)

    # Char/nchar: RTRIM applied in SQL and rstrip in normalizers; compare stripped.
    if sql_type.lower() in ("char", "nchar"):
        return str(act).rstrip() == str(gt).rstrip() if act is not None else str(gt).rstrip() == ""

    # Float/real: compare approximately (SQL Server precision may differ).
    if sql_type.lower() in ("float", "real"):
        if act is None or gt == 0.0:
            return act == gt
        try:
            return abs(float(act) - float(gt)) / max(abs(float(gt)), 1e-300) < 1e-5
        except (TypeError, ZeroDivisionError):
            return act == gt

    # varbinary/image: both are '0xABCD...' strings after normalization.
    # GT is capped at NVARCHAR(500)/NVARCHAR(502); if GT appears at the size limit,
    # accept a prefix match to handle potential truncation.
    if sql_type.lower() in ("varbinary", "image"):
        if act is None or gt is None:
            return act == gt
        act_s = str(act)
        gt_s = str(gt)
        if act_s == gt_s:
            return True
        # If GT is at the capture limit (502 chars = 250 bytes) it may be truncated.
        if len(gt_s) >= 500 and act_s.startswith(gt_s):
            return True
        return False

    # timestamp/rowversion: SQL Server stores as big-endian 8-byte binary, but
    # PAGE/ROW-compressed rows may be extracted as little-endian. Accept either.
    if sql_type.lower() == "timestamp":
        if isinstance(act, (bytes, bytearray)) and isinstance(gt, int):
            return int.from_bytes(act, "big") == gt or int.from_bytes(act, "little") == gt
        return act == gt

    # datetimeoffset: both sides are tz-aware datetimes; Python compares by UTC instant.
    if sql_type.lower() == "datetimeoffset":
        import datetime as _dt
        if act is None or gt is None:
            return act == gt
        try:
            act_utc = act.astimezone(_dt.timezone.utc) if act.tzinfo else act
            gt_utc = gt.astimezone(_dt.timezone.utc) if gt.tzinfo else gt  # type: ignore[union-attr]
            return act_utc == gt_utc
        except (AttributeError, TypeError):
            return act == gt

    return act == gt


# ---------------------------------------------------------------------------
# Parametrized test
# ---------------------------------------------------------------------------

# Known fixture gaps are resolved via the shared SSOT (tools/known_gaps.py) so
# the coverage doc and this test always agree.  gap_reason() is version-aware:
# a gap that passes on the active SQL version is not xfailed.  To add a gap,
# edit known_gaps.py.


def test_realworld_adventureworks_ext_xtp_tables_are_expected_skips() -> None:
    # All seven XTP tables now decode byte-exact + complete and LAND:
    # Sales.SpecialOffer_inmem (16), Demo.DemoSalesOrderDetailSeed (538),
    # Demo.DemoSalesOrderHeaderSeed (31465, from the XTP checkpoint container),
    # Sales.SpecialOfferProduct_inmem (538, via the seq-contiguity gate — no
    # IDENTITY surrogate but a gap-free seq 1..538), and Production.Product_inmem
    # (504, via the seq gate — a variable-column table decoded through the
    # XTP-native layout: width-then-colid fixed order, numeric as an 8-aligned
    # scaled mantissa, one-byte-per-bit, and fixed char/nchar in the variable
    # section), plus Sales.SalesOrderDetail_inmem (121,317) and
    # Sales.SalesOrderHeader_inmem (31,465).  See
    # docs/notes/2026-07-03-adventureworks-xtp-investigation.md.
    assert expected_skipped_tables("AdventureWorks2016_EXT") == frozenset()

# Column-level min/max gaps: {fixture_stem: frozenset of "schema.table.column"}.
# Row-count and null-count checks still run for these columns; only min/max
# comparisons are skipped.  Add here when an extraction limitation is known but
# not yet fixed rather than disabling entire fixture tests.
#
# Currently empty: every former entry was either
#   (a) a decoder gap that has since been fixed — the enc=5 Format D datetimeoffset
#       columns (columnstore_minimal.dbo.cs_10000.dto,
#       compressioncoverage_full.dbo.cmp_columnstore_archive.dto), the ghost-row
#       min/max (dirtycoverage_delete.dbo.delete_test.id,
#       dirtycoverage_temporal_update.dbo.temporal_test.ValidFrom) — all now match
#       ground truth byte-for-byte on every version; or
#   (b) a varchar/varbinary column already covered by the type-level
#       ``_MINMAX_SKIP_TYPES`` skip (tabletypecoverage_full.dbo.tt_partition.
#       c_varbinary_max and the AdventureWorks Person.Password / Production LOB
#       columns), so the per-column entry never had any effect.
_KNOWN_MINMAX_COL_GAPS: dict[str, frozenset[str]] = {}


@pytest.mark.parametrize(
    "bak_path,stats_path",
    _CASES,
    ids=[c[0].stem for c in _CASES],
)
def test_extraction_matches_sql_server_stats(
    bak_path: Path, stats_path: Path
) -> None:
    """mssqlbak extraction must match SQL Server ground-truth row/null counts."""
    _gap = gap_reason(bak_path.stem, _VERSION)
    if _gap is not None:
        pytest.xfail(_gap)
    import time

    ground_truth: dict[str, Any] = json.loads(stats_path.read_text())

    bak_input = _resolve_bak_input(bak_path)

    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.perf_counter()
        extract_bak_to_delta(bak_input, tmp)
        extract_s = round(time.perf_counter() - t0, 3)
        extracted_stats = _extract_table_stats(Path(tmp))

    bak_size_mb: float = ground_truth.get("bak_size_mb", 0)
    restore_s: float = ground_truth.get("sqlserver_restore_s", 0)
    extract_mb_s = round(bak_size_mb / extract_s, 1) if extract_s > 0 else 0
    restore_mb_s = round(bak_size_mb / restore_s, 1) if restore_s > 0 else 0
    speedup = round(restore_s / extract_s, 2) if extract_s > 0 and restore_s > 0 else None
    speedup_str = f"  mssqlbak is {speedup}× {'faster' if speedup >= 1 else 'slower'} than SQL Server restore" if speedup else ""
    print(
        f"\n  {bak_path.name}  ({bak_size_mb} MB)\n"
        f"  SQL Server restore : {restore_s:.1f}s  ({restore_mb_s} MB/s)\n"
        f"  mssqlbak extract   : {extract_s:.1f}s  ({extract_mb_s} MB/s)"
        f"{speedup_str}",
        file=sys.stderr,
    )

    errors: list[str] = []

    for tbl_info in ground_truth["tables"]:
        schema = tbl_info["schema"]
        tbl_name = tbl_info["name"]
        expected_rows = tbl_info["row_count"]
        fqn = f"{schema}.{tbl_name}"

        if fqn not in extracted_stats:
            if expected_rows != 0:
                if fqn in expected_skipped_tables(bak_path.stem):
                    continue  # intentionally skipped (unsupported table type)
                errors.append(f"{fqn}: table missing from mssqlbak output")
            continue

        actual = extracted_stats[fqn]
        if actual["row_count"] != expected_rows:
            errors.append(
                f"{fqn}: row_count {actual['row_count']} != expected {expected_rows}"
            )

        for col_info in tbl_info.get("columns", []):
            col_name = col_info["name"]
            expected_nulls = col_info.get("null_count")
            if expected_nulls is None:
                continue
            actual_nulls = actual["null_counts"].get(col_name)
            if actual_nulls is None:
                errors.append(f"{fqn}.{col_name}: column missing from extracted output")
                continue
            if actual_nulls != expected_nulls:
                errors.append(
                    f"{fqn}.{col_name}: null_count {actual_nulls} != expected {expected_nulls}"
                )

            sql_type = col_info.get("sql_type", "")
            gt_min = col_info.get("min_val")
            gt_max = col_info.get("max_val")

            # Skip min/max checks when the ground truth has no data for this col.
            if gt_min is None and gt_max is None:
                continue

            # Skip column-level known gaps (row/null checks above still run).
            col_key = f"{fqn}.{col_name}"
            if col_key in _KNOWN_MINMAX_COL_GAPS.get(bak_path.stem, frozenset()):
                continue

            act_min = actual["min_vals"].get(col_name)
            act_max = actual["max_vals"].get(col_name)

            if not _minmax_equal(act_min, gt_min, sql_type):
                errors.append(
                    f"{fqn}.{col_name}: min {act_min!r} != expected {gt_min!r}"
                    f" (sql_type={sql_type})"
                )
            if not _minmax_equal(act_max, gt_max, sql_type):
                errors.append(
                    f"{fqn}.{col_name}: max {act_max!r} != expected {gt_max!r}"
                    f" (sql_type={sql_type})"
                )

    if errors:
        bullet_list = "\n  ".join(errors)
        pytest.fail(
            f"mssqlbak extraction differs from SQL Server ground truth:\n  {bullet_list}"
        )
