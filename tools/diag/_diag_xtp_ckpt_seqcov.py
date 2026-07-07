#!/usr/bin/env python3
"""Report per-LB seq completeness from the REAL scan_cfp_log_records (post
splice change).

Usage:
    python -m tools.diag._diag_xtp_ckpt_seqcov --bak PATH
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.xtp import scan_cfp_log_records  # noqa: E402

_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"


def main(bak_path: Path) -> None:
    lb_map = scan_cfp_log_records(bak_path.read_bytes())
    print(f"bak: {bak_path.name}")
    for lb in sorted(lb_map):
        recs = lb_map[lb]
        seqs = [s for s, _ in recs]
        lo, hi = min(seqs), max(seqs)
        distinct = len(set(seqs))
        span = hi - lo + 1
        gaps = span - distinct
        flag = "COMPLETE" if gaps == 0 and lo == 1 else ""
        print(f"  LB=0x{lb:02x}: distinct={distinct} min={lo} max={hi} "
              f"span={span} gaps={gaps} {flag}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    args = ap.parse_args()
    main(args.bak)
