"""Offline parquet-only backfill: populate ``ordered_digest`` in ``.cells/_manifest.json``.

Usage
-----
    python -m tools.backfill_ordered_digest <fixtures_dir> [<fixtures_dir> ...]

For every ``.cells/_manifest.json`` found under the given directories:
- Skip tables whose ``mode`` is ``"digest-only"`` or that have no ``key_columns``.
- Read the corresponding ``<fqn>.parquet`` (canonical string columns already
  stored there by cells_capture).
- Compute ``_key_sort_indices`` over the key columns then
  ``_arrow_ordered_column_digest`` for each non-key column.
- Write ``ordered_digest`` into each ``columns[]`` entry in-place.
- Rewrite the manifest atomically (``_manifest.json.tmp`` → rename).

Idempotent: running again recomputes and overwrites the field; if the digest
did not change nothing observable is different.

No SQL Server required — all work is done from the parquet files that
``cells_capture`` already wrote.
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

# value_verify helpers — import after sys.path setup (handled by __main__ entry)
from tools.value_verify import _arrow_ordered_column_digest, _key_sort_indices

log = logging.getLogger(__name__)

MANIFEST_NAME = "_manifest.json"


def _backfill_manifest(manifest_path: Path) -> tuple[int, int]:
    """Backfill ``ordered_digest`` for one manifest file.

    Returns (tables_updated, tables_skipped).
    """
    cells_dir = manifest_path.parent
    manifest: dict = json.loads(manifest_path.read_text(encoding="utf-8"))
    tables: list[dict] = manifest.get("tables", [])

    updated = 0
    skipped = 0

    for tbl in tables:
        mode: str = tbl.get("mode", "")
        key_columns: list[str] = tbl.get("key_columns") or []
        fqn: str = tbl.get("fqn", "")

        if mode in {"digest-only", "sample"} or not key_columns:
            # sample-mode tables have fewer parquet rows than the full table, so
            # an ordered_digest derived from the sample would never match the full
            # extract during verify.  Skip to avoid polluting the manifest.
            skipped += 1
            continue

        parquet_path = cells_dir / f"{fqn}.parquet"
        if not parquet_path.exists():
            log.warning("parquet missing for %s in %s — skipping", fqn, manifest_path)
            skipped += 1
            continue

        table: pa.Table = pq.read_table(parquet_path)
        col_names = table.schema.names

        # Resolve key arrays (must all be present in parquet).
        missing_keys = [k for k in key_columns if k not in col_names]
        if missing_keys:
            log.warning(
                "key columns %s missing from parquet for %s — skipping",
                missing_keys,
                fqn,
            )
            skipped += 1
            continue

        key_arrs: list[pa.Array] = []
        for k in key_columns:
            arr = table.column(k)
            if hasattr(arr, "chunks"):
                arr = arr.combine_chunks()
            key_arrs.append(arr)

        sort_idx = _key_sort_indices(key_arrs)

        # Compute ordered_digest for every non-key column that is in the parquet.
        name_to_ordered: dict[str, str] = {}
        key_set = set(key_columns)
        for col_name in col_names:
            if col_name in key_set:
                continue
            arr = table.column(col_name)
            reordered = pc.take(arr, sort_idx)
            name_to_ordered[col_name] = _arrow_ordered_column_digest(reordered)

        # Write results back into the manifest columns list.
        for col in tbl.get("columns", []):
            name = col.get("name", "")
            if name in name_to_ordered:
                col["ordered_digest"] = name_to_ordered[name]

        updated += 1

    # Atomic rewrite: write to .tmp then rename.
    tmp_path = manifest_path.with_suffix(".json.tmp")
    tmp_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, manifest_path)

    return updated, skipped


def backfill_dir(fixture_dir: Path) -> tuple[int, int, int]:
    """Walk a fixture directory and backfill all manifests found.

    Returns (manifests_processed, tables_updated, tables_skipped).
    """
    manifests = sorted(fixture_dir.rglob(MANIFEST_NAME))
    if not manifests:
        log.warning("No %s files found under %s", MANIFEST_NAME, fixture_dir)
        return 0, 0, 0

    total_updated = 0
    total_skipped = 0
    for mp in manifests:
        try:
            u, s = _backfill_manifest(mp)
            total_updated += u
            total_skipped += s
        except Exception:
            log.exception("Failed to backfill %s", mp)

    return len(manifests), total_updated, total_skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline parquet-only backfill of ordered_digest into .cells manifests."
    )
    parser.add_argument(
        "fixture_dirs",
        nargs="+",
        metavar="FIXTURE_DIR",
        help="One or more fixture directories to walk for .cells/_manifest.json files.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    total_manifests = total_updated = total_skipped = 0
    for raw in args.fixture_dirs:
        d = Path(raw)
        if not d.is_dir():
            log.error("Not a directory: %s", d)
            return 1
        m, u, s = backfill_dir(d)
        total_manifests += m
        total_updated += u
        total_skipped += s
        print(
            f"{d}: {m} manifests, {u} tables updated, {s} tables skipped (digest-only/keyless/missing parquet)"
        )

    print(
        f"\nTotal: {total_manifests} manifests, {total_updated} tables updated, {total_skipped} skipped"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
