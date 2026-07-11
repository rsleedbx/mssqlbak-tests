"""Row-level value diff engine — the per-cell ground-truth comparator.

Aligns a decoded Arrow table to its ``<bak>.cells/<fqn>.parquet`` ground truth by
the manifest's ``key_columns``, canonicalizes both sides through
:func:`tools.cell_canon.canon`, counts matching cells, and verifies the per-column
:func:`tools.cell_canon.column_digest`. This catches the "right aggregate, wrong
cells" defect class that ``correctness_coverage``'s null/min-max/row-count checks
cannot.

The ground-truth capture side (``tools/cells_capture.py``) is built separately and
needs a live SQL Server; this module is fully offline given a ``.cells/`` sidecar.
"""

from __future__ import annotations

import functools
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tools.cell_canon import _base_type, _canon_bit, canon, column_digest

if TYPE_CHECKING:
    import pyarrow as pa

MANIFEST_NAME = "_manifest.json"


@dataclass
class TableVerifyResult:
    """Outcome of verifying one table's decoded cells against ground truth."""

    fqn: str
    mode: str  # "full" | "sample" | "digest-only"
    cells_ok: int = 0
    cells_total: int = 0
    col_mismatches: dict[str, int] = field(default_factory=dict)
    digest_mismatches: list[str] = field(default_factory=list)
    missing_keys: int = 0
    samples: list[tuple[Any, str, str | None, str | None]] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return (
            self.error is None
            and not self.col_mismatches
            and not self.digest_mismatches
            and self.missing_keys == 0
        )


def cells_dir_for(bak_path: Path) -> Path:
    """Return the ``<bak>.cells`` sidecar directory path for a ``.bak`` path."""
    return bak_path.parent / (bak_path.name + ".cells")


def load_manifest(cells_dir: Path) -> dict[str, Any]:
    """Load and parse the ``_manifest.json`` in a ``.cells/`` directory."""
    return json.loads((cells_dir / MANIFEST_NAME).read_text())


def _safe_to_pylist(col: "pa.ChunkedArray | pa.Array") -> list[Any]:
    """Convert an Arrow column to Python values, replacing overflow scalars with None.

    PyArrow timestamps stored as int64 nanoseconds may represent dates outside
    Python's datetime range (year < 1 or > 9999) when the underlying page data
    is corrupted.  Arrow raises ``OverflowError`` from ``as_py()`` in that case.

    Strategy: try the fast batch ``to_pylist()`` first; if it raises, fall back
    to per-element conversion so only the overflowing scalars become ``None``.
    """
    try:
        return col.to_pylist()  # type: ignore[union-attr]
    except (OverflowError, ValueError):
        pass
    # Slow path: convert element-by-element, substituting None for bad scalars.
    result: list[Any] = []
    chunks = col.chunks if hasattr(col, "chunks") else [col]  # type: ignore[union-attr]
    for chunk in chunks:
        for i in range(len(chunk)):
            try:
                result.append(chunk[i].as_py())
            except (OverflowError, ValueError):
                result.append(None)
    return result


# Types whose canonical form is a plain str() — no numeric quantization,
# no padding strip, no encoding, no special-casing needed.
# nchar is NOT included: it requires trailing-space rstrip.
# sql_variant is NOT included: it needs alias resolution inside canon().
_STR_PASSTHROUGH = frozenset(
    {
        "int",
        "bigint",
        "smallint",
        "tinyint",
        "varchar",
        "nvarchar",
        "text",
        "ntext",
        "hierarchyid",
    }
)


