"""Test: ascending sort for all code lengths EXCEPT cl=max_len, which uses descending.

The analysis shows that for underfull pages, the character substitutions involve
symbols at the highest code length (cl=max_len=15). The ascending sort gives:
  sym A (lower value) → lower code
  sym B (higher value) → higher code

But SQL Server seems to put HIGHER-valued symbols at LOWER codes within the cl=15 group.
This is consistent with DESCENDING sort for cl=max_len only.

Test this by modifying _build_huff_table to use descending sort only for the
max-len group and compare against baseline ascending.
"""
import sys
import array
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

def _build_huff_table_maxlen_desc(encode_array_128: bytes):
    """Like _build_huff_table but sorts descending ONLY for the cl=max_len group."""
    code_lens: list[int] = []
    for i in range(256):
        b = encode_array_128[i // 2]
        code_lens.append(b & 0xF if i % 2 == 0 else (b >> 4) & 0xF)

    max_len = max(code_lens)
    if max_len == 0:
        return None, 0

    by_len: dict[int, list[int]] = {}
    for sym, cl in enumerate(code_lens):
        if cl > 0:
            by_len.setdefault(cl, []).append(sym)

    code = 0
    sym_to_code: dict[int, tuple[int, int]] = {}
    for cl in range(1, max_len + 1):
        # Ascending for all groups except max_len
        syms = sorted(by_len.get(cl, []), reverse=(cl == max_len))
        for sym in syms:
            sym_to_code[sym] = (cl, code)
            code += 1
        code <<= 1

    tab: array.array = array.array("H", [0] * (1 << max_len))
    tab_sz = len(tab)
    for sym, (cl, code2) in sym_to_code.items():
        prefix = code2 << (max_len - cl)
        count = 1 << (max_len - cl)
        if prefix + count > tab_sz:
            return None, 0
        entry = (sym << 8) | cl
        for j in range(prefix, prefix + count):
            tab[j] = entry

    return tab, max_len


orig_build = dv._build_huff_table
dv._build_huff_table = _build_huff_table_maxlen_desc

store = PageStore.from_bak(bak_path)
schema = recover_schema(store)
tbl = next(t for t in schema.tables if t.name.lower() == "product_reviews")
rows = list(read_columnstore_rows(store, tbl))

dv._build_huff_table = orig_build

got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")
got_only = sorted(got_unique - gt_unique)
want_only = sorted(gt_unique - got_unique)
correct = gt_unique & got_unique

print(f"MAX-LEN-ONLY DESCENDING: correct={len(correct)}, got_only={len(got_only)}, want_only={len(want_only)}")
print(f"Delta vs ascending baseline: correct {len(correct)-83049:+d}, got_only {len(got_only)-76:+d}, want_only {len(want_only)-90:+d}")
