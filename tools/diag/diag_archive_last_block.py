#!/usr/bin/env python3
"""Probe the last compressed sub-block of archive_part_single col=3 and col=4.

Determines whether the last sub-block (mk != 0xFFFx) uses XPRESS
and what xpress_start (m+6 vs m+8) produces valid output.
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
from mssqlbak.xpress import _native_decompress_with_pos, decompress_until_input

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)
_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
WANT_TABLE = "archive_part_single"


def find_next_even_ffff(data: bytes, start: int) -> int:
    """Find next u16-aligned 0xFFFF at or after start."""
    pos = start
    while pos + 1 < len(data):
        if data[pos] == 0xFF and data[pos + 1] == 0xFF:
            return pos
        pos += 2
    return -1


def probe_sequential(inner: bytes, label: str, col_width: int = 10) -> None:
    """Walk sub-blocks sequentially using decompress_with_pos consumed counts."""
    print(f"\n{label}  inner={len(inner)}")
    pos = 0
    sub_idx = 0
    while pos < len(inner):
        m = find_next_even_ffff(inner, pos)
        if m < 0 or m + 8 > len(inner):
            break

        n_block = _U32.unpack_from(inner, m + 2)[0]
        mk = _U16.unpack_from(inner, m + 6)[0]
        pre_meta = inner[pos:m]

        is_xpress_marker = 0xFFF0 <= mk <= 0xFFFE

        xpress_start8 = m + 8
        xpress_start6 = m + 6

        result8 = ""
        result6 = ""

        if _native_decompress_with_pos:
            for xstart, tag in ((xpress_start8, "m+8"), (xpress_start6, "m+6")):
                for sz in (65536, 32768, 26132, 22000):
                    try:
                        out_b, consumed = _native_decompress_with_pos(inner[xstart:], sz)
                        info = f"{tag}({sz})→consumed={consumed} "
                        if tag == "m+8":
                            result8 = info
                        else:
                            result6 = info
                        break
                    except Exception:
                        continue

        # Also try decompress_until_input for m+8
        try:
            uit = decompress_until_input(inner, xpress_start8, len(inner))
            result8 += f"until_input→{len(uit)}"
        except Exception as e:
            result8 += f"until_input→ERR({e})"

        print(
            f"  [{sub_idx}] m={m} pre_meta={len(pre_meta)}B"
            f" n_block={n_block} mk=0x{mk:04X}"
            f" {'MARKER' if is_xpress_marker else 'other'}"
        )
        print(f"    m+8: {result8}")
        if not is_xpress_marker:
            print(f"    m+6: {result6}")

        # Advance past this sub-block
        if is_xpress_marker and _native_decompress_with_pos:
            consumed = 0
            for sz in (65536, 32768):
                try:
                    _, consumed = _native_decompress_with_pos(inner[xpress_start8:], sz)
                    break
                except Exception:
                    continue
            if consumed == 0:
                break
            pos = xpress_start8 + consumed
        else:
            # Last block: advance to end
            pos = len(inner)

        sub_idx += 1


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for tbl in schema.tables:
        if tbl.name != WANT_TABLE:
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        seen: set[int] = set()
        for seg in segs:
            if seg.enc_type != 5:
                continue
            if seg.col_id in seen:
                continue
            seen.add(seg.col_id)
            raw = all_blobs.get(seg.blob_id, b"")
            if not raw:
                continue
            inner = _unwrap_archive_blob(raw)
            probe_sequential(
                inner,
                f"col_id={seg.col_id} hobt={seg.hobt_id} blob={len(raw)}",
                col_width=10,
            )


if __name__ == "__main__":
    main()
