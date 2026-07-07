"""Diagnose enc=3 (dictionary) null count bugs for nchar(10) in columnstore_minimal.bak."""
import pathlib
import struct
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (
    _bootstrap, _collect_blobs, _read_column_segments, _read_dict_blob_ids,
    _parse_dict_strings,
    _BP_BPV, _BP_NW,
)

BAK = pathlib.Path("tests/fixtures_2022/columnstore_minimal.bak")


def u16(d, off): return struct.unpack_from("<H", d, off)[0]
def u32(d, off): return struct.unpack_from("<I", d, off)[0]
def i64(d, off): return struct.unpack_from("<q", d, off)[0]


def diag_enc3_segment(tbl, col_name):
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
        print(f"Column {col_name!r} not found in {tbl!r}")
        return

    print(f"\n{'='*70}")
    print(f"  {tbl}.{col_name}  type_id={col.type_id}  max_len={col.max_length}")
    print(f"{'='*70}")

    rowset_ids = {au.rowset_id for au in table.alloc_units}
    segs = [s for s in _read_column_segments(store, boot, rowset_ids)
            if s.col_id == col.colid + 1]
    dict_bid_map = _read_dict_blob_ids(store, boot, rowset_ids)

    for seg in segs:
        blob = blobs.get(seg.blob_id)
        if blob is None:
            continue
        print(f"\n  seg_id={seg.seg_id}  n_rows={seg.n_rows}  has_null={seg.has_null}")
        print(f"  mn={seg.mn}  magnitude={seg.magnitude}  null_val={seg.null_val}")
        print(f"  enc_type={seg.enc_type}  blob_len={len(blob)}")

        bpv = u16(blob, _BP_BPV)
        nw  = u32(blob, _BP_NW)
        print(f"  bpv={bpv}  nw={nw}")

        # Decode dictionary
        dict_bid = dict_bid_map.get((seg.hobt_id, seg.col_id, 0))
        dict_blob = blobs.get(dict_bid) if dict_bid else None
        dictionary = _parse_dict_strings(dict_blob) if dict_blob else []
        print(f"  dict_bid={dict_bid}  dict_entries={len(dictionary)}")
        for i, v in enumerate(dictionary[:15]):
            print(f"    dict[{i}] = {v!r}")

        if nw == 0 and len(blob) >= 28:
            # Compact RLE mode
            rle_offset = u32(blob, 20)
            rle_start = 48 + rle_offset * 8
            mn = seg.mn
            shift = mn - 2
            null_val = seg.null_val

            print("\n  Compact RLE mode:")
            print(f"  rle_offset@20={rle_offset}  rle_start={rle_start}")
            print(f"  mn={mn}  null_val={null_val}  shift=mn-2={shift}")
            print(f"  null_val in compact mode = {null_val}")
            print(f"  null_val - shift = {null_val - shift}  (should be 0 for null)")

            print("\n  RLE pairs (first 25):")
            total_rows = 0
            null_count = 0
            off = rle_start
            pairs = []
            while off + 8 <= len(blob):
                stored = u32(blob, off)
                run    = u32(blob, off + 4)
                off += 8
                if stored == 0 and run == 0:
                    break
                pairs.append((stored, run))

            for stored, run in pairs[:25]:
                direct_stored = stored - shift
                if direct_stored == 0:
                    label = f"NULL  (stored={stored} - shift={shift} = 0)"
                elif direct_stored == 1:
                    label = f"EMPTY (stored={stored} - shift={shift} = 1)"
                elif direct_stored >= 2 and (direct_stored - 2) < len(dictionary):
                    label = f"dict[{direct_stored-2}]={dictionary[direct_stored-2]!r}"
                else:
                    label = f"INVALID (direct_stored={direct_stored})"
                print(f"    stored={stored:3d}  run={run:5d}  → {label}")
                total_rows += run
                if direct_stored == 0:
                    null_count += run

            total_runs = sum(r for _,r in pairs)
            null_in_pairs = sum(r for s,r in pairs if (s - shift) == 0)
            print(f"\n  Total rows from pairs: {total_runs}")
            print(f"  Null rows from pairs: {null_in_pairs}  (expected: {seg.has_null and '142 or 1428'})")

            # Also check: what if null sentinel is seg.null_val, not mn?
            print(f"\n  Alternative: null sentinel = null_val={null_val} directly (no shift):")
            alt_null = sum(r for s, r in pairs if s == null_val)
            print(f"  Null count with direct null_val={null_val}: {alt_null}")

            # Check each distinct stored value
            distinct = sorted(set(s for s, r in pairs))
            print(f"\n  Distinct stored values in pairs: {distinct}")
            for sv in distinct:
                run = sum(r for s, r in pairs if s == sv)
                ds = sv - shift
                print(f"    stored={sv}  count={run}  direct_stored={ds}  "
                      f"null_val_match={sv==null_val}")


if __name__ == "__main__":
    diag_enc3_segment("cs_1000",  "ncf")
    diag_enc3_segment("cs_10000", "ncf")
