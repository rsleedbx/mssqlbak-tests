#!/usr/bin/env python3
"""Probe dirtycoverage_cci_delete: is the committed CCI/delta DELETE recoverable
from the .bak log tail, and does extraction currently apply it?

Validates the theory that the deletion information IS present in the backup
(as log records) and the gap is purely replay-side.  Prints:
  * log-tail record-set sizes (committed_delete_slots, redo_rows, dirty_slots…)
  * extracted row count + how many of the deleted ids (5001..6000) survive.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture  # noqa: E402

import mmap as _mmap  # noqa: E402
from collections import Counter  # noqa: E402

from mssqlbak import extract_bak_to_delta  # noqa: E402
from mssqlbak.logtail import (  # noqa: E402
    LOP_DELETE_ROWS,
    LOP_INSERT_ROWS,
    LOP_MODIFY_ROW,
    find_log_range,
    iter_log_records,
    logtail_from_bak,
)

_LOP_NAME = {
    LOP_INSERT_ROWS: "INSERT_ROWS",
    LOP_DELETE_ROWS: "DELETE_ROWS",
    LOP_MODIFY_ROW: "MODIFY_ROW",
}


def _tally_log_records(path) -> None:
    with open(path, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            start, end = find_log_range(mm)
            print(f"\n-- find_log_range window: [{start}, {end}) "
                  f"= {(end - start) // 4096} blocks ({end - start} bytes) --")
            # Compare against the *full* APAD..MSLS span to see if delete records
            # live outside the returned window.
            from mssqlbak.logtail import _APAD, _MSLS, _iter_cont_records  # type: ignore
            msls = mm.rfind(_MSLS)
            first_apad = mm.find(_APAD)
            wide_start = (first_apad + 4096) & ~4095
            wide_del = wide_open = wide_cont_del = 0
            for rec in iter_log_records(mm, wide_start, msls):
                if rec.lop == LOP_DELETE_ROWS:
                    wide_del += 1
                if rec.lop == LOP_INSERT_ROWS:
                    wide_open += 1
            for rec in _iter_cont_records(mm, wide_start, msls):
                if rec.lop == LOP_DELETE_ROWS:
                    wide_cont_del += 1
            print(f"-- full APAD..MSLS span [{wide_start}, {msls}) "
                  f"= {(msls - wide_start) // 4096} blocks --")
            print(f"  DELETE_ROWS (OPEN) in full span : {wide_del}")
            print(f"  DELETE_ROWS (CONT) in full span : {wide_cont_del}")
            print(f"  DELETE_ROWS total in full span  : {wide_del + wide_cont_del}")
            print(f"\n-- raw log records in find_log_range window [{start}, {end}) --")
            by_lop: Counter[str] = Counter()
            del_pages: Counter[int] = Counter()
            ins_pages: Counter[int] = Counter()
            for rec in iter_log_records(mm, start, end):
                by_lop[_LOP_NAME.get(rec.lop, hex(rec.lop))] += 1
                if rec.lop == LOP_DELETE_ROWS and rec.page_id is not None:
                    del_pages[rec.page_id] += 1
                if rec.lop == LOP_INSERT_ROWS and rec.page_id is not None:
                    ins_pages[rec.page_id] += 1
            for name, n in by_lop.most_common():
                print(f"  {name:14s} {n}")
            print(f"  DELETE_ROWS distinct pages : {len(del_pages)}")
            print(f"  INSERT_ROWS distinct pages : {len(ins_pages)}")
            print(f"  top INSERT pages (page_id:count): {ins_pages.most_common(6)}")
            print(f"  top DELETE pages (page_id:count): {del_pages.most_common(6)}")
        finally:
            mm.close()

VERSION = "2022"
NAME = "dirtycoverage_cci_delete.bak"
DELETED_LO, DELETED_HI = 5001, 6000  # COMPRESSED_ROWS+1 .. +DELETE_COUNT
EXPECTED_AFTER_DELETE = 6000


def main() -> None:
    path = fixture(VERSION, NAME)
    print(f"== fixture: {path}")

    res = logtail_from_bak(path)
    print("\n-- LogTailResult set sizes --")
    print(f"  dirty_slots            : {len(res.dirty_slots)}")
    print(f"  restore_slots          : {len(res.restore_slots)}")
    print(f"  modified_slots         : {len(res.modified_slots)}")
    print(f"  committed_delete_slots : {len(res.committed_delete_slots)}")
    print(f"  redo_rows              : {len(res.redo_rows)}")
    print(f"  redo_patches           : {len(res.redo_patches)}")
    print(f"  restore_rows           : {len(res.restore_rows)}")
    print(f"  before_images          : {len(res.before_images)}")

    _tally_log_records(path)

    import deltalake  # local import; deltalake is a runtime dep of extract

    # Optionally neutralize the log tail to measure the raw (ghost-filter-only)
    # read: if survivors are the SAME with and without the log tail, the rows
    # are physically live on captured pages (not on-page ghosts) and their
    # deletes are simply absent from what mssqlbak applies.
    raw_mode = "--raw" in sys.argv
    if raw_mode:
        import mssqlbak.extract as _ex
        from mssqlbak.logtail import LogTailResult as _LTR

        _empty = frozenset()
        _ex.logtail_from_bak = lambda *_a, **_k: _LTR(  # type: ignore[assignment]
            dirty_slots=_empty, restore_slots=_empty, modified_slots=_empty
        )
        print("\n[RAW MODE] log tail neutralized (ghost filter only)")

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(path), tmp)
        tables: dict[str, int] = {}
        survivors: list[int] = []
        total_deleted_range = 0
        for schema_dir in sorted(Path(tmp).iterdir()):
            if not schema_dir.is_dir():
                continue
            for tbl_dir in sorted(schema_dir.iterdir()):
                if not tbl_dir.is_dir():
                    continue
                dt = deltalake.DeltaTable(str(tbl_dir))
                t = dt.to_pyarrow_table()
                tables[f"{schema_dir.name}.{tbl_dir.name}"] = t.num_rows
                if "id" in t.column_names:
                    ids = t.column("id").to_pylist()
                    in_range = [i for i in ids if i is not None and DELETED_LO <= i <= DELETED_HI]
                    total_deleted_range += len(in_range)
                    survivors = in_range

    print("\n-- extracted tables --")
    for name, n in tables.items():
        print(f"  {name:40s} {n} rows")
    print("\n-- deleted-range survival (ids 5001..6000) --")
    print(f"  expected rows after delete : {EXPECTED_AFTER_DELETE}")
    print(f"  survivors still present    : {total_deleted_range} (want 0)")
    if survivors:
        print(f"  sample surviving ids       : {sorted(survivors)[:10]}")


if __name__ == "__main__":
    main()
