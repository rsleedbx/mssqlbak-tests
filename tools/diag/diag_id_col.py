#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Compare id column (enc=4) vs code column (enc=5) for archive_part_roundtrip partition 1.

Shows what id the id-column assigns to the first few and last few physical rows.
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
_I64 = struct.Struct("<q")
_FULL_SZ = 65536
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

        # Find the XPRESS enc=5 segment (code column, col_id=3) for the FIRST hobt
        code_segs = [
            seg
            for seg in segs
            if seg.col_id == 3
            and seg.enc_type == 5
            and _enc5_archive_has_compressed_subblocks(
                _unwrap_archive_blob(all_blobs.get(seg.blob_id, b""))
            )
        ]
        if not code_segs:
            print("No XPRESS code segments found")
            return

        code_seg = code_segs[0]
        target_hobt = code_seg.hobt_id
        print(f"target hobt={target_hobt}  code col_id={code_seg.col_id}")

        # Find the id column (col_id=1 or 2?) for the same hobt
        id_segs = [
            seg
            for seg in segs
            if seg.hobt_id == target_hobt and seg.enc_type == 4
        ]
        print(f"enc=4 segs for same hobt: {[(s.col_id, s.blob_id) for s in id_segs]}")

        for id_seg in id_segs:
            blob = all_blobs.get(id_seg.blob_id, b"")
            if len(blob) < 10:
                continue
            # Try to decode first few values from enc=4 blob
            # enc=4 format: header + bitpacked deltas
            print(f"\nid column: col_id={id_seg.col_id} blob_len={len(blob)} n_rows={id_seg.n_rows}")
            print(f"  mn={id_seg.mn} null_val={id_seg.null_val}")
            print(f"  First 20 bytes: {blob[:20].hex()}")

        # Now check the code column block 0: first and last valid entries with TRUE idx_start
        raw = all_blobs.get(code_seg.blob_id, b"")
        inner = _unwrap_archive_blob(raw)
        print(f"\ncode col blob_len={len(raw)} inner_len={len(inner)}")

        # Get block 0
        scan = 0
        while scan + 1 < len(inner):
            if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                break
            scan += 2
        m = scan
        n_block = _U32.unpack_from(inner, m + 2)[0]
        mk = _U16.unpack_from(inner, m + 6)[0]
        xpress_start = m + 8

        pool_idx_b, _ = decompress_with_pos(inner, xpress_start, _FULL_SZ)
        naive_idx = _FULL_SZ - n_block * 2
        rounded_idx = (naive_idx // COL_WIDTH) * COL_WIDTH
        print(f"\nblock 0: n_block={n_block} mk=0x{mk:04X}")
        print(f"  naive_idx_start={naive_idx}  rounded={rounded_idx}")

        # Scan for True idx_start: where are 0x0000 entries?
        print("\nSearching for idx_start where entry 0 → pool_off=0 (row 0=id=1 for asc, or last row for desc):")
        for candidate in range(rounded_idx - 20, rounded_idx + 20, 2):
            if 0 <= candidate and candidate + 2 <= _FULL_SZ:
                v = _U16.unpack_from(pool_idx_b, candidate)[0]
                v1 = _U16.unpack_from(pool_idx_b, candidate + 2)[0]
                if v == 0x0000:
                    pool_val = pool_idx_b[0:10].decode("ascii")
                    print(f"  candidate {candidate}: entry[0]=0x0000 (pool[0:10]={pool_val!r}), entry[1]={v1:#06x}")

        # Show first and last 10 index entries from each candidate
        for label, idx in (("naive", naive_idx), ("rounded", rounded_idx)):
            print(f"\n  Index from {label} ({idx}):")
            for i in range(10):
                off = idx + i * 2
                if off + 2 > _FULL_SZ:
                    break
                v = _U16.unpack_from(pool_idx_b, off)[0]
                if v == 0xFFFE:
                    decoded = "NULL"
                elif v + 10 <= idx:
                    decoded = pool_idx_b[v : v + 10].decode("ascii", errors="replace").rstrip()
                else:
                    decoded = f"(OOB: {v})"
                print(f"    [{i}]: {v:#06x} → {decoded!r}")

        break


if __name__ == "__main__":
    main()
