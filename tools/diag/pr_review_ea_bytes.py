"""Print the actual encode_array bytes for the two affected pages, and also test
what happens if we swap the nibble order (high↔low for each byte).
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

# Capture all unique encode_arrays
ALL_EAS: dict[str, bytes] = {}
current_ea: list = []

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    key = hashlib.md5(ea).hexdigest()[:8]
    ALL_EAS[key] = ea
    current_ea.clear()
    current_ea.append(key)
    return tab, ml, esc_start

R_TO_EA: dict[bytes, str] = {}
def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None and current_ea:
        ea_key = current_ea[0]
        results, esc = result
        for r in results:
            R_TO_EA[bytes(r)] = ea_key
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

print(f"Total unique EAs captured: {len(ALL_EAS)}")

TARGET_EAS = {"bde8b0ed", "b48c5b50"}

for ea_key in TARGET_EAS:
    ea = ALL_EAS.get(ea_key)
    if ea is None:
        print(f"EA {ea_key} not found")
        continue
    
    print(f"\n=== EA={ea_key} ===")
    
    # Parse code lengths both ways (normal and nibble-swapped)
    cl_normal = []
    cl_swapped = []
    for i in range(256):
        b = ea[i // 2]
        cl_normal.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        cl_swapped.append((b >> 4) & 0xF if i % 2 == 0 else b & 0xF)  # swap
    
    kraft_normal = sum(2**(-cl) for cl in cl_normal if cl > 0)
    kraft_swapped = sum(2**(-cl) for cl in cl_swapped if cl > 0)
    max_normal = max(cl_normal)
    max_swapped = max(cl_swapped)
    
    print(f"  Normal:  kraft={kraft_normal:.8f} max_len={max_normal}")
    print(f"  Swapped: kraft={kraft_swapped:.8f} max_len={max_swapped}")
    
    # Show the bytes around the key symbol range (sym 90-130 = bytes 45-65)
    print("  Bytes 45-65 (sym 90-130):")
    for byte_idx in range(45, 66):
        b = ea[byte_idx]
        sym_even = byte_idx * 2
        sym_odd = byte_idx * 2 + 1
        cl_even_norm = b & 0xF
        cl_odd_norm = (b >> 4) & 0xF
        cl_even_swap = (b >> 4) & 0xF
        cl_odd_swap = b & 0xF
        print(f"    byte[{byte_idx:3d}]=0x{b:02X}: sym{sym_even:3d} norm_cl={cl_even_norm} swap_cl={cl_even_swap} | sym{sym_odd:3d} norm_cl={cl_odd_norm} swap_cl={cl_odd_swap}")
    
    # With swapped nibbles, what's the cl=max_len group?
    cl15_swapped = sorted(sym for sym in range(256) if cl_swapped[sym] == max_swapped)
    cl15_normal = sorted(sym for sym in range(256) if cl_normal[sym] == max_normal)
    print(f"  Normal cl=max_len ({max_normal}) symbols: {cl15_normal[:25]}...")
    print(f"  Swapped cl=max_len ({max_swapped}) symbols: {cl15_swapped[:25]}...")
    
    # Check specific symbols involved in substitutions
    key_syms = [63, 64, 66, 94, 96, 97, 98, 125, 126, 127, 128]
    print("\n  Key symbols (normal vs swapped nibble):")
    for sym in key_syms:
        b = ea[sym // 2]
        cl_n = b & 0xF if sym % 2 == 0 else (b >> 4) & 0xF
        cl_s = (b >> 4) & 0xF if sym % 2 == 0 else b & 0xF
        diff = " SAME" if cl_n == cl_s else f" DIFF ({cl_n}→{cl_s})"
        char = chr(sym-2) if 32 <= sym-2 <= 126 else hex(sym-2)
        print(f"    sym={sym:3d} char={char!r:>4} byte[{sym//2}]=0x{b:02X} normal_cl={cl_n} swapped_cl={cl_s}{diff}")
