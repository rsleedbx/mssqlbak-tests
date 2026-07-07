#!/usr/bin/env python3
"""Diagnostic: extract and display XTP (Hekaton) checkpoint data from a .bak file.

Locates the XTP checkpoint streams embedded in a SQL Server backup file and
dumps their structure so the checkpoint-data row format can be reverse-engineered.

Usage:
    python -m tools.diag_xtp_blocks tests/fixtures_2022/xtp_simple_full.bak
    python -m tools.diag_xtp_blocks tests/fixtures_2022/xtp_simple_full.bak --hex-rows
    python -m tools.diag_xtp_blocks tests/fixtures_2022/xtp_simple_full.bak --search-values 100 999999999999
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

# Hekaton v2 checkpoint file path prefix embedded as UTF-16LE in every
# XTP checkpoint manifest block: /$HKv2
_HKV2_U16 = "/$HKv2".encode("utf-16-le")

# XTP checkpoint data block size is always 4 KB.
_XTP_BLOCK = 0x1000

# Search stride for locating HKv2 / row-data blocks.
_SCAN_STRIDE = 0x200  # 512 bytes

_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
_U64 = struct.Struct("<Q")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex_dump(data: bytes, base: int = 0, width: int = 16) -> str:
    lines = []
    for off in range(0, len(data), width):
        chunk = data[off : off + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        asc_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        lines.append(f"  {base + off:08x}: {hex_part:<{width * 3}}  {asc_part}")
    return "\n".join(lines)


def _find_all(haystack: bytes, needle: bytes) -> list[int]:
    positions, pos = [], 0
    while (pos := haystack.find(needle, pos)) >= 0:
        positions.append(pos)
        pos += 1
    return positions


def _decode_utf16le_str(data: bytes, offset: int, max_chars: int = 128) -> str:
    """Read a null-terminated UTF-16LE string from *data* at *offset*."""
    end = offset
    while end + 1 < len(data) and end < offset + max_chars * 2:
        if data[end] == 0 and data[end + 1] == 0:
            break
        end += 2
    try:
        return data[offset:end].decode("utf-16-le")
    except UnicodeDecodeError:
        return repr(data[offset:end])


# ---------------------------------------------------------------------------
# HKv2 manifest block scanner
# ---------------------------------------------------------------------------

def _scan_hkv2_manifests(bak: bytes) -> list[dict]:
    """Find all /$HKv2 manifest blocks and decode their headers."""
    manifests = []
    for hkv2_pos in _find_all(bak, _HKV2_U16):
        # The HKv2 path string starts at the beginning of the manifest.
        # Back up to the start of the 4KB-aligned block that contains it.
        block_start = (hkv2_pos // _XTP_BLOCK) * _XTP_BLOCK
        block = bak[block_start : block_start + _XTP_BLOCK]
        if len(block) < 64:
            continue
        # Decode the path (from HKv2 onwards).
        path = _decode_utf16le_str(block, hkv2_pos - block_start)
        manifests.append(
            {
                "file_offset": block_start,
                "hkv2_offset": hkv2_pos,
                "path": path,
                "raw_header": block[:64],
            }
        )
    return manifests


# ---------------------------------------------------------------------------
# XTP data block scanner
# ---------------------------------------------------------------------------

def _looks_like_xtp_data_block(block: bytes) -> bool:
    """Heuristic: an XTP checkpoint data block starts with a recognisable header.

    The first byte observed in all XTP data blocks from SQL Server 2017–2022
    is 0x50 (for the first block of a CFP file) or a small integer.  The block
    must NOT start with the HKv2 path signature (those are manifest blocks).
    """
    if len(block) < 16:
        return False
    # Reject HKv2 manifest blocks.
    if block[0x3C : 0x3C + len(_HKV2_U16)] == _HKV2_U16:
        return False
    # The XTP data block header observed experimentally:
    # byte 0 = 0x50 (first block of a CFP) or 0x40–0x60 range
    # bytes 4–7 contain a non-trivial value (offset/sequence)
    # The block must contain some non-zero content after offset 0x30.
    return (
        0x10 <= block[0] <= 0xFF
        and any(block[0x30 : 0x60])
    )


def _scan_xtp_data_blocks(bak: bytes) -> list[dict]:
    """Locate XTP checkpoint data blocks by scanning 4 KB-aligned positions.

    These blocks differ from manifest blocks in that they do NOT carry the
    HKv2 path signature and contain row data.
    """
    blocks = []
    for off in range(0, len(bak) - _XTP_BLOCK, _XTP_BLOCK):
        block = bak[off : off + _XTP_BLOCK]
        # Skip MDF pages (always 8 KB, header version = 1 at byte 0).
        if block[0] == 0x01 and block[1] in range(1, 20):
            continue
        # Skip HKv2 manifest blocks.
        if block[0x3C : 0x3C + len(_HKV2_U16)] == _HKV2_U16:
            continue
        if _looks_like_xtp_data_block(block):
            blocks.append({"file_offset": off, "raw": block})
    return blocks


# ---------------------------------------------------------------------------
# String / value search
# ---------------------------------------------------------------------------

def _search_values(bak: bytes, values: list[str]) -> None:
    print("=== Value search ===")
    for val in values:
        # Try as integer (little-endian uint32 / uint64).
        try:
            i = int(val)
            for fmt, name, lo, hi in [("<I", "uint32", 0, 2**32-1), ("<Q", "uint64", 0, 2**64-1)]:
                if not (lo <= i <= hi):
                    continue
                needle = struct.pack(fmt, i)
                for pos in _find_all(bak, needle):
                    block_off = (pos // _XTP_BLOCK) * _XTP_BLOCK
                    within = pos - block_off
                    print(
                        f"  {val!r} as {name} ({needle.hex()})  "
                        f"@ file:{pos:#010x}  block:{block_off:#010x}+{within:#05x}"
                    )
        except ValueError:
            pass
        # Try as UTF-16LE string.
        needle = val.encode("utf-16-le")
        for pos in _find_all(bak, needle):
            block_off = (pos // _XTP_BLOCK) * _XTP_BLOCK
            within = pos - block_off
            print(
                f"  {val!r} as UTF-16LE ({needle.hex()})  "
                f"@ file:{pos:#010x}  block:{block_off:#010x}+{within:#05x}"
            )
    print()


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _report(bak: bytes, hex_rows: bool = False) -> None:
    manifests = _scan_hkv2_manifests(bak)
    data_blocks = _scan_xtp_data_blocks(bak)

    print(f"=== XTP checkpoint manifest blocks  ({len(manifests)} found) ===")
    for i, m in enumerate(manifests):
        print(f"  [{i:2d}]  file:{m['file_offset']:#010x}  path={m['path']!r}")
    print()

    print(f"=== XTP checkpoint data blocks  ({len(data_blocks)} candidate blocks) ===")
    for i, b in enumerate(data_blocks):
        off = b["file_offset"]
        raw = b["raw"]
        print(f"\n  [{i:2d}]  file:{off:#010x}")
        print("  Header (first 192 bytes):")
        print(_hex_dump(raw[:192], base=off))
        if hex_rows and len(raw) > 192:
            # Show the rest of the block until trailing zeros.
            end = _XTP_BLOCK
            while end > 192 and raw[end - 1] == 0:
                end -= 1
            if end > 192:
                print(f"  Data [{0xc0:#x}..{end:#x}]:")
                print(_hex_dump(raw[0xC0:end], base=off + 0xC0))

    print()
    print(
        f"=== Summary ===\n"
        f"  File size:       {len(bak):,} bytes\n"
        f"  Manifest blocks: {len(manifests)}\n"
        f"  Data blocks:     {len(data_blocks)}\n"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("bak", help="path to .bak file")
    p.add_argument("--hex-rows", action="store_true", help="dump full non-zero data region of each data block")
    p.add_argument("--search-values", nargs="+", metavar="VAL",
                   help="search for known column values (int or string) in the backup stream")
    args = p.parse_args(argv)

    path = Path(args.bak)
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    print(f"Reading {path} ({path.stat().st_size:,} bytes) …")
    bak = path.read_bytes()
    print()

    if args.search_values:
        _search_values(bak, args.search_values)

    _report(bak, hex_rows=args.hex_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
