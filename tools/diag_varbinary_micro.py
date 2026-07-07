#!/usr/bin/env python3
"""Diagnostic: dump the enc=5 Format C blob for the F1 micro VARBINARY fixture.

Maps the XPRESS-decompressed pool + index to the 7 known values so M1 (pool
entry encoding), M2 (index encoding), and M3 (pool/index boundary) can be read
by hand.  Read-only; prints to stdout.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

from mssqlbak.catalog import recover_schema, _bootstrap  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.columnstore import (  # noqa: E402
    _collect_blobs,
    _read_column_segments,
    _unwrap_archive_blob,
    _find_enc5_xpress_marker,
    _xpress_decompress_chunk,
    _enc5_item_size,
    _u16,
)
from tools.make_cci_varbinary_micro_fixture import MICRO_ROWS  # noqa: E402

VARBINARY = 165


def hx(b: bytes) -> str:
    return b.hex()


def dump_table(store, schema, boot, all_blobs, table_name: str) -> None:
    tbl = next(t for t in schema.tables if t.name == table_name)
    rowset_ids = {au.rowset_id for au in tbl.alloc_units}
    segs = _read_column_segments(store, boot, rowset_ids)
    col_by_id = {col.colid + 1: col for col in tbl.columns}

    print(f"\n{'=' * 72}\nTABLE {table_name}\n{'=' * 72}")
    for s in sorted(segs, key=lambda x: (x.seg_id, x.col_id)):
        col = col_by_id.get(s.col_id)
        if col is None or col.type_id != VARBINARY:
            continue
        raw = all_blobs.get(s.blob_id, b"")
        blob = _unwrap_archive_blob(raw)
        item_size = _enc5_item_size(col)
        print(f"\ncol={col.name} colid={col.colid} enc={s.enc_type} "
              f"n_rows={s.n_rows} has_null={s.has_null} "
              f"max_length={col.max_length} _enc5_item_size={item_size}")
        print(f"  blob len(raw)={len(raw)} len(unwrapped)={len(blob)}")
        if s.enc_type != 5:
            print("  (not enc=5 — skipping Format C dump)")
            continue
        h38 = _u16(blob, 38)
        print(f"  u16@38={h38}  (Format C iff == n_rows={s.n_rows})")
        marker = _find_enc5_xpress_marker(blob, expected_size=item_size)
        marker_any = _find_enc5_xpress_marker(blob, expected_size=0)
        print(f"  marker(expected={item_size}): {marker}")
        print(f"  marker(any):              {marker_any}")
        m = marker or marker_any
        if m is None:
            print("  no XPRESS marker found")
            continue
        marker_off, sz, xpress_off = m
        print(f"  marker_off={marker_off} item_size_hdr={sz} xpress_off={xpress_off}")
        d = _xpress_decompress_chunk(blob, xpress_off, len(blob), 1 << 20)
        if d is None:
            print("  decompress failed")
            continue
        print(f"  decompressed len(d)={len(d)}")
        # Hex dump of the decompressed buffer (full when small).
        dump_limit = len(d) if len(d) <= 1536 else 256
        print(f"  --- decompressed buffer (first {dump_limit} bytes, 16/line) ---")
        for off in range(0, dump_limit, 16):
            print(f"    {off:5d}: {d[off:off + 16].hex(' ')}")
        if len(d) > dump_limit:
            print(f"    ... ({len(d) - dump_limit} more bytes) ...")
        # Interpret as [pool][n_rows x u16 index] for plausible n_non_null.
        n_rows = s.n_rows
        print("  --- candidate index tables (showing first 32 entries) ---")
        shown = 0
        for nn in range(0, n_rows + 1):
            idx_start = nn * sz
            if idx_start + n_rows * 2 > len(d):
                break
            idx = [_u16(d, idx_start + i * 2) for i in range(min(n_rows, 32))]
            print(f"    n_non_null={nn} idx_start={idx_start}: {idx}")
            shown += 1
            if shown >= 40:
                print("    ... (more layouts omitted) ...")
                break


_FIXTURES = {
    "cci_varbinary_micro_full.bak": [
        "cci_varbinary_micro",
        "cci_varbinary_micro_nullonly",
        "cci_varbinary_micro_1byte",
    ],
    "cci_varbinary_probe_full.bak": [
        "cci_varbinary_small_rowgroup",  # F5: 128 rows — Format C candidate
        "cci_varbinary_narrowmax",       # F3: VARBINARY(4), 1200 rows
        "cci_varbinary_maxwidth",        # F2: 16-byte values, 1200 rows
    ],
    "cci_types_large_full.bak": [
        "cci_varbinary",                 # reference: the original K3B case
    ],
}


def main() -> int:
    fdir = _REPO / "tests" / "fixtures_2022"
    print("MICRO_ROWS expected values:")
    for rid, (lit, val) in MICRO_ROWS.items():
        print(f"  id={rid} lit={lit} -> {None if val is None else hx(val)}")

    for fname, tables in _FIXTURES.items():
        fixture = fdir / fname
        if not fixture.exists():
            print(f"\n(missing fixture: {fixture})")
            continue
        print(f"\n########## {fname} ##########")
        store = PageStore.from_bak(fixture)
        schema = recover_schema(store)
        boot = _bootstrap(store)
        all_blobs = _collect_blobs(store)
        for tname in tables:
            try:
                dump_table(store, schema, boot, all_blobs, tname)
            except StopIteration:
                print(f"\n(table {tname} not found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
