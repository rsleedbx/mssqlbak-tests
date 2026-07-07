#!/usr/bin/env python3
"""Characterise the residual straddle edge cases (ids that the simple payload
splice still misses).  Prints the byte neighbourhood of a target id's record so
we can see whether the 4096-byte checkpoint-segment header lands inside the
record HEADER (not the payload).

Usage:
    python -m tools.diag._diag_xtp_ckpt_edge --id 682
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.compressed import (  # noqa: E402
    iter_decompressed_chunks as _iter_dc,
    _OFF_HEADER_VERSION,
    _HEADER_VERSION,
)
from mssqlbak.xtp import (  # noqa: E402
    _PAGE_MTYPE_MAX,
    _CKPT_PREAMBLE_SIG,
)

_U32 = struct.Struct("<I")
_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"
_PREAMBLE_BLOCK = 4096


def _segments(bak_bytes: bytes) -> list[bytes]:
    segments: list[bytes] = []
    cur: list[bytes] = []
    for ch in _iter_dc(bak_bytes):
        is_page = (
            len(ch) >= 96
            and ch[_OFF_HEADER_VERSION] == _HEADER_VERSION
            and 1 <= ch[1] <= _PAGE_MTYPE_MAX
        )
        if is_page:
            if cur:
                segments.append(b"".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        segments.append(b"".join(cur))
    return segments


def _expected_width(id_: int) -> int:
    return 1 + ((id_ - 1) % 400)


def main(bak_path: Path, target: int) -> None:
    bak_bytes = bak_path.read_bytes()
    segments = _segments(bak_bytes)
    exp_w = _expected_width(target)
    print(f"target id={target} expected width={exp_w} ({exp_w*2} var bytes)")

    # the expected fixed prefix of the record payload: id(4) width(4) nullbmp(2) varoff(2)
    prefix = struct.pack("<II", target, exp_w) + b"\x0c\x00" + struct.pack("<H", 12 + exp_w * 2)
    # a run of 'x' after prefix
    needle = prefix + b"\x78\x00" * 4

    for si, seg in enumerate(segments):
        pos = 0
        while True:
            hit = seg.find(needle, pos)
            if hit < 0:
                break
            print(f"\n--- payload-prefix hit in seg#{si} at abs {hit} ---")
            # the 20-byte header should be just before, at hit-20
            hdr_off = hit - 20
            print(f"  header@{hdr_off}: {seg[hdr_off:hdr_off+20].hex()}")
            print(f"  payload@{hit}: {seg[hit:hit+24].hex()}")
            # find nearest preamble near this record
            npre = seg.find(_CKPT_PREAMBLE_SIG, max(0, hit - 40), hit + exp_w * 2 + 64)
            if npre >= 0:
                print(f"  preamble near record at abs {npre} (payload+{npre-hit}, header+{npre-hdr_off})")
                print(f"    context [pre-8..pre+16]: {seg[npre-8:npre+16].hex()}")
            else:
                print("  no preamble in record span")
            pos = hit + 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    ap.add_argument("--id", type=int, required=True)
    args = ap.parse_args()
    main(args.bak, args.id)
