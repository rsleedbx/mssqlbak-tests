#!/usr/bin/env python3
"""Locate the CCI delete-bitmap rowset for dirty_cci and determine whether its
deletions live in the .bak log tail as INSERT records (bitmap-B-tree inserts).

Step 2 (empirical dump) of the decode-bug-workflow for the
dirtycoverage_cci_delete gap.
"""
from __future__ import annotations

import mmap as _mmap
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import find_table, fixture, open_store  # noqa: E402

from mssqlbak.columnstore.storage.segment_meta import (  # noqa: E402
    _cd_excess_be_int,
    _cd_records,
    _walk_pages,
)
from mssqlbak.logtail import (  # noqa: E402
    LOP_DELETE_ROWS,
    LOP_INSERT_ROWS,
    find_log_range,
    iter_log_records,
)

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"
TABLE = "dirty_cci"
ALLOC_IN_ROW = 1


def main() -> None:
    bak = fixture(VERSION, NAME)
    store, schema, boot, _blobs = open_store(bak)
    tbl = find_table(schema, TABLE)
    assert tbl is not None, f"table {TABLE} not found"
    oid = tbl.object_id
    print(f"== {TABLE} object_id={oid}")

    rowsets = boot.obj_to_rowsets.get(oid, [])
    print("-- rowsets for object (idminor, rowset_id, cmprlevel) --")
    bitmap_rs: list[int] = []
    for idminor, rs_id in rowsets:
        cmpr = boot.rowset_compression.get(rs_id, 0)
        print(f"   idminor={idminor} rs_id={rs_id} cmprlevel={cmpr}")
        if cmpr == 2:
            bitmap_rs.append(rs_id)

    bitmap_pages: set[int] = set()
    for rs_id in bitmap_rs:
        for au in boot.owner_to_allocs.get(rs_id, []):
            if au.unit_type != ALLOC_IN_ROW:
                continue
            fp_id = au.first_page[0]
            if not fp_id:
                continue
            pages = [p.header.page_id for p in _walk_pages(store, fp_id)]
            bitmap_pages.update(pages)
            print(f"   bitmap rs_id={rs_id} first_page={fp_id} pages={pages}")
            # Count persisted CD records (already-hardened bitmap entries).
            persisted = list(_cd_records(store, fp_id))
            decoded = []
            for cols in persisted:
                if len(cols) >= 2 and isinstance(cols[0], bytes) and isinstance(cols[1], bytes):
                    decoded.append((_cd_excess_be_int(cols[0]), _cd_excess_be_int(cols[1])))
            print(f"   persisted bitmap CD records: {len(persisted)} decoded={decoded[:8]}")

    print(f"\n-- bitmap pages: {sorted(bitmap_pages)}")

    # Scan the log: which pages do INSERT/DELETE records target, and do any hit
    # the bitmap pages?
    with open(bak, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            start, end = find_log_range(mm)
            ins_pages: Counter[int] = Counter()
            del_pages: Counter[int] = Counter()
            bitmap_hits = 0
            for rec in iter_log_records(mm, start, end):
                if rec.page_id is None:
                    continue
                if rec.lop == LOP_INSERT_ROWS:
                    ins_pages[rec.page_id] += 1
                    if rec.page_id in bitmap_pages:
                        bitmap_hits += 1
                elif rec.lop == LOP_DELETE_ROWS:
                    del_pages[rec.page_id] += 1
            print("\n-- log (find_log_range window, LCX=XACT scanner) --")
            print(f"   INSERT target pages: {ins_pages.most_common()}")
            print(f"   DELETE target pages: {del_pages.most_common()}")
            print(f"   INSERT records hitting bitmap pages: {bitmap_hits}")
        finally:
            mm.close()


if __name__ == "__main__":
    main()
