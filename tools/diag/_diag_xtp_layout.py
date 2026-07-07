#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Solve the XTP fixed-section layout for Product_inmem by locating each fixed
column's GT value in a rich (non-null) record's payload, revealing the ordering
rule (alignment grouping + any prefix)."""
from __future__ import annotations

import datetime as dt
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.xtp import _XTP_TICKS_PER_DAY, scan_cfp_log_records

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)

EPOCH = dt.date(1900, 1, 1)


def enc_candidates(col, val):
    """Return plausible little-endian byte encodings of GT string *val* for col."""
    if val is None:
        return []
    t = col.type_id
    out = []
    try:
        if t == 56:  # int
            out.append(struct.pack("<i", int(val)))
        elif t == 52:  # smallint
            out.append(struct.pack("<h", int(val)))
        elif t == 104:  # bit
            out.append(bytes([1 if str(val) in ("1", "True", "true") else 0]))
        elif t == 60:  # money: 8-byte, scaled *10000
            cents = int(round(float(val) * 10000))
            out.append(struct.pack("<q", cents))
        elif t in (231, 239):  # nvarchar/nchar -> utf-16-le
            out.append(str(val).encode("utf-16-le"))
        elif t == 42:  # datetime2 -> uint64 ticks since 1900
            d = dt.datetime.fromisoformat(str(val))
            days = (d.date() - EPOCH).days
            ticks = days * _XTP_TICKS_PER_DAY + (
                d.hour * 3600 + d.minute * 60 + d.second) * 10_000_000 + d.microsecond * 10
            out.append(struct.pack("<Q", ticks))
        elif t == 106:  # numeric/decimal - skip (complex)
            pass
    except Exception:
        pass
    return out


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "Product_inmem")
    gt = pq.read_table(CELLS_DIR / "Production.Product_inmem.parquet").to_pylist()

    # pick a rich row: non-null Color, Size, Weight, money>0
    rich = None
    for r in gt:
        if (r["Color"] and r["Size"] and r["StandardCost"]
                and float(r["StandardCost"]) > 0 and r["SizeUnitMeasureCode"]):
            rich = r
            break
    assert rich is not None
    print(f"rich row ProductID={rich['ProductID']} Name={rich['Name']!r}")

    raw = FIXTURE.read_bytes()
    recs = scan_cfp_log_records(raw)[0x08]
    name_utf16 = str(rich["Name"]).encode("utf-16-le")
    payload = None
    for _seq, p in recs:
        if name_utf16 in p:
            payload = p
            break
    assert payload is not None, "record not found by Name"
    print(f"payload {len(payload)}B:\n{payload.hex(' ')}")

    # locate each fixed column
    print("\ncolumn -> offset(s) found:")
    rows = []
    for c in sorted(table.columns, key=lambda c: c.colid):
        if c.is_variable:
            continue
        cands = enc_candidates(c, rich[c.name])
        found = []
        for pat in cands:
            if not pat:
                continue
            found += [i for i in range(len(payload) - len(pat) + 1)
                      if payload[i:i + len(pat)] == pat]
        rows.append((c.colid, c.name, c.type_id, c.max_length, rich[c.name], found))
    for colid, name, tid, ml, val, found in rows:
        print(f"  colid={colid:2d} {name:24s} type={tid} len={ml} val={str(val)[:16]:16s} -> {found}")


if __name__ == "__main__":
    main()
