#!/usr/bin/env python3
"""Compare page LSN vs committed INSERT LSN for 2019/2025 concurrent fixtures."""
from __future__ import annotations

import mmap
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak.logtail import (  # type: ignore[attr-defined]
    logtail_from_bak,
    iter_log_records,
    find_log_range,
    LOP_INSERT_ROWS,
    LOP_COMMIT_XACT,
)
from mssqlbak.rows import _data_pages  # type: ignore[attr-defined]


def lsn_tuple(lsn_bytes: bytes) -> tuple[int, int, int]:
    """Convert 6-byte LSN to (vlfseq, sector, slot) comparable tuple."""
    if len(lsn_bytes) < 6:
        return (0, 0, 0)
    vlfseq = int.from_bytes(lsn_bytes[:4], "big")
    sector = int.from_bytes(lsn_bytes[4:6], "big")
    return (vlfseq, sector, 0)


def main() -> None:
    for version in ("2019", "2025"):
        path = fixture(version, "dirtycoverage_concurrent.bak")
        lt = logtail_from_bak(path)
        store, schema, _boot, _blobs = open_store(path)
        tbl = find_table(schema, "dirty_test")
        assert tbl is not None

        print(f"\n=== {version} concurrent ===")
        print(f"  redo_rows: {list(lt.redo_rows.keys())}")

        # Get page LSN for each page in dirty_test
        for pid, fid in _data_pages(store, tbl):  # type: ignore[arg-type]
            page = store.page(pid, fid)  # type: ignore[attr-defined]
            page_lsn = page.header.lsn
            print(f"  page ({fid},{pid}) LSN={page_lsn.hex() if page_lsn else 'None'}  slot_cnt={page.header.slot_cnt}")

        # Check redo row LSN from log records
        with open(path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
                start, end = find_log_range(data)
                all_recs = list(iter_log_records(data, start, end))

        committed_set = set()
        had_dml: set[bytes] = set()
        for rec in all_recs:
            if rec.lop == LOP_COMMIT_XACT:
                committed_set.add(rec.xact_id)
            elif rec.lop == LOP_INSERT_ROWS:
                had_dml.add(rec.xact_id)
        committed = had_dml & committed_set

        for rec in all_recs:
            if (rec.lop == LOP_INSERT_ROWS
                    and rec.xact_id in committed
                    and rec.page_id is not None):
                for (f, p, sl) in lt.redo_rows:
                    if rec.page_id == p and rec.slot_id == sl and rec.file_id == f:
                        print(f"  redo INSERT rec: page=({f},{p}) slot={sl} lsn={getattr(rec, 'lsn', 'N/A')}")


if __name__ == "__main__":
    main()
