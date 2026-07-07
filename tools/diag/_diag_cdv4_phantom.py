#!/usr/bin/env python3
"""Find the phantom deleted row(s) in committed_delete_v4 (2017) and report their
physical (file,page,slot) vs the committed_delete_slots suppression set.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.extract import _data_pages  # noqa: E402
from mssqlbak.logtail import logtail_from_bak  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.rows import read_table_rows  # noqa: E402

BAND = range(1, 1001)


def main() -> None:
    bak = _REPO / "tests" / "fixtures_2017" / "dirtycoverage_committed_delete_v4.bak"
    store = PageStore.from_bak(bak)
    lt = logtail_from_bak(bak)
    table = next(t for t in recover_schema(store).tables if t.name == "dirty_v4")

    rows = list(read_table_rows(
        store, table,
        dirty_slots=lt.dirty_slots,
        restore_slots=lt.restore_slots,
        before_images=lt.before_images,
        redo_rows=lt.redo_rows,
        committed_delete_slots=lt.committed_delete_slots,
        redo_patches=lt.redo_patches,
        restore_rows=lt.restore_rows,
        dirty_row_bytes=lt.dirty_row_bytes,
    ))
    ids = [r["id"] for r in rows if isinstance(r.get("id"), int)]
    phantom = sorted(i for i in ids if i in BAND)
    print(f"total rows={len(rows)} (expected 4000); phantom deleted ids still present={phantom}")

    # Map id -> physical (fid,pid,slot) by scanning data pages raw.
    loc: dict[int, tuple[int, int, int]] = {}
    from mssqlbak.recordtype import fixedvar_emittable
    for pid, fid in _data_pages(store, table):
        page = store.page(pid, fid)
        for slot in range(page.header.slot_cnt):
            raw = page.record(slot)
            if not fixedvar_emittable(raw):
                continue
            # id is the clustered key, first fixed column at offset 4 (INT)
            try:
                val = int.from_bytes(raw[4:8], "little", signed=True)
            except Exception:
                continue
            if val in BAND and val not in loc:
                loc[val] = (fid, pid, slot)

    cds = lt.committed_delete_slots
    for pid_ in phantom:
        triple = loc.get(pid_)
        supp = triple in cds if triple else None
        print(f"  phantom id={pid_}: physical={triple} in committed_delete_slots={supp}")
    if not phantom:
        print("NO PHANTOM — fixture already clean!")


if __name__ == "__main__":
    main()
