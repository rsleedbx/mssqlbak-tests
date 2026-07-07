#!/usr/bin/env python3
"""Find exact positions of 0xFFFE in last sub-block decompressed data.

Also compares against full-size (65536-byte) sub-block to understand layout.
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
_NULL = 0xFFFE
_LO, _HI = 0xFFF0, 0xFFFE


def find_ffe_positions(data: bytes) -> list[int]:
    """Return u16-aligned positions of 0xFFFE."""
    out = []
    for i in range(0, len(data) - 1, 2):
        if _U16.unpack_from(data, i)[0] == _NULL:
            out.append(i)
    return out


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

            pos = 0
            block_idx = 0
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

                ffffe = find_ffe_positions(b)
                blocks.append((block_idx, n_block, mk, b, ffffe))
                block_idx += 1

                if not (_LO <= mk <= _HI):
                    break

            # Focus on the last block
            bi, n_block, mk, pool_idx, ffffe = blocks[-1]
            n_valid = 2181
            idx_start_end = len(pool_idx) - n_valid * 2  # my current assumption

            print(
                f"Last block [{bi}]: n_block={n_block} mk=0x{mk:04X}"
                f" decomp={len(pool_idx)}"
            )
            print(f"  0xFFFE positions (u16-aligned): {ffffe}")
            print("  Expected null rows (0-indexed): 180, 680, 1180, 1680, 2180")
            print(
                f"\n  HYPOTHESIS A: index at END  → idx_start={idx_start_end}"
            )
            for np in [180, 680, 1180, 1680, 2180]:
                off = idx_start_end + np * 2
                if off + 2 <= len(pool_idx):
                    v = _U16.unpack_from(pool_idx, off)[0]
                    print(f"    row[{np}] off={off} val=0x{v:04X}")
                else:
                    print(f"    row[{np}] off={off} OUT OF BOUNDS")

            print("\n  HYPOTHESIS B: index at BEGINNING → idx_start=0")
            for np in [180, 680, 1180, 1680, 2180]:
                off = np * 2
                if off + 2 <= len(pool_idx):
                    v = _U16.unpack_from(pool_idx, off)[0]
                    print(f"    row[{np}] off={off} val=0x{v:04X} {'NULL' if v==_NULL else ''}")
                else:
                    print(f"    row[{np}] off={off} OUT OF BOUNDS")

            # Check if ffffe positions match either hypothesis
            h_a_null_offs = [idx_start_end + np * 2 for np in [180, 680, 1180, 1680, 2180]]
            h_b_null_offs = [np * 2 for np in [180, 680, 1180, 1680, 2180]]
            print(f"\n  0xFFFE at hypothesis A positions: {[p in ffffe for p in h_a_null_offs]}")
            print(f"  0xFFFE at hypothesis B positions: {[p in ffffe for p in h_b_null_offs]}")

            # First 4 sub-block analysis for reference
            print("\nFull-size sub-blocks (index at END):")
            for bi2, nb2, mk2, b2, ff2 in blocks[:2]:
                n_v = nb2
                i_start = len(b2) - n_v * 2
                null_in_idx = sum(1 for p in ff2 if p >= i_start)
                null_in_pool = sum(1 for p in ff2 if p < i_start)
                print(
                    f"  [{bi2}] n_block={nb2} decomp={len(b2)} idx_start={i_start}"
                    f" 0xFFFE in_idx={null_in_idx} in_pool={null_in_pool}"
                )
            break
        break


if __name__ == "__main__":
    main()
