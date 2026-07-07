#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Inspect pool bytes and index entries for archive_part_roundtrip block 0.

Shows what the pool and index actually contain to understand the layout.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (  # type: ignore[attr-defined]
    _bootstrap,
    _collect_blobs,
    _enc5_archive_has_compressed_subblocks,
    _read_column_segments,
    _unwrap_archive_blob,
)
from mssqlbak.pages import PageStore
from mssqlbak.xpress import decompress_with_pos

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)
_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
_FULL_SZ = 65536
_MARKER_LO = 0xFFF0
_MARKER_HI = 0xFFFE
COL_WIDTH = 10


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for tbl in schema.tables:
        if tbl.name != "archive_part_roundtrip":
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        for seg in segs:
            if seg.col_id != 3 or seg.enc_type != 5:
                continue
            raw = all_blobs.get(seg.blob_id, b"")
            inner = _unwrap_archive_blob(raw)
            if not _enc5_archive_has_compressed_subblocks(inner):
                continue

            print(f"hobt={seg.hobt_id} blob={len(raw)} n_rows={seg.n_rows}")

            # Get block 0 (first full-size sub-block)
            scan = 0
            while scan + 1 < len(inner):
                if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                    break
                scan += 2

            m = scan
            n_block = _U32.unpack_from(inner, m + 2)[0]
            mk = _U16.unpack_from(inner, m + 6)[0]
            xpress_start = m + 8

            print(f"  block 0: m={m} mk=0x{mk:04X} n_block={n_block}")

            pool_idx_b, consumed = decompress_with_pos(inner, xpress_start, _FULL_SZ)
            idx_start = len(pool_idx_b) - n_block * 2
            print(f"  idx_start={idx_start}  pool_size={idx_start}")

            # Print first 10 pool entries (bytes 0:100)
            print("\n  First 10 pool entries (pool_idx_b[0:100]):")
            for k in range(10):
                entry = pool_idx_b[k * COL_WIDTH : (k + 1) * COL_WIDTH]
                try:
                    val = entry.decode("ascii").rstrip()
                except Exception:
                    val = repr(entry)
                print(f"    pool[{k*COL_WIDTH}:{(k+1)*COL_WIDTH}] = {val!r}")

            # Print last 10 pool entries (bytes around idx_start)
            print(f"\n  Last 10 pool entries before idx_start={idx_start}:")
            for k in range(10, 0, -1):
                off = idx_start - k * COL_WIDTH
                if off < 0:
                    continue
                entry = pool_idx_b[off : off + COL_WIDTH]
                try:
                    val = entry.decode("ascii").rstrip()
                except Exception:
                    val = repr(entry)
                print(f"    pool[{off}:{off+COL_WIDTH}] = {val!r}")

            # Count non-null index entries and their range
            print(f"\n  Index entry stats (n_block={n_block}):")
            nulls = 0
            min_off = 999999
            max_off = -1
            first_5 = []
            last_5 = []
            for i in range(n_block):
                off = idx_start + i * 2
                if off + 2 > len(pool_idx_b):
                    break
                v = _U16.unpack_from(pool_idx_b, off)[0]
                if v == 0xFFFE:
                    nulls += 1
                else:
                    min_off = min(min_off, v)
                    max_off = max(max_off, v)
                if i < 5:
                    first_5.append(v)
                if i >= n_block - 5:
                    last_5.append(v)

            print(f"    nulls={nulls}, min_pool_off={min_off}, max_pool_off={max_off}")
            print(f"    first 5 entries: {first_5}")
            print(f"    last 5 entries: {last_5}")

            # Print what the pool values are for first/last entries
            for tag, entries in (("first", first_5), ("last", last_5)):
                print(f"\n  Pool values for {tag} 5 rows:")
                for v in entries:
                    if v == 0xFFFE:
                        print("    NULL")
                    elif 0 <= v < idx_start:
                        entry = pool_idx_b[v : v + COL_WIDTH]
                        try:
                            val = entry.decode("ascii").rstrip()
                        except Exception:
                            val = repr(entry)
                        print(f"    off={v} → {val!r}")
                    else:
                        print(f"    off={v} (OOB)")

            break
        break


if __name__ == "__main__":
    main()
