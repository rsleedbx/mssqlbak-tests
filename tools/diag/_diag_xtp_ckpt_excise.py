#!/usr/bin/env python3
"""Model B: excise every 4096-byte checkpoint-segment header block, then walk
records on the resulting clean contiguous stream.

Confirms: (1) preamble signatures sit at a regular 1 MB stride, (2) each header
block is exactly 4096 bytes (data resumes at +4096), (3) after excising them the
record stream is perfectly contiguous and yields the full {1..N}.

Usage:
    python -m tools.diag._diag_xtp_ckpt_excise [--bak PATH]
"""
from __future__ import annotations

import argparse
import struct
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
from mssqlbak.xtp import (  # noqa: E402
    _PAGE_MTYPE_MAX,
    _CKPT_PREAMBLE_SIG,
    _LOG_HEADER_SIZE,
    _LOG_MIN_CHAIN,
    _read_log_header,
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


def _find_preambles(seg: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        p = seg.find(_CKPT_PREAMBLE_SIG, pos)
        if p < 0:
            break
        out.append(p)
        pos = p + 1
    return out


def _excise(seg: bytes, preambles: list[int]) -> bytes:
    out = bytearray()
    prev = 0
    for p in preambles:
        out += seg[prev:p]
        prev = p + _PREAMBLE_BLOCK
    out += seg[prev:]
    return bytes(out)


def _walk(seg: bytes) -> dict[int, bytes]:
    n = len(seg)
    recovered: dict[int, bytes] = {}
    off = 0
    while off + _LOG_HEADER_SIZE <= n:
        hv = _read_log_header(seg, off, n)
        if hv is None:
            off += 1
            continue
        chain: list[tuple[int, int, bytes]] = []
        walk = off
        while walk + _LOG_HEADER_SIZE <= n:
            hv2 = _read_log_header(seg, walk, n)
            if hv2 is None:
                break
            size, lb = hv2
            seq = _U32.unpack_from(seg, walk + 8)[0]
            payload = seg[walk + _LOG_HEADER_SIZE : walk + _LOG_HEADER_SIZE + size]
            chain.append((lb, seq, payload))
            walk += _LOG_HEADER_SIZE + size
        if len(chain) >= _LOG_MIN_CHAIN:
            for lb, seq, payload in chain:
                recovered.setdefault(seq, payload)
            off = walk
        else:
            off += 1
    return recovered


def main(bak_path: Path) -> None:
    bak_bytes = bak_path.read_bytes()
    segments = _segments(bak_bytes)

    all_recovered: dict[int, bytes] = {}
    for si, seg in enumerate(segments):
        preambles = _find_preambles(seg)
        if preambles:
            strides = [b - a for a, b in zip(preambles, preambles[1:])]
            sc = Counter(strides)
            print(f"seg#{si}: {len(preambles)} preambles; stride histogram "
                  f"(top 4): {sc.most_common(4)}")
        clean = _excise(seg, preambles)
        rec = _walk(clean)
        for seq, payload in rec.items():
            all_recovered.setdefault(seq, payload)

    seqs = set(all_recovered)
    hi = max(seqs)
    missing = sorted(set(range(1, hi + 1)) - seqs)
    print(f"\nrecovered distinct seq: {len(seqs)}  max={hi}")
    print(f"missing from 1..{hi}: {len(missing)} {missing[:20]}")

    # byte-exact validation for the synthetic fixture
    bad_seqs: list[int] = []
    for seq, payload in all_recovered.items():
        if seq < 1 or seq > hi:
            continue
        exp = _expected_width(seq)
        ok = False
        if len(payload) >= 12:
            pid = _U32.unpack_from(payload, 0)[0]
            pw = _U32.unpack_from(payload, 4)[0]
            var = payload[12:]
            ok = pid == seq and pw == exp and var == b"\x78\x00" * exp
        if not ok:
            bad_seqs.append(seq)
    bad_seqs.sort()
    print(f"byte-exact payload mismatches: {len(bad_seqs)}")
    if bad_seqs:
        print(f"  bad seq min={bad_seqs[0]} max={bad_seqs[-1]}")
        print(f"  first 30: {bad_seqs[:30]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    args = ap.parse_args()
    main(args.bak)
