"""
Compare decoded pr_review_content unique values against GT.
Shows got-only and want-only values with decode path details.
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
print(f"GT unique values: {len(gt_unique)}")

# Patch _split_v4_record to track which values come from which format
VALUE_META: dict = {}  # value -> (from_python_fallback, is_escape, r0, r1, decoded0)
orig_split = dv._split_v4_record


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    off = 2
    if r:
        r0 = r[0]
        r1 = r[1] if len(r) >= 2 else -1
        d0 = r0 - off
        for v in result:
            if v not in VALUE_META:
                VALUE_META[v] = (from_python_fallback, is_escape, r0, r1, d0)
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
print(f"Got unique values: {len(got_unique)}")

got_only = sorted(got_unique - gt_unique)
want_only = sorted(gt_unique - got_unique)
correct = gt_unique & got_unique

print(f"\ncorrect={len(correct)}, got_only={len(got_only)}, want_only={len(want_only)}")

print("\nGOT_ONLY (all, with decode path):")
for i, v in enumerate(got_only):
    meta = VALUE_META.get(v)
    if meta:
        fb, esc, r0, r1, d0 = meta
        print(
            f"  [{i}] fb={int(fb)} esc={int(esc)} "
            f"r0=0x{r0:02x} r1=0x{r1:02x} d0={d0}: {repr(v[:100])}"
        )
    else:
        print(f"  [{i}] (no meta): {repr(v[:100])}")

print("\nWANT_ONLY (all GT values we don't produce):")
for i, v in enumerate(want_only):
    print(f"  [{i}] {repr(v[:100])}")
