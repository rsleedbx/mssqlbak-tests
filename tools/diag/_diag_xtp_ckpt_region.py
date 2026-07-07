#!/usr/bin/env python3
"""Dump the record/preamble layout in a concat-offset window so we can see the
structure around a tricky id (e.g. 682) and around a clean 1 MB boundary.

Usage:
    python -m tools.diag._diag_xtp_ckpt_region --start 1268000 --end 1275000
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
    _LOG_HEADER_SIZE,
    _read_log_header,
)

_U32 = struct.Struct("<I")
_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"


def _segment2(bak_bytes: bytes) -> bytes:
    cur: list[bytes] = []
    segs: list[bytes] = []
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
    return max(segs, key=len)


def main(bak_path: Path, start: int, end: int) -> None:
    seg = _segment2(bak_bytes=bak_path.read_bytes())
    n = len(seg)
    print(f"segment len={n}; window [{start}..{end})")

    # mark preambles in window
    pres = []
    pos = start
    while True:
        p = seg.find(_CKPT_PREAMBLE_SIG, pos, end)
        if p < 0:
            break
        pres.append(p)
        pos = p + 1
    print(f"preambles in window: {pres}")

    # try to interpret records in the window by resync
    off = start
    while off + _LOG_HEADER_SIZE <= min(end, n):
        hv = _read_log_header(seg, off, n)
        if hv is None:
            off += 1
            continue
        size, lb = hv
        seq = _U32.unpack_from(seg, off + 8)[0]
        marker = _U32.unpack_from(seg, off + 12)[0]
        pid = _U32.unpack_from(seg, off + _LOG_HEADER_SIZE)[0] if off + 24 <= n else -1
        pw = _U32.unpack_from(seg, off + _LOG_HEADER_SIZE + 4)[0] if off + 28 <= n else -1
        note = ""
        payload = seg[off + _LOG_HEADER_SIZE : off + _LOG_HEADER_SIZE + size]
        if _CKPT_PREAMBLE_SIG in payload:
            note = f"PAYLOAD-STRADDLE @+{payload.find(_CKPT_PREAMBLE_SIG)}"
        print(f"  rec@{off}: size={size} lb=0x{lb:02x} seq={seq} marker=0x{marker:x} "
              f"pid={pid} pw={pw} {note}")
        off += _LOG_HEADER_SIZE + size


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    args = ap.parse_args()
    main(args.bak, args.start, args.end)
