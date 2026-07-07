"""For specific got-only strings, capture the raw r-buffer and the Huffman page
encode_array, then show the code assignments for the substituted symbols.

Focus on MIDDLE_WRONG case [8]: '|' instead of '`' at position 118.
"""
import sys
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

# Known MIDDLE_WRONG got-only strings exhibiting character substitutions.
# Key: got string prefix (first 20 chars), Value: (expected_char, got_char, position)
TARGET_SUBS = {
    # case [8]: got '|' at position 118, gt '`'
    "ue called |treatment.'": ('|', '`', 118),
    # case [14]: got '{why{' - '{' at 943, gt '_why_'
    "effects. {why{? Also": ('{', '_', 9),
    # case [7]: got '=' instead of '%' at position 342
    "of over 20=. One does": ('=', '%', 342),
    # case [12]: got '>' instead of '+' at position 1006
    "g grade 'A>'. Thanks": ('>', '+', 1006),
}

off = dv._V4_CHAR_OFFSET

# Capture: for each page, the encode_array and all decoded records with substituted chars
CAPTURES: list[dict] = []

orig_split = dv._split_v4_record
orig_huff = dv._huff_decode_page_py
orig_build = dv._build_huff_table

page_context: list = []  # [encode_array, page_id]

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    page_context.clear()
    page_context.append(bytes(encode_array_128))
    return tab, ml, esc_start

def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    return result

def hooked_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and r:
        decoded0 = r[0] - off
        for v in result:
            # Check if this value contains one of our target substitutions
            for target_prefix, (got_c, gt_c, approx_pos) in TARGET_SUBS.items():
                # Check by first 20 chars of content
                check_str = target_prefix[:10]
                if check_str in v:
                    CAPTURES.append({
                        'value': v,
                        'got_c': got_c,
                        'gt_c': gt_c,
                        'approx_pos': approx_pos,
                        'r_hex': r[:40].hex(),
                        'r_len': len(r),
                        'decoded0': decoded0,
                        'd1': (r[1] - off) if len(r) >= 2 else -1,
                        'encode_array': bytes(page_context[0]) if page_context else None,
                        'is_escape': is_escape,
                    })
    return result

dv._build_huff_table = hooked_build
dv._split_v4_record = hooked_split

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")
rows = list(read_columnstore_rows(store, tbl))

dv._build_huff_table = orig_build
dv._split_v4_record = orig_split

print(f"Captured {len(CAPTURES)} matching records\n")

# For each capture, rebuild the Huffman table and show code assignments for the
# substituted and target symbols
seen_eas = set()
for cap in CAPTURES[:8]:  # Show first 8 captures
    ea = cap['encode_array']
    if ea is None:
        print("No encode_array captured for this record\n")
        continue
    if ea in seen_eas:
        continue
    seen_eas.add(ea)

    print(f"--- got_c='{cap['got_c']}' gt_c='{cap['gt_c']}' decoded0={cap['decoded0']} d1={cap['d1']} ---")
    print(f"    r_hex[:40]={cap['r_hex']}")
    print(f"    value[:50]={repr(cap['value'][:50])}")

    # Rebuild table and show symbol codes
    tab, ml, esc_start = orig_build(ea)
    if tab is None:
        print("    Table build failed\n")
        continue

    code_lens = []
    for i in range(256):
        b = ea[i // 2]
        code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)

    kraft = sum(2**(-cl) for cl in code_lens if cl > 0)
    print(f"    kraft={kraft:.8f} max_len={ml}")

    # Show code assignments for the substituted pair
    got_sym = ord(cap['got_c']) + 2
    gt_sym = ord(cap['gt_c']) + 2
    
    for sym in sorted(set([got_sym, gt_sym, got_sym-1, got_sym+1, gt_sym-1, gt_sym+1])):
        if 0 <= sym < 256:
            cl = code_lens[sym]
            char = chr(sym - 2) if 32 <= sym - 2 <= 126 else repr(chr(sym-2))
            print(f"    sym={sym:3d} char={char} cl={cl}")
    
    # Show the canonical code assignment for got_sym and gt_sym
    # Rebuild manually
    by_len: dict = {}
    for sym, cl in enumerate(code_lens):
        if cl > 0:
            by_len.setdefault(cl, []).append(sym)
    
    code = 0
    sym_to_code: dict = {}
    for cl in range(1, ml + 1):
        for sym in sorted(by_len.get(cl, [])):
            sym_to_code[sym] = (cl, code)
            code += 1
        code <<= 1
    
    print("    --- canonical codes ---")
    if got_sym in sym_to_code:
        cl_g, c_g = sym_to_code[got_sym]
        print(f"    got_sym={got_sym} cl={cl_g} code={c_g:0{cl_g}b} ({c_g})")
    else:
        print(f"    got_sym={got_sym} cl=0 (UNUSED)")
    if gt_sym in sym_to_code:
        cl_r, c_r = sym_to_code[gt_sym]
        print(f"    gt_sym={gt_sym}  cl={cl_r} code={c_r:0{cl_r}b} ({c_r})")
    else:
        print(f"    gt_sym={gt_sym} cl=0 (UNUSED)")
    
    # Show surrounding symbols in same code length groups
    for sym in [got_sym, gt_sym]:
        if sym in sym_to_code:
            cl, c = sym_to_code[sym]
            neighbors = sorted(by_len.get(cl, []))
            idx = neighbors.index(sym)
            start = max(0, idx - 3)
            end = min(len(neighbors), idx + 4)
            group = neighbors[start:end]
            print(f"    sym {sym} neighbors in cl={cl}: {group} (index {idx})")
    print()
