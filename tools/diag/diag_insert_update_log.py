#!/usr/bin/env python3
"""Compare log record order for 2017 temporal vs 2022 insert+update fixtures."""
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
    LOP_BEGIN_XACT,
    LOP_COMMIT_XACT,
    iter_log_records,
    find_log_range,
    build_uncommitted_set,
)

FIXTURES = [
    ("2017 temporal_update", fixture("2017", "dirtycoverage_temporal_update.bak")),
    ("2022 insert_update", fixture("2022", "dirtycoverage_insert_update.bak")),
]


def lop_name(lop: int) -> str:
    return {
        LOP_INSERT_ROWS: "INSERT",
        LOP_MODIFY_ROW: "MODIFY",
        LOP_DELETE_ROWS: "DELETE",
        LOP_BEGIN_XACT: "BEGIN",
        LOP_COMMIT_XACT: "COMMIT",
    }.get(lop, f"0x{lop:04x}")


def main() -> None:
    for label, path in FIXTURES:
        with open(path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
                start, end = find_log_range(data)
                records = list(iter_log_records(data, start, end))

        uncommitted = build_uncommitted_set(iter(records))
        print(f"\n=== {label} ===")
        print(f"Total records: {len(records)}, Uncommitted xacts: {len(uncommitted)}")

        # For each slot that has BOTH INSERT and MODIFY from uncommitted xacts,
        # check the ORDER (which comes first)
        slot_records: dict[tuple, list[tuple[int, str]]] = {}
        for i, rec in enumerate(records):
            if rec.xact_id not in uncommitted:
                continue
            if rec.lop not in (LOP_INSERT_ROWS, LOP_MODIFY_ROW):
                continue
            if rec.file_id is None or rec.page_id is None or rec.slot_id is None:
                continue
            key = (rec.file_id, rec.page_id, rec.slot_id)
            slot_records.setdefault(key, []).append((i, lop_name(rec.lop)))

        for key, ops in sorted(slot_records.items()):
            if len(ops) > 1:
                order = " → ".join(op for _, op in ops)
                print(f"  {key}: {order}")


if __name__ == "__main__":
    main()
