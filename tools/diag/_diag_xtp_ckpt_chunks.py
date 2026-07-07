#!/usr/bin/env python3
"""Inspect the raw decompressed-chunk structure of the straddle fixture:
chunk sizes, first bytes, and where preamble signatures fall relative to chunk
boundaries.  Distinguishes "segment header inside a chunk" from "chunk boundary".

Usage:
    python -m tools.diag._diag_xtp_ckpt_chunks [--bak PATH]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.compressed import (  # noqa: E402
    iter_decompressed_chunks as _iter_dc,
    _OFF_HEADER_VERSION,
    _HEADER_VERSION,
)
from mssqlbak.xtp import _PAGE_MTYPE_MAX, _CKPT_PREAMBLE_SIG  # noqa: E402

_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"


def _is_page(ch: bytes) -> bool:
    return (
        len(ch) >= 96
        and ch[_OFF_HEADER_VERSION] == _HEADER_VERSION
        and 1 <= ch[1] <= _PAGE_MTYPE_MAX
    )


def main(bak_path: Path) -> None:
    bak_bytes = bak_path.read_bytes()
    chunks = list(_iter_dc(bak_bytes))
    print(f"total decompressed chunks: {len(chunks)}")
    size_hist = Counter(len(c) for c in chunks)
    print(f"chunk-size histogram (top 8): {size_hist.most_common(8)}")

    # Among non-page chunks, how many begin with the preamble sig?
    nonpage = [c for c in chunks if not _is_page(c)]
    page = [c for c in chunks if _is_page(c)]
    print(f"non-page chunks: {len(nonpage)}  page chunks: {len(page)}")
    starts_with_pre = sum(1 for c in nonpage if c.startswith(_CKPT_PREAMBLE_SIG))
    print(f"non-page chunks starting with preamble sig: {starts_with_pre}")

    # For non-page chunks: distribution of first 2 bytes
    b01 = Counter((c[0], c[1]) for c in nonpage if len(c) >= 2)
    print(f"non-page first-2-byte histogram (top 8): {b01.most_common(8)}")

    # Walk the concatenated non-page segment; for each preamble sig, report its
    # offset relative to the START of the chunk it falls in.
    print("\n--- preamble sig positions relative to chunk boundaries ---")
    seg_parts: list[tuple[int, int]] = []  # (abs_start, chunk_len) for non-page
    running = 0
    concat = bytearray()
    for c in chunks:
        if _is_page(c):
            continue
        seg_parts.append((running, len(c)))
        concat += c
        running += len(c)
    concat_b = bytes(concat)

    def chunk_of(off: int) -> tuple[int, int]:
        for ci, (start, ln) in enumerate(seg_parts):
            if start <= off < start + ln:
                return ci, off - start
        return -1, -1

    pos = 0
    count = 0
    rel_hist: Counter[int] = Counter()
    while True:
        p = concat_b.find(_CKPT_PREAMBLE_SIG, pos)
        if p < 0:
            break
        ci, rel = chunk_of(p)
        rel_hist[rel] += 1
        if count < 20:
            print(f"  preamble @concat {p}: chunk#{ci} chunk_off={rel} "
                  f"(chunk_len={seg_parts[ci][1] if ci >= 0 else '?'})")
        count += 1
        pos = p + 1
    print(f"\ntotal preamble sigs in non-page segment: {count}")
    print(f"chunk-offset histogram of preamble sigs (top 8): {rel_hist.most_common(8)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    args = ap.parse_args()
    main(args.bak)
