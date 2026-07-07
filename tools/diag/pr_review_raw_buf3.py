"""Find r buffer with r[0]=0x91, r[1]=0x03 (the An excellent work entry with |).

Also patch _huff_decode_page_py to check if byte 126 is ever appended.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
from mssqlbak.columnstore.decode import dict_xvelocity as dv
import mssqlbak.columnstore.assembly.reader as _reader_mod

bak_path = Path("tests/fixtures_realworld/tpcxbb_1gb.bak")

TARGET_R0 = 0x91
TARGET_R1 = 0x03

captured = {}
orig_split = dv._split_v4_record
off = dv._V4_CHAR_OFFSET

# Patch huff decoder to check for byte 126 in buf
orig_huff = dv._huff_decode_page_py

byte126_count = [0]


def checked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None:
        results, esc = result
        for r in results:
            if 126 in r:
                byte126_count[0] += 1
                if byte126_count[0] <= 3:
                    pos = list(r).index(126)
                    print(f"  FOUND byte 126 in huff result at pos {pos}, len={len(r)}, "
                          f"r[0]=0x{r[0]:02x} r[1]=0x{r[1]:02x}")
    return result


dv._huff_decode_page_py = checked_huff


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    if from_python_fallback and r and r[0] == TARGET_R0 and (len(r) < 2 or r[1] == TARGET_R1) and not captured:
        captured['v_before'] = None
        captured['r'] = bytes(r)
        captured['esc'] = is_escape
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and r and r[0] == TARGET_R0 and (len(r) < 2 or r[1] == TARGET_R1) and 'v' not in captured:
        captured['v'] = result[0] if result else ""
    return result


dv._split_v4_record = patched_split
try:
    _reader_mod._split_v4_record = patched_split  # type: ignore[attr-defined]
except AttributeError:
    pass

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")

for row in read_columnstore_rows(store, tbl):
    if captured:
        break

dv._split_v4_record = orig_split
dv._huff_decode_page_py = orig_huff
try:
    _reader_mod._split_v4_record = orig_split  # type: ignore[attr-defined]
except AttributeError:
    pass

print(f"\nbyte 126 found in huff results: {byte126_count[0]} times")

if not captured:
    print("NOT CAPTURED - target r0/r1 not found in first pass")
    sys.exit(0)

r = captured['r']
v = captured.get('v', '')

print("\nTarget buffer captured!")
print(f"r len = {len(r)}, r[0]=0x{r[0]:02x}, r[1]=0x{r[1]:02x}")
print(f"v[:80] = {repr(v[:80] if v else '')}")

# Find all '|' positions in v
pipe_positions = [i for i, c in enumerate(v) if c == '|']
print(f"\n'|' positions in v: {pipe_positions[:10]}")

for pos in pipe_positions[:5]:
    ri = pos + 2
    if ri < len(r):
        print(f"  v[{pos}]='|' → r[{ri}]=0x{r[ri]:02x}={r[ri]}  (sym={r[ri]}, chr={repr(chr(r[ri]-off))})")

# Print full r bytes around the first divergence
if pipe_positions:
    p = pipe_positions[0]
    ri = p + 2
    print(f"\nRaw bytes r[{max(0,ri-5)}:{ri+10}]:")
    for i in range(max(0, ri-5), min(len(r), ri+10)):
        b = r[i]
        print(f"  r[{i}] = 0x{b:02x} = {b:3d}  chr(b-2)={repr(chr(b-off))}")