def _make_canonicalizer(sql_type: str):
    """Return a fast per-value function for *sql_type*.

    For types whose canonical form is provably ``str(value)`` (or a trivial
    variant), the returned function skips the full ``canon`` dispatch and
    resolves the type branch only once per column.  All other types fall back
    to ``canon`` so behaviour is identical to the previous implementation.
    """
    t = _base_type(sql_type)

    if t in _STR_PASSTHROUGH:

        def _fast(v: Any) -> "str | None":
            return None if v is None else str(v)

        return _fast

    if t in ("char", "nchar"):

        def _fast_char(v: Any) -> "str | None":
            return None if v is None else str(v).rstrip(" ")

        return _fast_char

    if t == "bit":

        def _fast_bit(v: Any) -> "str | None":
            return None if v is None else _canon_bit(v)

        return _fast_bit

    # All other types (decimal, numeric, money, float, real, binary,
    # uniqueidentifier, xml, geometry, geography, datetimeoffset, datetime,
    # datetime2, date, time, smalldatetime, sql_variant, etc.) use canon().
    return functools.partial(canon, sql_type=sql_type)


def _canon_col(values: list[Any], sql_type: str) -> list[str | None]:
    f = _make_canonicalizer(sql_type)
    return [f(v) for v in values]


def _canon_arrow_col(col: "pa.ChunkedArray | pa.Array", sql_type: str) -> list[str | None]:
    """Canonicalize an Arrow column without going through Python scalars where possible.

    For decimal128 columns (money/decimal/numeric/smallmoney) the Arrow string
    cast produces ``format(Decimal(...).quantize(scale), "f")`` — byte-identical
    to ``canon`` for those types (validated across multiple scales) and roughly
    3x faster than the per-value ``Decimal.quantize()`` path.

    Integer columns are NOT accelerated here: ``pc.cast(int_array, string)``
    benchmarks slower than the existing ``str()`` fast path in ``_make_canonicalizer``
    due to the Arrow materialisation overhead.

    All other types fall back to :func:`_safe_to_pylist` + :func:`_canon_col`.

    Returns the same ``list[str | None]`` that ``_canon_col`` would produce.
    """
    import pyarrow as pa
    import pyarrow.compute as pc

    t = _base_type(sql_type)

    # Decimals: pc.cast(decimal128_array, string) == format(Decimal, "f") at the
    # stored scale, which matches canon() for money/decimal/numeric/smallmoney.
    # Only apply when the Arrow column's actual type is decimal128 (not when it
    # has been cast to float by an older decoder).
    if t in ("money", "smallmoney", "decimal", "numeric"):
        try:
            arr = col.combine_chunks() if hasattr(col, "chunks") else col
            if pa.types.is_decimal(arr.type):
                return pc.cast(arr, pa.string()).to_pylist()
        except Exception:
            pass

    # All other types (int, datetime, float, binary, nchar, xml, spatial, etc.):
    # use the safe Python path.
    return _canon_col(_safe_to_pylist(col), sql_type)


def _effective_sql_type(column_meta: dict[str, Any]) -> str:
    return column_meta.get("base_sql_type") or column_meta.get("sql_type", "")


