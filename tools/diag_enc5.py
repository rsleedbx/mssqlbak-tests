"""Diagnostic for enc=5 Format C/D column segments in columnstore_minimal.bak."""
import pathlib
import struct
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (
    _bootstrap, _collect_blobs, _read_column_segments, _enc5_item_size,
    _find_enc5_xpress_marker,
)
from mssqlbak.xpress import decompress_chunk as _xdc

BAK = pathlib.Path("tests/fixtures_2022/columnstore_minimal.bak")


def u16(d, off):
    return struct.unpack_from("<H", d, off)[0]


def scan_format_d_validity(d, n_non_null, item_size):
    """Scan for idx_start by validity: find first idx_start where ALL n_non_null
    index entries at [idx_start : idx_start + n_non_null * 2] are valid offsets
    (< idx_start AND divisible by item_size).  Skip all-zero candidates."""
    for nn in range(0, len(d) // max(item_size, 1) + 2):
        idx_start = nn * item_size
        if idx_start + n_non_null * 2 > len(d):
            break
        valid = True
        n_zeros = 0
        for i in range(n_non_null):
            v = u16(d, idx_start + i * 2)
            if v >= idx_start or v % item_size != 0:
                valid = False
                break
            if v == 0:
                n_zeros += 1
        if valid:
            all_zero = (n_zeros == n_non_null)
            yield (nn, idx_start, all_zero)
            if not all_zero:
                return  # first non-trivial candidate found


def diag_segment(tbl, col_name):
    store = PageStore.from_bak(BAK)
    blobs = _collect_blobs(store)
    boot = _bootstrap(store)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    table = tables.get(tbl)
    if table is None:
        print(f"Table {tbl!r} not found")
        return
    col = next((c for c in table.columns if c.name == col_name), None)
    if col is None:
        print(f"Col {col_name!r} not found in {tbl}")
        return

    item_size = _enc5_item_size(col)
    print(f"\n{'='*70}")
    print(f"  {tbl}.{col_name}  type_id={col.type_id}  max_len={col.max_length}  "
          f"scale={col.scale}  item_size={item_size}")
    print(f"{'='*70}")

    rowset_ids = {au.rowset_id for au in table.alloc_units}
    segs = [s for s in _read_column_segments(store, boot, rowset_ids)
            if s.col_id == col.colid + 1]

    if not segs:
        print(f"  No enc=5 segments found for colid={col.colid}")
        return

    for seg in segs:
        blob = blobs.get(seg.blob_id)
        if blob is None:
            print(f"  seg_id={seg.seg_id}: blob {seg.blob_id} not found")
            continue
        print(f"\n  seg_id={seg.seg_id}  n_rows={seg.n_rows}  has_null={seg.has_null}  "
              f"enc_type={seg.enc_type}  blob_len={len(blob)}")
        h38 = u16(blob, 38)
        fmt = 'C' if h38 == seg.n_rows else f'D (n_null={h38})'
        print(f"  h38={h38}  → Format {fmt}")

        marker_info = _find_enc5_xpress_marker(blob)
        print(f"  _find_enc5_xpress_marker: {marker_info}")

        if marker_info is None:
            print("  → No C/D marker; segment is Format A or B")
            continue

        marker_off, sz_hdr, xpress_off = marker_info
        print(f"  marker_off={marker_off}  sz_hdr={sz_hdr}  xpress_off={xpress_off}")
        if sz_hdr != item_size:
            print(f"  *** WARNING: sz_hdr ({sz_hdr}) != expected item_size ({item_size}) — FALSE MARKER ***")

        d = _xdc(blob, xpress_off, len(blob), 1 << 20)
        if d is None:
            print("  XPRESS decompression failed")
            continue
        print(f"  decompressed len={len(d)}")

        # Find true data end
        nz_end = len(d)
        while nz_end > 0 and d[nz_end - 1] == 0:
            nz_end -= 1
        print(f"  non-zero region: [0:{nz_end}]  ({nz_end} bytes)")

        if h38 == seg.n_rows:
            # ── Format C ──
            print(f"\n  Format C scan (item_size={item_size}, n_rows={seg.n_rows}):")
            shown = 0
            for nn in range(0, seg.n_rows + 1):
                idx_start = nn * item_size
                if idx_start + seg.n_rows * 2 > len(d):
                    print(f"    Scan stopped: idx_start={idx_start} leaves no room")
                    break
                valid = True
                n_nulls = 0
                for i in range(seg.n_rows):
                    v = u16(d, idx_start + i * 2)
                    if v == 0xFFFE:
                        n_nulls += 1
                        continue
                    if v >= idx_start or v % item_size != 0:
                        valid = False
                        break
                if valid:
                    in_zp = idx_start >= nz_end
                    print(f"    VALID  n_non_null={nn:4d}  idx_start={idx_start:6d}  "
                          f"nulls={n_nulls:4d}  in_zero_pad={in_zp}")
                    shown += 1
                    if shown >= 5:
                        print("    (stopped after 5 valid candidates)")
                        break
        else:
            # ── Format D ──
            n_null = h38
            n_non_null = seg.n_rows - n_null
            print(f"\n  Format D  n_non_null={n_non_null}  n_null={n_null}")

            # Current self-referential scan
            print("  Self-ref scan (current code):")
            for n_dedup_try in range(min(n_non_null, 0xFFFF // max(item_size, 1) + 1), 0, -1):
                cand = n_dedup_try * item_size
                if cand + 2 > len(d):
                    continue
                entry0 = u16(d, cand)
                if entry0 == cand - item_size:
                    print(f"    FOUND  n_dedup={n_dedup_try}  idx_start={cand}  "
                          f"entry[0]={entry0}  expected={cand - item_size}")
                    break
            else:
                print("    NOT FOUND")

            # Proposed validity scan
            print("  Validity scan (proposed):")
            for nn, idx_s, all_zero in scan_format_d_validity(d, n_non_null, item_size):
                in_zp = idx_s >= nz_end
                print(f"    {'ZERO-PAD' if all_zero else 'DATA    '}  "
                      f"n_unique={nn}  idx_start={idx_s}  in_zero_pad={in_zp}")
                if not all_zero:
                    print(f"    Sampling first 6 of {n_non_null} rows:")
                    for i in range(min(6, n_non_null)):
                        v = u16(d, idx_s + i * 2)
                        if v < idx_s:
                            raw = bytes(d[v : v + item_size])
                            try:
                                text = raw.decode("utf-16-le").rstrip("\x00 ")
                            except Exception:
                                text = raw[:8].hex()
                        else:
                            text = f"INVALID(ptr={v})"
                        print(f"      row[{i}]  ptr={v}  → {text!r}")


if __name__ == "__main__":
    diag_segment("cs_100",   "name")
    diag_segment("cs_1000",  "ncf")
    diag_segment("cs_10000", "ncf")
    diag_segment("cs_10000", "dto")
