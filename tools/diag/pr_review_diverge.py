"""Find exact divergence point between got-only and corresponding GT strings.

For each got-only entry, finds the best-matching GT string (longest common prefix)
and reports the first position where they differ.  This distinguishes:
  - Position 0: format discrimination (wrong overhead byte)
  - Position N < len(GT): Huffman symbol error in the middle
  - Position = len(GT): extra garbage at the tail (over-read)
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

gt = pq.read_table(gt_path, columns=["pr_review_content"])
gt_vals = [v.as_py() for v in gt.column("pr_review_content")]
gt_unique = set(v for v in gt_vals if v is not None)

off = dv._V4_CHAR_OFFSET
VALUE_DETAIL: dict = {}
orig_split = dv._split_v4_record


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and r:
        decoded0 = r[0] - off
        d1 = (r[1] - off) if len(r) >= 2 else -1
        for v in result:
            if v not in VALUE_DETAIL:
                VALUE_DETAIL[v] = (decoded0, d1, len(r), bool(is_escape))
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


def best_gt_match(v: str) -> "tuple[str | None, int]":
    """Return (best_gt, common_prefix_len) for the GT string with the longest common prefix."""
    best_gt = None
    best_len = -1
    for gt_s in gt_unique:
        cl = 0
        for a, b in zip(v, gt_s):
            if a == b:
                cl += 1
            else:
                break
        if cl > best_len:
            best_len = cl
            best_gt = gt_s
    return best_gt, best_len


print(f"correct={len(gt_unique & got_unique)}, got_only={len(got_only)}, want_only={len(want_only)}")
print("\n=== Divergence analysis for got-only entries ===\n")

# Build a prefix-sorted index of GT strings for faster lookup
gt_sorted = sorted(gt_unique)

tail_only = 0
start_only = 0
middle_only = 0
correct_start_long = 0

for i, v in enumerate(got_only):
    meta = VALUE_DETAIL.get(v)
    d0 = meta[0] if meta else -1
    d1 = meta[1] if meta else -1
    rlen = meta[2] if meta else -1
    is_esc = meta[3] if meta else False

    # Find best GT match
    best_gt, cl = best_gt_match(v)

    if best_gt is None:
        print(f"[{i}] NO GT MATCH FOUND")
        continue

    glen = len(best_gt)
    vlen = len(v)

    if cl == glen:
        # Got string starts correctly and GT ends here; got has extra tail
        cat = "TAIL_OVER"
        tail_only += 1
    elif cl == 0:
        cat = "START_WRONG"
        start_only += 1
    elif cl < glen and cl < vlen:
        cat = "MIDDLE_WRONG"
        middle_only += 1
    else:
        cat = "OTHER"

    if d0 >= 0:
        printable_d1 = 0x20 <= d1 <= 0x7F
        d1_repr = repr(chr(d1)) if 32 <= d1 <= 126 else f"\\x{d1:02x}"
        meta_str = f"d0={d0} d1={d1_repr} rlen={rlen} esc={int(is_esc)}"
    else:
        meta_str = "(no meta)"

    print(f"[{i}] {cat} cl={cl} glen={glen} vlen={vlen}  {meta_str}")
    if cat == "MIDDLE_WRONG":
        # Show the divergence context
        ctx_start = max(0, cl - 10)
        print(f"     got[{cl-5}:{cl+15}]:  {repr(v[ctx_start:cl+20])}")
        print(f"     gt [{cl-5}:{cl+15}]:  {repr(best_gt[ctx_start:cl+20])}")
    elif cat == "START_WRONG":
        print(f"     got[:30]: {repr(v[:30])}")
        print(f"     gt [:30]: {repr(best_gt[:30])}")
    elif cat == "TAIL_OVER":
        extra = v[glen:]
        print(f"     extra tail [{len(extra)} chars]: {repr(extra[:40])}")

print("\nSummary:")
print(f"  TAIL_OVER (extra chars after correct prefix): {tail_only}")
print(f"  MIDDLE_WRONG (error within string body):      {middle_only}")
print(f"  START_WRONG (wrong from char 0):              {start_only}")
