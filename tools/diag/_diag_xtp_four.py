#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Completeness census for the four still-skipped XTP tables.

Uses the PRODUCTION scanner (scan_cfp_log_records, now container-aware) to get
records per LB, maps each of the four tables to its LB by decode-overlap with
ground truth, then reports distinct-key coverage vs .cells: complete-but-
unprovable (all GT keys present, only strays extra) vs genuinely partial
(GT keys missing).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.xtp import _decode_payload, _fixed_cols, scan_cfp_log_records

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)

# table short name -> (cells file, key column(s))
TABLES = {
    "Product_inmem": ("Production.Product_inmem.parquet", ("ProductID",)),
    "SpecialOfferProduct_inmem": (
        "Sales.SpecialOfferProduct_inmem.parquet", ("SpecialOfferID", "ProductID")),
    "SalesOrderHeader_inmem": (
        "Sales.SalesOrderHeader_inmem.parquet", ("SalesOrderID",)),
    "SalesOrderDetail_inmem": (
        "Sales.SalesOrderDetail_inmem.parquet", ("SalesOrderDetailID",)),
}


def _key_of(row: dict, keycols: tuple[str, ...]):
    vals = [row.get(c) for c in keycols]
    if any(not isinstance(v, int) for v in vals):
        return None
    return tuple(vals) if len(vals) > 1 else vals[0]


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    raw = FIXTURE.read_bytes()
    lb_groups = scan_cfp_log_records(raw)
    print(f"LB groups: { {hex(k): len(v) for k, v in sorted(lb_groups.items())} }")

    for short, (cellfile, keycols) in TABLES.items():
        table = next((t for t in schema.tables if t.name == short), None)
        if table is None:
            print(f"\n{short}: not in schema")
            continue
        gt_rows = pq.read_table(CELLS_DIR / cellfile).to_pylist()
        # GT keys (cells store values as strings; cast ints)
        gt_keys = set()
        for r in gt_rows:
            vals = [int(r[c]) for c in keycols if r[c] is not None]
            if len(vals) == len(keycols):
                gt_keys.add(tuple(vals) if len(vals) > 1 else vals[0])
        fw = sum(c.max_length for c in _fixed_cols(table))

        # map to best LB by decoded-key overlap with GT
        best = None  # (overlap, lb, decoded_keys, extra_keys, ndecoded)
        for lb, recs in lb_groups.items():
            decoded_keys = set()
            extra = 0
            ndec = 0
            for _seq, p in recs:
                if len(p) < fw:
                    continue
                try:
                    row = _decode_payload(p, table, xtp_log_mode=True)
                except Exception:
                    continue
                k = _key_of(row, keycols)
                if k is None:
                    continue
                ndec += 1
                if k in gt_keys:
                    decoded_keys.add(k)
                else:
                    extra += 1
            ov = len(decoded_keys)
            if best is None or ov > best[0]:
                best = (ov, lb, decoded_keys, extra, ndec)
        assert best is not None
        overlap, lb, decoded_keys, extra, ndec = best
        missing = gt_keys - decoded_keys
        print(f"\n{short}: key={keycols} GT={len(gt_keys)} best_lb=0x{lb:02x}")
        print(f"  decoded records={ndec}  distinct GT-keys covered={overlap}  "
              f"missing={len(missing)}  extra(non-GT decoded)={extra}")
        if missing:
            sample = sorted(missing)[:8] if all(
                isinstance(x, int) for x in missing) else list(missing)[:8]
            print(f"  MISSING sample: {sample}")
        verdict = ("COMPLETE (all GT keys present)" if not missing
                   else f"PARTIAL ({len(missing)} GT keys absent)")
        print(f"  => {verdict}")


if __name__ == "__main__":
    main()
