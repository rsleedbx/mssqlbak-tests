"""Dump raw bytes of candidate pages and report which 'label' strings each
holds, to decide whether the modified rows live on page 320 or 328."""
from __future__ import annotations

import sys

from mssqlbak.pages import PageStore


def _scan(raw: bytes, needles: list[bytes]) -> list[str]:
    found = []
    for n in needles:
        c = raw.count(n)
        if c:
            found.append(f"{n!r}x{c}")
    return found


def main() -> int:
    bak = sys.argv[1]
    pages = [int(x) for x in sys.argv[2:]] or [320, 328]
    ps = PageStore.from_bak(bak)
    # UTF-16LE needles for original_/modified_ labels
    needles_ascii = [b"original_", b"modified_"]
    needles_utf16 = [b"o\x00r\x00i\x00g\x00i\x00n\x00a\x00l\x00_\x00",
                     b"m\x00o\x00d\x00i\x00f\x00i\x00e\x00d\x00_\x00"]
    for pid in pages:
        try:
            raw = ps.page_raw(pid, 1)
        except Exception as exc:  # noqa: BLE001
            print(f"page {pid}: ERROR {exc}")
            continue
        m_type = ps.page_m_type(pid, 1)
        a = _scan(raw, needles_ascii)
        u = _scan(raw, needles_utf16)
        print(f"page {pid}: m_type={m_type} ascii={a} utf16={u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
