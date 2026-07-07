#!/usr/bin/env python3
"""Report the gap structure (consecutive missing-seq runs) for a given LB, and
dump the byte neighbourhood at the first gap so we can see the boundary artifact.

Caches the concatenated non-page segment to /tmp to make iteration fast.

Usage:
    python -m tools.diag._diag_xtp_ckpt_gapmap --bak PATH --lb 13
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.xtp import scan_cfp_log_records  # noqa: E402

_U32 = struct.Struct("<I")


def _runs(missing: list[int]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    if not missing:
        return runs
    start = prev = missing[0]
    for m in missing[1:]:
        if m == prev + 1:
            prev = m
        else:
            runs.append((start, prev))
            start = prev = m
    runs.append((start, prev))
    return runs


def main(bak_path: Path, lb: int) -> None:
    lb_map = scan_cfp_log_records(bak_path.read_bytes())
    if lb not in lb_map:
        print(f"LB 0x{lb:02x} not present. Present: {sorted(lb_map)}")
        return
    seqs = sorted({s for s, _ in lb_map[lb]})
    lo, hi = seqs[0], seqs[-1]
    present = set(seqs)
    missing = [s for s in range(lo, hi + 1) if s not in present]
    runs = _runs(missing)
    print(f"LB=0x{lb:02x}: min={lo} max={hi} distinct={len(seqs)} "
          f"missing={len(missing)} gap_runs={len(runs)}")
    print("  run-length histogram: ", end="")
    from collections import Counter
    rl = Counter(b - a + 1 for a, b in runs)
    print(dict(sorted(rl.items())))
    print(f"  first 15 runs: {runs[:15]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, required=True)
    ap.add_argument("--lb", type=int, required=True)
    args = ap.parse_args()
    main(args.bak, args.lb)
