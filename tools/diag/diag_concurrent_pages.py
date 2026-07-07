#!/usr/bin/env python3
"""Enumerate pages, slot counts, and ghost rows for 2019 concurrent dirty_test."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak.logtail import logtail_from_bak  # type: ignore[attr-defined]
from mssqlbak.rows import _data_pages  # type: ignore[attr-defined]

FIXTURE = fixture("2019", "dirtycoverage_concurrent.bak")


def main() -> None:
    lt = logtail_from_bak(FIXTURE)
    store, schema, _boot, _blobs = open_store(FIXTURE)
    tbl = find_table(schema, "dirty_test")
    assert tbl is not None

    print(f"redo_rows:  {list(lt.redo_rows.keys())}")
    print(f"dirty_slots: {list(lt.dirty_slots)[:10]}")
    print(f"dirty_row_bytes: {len(lt.dirty_row_bytes)}")

    total_slots = 0
    for pid, fid in _data_pages(store, tbl):  # type: ignore[arg-type]
        page = store.page(pid, fid)  # type: ignore[attr-defined]
        slot_cnt = page.header.slot_cnt
        # Count non-ghost (emittable) slots
        live = 0
        ghost = 0
        for sl in range(slot_cnt):
            raw = page.record(sl)
            # Check slot type: first byte bit 0x08 = GHOST_FORWARDED, bit 0x04 = GHOST_DATA
            status = raw[0] if raw else 0
            is_ghost = bool(status & 0x0C)
            if is_ghost:
                ghost += 1
            else:
                live += 1
        total_slots += live
        print(f"  pid={pid:4d} fid={fid}  slot_cnt={slot_cnt:4d}  live={live:4d}  ghost={ghost}")

    print(f"\nTotal live slots: {total_slots}")


if __name__ == "__main__":
    main()
