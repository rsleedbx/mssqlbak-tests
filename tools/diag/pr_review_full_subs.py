"""Show ALL substitutions for each affected encode_array.

For each got_only string, find what got_sym/gt_sym pair exists at the first
divergence and what encode_array (by hash) produced it.
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

off = dv._V4_CHAR_OFFSET
orig_build = dv._build_huff_table
orig_huff = dv._huff_decode_page_py
orig_split = dv._split_v4_record

ALL_EAS: dict[str, bytes] = {}
current_ea: list = []
EA_CL: dict[str, list] = {}  # ea_key -> code_lens

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    key = hashlib.md5(ea).hexdigest()[:8]
    if key not in ALL_EAS:
        ALL_EAS[key] = ea
        cl = []
        for i in range(256):
            b = ea[i // 2]
            cl.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        EA_CL[key] = cl
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

def best_gt_match(v):
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

def ea_short(ea): return hashlib.md5(ea).hexdigest()[:8]

# Collect ALL substitutions per EA
sub_by_ea: dict[str, list] = {}

for v in got_only:
    r = VALUE_TO_R.get(v)
    ea_key = R_TO_EA.get(r) if r is not None else None
    if ea_key is None:
        continue
    
    best_gt, cl_len = best_gt_match(v)
    glen = len(best_gt) if best_gt else 0
    
    if cl_len < glen and cl_len < len(v) and best_gt:
        got_c = v[cl_len]
        gt_c = best_gt[cl_len]
        got_sym = ord(got_c) + 2
        gt_sym = ord(gt_c) + 2
        
        cl_info = EA_CL.get(ea_key, [])
        if cl_info:
            got_cl = cl_info[got_sym] if got_sym < 256 else -1
            gt_cl = cl_info[gt_sym] if gt_sym < 256 else -1
        else:
            got_cl = gt_cl = -1
        
        sub_by_ea.setdefault(ea_key, []).append(
            (cl_len, got_sym, gt_sym, got_c, gt_c, got_cl, gt_cl)
        )

TARGET_EAS = {"bde8b0ed", "b48c5b50"}
for ea_key in TARGET_EAS:
    subs = sub_by_ea.get(ea_key, [])
    ea = ALL_EAS.get(ea_key)
    if ea is None:
        print(f"EA {ea_key}: not found")
        continue
    
    cl_list = EA_CL[ea_key]
    max_cl = max(cl_list)
    cl_max_syms = sorted(s for s in range(256) if cl_list[s] == max_cl)
    
    # Compute C_max_start
    by_len: dict = {}
    for sym, cl in enumerate(cl_list):
        if cl > 0:
            by_len.setdefault(cl, []).append(sym)
    code = 0
    c_start = {}
    for cl in range(1, max_cl + 1):
        c_start[cl] = code
        code += len(by_len.get(cl, []))
        code <<= 1
    C = c_start[max_cl]
    
    sym_to_our_pos = {sym: i for i, sym in enumerate(cl_max_syms)}
    
    print(f"\n=== EA={ea_key}: {len(subs)} MIDDLE substitutions, cl15_start={C}, {len(cl_max_syms)} cl=15 syms ===")
    
    # Deduplicate substitutions (same got/gt pair may appear multiple times)
    seen = set()
    unique_subs = []
    for entry in sorted(subs, key=lambda x: x[1]):  # sort by got_sym
        key = (entry[1], entry[2])  # (got_sym, gt_sym)
        if key not in seen:
            seen.add(key)
            unique_subs.append(entry)
    
    # For each unique sub, compute our pos and inferred SQL pos
    print("  Unique substitutions (got→gt at first divergence):")
    for _, got_sym, gt_sym, got_c, gt_c, got_cl, gt_cl in unique_subs:
        our_pos_got = sym_to_our_pos.get(got_sym, -1)
        our_pos_gt = sym_to_our_pos.get(gt_sym, -1)
        
        # SQL Server encoded gt_sym with our code for got_sym
        # SQL_pos(gt_sym) = our_pos(got_sym)
        sql_pos_gt = our_pos_got
        shift = sql_pos_gt - our_pos_gt if our_pos_gt >= 0 else '?'
        
        shift_str = f"{shift:+}" if isinstance(shift, int) else str(shift)
        print(f"    got={repr(got_c):>3}(sym={got_sym:3d} cl={got_cl:2d} ourPos={our_pos_got:3d}) → "
              f"gt={repr(gt_c):>3}(sym={gt_sym:3d} cl={gt_cl:2d} ourPos={our_pos_gt:3d}) "
              f"SQL_pos(gt)={sql_pos_gt} shift={shift_str}")
    
    # Show the cl=15 group with known SQL positions highlighted
    print(f"\n  cl=15 group ({len(cl_max_syms)} syms), known SQL positions:")
    known_sql_pos = {}  # sym → sql_pos
    for _, got_sym, gt_sym, *_ in unique_subs:
        if got_sym in sym_to_our_pos and gt_sym in sym_to_our_pos:
            sql_pos = sym_to_our_pos[got_sym]
            known_sql_pos[gt_sym] = sql_pos
    
    for i, sym in enumerate(cl_max_syms[:30]):
        char = repr(chr(sym-2)) if 32 <= sym-2 <= 126 else hex(sym-2)
        sql_pos_info = f"→SQL_pos={known_sql_pos[sym]}" if sym in known_sql_pos else ""
        print(f"    pos {i:3d}: sym={sym:3d} {char:>5}{sql_pos_info}")
    if len(cl_max_syms) > 30:
        print(f"    ... ({len(cl_max_syms)-30} more)")
