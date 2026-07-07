#!/usr/bin/env python3
"""Prototype VARIABLE-block-size splice scanner on a cached segment, reporting
per-LB seq completeness.  Block size is detected per straddle by locating where
the straddling record's tail + the next record (seq+1, same LB) resume.

Usage:
    python -m tools.diag._diag_xtp_ckpt_vscan --bin /tmp/aw_xtp.bin
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
    _LOG_MIN_CHAIN,
    _validate_log_header,
)

_U32 = struct.Struct("<I")
_BLOCK_STEP = 512
_MAX_BLOCK = 16384


def _find_aligned_sig(seg: bytes, start: int, end: int) -> int:
    """First _BLOCK_STEP-aligned preamble sig in [start, end), or -1.

    Real segment-header blocks are always 512-aligned; requiring alignment
    rejects a coincidental sig inside legitimate record data."""
    pos = start
    while True:
        p = seg.find(_CKPT_PREAMBLE_SIG, pos, end)
        if p < 0:
            return -1
        if p % _BLOCK_STEP == 0:
            return p
        pos = p + 1


def _detect_block(seg: bytes, p: int, rem: int, lb: int, seq: int, n: int) -> int:
    """Return block size K (multiple of 512) such that the straddling record's
    `rem` tail bytes sit at [p+K, p+K+rem) and the next record (seq+1, same LB)
    starts at p+K+rem; else -1."""
    k = _BLOCK_STEP
    while k <= _MAX_BLOCK:
        h = p + k + rem
        if h + _LOG_HEADER_SIZE > n:
            break
        hv = _validate_log_header(seg[h : h + _LOG_HEADER_SIZE])
        if hv is not None:
            _size2, lb2 = hv
            seq2 = _U32.unpack_from(seg, h + 8)[0]
            if lb2 == lb and seq2 == seq + 1:
                return k
        k += _BLOCK_STEP
    return -1


def _read_record(seg: bytes, walk: int, n: int) -> tuple[int, int, bytes, int] | None:
    """Read one record at *walk*, splicing out a single variable-size checkpoint
    -segment block from the header and/or the payload.  Returns
    ``(lb, seq, payload, end)`` or ``None``.  The block size K is locked by
    requiring the record to end at a valid header whose seq == this seq + 1 and
    same LB (dense-seq anchor)."""
    hs = _find_aligned_sig(seg, walk, walk + _LOG_HEADER_SIZE)
    if hs >= 0:
        # header straddle: block at hs splits the 20-byte header
        pre = seg[walk:hs]
        need = _LOG_HEADER_SIZE - len(pre)
        k = _BLOCK_STEP
        while k <= _MAX_BLOCK:
            hdr = pre + seg[hs + k : hs + k + need]
            hv = _validate_log_header(hdr)
            if hv is not None:
                size, lb = hv
                seq = _U32.unpack_from(hdr, 8)[0]
                data_off = hs + k + need
                rec = _read_payload(seg, data_off, size, lb, seq, n)
                if rec is not None:
                    return lb, seq, rec[0], rec[1]
            k += _BLOCK_STEP
        return None
    hv = _validate_log_header(seg[walk : walk + _LOG_HEADER_SIZE])
    if hv is None:
        return None
    size, lb = hv
    seq = _U32.unpack_from(seg, walk + 8)[0]
    rec = _read_payload(seg, walk + _LOG_HEADER_SIZE, size, lb, seq, n)
    if rec is None:
        return None
    return lb, seq, rec[0], rec[1]


def _read_payload(seg, data_off, size, lb, seq, n):  # noqa: ANN001
    """Read a *size*-byte payload from *data_off*, splicing one variable block if
    present.  Returns (payload, end) or None."""
    sig = _find_aligned_sig(seg, data_off, min(data_off + size, n))
    if sig < 0:
        if data_off + size > n:
            return None
        return seg[data_off : data_off + size], data_off + size
    head_len = sig - data_off
    rem = size - head_len
    k = _detect_block(seg, sig, rem, lb, seq, n)
    if k < 0:
        return None
    return seg[data_off:sig] + seg[sig + k : sig + k + rem], sig + k + rem


def scan(seg: bytes) -> dict[int, dict[int, bytes]]:
    n = len(seg)
    lb_seen: dict[int, dict[int, bytes]] = {}
    off = 0
    while off + _LOG_HEADER_SIZE <= n:
        if (
            _find_aligned_sig(seg, off, off + _LOG_HEADER_SIZE) < 0
            and _validate_log_header(seg[off : off + _LOG_HEADER_SIZE]) is None
        ):
            off += 1
            continue
        chain: list[tuple[int, int, bytes]] = []
        walk = off
        while walk + _LOG_HEADER_SIZE <= n:
            rec = _read_record(seg, walk, n)
            if rec is None:
                break
            lb, seq, payload, end = rec
            if end <= walk:
                break
            chain.append((lb, seq, payload))
            walk = end
        if len(chain) >= _LOG_MIN_CHAIN:
            for lb, seq, payload in chain:
                lb_seen.setdefault(lb, {}).setdefault(seq, payload)
            off = walk
        else:
            off += 1
    return lb_seen


def main(bin_path: Path, synth: bool) -> None:
    seg = bin_path.read_bytes()
    lb_map = scan(seg)
    print(f"bin: {bin_path.name}")
    for lb in sorted(lb_map):
        seqs = sorted(lb_map[lb])
        lo, hi = seqs[0], seqs[-1]
        distinct = len(seqs)
        span = hi - lo + 1
        gaps = span - distinct
        flag = "COMPLETE" if gaps == 0 and lo == 1 else ""
        print(f"  LB=0x{lb:02x}: distinct={distinct} min={lo} max={hi} "
              f"span={span} gaps={gaps} {flag}")
    if synth and 0 in lb_map:
        bad = 0
        for seq, payload in lb_map[0].items():
            w = 1 + ((seq - 1) % 400)
            ok = (
                len(payload) >= 12
                and _U32.unpack_from(payload, 0)[0] == seq
                and _U32.unpack_from(payload, 4)[0] == w
                and payload[12:] == b"\x78\x00" * w
            )
            if not ok:
                bad += 1
        print(f"  synth byte-exact mismatches: {bad}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("--synth", action="store_true")
    args = ap.parse_args()
    main(args.bin, args.synth)
