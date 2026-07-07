#!/usr/bin/env python3
"""For every preamble sig in a cached segment, measure the block size by finding
where a valid log-record chain resumes (512-aligned search), and report the
distribution.  Confirms whether block size is variable and detectable.

Usage:
    python -m tools.diag._diag_xtp_ckpt_blocksize --bin /tmp/aw_xtp.bin
"""
from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.xtp import (  # noqa: E402
    _CKPT_PREAMBLE_SIG,
    _LOG_HEADER_SIZE,
    _validate_log_header,
)

_U32 = struct.Struct("<I")


def _chain_len(seg: bytes, off: int, n: int, limit: int = 4) -> int:
    walk = off
    count = 0
    while count < limit and walk + _LOG_HEADER_SIZE <= n:
        hv = _validate_log_header(seg[walk : walk + _LOG_HEADER_SIZE])
        if hv is None:
            break
        size, _lb = hv
        walk += _LOG_HEADER_SIZE + size
        count += 1
    return count


def main(bin_path: Path) -> None:
    seg = bin_path.read_bytes()
    n = len(seg)
    pos = 0
    block_hist: Counter[int] = Counter()
    resume_align: Counter[int] = Counter()
    pre_align: Counter[int] = Counter()
    unresolved = 0
    total = 0
    while True:
        p = seg.find(_CKPT_PREAMBLE_SIG, pos)
        if p < 0:
            break
        total += 1
        pos = p + 1
        pre_align[p % 512] += 1
        # find first 512-aligned offset E in (p, p+16384] where a >=3 chain starts
        resolved = False
        for k in range(512, 16384 + 1, 512):
            E = p + k
            if E + _LOG_HEADER_SIZE > n:
                break
            if _chain_len(seg, E, n, limit=4) >= 3:
                block_hist[k] += 1
                resume_align[E % 512] += 1
                resolved = True
                break
        if not resolved:
            unresolved += 1
    print(f"preambles: {total}")
    print(f"preamble %512 alignment: {dict(pre_align)}")
    print(f"block-size histogram (resume - preamble, 512-aligned chain): "
          f"{dict(sorted(block_hist.items()))}")
    print(f"resume %512 alignment: {dict(resume_align)}")
    print(f"unresolved (no chain within 16KB): {unresolved}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", type=Path, required=True)
    args = ap.parse_args()
    main(args.bin)
