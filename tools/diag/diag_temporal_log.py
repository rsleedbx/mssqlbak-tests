"""Temporal-update log diagnostic.

Scans the log tail in dirtycoverage_temporal_update.bak (any fixture version)
for records with discrim=0x06 (_DISCRIM_TEMPORAL) and reports:

  - subtype (0x04 = _SUB_DML, 0x00 = _SUB_XACT)
  - page_id / slot_id
  - the 3 undo bytes at +0x80 (ValidFrom before-image)
  - byte at +0x80 relative to the block start (for boundary checks)

Also shows the logtail_from_bak restore_slots and dirty_slots counts so we can
confirm whether the temporal patch is being captured at all.

Run:
    .venv/bin/python tools/diag_temporal_log.py [fixture_version]

fixture_version: 2017 | 2019 | 2022 | 2025  (default: 2017)
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from mssqlbak.logtail import (
    _BLOCK_SIZE,
    _BLOCK_STATUS_CONT,
    _BLOCK_STATUS_OPEN,
    _LCX_XACT,
    _OFF_LCX,
    _OFF_PAGE_ID,
    _OFF_SLOT_ID,
    _OFF_SUBTYPE,
    _OFF_TX_TYPE,
    _OFF_XACT_ID,
    _SCAN_STEP,
    _SUB_DML,
    _SUB_XACT,
    logtail_from_bak,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_DISCRIM_TEMPORAL = 0x06
_DISCRIM_INSERT   = 0x02
_DISCRIM_DELETE   = 0x03
_TX_MODIFY        = 0x04


def _u32(d: bytes | bytearray | memoryview, off: int) -> int:
    return struct.unpack_from("<I", d, off)[0]


def _u16(d: bytes | bytearray | memoryview, off: int) -> int:
    return struct.unpack_from("<H", d, off)[0]


def scan_bak(bak_path: Path) -> None:
    print(f"=== {bak_path.name} ===")

    # High-level logtail result
    result = logtail_from_bak(str(bak_path))
    print(f"  restore_slots : {len(result.restore_slots)}")
    print(f"  dirty_slots   : {len(result.dirty_slots)}")
    print(f"  modified_slots: {len(result.modified_slots)}")
    if result.restore_slots:
        print(f"  restore_slots keys (first 5): {list(result.restore_slots)[:5]}")
    print()

    # Raw scan for discrim=0x06
    raw = bak_path.read_bytes()
    total_0x06 = 0
    subtype_counts: dict[int, int] = {}

    for off in range(0, len(raw) - _BLOCK_SIZE, _BLOCK_SIZE):
        status = raw[off]
        if status not in (_BLOCK_STATUS_OPEN, _BLOCK_STATUS_CONT):
            continue

        block = raw[off : off + _BLOCK_SIZE]
        pos = 0
        while pos + 0x30 <= _BLOCK_SIZE:
            if block[pos + _OFF_LCX] == _LCX_XACT:
                xact_id = bytes(block[pos + _OFF_XACT_ID : pos + _OFF_XACT_ID + 6])
                if xact_id != b"\x00\x00\x00\x00\x00\x00":
                    subtype = block[pos + _OFF_SUBTYPE]
                    discrim = block[pos + _OFF_TX_TYPE]
                    if discrim == _DISCRIM_TEMPORAL:
                        page_id = _u32(block, pos + _OFF_PAGE_ID)
                        slot_id = _u16(block, pos + _OFF_SLOT_ID)
                        subtype_counts[subtype] = subtype_counts.get(subtype, 0) + 1
                        total_0x06 += 1

                        # Read the 3 undo bytes at pos+0x80 (ValidFrom before-image)
                        undo_3 = None
                        if pos + 0x83 <= _BLOCK_SIZE:
                            undo_3 = block[pos + 0x80 : pos + 0x83]
                        else:
                            # Crosses into the next block
                            undo_3 = b"<spans next block>"

                        # Check if the undo region crosses a 512-byte boundary
                        undo_in_block_off = pos + 0x80
                        sector_boundary = (undo_in_block_off // 512) * 512
                        next_boundary   = sector_boundary + 512
                        crosses_512 = undo_in_block_off < next_boundary <= undo_in_block_off + 3

                        # Row offset for ValidFrom (at pos+0x44)
                        vf_row_off = _u16(block, pos + 0x44) if pos + 0x46 <= _BLOCK_SIZE else None

                        print(
                            f"  0x06 record: block={off:#010x} pos={pos:#06x} "
                            f"subtype={subtype:#04x} page={page_id} slot={slot_id} "
                            f"xact={xact_id.hex()}"
                        )
                        print(
                            f"           vf_row_off={vf_row_off} "
                            f"undo@+0x80={undo_3.hex() if isinstance(undo_3, bytes) else undo_3} "
                            f"crosses_512={crosses_512}"
                        )
            pos += _SCAN_STEP

    print(f"\n  Total discrim=0x06: {total_0x06}")
    for sub, cnt in sorted(subtype_counts.items()):
        label = "_SUB_DML(0x04)" if sub == _SUB_DML else "_SUB_XACT(0x00)" if sub == _SUB_XACT else f"0x{sub:02x}"
        print(f"    subtype {label}: {cnt} records")
    print()


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "2017"
    fixtures_dir = REPO_ROOT / f"tests/fixtures_{version}"
    bak = fixtures_dir / "dirtycoverage_temporal_update.bak"
    if not bak.exists():
        print(f"ERROR: {bak} not found")
        sys.exit(1)
    scan_bak(bak)

    # Also scan 2022 for comparison if version != 2022
    if version != "2022":
        bak_2022 = REPO_ROOT / "tests/fixtures_2022/dirtycoverage_temporal_update.bak"
        if bak_2022.exists():
            print("--- 2022 (reference, passes) ---")
            scan_bak(bak_2022)


if __name__ == "__main__":
    main()
