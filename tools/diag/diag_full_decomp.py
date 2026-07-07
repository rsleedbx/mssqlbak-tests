#!/usr/bin/env python3
"""Compare decompress_until_input vs decompress_with_pos(65536) for last sub-block.

Looking for 0xFFFE positions in both to understand the true index layout.
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


def find_ffe(data: bytes) -> list[int]:
    return [i for i in range(0, len(data) - 1, 2) if _U16.unpack_from(data, i)[0] == _NULL]


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

            # Walk to the last sub-block
            pos = 0
            last_xp = 0
            last_n_block = 0
            block_idx = 0

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
                    last_n_block = n_block
                    pos = len(inner)
                    break
                block_idx += 1

            print(f"Last sub-block index: {block_idx}")
            print(f"xpress_start: {last_xp}, n_block: {last_n_block}")
            print(f"Remaining compressed bytes: {len(inner) - last_xp}")

            n_valid = 2181

            # Compare until_input vs with_pos(65536)
            b_small = decompress_until_input(inner, last_xp, len(inner))
            b_large, consumed = decompress_with_pos(inner, last_xp, FULL_SZ)

            print(f"\ndecompress_until_input → {len(b_small)} bytes")
            ff_small = find_ffe(b_small)
            print(f"  0xFFFE positions: {ff_small}")

            print(f"\ndecompress_with_pos(65536) → {len(b_large)} bytes, consumed={consumed}")
            ff_large = find_ffe(b_large)
            # Only show first 20 to avoid clutter
            print(f"  0xFFFE positions: {ff_large[:30]} ...")

            # For b_small: what is idx_start if we align to col_width=10?
            idx_approx = len(b_small) - n_valid * 2  # 21763
            idx_aligned = (idx_approx // 10) * 10  # 21760

            print(f"\nb_small idx_approx={idx_approx} idx_aligned={idx_aligned}")
            # Check nulls at various idx_start candidates near idx_approx
            for cand in range(idx_aligned + 20, idx_aligned - 200, -10):
                if cand < 0:
                    break
                positions_match = all(
                    (cand + null_pos * 2) in ff_small
                    for null_pos in [180, 680, 1180, 1680, 2180]
                )
                if positions_match:
                    print(f"  MATCH: idx_start={cand}")
                    break
            else:
                # Try all positions systematically
                print("  No clean match found near idx_approx")
                # Find by scanning: the difference between consecutive nulls should be 500
                print(f"  Null spacing: {[ff_small[i+1]-ff_small[i] for i in range(len(ff_small)-1)]}")

            break
        break


if __name__ == "__main__":
    main()
