"""Dump SS2025 native-json raw bytes alongside the expected string."""
from __future__ import annotations

import sys
from pathlib import Path

import pyarrow.parquet as pq

from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.rows import read_table_rows


def main() -> int:
    bak = Path(sys.argv[1])
    ps = PageStore.from_bak(str(bak))
    sch = recover_schema(ps)
    tbl = next(t for t in sch.tables if "json" in t.name.lower())
    # want strings from cells parquet
    cells = bak.parent / f"{bak.name}.cells" / f"dbo.{tbl.name}.parquet"
    want = {}
    if cells.exists():
        t = pq.read_table(cells)
        d = t.to_pydict()
        # key col + doc col
        keys = d.get("id") or d.get(list(d.keys())[0])
        docs = d.get("doc")
        for k, v in zip(keys, docs):
            want[str(k)] = v
    rows = list(read_table_rows(ps, tbl))
    for r in rows:
        rid = str(r.get("id"))
        raw = r.get("doc")
        print(f"\n=== id={rid}  want={want.get(rid)!r}")
        if isinstance(raw, (bytes, bytearray)):
            b = bytes(raw)
            print(f"  len={len(b)}")
            print("  hex:", b.hex(" "))
            # annotated bytes
            ann = []
            for i, ch in enumerate(b):
                c = chr(ch) if 32 <= ch < 127 else "."
                ann.append(f"{i:3d}:{ch:02x}{c}")
            print("  ", " ".join(ann))
        else:
            print("  decoded:", repr(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
