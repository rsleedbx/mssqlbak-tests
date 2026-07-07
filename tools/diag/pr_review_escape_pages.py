"""Find which encode_arrays produce the broken escape handles after the fix.

Prints the EA key, n_available-n_max (unused count), and sample strings
for escape handles (esc=1) that end up in got_only.
"""
import sys
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq
from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
from mssqlbak.columnstore.decode import dict_xvelocity as dv

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")
gt_path = Path(
    "tests/fixtures_realworld/tpcxbb_1gb.bak.cells/dbo.product_reviews.parquet"
)

gt = pq.read_table(gt_path, columns=["pr_review_content"])
gt_unique = set(v.as_py() for v in gt.column("pr_review_content") if v.as_py() is not None)

orig_build = dv._build_huff_table
orig_huff = dv._huff_decode_page_py
orig_split = dv._split_v4_record

EA_INFO: dict[str, dict] = {}
current_ea: list = []

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    key = hashlib.md5(ea).hexdigest()[:8]
    if key not in EA_INFO:
        cl = []
        for i in range(256):
            b = ea[i // 2]
            cl.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        max_len = max(cl)
        n_max = sum(1 for c in cl if c == max_len)
        # Compute n_available the same way build does
        code = 0
        by_len: dict = {}
        for sym, c in enumerate(cl):
            if c > 0:
                by_len.setdefault(c, []).append(sym)
        for c in range(1, max_len):
            code += len(by_len.get(c, []))
            code <<= 1
        n_available = (1 << max_len) - code
        unused = n_available - n_max
        EA_INFO[key] = {"max_len": max_len, "n_max": n_max, "n_available": n_available, "unused": unused}
    current_ea.clear()
    current_ea.append(key)
    return tab, ml, esc_start

R_TO_EA: dict[bytes, str] = {}
def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None and current_ea:
        key = current_ea[0]
        for r in result[0]:
            R_TO_EA[bytes(r)] = key
    return result

VALUE_TO_R: dict[str, bytes] = {}
def hooked_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback:
        for v in result:
            if v not in VALUE_TO_R:
                VALUE_TO_R[v] = bytes(r)
    return result

dv._build_huff_table = hooked_build
dv._huff_decode_page_py = hooked_huff
dv._split_v4_record = hooked_split

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")
rows = list(read_columnstore_rows(store, tbl))

dv._build_huff_table = orig_build
dv._huff_decode_page_py = orig_huff
dv._split_v4_record = orig_split

got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")
got_only = sorted(got_unique - gt_unique)

print(f"got_only count: {len(got_only)}")
print()

# For each got_only, find its EA and show unused count
ea_stats: dict[str, list] = {}
for v in got_only:
    r = VALUE_TO_R.get(v)
    ea_key = R_TO_EA.get(r) if r is not None else None
    if ea_key is None:
        print(f"  NO EA: {repr(v[:60])}")
        continue
    ea_stats.setdefault(ea_key, []).append(v)

for ea_key, vals in sorted(ea_stats.items()):
    info = EA_INFO.get(ea_key, {})
    print(f"EA={ea_key}: unused={info.get('unused','?')}, n_max={info.get('n_max','?')}, "
          f"n_available={info.get('n_available','?')}, {len(vals)} got_only strings")
    for v in vals[:3]:
        r0 = VALUE_TO_R.get(v, b'')
        r0_hex = hex(r0[0]) if r0 else '?'
        print(f"  r0={r0_hex}: {repr(v[:80])}")
