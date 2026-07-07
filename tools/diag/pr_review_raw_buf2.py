"""Capture the exact raw buffer bytes for a specific got-only string.

We patch _split_v4_record to grab `r` bytes, then exit early.
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

TARGET_PREFIX = "An excellent work on one town's experience"

captured = {}
orig_split = dv._split_v4_record
off = dv._V4_CHAR_OFFSET


def patched_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and not captured:
        for v in result:
            if v.startswith(TARGET_PREFIX):
                captured['v'] = v
                captured['r'] = bytes(r)
                captured['esc'] = is_escape
    return result


dv._split_v4_record = patched_split
try:
    _reader_mod._split_v4_record = patched_split  # type: ignore[attr-defined]
except AttributeError:
    pass

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")

# Read row-by-row, stop once captured
for row in read_columnstore_rows(store, tbl):
    if captured:
        break

dv._split_v4_record = orig_split
try:
    _reader_mod._split_v4_record = orig_split  # type: ignore[attr-defined]
except AttributeError:
    pass

if not captured:
    print("NOT CAPTURED")
    sys.exit(1)

v = captured['v']
r = captured['r']

print(f"Target string: {repr(v[:80])}")
print(f"r len = {len(r)}, escaped = {captured['esc']}")
print(f"r[0]=0x{r[0]:02x} r[1]=0x{r[1]:02x}")
print(f"decoded0 = r[0]-2 = {r[0]-off}")
print(f"d1 = r[1]-2 = {r[1]-off}")
print()

# Find divergence from GT
# GT string: "An excellent work on one town's experience in the individual. ..."
# Manually known correct string (use a reference)
# From divergence analysis: cl=118, got '|', want '`'
# r[120] = byte at divergence

print("Bytes around divergence position 118 in decoded string:")
print("(r[i+2] for i in range(113, 135)):")
for i in range(113, 135):
    ri = i + 2  # r index = decoded index + 2 (overhead)
    if ri < len(r):
        b = r[ri]
        decoded = chr(b - off) if b - off >= 32 and b - off < 128 else repr(chr(b - off))
        print(f"  r[{ri}] = 0x{b:02x} = {b:3d}  decoded: {decoded}")
    else:
        print(f"  r[{ri}] = OUT OF RANGE (len={len(r)})")

print()
print("The full decoded string (v):")
print(f"  v[110:140] = {repr(v[110:140])}")
print()
print("Checking if '|' is char(124) which needs raw byte 126:")
for i, c in enumerate(v):
    if c == '|':
        ri = i + 2
        print(f"  v[{i}] = '|', r[{ri}] = 0x{r[ri]:02x} = {r[ri]}")
        break
