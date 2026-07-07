"""G44 blob-format diagnostic.

Loads ``cs_lob_preamble2.bak``, extracts all columnstore-related blobs and
segments, and reverse-engineers the binary layout so we can implement a
version-4 hash-dictionary decoder in columnstore.py.

Run without prompts:
    .venv/bin/python tools/diag_g44_blob.py [path/to/fixture.bak]

What this script investigates:
  1. Segment metadata for the ``long_str`` column (enc_type=1, bit-packed).
  2. All dictionary-related LOB blobs (sizes, headers, entry counts).
  3. Blob 23844 (sorted string pool) — entry format and string extraction.
  4. Blob 2001 (hash dictionary) — header, hash-table layout, pool section.
  5. Whether all 1200 dictionary strings can be recovered from the blobs.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BAK = REPO_ROOT / "tests" / "fixtures_2022" / "cs_lob_preamble2.bak"


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _u16(d: bytes | bytearray, o: int = 0) -> int:
    return struct.unpack_from("<H", d, o)[0]


def _u32(d: bytes | bytearray, o: int = 0) -> int:
    return struct.unpack_from("<I", d, o)[0]


def _u64(d: bytes | bytearray, o: int = 0) -> int:
    return struct.unpack_from("<Q", d, o)[0]


def _f32(d: bytes | bytearray, o: int = 0) -> float:
    return struct.unpack_from("<f", d, o)[0]


# ---------------------------------------------------------------------------
# Section 1 — Segment analysis
# ---------------------------------------------------------------------------

def analyse_segment(store, boot, t, blobs: dict) -> list[int]:
    """Return the list of raw dictionary indices stored in the enc=1 segment."""
    from mssqlbak.columnstore import (  # noqa: PLC0415
        _read_column_segments,
        _unwrap_archive_blob,
        _BP_BPV,
        _BP_NW,
    )

    rowset_ids = {rs for _, rs in boot.obj_to_rowsets.get(t.object_id, [])}
    segs = _read_column_segments(store, boot, rowset_ids)

    print("\n=== Column segments ===")
    for s in segs:
        print(f"  col_id={s.col_id}  enc={s.enc_type}  blob_id={s.blob_id}"
              f"  n_rows={s.n_rows}  prim_dict={s.prim_dict}"
              f"  sec_dict={s.sec_dict}")

    ls_seg = next((s for s in segs if s.col_id == 2), None)
    if ls_seg is None:
        print("  ERROR: no segment for col_id=2 (long_str)")
        return []

    print("\n--- long_str segment (col_id=2) ---")
    print(f"  enc_type={ls_seg.enc_type} (1=value-encoded, 3=dict-encoded)")
    print(f"  blob_id={ls_seg.blob_id}, n_rows={ls_seg.n_rows}")
    print(f"  prim_dict={ls_seg.prim_dict}, sec_dict={ls_seg.sec_dict}")

    seg_blob = blobs.get(ls_seg.blob_id)
    if seg_blob is None:
        print(f"  ERROR: segment blob {ls_seg.blob_id} not in blobs dict")
        return []

    unwrapped = _unwrap_archive_blob(seg_blob)
    bpv = _u16(unwrapped, _BP_BPV)
    nw  = _u32(unwrapped, _BP_NW)
    mask = (1 << bpv) - 1
    vpw  = 64 // bpv
    bp_start = len(unwrapped) - nw * 8

    stored_vals: list[int] = []
    for wi in range(nw):
        word = _u64(unwrapped, bp_start + wi * 8)
        for vi in range(vpw):
            stored_vals.append((word >> (vi * bpv)) & mask)

    dict_indices = stored_vals[: ls_seg.n_rows]

    print(f"\n  Bit-pack: bpv={bpv}, nw={nw}, bp_start={bp_start}")
    print(f"  Stored values (first 10): {dict_indices[:10]}")
    print(f"  Stored values (last 10):  {dict_indices[-10:]}")
    print(f"  Range: {min(dict_indices)}..{max(dict_indices)}")
    print(f"  Unique count: {len(set(dict_indices))}")
    print("  → These are dictionary indices. Fix needed: look them up in the string pool.")

    return dict_indices


# ---------------------------------------------------------------------------
# Section 2 — Blob 23844: sorted string pool (version-4 CSINDEX)
# ---------------------------------------------------------------------------

def analyse_sorted_pool(b: bytes) -> dict[int, str]:
    """Parse blob 23844 (sorted string pool) → {rank: string}."""
    n = len(b)
    # 64-byte header
    magic      = _u32(b, 0)
    num_entries_hdr = _u32(b, 12)
    num_entries_hdr2 = _u32(b, 20)

    print(f"\n=== Blob 23844 (sorted string pool): {n} bytes ===")
    print(f"  magic=0x{magic:08x}  num_entries[hdr3]={num_entries_hdr}"
          f"  num_entries[hdr5]={num_entries_hdr2}")
    print(f"  hdr float[7]={_f32(b, 28):.6g}  float[8]={_f32(b, 32):.6g}")

    # Scan for 103-byte entries: u16=103 then 80 printable ASCII bytes
    entries: dict[int, str] = {}
    rank = 0
    off = 0
    while off + 103 <= n:
        sz = _u16(b, off)
        if sz == 103:
            s = b[off + 2 : off + 2 + 80]
            if all(32 <= x < 128 for x in s):
                entries[rank] = s.decode("ascii")
                rank += 1
                off += 103
                continue
        off += 1

    print(f"  Decoded {len(entries)} 103-byte entries (sorted ranks 0..{len(entries)-1})")
    if entries:
        print(f"  Entry[0]:   {entries[0]!r}")
        print(f"  Entry[{len(entries)-1:4d}]: {entries[len(entries)-1]!r}")

    # Summarise unexplained regions
    if entries:
        first_entry_off = 1945
        last_entry_end  = first_entry_off + len(entries) * 103
        print("\n  Layout regions:")
        print(f"    [0:{first_entry_off}]        = {first_entry_off} bytes (header + unknown)")
        print(f"    [{first_entry_off}:{last_entry_end}]  = {last_entry_end - first_entry_off} bytes "
              f"({len(entries)} × 103-byte entries)")
        remaining = n - last_entry_end
        print(f"    [{last_entry_end}:{n}]   = {remaining} bytes (unknown — "
              f"may contain ranks {len(entries)}..{num_entries_hdr - 1})")

        # Peek at the unknown tail for patterns
        tail = b[last_entry_end:]
        nz   = sum(1 for x in tail if x != 0)
        print(f"    Tail non-zero bytes: {nz}/{remaining}")
        print(f"    Tail first 40 bytes: {tail[:40].hex()}")

    return entries


# ---------------------------------------------------------------------------
# Section 3 — Blob 2001: hash dictionary (version-4)
# ---------------------------------------------------------------------------

def analyse_hash_dict(b: bytes) -> None:
    """Summarise blob 2001 (version-4 hash dictionary)."""
    n = len(b)
    num_entries = _u32(b, 4 * 4)   # hdr[4]
    hash_slots  = _u32(b, 5 * 4)   # hdr[5]
    ht_start    = 6 * 4             # 24 bytes header
    ht_end      = ht_start + hash_slots * 4
    pool_start  = ht_end
    pool_end    = n

    print(f"\n=== Blob 2001 (hash dictionary): {n} bytes ===")
    print(f"  hdr[0..7]: {[_u32(b, i*4) for i in range(8)]}")
    print(f"  num_entries={num_entries}  hash_slots={hash_slots}")
    print(f"  Hash table:  [{ht_start}:{ht_end}] = {ht_end - ht_start} bytes"
          f"  ({hash_slots} × 4-byte slots)")
    print(f"  String pool: [{pool_start}:{pool_end}] = {pool_end - pool_start} bytes")

    # Non-zero hash slots
    nz_slots = 0
    for i in range(hash_slots):
        if _u32(b, ht_start + i * 4) != 0:
            nz_slots += 1
    print(f"  Non-zero hash slots: {nz_slots} / {hash_slots}")

    # Peek at pool
    pool = b[pool_start:pool_end]
    nz_pool = sum(1 for x in pool if x != 0)
    print(f"  Pool non-zero bytes: {nz_pool}/{len(pool)}")
    print(f"  Pool first 32 hex:   {pool[:32].hex()}")
    print(f"  Pool first 32 ASCII: {bytes(x if 32<=x<128 else ord('.') for x in pool[:32]).decode()}")
    print("  → Pool format is binary (not u16-prefixed ASCII). Further analysis required.")


# ---------------------------------------------------------------------------
# Section 4 — Row decode verification
# ---------------------------------------------------------------------------

def verify_row_decode(store, t) -> None:
    from mssqlbak.rows import read_table_rows  # noqa: PLC0415

    rows  = list(read_table_rows(store, t))
    total = len(rows)
    nonne = sum(1 for r in rows if r.get("long_str"))
    empty = sum(1 for r in rows if r.get("long_str") == "")
    none_ = sum(1 for r in rows if r.get("long_str") is None)

    print("\n=== Row decode check ===")
    print(f"  Total rows: {total}")
    print(f"  non-empty long_str: {nonne}")
    print(f"  empty string:       {empty}")
    print(f"  None:               {none_}")
    if nonne > 0:
        sample = next(r["long_str"] for r in rows if r.get("long_str"))
        print(f"  Sample: {sample[:80]!r}")
    else:
        print("  *** All long_str values are empty/None — decoder fix needed ***")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyse(bak_path: Path) -> None:
    from mssqlbak.catalog import _bootstrap, recover_schema  # noqa: PLC0415
    from mssqlbak.columnstore import _collect_blobs, _read_dict_blob_ids  # noqa: PLC0415
    from mssqlbak.mtf import extract_mdf_pages  # noqa: PLC0415
    from mssqlbak.pages import PageStore  # noqa: PLC0415

    print(f"Loading {bak_path} …")
    img   = extract_mdf_pages(bak_path)
    store = PageStore(img)
    boot  = _bootstrap(store)
    schema = recover_schema(store)
    t     = schema.tables[0]

    print(f"\nTable: {t.name}  cols: {[c.name for c in t.columns]}")

    blobs = _collect_blobs(store)

    # --- Dict blob IDs from syscsdictionaries --------------------------------
    rowset_ids = {rs for _, rs in boot.obj_to_rowsets.get(t.object_id, [])}
    dict_bids  = _read_dict_blob_ids(store, boot, rowset_ids)
    print(f"\nAll LOB blob IDs: {sorted(blobs.keys())}")
    print(f"Dict blob IDs (from syscsdictionaries): {dict_bids}")

    # --- Segment analysis ---------------------------------------------------
    analyse_segment(store, boot, t, blobs)

    # --- Dictionary blob analysis -------------------------------------------
    for bid in sorted(blobs.keys()):
        b = blobs[bid]
        if bid == 23844:
            analyse_sorted_pool(b)
        elif bid == 2001:
            analyse_hash_dict(b)
        elif bid in (2002, 2003, 2004):
            print(f"\n=== Blob {bid}: {len(b)} bytes (segment data, not decoded here) ===")

    # --- Row decode verification --------------------------------------------
    verify_row_decode(store, t)

    print("\n=== Summary ===")
    print("  Known: blob 23844 contains 194 sorted-pool entries (ranks 0..193)")
    print("         using 103-byte format: u16 size + 80 ASCII chars + 21 meta bytes.")
    print("  Unknown: ranks 194..1199 — stored in blob 23844 tail or blob 2001 pool.")
    print("  Next step: run g44-probe to get DBCC CSINDEX → dict index→string mapping.")


def main() -> int:
    bak_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BAK
    if not bak_path.exists():
        print(f"ERROR: {bak_path} not found", file=sys.stderr)
        return 1
    analyse(bak_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
