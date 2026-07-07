#!/usr/bin/env python3
"""Show all log records touching (1, 320, 1) in 2017 dirtycoverage_temporal_update.bak."""
from __future__ import annotations

import mmap
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture

from mssqlbak.logtail import (  # type: ignore[attr-defined]
    LOP_INSERT_ROWS,
    LOP_MODIFY_ROW,
    LOP_DELETE_ROWS,
    iter_log_records,
    find_log_range,
    build_uncommitted_set,
)

FIXTURE = fixture("2017", "dirtycoverage_temporal_update.bak")
TARGET_PAGE = 320
TARGET_SLOT = 1


def lop_name(lop: int) -> str:
    return {
        LOP_INSERT_ROWS: "LOP_INSERT_ROWS",
        LOP_MODIFY_ROW: "LOP_MODIFY_ROW",
        LOP_DELETE_ROWS: "LOP_DELETE_ROWS",
    }.get(lop, f"lop=0x{lop:04x}")


def main() -> None:
    with open(FIXTURE, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
            start, end = find_log_range(data)
            print(f"Log range: 0x{start:x} - 0x{end:x}")
            records = list(iter_log_records(data, start, end))

    print(f"Total log records: {len(records)}")

    uncommitted = build_uncommitted_set(iter(records))
    print(f"Uncommitted xact_ids: {len(uncommitted)}")
    print()

    print(f"Records for (file=1, page={TARGET_PAGE}, slot={TARGET_SLOT}):")
    count = 0
    for rec in records:
        if rec.page_id == TARGET_PAGE and rec.slot_id == TARGET_SLOT and rec.file_id == 1:
            status = "UNCOMMITTED" if rec.xact_id in uncommitted else "committed  "
            xact = rec.xact_id.hex() if rec.xact_id else "None"
            print(f"  {lop_name(rec.lop):20s}  xact={xact}  {status}")
            count += 1
    if count == 0:
        print("  (none)")
    print()

    # Also show all uncommitted INSERT_ROWS records
    print("All uncommitted LOP_INSERT_ROWS records:")
    for rec in records:
        if rec.lop == LOP_INSERT_ROWS and rec.xact_id in uncommitted:
            xact = rec.xact_id.hex() if rec.xact_id else "None"
            print(f"  fid={rec.file_id}  page={rec.page_id}  slot={rec.slot_id}  xact={xact}")
    print()
    print("All 21 log records (lop, xact, page, slot):")
    from mssqlbak.logtail import LOP_BEGIN_XACT, LOP_COMMIT_XACT  # type: ignore[attr-defined]
    for rec in records:
        lop = {LOP_INSERT_ROWS: "INSERT", LOP_MODIFY_ROW: "MODIFY",
               LOP_DELETE_ROWS: "DELETE", LOP_BEGIN_XACT: "BEGIN",
               LOP_COMMIT_XACT: "COMMIT"}.get(rec.lop, f"0x{rec.lop:04x}")
        xact = rec.xact_id.hex()[:8] if rec.xact_id else "None    "
        pg = f"pg={rec.page_id}" if rec.page_id else "pg=None"
        sl = f"sl={rec.slot_id}" if rec.slot_id is not None else "sl=None"
        uc = "UNCOMMITTED" if rec.xact_id in uncommitted else "committed  "
        print(f"  {lop:8s}  xact={xact}  {pg:8s}  {sl:6s}  {uc}")


if __name__ == "__main__":
    main()
