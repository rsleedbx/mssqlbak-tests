#!/usr/bin/env python3
"""Enumerate the uncompressed (cmprlevel=0) delta-store pages for dirty_cci and
tally which id-band each page holds (compressed 1-5000 / deleted 5001-6000 /
survived 6001-7000).  Phase 0b: locate where the deleted rows physically live and
which pages are candidates for wholesale deallocation.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import find_table, fixture, open_store  # noqa: E402

from mssqlbak.columnstore.storage.segment_meta import _walk_pages  # noqa: E402
from mssqlbak.recordtype import fixedvar_emittable, fixedvar_record_type  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"
TABLE = "dirty_cci"


def main() -> None:
    store, schema, boot, _blobs = open_store(fixture(VERSION, NAME))
    tbl = find_table(schema, TABLE)
    assert tbl is not None
    oid = tbl.object_id

    for idminor, rs_id in boot.obj_to_rowsets.get(oid, []):
        cmpr = boot.rowset_compression.get(rs_id, 0)
        if cmpr != 0:
            continue
        print(f"\n==== cmprlevel=0 rowset rs_id={rs_id} ====")
        for au in boot.owner_to_allocs.get(rs_id, []):
            fp = au.first_page[0]
            if not fp:
                continue
            print(f"  alloc unit_type={au.unit_type} first_page={fp}")
            seen = 0
            for page in _walk_pages(store, fp):
                pid = page.header.page_id
                # Reliable signal: classify each slot's record with the real
                # FixedVar classifier (live PRIMARY vs ghost variants 5/6/7).
                live = 0
                ghost = 0
                orig = 0
                for slot in range(page.header.slot_cnt):
                    try:
                        raw = bytes(page.record(slot))
                    except Exception:
                        continue
                    if len(raw) < 2:
                        continue
                    if b"original_" in raw:
                        orig += 1
                    if fixedvar_emittable(raw):
                        live += 1
                    elif fixedvar_record_type(raw) in (5, 6, 7):
                        ghost += 1
                print(
                    f"    page {pid}: slots={page.header.slot_cnt} "
                    f"original_rows={orig} live={live} ghost={ghost}"
                )
                seen += 1
                if seen >= 80:
                    print("    ... (capped at 80 pages)")
                    break


if __name__ == "__main__":
    main()
