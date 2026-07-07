"""Check all unique encode_arrays used across all underfull pages.

For each unique encode_array, show code_lens for sym 126 (which should be 0 for the
main underfull tree, but might differ for pages that share a different encode_array).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import mssqlbak.columnstore.decode.dict_xvelocity as dv
from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")

unique_eas: dict[bytes, list] = {}  # ea -> list of (kraft, max_len)
orig_build = dv._build_huff_table


def hooked_build(encode_array_128):
    tab, ml, esc_start = orig_build(encode_array_128)
    if tab is not None and ml > 0:
        code_lens = []
        for i in range(256):
            b = encode_array_128[i // 2]
            code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
        kraft = sum(2**(-cl) for cl in code_lens if cl > 0)
        if kraft < 1.0 - 1e-6:  # underfull
            key = bytes(encode_array_128)
            if key not in unique_eas:
                unique_eas[key] = []
            unique_eas[key].append((kraft, ml))
    return tab, ml, esc_start


dv._build_huff_table = hooked_build

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")

# Process enough rows to trigger all dictionary decodes
row_count = 0
for row in read_columnstore_rows(store, tbl):
    row_count += 1
    # After 10k rows, all global dicts should be decoded
    if row_count >= 10000:
        break

dv._build_huff_table = orig_build

print(f"Processed {row_count} rows")
print(f"Unique underfull encode_arrays found: {len(unique_eas)}\n")

off = dv._V4_CHAR_OFFSET

for ea_bytes, instances in unique_eas.items():
    kraft, ml = instances[0]
    code_lens = []
    for i in range(256):
        b = ea_bytes[i // 2]
        code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)

    # Show code lengths for interesting symbols (around sym 126)
    print(f"Encode array (first 8 bytes): {ea_bytes[:8].hex()}")
    print(f"  kraft={kraft:.8f} ml={ml} used_by {len(instances)} pages")
    for sym in [93, 95, 96, 97, 98, 124, 125, 126, 127, 128, 129, 130, 131]:
        cl = code_lens[sym]
        ch = chr(sym - off) if 32 <= sym - off < 128 else f"\\x{sym-off:02x}"
        marker = " <-- sym 126 has cl>0!" if sym == 126 and cl > 0 else ""
        if cl > 0 or sym in (126, 98, 125, 127, 128):
            print(f"    sym={sym:3d} ({ch:4s}) cl={cl}{marker}")
    print()
