#!/usr/bin/env python3
"""Dump the EXACT leaf chain read_table_rows follows for the included delta
rowset (…054400), per page: m_type, slot_cnt, live/ghost, id range of live rows,
and page LSN.  Pinpoints whether the 834 surplus deleted rows arrive via stale /
superseded pages reachable through the captured next_page chain.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import find_table, fixture, open_store  # noqa: E402

from mssqlbak.catalog import ALLOC_IN_ROW, Table as CatTable, _bootstrap as cat_bootstrap  # noqa: E402
from mssqlbak.recordtype import fixedvar_emittable, fixedvar_record_type  # noqa: E402
from mssqlbak.records import decode_record  # noqa: E402
from mssqlbak.rows import _data_pages, _record_columns  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"
TABLE = "dirty_cci"


def main() -> None:
    store, schema, boot, _blobs = open_store(fixture(VERSION, NAME))
    tbl = find_table(schema, TABLE)
    assert tbl is not None
    cat_boot = cat_bootstrap(store)
    all_rowsets = cat_boot.obj_to_rowsets.get(tbl.object_id, [])

    target = None
    for _, rs_id in all_rowsets:
        if cat_boot.rowset_compression.get(rs_id, 0) == 0 and cat_boot.rowset_rcrows.get(rs_id, 0) == 2000:
            target = rs_id
            break
    assert target is not None, "included delta rowset (rcrows=2000) not found"
    aus = cat_boot.owner_to_allocs.get(target, [])
    in_row = next((a for a in aus if a.unit_type == ALLOC_IN_ROW), None)
    assert in_row is not None
    print(f"rowset={target} first_page={in_row.first_page} root_page={in_row.root_page} first_iam={in_row.first_iam}")

    delta_tbl = CatTable(
        name=f"__cs_delta_{target}",
        object_id=tbl.object_id,
        index_id=1 if in_row.root_page[0] else 0,
        compression=0,
        columns=tbl.columns,
        alloc_units=aus,
    )
    rec_cols = _record_columns(delta_tbl)

    def _id(raw: bytes) -> int | None:
        try:
            cell = decode_record(raw, rec_cols, {}).get("id")
        except Exception:
            return None
        return int.from_bytes(cell, "little") if isinstance(cell, bytes) else None

    tot_live = 0
    tot_ghost = 0
    band_del = 0  # 5001-6000
    band_surv = 0  # 6001-7000
    n_pages = 0
    for pid, fid in _data_pages(store, delta_tbl):
        page = store.page(pid, fid)
        live = ghost = 0
        ids: list[int] = []
        for slot in range(page.header.slot_cnt):
            try:
                raw = bytes(page.record(slot))
            except Exception:
                continue
            if fixedvar_emittable(raw):
                live += 1
                i = _id(raw)
                if isinstance(i, int):
                    ids.append(i)
                    if 5001 <= i <= 6000:
                        band_del += 1
                    elif 6001 <= i <= 7000:
                        band_surv += 1
            elif fixedvar_record_type(raw) in (5, 6, 7):
                ghost += 1
        tot_live += live
        tot_ghost += ghost
        n_pages += 1
        lsn = page.header.lsn
        idrange = f"{min(ids)}..{max(ids)}" if ids else "-"
        print(
            f"  pg {pid:>5} m={page.header.m_type} slots={page.header.slot_cnt:>3} "
            f"live={live:>3} ghost={ghost:>3} ids[{idrange}] lsn={lsn}"
        )
    print(
        f"\nTOTAL pages={n_pages} live={tot_live} ghost={tot_ghost} "
        f"| live band 5001-6000(DELETED)={band_del} 6001-7000(survive)={band_surv}"
    )


if __name__ == "__main__":
    main()
