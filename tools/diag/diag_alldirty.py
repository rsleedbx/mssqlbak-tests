"""Diagnose why alldirty has 6 remaining rows after logtail filtering."""
from __future__ import annotations
import struct
import pathlib
from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.rows import read_table_rows
from mssqlbak.logtail import logtail_from_bak

REPO = pathlib.Path(__file__).resolve().parent.parent
BAK = REPO / "tests/fixtures_2022/dirtycoverage_alldirty.bak"


def main() -> None:
    store = PageStore.from_bak(BAK)
    schema = recover_schema(store)
    table = schema.tables[0]
    print(f"table: {table.name}  obj_id={table.object_id}")

    logtail = logtail_from_bak(BAK)
    print(f"dirty_slots ({len(logtail.dirty_slots)}):", sorted(logtail.dirty_slots))

    rows_raw = list(read_table_rows(store, table))
    print(f"rows without filter: {len(rows_raw)}")

    rows_filtered = list(read_table_rows(store, table, dirty_slots=logtail.dirty_slots))
    print(f"rows with filter: {len(rows_filtered)}")

    # Find the data pages for this table
    p = store.page(344)
    raw = store.page_raw(344)
    sc = p.header.slot_cnt
    print(f"\npage 344: slot_cnt={sc}")
    for s in range(sc):
        off_ptr = len(raw) - 2 * (s + 1)
        slot_off = struct.unpack_from("<H", raw, off_ptr)[0]
        if 0 < slot_off < len(raw) - 4:
            status = raw[slot_off]
            ghost = bool(status & 0x10)
            is_dirty = (1, 344, s) in logtail.dirty_slots
            print(f"  slot {s:2d}: off={slot_off} status={status:#04x} ghost={ghost} dirty={is_dirty}")


if __name__ == "__main__":
    main()
