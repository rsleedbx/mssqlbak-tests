#!/usr/bin/env python3
"""Debug redo_rows injection for 2019 concurrent fixture."""
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

    print(f"redo_rows: {list(lt.redo_rows.keys())}")
    target_fid, target_pid, target_slot = 1, 312, 60

    # Check which pages are visited for dirty_test — _data_pages yields (pid, fid)
    pages_visited = []
    for pid, fid in _data_pages(store, tbl):  # type: ignore[arg-type]
        pages_visited.append((fid, pid))
        if fid == target_fid and pid == target_pid:
            page = store.page(pid, fid)  # type: ignore[attr-defined]
            print(f"\nFound page ({fid}, {pid}): slot_cnt={page.header.slot_cnt}")
            print(f"  slot {target_slot} exists? {target_slot < page.header.slot_cnt}")
            # Try injecting
            rb = lt.redo_rows[(target_fid, target_pid, target_slot)]
            print(f"  redo row bytes: {rb[:32].hex()}")
            page2 = page.with_injected_rows({target_slot: rb})
            print(f"  After inject: slot_cnt={page2.header.slot_cnt}")
            break
    else:
        print(f"\nPage ({target_fid}, {target_pid}) NOT FOUND in data pages!")
        print(f"Pages visited (fid, pid): {pages_visited}")


if __name__ == "__main__":
    main()
