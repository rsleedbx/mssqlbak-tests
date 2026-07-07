"""Bucket A diagnostic: hex-dump raw r[] bytes for every escape handle
on EA bde8b0ed / b48c5b50 that produces a got_only string.

Prints for each:
  - EA key and n_unused
  - r[] in hex
  - byte-by-byte decode: sym, chr(sym-2), and whether it matches gt
  - got string vs best-matching gt string (suffix-based fast lookup)
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

# ── hooking ─────────────────────────────────────────────────────────────────

current_ea_key: list[str] = []
current_ea_bytes: list[bytes] = []

EA_INFO: dict[str, dict] = {}


def _ea_info(ea: bytes) -> dict:
    cl = []
    for i in range(256):
        b = ea[i // 2]
        cl.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)
    max_len = max(cl)
    n_max = sum(1 for c in cl if c == max_len)
    code = 0
    by_len: dict[int, list[int]] = {}
    for sym, c in enumerate(cl):
        if c > 0:
            by_len.setdefault(c, []).append(sym)
    for c in range(1, max_len):
        code += len(by_len.get(c, []))
        code <<= 1
    n_available = (1 << max_len) - code
    return {"max_len": max_len, "n_max": n_max, "n_available": n_available,
            "unused": n_available - n_max}


def hooked_build(encode_array_128: bytes):
    tab, ml, esc_start = orig_build(encode_array_128)
    ea = bytes(encode_array_128)
    key = hashlib.md5(ea).hexdigest()[:8]
    current_ea_key.clear()
    current_ea_key.append(key)
    current_ea_bytes.clear()
    current_ea_bytes.append(ea)
    if key not in EA_INFO:
        EA_INFO[key] = _ea_info(ea)
    return tab, ml, esc_start


# Map raw r bytes → (ea_key, is_escape)
R_TO_INFO: dict[bytes, tuple[str, bool]] = {}


def hooked_huff(bitstream, cbuf_off, table, max_len, bos, stb):
    result = orig_huff(bitstream, cbuf_off, table, max_len, bos, stb)
    if result is not None and current_ea_key:
        key = current_ea_key[0]
        results, esc_indices = result
        for i, r in enumerate(results):
            R_TO_INFO[bytes(r)] = (key, i in esc_indices)
    return result


# Map got value → r bytes (only for fallback escapes)
VALUE_TO_R: dict[str, bytes] = {}


def hooked_split(r, *, from_python_fallback=False, is_escape=False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and is_escape:
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

gt_list = list(gt_unique)

print(f"got_only total: {len(got_only)}")
print(f"escape got_only captured: {len(VALUE_TO_R)}")
print()

TARGET_EAS = {"bde8b0ed", "b48c5b50"}


def best_gt_match(got: str, gt_list: list[str]) -> str:
    """Find gt string sharing the longest suffix with got."""
    # Use a long tail of the got string (past any prefix divergence)
    tail = got[3:] if len(got) > 3 else got
    candidates = [g for g in gt_list if tail in g]
    if candidates:
        # Prefer same length, then longest common overlap
        same_len = [g for g in candidates if len(g) == len(got)]
        return same_len[0] if same_len else candidates[0]
    # Short tail fallback
    tail20 = got[-20:] if len(got) >= 20 else got
    candidates = [g for g in gt_list if tail20 in g]
    return candidates[0] if candidates else ""


for v in sorted(got_only):
    r = VALUE_TO_R.get(v)
    if r is None:
        continue
    info = R_TO_INFO.get(r)
    if info is None:
        continue
    ea_key, is_esc = info
    if ea_key not in TARGET_EAS:
        continue

    ea_inf = EA_INFO.get(ea_key, {})
    gt_match = best_gt_match(v, gt_list)

    print(f"EA={ea_key}  unused={ea_inf.get('unused','?')}  is_escape={is_esc}")
    print(f"  got ({len(v):3d} chars): {repr(v[:80])}")
    print(f"  gt  ({len(gt_match):3d} chars): {repr(gt_match[:80])}")
    print(f"  r len={len(r)}")

    # Hex dump of r with per-byte decode
    print("  hex dump:")
    for i, b in enumerate(r):
        sym = b
        ch = chr(sym - off) if 0x20 <= sym - off <= 0x7E else "·"
        # Is this byte the first content byte position?
        marker = ""
        if i == 0:
            marker = " ← r[0] (overhead/length?)"
        elif i == 1:
            marker = " ← r[1] (first content byte in current is_escape path)"
        print(f"    r[{i:2d}] = 0x{b:02X}  sym={b:3d}  chr(sym-{off})={repr(ch)}{marker}")

    # Find where got vs gt first diverges
    gt_stripped = gt_match  # full gt
    diverge = -1
    for i, (gc, gtc) in enumerate(zip(v, gt_stripped)):
        if gc != gtc:
            diverge = i
            break
    if diverge >= 0:
        print(f"  first divergence at pos {diverge}:"
              f" got={repr(v[diverge])} gt={repr(gt_stripped[diverge])}")
        # Estimate r-byte index for this position
        # In current escape path: decode_payload(r[1:]) = r[1],r[2],...
        # So content position i maps to r[1+i]
        r_idx_b = 1 + diverge
        r_idx_a = 0 + diverge  # alternative: content starts at r[0]
        if r_idx_b < len(r):
            b_b = r[r_idx_b]
            print(f"    if content@r[1:] → r[{r_idx_b}]=0x{b_b:02X}  chr(sym-{off})={chr(b_b-off)!r}")
        if r_idx_a < len(r):
            b_a = r[r_idx_a]
            print(f"    if content@r[0:] → r[{r_idx_a}]=0x{b_a:02X}  chr(sym-{off})={chr(b_a-off)!r}")
        expected_sym = ord(gt_stripped[diverge]) + off
        print(f"    expected sym for gt[{diverge}]={repr(gt_stripped[diverge])}: {expected_sym} = 0x{expected_sym:02X}")
    print()
