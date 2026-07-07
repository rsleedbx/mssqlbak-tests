#!/usr/bin/env python3
"""Probe inner structure of ARCHIVE enc=5 blobs for archive_part_all vs archive_part_single."""
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
from mssqlbak.xpress import _native_decompress_with_pos

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)
_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
WANT_TABLES = {"archive_part_all", "archive_part_single"}


def find_ffff(data: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = data.find(b"\xff\xff", pos)
        if pos < 0:
            break
        if pos % 2 == 0:
            out.append(pos)
        pos += 2
    return out


def probe(inner: bytes, label: str) -> None:
    markers = find_ffff(inner)
    print(f"\n{label}")
    print(f"  inner={len(inner)}  #0xFFFF={len(markers)}")
    for i, m in enumerate(markers[:10]):
        if m + 8 > len(inner):
            break
        n_block = _U32.unpack_from(inner, m + 2)[0]
        mk = _U16.unpack_from(inner, m + 6)[0]
        is_compressed = 0xFFF0 <= mk <= 0xFFFE
        xp = m + 8
        decomp_info = ""
        if is_compressed and _native_decompress_with_pos:
            for sz in (65536, 32768, 16384):
                try:
                    out_b, consumed = _native_decompress_with_pos(inner[xp:], sz)
                    decomp_info = f" → out={sz} consumed={consumed}"
                    break
                except Exception:
                    continue
        print(
            f"  [{i}] m={m} n_block={n_block} mk=0x{mk:04X}"
            f" {'XPRESS' if is_compressed else 'RAW'}{decomp_info}"
        )


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for tbl in schema.tables:
        if tbl.name not in WANT_TABLES:
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        print(f"\n=== {tbl.name}: {len(segs)} segments total")
        col_ids_seen: set[tuple[int, int]] = set()
        for seg in segs[:20]:
            print(
                f"  seg col_id={seg.col_id} enc={seg.enc_type}"
                f" hobt={seg.hobt_id} blob_id={seg.blob_id}"
                f" blob_sz={len(all_blobs.get(seg.blob_id, b''))}"
            )
            key = (seg.col_id, seg.enc_type)
            if seg.enc_type == 5 and key not in col_ids_seen:
                col_ids_seen.add(key)
                raw = all_blobs.get(seg.blob_id, b"")
                inner = _unwrap_archive_blob(raw)
                probe(inner, f"  col_id={seg.col_id} hobt={seg.hobt_id} blob={len(raw)}")


if __name__ == "__main__":
    main()
