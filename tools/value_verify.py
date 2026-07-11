"""Row-level value diff engine — the per-cell ground-truth comparator.

Aligns a decoded Arrow table to its ``<bak>.cells/<fqn>.parquet`` ground truth by
the manifest's ``key_columns``, canonicalizes both sides through
:func:`tools.cell_canon.canon`, counts matching cells, and verifies the per-column
:func:`tools.cell_canon.column_digest`. This catches the "right aggregate, wrong
cells" defect class that ``correctness_coverage``'s null/min-max/row-count checks
cannot.

The ground-truth capture side (``tools/cells_capture.py``) is built separately and
needs a live SQL Server; this module is fully offline given a ``.cells/`` sidecar.

Performance notes
-----------------
The hot paths for large tables are fully vectorized via PyArrow compute:

* :func:`_canon_to_arrow` canonicalizes an Arrow column to a ``pa.string()`` array
  entirely in C++ for the high-volume SQL types (integers, strings, char, bit,
  decimal, uniqueidentifier).  Only float/real, temporal, binary, XML, spatial, and
  ``sql_variant`` fall back to a Python-per-value loop.

* :func:`_arrow_column_digest` reproduces :func:`cell_canon.column_digest`
  bit-for-bit using Arrow's C++ sort and zero-copy ``memoryview`` buffer access
  rather than materializing Python ``bytes`` objects per value.

* :func:`verify_table` uses ``pc.take`` + ``pc.equal`` for the keyed cell
  comparison instead of a Python ``dict`` + per-cell ``==`` loop.  The digest is
  skipped for ``full``-mode tables where the keyed compare already covers every row.

* :func:`verify_bak` runs table verification concurrently: the Arrow C++ hot paths
  release the GIL, so a small thread pool gives real parallelism.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc

from tools.cell_canon import _base_type, _canon_bit, canon

if TYPE_CHECKING:
    pass

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

    return functools.partial(canon, sql_type=sql_type)


def _canon_col(values: list[Any], sql_type: str) -> list[str | None]:
    f = _make_canonicalizer(sql_type)
    return [f(v) for v in values]


# ---------------------------------------------------------------------------
# Vectorized Arrow canonicalization
# ---------------------------------------------------------------------------

# SQL base types with a single-call C++ fast path in _canon_to_arrow.
_INT_ARROW = frozenset({"int", "bigint", "smallint", "tinyint"})
_STR_ARROW = frozenset({"varchar", "nvarchar", "text", "ntext", "hierarchyid"})
_CHAR_ARROW = frozenset({"char", "nchar"})
_DECIMAL_ARROW = frozenset({"decimal", "numeric", "money", "smallmoney"})


def _canon_to_arrow(
    col: "pa.ChunkedArray | pa.Array", sql_type: str
) -> "pa.Array":
    """Canonicalize *col* to a ``pa.string()`` array, using C++ where possible.

    Fast paths (no Python loop):
    * ``int/bigint/smallint/tinyint`` → ``pc.cast(col, pa.string())``
    * ``varchar/nvarchar/text/ntext/hierarchyid`` → identity or cast to string
    * ``char/nchar`` → ``pc.utf8_rtrim(col, " ")``  (trailing-space trim)
    * ``bit`` (bool Arrow type) → ``pc.if_else(col, "1", "0")``
    * ``decimal/numeric/money/smallmoney`` (decimal128) → ``pc.cast(col, pa.string())``
    * ``uniqueidentifier`` → ``pc.utf8_lower(col)``

    Python per-value fallback (via ``canon()``) for: float/real, all temporal
    types, binary/varbinary/timestamp/image, xml, geometry/geography,
    datetimeoffset, sql_variant, and any type whose Arrow storage doesn't
    match the expected fast-path Arrow type.
    """
    arr = col.combine_chunks() if hasattr(col, "chunks") else col
    t = _base_type(sql_type)

    if t in _INT_ARROW and pa.types.is_integer(arr.type):
        return pc.cast(arr, pa.string())

    if t in _STR_ARROW:
        if pa.types.is_large_string(arr.type):
            return arr.cast(pa.string())
        if pa.types.is_string(arr.type):
            return arr
        return pc.cast(arr, pa.string())

    if t in _CHAR_ARROW:
        s = arr if pa.types.is_string(arr.type) else pc.cast(arr, pa.string())
        return pc.utf8_rtrim(s, " ")

    if t == "bit" and pa.types.is_boolean(arr.type):
        return pc.if_else(arr, "1", "0")

    if t in _DECIMAL_ARROW and pa.types.is_decimal(arr.type):
        return pc.cast(arr, pa.string())

    if t == "uniqueidentifier":
        s = arr if pa.types.is_string(arr.type) else pc.cast(arr, pa.string())
        return pc.utf8_lower(s)

    # Python fallback: float/real, temporal, binary, xml, spatial, sql_variant.
    return pa.array(_canon_col(_safe_to_pylist(arr), sql_type), pa.string())


def _arrow_column_digest(arr: "pa.Array | pa.ChunkedArray") -> str:
    """Reproduce :func:`cell_canon.column_digest` bit-for-bit from an Arrow string array.

    Drops nulls, sorts in C++ (same lexicographic order as Python ``sorted()``
    on UTF-8 bytes), then feeds each value as
    ``uint32-LE-length || UTF-8-bytes`` into SHA-256 via zero-copy
    ``memoryview`` slices of the Arrow string buffer — no Python ``bytes``
    allocation per value.

    Handles both ``pa.string()`` (int32 offsets) and ``pa.large_string()``
    (int64 offsets); large_string is cast to string first for uniform buffer access.
    Accepts ChunkedArray (e.g. from parquet reads) in addition to plain Array.
    """
    # Consolidate chunks so we can access the underlying Arrow buffer.
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    arr = pc.drop_null(arr)
    # Another combine after drop_null in case it returns a ChunkedArray.
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    if pa.types.is_large_string(arr.type):
        arr = arr.cast(pa.string())
    arr = arr.sort()
    n = len(arr)
    h = hashlib.sha256()
    if n == 0:
        return "sha256:" + h.hexdigest()

    # Arrow string buffer layout for a freshly sorted (offset == 0) array:
    #   buffers[0]: validity bitmap (None after drop_null)
    #   buffers[1]: int32 offsets  (n+1 values)
    #   buffers[2]: contiguous UTF-8 value bytes
    buffers = arr.buffers()
    offset = arr.offset  # 0 for freshly created arrays, handled generically
    offsets_np = np.frombuffer(buffers[1], dtype=np.int32)[offset : offset + n + 1]
    lengths_u32 = (offsets_np[1:] - offsets_np[:-1]).astype(np.uint32)

    # Zero-copy views: avoids one Python bytes object per value.
    # ndarray.data is already typed as memoryview in numpy stubs.
    lengths_mv = lengths_u32.view(np.uint8).data
    vals_mv = memoryview(buffers[2])

    for i in range(n):
        # Feeds: uint32-LE length (4 B) then UTF-8 bytes — identical to
        # len(b).to_bytes(4, "little") + b in cell_canon.column_digest.
        h.update(lengths_mv[4 * i : 4 * i + 4])
        h.update(vals_mv[int(offsets_np[i]) : int(offsets_np[i + 1])])

    return "sha256:" + h.hexdigest()


# ---------------------------------------------------------------------------
# Legacy helpers kept for backward-compat and error-path diagnostics
# ---------------------------------------------------------------------------


def _canon_arrow_col(col: "pa.ChunkedArray | pa.Array", sql_type: str) -> list[str | None]:
    """Canonicalize an Arrow column to a Python list of canonical strings.

    Used by :func:`_diagnose_digest_only` (error path).  New code should call
    :func:`_canon_to_arrow` and stay in Arrow end-to-end.
    """
    t = _base_type(sql_type)
    if t in ("money", "smallmoney", "decimal", "numeric"):
        try:
            arr = col.combine_chunks() if hasattr(col, "chunks") else col
            if pa.types.is_decimal(arr.type):
                return pc.cast(arr, pa.string()).to_pylist()
        except Exception:
            pass
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
            for v in _canon_arrow_col(gt.column(name), sql_types.get(name, ""))
            if v is not None
        )
        got = sorted(
            v
            for v in _canon_arrow_col(extracted.column(name), sql_types.get(name, ""))
            if v is not None
        )
        want_set, got_set = set(want), set(got)
        only_got = [v for v in got if v not in want_set]
        only_want = [v for v in want if v not in got_set]
        for ex in only_got[: per_col // 2 or 1]:
            res.samples.append((name, "got-only", ex, None))
        for ex in only_want[: per_col // 2 or 1]:
            res.samples.append((name, "want-only", None, ex))


# ---------------------------------------------------------------------------
# Core verification
# ---------------------------------------------------------------------------


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

    Canonicalization and digest computation are vectorized via
    :func:`_canon_to_arrow` and :func:`_arrow_column_digest`; the keyed
    cell comparison uses ``pc.take`` + ``pc.equal`` rather than a Python
    per-cell loop.

    Full-mode tables (≤ ``sample_threshold`` rows) skip the digest check
    because the keyed compare already covers every row.
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

    # Memoized Arrow canonicalization of extracted columns.
    # Each column is canonicalized at most once and reused for both the
    # digest check and the keyed comparison.
    _ext_arr_cache: dict[str, pa.Array] = {}

    def _ext_arr(name: str) -> pa.Array:
        a = _ext_arr_cache.get(name)
        if a is None:
            a = _canon_to_arrow(extracted.column(name), sql_types.get(name, ""))
            _ext_arr_cache[name] = a
        return a

    # ── Per-column digest ────────────────────────────────────────────────────
    # Skip digest for ``full`` mode: the keyed compare below covers every row,
    # making the digest check redundant.  For ``sample`` and ``digest-only``
    # modes the digest is the authority for the full column.
    skip_digest = mode == "full"

    # For ``digest-only`` tables whose parquet stores the complete sorted
    # non-null canonical values (``values_sorted`` and not ``values_capped``),
    # re-derive the expected digest from the parquet to handle older sidecars
    # whose stored strings predate the current ``canon()`` rules.
    gt_recanon = (
        mode == "digest-only"
        and manifest_entry.get("values_sorted")
        and not manifest_entry.get("values_capped")
        and gt is not None
    )

    if not skip_digest:
        for col in manifest_entry.get("columns", []):
            name, want_digest = col["name"], col.get("digest")
            if not want_digest or name not in ext_names:
                continue
            got = _arrow_column_digest(_ext_arr(name))
            expected_digests = {want_digest}
            if gt_recanon and name in gt_names:
                assert gt is not None
                # Two reference digests: (a) raw parquet strings as stored,
                # (b) after re-running through canon() — handles old sidecars.
                raw_gt_arr = (
                    gt.column(name).cast(pa.string())
                    if pa.types.is_large_string(gt.column(name).type)
                    else gt.column(name)
                )
                raw_gt_digest = _arrow_column_digest(raw_gt_arr)
                canon_gt_digest = _arrow_column_digest(
                    _canon_to_arrow(gt.column(name), sql_types.get(name, ""))
                )
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

    if any(k not in ext_names for k in key_cols):
        res.error = f"key columns {key_cols} not in decoded table"
        return res

    # ── Keyed cell comparison ────────────────────────────────────────────────
    # Canonicalize GT columns through the same SSOT so old sidecars are
    # normalized consistently with the extracted side.
    _gt_arr_cache: dict[str, pa.Array] = {}

    def _gt_arr(name: str) -> pa.Array:
        a = _gt_arr_cache.get(name)
        if a is None:
            a = _canon_to_arrow(gt.column(name), sql_types.get(name, ""))  # type: ignore[union-attr]
            _gt_arr_cache[name] = a
        return a

    cmp_cols = [n for n in gt.schema.names if n in ext_names and n not in key_cols]

    if len(key_cols) == 1:
        # ── Single-key fast path ─────────────────────────────────────────────
        k0 = key_cols[0]
        ext_key_list = _ext_arr(k0).to_pylist()
        ext_index_1: dict[str | None, int] = {}
        for i, k in enumerate(ext_key_list):
            ext_index_1.setdefault(k, i)

        gt_key_list = _gt_arr(k0).to_pylist()
        matched_gt: list[int] = []
        matched_ext: list[int] = []
        for j, key in enumerate(gt_key_list):
            ei = ext_index_1.get(key)
            if ei is None:
                res.missing_keys += 1
                if len(res.samples) < max_samples:
                    res.samples.append(((key,), "<row>", None, "<missing in decode>"))
            else:
                matched_gt.append(j)
                matched_ext.append(ei)

        if matched_gt:
            gt_idx = pa.array(matched_gt, pa.int64())
            ext_idx = pa.array(matched_ext, pa.int64())
            n_matched = len(matched_gt)

            for name in cmp_cols:
                gt_col = pc.take(_gt_arr(name), gt_idx)
                ext_col = pc.take(_ext_arr(name), ext_idx)

                # Null-aware equality: both-null counts as equal, matching
                # the previous ``got == want`` semantics (None == None is True).
                raw_eq = pc.equal(gt_col, ext_col)
                both_null = pc.and_(pc.is_null(gt_col), pc.is_null(ext_col))
                match = pc.if_else(pc.is_null(raw_eq), both_null, raw_eq)

                ok = pc.sum(match).as_py() or 0
                res.cells_ok += ok
                res.cells_total += n_matched
                mismatches = n_matched - ok
                if mismatches > 0:
                    res.col_mismatches[name] = mismatches
                    if len(res.samples) < max_samples:
                        match_list = match.to_pylist()
                        name_arr_ext = _ext_arr(name)
                        name_arr_gt = _gt_arr(name)
                        for pos, is_ok in enumerate(match_list):
                            if not is_ok:
                                res.samples.append((
                                    (gt_key_list[matched_gt[pos]],),
                                    name,
                                    name_arr_ext[matched_ext[pos]].as_py(),
                                    name_arr_gt[matched_gt[pos]].as_py(),
                                ))
                                if len(res.samples) >= max_samples:
                                    break
        return res

    # ── Multi-key path ───────────────────────────────────────────────────────
    ext_key_lists = [_ext_arr(k).to_pylist() for k in key_cols]
    ext_index: dict[tuple[str | None, ...], int] = {}
    for i in range(extracted.num_rows):
        key = tuple(ext_key_lists[ki][i] for ki in range(len(key_cols)))
        ext_index.setdefault(key, i)

    gt_key_lists = [_gt_arr(k).to_pylist() for k in key_cols]
    matched_gt_m: list[int] = []
    matched_ext_m: list[int] = []
    for j in range(gt.num_rows):
        key = tuple(gt_key_lists[ki][j] for ki in range(len(key_cols)))
        ei = ext_index.get(key)
        if ei is None:
            res.missing_keys += 1
            if len(res.samples) < max_samples:
                res.samples.append((key, "<row>", None, "<missing in decode>"))
        else:
            matched_gt_m.append(j)
            matched_ext_m.append(ei)

    if matched_gt_m:
        gt_idx_m = pa.array(matched_gt_m, pa.int64())
        ext_idx_m = pa.array(matched_ext_m, pa.int64())
        n_matched = len(matched_gt_m)

        for name in cmp_cols:
            gt_col = pc.take(_gt_arr(name), gt_idx_m)
            ext_col = pc.take(_ext_arr(name), ext_idx_m)

            raw_eq = pc.equal(gt_col, ext_col)
            both_null = pc.and_(pc.is_null(gt_col), pc.is_null(ext_col))
            match = pc.if_else(pc.is_null(raw_eq), both_null, raw_eq)

            ok = pc.sum(match).as_py() or 0
            res.cells_ok += ok
            res.cells_total += n_matched
            mismatches = n_matched - ok
            if mismatches > 0:
                res.col_mismatches[name] = mismatches
                if len(res.samples) < max_samples:
                    match_list = match.to_pylist()
                    name_arr_ext = _ext_arr(name)
                    name_arr_gt = _gt_arr(name)
                    for pos, is_ok in enumerate(match_list):
                        if not is_ok:
                            j = matched_gt_m[pos]
                            key_t = tuple(gt_key_lists[ki][j] for ki in range(len(key_cols)))
                            res.samples.append((
                                key_t,
                                name,
                                name_arr_ext[matched_ext_m[pos]].as_py(),
                                name_arr_gt[j].as_py(),
                            ))
                            if len(res.samples) >= max_samples:
                                break

    return res


def verify_bak(
    extracted_tables: dict[str, "pa.Table"], cells_dir: Path
) -> dict[str, TableVerifyResult]:
    """Verify every table in a manifest that has a decoded Arrow table in hand.

    Tables are independent and verified concurrently.  Because the hot paths
    in :func:`verify_table` now run in Arrow C++ (which releases the GIL),
    a thread pool gives real parallelism.  The pool size defaults to
    ``min(4, cpu_count)`` and can be overridden with the
    ``MSSQLBAK_VERIFY_THREADS`` environment variable (set to ``1`` for serial
    execution when debugging).
    """
    manifest = load_manifest(cells_dir)
    entries = manifest.get("tables", [])

    default_workers = min(4, os.cpu_count() or 1)
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
