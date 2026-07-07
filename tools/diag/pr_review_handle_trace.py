"""Trace specific handles that produce MIDDLE_WRONG got-only strings.

For each MIDDLE_WRONG got-only string, find the handle that produces it,
capture the exact encode_array for that handle's page, and show which Huffman
code maps to the got symbol vs the expected GT symbol.
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

off = dv._V4_CHAR_OFFSET

# Map: Huffman page result r_bytes -> (encode_array, bos_list, handle_local_idx)
R_TO_EA: dict[bytes, bytes] = {}

orig_huff = dv._huff_decode_page_py
orig_build = dv._build_huff_table

current_ea: list[bytes] = []

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    current_ea.clear()
    current_ea.append(bytes(encode_array_128))
    return tab, ml, esc_start

def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None and current_ea:
        results, esc = result
        ea = current_ea[0]
        for i, r in enumerate(results):
            R_TO_EA[bytes(r)] = ea
    return result

dv._build_huff_table = hooked_build
dv._huff_decode_page_py = hooked_huff

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")
rows = list(read_columnstore_rows(store, tbl))

dv._build_huff_table = orig_build
dv._huff_decode_page_py = orig_huff

# Collect got_only
got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")
got_only = sorted(got_unique - gt_unique)

print(f"R_TO_EA has {len(R_TO_EA)} entries")
print(f"got_only: {len(got_only)}")

# We need to find the r buffer for specific got_only strings.
# Re-run split with patching to get r -> value mapping.
orig_split = dv._split_v4_record
VALUE_TO_R: dict[str, bytes] = {}

def hooked_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback:
        for v in result:
            if v not in VALUE_TO_R:
                VALUE_TO_R[v] = bytes(r)
    return result

dv._split_v4_record = hooked_split
dv._build_huff_table = hooked_build
dv._huff_decode_page_py = hooked_huff

rows2 = list(read_columnstore_rows(store, tbl))

dv._split_v4_record = orig_split
dv._build_huff_table = orig_build
dv._huff_decode_page_py = orig_huff

# Now analyze specific got_only strings
print(f"\nVALUE_TO_R: {len(VALUE_TO_R)} entries\n")

# Focus on MIDDLE_WRONG cases with clear character substitutions
TARGET_CASES = [
    # (got_prefix, got_char, gt_char, diverge_pos)
    ("ue called |treatment.'", '|', '`', 118),
    ("effects. {why{? Also", '{', '_', 943),
    ("of over 20=. One does", '=', '%', 342),
    ("g grade 'A>'. Thanks", '>', '+', 1006),
    ("anerickson`alumni.duke.edu", '`', '@', 960),  # case 22
    ("anerickson`alumni.duke.edu", '`', '@', 1539), # case 59
]

for got_prefix, got_c, gt_c, pos in TARGET_CASES:
    # Find the got_only string
    matching = [v for v in got_only if got_prefix in v]
    if not matching:
        print(f"NOT FOUND: {repr(got_prefix[:20])}")
        continue

    v = matching[0]
    r_buf = VALUE_TO_R.get(v)
    if r_buf is None:
        print(f"NO r_buf for {repr(got_prefix[:20])}")
        continue

    ea = R_TO_EA.get(r_buf)
    if ea is None:
        print(f"NO ea for {repr(got_prefix[:20])} (r_len={len(r_buf)})")
        continue

    # Rebuild the Huffman table
    tab, ml, esc_start = orig_build(ea)
    if tab is None:
        print("Table build failed")
        continue

    code_lens = []
    for i in range(256):
        b = ea[i // 2]
        code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)

    kraft = sum(2**(-cl) for cl in code_lens if cl > 0)

    got_sym = ord(got_c) + 2  # Huffman symbol for got char
    gt_sym = ord(gt_c) + 2    # Huffman symbol for expected char

    # Rebuild canonical assignment
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

    print(f"=== got='{got_c}' gt='{gt_c}' at pos={pos} ===")
    print(f"  r_len={len(r_buf)} ea_kraft={kraft:.8f} max_len={ml}")
    print(f"  got_sym={got_sym} cl={code_lens[got_sym]}")
    print(f"  gt_sym={gt_sym}  cl={code_lens[gt_sym]}")

    if got_sym in sym_to_code:
        gcl, gc = sym_to_code[got_sym]
        print(f"  got canonical: sym={got_sym} cl={gcl} code={gc:0{gcl}b}({gc})")
    else:
        print(f"  got_sym={got_sym} UNUSED in table")

    if gt_sym in sym_to_code:
        rcl, rc = sym_to_code[gt_sym]
        print(f"  gt  canonical: sym={gt_sym} cl={rcl} code={rc:0{rcl}b}({rc})")
    else:
        print(f"  gt_sym={gt_sym} UNUSED in table -- cl=0!")

    # Find what the table actually returns for the GT code
    if gt_sym in sym_to_code:
        rcl, rc = sym_to_code[gt_sym]
        # The table fills prefix = rc << (ml - rcl) to prefix + 2^(ml-rcl) - 1
        prefix = rc << (ml - rcl)
        table_entry = tab[prefix]
        table_sym = table_entry >> 8
        table_cl = table_entry & 0xFF
        print(f"  tab[{prefix}] = sym={table_sym} cl={table_cl} (expected sym={gt_sym})")

    # Now look for the specific byte in r that corresponds to the substitution
    # For Format A (d0>=0x80), content starts at r[2]. Position `pos` in content = r[2+pos].
    decoded0 = r_buf[0] - off
    if decoded0 >= 0x80:  # Format A
        r_pos = 2 + pos
    else:
        r_pos = 1 + pos
    if r_pos < len(r_buf):
        actual_byte = r_buf[r_pos]
        print(f"  r[{r_pos}]=0x{actual_byte:02X}=sym{actual_byte} (correct would be sym{gt_sym}=0x{gt_sym:02X})")
    print()
