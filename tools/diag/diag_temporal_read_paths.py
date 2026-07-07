#!/usr/bin/env python3
"""Compare 3 row-reading paths for 2017 dirtycoverage_temporal_update.bak."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak.logtail import logtail_from_bak  # type: ignore[attr-defined]
from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]

FIXTURE = fixture("2017", "dirtycoverage_temporal_update.bak")
TABLE = "temporal_test"


def main() -> None:
    store, schema, _boot, _blobs = open_store(FIXTURE)
    tbl = find_table(schema, TABLE)
    assert tbl is not None, f"Table {TABLE!r} not found"

    lt = logtail_from_bak(FIXTURE)

    # Path A: no logtail (same as CLI)
    rows_a = list(read_table_rows(store, tbl, schema.obj_to_name))
    print(f"A (no logtail):           {len(rows_a)} rows")

    # Path B: logtail via keyword args (same as _load_table_with_logtail in tests)
    rows_b = list(read_table_rows(
        store, tbl,
        dirty_slots=lt.dirty_slots,
        restore_slots=lt.restore_slots,
        before_images=lt.before_images,
        redo_rows=lt.redo_rows,
        committed_delete_slots=lt.committed_delete_slots,
        redo_patches=lt.redo_patches,
        restore_rows=lt.restore_rows,
        dirty_row_bytes=lt.dirty_row_bytes,
    ))
    print(f"B (logtail, no obj_name): {len(rows_b)} rows")
    ids_b = {r["id"] for r in rows_b}
    ids_a = {r["id"] for r in rows_a}
    missing = ids_a - ids_b
    if missing:
        print(f"  Missing in B vs A: {sorted(missing)}")

    # Path C: logtail WITH obj_to_name (add it as 3rd positional arg)
    rows_c = list(read_table_rows(
        store, tbl, schema.obj_to_name,
        dirty_slots=lt.dirty_slots,
        restore_slots=lt.restore_slots,
        before_images=lt.before_images,
        redo_rows=lt.redo_rows,
        committed_delete_slots=lt.committed_delete_slots,
        redo_patches=lt.redo_patches,
        restore_rows=lt.restore_rows,
        dirty_row_bytes=lt.dirty_row_bytes,
    ))
    print(f"C (logtail, with obj_name): {len(rows_c)} rows")
    ids_c = {r["id"] for r in rows_c}
    missing_c = ids_a - ids_c
    if missing_c:
        print(f"  Missing in C vs A: {sorted(missing_c)}")


if __name__ == "__main__":
    main()
