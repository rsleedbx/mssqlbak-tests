"""For each got_only string, identify its encode_array hash and the substitution pair.

This shows which page each got_only comes from and groups the substitutions by page.
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

current_ea: list = []
R_TO_EA: dict[bytes, bytes] = {}
EA_INFO: dict[bytes, dict] = {}

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    current_ea.clear()
    current_ea.append(ea)
    if ea not in EA_INFO:
        code_lens = []
        for i in range(256):
            b = ea[i // 2]
            code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        kraft = sum(2**(-cl) for cl in code_lens if cl > 0)
        ml2 = max(code_lens)
        c15_syms = sorted(sym for sym in range(256) if code_lens[sym] == ml2)
        # compute starting code for max_len
        by_len: dict = {}
        for sym, cl in enumerate(code_lens):
            if cl > 0:
                by_len.setdefault(cl, []).append(sym)
        code = 0
        c_start = {}
        for cl in range(1, ml2 + 1):
            c_start[cl] = code
            code += len(by_len.get(cl, []))
            code <<= 1
        EA_INFO[ea] = {
            'kraft': kraft, 'max_len': ml2,
            'c15_syms': c15_syms, 'c15_start': c_start.get(ml2, 0),
            'code_lens': code_lens,
        }
    return tab, ml, esc_start

def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None and current_ea:
        ea = current_ea[0]
        results, esc = result
        for r in results:
            R_TO_EA[bytes(r)] = ea
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
want_only = sorted(got_unique - gt_unique)

print(f"got_only: {len(got_only)}, unique EAs: {len(EA_INFO)}\n")

# Run diverge analysis to get substitution pairs for each got_only string
def best_gt_match(v: str):
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

def ea_short(ea: bytes) -> str:
    return hashlib.md5(ea).hexdigest()[:8]

# Group got_only by their encode_array
by_ea: dict[str, list] = {}
for v in got_only:
    r = VALUE_TO_R.get(v)
    ea = R_TO_EA.get(r) if r is not None else None
    key = ea_short(ea) if ea else "none"
    info = EA_INFO.get(ea) if ea else None
    by_ea.setdefault(key, []).append((v, r, ea, info))

print(f"got_only grouped by EA: {len(by_ea)} groups")
for key, items in sorted(by_ea.items(), key=lambda x: -len(x[1])):
    ea = items[0][2]
    info = items[0][3]
    kraft_str = f"{info['kraft']:.8f}" if info else "?"
    c15_start = info['c15_start'] if info else "?"
    n_c15 = len(info['c15_syms']) if info else "?"
    print(f"\n  EA={key} kraft={kraft_str} C15_start={c15_start} n_c15={n_c15} count={len(items)}")
    
    for v, r, ea, info in items[:3]:  # show first 3 per group
        best_gt, cl_len = best_gt_match(v)
        glen = len(best_gt) if best_gt else 0
        vlen = len(v)
        if cl_len == glen:
            cat = f"TAIL_OVER+{vlen-glen}"
        elif cl_len < glen and cl_len < vlen:
            cat = f"MIDDLE@{cl_len}"
        else:
            cat = "?"
        
        # Find substitution at divergence point
        if best_gt and cl_len < glen and cl_len < vlen:
            got_c = v[cl_len]
            gt_c = best_gt[cl_len]
            got_sym = ord(got_c) + 2
            gt_sym = ord(gt_c) + 2
            sub_info = f" got={repr(got_c)}(sym={got_sym}) gt={repr(gt_c)}(sym={gt_sym})"
            if info:
                code_lens = info['code_lens']
                c15_start = info['c15_start']
                c15_syms = info['c15_syms']
                if got_sym in c15_syms and gt_sym in c15_syms:
                    our_pos_got = c15_syms.index(got_sym)
                    our_pos_gt = c15_syms.index(gt_sym)
                    our_code_got = c15_start + our_pos_got
                    our_code_gt = c15_start + our_pos_gt
                    # SQL Server code for gt_sym = our code for got_sym
                    sql_pos_gt = our_pos_got
                    sub_info += f" [our_pos: got={our_pos_got} gt={our_pos_gt}] SQL_pos(gt)={sql_pos_gt}"
        else:
            sub_info = ""
        
        print(f"    {cat}{sub_info}  val[:40]={repr(v[:40])}")
