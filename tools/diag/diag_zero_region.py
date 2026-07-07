#!/usr/bin/env python3
"""Examine what's beyond position 25760 in decompress_with_pos(65536) output.

Determine if it's all zeros, and at what position the last non-zero byte is.
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
TARGET_BLOB = 148124
FULL_SZ = 65536
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

            # Walk to last sub-block
            pos = 0
            last_xp = 0
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
                    _, consumed = decompress_with_pos(inner, xp, FULL_SZ)
                    pos = xp + consumed
                else:
                    last_xp = xp
                    break

            b65 = decompress_with_pos(inner, last_xp, FULL_SZ)[0]
            b_small = decompress_until_input(inner, last_xp, len(inner))

            print("65536-byte output for last sub-block")
            print("  0xFFFE positions: [21760, 22760, 23760, 24760, 25760] (expected)")

            # Find last non-zero byte in 65536 output
            last_nz = -1
            for i in range(len(b65) - 1, -1, -1):
                if b65[i] != 0:
                    last_nz = i
                    break
            print(f"  Last non-zero byte at position {last_nz}")

            # Find last non-zero U16 in 65536 output
            last_nz_u16 = -1
            for i in range(len(b65) - 2, -1, -2):
                if b65[i] != 0 or b65[i + 1] != 0:
                    last_nz_u16 = i
                    break
            print(f"  Last non-zero u16 at position {last_nz_u16} = 0x{_U16.unpack_from(b65, last_nz_u16)[0]:04X}")

            # Show bytes around the boundary [25756:25800]
            print("\n  Bytes [25756:25800] in 65536 output:")
            for i in range(25756, 25800, 2):
                v = _U16.unpack_from(b65, i)[0]
                print(f"    [{i}] 0x{v:04X}")

            # Show where zeros start
            print("\n  Non-zero regions in [25762:65536]:")
            zones = []
            i = 25762
            while i < len(b65) - 1:
                v = _U16.unpack_from(b65, i)[0]
                if v != 0:
                    zones.append((i, v))
                i += 2
            print(f"    Count of non-zero u16s: {len(zones)}")
            if zones:
                print(f"    First 10: {zones[:10]}")
                print(f"    Last 10: {zones[-10:]}")

            # Also check b_small [25762:26125]
            print("\n  Non-zero u16s in b_small [25762:26125]:")
            zones_small = []
            i = 25762
            while i < len(b_small) - 1:
                v = _U16.unpack_from(b_small, i)[0]
                if v != 0:
                    zones_small.append((i, v))
                i += 2
            print(f"    Count: {len(zones_small)}, values: {zones_small[:20]}")

            # Verify idx_start using MAX valid pool offset
            # Assume idx_start=21400, check max of non-null entries
            idx_start_true = 21400
            n_valid = 2181
            col_width = 10
            max_offset = 0
            null_cnt = 0
            for i in range(n_valid):
                off = idx_start_true + i * 2
                v = _U16.unpack_from(b_small, off)[0]
                if v == 0xFFFE:
                    null_cnt += 1
                elif v > max_offset:
                    max_offset = v
            print(f"\n  With idx_start=21400: null_cnt={null_cnt} max_non_null={max_offset}")
            print(f"  max_non_null + col_width = {max_offset + col_width} (should == pool_size=21400)")

            break
        break


if __name__ == "__main__":
    main()
