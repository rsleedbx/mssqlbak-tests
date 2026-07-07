#!/usr/bin/env python3
"""Re-walk the XTP log-record stream WITH the checkpoint-segment splice rule and
verify complete {1..N} recovery.

Model confirmed by _diag_xtp_ckpt_splice: the XTP checkpoint DATA file is a
series of 1 MB segments; each begins with a fixed 4096-byte header (preamble +
zero-pad).  User records pack contiguously in the remaining bytes and straddle
freely across the 4096-byte headers of following segments.  To recover a
straddle record, splice out the 4096-byte header block and rejoin the payload
head + tail.

This walks every segment, applies the splice, and reports how many distinct
seq values are recovered vs the expected {1..N}.

Usage:
    python -m tools.diag._diag_xtp_ckpt_recover [--bak PATH]
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


def _read_payload_spliced(seg: bytes, data_off: int, size: int, n: int) -> tuple[bytes, int]:
    """Read *size* payload bytes from *data_off*, splicing out any 4096-byte
    checkpoint-segment header that interrupts the payload.

    Returns (payload, end_off) where end_off is the offset just past the record.
    """
    out = bytearray()
    pos = data_off
    while len(out) < size:
        remaining = size - len(out)
        # is there a preamble signature within the next `remaining` bytes?
        window_end = min(pos + remaining, n)
        rel = seg.find(_CKPT_PREAMBLE_SIG, pos, window_end)
        if rel < 0:
            out += seg[pos : pos + remaining]
            pos += remaining
            break
        # copy head up to the preamble, then skip the 4096-byte header block
        out += seg[pos:rel]
        pos = rel + _PREAMBLE_BLOCK
    return bytes(out), pos


def main(bak_path: Path) -> None:
    bak_bytes = bak_path.read_bytes()
    segments = _segments(bak_bytes)

    recovered: dict[int, bytes] = {}
    straddle_ok = 0
    straddle_bad = 0

    for seg in segments:
        n = len(seg)
        off = 0
        while off + _LOG_HEADER_SIZE <= n:
            hv0 = _read_log_header(seg, off, n)
            if hv0 is None:
                off += 1
                continue
            chain: list[tuple[int, int, bytes]] = []
            walk = off
            while walk + _LOG_HEADER_SIZE <= n:
                hv = _read_log_header(seg, walk, n)
                if hv is None:
                    break
                size, lb = hv
                seq = _U32.unpack_from(seg, walk + 8)[0]
                data_off = walk + _LOG_HEADER_SIZE
                straddles = (
                    seg.find(_CKPT_PREAMBLE_SIG, data_off, min(data_off + size, n)) >= 0
                )
                if straddles:
                    payload, end = _read_payload_spliced(seg, data_off, size, n)
                    # validate against synthetic width
                    if len(payload) >= 12:
                        pid = _U32.unpack_from(payload, 0)[0]
                        pw = _U32.unpack_from(payload, 4)[0]
                        var = payload[12:]
                        exp = _expected_width(seq)
                        if pid == seq and pw == exp and len(var) == exp * 2 and \
                                var == (b"\x78\x00" * exp):
                            straddle_ok += 1
                        else:
                            straddle_bad += 1
                    chain.append((lb, seq, payload))
                    walk = end
                else:
                    payload = seg[data_off : data_off + size]
                    chain.append((lb, seq, payload))
                    walk = data_off + size
            if len(chain) >= _LOG_MIN_CHAIN:
                for lb, seq, payload in chain:
                    recovered.setdefault(seq, payload)
                off = walk
            else:
                off += 1

    seqs = set(recovered)
    hi = max(seqs)
    full = set(range(1, hi + 1))
    missing = sorted(full - seqs)
    print(f"recovered distinct seq: {len(seqs)}  max={hi}")
    print(f"straddle records: ok={straddle_ok} bad={straddle_bad}")
    print(f"missing from 1..{hi}: {len(missing)}")
    if missing[:20]:
        print(f"  first missing: {missing[:20]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK)
    args = ap.parse_args()
    main(args.bak)
