#!/usr/bin/env python3
"""Show all hobts and enc=5 blob structures for all 4 archive_part_* tables."""
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
    _enc5_archive_has_compressed_subblocks,
)

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)
_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
WANT_COL_ID = 3  # 'code'


def first_mk(inner: bytes) -> str:
    pos = 0
    while pos + 7 < len(inner):
        if inner[pos] == 0xFF and inner[pos + 1] == 0xFF:
            mk = _U16.unpack_from(inner, pos + 6)[0]
            n_block = _U32.unpack_from(inner, pos + 2)[0]
            return f"mk=0x{mk:04X} n_block={n_block}"
        pos += 2
    return "no-marker"


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    all_blobs = _collect_blobs(store)

    for tbl in schema.tables:
        if not tbl.name.startswith("archive_part_"):
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        enc5_segs = [s for s in segs if s.col_id == WANT_COL_ID and s.enc_type == 5]
        print(f"\n=== {tbl.name}: {len(enc5_segs)} enc=5 code segments")

        for seg in sorted(enc5_segs, key=lambda s: s.hobt_id):
            raw = all_blobs.get(seg.blob_id, b"")
            inner = _unwrap_archive_blob(raw)
            compressed = _enc5_archive_has_compressed_subblocks(inner)
            fmt = "XPRESS" if compressed else "RAW"
            fmk = first_mk(inner)
            print(
                f"  hobt={seg.hobt_id} seg={seg.seg_id}"
                f" blob={len(raw)} inner={len(inner)} {fmt} | {fmk}"
            )


if __name__ == "__main__":
    main()
