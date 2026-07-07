#!/usr/bin/env python3
"""Test whether a straddle row's payload TAIL is displaced (recoverable) or
truly destroyed at an XTP checkpoint segment boundary.

The synthetic fixture ``xtp_checkpoint_straddle_full.bak`` stores, for id ``i``,
``payload = REPLICATE(N'x', 1 + ((i-1) % 400))`` — a pure ``78 00`` (UTF-16LE
'x') run.  For a straddle record (payload contains the chunk preamble
signature) this locates the preamble, then scans forward past it for the next
long ``78 00`` run and reports whether head-chars + tail-chars == expected width.

Usage:
    python -m tools.diag._diag_xtp_ckpt_splice [--bak PATH] [--limit N]
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


def _run_of_x(buf: bytes, start: int) -> int:
    n = 0
    i = start
    while i + 1 < len(buf) and buf[i] == 0x78 and buf[i + 1] == 0x00:
        n += 2
        i += 2
    return n


def _next_x_run(buf: bytes, start: int, min_len: int) -> tuple[int, int]:
    """Find the next ``78 00`` run of at least *min_len* bytes at/after start.

    Returns (run_start, run_len) or (-1, 0).
    """
    i = start
    while i + 1 < len(buf):
        if buf[i] == 0x78 and buf[i + 1] == 0x00:
            rl = _run_of_x(buf, i)
            if rl >= min_len:
                return i, rl
            i += rl if rl else 2
        else:
            i += 1
    return -1, 0


def main(bak_path: Path, limit: int) -> None:
    bak_bytes = bak_path.read_bytes()
    segments = _segments(bak_bytes)
    print(f"segments: {len(segments)}  total={sum(len(s) for s in segments)} bytes")

    shown = 0
    for si, seg in enumerate(segments):
        n = len(seg)
        off = 0
        while off + _LOG_HEADER_SIZE <= n:
            hv = _read_log_header(seg, off, n)
            if hv is None:
                off += 1
                continue
            size, lb = hv
            seq = _U32.unpack_from(seg, off + 8)[0]
            payload = seg[off + _LOG_HEADER_SIZE : off + _LOG_HEADER_SIZE + size]
            if _CKPT_PREAMBLE_SIG in payload:
                pre_rel = payload.find(_CKPT_PREAMBLE_SIG)
                head = payload[:pre_rel]
                abs_pre = off + _LOG_HEADER_SIZE + pre_rel
                exp_w = _expected_width(seq) if seq else -1
                head_x = _run_of_x(head, head.find(b"\x78\x00")) if b"\x78\x00" in head else 0
                need_chars = exp_w - head_x // 2

                # search a wide window after the preamble for the resumed run
                run_off, run_len = _next_x_run(seg, abs_pre, min_len=max(8, (need_chars - 4) * 2))

                print("\n" + "=" * 78)
                print(f"STRADDLE seq={seq} lb=0x{lb:02x} size={size} seg#{si} off={off}")
                print(f"  expected width={exp_w} chars; head has {head_x//2} chars; "
                      f"need {need_chars} more chars ({need_chars*2} bytes)")
                print(f"  preamble at abs {abs_pre}")
                if run_off >= 0:
                    delta = run_off - abs_pre
                    print(f"  RESUMED 78-00 run at abs {run_off} (preamble+{delta}) "
                          f"len={run_len} bytes ({run_len//2} chars)")
                    print(f"  head+tail chars = {head_x//2 + run_len//2} (expected {exp_w}) "
                          f"{'MATCH' if head_x//2 + run_len//2 >= exp_w else 'SHORT'}")
                    print(f"  bytes [preamble .. resumed): {delta} bytes of preamble/header")
                    print(f"  preamble+{delta-16}..+{delta+8}: "
                          f"{seg[run_off-16:run_off+8].hex()}")
                else:
                    print("  NO resumed 78-00 run found after preamble (window)")
                    print(f"  preamble..+96: {seg[abs_pre:abs_pre+96].hex()}")
                shown += 1
                if shown >= limit:
                    return
                off += _LOG_HEADER_SIZE + size
            else:
                off += _LOG_HEADER_SIZE + size


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    ap.add_argument("--limit", type=int, default=6)
    args = ap.parse_args()
    main(args.bak, args.limit)