def _diagnose_digest_only(
    res: TableVerifyResult,
    extracted: "pa.Table",
    cells_dir: Path,
    manifest_entry: dict[str, Any],
    sql_types: dict[str, str],
    max_samples: int,
) -> None:
    """Populate ``res.samples`` with a per-column set diff for a digest-only table.

    Keyless tables store each column's binary-sorted non-null canonical values
    (``values_sorted``); when a digest mismatches we compare the decoded value
    *set* against ground truth to show which canonical values the decoder got
    wrong (``got-only``) or dropped (``want-only``). This is diagnostic context
    only — the digest remains the pass/fail authority.
    """
    if not res.digest_mismatches or not manifest_entry.get("values_sorted"):
        return
    gt_path = cells_dir / f"{manifest_entry['fqn']}.parquet"
    if not gt_path.exists():
        return
    import pyarrow.parquet as pq

    gt = pq.read_table(gt_path)
    ext_names = set(extracted.schema.names)
    per_col = max(2, max_samples // max(1, len(res.digest_mismatches)))
    for name in res.digest_mismatches:
        if name not in ext_names or name not in gt.schema.names:
            continue
        want = sorted(
            v
            for v in _canon_col(_safe_to_pylist(gt.column(name)), sql_types.get(name, ""))
            if v is not None
        )
        got = sorted(
            v
            for v in _canon_col(_safe_to_pylist(extracted.column(name)), sql_types.get(name, ""))
            if v is not None
        )
        want_set, got_set = set(want), set(got)
        only_got = [v for v in got if v not in want_set]
        only_want = [v for v in want if v not in got_set]
        for ex in only_got[: per_col // 2 or 1]:
            res.samples.append((name, "got-only", ex, None))
        for ex in only_want[: per_col // 2 or 1]:
            res.samples.append((name, "want-only", None, ex))


def verify_table(
    extracted: "pa.Table",
    cells_dir: Path,
    manifest_entry: dict[str, Any],
    *,
    max_samples: int = 20,
) -> TableVerifyResult:
    """Diff ``extracted`` against the ground-truth parquet for one table.

    ``manifest_entry`` is the per-table object from ``_manifest.json`` (fqn,
    key_columns, mode, columns[{name, sql_type, digest, ...}]).
    """
    import pyarrow.parquet as pq

    fqn = manifest_entry["fqn"]
    mode = manifest_entry.get("mode", "full")
    res = TableVerifyResult(fqn=fqn, mode=mode)

    sql_types: dict[str, str] = {
        c["name"]: _effective_sql_type(c) for c in manifest_entry.get("columns", [])
    }
    ext_names = set(extracted.schema.names)
    gt: pa.Table | None = None
    gt_names: set[str] = set()
    gt_path = cells_dir / f"{fqn}.parquet"
    if gt_path.exists():
        loaded_gt = pq.read_table(gt_path)
        if loaded_gt is not None:
            gt = loaded_gt
            gt_names = set(loaded_gt.schema.names)

    full_sidecar_digest = mode == "full" or (
        mode == "digest-only"
        and manifest_entry.get("values_sorted")
        and not manifest_entry.get("values_capped")
    )

    # Memoized accessor: each extracted column is canonicalized at most once,
    # then reused by both the digest loop below and the keyed comparison.
    # _canon_arrow_col avoids a full Python materialisation for integer columns.
    _ext_cache: dict[str, list[str | None]] = {}

    def _ext_canon(name: str) -> list[str | None]:
        c = _ext_cache.get(name)
        if c is None:
            c = _canon_arrow_col(extracted.column(name), sql_types.get(name, ""))
            _ext_cache[name] = c
        return c

    # Per-column digest over the full decoded column.  Old full sidecars may
    # contain pre-normalized strings (for example "True"/"False" for alias BIT
    # types), so compare decoded values against the current canonical form of the
    # sidecar column.  Sampled and capped sidecars do not contain the whole value
    # set in parquet; for those, the manifest digest remains the full-column
    # authority.
    for col in manifest_entry.get("columns", []):
        name, want_digest = col["name"], col.get("digest")
        if not want_digest or name not in ext_names:
            continue
        got = column_digest(_ext_canon(name))
        expected_digests = {want_digest}
        if full_sidecar_digest and gt is not None and name in gt_names:
            gt_values = _safe_to_pylist(gt.column(name))
            raw_gt_digest = column_digest(gt_values)
            canon_gt_digest = column_digest(_canon_col(gt_values, sql_types.get(name, "")))
            if want_digest not in {raw_gt_digest, canon_gt_digest}:
                res.digest_mismatches.append(name)
                continue
            expected_digests = {canon_gt_digest}
        if got not in expected_digests:
            res.digest_mismatches.append(name)

    key_cols: list[str] = manifest_entry.get("key_columns", []) or []
    if mode == "digest-only" or not key_cols:
        res.mode = "digest-only"
        _diagnose_digest_only(res, extracted, cells_dir, manifest_entry, sql_types, max_samples)
        return res

    if gt is None:
        res.error = f"ground-truth parquet missing: {gt_path.name}"
        return res

    if not key_cols or any(k not in ext_names for k in key_cols):
        res.error = f"key columns {key_cols} not in decoded table"
        return res

    # Re-run the sidecar through canon() too.  canon() is deliberately
    # idempotent for canonical strings and also normalizes older sidecars whose
    # stored text predates newer comparison rules.
    cmp_cols = [n for n in gt.schema.names if n in ext_names and n not in key_cols]
    ext_canon = {n: _ext_canon(n) for n in ext_names}
    gt_canon = {
        n: _canon_col(_safe_to_pylist(gt.column(n)), sql_types.get(n, "")) for n in gt.schema.names
    }

    # Map canonical key -> decoded row index (first occurrence).
    ext_rows = extracted.num_rows
    if len(key_cols) == 1:
        # Fast path: single-key tables (the common case for fact tables).
        # Use the value directly rather than boxing it in a 1-tuple.
        _k0 = key_cols[0]
        _kv = ext_canon[_k0]
        ext_index_1: dict[str | None, int] = {}
        for i in range(ext_rows):
            ext_index_1.setdefault(_kv[i], i)

        for j in range(gt.num_rows):
            key_1 = gt_canon[_k0][j]
            i = ext_index_1.get(key_1)
            if i is None:
                res.missing_keys += 1
                if len(res.samples) < max_samples:
                    res.samples.append(((key_1,), "<row>", None, "<missing in decode>"))
                continue
            for n in cmp_cols:
                res.cells_total += 1
                want = gt_canon[n][j]
                got = ext_canon[n][i]
                if got == want:
                    res.cells_ok += 1
                else:
                    res.col_mismatches[n] = res.col_mismatches.get(n, 0) + 1
                    if len(res.samples) < max_samples:
                        res.samples.append(((key_1,), n, got, want))
        return res

    # Multi-key path (unchanged).
    ext_index: dict[tuple[str | None, ...], int] = {}
    for i in range(ext_rows):
        ext_index.setdefault(tuple(ext_canon[k][i] for k in key_cols), i)

    for j in range(gt.num_rows):
        key = tuple(gt_canon[k][j] for k in key_cols)
        i = ext_index.get(key)
        if i is None:
            res.missing_keys += 1
            if len(res.samples) < max_samples:
                res.samples.append((key, "<row>", None, "<missing in decode>"))
            continue
        for n in cmp_cols:
            res.cells_total += 1
            want = gt_canon[n][j]
            got = ext_canon[n][i]
            if got == want:
                res.cells_ok += 1
            else:
                res.col_mismatches[n] = res.col_mismatches.get(n, 0) + 1
                if len(res.samples) < max_samples:
                    res.samples.append((key, n, got, want))

    return res


def verify_bak(
    extracted_tables: dict[str, "pa.Table"], cells_dir: Path
) -> dict[str, TableVerifyResult]:
    """Verify every table in a manifest that has a decoded Arrow table in hand.

    Tables are independent, so verification runs concurrently using a bounded
    thread pool.  The pool size is capped at 4 to avoid oversubscribing when the
    outer fixture runner already uses ``ProcessPoolExecutor`` across fixtures.
    The cap can be overridden with the ``MSSQLBAK_VERIFY_THREADS`` environment
    variable (set to ``1`` to force serial for debugging).
    """
    manifest = load_manifest(cells_dir)
    entries = manifest.get("tables", [])

    default_workers = 1  # serial by default; GIL prevents threading gains on large tables
    n_workers = int(os.environ.get("MSSQLBAK_VERIFY_THREADS", default_workers))

    def _run_entry(entry: dict) -> tuple[str, TableVerifyResult]:
        fqn = entry["fqn"]
        ext = extracted_tables.get(fqn)
        if ext is None:
            r = TableVerifyResult(fqn=fqn, mode=entry.get("mode", "full"))
            r.error = "table absent from decode output"
            return fqn, r
        return fqn, verify_table(ext, cells_dir, entry)

    out: dict[str, TableVerifyResult] = {}
    if n_workers == 1 or len(entries) <= 1:
        for entry in entries:
            fqn, r = _run_entry(entry)
            out[fqn] = r
        return out

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = {pool.submit(_run_entry, entry): entry["fqn"] for entry in entries}
        for fut in as_completed(futures):
            fqn, r = fut.result()
            out[fqn] = r
    return out
