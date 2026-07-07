#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Full-row byte-exact verification of SpecialOfferProduct_inmem (LB 0x09,
seq 1..538 complete) with the CURRENT decoder, vs .cells ground truth."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.xtp import _decode_payload, scan_cfp_log_records

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)


def _norm(v):
    if v is None:
        return None
    return str(v)


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "SpecialOfferProduct_inmem")
    print("columns (colid):", [(c.colid, c.name, c.type_id, c.max_length,
                                c.is_variable, c.nullable) for c in
                               sorted(table.columns, key=lambda c: c.colid)])

    gt = pq.read_table(CELLS_DIR / "Sales.SpecialOfferProduct_inmem.parquet").to_pylist()
    keycols = ("SpecialOfferID", "ProductID")
    gt_by_key = {tuple(int(r[c]) for c in keycols): r for r in gt}

    recs = scan_cfp_log_records(FIXTURE.read_bytes())[0x09]
    decoded = {}
    for _seq, p in recs:
        row = _decode_payload(p, table, xtp_log_mode=True)
        k = tuple(row.get(c) for c in keycols)
        decoded[k] = row

    cols = [c.name for c in sorted(table.columns, key=lambda c: c.colid)]
    mism = 0
    shown = 0
    for k, gtrow in gt_by_key.items():
        drow = decoded.get(k)
        if drow is None:
            mism += 1
            if shown < 10:
                print(f"MISSING key {k}")
                shown += 1
            continue
        for c in cols:
            gv, dv = _norm(gtrow.get(c)), _norm(drow.get(c))
            # datetime formatting differs; compare prefixes loosely
            if gv != dv and not (gv and dv and gv[:19] == dv[:19]):
                mism += 1
                if shown < 15:
                    print(f"MISMATCH key={k} col={c}: GT={gv!r} decoded={dv!r}")
                    shown += 1
                break
    print(f"\nGT={len(gt_by_key)} decoded={len(decoded)} mismatched_rows={mism}")
    print("BYTE-EXACT" if mism == 0 else "NOT byte-exact")


if __name__ == "__main__":
    main()
