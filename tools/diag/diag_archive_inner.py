#!/usr/bin/env python3
"""Probe inner structure of failing ARCHIVE partition blobs.

Runs after _unwrap_archive_blob and shows how sub-blocks are laid out.
"""
from __future__ import annotations

import struct
from pathlib import Path

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import _unwrap_archive_blob  # type: ignore[attr-defined]
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


def _find_ffff_markers(data: bytes) -> list[int]:
    """Return u16-aligned positions of 0xFFFF in data."""
    positions = []
    pos = 0
    while pos + 1 < len(data):
        if data[pos] == 0xFF and data[pos + 1] == 0xFF:
            positions.append(pos)
        pos += 2
    return positions


def probe_blob(blob: bytes, label: str) -> None:
    inner = _unwrap_archive_blob(blob)
    print(f"\n{label}")
    print(f"  blob size: {len(blob)}, inner size: {len(inner)}")

    markers = _find_ffff_markers(inner)
    print(f"  0xFFFF markers: {len(markers)} at positions {markers[:8]}")

    for i, m in enumerate(markers[:8]):
        n_block = _U32.unpack_from(inner, m + 2)[0] if m + 6 <= len(inner) else 0
        marker_u16 = _U16.unpack_from(inner, m + 6)[0] if m + 8 <= len(inner) else 0
        print(
            f"  sub-block {i}: m={m} n_block={n_block} marker=0x{marker_u16:04X}"
        )
        xpress_start = m + 8
        if 0xFFF0 <= marker_u16 <= 0xFFFF and xpress_start < len(inner):
            try:
                decomp, consumed = decompress_with_pos(inner, xpress_start, 65536)
                print(
                    f"    -> decomp_with_pos(65536): consumed={consumed} out={len(decomp)}"
                )
            except Exception as exc:
                print(f"    -> decomp_with_pos(65536) FAILED: {exc}")
                try:
                    decomp, consumed = decompress_with_pos(inner, xpress_start, 32768)
                    print(
                        f"    -> decomp_with_pos(32768): consumed={consumed} out={len(decomp)}"
                    )
                except Exception as exc2:
                    print(f"    -> decomp_with_pos(32768) FAILED: {exc2}")


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)

    target_tables = {"archive_part_all", "archive_part_mixed", "archive_part_single"}
    for tbl in schema.tables:
        if tbl.name not in target_tables:
            continue
        hobts = [p.hobt_id for p in getattr(tbl, "partitions", [])]
        print(f"\n=== Table: {tbl.name}, partitions/hobts: {hobts[:4]}")


if __name__ == "__main__":
    main()
