#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Per-LB seq structure: is `seq` a dense contiguous per-table sequence?

If yes, seq contiguity (count == max-min+1, no gaps) is a runtime completeness
signal that does NOT need a dense {1..N} IDENTITY.  Compares gap count to the
known GT shortfall per table.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.pages import PageStore  # noqa: F401  (parity w/ other diags)
from mssqlbak.xtp import scan_cfp_log_records

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)

# LB -> (table, GT rows) by record-count mapping
LB_TABLE = {
    0x07: ("SpecialOffer_inmem", 16),
    0x08: ("Product_inmem", 504),
    0x09: ("SpecialOfferProduct_inmem", 538),
    0x0a: ("SalesOrderHeader_inmem", 31465),
    0x0b: ("SalesOrderDetail_inmem", 121317),
    0x0c: ("DemoSalesOrderDetailSeed", 538),
    0x0d: ("DemoSalesOrderHeaderSeed", 31465),
}


def main() -> None:
    raw = FIXTURE.read_bytes()
    lb_groups = scan_cfp_log_records(raw)
    for lb in sorted(lb_groups):
        recs = lb_groups[lb]
        seqs = sorted(s for s, _ in recs)
        name, gt = LB_TABLE.get(lb, ("?", -1))
        if not seqs:
            print(f"0x{lb:02x} {name}: empty")
            continue
        lo, hi = seqs[0], seqs[-1]
        span = hi - lo + 1
        distinct = len(set(seqs))
        gaps = span - distinct
        # payload size histogram
        sizes = {}
        for _s, p in recs:
            sizes[len(p)] = sizes.get(len(p), 0) + 1
        print(f"0x{lb:02x} {name}: recs={len(recs)} GT={gt} "
              f"seq[{lo}..{hi}] span={span} distinct={distinct} gaps={gaps} "
              f"contiguous={gaps == 0} sizes={sizes}")


if __name__ == "__main__":
    main()
