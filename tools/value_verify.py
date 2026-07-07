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

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tools.cell_canon import canon, column_digest

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


def _canon_col(values: list[Any], sql_type: str) -> list[str | None]:
    return [canon(v, sql_type) for v in values]


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
            for v in _canon_col(gt.column(name).to_pylist(), sql_types.get(name, ""))
            if v is not None
        )
        got = sorted(
            v for v in _canon_col(extracted.column(name).to_pylist(), sql_types.get(name, ""))
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

    sql_types: dict[str, str] = {c["name"]: _effective_sql_type(c) for c in manifest_entry.get("columns", [])}
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
        got = column_digest(_canon_col(extracted.column(name).to_pylist(), sql_types[name]))
        expected_digests = {want_digest}
        if full_sidecar_digest and gt is not None and name in gt_names:
            gt_values = gt.column(name).to_pylist()
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
    ext_canon = {n: _canon_col(extracted.column(n).to_pylist(), sql_types.get(n, "")) for n in ext_names}
    gt_canon = {n: _canon_col(gt.column(n).to_pylist(), sql_types.get(n, "")) for n in gt.schema.names}

    # Map canonical key tuple -> decoded row index (first occurrence).
    ext_rows = extracted.num_rows
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
    """Verify every table in a manifest that has a decoded Arrow table in hand."""
    manifest = load_manifest(cells_dir)
    out: dict[str, TableVerifyResult] = {}
    for entry in manifest.get("tables", []):
        fqn = entry["fqn"]
        ext = extracted_tables.get(fqn)
        if ext is None:
            r = TableVerifyResult(fqn=fqn, mode=entry.get("mode", "full"))
            r.error = "table absent from decode output"
            out[fqn] = r
            continue
        out[fqn] = verify_table(ext, cells_dir, entry)
    return out
