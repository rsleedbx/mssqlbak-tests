#!/usr/bin/env python3
"""Count nulls per sub-block for archive_part_mixed hobt2 (XPRESS, blob=148124).

Compares expected null counts (code NULL every 500th row) against decoded values.
"""
from __future__ import annotations

import struct
from pathlib import Path

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.columnstore import (  # type: ignore[attr-defined]
    _bootstrap,
    _collect_blobs,
    _read_column_segments,
    _unwrap_archive_blob,
)
from mssqlbak.xpress import decompress_with_pos, decompress_until_input

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)
_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
NULL_EVERY = 500
TARGET_BLOB_SIZE = 148124
FULL_SZ = 65536
_NULL_SENTINEL = 0xFFFE
_LO = 0xFFF0
_HI = 0xFFFE


def decode_block(pool_idx: bytes, n_valid: int) -> tuple[int, int]:
    """Return (null_count, non_null_count) for the given pool+index block."""
    idx_start = len(pool_idx) - n_valid * 2
    if idx_start < 0:
        return 0, n_valid
    nulls = 0
    non_nulls = 0
    for i in range(n_valid):
        off = idx_start + i * 2
        if off + 2 > len(pool_idx):
            break
        v = _U16.unpack_from(pool_idx, off)[0]
        if v == _NULL_SENTINEL:
            nulls += 1
        else:
            non_nulls += 1
    return nulls, non_nulls


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    # Find the first XPRESS enc=5 blob of archive_part_mixed col_id=3
    for tbl in schema.tables:
        if tbl.name != "archive_part_mixed":
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        for seg in sorted(segs, key=lambda s: s.hobt_id):
            if seg.col_id != 3 or seg.enc_type != 5:
                continue
            raw = all_blobs.get(seg.blob_id, b"")
            if len(raw) != TARGET_BLOB_SIZE:
                continue
            inner = _unwrap_archive_blob(raw)
            print(
                f"hobt={seg.hobt_id} blob={len(raw)} inner={len(inner)}"
            )

            n_rows = 35000
            pos = 0
            row_offset = 0
            total_nulls = 0
            block_idx = 0

            while row_offset < n_rows:
                m = -1
                scan = pos
                while scan + 1 < len(inner):
                    if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                        m = scan
                        break
                    scan += 2

                if m < 0 or m + 8 > len(inner):
                    print(f"  [{block_idx}] NO MARKER FOUND at pos={pos}")
                    break

                n_block = _U32.unpack_from(inner, m + 2)[0]
                mk = _U16.unpack_from(inner, m + 6)[0]
                xp = m + 8

                if _LO <= mk <= _HI:
                    pool_idx_b, consumed = decompress_with_pos(inner, xp, FULL_SZ)
                    pos = xp + consumed
                else:
                    pool_idx_b = decompress_until_input(inner, xp, len(inner))
                    pos = len(inner)

                n_rows_left = n_rows - row_offset
                n_valid = min(n_block, n_rows_left)
                nulls, non_nulls = decode_block(pool_idx_b, n_valid)

                # Expected nulls in rows [row_offset, row_offset+n_valid)
                expected = sum(
                    1
                    for r in range(row_offset + 1, row_offset + n_valid + 1)
                    if r % NULL_EVERY == 0
                )

                total_nulls += nulls
                status = "✓" if nulls == expected else f"✗ (expected {expected})"
                print(
                    f"  [{block_idx}] m={m} mk=0x{mk:04X} n_block={n_block}"
                    f" n_valid={n_valid} nulls={nulls}/{expected} {status}"
                    f" decomp={len(pool_idx_b)}"
                )

                row_offset += n_valid
                block_idx += 1

            print(f"  TOTAL: {total_nulls} nulls (expected 70)")
            break
        break


if __name__ == "__main__":
    main()
