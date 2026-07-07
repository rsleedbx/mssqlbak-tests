#!/usr/bin/env python3
"""Dump the raw bytes around a checkpoint-segment boundary and probe where valid
log-record headers resume, to measure the true block size and whether records
are displaced (insertion) or destroyed (overwrite).

Usage:
    python -m tools.diag._diag_xtp_ckpt_boundary --bin /tmp/aw_xtp.bin --at 1343300
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.xtp import (  # noqa: E402
    _CKPT_PREAMBLE_SIG,
    _LOG_HEADER_SIZE,
    _validate_log_header,
)

_U32 = struct.Struct("<I")


def main(bin_path: Path, at: int) -> None:
    seg = bin_path.read_bytes()
    n = len(seg)

    pre = seg.find(_CKPT_PREAMBLE_SIG, at, at + 8000)
    print(f"first preamble sig at/after {at}: {pre} (+{pre-at})")
    if pre < 0:
        return
    print(f"\npreamble block first 64 bytes: {seg[pre:pre+64].hex()}")
    # scan the region after the preamble: where do zeros end / data resume?
    # find the end of the initial preamble+zero-fill region
    j = pre + 8
    while j < n and seg[j] != 0:
        j += 1
    zstart = j
    while j < n and seg[j] == 0:
        j += 1
    print(f"non-zero preamble header: [{pre}..{zstart}) = {zstart-pre} bytes")
    print(f"zero-fill: [{zstart}..{j}) = {j-zstart} bytes; first data byte at {j} (+{j-pre})")

    # probe for the first valid log-record header at each offset after the preamble
    print("\nvalid log headers in [pre, pre+8192):")
    found = 0
    for o in range(pre, min(pre + 8192, n - _LOG_HEADER_SIZE)):
        hv = _validate_log_header(seg[o : o + _LOG_HEADER_SIZE])
        if hv is not None:
            size, lb = hv
            seq = _U32.unpack_from(seg, o + 8)[0]
            # sanity: only plausible LB/size
            if 0x07 <= lb <= 0x0d and 8 <= size <= 4096:
                print(f"  @{o} (+{o-pre}): lb=0x{lb:02x} size={size} seq={seq}")
                found += 1
                if found >= 12:
                    break


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("--at", type=int, required=True)
    args = ap.parse_args()
    main(args.bin, args.at)
