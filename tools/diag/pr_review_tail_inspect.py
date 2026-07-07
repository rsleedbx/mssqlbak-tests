"""Inspect raw _split_v4_record buffers for TAIL_OVER handles.

Captures the raw `r` bytes for the Format-A (d0>=0x80) TAIL_OVER cases
and attempts to walk the chunk structure so we can understand where each
chunk boundary lies and how many real chars vs garbage are in the buffer.
"""
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

# Capture raw buffers for python-fallback, non-escape records
CAPTURED: list[tuple[bytes, str]] = []  # (r, best_gt)
orig_split = dv._split_v4_record


def best_gt_match(got: str) -> "tuple[str | None, int]":
    best_gt = None
    best_len = -1
    for gt_s in gt_unique:
        cl = sum(1 for a, b in zip(got, gt_s) if a == b) if got[0:1] == gt_s[0:1] else 0
        # fast prefix check
        mn = min(len(got), len(gt_s))
        cl = 0
        for i in range(mn):
            if got[i] == gt_s[i]:
                cl += 1
            else:
                break
        if cl > best_len:
            best_len = cl
            best_gt = gt_s
    return best_gt, best_len


def patched_split(r: bytes, *, from_python_fallback: bool = False, is_escape: bool = False):
    result = orig_split(r, from_python_fallback=from_python_fallback, is_escape=is_escape)
    if from_python_fallback and not is_escape and r:
        d0 = r[0] - off
        if d0 >= 0x80:
            # Only capture Format A (multi-chunk) handles
            for v in result:
                if isinstance(v, str) and v:
                    CAPTURED.append((bytes(r), v))
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

# Find TAIL_OVER captures that are still wrong
tail_over_captures: list[tuple[bytes, str, str]] = []
for r, got in CAPTURED:
    if got not in got_only:
        continue
    best_gt, cl = best_gt_match(got)
    if best_gt and cl == len(best_gt):
        tail_over_captures.append((r, got, best_gt))

print(f"Format-A TAIL_OVER captures: {len(tail_over_captures)}")
print()


def walk_chunks(r: bytes, glen: int) -> None:
    """Walk the buffer as a sequence of chunks and annotate each boundary."""
    pos = 0
    chunk = 0
    total_chars = 0
    while pos < len(r):
        if pos + 1 >= len(r):
            print(f"  [eof at pos={pos}]")
            break
        d0 = r[pos] - off
        d1 = r[pos + 1] - off
        marker = " ←REAL" if total_chars < glen else " ←GARBAGE"
        if d0 >= 0x80 and d1 >= 0x80:
            clen = d0
            content_end = pos + 2 + clen
            snip = r[pos + 2 : pos + 2 + min(clen, 30)]
            snip_str = snip.decode("latin-1", errors="replace")
            print(
                f"  chunk {chunk}: 2-hdr d0={d0} d1={d1} "
                f"clen={clen} pos={pos}..{content_end}  "
                f"'{snip_str[:20]}...'{marker}"
            )
            total_chars += clen
            pos = content_end
        elif d0 >= 0x80 and d1 < 0x80:
            # slen=d0, next byte is d1 (possible next chunk header or end)
            clen = d0
            content_end = pos + 1 + clen
            snip = r[pos + 1 : pos + 1 + min(clen, 30)]
            snip_str = snip.decode("latin-1", errors="replace")
            print(
                f"  chunk {chunk}: 1-hdr d0={d0} d1={d1} "
                f"clen={clen} pos={pos}..{content_end}  "
                f"'{snip_str[:20]}...'{marker}"
            )
            total_chars += clen
            pos = content_end
        else:
            # Small slen
            clen = d0
            if clen < 0:
                print(f"  [neg slen={clen} at pos={pos}]")
                break
            content_end = pos + 1 + clen
            snip = r[pos + 1 : pos + 1 + min(clen, 30)]
            snip_str = snip.decode("latin-1", errors="replace")
            print(
                f"  chunk {chunk}: 1-hdr d0={d0} clen={clen} "
                f"pos={pos}..{content_end}  "
                f"'{snip_str[:20]}...'{marker}"
            )
            total_chars += clen
            pos = content_end
        chunk += 1
        if pos > len(r):
            print(f"  [overflow pos={pos} > len={len(r)}]")
            break
        if chunk > 30:
            print(f"  [truncated after 30 chunks, pos={pos}]")
            break
    print(f"  → total walked chars={total_chars}, glen={glen}, len(r)={len(r)}")


for i, (r, got, gt_str) in enumerate(tail_over_captures):
    d0 = r[0] - off
    d1 = r[1] - off if len(r) >= 2 else -1
    print(f"=== [{i}] glen={len(gt_str)} rlen={len(r)} d0={d0} d1={d1} ===")
    print(f"  gt[:60]:  {repr(gt_str[:60])}")
    print(f"  got[:60]: {repr(got[:60])}")
    walk_chunks(r, len(gt_str))
    print()
