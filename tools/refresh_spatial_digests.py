"""Offline refresh of geometry/geography column digests in .cells/_manifest.json files.

Manifests become stale when the canonical form of spatial values changes.  The
known cause:

  _canon_wkt_text addition (commit after cells_capture was first run)
    cell_canon.canon() now passes geometry/geography values through
    _canon_wkt_text() which rounds WKT coordinate numbers to 15 significant
    digits.  Manifests captured before this was wired into canon() store the
    raw full-precision AsTextZM() text (up to 17 sig digits), so their stored
    digests never match the extractor's .15g-rounded digests.

This script recomputes only the geometry/geography column digests from
existing data — no live SQL Server required — and rewrites the affected
manifests.

Three cases are handled per spatial column:

  mode=full, parquet present
    The parquet already contains the SQL Server authoritative WKT strings.
    Passing those strings through canon(v, base_type) at the current
    _canon_wkt_text rules produces the same digest as running the extractor.
    For tables with key_columns, also recomputes ordered_digest (key-sorted
    column order).

  mode=digest-only, parquet absent but .bak present
    Extract via extract_bak (InMemorySink) and canonicalize from the decoded
    Arrow column.  Only digest is recomputed; no ordered_digest for
    digest-only tables.

  mode=sample, or no parquet and no .bak
    Warn and skip.  Sample tables' ordered_digest is not maintained (partial
    rows would not match the full-table digest the extractor produces).

Usage:
    .venv/bin/python tools/refresh_spatial_digests.py tests/fixtures_realworld
    .venv/bin/python tools/refresh_spatial_digests.py tests/fixtures_realworld --dry-run
    .venv/bin/python tools/refresh_spatial_digests.py tests/fixtures_realworld --only ContosoRetailDW
    .venv/bin/python tools/refresh_spatial_digests.py \\
        tests/fixtures_2017 tests/fixtures_2019 tests/fixtures_2022 tests/fixtures_2025 \\
        tests/fixtures_realworld
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

log = logging.getLogger(__name__)

_SPATIAL_TYPES = frozenset({"geometry", "geography"})
_MANIFEST_NAME = "_manifest.json"


def _base_sql_type(col: dict) -> str:
    t = (col.get("base_sql_type") or col.get("sql_type") or "").strip().lower()
    paren = t.find("(")
    return t[:paren].strip() if paren != -1 else t


def _recompute_digest_from_parquet(
    parquet_path: Path,
    col_name: str,
    base_type: str,
) -> str:
    from tools.cell_canon import canon, column_digest

    tbl = pq.read_table(parquet_path, columns=[col_name])
    raw_vals = tbl.column(col_name).to_pylist()
    canon_vals = [canon(v, base_type) for v in raw_vals]
    return column_digest(canon_vals)


def _recompute_ordered_digest_from_parquet(
    parquet_path: Path,
    col_name: str,
    base_type: str,
    key_columns: list[str],
) -> str | None:
    """Recompute ordered_digest for col_name, key-sorted by key_columns.

    Returns None when any key column is missing from the parquet.
    """
    from tools.cell_canon import canon, column_ordered_digest
    from tools.value_verify import _key_sort_indices

    needed = list(dict.fromkeys(key_columns + [col_name]))
    try:
        tbl = pq.read_table(parquet_path, columns=needed)
    except Exception as exc:
        log.warning("Cannot read %s columns %s: %s", parquet_path.name, needed, exc)
        return None

    missing = [k for k in key_columns if k not in tbl.schema.names]
    if missing:
        log.warning("Key columns %s missing from %s — skipping ordered_digest", missing, parquet_path.name)
        return None

    key_arrs: list[pa.Array] = []
    for k in key_columns:
        arr = tbl.column(k)
        if hasattr(arr, "chunks"):
            arr = arr.combine_chunks()
        key_arrs.append(arr)

    sort_idx = _key_sort_indices(key_arrs)

    arr = tbl.column(col_name)
    if hasattr(arr, "chunks"):
        arr = arr.combine_chunks()
    reordered = pc.take(arr, sort_idx)
    raw_vals = reordered.to_pylist()
    canon_vals = [canon(v, base_type) for v in raw_vals]
    return column_ordered_digest(canon_vals)


def _recompute_digest_from_bak(bak_path: Path, fqn: str, col_name: str, base_type: str) -> str:
    """Recompute digest by extracting the .bak (for digest-only tables without parquet)."""
    from mssqlbak.extract import extract_bak
    from mssqlbak.sink import InMemorySink
    from tools.cell_canon import canon, column_digest

    sink = InMemorySink()
    extract_bak(bak_path, sink)
    tbl = sink.to_arrow_table(fqn)
    if tbl is None:
        raise ValueError(f"Table {fqn} not found in extracted .bak")
    vals = tbl.column(col_name).to_pylist()
    canon_vals = [canon(v, base_type) for v in vals]
    return column_digest(canon_vals)


def _update_manifest(
    manifest_path: Path,
    updates: dict[tuple[str, str], dict[str, str]],
    *,
    dry_run: bool,
) -> int:
    """Apply digest updates to a manifest.

    updates: {(fqn, col_name): {"digest": new, "ordered_digest": new (optional)}}
    Returns number of fields changed.
    """
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed = 0

    for table in data.get("tables", []):
        fqn = table.get("fqn", "")
        for col in table.get("columns", []):
            col_name = col.get("name", "")
            key = (fqn, col_name)
            if key not in updates:
                continue
            new_vals = updates[key]
            for field, new_val in new_vals.items():
                old_val = col.get(field)
                if old_val != new_val:
                    col[field] = new_val
                    changed += 1

    if changed and not dry_run:
        tmp_path = manifest_path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp_path, manifest_path)

    return changed


def _refresh_manifest(
    manifest_path: Path,
    *,
    dry_run: bool,
    only: str | None,
) -> tuple[int, int, int]:
    """Refresh spatial digests for one manifest.

    Returns (columns_checked, columns_updated, columns_skipped).
    """
    cells_dir = manifest_path.parent
    bak_stem = cells_dir.name.removesuffix(".bak.cells")
    fixture_dir = cells_dir.parent

    if only and only not in bak_stem:
        return 0, 0, 0

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tables = manifest.get("tables", [])

    updates: dict[tuple[str, str], dict[str, str]] = {}
    checked = updated = skipped = 0
    log_prefix = f"{bak_stem}"

    for tbl in tables:
        fqn: str = tbl.get("fqn", "")
        mode: str = tbl.get("mode", "full")
        key_columns: list[str] = tbl.get("key_columns") or []
        columns: list[dict] = tbl.get("columns", [])

        spatial_cols = [
            (col, _base_sql_type(col))
            for col in columns
            if _base_sql_type(col) in _SPATIAL_TYPES
        ]
        if not spatial_cols:
            continue

        parquet_path = cells_dir / f"{fqn}.parquet"
        bak_candidates = sorted(fixture_dir.glob(f"{bak_stem}.bak"))
        bak_path = bak_candidates[0] if bak_candidates else None

        for col, base_type in spatial_cols:
            col_name: str = col.get("name", "")
            checked += 1
            col_updates: dict[str, str] = {}

            if mode == "sample":
                log.debug("%s %s.%s: sample mode — skip", log_prefix, fqn, col_name)
                skipped += 1
                continue

            if parquet_path.exists():
                try:
                    new_digest = _recompute_digest_from_parquet(parquet_path, col_name, base_type)
                except Exception as exc:
                    log.warning("%s %s.%s: parquet digest failed: %s", log_prefix, fqn, col_name, exc)
                    skipped += 1
                    continue

                old_digest = col.get("digest")
                if old_digest != new_digest:
                    col_updates["digest"] = new_digest
                    log.info(
                        "%s %s.%s: digest %s -> %s",
                        log_prefix, fqn, col_name,
                        (old_digest or "")[:16], new_digest[:16],
                    )

                # Recompute ordered_digest for full-mode tables with key columns.
                # digest-only tables have no ordered_digest by convention.
                if mode == "full" and key_columns and col.get("ordered_digest") is not None:
                    try:
                        new_ord = _recompute_ordered_digest_from_parquet(
                            parquet_path, col_name, base_type, key_columns
                        )
                    except Exception as exc:
                        log.warning(
                            "%s %s.%s: ordered_digest failed: %s", log_prefix, fqn, col_name, exc
                        )
                        new_ord = None
                    if new_ord is not None:
                        old_ord = col.get("ordered_digest")
                        if old_ord != new_ord:
                            col_updates["ordered_digest"] = new_ord
                            log.info(
                                "%s %s.%s: ordered_digest updated",
                                log_prefix, fqn, col_name,
                            )

            elif mode == "digest-only" and bak_path is not None:
                log.info("%s %s.%s: no parquet, extracting from .bak …", log_prefix, fqn, col_name)
                try:
                    new_digest = _recompute_digest_from_bak(bak_path, fqn, col_name, base_type)
                except Exception as exc:
                    log.warning(
                        "%s %s.%s: bak extract failed: %s", log_prefix, fqn, col_name, exc
                    )
                    skipped += 1
                    continue
                old_digest = col.get("digest")
                if old_digest != new_digest:
                    col_updates["digest"] = new_digest
                    log.info(
                        "%s %s.%s: digest (bak) %s -> %s",
                        log_prefix, fqn, col_name,
                        (old_digest or "")[:16], new_digest[:16],
                    )

            else:
                reason = "no parquet, no .bak" if bak_path is None else "no parquet (digest-only, no bak fallback)"
                log.warning("%s %s.%s: skip — %s", log_prefix, fqn, col_name, reason)
                skipped += 1
                continue

            if col_updates:
                updates[(fqn, col_name)] = col_updates
                updated += 1
            else:
                log.debug("%s %s.%s: already correct", log_prefix, fqn, col_name)

    if not updates:
        return checked, 0, skipped

    n_changed = _update_manifest(manifest_path, updates, dry_run=dry_run)
    tag = "DRY-RUN" if dry_run else "UPDATED"
    col_list = ", ".join(f"{fqn}.{cn}" for fqn, cn in sorted(updates))
    print(f"[{log_prefix}] {tag}  {n_changed} field(s) in: {col_list}")

    return checked, updated, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "fixture_dirs",
        nargs="+",
        metavar="FIXTURE_DIR",
        help="Fixture directories to scan for .cells/_manifest.json files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing any files.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging.",
    )
    parser.add_argument(
        "--only",
        metavar="BAK_STEM",
        default=None,
        help=(
            "Only refresh manifests whose .bak stem contains this string "
            "(e.g. --only ContosoRetailDW). Useful for targeted reruns."
        ),
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    total_checked = total_updated = total_skipped = total_manifests = 0
    any_error = False

    for raw in args.fixture_dirs:
        d = Path(raw)
        if not d.is_dir():
            log.error("Not a directory: %s", d)
            any_error = True
            continue

        manifests = sorted(d.rglob(_MANIFEST_NAME))
        if not manifests:
            log.warning("No %s files found under %s", _MANIFEST_NAME, d)
            continue

        for mp in manifests:
            try:
                checked, updated, skipped = _refresh_manifest(
                    mp, dry_run=args.dry_run, only=args.only
                )
                if checked > 0:
                    total_manifests += 1
                    total_checked += checked
                    total_updated += updated
                    total_skipped += skipped
                    if updated == 0 and skipped == 0:
                        bak_stem = mp.parent.name.removesuffix(".bak.cells")
                        print(f"[{bak_stem}] OK  (all {checked} spatial column(s) already correct)")
            except Exception:
                log.exception("Failed to refresh %s", mp)
                any_error = True

    print(
        f"\nTotal: {total_manifests} manifests with spatial columns, "
        f"{total_checked} columns checked, "
        f"{total_updated} updated, "
        f"{total_skipped} skipped"
    )
    if args.dry_run:
        print("(dry-run: no files were modified)")

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
