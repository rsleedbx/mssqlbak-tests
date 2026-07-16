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
  decimal, uniqueidentifier, **date, datetime/datetime2/smalldatetime, time**).
  Only float/real, binary, XML, spatial, datetimeoffset, and ``sql_variant`` fall
  back to a Python-per-value loop.

* :func:`_arrow_column_digest` reproduces :func:`cell_canon.column_digest`
  bit-for-bit using numpy buffer assembly — the interleaved length-prefixed byte
  stream is built in C via scatter operations and fed to SHA-256 as a single
  :py:meth:`~hashlib.HASH.update` call per :data:`_HASH_BLOCK_ROWS` rows.
  No Python loop over individual values.

* :func:`_arrow_ordered_column_digest` similarly vectorizes the ordered hash-feed,
  emitting null sentinels via masked prefix assembly and gathering non-null value
  bytes without a Python row loop.

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

from mssqlbak.sink import resolve_sanitized_name
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
    order_mismatches: list[str] = field(default_factory=list)
    missing_keys: int = 0
    samples: list[tuple[Any, str, str | None, str | None]] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return (
            self.error is None
            and not self.col_mismatches
            and not self.digest_mismatches
            and not self.order_mismatches
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
_DATE_ARROW = frozenset({"date"})
_DATETIME_ARROW = frozenset({"datetime", "datetime2", "smalldatetime"})
_TIME_ARROW = frozenset({"time"})

# Per-block row cap for vectorized hash-feed to bound transient RAM.
# At 2M rows × avg 50 bytes/value the output buffer is ~108 MB — well within budget.
_HASH_BLOCK_ROWS = 1 << 21  # 2 097 152 rows


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
    * ``date`` (Arrow date32) → ``pc.strftime(col, "%Y-%m-%d")``
    * ``datetime/datetime2/smalldatetime`` (tz-naive Arrow timestamp) →
      ``pc.strftime(col, "%Y-%m-%dT%H:%M:%S")`` then strip the ``.000000`` suffix
      to reproduce Python ``isoformat()``'s conditional-microseconds behaviour.
    * ``time`` (Arrow time32/time64) → same strftime + ``.000000`` strip approach.

    Python per-value fallback (via ``canon()``) for: float/real,
    binary/varbinary/timestamp/image, xml, geometry/geography,
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

    # date32 → "YYYY-MM-DD"  (matches Python date.isoformat())
    if t in _DATE_ARROW and pa.types.is_date(arr.type):
        return pc.strftime(arr, format="%Y-%m-%d")

    # tz-naive timestamp → "YYYY-MM-DDTHH:MM:SS[.ffffff]"
    # Arrow's strftime embeds sub-second precision directly in %S (not %f, which is
    # not a valid Arrow format specifier).  For timestamp[us], %S emits "SS.ffffff";
    # for timestamp[s], it emits plain "SS".  Cast to microsecond precision first so
    # the output is always 0 or 6 decimal places, matching Python datetime.isoformat().
    if t in _DATETIME_ARROW and pa.types.is_timestamp(arr.type) and arr.type.tz is None:
        arr_us = pc.cast(arr, pa.timestamp("us")) if arr.type.unit != "us" else arr
        formatted = pc.strftime(arr_us, format="%Y-%m-%dT%H:%M:%S")
        return pc.replace_substring_regex(formatted, pattern=r"\.000000$", replacement="")

    # time32/time64 → "HH:MM:SS[.ffffff]"  (matches Python time.isoformat())
    # Same %S convention: cast to time64[us] then strip ".000000".
    if t in _TIME_ARROW and pa.types.is_time(arr.type):
        arr_us: "pa.Array" = (
            pc.cast(arr, pa.time64("us")) if arr.type.unit != "us" else arr
        )
        formatted = pc.strftime(arr_us, format="%H:%M:%S")
        return pc.replace_substring_regex(formatted, pattern=r"\.000000$", replacement="")

    # Python fallback: float/real, binary, xml, spatial, datetimeoffset, sql_variant.
    return pa.array(_canon_col(_safe_to_pylist(arr), sql_type), pa.string())


def _arrow_column_digest(arr: "pa.Array | pa.ChunkedArray") -> str:
    """Reproduce :func:`cell_canon.column_digest` bit-for-bit from an Arrow string array.

    Drops nulls, sorts in C++ (same lexicographic order as Python ``sorted()``
    on UTF-8 bytes), then feeds each value as
    ``uint32-LE-length || UTF-8-bytes`` into SHA-256.

    Vectorized via numpy: assembles the interleaved length-prefixed byte stream
    entirely in C without a Python loop, then calls ``h.update`` once per
    :data:`_HASH_BLOCK_ROWS` rows so the transient buffer stays bounded.

    Handles both ``pa.string()`` (int32 offsets) and ``pa.large_string()``
    (int64 offsets); large_string is cast to string first for uniform buffer access.
    Accepts ChunkedArray (e.g. from parquet reads) in addition to plain Array.
    """
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    arr = pc.drop_null(arr)
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    if pa.types.is_large_string(arr.type):
        arr = arr.cast(pa.string())
    arr = arr.sort()
    n = len(arr)
    h = hashlib.sha256()
    if n == 0:
        return "sha256:" + h.hexdigest()

    # Arrow string buffer layout after drop_null + sort (array offset is 0):
    #   buffers[1]: int32 offsets (n+1 values)
    #   buffers[2]: contiguous UTF-8 value bytes
    buffers = arr.buffers()
    arr_off = arr.offset  # almost always 0 after a fresh sort
    offsets_np = np.frombuffer(buffers[1], dtype=np.int32)[arr_off : arr_off + n + 1].astype(
        np.int64
    )
    buf_u8 = np.frombuffer(buffers[2], dtype=np.uint8)

    for blk_start in range(0, n, _HASH_BLOCK_ROWS):
        blk_end = min(blk_start + _HASH_BLOCK_ROWS, n)
        blen = blk_end - blk_start
        blk_off = offsets_np[blk_start : blk_end + 1]  # (blen+1,) int64
        blk_lens = (blk_off[1:] - blk_off[:-1]).astype(np.uint32)  # (blen,) uint32
        buf_start = int(blk_off[0])
        buf_end = int(blk_off[blen])
        blk_total = buf_end - buf_start

        # Output stream: [len0(4B), val0, len1(4B), val1, …]
        # Row i's length prefix starts at: blk_rel_off[i] + 4*i
        # Row i's value bytes start at: blk_rel_off[i] + 4*(i+1)
        out = np.empty(4 * blen + blk_total, dtype=np.uint8)
        blk_rel = (blk_off[:-1] - buf_start).astype(np.int64)  # relative offsets, shape (blen,)
        len_pos = blk_rel + 4 * np.arange(blen, dtype=np.int64)
        # Assign 4-byte LE length prefix for each row.
        out[len_pos[:, None] + np.arange(4, dtype=np.int64)] = blk_lens.view(np.uint8).reshape(
            blen, 4
        )
        if blk_total > 0:
            # For value byte j (global within block): its output position is
            # j + 4*(row_index+1) where row_index = which row owns byte j.
            # row_index is computed via np.repeat without a Python loop.
            blk_lens_i64 = blk_lens.astype(np.int64)
            val_dst = np.arange(blk_total, dtype=np.int64) + 4 * np.repeat(
                np.arange(1, blen + 1, dtype=np.int64), blk_lens_i64
            )
            out[val_dst] = buf_u8[buf_start:buf_end]
        h.update(out.data)

    return "sha256:" + h.hexdigest()


def _arrow_ordered_column_digest(arr: "pa.Array | pa.ChunkedArray") -> str:
    """Reproduce :func:`cell_canon.column_ordered_digest` bit-for-bit from an Arrow string array.

    Feeds each value **in its original position order** (no sort) as
    ``uint32-LE-length || UTF-8-bytes`` into SHA-256.  Nulls emit the 4-byte
    sentinel ``0xFFFFFFFF`` with no payload, matching ``column_ordered_digest``.

    Vectorized via numpy: assembles the length-prefixed stream in C, treating
    null rows' 4-byte prefix as the sentinel and gathering only non-null value
    bytes from the Arrow buffer, then calls ``h.update`` once per
    :data:`_HASH_BLOCK_ROWS` rows so the transient buffer stays bounded.

    Handles both ``pa.string()`` and ``pa.large_string()`` arrays and
    ChunkedArrays from parquet reads.
    """
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    if pa.types.is_large_string(arr.type):
        arr = arr.cast(pa.string())

    n = len(arr)
    h = hashlib.sha256()
    if n == 0:
        return "sha256:" + h.hexdigest()

    # Arrow string buffer layout:
    #   buffers[0]: validity bitmap (may be None when all non-null)
    #   buffers[1]: int32 offsets (n+1 values)
    #   buffers[2]: contiguous UTF-8 value bytes (null rows have length 0 in PyArrow)
    buffers = arr.buffers()
    arr_off = arr.offset
    offsets_np = np.frombuffer(buffers[1], dtype=np.int32)[arr_off : arr_off + n + 1].astype(
        np.int64
    )
    buf_u8 = np.frombuffer(buffers[2], dtype=np.uint8) if buffers[2] is not None else np.empty(
        0, dtype=np.uint8
    )

    # Validity: True = non-null.  pc.is_valid is faster than unpacking the bitmap.
    valid_np = pc.is_valid(arr).to_numpy(zero_copy_only=False)  # bool array, shape (n,)

    for blk_start in range(0, n, _HASH_BLOCK_ROWS):
        blk_end = min(blk_start + _HASH_BLOCK_ROWS, n)
        blen = blk_end - blk_start
        blk_off = offsets_np[blk_start : blk_end + 1]  # (blen+1,) int64
        blk_raw_lens = (blk_off[1:] - blk_off[:-1]).astype(np.uint32)  # Arrow buffer lengths
        blk_valid = valid_np[blk_start:blk_end]  # bool (blen,)

        # For null rows: effective value length is 0 (sentinel is 4 bytes, no value).
        # For non-null rows: effective value length is the Arrow buffer length.
        eff_lens = np.where(blk_valid, blk_raw_lens, np.uint32(0))  # (blen,) uint32
        eff_total = int(eff_lens.sum())

        # Row i's 4-byte prefix starts at: 4*i + prefix_eff[i]
        # where prefix_eff[i] = sum of eff_lens for rows 0..i-1.
        prefix_eff = np.empty(blen, dtype=np.int64)
        prefix_eff[0] = 0
        if blen > 1:
            np.cumsum(eff_lens[:-1], out=prefix_eff[1:])
        row_pos = 4 * np.arange(blen, dtype=np.int64) + prefix_eff

        total_out = 4 * blen + eff_total
        out = np.empty(total_out, dtype=np.uint8)

        # Write 4-byte prefixes:
        #   null rows  → 0xFF 0xFF 0xFF 0xFF (sentinel)
        #   non-null   → uint32-LE length
        null_mask = ~blk_valid
        if null_mask.any():
            null_pos = row_pos[null_mask]
            out[null_pos[:, None] + np.arange(4, dtype=np.int64)] = np.uint8(0xFF)
        if blk_valid.any():
            nonnull_pos = row_pos[blk_valid]
            nonnull_lens = blk_raw_lens[blk_valid]  # uint32
            out[nonnull_pos[:, None] + np.arange(4, dtype=np.int64)] = (
                nonnull_lens.view(np.uint8).reshape(-1, 4)
            )
            # Gather non-null value bytes from the Arrow buffer into `out`.
            # nonnull_src_start[rr] = start offset in buf_u8 of non-null row rr.
            nonnull_src_start = blk_off[:-1][blk_valid]  # int64
            nonnull_lens_i64 = nonnull_lens.astype(np.int64)
            nonnull_total = int(nonnull_lens_i64.sum())
            if nonnull_total > 0:
                # Cumulative start of each non-null row within the gathered bytes.
                nn_prefix = np.empty(len(nonnull_pos), dtype=np.int64)
                nn_prefix[0] = 0
                if len(nonnull_pos) > 1:
                    np.cumsum(nonnull_lens_i64[:-1], out=nn_prefix[1:])
                # intra[k] = within-row offset for the k-th gathered value byte.
                intra = np.arange(nonnull_total, dtype=np.int64) - np.repeat(
                    nn_prefix, nonnull_lens_i64
                )
                dst = np.repeat(nonnull_pos + 4, nonnull_lens_i64) + intra
                src = np.repeat(nonnull_src_start, nonnull_lens_i64) + intra
                out[dst] = buf_u8[src]

        h.update(out.data)

    return "sha256:" + h.hexdigest()


def _key_sort_indices(key_arrs: list["pa.Array"]) -> "pa.Array":
    """Return sort indices that put rows in ascending Arrow-binary-order by key columns.

    Uses ``pc.sort_indices`` with a stable multi-key sort over canonical string
    arrays so the order matches what :func:`backfill_ordered_digest` computes
    from the GT parquet.

    ``key_arrs`` are canonical string arrays (output of ``_canon_to_arrow``),
    one per key column, in key-ordinal order.
    """
    if len(key_arrs) == 1:
        return pc.sort_indices(key_arrs[0])

    # Build a temporary RecordBatch and sort it multi-column.
    fields = [pa.field(f"k{i}", pa.string()) for i in range(len(key_arrs))]
    rb = pa.record_batch(key_arrs, schema=pa.schema(fields))
    sort_keys = [(f"k{i}", "ascending") for i in range(len(key_arrs))]
    return pc.sort_indices(rb, sort_keys=sort_keys)


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
    _diag_ext_names: set[str] = set(extracted.schema.names)
    per_col = max(2, max_samples // max(1, len(res.digest_mismatches)))
    for name in res.digest_mismatches:
        ext_col_name = resolve_sanitized_name(_diag_ext_names, name, column=True)
        if ext_col_name is None or name not in gt.schema.names:
            continue
        want = sorted(
            v
            for v in _canon_arrow_col(gt.column(name), sql_types.get(name, ""))
            if v is not None
        )
        got = sorted(
            v
            for v in _canon_arrow_col(extracted.column(ext_col_name), sql_types.get(name, ""))
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
    level: str = "full",
    max_samples: int = 20,
) -> TableVerifyResult:
    """Diff ``extracted`` against the ground-truth parquet for one table.

    ``manifest_entry`` is the per-table object from ``_manifest.json`` (fqn,
    key_columns, mode, columns[{name, sql_type, digest, ...}]).

    Canonicalization and digest computation are vectorized via
    :func:`_canon_to_arrow` and :func:`_arrow_column_digest`; the keyed
    cell comparison uses ``pc.take`` + ``pc.equal`` rather than a Python
    per-cell loop.

    ``level`` controls verification depth:

    * ``"full"`` (default): exhaustive keyed row-level compare; also catches
      value-preserving row misalignment/transposition.  Full-mode manifest
      tables skip the redundant digest (the keyed compare already covers every
      row).
    * ``"digest"``: per-column SHA-256 digest check only — O(rows) with no GT
      parquet read and no Python key index.  Catches any multiset-level value
      corruption (wrong values somewhere in a column) combined with the
      already-present row-count and null-count aggregates.  Does *not* detect
      value-preserving row reorderings.  Manifest ``digest-only`` tables are
      handled identically to ``full`` (their path is already digest-based).
    * ``"none"``: not handled here — the runner skips calling this function.
    """
    import pyarrow.parquet as pq

    fqn = manifest_entry["fqn"]
    mode = manifest_entry.get("mode", "full")
    res = TableVerifyResult(fqn=fqn, mode=mode)

    sql_types: dict[str, str] = {
        c["name"]: _effective_sql_type(c) for c in manifest_entry.get("columns", [])
    }
    _raw_ext_names: set[str] = set(extracted.schema.names)

    def _resolve_ext(name: str) -> str | None:
        """Return the column name as it exists in *extracted*, or None.

        The manifest always stores original SQL names (e.g. ``"City Key"``).
        When the extracted table came back from a DeltaSink round-trip the
        column was sanitized to ``"City_Key"``.  This resolver tries the
        verbatim name first, then the sanitized form, so both paths work
        transparently.
        """
        return resolve_sanitized_name(_raw_ext_names, name, column=True)

    # ── Decide which GT parquet reads are required ───────────────────────────
    # For level="digest" we skip the parquet entirely for full/sample manifest
    # tables (no keyed compare, no gt_recanon path).  We still need it for
    # digest-only manifest tables with gt_recanon (handled below).
    _need_gt_for_keyed = level == "full"
    _maybe_need_gt_for_recanon = (
        mode == "digest-only"
        and manifest_entry.get("values_sorted")
        and not manifest_entry.get("values_capped")
    )
    _load_gt = _need_gt_for_keyed or _maybe_need_gt_for_recanon

    gt: pa.Table | None = None
    gt_names: set[str] = set()
    gt_path = cells_dir / f"{fqn}.parquet"
    if _load_gt and gt_path.exists():
        loaded_gt = pq.read_table(gt_path)
        if loaded_gt is not None:
            gt = loaded_gt
            gt_names = set(loaded_gt.schema.names)

    # Memoized Arrow canonicalization of extracted columns.
    # Each column is canonicalized at most once and reused for both the
    # digest check and the keyed comparison.  The cache key is the *manifest*
    # name (original SQL form); the actual column fetch uses _resolve_ext so
    # sanitized Delta round-trip names are found transparently.
    _ext_arr_cache: dict[str, pa.Array] = {}

    def _ext_arr(name: str) -> pa.Array:
        a = _ext_arr_cache.get(name)
        if a is None:
            ext_col_name = _resolve_ext(name)
            if ext_col_name is None:
                raise KeyError(f"Column {name!r} not found in extracted table (tried sanitized form too)")
            a = _canon_to_arrow(extracted.column(ext_col_name), sql_types.get(name, ""))
            _ext_arr_cache[name] = a
        return a

    # ── Per-column digest ────────────────────────────────────────────────────
    # Skip digest for ``full`` mode on full-manifest tables: the keyed compare
    # below covers every row, making the digest redundant.  For ``sample`` and
    # ``digest-only`` manifest modes, and always when level="digest", run the
    # digest check for the whole-column aggregate signal.
    skip_digest = mode == "full" and level == "full"

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
            if not want_digest or _resolve_ext(name) is None:
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

    # ── Fast path: digest level — ordered digest check then return ───────────
    # For full/sample manifest-mode tables with level="digest" we do two checks
    # and then return without reading the GT parquet or building a key index:
    #   1. Multiset digest (already done above) — catches wrong values anywhere.
    #   2. Key-ordered digest (when ordered_digest present in manifest) — catches
    #      value-preserving row misalignment/transposition.
    # digest-only manifest tables fall through to their own branch below.
    if level == "digest" and mode != "digest-only":
        # Key-ordered digest: only valid for full-mode tables where the GT parquet
        # contains every row.  For sample-mode tables the parquet has fewer rows than
        # the extracted table, so the pre-computed ordered_digest from backfill would
        # never match — skip the ordered check but still return here on the multiset
        # digest (reading the GT parquet / building a key index would be wrong for a
        # sampled table).  If any other prerequisite is missing, skip gracefully
        # (multiset-only degradation).
        key_cols_digest: list[str] = manifest_entry.get("key_columns", []) or []
        if mode != "sample" and key_cols_digest and extracted.num_rows > 0:
            # Build canonical key arrays (reuse the _ext_arr cache).
            key_arrs = [_ext_arr(k) for k in key_cols_digest if _resolve_ext(k) is not None]
            if len(key_arrs) == len(key_cols_digest):
                sort_idx = _key_sort_indices(key_arrs)
                for col in manifest_entry.get("columns", []):
                    name = col["name"]
                    want_ordered = col.get("ordered_digest")
                    if not want_ordered or name in key_cols_digest or _resolve_ext(name) is None:
                        continue
                    reordered = pc.take(_ext_arr(name), sort_idx)
                    got_ordered = _arrow_ordered_column_digest(reordered)
                    if got_ordered != want_ordered:
                        res.order_mismatches.append(name)

        res.mode = "digest"
        return res

    key_cols: list[str] = manifest_entry.get("key_columns", []) or []
    if mode == "digest-only" or not key_cols:
        res.mode = "digest-only"
        _diagnose_digest_only(res, extracted, cells_dir, manifest_entry, sql_types, max_samples)
        return res

    if gt is None:
        res.error = f"ground-truth parquet missing: {gt_path.name}"
        return res

    if any(_resolve_ext(k) is None for k in key_cols):
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

    cmp_cols = [n for n in gt.schema.names if _resolve_ext(n) is not None and n not in key_cols]

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
    extracted_tables: dict[str, "pa.Table"],
    cells_dir: Path,
    *,
    level: str = "full",
) -> dict[str, TableVerifyResult]:
    """Verify every table in a manifest that has a decoded Arrow table in hand.

    Tables are independent and verified concurrently.  Because the hot paths
    in :func:`verify_table` now run in Arrow C++ (which releases the GIL),
    a thread pool gives real parallelism.  The pool size defaults to
    ``min(4, cpu_count)`` and can be overridden with the
    ``MSSQLBAK_VERIFY_THREADS`` environment variable (set to ``1`` for serial
    execution when debugging).

    ``level`` is forwarded to :func:`verify_table`; see its docstring for
    ``"full"`` vs ``"digest"`` semantics.
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
        return fqn, verify_table(ext, cells_dir, entry, level=level)

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
