"""Diagnose page 344 slots in dirtycoverage_alldirty."""
from __future__ import annotations
import pathlib
from mssqlbak.pages import PageStore

REPO = pathlib.Path(__file__).resolve().parent.parent
BAK = REPO / "tests/fixtures_2022/dirtycoverage_alldirty.bak"


def main() -> None:
    store = PageStore.from_bak(BAK)
    p = store.page(344)
    sc = p.header.slot_cnt
    sa = p.slot_array()
    print(f"page 344: slot_cnt={sc} m_type={p.header.m_type} obj_id={p.header.obj_id}")
    print()

    for s in range(sc):
        try:
            rec = p.record(s)
        except Exception as e:
            print(f"  slot {s:2d}: ERROR {e}")
            continue
        if not rec:
            print(f"  slot {s:2d}: empty")
            continue
        sb = rec[0]
        # In SQL Server FixedVar records:
        # bits 1-3 of status byte = record type:
        #   0 = primary data
        #   1 = forwarded record
        #   2 = forwarding stub
        #   3 = index
        #   4 = blob/text
        #   5 = ghost index
        #   6 = ghost data
        rec_type = (sb >> 1) & 0x07
        ghost = rec_type in (5, 6)
        slot_off = sa[s] if s < len(sa) else 0
        rb = rec[:12].hex()
        print(f"  slot {s:2d}: off={slot_off:#06x} status={sb:#04x} rec_type={rec_type} ghost={ghost}  raw={rb}")


if __name__ == "__main__":
    main()
