"""Capture the raw buffer `r` for a few got-only strings to see exact bytes.

We look at got-only strings that have '|' or '}' → '`' substitutions
to verify where those bytes come from in `r`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq
import mssqlbak.columnstore.decode.dict_xvelocity as dv2
from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
from mssqlbak.columnstore.decode import dict_xvelocity as dv
import mssqlbak.columnstore.assembly.reader as _reader_mod

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")
gt_path = Path(
    "tests/fixtures_realworld/tpcxbb_1gb.bak.cells/dbo.product_reviews.parquet"
)

gt = pq.read_table(gt_path, columns=["pr_review_content"])
gt_unique = set(v.as_py() for v in gt.column("pr_review_content") if v.as_py() is not None)

off = dv._V4_CHAR_OFFSET

# Target got-only strings to inspect (first 60 chars as key)
TARGET_PREFIXES = [
    "An excellent work on one town's experience",   # [8]
    "Awesome Preview of Europe for those of us",    # [12]
    "It's been almost year isn't",                  # [27]
    "from the If",                                  # [67]
    "Chrono Cross Time",                            # [16]
]

VALUE_BUF: dict = {}  # value_prefix → (full_value, r_bytes, from_py, is_esc)

orig_split = dv._split_v4_record


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and r:
        for v in result:
            for pfx in TARGET_PREFIXES:
                if v.startswith(pfx) and pfx not in VALUE_BUF:
                    VALUE_BUF[pfx] = (v, bytes(r), from_python_fallback, is_escape)
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

got_unique = set(row.get("pr_review_content") for row in rows if row.get("pr_review_content"))
got_only = got_unique - gt_unique

print(f"Got-only: {len(got_only)}\n")

for pfx in TARGET_PREFIXES:
    if pfx not in VALUE_BUF:
        print(f"NOT CAPTURED: {pfx[:40]}")
        continue

    v, r, fb, esc = VALUE_BUF[pfx]
    is_got_only = v in got_only
    print(f"=== {pfx[:40]} ===")
    print(f"  got_only={is_got_only}, fb={fb}, esc={esc}, len(r)={len(r)}")
    print(f"  v[:120]: {repr(v[:120])}")

    # Find first char position where v differs from GT (find best GT match)
    best_gt = None
    best_cl = -1
    for gt_s in gt_unique:
        cl = 0
        for a, b in zip(v, gt_s):
            if a == b:
                cl += 1
            else:
                break
        if cl > best_cl:
            best_cl = cl
            best_gt = gt_s

    if best_gt:
        print(f"  best GT match: cl={best_cl}, gt_len={len(best_gt)}")
        if best_cl < len(v) and best_cl < len(best_gt):
            print(f"  diverge pos {best_cl}: got='{v[best_cl]}' (ord={ord(v[best_cl])}) "
                  f"want='{best_gt[best_cl]}' (ord={ord(best_gt[best_cl])})")
            # Show the raw buffer bytes around the divergence
            # r is the decoded buf (post-Huffman), v = _decode_payload(r[2:])
            # so v[i] = chr(r[i+2] - 2)  →  r[i+2] = ord(v[i]) + 2
            div_r_pos = best_cl + 2  # position in r (adding 2 for overhead)
            print(f"  r[{div_r_pos-3}:{div_r_pos+5}] raw bytes: "
                  f"{' '.join(f'0x{b:02x}' for b in r[max(0,div_r_pos-3):div_r_pos+5])}")
            print(f"  decoded chars at those positions: "
                  f"{repr(''.join(chr(b-2) for b in r[max(0,div_r_pos-3):div_r_pos+5]))}")
            # Check: what does r[div_r_pos] decode to?
            b = r[div_r_pos]
            print(f"  r[{div_r_pos}] = 0x{b:02x} = {b} → decoded chr = '{chr(b-2)}' "
                  f"(ord={ord(chr(b-2))})")
            # What symbol is this in the Huffman context?
            print(f"  As Huffman symbol: sym={b} → chr(sym-2)='{chr(b-2)}'")
    print()

# Also show the Huffman table entries for the interesting symbols
captured_ea: list[bytes | None] = [None]
orig_build = dv2._build_huff_table


def hook_build(ea):
    tab, ml, esc_start = orig_build(ea)
    if tab is not None and ml > 0:
        code_lens2 = []
        for i in range(256):
            b2 = ea[i // 2]
            code_lens2.append(b2 & 0xF if i % 2 == 0 else (b2 >> 4) & 0xF)
        kraft = sum(2**(-cl) for cl in code_lens2 if cl > 0)
        if kraft < 0.9999:
            if captured_ea[0] is None:
                captured_ea[0] = bytes(ea)
    return tab, ml, esc_start


dv2._build_huff_table = hook_build
# Re-run briefly to capture encode_array
store2 = PageStore.from_bak(bak_path)
schema2 = recover_schema(store2)
tbl2 = next(t for t in schema2.tables if t.name.lower() == "product_reviews")
for _ in read_columnstore_rows(store2, tbl2):
    if captured_ea[0]:
        break
dv2._build_huff_table = orig_build

if captured_ea[0]:
    ea = captured_ea[0]
    code_lens = []
    for i in range(256):
        b2 = ea[i // 2]
        code_lens.append(b2 & 0xF if i % 2 == 0 else (b2 >> 4) & 0xF)

    print("\n=== Code lengths for relevant symbols ===")
    for sym in [94, 95, 96, 97, 98, 99, 124, 125, 126, 127, 128, 129, 130, 131, 136]:
        cl = code_lens[sym]
        ch = chr(sym - off) if 32 <= sym - off < 128 else f"\\x{sym-off:02x}"
        print(f"  sym={sym:3d} ({ch}) cl={cl}")
