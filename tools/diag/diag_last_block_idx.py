#!/usr/bin/env python3
"""Inspect the index entries for the last sub-block of archive_part_mixed hobt2."""
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
TARGET_BLOB = 148124
FULL_SZ = 65536
_NULL = 0xFFFE
_LO, _HI = 0xFFF0, 0xFFFE


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for tbl in schema.tables:
        if tbl.name != "archive_part_mixed":
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)
        for seg in sorted(segs, key=lambda s: s.hobt_id):
            if seg.col_id != 3 or seg.enc_type != 5:
                continue
            raw = all_blobs.get(seg.blob_id, b"")
            if len(raw) != TARGET_BLOB:
                continue
            inner = _unwrap_archive_blob(raw)

            # Walk to the last sub-block sequentially
            pos = 0
            blocks = []
            while True:
                m = -1
                scan = pos
                while scan + 1 < len(inner):
                    if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                        m = scan
                        break
                    scan += 2
                if m < 0 or m + 8 > len(inner):
                    break
                n_block = _U32.unpack_from(inner, m + 2)[0]
                if n_block == 0 or n_block > 35000:
                    break
                mk = _U16.unpack_from(inner, m + 6)[0]
                xp = m + 8
                if _LO <= mk <= _HI:
                    b, consumed = decompress_with_pos(inner, xp, FULL_SZ)
                    pos = xp + consumed
                else:
                    b = decompress_until_input(inner, xp, len(inner))
                    pos = len(inner)
                blocks.append((n_block, mk, b))
                if not (_LO <= mk <= _HI):
                    break

            # Inspect the last block
            n_block, mk, pool_idx = blocks[-1]
            n_valid = 2181
            idx_start = len(pool_idx) - n_valid * 2
            print(
                f"Last block: n_block={n_block} mk=0x{mk:04X}"
                f" decomp={len(pool_idx)} idx_start={idx_start}"
            )

            # Print index entries at expected null positions (every 500th row from 32820)
            # Null positions within last block: 180, 680, 1180, 1680, 2180
            null_positions = [i for i in range(n_valid) if (32820 + i) % 500 == 0]
            print(f"Expected null row positions (0-indexed): {null_positions}")
            for np in null_positions:
                off = idx_start + np * 2
                if off + 2 <= len(pool_idx):
                    v = _U16.unpack_from(pool_idx, off)[0]
                    is_null = v == _NULL
                    print(f"  row[{np}] idx_off={off} value=0x{v:04X} {'NULL' if is_null else 'non-null'}")
                else:
                    print(f"  row[{np}] idx_off={off} OUT OF BOUNDS (decomp={len(pool_idx)})")

            # Also print first and last 5 index entries
            print("\nFirst 5 index entries:")
            for i in range(5):
                off = idx_start + i * 2
                v = _U16.unpack_from(pool_idx, off)[0]
                print(f"  row[{i}] = 0x{v:04X} = {v}")

            print("Last 5 index entries:")
            for i in range(n_valid - 5, n_valid):
                off = idx_start + i * 2
                if off + 2 > len(pool_idx):
                    print(f"  row[{i}] OUT OF BOUNDS")
                    continue
                v = _U16.unpack_from(pool_idx, off)[0]
                print(f"  row[{i}] = 0x{v:04X} = {v}")

            # Scan all index entries for 0xFFFE
            null_found = sum(
                1 for i in range(n_valid)
                if idx_start + i * 2 + 2 <= len(pool_idx)
                and _U16.unpack_from(pool_idx, idx_start + i * 2)[0] == _NULL
            )
            print(f"\nTotal 0xFFFE entries found: {null_found}")
            # Also search for 0xFFFE anywhere in pool_idx
            total_ffffe = sum(
                1 for i in range(0, len(pool_idx) - 1, 2)
                if _U16.unpack_from(pool_idx, i)[0] == _NULL
            )
            print(f"Total 0xFFFE anywhere in pool_idx: {total_ffffe}")
            break
        break


if __name__ == "__main__":
    main()
