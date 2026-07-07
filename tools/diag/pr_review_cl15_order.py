"""Enumerate all cl=15 symbols for the underfull page and determine what
ordering SQL Server uses vs our ascending sort.

We know the bitstream contains the WRONG symbol values for specific positions.
For each known substitution (got_sym, gt_sym), the bitstream has SQL Server's
code for gt_sym, but our table maps that code to got_sym. This tells us that:
  SQL Server's code for gt_sym = our code for got_sym

Equivalently: in SQL Server's canonical ordering, gt_sym is at the position
where our table has got_sym.
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
orig_build = dv._build_huff_table
orig_huff = dv._huff_decode_page_py
orig_split = dv._split_v4_record

# Capture all unique encode arrays seen during decoding
ALL_EAS: dict[bytes, dict] = {}
current_ea: list = []

def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    if ea not in ALL_EAS:
        # Compute code_lens
        code_lens = []
        for i in range(256):
            b = ea[i // 2]
            code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        kraft = sum(2**(-cl) for cl in code_lens if cl > 0)
        max_len = max(code_lens) if any(code_lens) else 0
        ALL_EAS[ea] = {'kraft': kraft, 'max_len': max_len, 'code_lens': code_lens, 'call_count': 0}
    ALL_EAS[ea]['call_count'] += 1
    current_ea.clear()
    current_ea.append(ea)
    return tab, ml, esc_start

# Capture r->ea mapping
R_TO_EA: dict[bytes, bytes] = {}
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

# Identify got_only strings
got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")
got_only = sorted(got_unique - gt_unique)

print(f"Unique encode_arrays seen: {len(ALL_EAS)}")
print(f"got_only: {len(got_only)}\n")

# Known substitution pairs: (got_sym, gt_sym) — bitstream has SQL Server's code for gt_sym,
# our table maps that code to got_sym.
# These all have the same kraft=0.99990845 page.
KNOWN_SUBS = [
    (126, 98),   # got '|' gt '`': bitstream code = our sym=126 code, SQL Server's sym=98 code
    (125, 97),   # got '{' gt '_'
    (63, 39),    # got '=' gt '%'
    (64, 45),    # got '>' gt '+'
    (98, 66),    # got '`' gt '@' (cases 22,59 — might be different page)
    (128, 96),   # got '~' gt '^' ? case 21: got '~' gt '`'... recheck
]

# Recheck case 21 from diverge output:
# [21] got: '1.fw from \x81/.wine/drive_c/Prog', gt: '1.fw from ~/.wine/drive_c/Prog'
# got '\x81' (chr(129)) at position 1200, gt '~' (chr(126))
# sym(\x81) = 131, sym(~) = 128
KNOWN_SUBS_V2 = [
    (126, 98),   # |→`
    (125, 97),   # {→_
    (63, 39),    # =→%
    (64, 45),    # >→+
    (98, 66),    # `→@ (may be different page)
    (131, 128),  # \x81 → ~ (chr(129)→chr(126))
    (96, 94),    # `→^ (case 68: got '`{`', gt '^_^': pos 406 got '`' gt '^')
]

# Find the encode_array used for each substitution
print("=== Substitution → encode_array mapping ===")

sub_eas: dict[tuple, bytes] = {}
for v in got_only:
    r = VALUE_TO_R.get(v)
    if r is None:
        continue
    ea = R_TO_EA.get(r)
    if ea is None:
        continue
    
    # Which substitution does this value exhibit?
    # Check for specific substitution pairs
    for got_sym, gt_sym in KNOWN_SUBS_V2:
        got_c = chr(got_sym - 2)
        gt_c = chr(gt_sym - 2)
        if got_c in v:  # value contains the got char
            key = (got_sym, gt_sym)
            if key not in sub_eas:
                sub_eas[key] = ea
                ea_info = ALL_EAS[ea]
                code_lens = ea_info['code_lens']
                print(f"  got={got_c!r}(sym={got_sym}) gt={gt_c!r}(sym={gt_sym}): "
                      f"kraft={ea_info['kraft']:.8f} max_len={ea_info['max_len']} "
                      f"sym_cl={code_lens[got_sym]},{code_lens[gt_sym]}")

print()

# For each unique encode_array that has substitutions, enumerate all cl=15 symbols
# and determine the SQL Server vs our ordering
processed_eas = set()
for key, ea in sub_eas.items():
    if ea in processed_eas:
        continue
    processed_eas.add(ea)

    ea_info = ALL_EAS[ea]
    code_lens = ea_info['code_lens']
    max_len = ea_info['max_len']
    kraft = ea_info['kraft']
    
    print(f"=== encode_array (kraft={kraft:.8f}, max_len={max_len}) ===")
    
    # Get all cl=max_len symbols sorted ascending
    cl_max_syms = sorted(sym for sym in range(256) if code_lens[sym] == max_len)
    print(f"  cl={max_len} symbols ({len(cl_max_syms)} total): {cl_max_syms}")
    
    # Compute C15_start (starting code for max_len group)
    by_len: dict = {}
    for sym, cl in enumerate(code_lens):
        if cl > 0:
            by_len.setdefault(cl, []).append(sym)
    
    code = 0
    c_start: dict[int, int] = {}
    for cl in range(1, max_len + 1):
        c_start[cl] = code
        for sym in sorted(by_len.get(cl, [])):
            code += 1
        code <<= 1
    
    C_MAX_START = c_start[max_len]
    print(f"  C{max_len}_start = {C_MAX_START}")
    print("  Our ascending order (position = code - C_start):")
    
    # Build position→sym and sym→position for our ordering
    our_order = sorted(cl_max_syms)  # ascending
    our_sym_to_pos = {sym: i for i, sym in enumerate(our_order)}
    
    # Known SQL Server positions (derived from substitutions)
    # Substitution (got_sym, gt_sym) means: bitstream has code for SQL Server's gt_sym
    # which equals our code for got_sym. So SQL Server's position for gt_sym = our position for got_sym.
    sql_pos_known: dict[int, int] = {}  # sym → SQL Server position
    
    for (got_sym, gt_sym) in KNOWN_SUBS_V2:
        if got_sym not in our_sym_to_pos or gt_sym not in our_sym_to_pos:
            continue
        ea_for_sub = sub_eas.get((got_sym, gt_sym))
        if ea_for_sub != ea:
            continue
        # SQL Server's position for gt_sym = our position for got_sym
        sql_pos = our_sym_to_pos[got_sym]
        sql_pos_known[gt_sym] = sql_pos
        print(f"    got_sym={got_sym}('{chr(got_sym-2)}') gt_sym={gt_sym}('{chr(gt_sym-2)}'): "
              f"our_pos(got)={our_sym_to_pos[got_sym]}, "
              f"SQL_Server_pos(gt)={sql_pos}")
    
    print("\n  Comparison: our ascending order vs SQL Server order (known positions):")
    print(f"  {'Pos':>4}  {'Our sym':>8} {'Our char':>9}  {'SQL sym':>8} {'SQL char':>9}")
    
    # Reconstruct SQL order (fill with ??? for unknowns)
    sql_order: list[int | None] = [None] * len(our_order)
    for sym, sql_pos in sql_pos_known.items():
        if sql_pos < len(sql_order):
            sql_order[sql_pos] = sym
    
    for pos, (our_sym) in enumerate(our_order):
        sql_sym = sql_order[pos] if pos < len(sql_order) else None
        our_char = repr(chr(our_sym - 2)) if 32 <= our_sym - 2 <= 126 else hex(our_sym)
        sql_char = repr(chr(sql_sym - 2)) if sql_sym is not None and 32 <= sql_sym - 2 <= 126 else (hex(sql_sym) if sql_sym else '?')
        print(f"  {pos:>4}  {our_sym:>8} {our_char:>9}  {str(sql_sym):>8} {sql_char:>9}")
    print()
