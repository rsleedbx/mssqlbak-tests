#!/usr/bin/env python3
"""Compare expected vs extracted row counts for concurrent fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak.logtail import logtail_from_bak  # type: ignore[attr-defined]
from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]


def check(version: str) -> None:
    path = fixture(version, "dirtycoverage_concurrent.bak")
    lt = logtail_from_bak(path)
    store, schema, _boot, _blobs = open_store(path)
    tbl = find_table(schema, "dirty_test")
    assert tbl is not None

    # Without redo_rows
    rows_no_redo = list(read_table_rows(store, tbl, schema.obj_to_name))

    # With redo_rows (full logtail)
    rows_with_redo = list(read_table_rows(
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

    print(f"\n=== {version} concurrent ===")
    print(f"  no redo:   {len(rows_no_redo)} rows")
    print(f"  with redo: {len(rows_with_redo)} rows")
    print(f"  redo_rows keys: {list(lt.redo_rows.keys())}")

    if lt.redo_rows:
        ids_no = {r["id"] for r in rows_no_redo}
        ids_redo = {r["id"] for r in rows_with_redo}
        gained = ids_redo - ids_no
        lost = ids_no - ids_redo
        print(f"  gained by redo: {sorted(gained)}")
        if lost:
            print(f"  lost by redo:   {sorted(lost)}")


def main() -> None:
    check("2019")
    check("2025")


if __name__ == "__main__":
    main()
