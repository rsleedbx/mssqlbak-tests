"""Shared helpers for mssqlbak diagnostic scripts.

Import this module at the top of any new diag script:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))   # find _lib
    from _lib import fixture, open_store, iter_subblocks, hexdump, U16, U32

This module also ensures the repo root is on sys.path so ``mssqlbak``
imports resolve regardless of how the script is invoked.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path
from typing import Any, Iterator

# ── Repo root (3 levels up: tools/diag/_lib.py → repo root) ──────────────────
REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── Struct accessors ──────────────────────────────────────────────────────────
U16: struct.Struct = struct.Struct("<H")
U32: struct.Struct = struct.Struct("<I")
I64: struct.Struct = struct.Struct("<q")


def u16(data: bytes, off: int) -> int:
    return U16.unpack_from(data, off)[0]


def u32(data: bytes, off: int) -> int:
    return U32.unpack_from(data, off)[0]


def i64(data: bytes, off: int) -> int:
    return I64.unpack_from(data, off)[0]


# ── ARCHIVE XPRESS constants ──────────────────────────────────────────────────
FULL_SZ: int = 65536      # decompressed size for full-size sub-blocks
MARKER_LO: int = 0xFFF0   # inclusive lower bound for "full-size" marker range
MARKER_HI: int = 0xFFFE   # inclusive upper bound (also the NULL sentinel value)
NULL_SENTINEL: int = 0xFFFE


# ── Fixture path resolution ───────────────────────────────────────────────────
def fixture(version: str | int, name: str) -> Path:
    """Return absolute path to a test fixture.

    Example::

        fixture("2022", "archive_columnstore_partition_full.bak")
        fixture(2022, "columnstore_minimal.bak")
    """
    return REPO_ROOT / "tests" / f"fixtures_{version}" / name


# ── Store bootstrap ───────────────────────────────────────────────────────────
def open_store(
    path: Path,
) -> tuple[Any, Any, Any, dict[int, bytes]]:
    """Open a .bak and return (store, schema, boot, blobs).

    All four objects are needed for most diagnostic work::

        store, schema, boot, blobs = open_store(fixture("2022", "foo.bak"))
    """
    from mssqlbak.catalog import recover_schema
    from mssqlbak.columnstore import (  # type: ignore[attr-defined]
        _bootstrap,
        _collect_blobs,
    )
    from mssqlbak.pages import PageStore

    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    blobs: dict[int, bytes] = _collect_blobs(store)
    return store, schema, boot, blobs


# ── Segment helpers ───────────────────────────────────────────────────────────
def segments_for_table(store: Any, boot: Any, schema: Any, table_name: str) -> list[Any]:
    """Return all column segments for the named table, or [] if not found."""
    from mssqlbak.columnstore import _read_column_segments  # type: ignore[attr-defined]

    for tbl in schema.tables:  # type: ignore[union-attr]
        if tbl.name == table_name:
            rowset_ids = {au.rowset_id for au in tbl.alloc_units}
            return list(_read_column_segments(store, boot, rowset_ids))
    return []


def find_table(schema: Any, name: str) -> Any | None:
    """Return the Table object for *name*, or None."""
    for tbl in schema.tables:  # type: ignore[union-attr]
        if tbl.name == name:
            return tbl
    return None


# ── Sub-block iterator ────────────────────────────────────────────────────────
def iter_subblocks(inner: bytes) -> Iterator[tuple[int, int, int, bytes]]:
    """Iterate over XPRESS-compressed ARCHIVE sub-blocks in *inner*.

    Yields ``(block_idx, n_block, marker, pool_idx_b)`` for each sub-block.

    - ``block_idx`` — 0-based counter.
    - ``n_block``   — row count declared in the sub-block header.
    - ``marker``    — the 2-byte value after ``[0xFFFF][n_block u32]``; values
      in ``[MARKER_LO, MARKER_HI]`` indicate a full-size 65536-byte block.
    - ``pool_idx_b``— decompressed bytes (pool region followed by index region).

    The pool+index layout inside each ``pool_idx_b``::

        [pool: variable bytes][index: n_block × u16 pool byte-offsets]

    Use ``compute_idx_start`` to locate the index boundary.
    """
    from mssqlbak.xpress import decompress_until_input, decompress_with_pos

    pos = 0
    block_idx = 0
    while True:
        # Locate next 0xFFFF at a u16-aligned offset.
        m = -1
        scan = pos
        while scan + 1 < len(inner):
            if inner[scan] == 0xFF and inner[scan + 1] == 0xFF:
                m = scan
                break
            scan += 2

        if m < 0 or m + 8 > len(inner):
            break

        n_block = u32(inner, m + 2)
        if n_block == 0:
            break
        mk = u16(inner, m + 6)
        xp = m + 8

        if MARKER_LO <= mk <= MARKER_HI:
            try:
                pool_idx_b, consumed = decompress_with_pos(inner, xp, FULL_SZ)
            except Exception:
                break
            pos = xp + consumed
        else:
            try:
                pool_idx_b = decompress_until_input(inner, xp, len(inner))
            except Exception:
                break
            pos = len(inner)

        yield block_idx, n_block, mk, pool_idx_b
        block_idx += 1
        if pos >= len(inner):
            break


# ── Pool / index helpers ──────────────────────────────────────────────────────
def compute_idx_start(pool_idx: bytes, n_valid: int, col_width: int = 0) -> int:
    """Return the byte offset where the index starts in *pool_idx*.

    The index occupies the last ``n_valid × 2`` bytes.  When *col_width* > 0
    the result is rounded DOWN to the nearest multiple of *col_width* to
    compensate for XPRESS sub-chunk alignment padding.
    """
    idx = len(pool_idx) - n_valid * 2
    if idx < 0:
        return 0
    if col_width > 0:
        idx = (idx // col_width) * col_width
    return idx


def find_ffe_positions(data: bytes) -> list[int]:
    """Return all u16-aligned byte offsets of 0xFFFE (NULL sentinel) in *data*."""
    out: list[int] = []
    for i in range(0, len(data) - 1, 2):
        if u16(data, i) == NULL_SENTINEL:
            out.append(i)
    return out


def decode_pool_entry(
    pool_idx: bytes, pool_off: int, col_width: int, idx_start: int
) -> str:
    """Decode one index entry value into a human-readable string.

    Returns ``"NULL"`` for the null sentinel, ``"(OOB:N)"`` for out-of-bounds
    offsets, or the ASCII-decoded (rstripped) pool slice for valid offsets.
    """
    if pool_off == NULL_SENTINEL:
        return "NULL"
    if col_width > 0 and pool_off + col_width > idx_start:
        return f"(OOB:{pool_off})"
    raw = pool_idx[pool_off : pool_off + col_width] if col_width > 0 else pool_idx[pool_off:]
    try:
        return raw.decode("ascii", errors="replace").rstrip()
    except Exception:
        return raw.hex()


# ── Display helpers ───────────────────────────────────────────────────────────
def hexdump(
    data: bytes,
    base: int = 0,
    limit: int | None = None,
    *,
    ascii_col: bool = True,
    indent: str = "  ",
) -> None:
    """Print a hex+ASCII dump of *data*.

    Args:
        data:      Bytes to dump.
        base:      Starting offset label (default 0).
        limit:     Maximum number of bytes to show (default: all).
        ascii_col: Show ASCII sidebar (default True).
        indent:    Leading whitespace per line (default two spaces).
    """
    view = data if limit is None else data[:limit]
    for i in range(0, len(view), 16):
        chunk = view[i : i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        line = f"{indent}{base + i:06x}: {hex_part:<48}"
        if ascii_col:
            line += "  " + "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(line)
