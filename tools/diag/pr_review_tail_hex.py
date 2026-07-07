"""Hex dump of raw Format-A buffers to find length encoding for 1-hdr cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq
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
gt_vals = [v.as_py() for v in gt.column("pr_review_content")]
gt_unique = set(v for v in gt_vals if v is not None)

off = dv._V4_CHAR_OFFSET
CAPTURES: list[tuple[bytes, str]] = []  # (r, got)
orig_split = dv._split_v4_record


def patched_split(r: bytes, *, from_python_fallback: bool = False, is_escape: bool = False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and not is_escape and r:
        d0 = r[0] - off
        d1 = r[1] - off if len(r) >= 2 else -1
        # Capture 1-hdr Format A (d0 >= 0x80, d1 < 0x80)
        if d0 >= 0x80 and 0 <= d1 < 0x20:
            for v in result:
                if isinstance(v, str) and v:
                    CAPTURES.append((bytes(r), v))
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

got_vals = [row.get("pr_review_content") for row in rows]
got_unique = set(v for v in got_vals if v is not None and v != "")
got_only = sorted(got_unique - gt_unique)

# Only show TAIL_OVER captures (got is wrong)
for r, got in CAPTURES:
    if got not in got_only:
        continue
    d0 = r[0] - off
    d1 = r[1] - off
    # Find GT match
    best_gt = max(gt_unique, key=lambda s: sum(1 for a, b in zip(got, s) if a == b))
    glen = len(best_gt)
    common = sum(1 for a, b in zip(got, best_gt) if a == b)
    if common < glen:
        continue  # not TAIL_OVER
    print(f"glen={glen} rlen={len(r)} d0={d0} d1={d1}")
    print(f"  gt[:50]: {repr(best_gt[:50])}")
    # Print first 32 bytes as hex
    print(f"  r[0:32] hex: {' '.join(f'{b:02X}' for b in r[:32])}")
    # Print raw bytes at the boundary
    boundary = 2 + glen
    print(f"  r[{boundary-4}:{boundary+8}] hex: "
          f"{' '.join(f'{b:02X}' for b in r[boundary-4:boundary+8])}")
    # Check if any 3-byte overhead formula works
    if len(r) >= 3:
        r2 = r[2] - off
        print(f"  r[2]-off={r2} (r[2]=0x{r[2]:02X})")
        # Try: glen = d0 + d1*256 + r2
        print(f"  d0+d1*256={d0+d1*256}  d0+d1*128={d0+d1*128}  d0+r2={d0+r2}")
        print(f"  d0+d1*N formula: glen-d0={glen-d0}, (glen-d0)/d1={((glen-d0)/d1) if d1 else 'inf':.2f}")
    print()
