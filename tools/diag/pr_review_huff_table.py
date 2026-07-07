"""Examine the Huffman table for the tpcxbb pr_review_content underfull page."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
from mssqlbak.columnstore.decode.dict_xvelocity import (
    _build_huff_table,
    _V4_CHAR_OFFSET,
)
import mssqlbak.columnstore.decode.dict_xvelocity as dv
from mssqlbak.pages import PageStore

# Hook _build_huff_table to capture the FIRST underfull page's encode_array.
captured_arrays: list = []
orig_build = _build_huff_table


call_count = [0]

def hooked_build(encode_array_128):
    tab, ml, esc_start = orig_build(encode_array_128)
    call_count[0] += 1
    if tab is not None and ml > 0:
        # Compute Kraft sum to check underfull
        code_lens = []
        for i in range(256):
            b = encode_array_128[i // 2]
            code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        kraft = sum(2**(-cl) for cl in code_lens if cl > 0)
        if call_count[0] <= 5:
            print(f"  _build_huff_table call #{call_count[0]}: kraft={kraft:.8f} ml={ml}")
        if kraft < 1.0 - 1e-6:  # underfull
            captured_arrays.append((bytes(encode_array_128), kraft, ml))
    return tab, ml, esc_start


dv._build_huff_table = hooked_build

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")
store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")

# Read a few rows to trigger dictionary decode
for i, _ in enumerate(read_columnstore_rows(store, tbl)):
    if captured_arrays:
        break
    if i > 5000:
        break

dv._build_huff_table = orig_build

if not captured_arrays:
    print("ERROR: No underfull page captured")
    sys.exit(1)

encode_array, kraft, max_len = captured_arrays[0]
print(f"Captured underfull page: Kraft sum={kraft:.8f}, max_len={max_len}")

# Parse the code lengths
code_lens: list[int] = []
for i in range(256):
    b = encode_array[i // 2]
    code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)

# Count entries by code length
cl_counter = Counter(cl for cl in code_lens if cl > 0)
print(f"Code length distribution (non-zero): {sorted(cl_counter.items())}")
print(f"Symbols with cl=0: {sum(1 for cl in code_lens if cl == 0)}")
print(f"Max code len: {max_len}")

# Build canonical code assignment
code = 0
sym_to_code: dict[int, tuple[int, int]] = {}
by_len: dict[int, list[int]] = {}
for sym, cl in enumerate(code_lens):
    if cl > 0:
        by_len.setdefault(cl, []).append(sym)

for cl in range(1, max_len + 1):
    for sym in sorted(by_len.get(cl, [])):
        sym_to_code[sym] = (cl, code)
        code += 1
    code <<= 1

off = _V4_CHAR_OFFSET

# Show the substitutions
print("\n=== Substitution symbol analysis ===")
print("(got_char → want_char: Huffman code info, table index delta)\n")

substitutions = [
    # (wrong_decoded_char, correct_decoded_char)
    ('|', '`'),    # raw 126 → 98
    ('}', '`'),    # raw 127 → 98
    ('{', '_'),    # raw 125 → 97
    ('>', '+'),    # raw 64 → 45
    ('=', '%'),    # raw 63 → 39
    ('@', '='),    # raw 66 → 63
    ('^', '>'),    # raw 96 → 64
    ('\x86', '~'), # raw 136 → 128
    ('\x81', '~'), # raw 131 → 128
    ('`', '@'),    # raw 98 → 66  (reversed)
    ('~', '{'),    # raw 128 → 125
    ('\x80', '}'), # raw 130 → 127
    ('\x7f', '}'), # raw 129 → 127
    ('}', '{'),    # raw 127 → 125
]

for got_ch, want_ch in substitutions:
    got_sym = ord(got_ch) + off
    want_sym = ord(want_ch) + off
    got_info = sym_to_code.get(got_sym)
    want_info = sym_to_code.get(want_sym)
    g_repr = repr(got_ch) if 32 <= ord(got_ch) < 127 else f"\\x{ord(got_ch):02x}"
    w_repr = repr(want_ch) if 32 <= ord(want_ch) < 127 else f"\\x{ord(want_ch):02x}"
    if got_info and want_info:
        gcl, gc = got_info
        wcl, wc = want_info
        # Table start index for each symbol in the max_len table
        g_tbl = gc << (max_len - gcl)
        w_tbl = wc << (max_len - wcl)
        print(
            f"  {g_repr}(sym={got_sym:3d}) cl={gcl:2d} code={gc:6d}  →  "
            f"{w_repr}(sym={want_sym:3d}) cl={wcl:2d} code={wc:6d}  "
            f"Δcode={g_tbl-w_tbl:+6d}"
        )
    else:
        print(
            f"  {g_repr}(sym={got_sym:3d}) {got_info}  →  {w_repr}(sym={want_sym:3d}) {want_info}"
        )

# Also show all symbols in code-length order around the interesting ones
print("\n=== Symbols around the substitution pairs (sorted by code) ===")

interesting_syms = set()
for got_ch, want_ch in substitutions:
    interesting_syms.add(ord(got_ch) + off)
    interesting_syms.add(ord(want_ch) + off)

# Sort by (cl, code)
sorted_syms = sorted(sym_to_code.items(), key=lambda x: (x[1][0], x[1][1]))
for sym, (cl, c) in sorted_syms:
    ch = chr(sym - off)
    ch_repr = repr(ch) if 32 <= ord(ch) < 127 else f"\\x{ord(ch):02x}"
    if sym in interesting_syms:
        marker = " <<<< SUBSTITUTION INVOLVED"
    else:
        marker = ""
    # Only show lines near interesting symbols (within 3 positions in the code list)
    # Find neighbors of interesting syms
    pass

# Just show all interesting syms and their neighbors in the table
sorted_syms_list = [(sym, cl, c) for sym, (cl, c) in sorted_syms]
for i, (sym, cl, c) in enumerate(sorted_syms_list):
    if sym in interesting_syms:
        # Show a window around this symbol
        for j in range(max(0, i-2), min(len(sorted_syms_list), i+4)):
            s2, cl2, c2 = sorted_syms_list[j]
            ch2 = chr(s2 - off)
            ch2_repr = repr(ch2) if 32 <= ord(ch2) < 127 else f"\\x{ord(ch2):02x}"
            marker = " <<<" if s2 in interesting_syms else ""
            print(f"  sym={s2:3d} {ch2_repr:6s} cl={cl2:2d} code={c2:6d}  (tbl={c2<<(max_len-cl2):6d}){marker}")
        print("  ---")
