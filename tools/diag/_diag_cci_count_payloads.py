#!/usr/bin/env python3
"""Count raw occurrences of each row's value-string across the whole .bak.

A live data-page copy of a row contributes one occurrence; a log before-image
(committed DELETE record) contributes another.  Deleted ids (5001-6000) with a
delete log record should appear >= 2x; survived ids (6001-7000) ~1x.  Resolves
whether the .bak actually carries delete records for all 1000 deleted rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture  # noqa: E402

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"

DELETED = [5001, 5002, 5100, 5500, 5900, 5999, 6000]
SURVIVED = [6001, 6002, 6500, 6999, 7000]


def main() -> None:
    data = fixture(VERSION, NAME).read_bytes()
    print(f"file size: {len(data):,} bytes\n")
    print("id      kind      occurrences of b'original_<id>'")
    for ids, kind in ((DELETED, "DELETED"), (SURVIVED, "survived")):
        for i in ids:
            needle = b"original_%d" % i
            # exact-token count: avoid 5001 matching inside 50011 by checking the
            # following byte is not an ASCII digit.
            count = 0
            pos = 0
            while True:
                j = data.find(needle, pos)
                if j < 0:
                    break
                nxt = data[j + len(needle): j + len(needle) + 1]
                if not (nxt and nxt.isdigit()):
                    count += 1
                pos = j + 1
            print(f"{i:<7} {kind:<9} {count}")


if __name__ == "__main__":
    main()
