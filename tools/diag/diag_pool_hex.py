#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Dump raw hex of pool and index regions for roundtrip block 0."""
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


def hexdump(data: bytes, offset: int = 0, label: str = "") -> None:
    if label:
        print(f"  {label}")
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {offset+i:06x}: {hex_part:<48}  {ascii_part}")


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

            print(f"block 0: m={m} n_block={n_block} mk=0x{mk:04X}")
            pool_idx_b, _ = decompress_with_pos(inner, xpress_start, _FULL_SZ)
            idx_start = _FULL_SZ - n_block * 2
            print(f"idx_start={idx_start}  pool_size={idx_start}")

            print("\nPool bytes [0:80] (first 8 entries if 10-byte each):")
            hexdump(pool_idx_b[:80], 0, "")

            print(f"\nPool bytes around idx_start [{idx_start-20}:{idx_start+20}]:")
            hexdump(pool_idx_b[idx_start - 20 : idx_start + 20], idx_start - 20, "")

            print(f"\nIndex bytes [{idx_start}:{idx_start+40}] (first 20 entries):")
            hexdump(pool_idx_b[idx_start : idx_start + 40], idx_start, "")

            print(f"\nIndex bytes [{_FULL_SZ-40}:{_FULL_SZ}] (last 20 entries):")
            hexdump(pool_idx_b[_FULL_SZ - 40 :], _FULL_SZ - 40, "")

            # What is the true n_block from the pool?
            # Find the maximum non-null index entry (= last pool offset)
            max_off = 0
            for i in range(n_block):
                off = idx_start + i * 2
                if off + 2 > _FULL_SZ:
                    break
                v = _U16.unpack_from(pool_idx_b, off)[0]
                if v != 0xFFFE and v < idx_start:
                    max_off = max(max_off, v)
            print(f"\nmax non-null pool offset in index = {max_off}")
            print(f"last pool entry at [{max_off}:{max_off+20}]:")
            hexdump(pool_idx_b[max_off : max_off + 20], max_off, "")

            break
        break


if __name__ == "__main__":
    main()
