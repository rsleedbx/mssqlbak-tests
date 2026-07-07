#!/usr/bin/env python3
"""Replicate delta.py's rowset-selection + read_table_rows (NO log tail) and tally
emitted rows by id-band, to pinpoint why mssqlbak over-emits deleted delta rows.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import find_table, fixture, open_store  # noqa: E402

from mssqlbak.catalog import ALLOC_IN_ROW, Table as CatTable, _bootstrap as cat_bootstrap  # noqa: E402
from mssqlbak.columnstore.storage.segment_meta import _read_column_segments  # noqa: E402
from mssqlbak.rows import read_table_rows  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"
TABLE = "dirty_cci"


def _band(i: int | None) -> str:
    if i is None:
        return "id=None"
    if i <= 5000:
        return "1-5000"
    if i <= 6000:
        return "5001-6000(DELETED)"
    if i <= 7000:
        return "6001-7000"
    return f"other({i})"


def main() -> None:
    store, schema, boot, _blobs = open_store(fixture(VERSION, NAME))
    tbl = find_table(schema, TABLE)
    assert tbl is not None
    cat_boot = cat_bootstrap(store)
    all_rowsets = cat_boot.obj_to_rowsets.get(tbl.object_id, [])

    compressed_rcrows: set[int] = set()
    cs_rowset_ids: set[int] = set()
    for _, rs_id in all_rowsets:
        if cat_boot.rowset_compression.get(rs_id, 0) == 3:
            rc = cat_boot.rowset_rcrows.get(rs_id, 0)
            if rc > 0:
                compressed_rcrows.add(rc)
                cs_rowset_ids.add(rs_id)
    if cs_rowset_ids:
        for seg in _read_column_segments(store, boot, cs_rowset_ids):
            if seg.n_rows > 0:
                compressed_rcrows.add(seg.n_rows)
    print(f"compressed_rcrows tombstone set: {sorted(compressed_rcrows)}")

    for _, rs_id in all_rowsets:
        cmpr = cat_boot.rowset_compression.get(rs_id, 0)
        rc = cat_boot.rowset_rcrows.get(rs_id, 0)
        if cmpr != 0:
            print(f"  rs_id={rs_id} cmpr={cmpr} rcrows={rc} -> (not delta)")
            continue
        skip = ""
        if rc <= 0:
            skip = "empty"
        elif rc in compressed_rcrows:
            skip = "tombstone(rc matches compressed)"
        print(f"  rs_id={rs_id} cmpr=0 rcrows={rc} -> {'SKIP: ' + skip if skip else 'INCLUDED'}")
        if skip:
            continue
        aus = cat_boot.owner_to_allocs.get(rs_id, [])
        in_row = next((a for a in aus if a.unit_type == ALLOC_IN_ROW), None)
        if in_row is None or not in_row.first_page[0]:
            print("      (no in-row alloc)")
            continue
        delta_tbl = CatTable(
            name=f"__cs_delta_{rs_id}",
            object_id=tbl.object_id,
            index_id=1 if in_row.root_page[0] else 0,
            compression=0,
            columns=tbl.columns,
            alloc_units=aus,
        )
        bands: Counter[str] = Counter()
        for row in read_table_rows(store, delta_tbl):
            bands[_band(row.get("id"))] += 1
        print(f"      emitted {sum(bands.values())} rows: {dict(bands)}")


if __name__ == "__main__":
    main()
