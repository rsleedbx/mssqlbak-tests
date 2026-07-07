#!/usr/bin/env python3
"""Decompress a .bak once and cache the concatenated non-page segments to /tmp
so downstream analysis is fast.  Writes <cache>.bin and a small <cache>.idx with
segment boundaries.

Usage:
    python -m tools.diag._diag_xtp_ckpt_cache --bak PATH --out /tmp/aw_xtp.bin
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.compressed import (  # noqa: E402
    iter_decompressed_chunks as _iter_dc,
    _OFF_HEADER_VERSION,
    _HEADER_VERSION,
)
from mssqlbak.xtp import _PAGE_MTYPE_MAX  # noqa: E402


def main(bak_path: Path, out: Path) -> None:
    bak_bytes = bak_path.read_bytes()
    segs: list[bytes] = []
    cur: list[bytes] = []
    for ch in _iter_dc(bak_bytes):
        is_page = (
            len(ch) >= 96
            and ch[_OFF_HEADER_VERSION] == _HEADER_VERSION
            and 1 <= ch[1] <= _PAGE_MTYPE_MAX
        )
        if is_page:
            if cur:
                segs.append(b"".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        segs.append(b"".join(cur))

    bounds: list[tuple[int, int]] = []
    running = 0
    with out.open("wb") as f:
        for s in segs:
            bounds.append((running, len(s)))
            f.write(s)
            running += len(s)
    out.with_suffix(".idx").write_text(json.dumps(bounds))
    print(f"wrote {out} ({running} bytes, {len(segs)} segments)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    main(args.bak, args.out)
