"""Offline refresh of full-mode column digests in .cells/_manifest.json files.

Manifests become stale whenever the canonical form of values changes — e.g. when
``canon()`` rules are extended (bit alias resolution, xml normalisation, WKT
coordinate rounding, temporal format changes).  The stored ``digest`` and
``ordered_digest`` fields are then wrong, causing ``level="digest"`` verification
failures even though the decoder itself is correct.

This tool recomputes every **full-mode** column digest from existing GT parquet
files using the **exact same code path** as ``tools.value_verify.verify_table``
so the stored fingerprints are guaranteed consistent with the verifier:

  * ``digest``         = ``_arrow_column_digest(_canon_to_arrow(col, eff_type))``
  * ``ordered_digest`` = ``_arrow_ordered_column_digest(pc.take(..., sort_idx))``
                         where ``sort_idx`` is built from ``_canon_to_arrow``'d key arrays.
  * ``eff_type``       = ``_effective_sql_type(col_meta)`` (honours ``base_sql_type``,
                         keeps ``(p,s)`` params for decimal).

Only mismatching values are written — already-correct columns are untouched.

**digest-only and sample tables are intentionally skipped.**  Their multiset
digests were computed at capture time over the *full* table from SQL Server.
The on-disk parquet is intentionally partial (``values_capped``), so recomputing
from it would produce a wrong digest.  These digests can only be refreshed by
re-running the cells capture against a live SQL Server instance.

Usage::

    .venv/bin/python -m tools.refresh_manifest_digests tests/fixtures_realworld
    .venv/bin/python -m tools.refresh_manifest_digests tests/fixtures_realworld --dry-run
    .venv/bin/python -m tools.refresh_manifest_digests \\
        tests/fixtures_2017 tests/fixtures_2019 tests/fixtures_2022 \\
        tests/fixtures_2025 tests/fixtures_realworld
    .venv/bin/python -m tools.refresh_manifest_digests tests/fixtures_realworld \\
        --only AdventureWorks2008R2
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

log = logging.getLogger(__name__)

_MANIFEST_NAME = "_manifest.json"


def _refresh_manifest(
    manifest_path: Path,
    *,
    dry_run: bool,
    only: str | None,
) -> tuple[int, int, int]:
    """Refresh digests for one manifest.

    Returns ``(columns_checked, columns_updated, columns_skipped)``.
    Only ``mode="full"`` tables are processed.
    ``mode="sample"`` and ``mode="digest-only"`` tables are always skipped.
    """
    from tools.value_verify import (
        _arrow_column_digest,
        _arrow_ordered_column_digest,
        _canon_to_arrow,
        _effective_sql_type,
        _key_sort_indices,
    )

    cells_dir = manifest_path.parent
    bak_stem = cells_dir.name.removesuffix(".bak.cells")

    if only and only not in bak_stem:
        return 0, 0, 0

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tables = manifest.get("tables", [])

    updates: dict[tuple[str, str], dict[str, str]] = {}
    checked = updated = skipped = 0
    log_prefix = bak_stem

    for tbl in tables:
        fqn: str = tbl.get("fqn", "")
        mode: str = tbl.get("mode", "full")
        key_columns: list[str] = tbl.get("key_columns") or []
        columns: list[dict] = tbl.get("columns", [])

        # digest-only and sample digests cover the *full* table from SQL Server;
        # the on-disk parquet is intentionally partial (values_capped).  Never
        # recompute from the partial parquet — only a live-capture can refresh them.
        if mode in ("sample", "digest-only"):
            log.debug("%s %s: mode=%s — skip", log_prefix, fqn, mode)
            skipped += len(columns)
            continue

        parquet_path = cells_dir / f"{fqn}.parquet"
        if not parquet_path.exists():
            log.debug("%s %s: no parquet — skip", log_prefix, fqn)
            skipped += len(columns)
            continue

        try:
            gt = pq.read_table(parquet_path)
        except Exception as exc:
            log.warning("%s %s: cannot read parquet: %s", log_prefix, fqn, exc)
            skipped += len(columns)
            continue

        gt_names = set(gt.schema.names)
        sql_types = {c["name"]: _effective_sql_type(c) for c in columns}

        # Pre-build canonical key arrays for ordered_digest (done once per table).
        sort_idx = None
        if key_columns and all(k in gt_names for k in key_columns):
            try:
                key_arrs = [
                    _canon_to_arrow(gt.column(k), sql_types.get(k, ""))
                    for k in key_columns
                ]
                sort_idx = _key_sort_indices(key_arrs)
            except Exception as exc:
                log.warning(
                    "%s %s: key sort failed: %s — ordered_digest skipped",
                    log_prefix, fqn, exc,
                )

        for col in columns:
            col_name: str = col.get("name", "")
            stored_digest = col.get("digest")
            if not stored_digest:
                continue
            if col_name not in gt_names:
                log.debug("%s %s.%s: not in parquet — skip", log_prefix, fqn, col_name)
                skipped += 1
                continue

            checked += 1
            eff = sql_types.get(col_name, "")
            col_updates: dict[str, str] = {}

            try:
                canon_arr = _canon_to_arrow(gt.column(col_name), eff)
                new_digest = _arrow_column_digest(canon_arr)
            except Exception as exc:
                log.warning(
                    "%s %s.%s: digest compute failed: %s", log_prefix, fqn, col_name, exc
                )
                skipped += 1
                continue

            if new_digest != stored_digest:
                col_updates["digest"] = new_digest
                log.info(
                    "%s %s.%s: digest %s → %s",
                    log_prefix, fqn, col_name,
                    stored_digest[:16], new_digest[:16],
                )

            # Recompute ordered_digest when it exists and sort is available.
            if sort_idx is not None and col_name not in key_columns and col.get("ordered_digest"):
                try:
                    reordered = pc.take(canon_arr, sort_idx)
                    new_ord = _arrow_ordered_column_digest(reordered)
                except Exception as exc:
                    log.warning(
                        "%s %s.%s: ordered_digest compute failed: %s",
                        log_prefix, fqn, col_name, exc,
                    )
                    new_ord = None
                if new_ord is not None:
                    old_ord = col.get("ordered_digest")
                    if new_ord != old_ord:
                        col_updates["ordered_digest"] = new_ord
                        log.info(
                            "%s %s.%s: ordered_digest updated",
                            log_prefix, fqn, col_name,
                        )

            if col_updates:
                updates[(fqn, col_name)] = col_updates
                updated += 1

    if not updates:
        return checked, 0, skipped

    # Atomic write.
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed_fields = 0
    for table in data.get("tables", []):
        fqn = table.get("fqn", "")
        for col in table.get("columns", []):
            key = (fqn, col.get("name", ""))
            new_vals = updates.get(key)
            if not new_vals:
                continue
            for field, new_val in new_vals.items():
                if col.get(field) != new_val:
                    col[field] = new_val
                    changed_fields += 1

    tag = "DRY-RUN" if dry_run else "UPDATED"
    col_list = ", ".join(f"{fqn}.{cn}" for fqn, cn in sorted(updates))
    print(f"[{log_prefix}] {tag}  {changed_fields} field(s) in: {col_list}")

    if not dry_run:
        tmp_path = manifest_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, manifest_path)

    return checked, updated, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging.",
    )
    parser.add_argument(
        "--only",
        metavar="BAK_STEM",
        default=None,
        help=(
            "Only refresh manifests whose .bak stem contains this string "
            "(e.g. --only AdventureWorks2008R2)."
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
                checked, upd, skipped = _refresh_manifest(
                    mp, dry_run=args.dry_run, only=args.only
                )
                if checked > 0 or upd > 0:
                    total_manifests += 1
                    total_checked += checked
                    total_updated += upd
                    total_skipped += skipped
                    if upd == 0:
                        bak_stem = mp.parent.name.removesuffix(".bak.cells")
                        print(f"[{bak_stem}] OK  (all {checked} full-mode column(s) already correct)")
            except Exception:
                log.exception("Failed to refresh %s", mp)
                any_error = True

    print(
        f"\nTotal: {total_manifests} manifests, "
        f"{total_checked} full-mode columns checked, "
        f"{total_updated} updated, "
        f"{total_skipped} skipped (sample/digest-only/no-parquet)"
    )
    if args.dry_run:
        print("(dry-run: no files were modified)")

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
