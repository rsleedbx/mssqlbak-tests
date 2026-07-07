#!/usr/bin/env python3
"""Decode SalesOrderHeader_inmem via the seq gate and diff each column against
the .cells ground truth, printing the specific mismatching rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pyarrow.parquet as pq

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.xtp import (  # noqa: E402
    scan_cfp_log_records,
    _seq_complete_rows,
)
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402

BAK = Path("tests/fixtures_realworld/AdventureWorks2016_EXT.bak")
CELLS = Path("tests/fixtures_realworld/AdventureWorks2016_EXT.bak.cells/"
             "Sales.SalesOrderHeader_inmem.parquet")


def main() -> None:
    store = PageStore.from_bak(str(BAK))
    schema = recover_schema(store)
    soh = next(t for t in schema.tables if t.name == "SalesOrderHeader_inmem")

    lb_map = scan_cfp_log_records(BAK.read_bytes())
    rows = None
    for lb, recs in sorted(lb_map.items()):
        r = _seq_complete_rows(recs, soh)
        if r is not None:
            rows = r
            print(f"landed via LB=0x{lb:02x}, {len(r)} rows")
            break
    if rows is None:
        print("SOH did not land")
        return

    dec = {row["SalesOrderID"]: row for row in rows}
    gt = pq.read_table(CELLS).to_pydict()
    ids = gt["SalesOrderID"]
    cols = [c for c in gt if c != "SalesOrderID"]
    n_mismatch = {c: 0 for c in cols}
    for i, sid_str in enumerate(ids):
        sid = int(sid_str)
        drow = dec.get(sid)
        if drow is None:
            print(f"  MISSING decoded row for SalesOrderID={sid}")
            continue
        for c in cols:
            exp = gt[c][i]
            got = drow.get(c)
            if isinstance(got, bool):
                gs = "1" if got else "0"
            else:
                gs = None if got is None else str(got)
            # normalise datetime str: ground truth uses ISO 'T'
            if gs is not None and " " in gs and "T" not in gs:
                gs = gs.replace(" ", "T")
            if gs != exp:
                if n_mismatch[c] < 6:
                    print(f"  SID={sid} {c}: exp={exp!r} got={gs!r} raw_got={got!r}")
                n_mismatch[c] += 1
    print("mismatch counts:", {c: n for c, n in n_mismatch.items() if n})


if __name__ == "__main__":
    main()
