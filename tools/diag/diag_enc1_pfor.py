"""
Diagnose enc=1 ARCHIVE segment blob structure to check for PFOR exception fields.

Per docs/260616-2-fixture-dbcc-page-verifier.md §15, SQL Server's enc=1 may use
PFOR (Patched Frame-of-Reference) encoding with a linked-list exception mechanism.
This script examines the actual bytes of enc=1 segment blobs to identify:
  1. All header fields (offsets 0-60)
  2. Whether there's an exception-count / exception-offset field anywhere
  3. Structure at the END of the bitpack region (exception values grow backward)
  4. The entry-point array structure (7-bit patch-start + 25-bit exception position)
"""
import struct
import sys
from pathlib import Path

repo = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo))

from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.columnstore import (  # noqa: E402
    _bootstrap,
    _read_column_segments,
    _collect_blobs,
    _unwrap_archive_blob,
)

_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
_U64 = struct.Struct("<Q")
_I32 = struct.Struct("<i")


def dump_blob_header(blob: bytes, label: str) -> None:
    """Dump first 80 bytes + end of bitpack as hex + interpreted fields."""
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  blob len = {len(blob)}")
    print(f"{'='*70}")

    # Known fields
    bpv = _U16.unpack_from(blob, 34)[0]
    nw  = _U32.unpack_from(blob, 36)[0]
    n_rows_hdr = _U32.unpack_from(blob, 52)[0]
    n_frags = _U32.unpack_from(blob, 20)[0]

    print(f"  Known: bpv={bpv}  nw={nw}  n_rows@52={n_rows_hdr}  n_frags@20={n_frags}")
    print(f"  vpw = {64 // bpv if bpv else 0}  cap = {nw * (64 // bpv) if bpv else 0}")

    bp_start = len(blob) - nw * 8
    print(f"  bitpack_start = {bp_start}  bitpack_end = {len(blob)}")

    # Dump all header bytes 0..79 as hex groups + u32 interpretation
    print("\n  Header bytes (u32 view, offset: value):")
    for off in range(0, min(80, len(blob)), 4):
        val32 = _U32.unpack_from(blob, off)[0]
        i32   = _I32.unpack_from(blob, off)[0]
        print(f"    [{off:3d}] u32={val32:10d}  (0x{val32:08X})  i32={i32:10d}")

    # Dump bytes just before bitpack start — look for exception count, entry-point array
    if bp_start > 80:
        print(f"\n  Pre-bitpack bytes (u32 view, last 64 bytes before bp_start={bp_start}):")
        start_dump = max(80, bp_start - 64)
        for off in range(start_dump, bp_start, 4):
            val32 = _U32.unpack_from(blob, off)[0]
            print(f"    [{off:5d}] u32={val32:10d}  (0x{val32:08X})")

    # Dump end of bitpack — look for exception values growing backward
    print(f"\n  END of bitpack ({min(128, nw*8)} bytes before end):")
    end_start = max(bp_start, len(blob) - min(128, nw * 8))
    for off in range(end_start, len(blob), 8):
        w = _U64.unpack_from(blob, off)[0] if off + 8 <= len(blob) else 0
        # Check: are these plausible "exception values" (raw 64-bit values)?
        bitmask = (1 << bpv) - 1 if bpv else 0
        # Exception slots should NOT look like normal bpv-bit values
        print(f"    [{off:5d}] 0x{w:016X}  (first_bpv_slot={w & bitmask})")

    # Check for PFOR entry-point array between fragment table end and bitpack start
    # Entry-point array: one 32-bit word per 128 values = 7-bit patch-start + 25-bit pos
    n_blocks = (n_rows_hdr + 127) // 128
    frag_table_end = 48 + n_frags * 8
    pfor_ep_start = frag_table_end
    pfor_ep_end   = pfor_ep_start + n_blocks * 4
    if pfor_ep_end < bp_start and n_blocks > 0:
        print(f"\n  Potential PFOR entry-point array (if n_blocks={n_blocks} × 4B):")
        print(f"    [{pfor_ep_start}..{pfor_ep_end}) = {pfor_ep_end - pfor_ep_start} bytes")
        for i in range(n_blocks):
            off = pfor_ep_start + i * 4
            if off + 4 > len(blob):
                break
            val = _U32.unpack_from(blob, off)[0]
            patch_start = (val >> 25) & 0x7F   # top 7 bits
            first_exc   = val & 0x1FFFFFF       # bottom 25 bits
            print(f"    block[{i:3d}]: 0x{val:08X}  patch_start={patch_start}  first_exc_pos={first_exc}")
    else:
        print(f"\n  No room for PFOR entry-point array (frag_table_end={frag_table_end}, bp_start={bp_start})")

    # First few bitpack words decoded naively
    print("\n  First 8 bitpack words (raw u64 + first two bpv-bit values):")
    mask = (1 << bpv) - 1 if bpv else 0
    for wi in range(min(8, nw)):
        off = bp_start + wi * 8
        if off + 8 > len(blob):
            break
        w = _U64.unpack_from(blob, off)[0]
        v0 = w & mask
        v1 = (w >> bpv) & mask if bpv else 0
        print(f"    word[{wi:3d}] 0x{w:016X}  v0={v0}  v1={v1}")


def main() -> None:
    import sys as _sys
    bak_arg = _sys.argv[1] if len(_sys.argv) > 1 else None
    table_arg = _sys.argv[2] if len(_sys.argv) > 2 else None

    fixture = Path(bak_arg) if bak_arg else (repo / "tests" / "fixtures_2022" / "archive_columnstore_partition_full.bak")
    if not fixture.exists():
        print(f"Fixture not found: {fixture}")
        return

    print(f"Opening {fixture.name}...")
    store = PageStore.from_bak(fixture)
    boot  = _bootstrap(store)
    schema = recover_schema(store)
    all_blobs = _collect_blobs(store)

    for table in schema.tables:
        if table_arg and table.name != table_arg:
            continue
        if not table_arg and table.name not in ("archive_part_all", "archive_null"):
            continue
        rowset_ids = {au.rowset_id for au in table.alloc_units}
        segs = list(_read_column_segments(store, boot, rowset_ids))
        blobs = all_blobs

        # Find enc=1 segments (likely the id column)
        done = 0
        for seg in segs:
            if seg.enc_type not in (1, 2):
                continue
            raw_blob = blobs.get(seg.blob_id, b"")
            if not raw_blob:
                continue
            inner = _unwrap_archive_blob(raw_blob)
            label = (
                f"hobt={seg.hobt_id} col={seg.col_id} seg={seg.seg_id} "
                f"enc={seg.enc_type} n_rows={seg.n_rows} "
                f"mn={seg.mn} mag={seg.magnitude:.0f}"
            )
            dump_blob_header(inner, label)
            done += 1
            if done >= 2:
                break

    print("\nDone.")


if __name__ == "__main__":
    main()
