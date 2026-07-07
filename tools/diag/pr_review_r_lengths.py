"""Examine raw buffer lengths vs decoded0 for got-only entries.

For records with decoded0 >= 0x80 and non-printable d1, the current code uses
r[2:] (unbounded). If the Python fallback over-reads past the actual content,
len(r) > 2+decoded0 and the tail bytes are garbage.  This script checks whether
bounding to r[2:2+decoded0] would fix the got-only entries.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq
from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
from mssqlbak.columnstore.decode import dict_xvelocity as dv
import mssqlbak.columnstore.assembly.reader as _reader_mod

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")
gt_path = Path(
    "tests/fixtures_realworld/tpcxbb_1gb.bak.cells/dbo.product_reviews.parquet"
)

# Load GT
gt = pq.read_table(gt_path, columns=["pr_review_content"])
gt_vals = [v.as_py() for v in gt.column("pr_review_content")]
gt_unique = set(v for v in gt_vals if v is not None)

off = dv._V4_CHAR_OFFSET

# Capture detailed info about each buffer for decoded0>=0x80 records
# VALUE_META: value -> (from_python_fallback, is_escape, r_bytes)
VALUE_DETAIL: dict = {}
orig_split = dv._split_v4_record


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and r and not is_escape:
        decoded0 = r[0] - off
        if decoded0 >= 0x80 and len(r) >= 2:
            d1 = r[1] - off
            for v in result:
                if v not in VALUE_DETAIL:
                    VALUE_DETAIL[v] = (decoded0, d1, len(r), bytes(r[:min(20,len(r))]))
    return result


dv._split_v4_record = patched_split
try:
    _reader_mod._split_v4_record = patched_split  # type: ignore[attr-defined]
except AttributeError:
    pass

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")
rows = list(read_columnstore_rows(store, tbl))

dv._split_v4_record = orig_split
try:
    _reader_mod._split_v4_record = orig_split  # type: ignore[attr-defined]
except AttributeError:
    pass

got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")

got_only = sorted(got_unique - gt_unique)
want_only = sorted(gt_unique - got_unique)

print(f"correct={len(gt_unique & got_unique)}, got_only={len(got_only)}, want_only={len(want_only)}")

print("\n=== GOT_ONLY entries with decoded0 >= 0x80 ===")
print("(checking if r[2:2+decoded0] would fix tail errors)\n")

for i, v in enumerate(got_only):
    if v not in VALUE_DETAIL:
        continue
    decoded0, d1, rlen, r_head = VALUE_DETAIL[v]
    over = rlen - 2 - decoded0
    printable_d1 = 0x20 <= d1 <= 0x7F
    d1_char = chr(d1) if 32 <= d1 <= 126 else f"\\x{d1:02x}"

    # Check if bounding to decoded0 would give a string that matches some want-only
    # We can simulate: the current value v came from r[2:] (up to rlen-2 chars from pos 2)
    # r[2:2+decoded0] would give v[:decoded0] (first decoded0 chars of v)
    bounded_v = v[:decoded0]
    matches_gt = bounded_v in gt_unique

    status = ""
    if matches_gt:
        status = "*** BOUNDED MATCHES GT ***"
    elif printable_d1:
        status = "[printable d1 - discrimination issue]"
    elif over > 0:
        status = f"[over-read by {over} chars]"

    print(
        f"  [{i}] d0={decoded0} d1={d1_char} rlen={rlen} 2+d0={2+decoded0} "
        f"over={over} prtbl={int(printable_d1)} {status}"
    )
    print(f"       got:  {repr(v[:80])}")
    if matches_gt:
        print(f"       bounded({decoded0}): {repr(bounded_v[:80])}")

print("\n=== Summary ===")
fixable = 0
for v in got_only:
    if v not in VALUE_DETAIL:
        continue
    decoded0, d1, rlen, r_head = VALUE_DETAIL[v]
    bounded_v = v[:decoded0]
    if bounded_v in gt_unique:
        fixable += 1

print(f"Got-only entries where r[2:2+decoded0] (= v[:decoded0]) matches GT: {fixable}")
