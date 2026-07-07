#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Inspect the first full-size XPRESS sub-block for archive_part_mixed col_id=3.

Shows raw index entries and compares idx_start placement assumptions.
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
from mssqlbak.xpress import decompress_until_input, decompress_with_pos

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
_NULL = 0xFFFE
COL_WIDTH = 10


def decode_first_entries(pool_idx_b: bytes, n_valid: int, label: str) -> None:
    """Try reading first index entries with both idx_start approaches."""
    naive = len(pool_idx_b) - n_valid * 2
    exact = n_valid * COL_WIDTH  # idx_start = n_valid*col_width (pool is exactly n_valid entries)

    for tag, idx_start in (("naive", naive), ("exact", exact)):
        print(f"\n  [{label} idx_start={idx_start} ({tag})]")
        for i in range(6):
            off = idx_start + i * 2
            if off + 2 > len(pool_idx_b):
                print(f"    [{i}]: OOB")
                break
            val = _U16.unpack_from(pool_idx_b, off)[0]
            if val == _NULL:
                print(f"    [{i}]: NULL(0xFFFE)")
            elif val < idx_start:
                raw = pool_idx_b[val : val + COL_WIDTH]
                try:
                    decoded = raw.decode("ascii").rstrip()
                except Exception:
                    decoded = repr(raw)
                print(f"    [{i}]: off={val} → {decoded!r}")
            else:
                print(f"    [{i}]: off={val} (OOB/invalid for pool_size={idx_start})")


def walk_sub_blocks(inner: bytes, n_rows: int, table_label: str) -> None:
    pos = 0
    block_idx = 0
    rows_seen = 0

    while rows_seen < n_rows:
        scan = pos
        m = -1
        while scan + 1 < len(inner):
            if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                m = scan
                break
            scan += 2

        if m < 0 or m + 8 > len(inner):
            break

        n_block = _U32.unpack_from(inner, m + 2)[0]
        if n_block == 0 or n_block > n_rows:
            break
        mk = _U16.unpack_from(inner, m + 6)[0]
        xpress_start = m + 8
        is_full = _MARKER_LO <= mk <= _MARKER_HI

        n_rows_left = n_rows - rows_seen
        n_valid = min(n_block, n_rows_left)

        print(
            f"\n[{table_label}] block {block_idx}: m={m} mk=0x{mk:04X}"
            f" n_block={n_block} n_valid={n_valid} is_full={is_full}"
        )

        if is_full:
            try:
                pool_idx_b, consumed = decompress_with_pos(inner, xpress_start, _FULL_SZ)
            except Exception as e:
                print(f"  decompress_with_pos FAILED: {e}")
                break
            pos = xpress_start + consumed
        else:
            try:
                pool_idx_b = decompress_until_input(inner, xpress_start, len(inner))
            except Exception as e:
                print(f"  decompress_until_input FAILED: {e}")
                break
            pos = len(inner)

        print(f"  decomp_size={len(pool_idx_b)}")
        decode_first_entries(pool_idx_b, n_valid, f"b{block_idx}")

        rows_seen += n_valid
        block_idx += 1

        if not is_full:
            break


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for table_name in ("archive_part_mixed", "archive_part_roundtrip"):
        for tbl in schema.tables:
            if tbl.name != table_name:
                continue
            rowset_ids = {au.rowset_id for au in tbl.alloc_units}
            segs = _read_column_segments(store, boot, rowset_ids)

            xpress_segs = [
                seg
                for seg in segs
                if seg.col_id == 3
                and seg.enc_type == 5
                and _enc5_archive_has_compressed_subblocks(
                    _unwrap_archive_blob(all_blobs.get(seg.blob_id, b""))
                )
            ]

            for seg in xpress_segs[:1]:
                raw = all_blobs.get(seg.blob_id, b"")
                inner = _unwrap_archive_blob(raw)
                print(
                    f"\n{'='*60}\n{table_name}: hobt={seg.hobt_id}"
                    f" blob={len(raw)} inner={len(inner)} n_rows={seg.n_rows}"
                )
                walk_sub_blocks(inner, seg.n_rows, table_name)
            break


if __name__ == "__main__":
    main()
