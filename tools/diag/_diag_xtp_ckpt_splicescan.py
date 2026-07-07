#!/usr/bin/env python3
"""Prototype scanner with the 4096-byte checkpoint-segment-header splice, and
report per-LB seq completeness.  Validates the recovery rule on both the
synthetic straddle fixture and AdventureWorks before touching xtp.py.

Usage:
    python -m tools.diag._diag_xtp_ckpt_splicescan --bak PATH
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
    _LOG_MIN_CHAIN,
    _read_log_header,
)

_U32 = struct.Struct("<I")
_PREAMBLE_BLOCK = 4096
_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"


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


def _splice_payload(seg: bytes, data_off: int, size: int, n: int) -> tuple[bytes, int]:
    """Collect *size* payload bytes from *data_off*, splicing out each 4096-byte
    checkpoint-segment header block (starting with the preamble sig) that
    interrupts the payload.  Returns (payload, next_off)."""
    out = bytearray()
    pos = data_off
    guard = 0
    while len(out) < size and pos < n:
        remaining = size - len(out)
        window_end = min(pos + remaining, n)
        rel = seg.find(_CKPT_PREAMBLE_SIG, pos, window_end)
        if rel < 0:
            out += seg[pos:window_end]
            pos = window_end
            break
        out += seg[pos:rel]
        pos = rel + _PREAMBLE_BLOCK
        guard += 1
        if guard > 64:
            break
    return bytes(out), pos


def scan(bak_bytes: bytes) -> dict[int, dict[int, bytes]]:
    segments = _segments(bak_bytes)
    lb_seen: dict[int, dict[int, bytes]] = {}
    for seg in segments:
        n = len(seg)
        off = 0
        while off + _LOG_HEADER_SIZE <= n:
            # skip a standalone segment-header block at the resync point
            if seg.find(_CKPT_PREAMBLE_SIG, off, off + _LOG_HEADER_SIZE) >= 0:
                sp = seg.find(_CKPT_PREAMBLE_SIG, off, off + _LOG_HEADER_SIZE)
                off = sp + _PREAMBLE_BLOCK
                continue
            hv = _read_log_header(seg, off, n)
            if hv is None:
                off += 1
                continue
            chain: list[tuple[int, int, bytes]] = []
            walk = off
            while walk + _LOG_HEADER_SIZE <= n:
                # header straddle: a segment header block splits the 20-byte header
                if seg.find(_CKPT_PREAMBLE_SIG, walk, walk + _LOG_HEADER_SIZE) >= 0:
                    break
                hv2 = _read_log_header(seg, walk, n)
                if hv2 is None:
                    break
                size, lb = hv2
                seq = _U32.unpack_from(seg, walk + 8)[0]
                data_off = walk + _LOG_HEADER_SIZE
                straddle = seg.find(_CKPT_PREAMBLE_SIG, data_off, min(data_off + size, n)) >= 0
                if straddle:
                    payload, walk = _splice_payload(seg, data_off, size, n)
                else:
                    payload = seg[data_off : data_off + size]
                    walk = data_off + size
                chain.append((lb, seq, payload))
            if len(chain) >= _LOG_MIN_CHAIN:
                for lb, seq, payload in chain:
                    lb_seen.setdefault(lb, {}).setdefault(seq, payload)
                off = walk
            else:
                off += 1
    return lb_seen


def main(bak_path: Path) -> None:
    lb_map = scan(bak_path.read_bytes())
    print(f"bak: {bak_path.name}")
    for lb in sorted(lb_map):
        seqs = sorted(lb_map[lb])
        lo, hi = seqs[0], seqs[-1]
        distinct = len(seqs)
        span = hi - lo + 1
        gaps = span - distinct
        print(f"  LB=0x{lb:02x}: distinct={distinct} min={lo} max={hi} "
              f"span={span} gaps={gaps} "
              f"{'COMPLETE' if gaps == 0 and lo == 1 else ''}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    args = ap.parse_args()
    main(args.bak)
