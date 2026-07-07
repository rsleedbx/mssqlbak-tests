#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Authoritative byte-exact verification of Product_inmem (LB 0x08, seq 1..504
complete) with the CURRENT decoder (XTP-native fixed/variable partition +
numeric mantissa), using the production comparator primitives (tools.cell_canon
+ the .cells manifest sql_types)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.xtp import _decode_payload, scan_cfp_log_records
from tools.cell_canon import canon
from tools.value_verify import _effective_sql_type, load_manifest

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)
FQN = "Production.Product_inmem"


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "Product_inmem")

    manifest = load_manifest(CELLS_DIR)
    entry = next(t for t in manifest["tables"] if t["fqn"] == FQN)
    sql_types = {c["name"]: _effective_sql_type(c) for c in entry["columns"]}
    keycols = entry["key_columns"]

    gt = pq.read_table(CELLS_DIR / f"{FQN}.parquet").to_pylist()
    gt_by_key = {tuple(canon(r[k], sql_types[k]) for k in keycols): r for r in gt}

    recs = scan_cfp_log_records(FIXTURE.read_bytes())[0x08]
    decoded = {}
    for _seq, p in recs:
        row = _decode_payload(p, table, xtp_log_mode=True)
        k = tuple(canon(row.get(c), sql_types.get(c, "")) for c in keycols)
        decoded[k] = row

    cols = [c["name"] for c in entry["columns"]]
    mism = 0
    shown = 0
    for k, gtrow in gt_by_key.items():
        drow = decoded.get(k)
        if drow is None:
            mism += 1
            if shown < 15:
                print(f"MISSING key {k}")
                shown += 1
            continue
        for c in cols:
            st = sql_types.get(c, "")
            gv = canon(gtrow.get(c), st)
            dv = canon(drow.get(c), st)
            if gv != dv:
                mism += 1
                if shown < 25:
                    print(f"MISMATCH key={k} col={c} ({st}): GT={gv!r} decoded={dv!r}")
                    shown += 1
                break
    print(f"\nGT={len(gt_by_key)} decoded={len(decoded)} mismatched_rows={mism}")
    print("BYTE-EXACT (canon)" if mism == 0 else "NOT byte-exact")


if __name__ == "__main__":
    main()
