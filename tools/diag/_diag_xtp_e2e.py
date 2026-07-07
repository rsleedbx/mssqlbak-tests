#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""End-to-end read_xtp_rows check for AdventureWorks2016_EXT: which XTP tables land
and are they byte-exact vs .cells."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.xtp import read_xtp_rows

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    xtp_tables = [t for t in schema.tables if t.is_memory_optimized]
    raw = FIXTURE.read_bytes()
    rows = read_xtp_rows(raw, xtp_tables, is_compressed=True)
    landed = {k: v for k, v in rows.items() if v}
    print("landed XTP tables (non-empty):")
    for name, rws in sorted(landed.items()):
        print(f"  {name}: {len(rws)} rows")

    # byte-exact spot check DemoSalesOrderHeaderSeed
    tgt = "DemoSalesOrderHeaderSeed"
    if tgt in landed:
        cells = CELLS_DIR / "Demo.DemoSalesOrderHeaderSeed.parquet"
        gt = {int(r["LocalID"]): r for r in pq.read_table(cells).to_pylist()}
        by_id = {r["LocalID"]: r for r in landed[tgt]}
        mism = []
        for lid, grow in gt.items():
            drow = by_id.get(lid)
            if drow is None:
                mism.append((lid, "MISSING"))
                continue
            for col in ("CustomerID", "SalesPersonID", "BillToAddressID",
                        "ShipToAddressID", "ShipMethodID", "DueDate"):
                gv = grow[col]
                dv = drow.get(col)
                dv_s = dv.isoformat() if isinstance(dv, datetime.datetime) else str(dv)
                if gv is None:
                    if dv is not None:
                        mism.append((lid, col, dv_s, "None"))
                        break
                    continue
                if dv_s != str(gv):
                    mism.append((lid, col, dv_s, gv))
                    break
            if len(mism) > 8:
                break
        print(f"\n{tgt}: GT={len(gt)} landed={len(by_id)} mismatches={len(mism)} "
              f"{'BYTE-EXACT COMPLETE' if not mism and len(by_id)==len(gt) else mism[:4]}")


if __name__ == "__main__":
    main()
