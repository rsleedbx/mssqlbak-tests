#!/usr/bin/env python3
"""Locate the 42 straddle-dropped XTP rows across ALL decompressed chunks.

For each id that `scan_cfp_log_records` failed to recover, searches the full
decompressed stream (page-classified AND non-page chunks) for a byte pattern
that could correspond to the row's fixed-section prefix, then classifies where
the intact row copy lives so Phase 3 knows the recovery rule.

Usage:
    python -m tools.diag._diag_xtp_ckpt_locate [--bak PATH]
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))  # noqa: E402

from mssqlbak.compressed import (  # noqa: E402
    iter_decompressed_chunks as _iter_dc,
    _OFF_HEADER_VERSION,
    _HEADER_VERSION,
)
from mssqlbak.xtp import (  # noqa: E402
    scan_cfp_log_records,
    _PAGE_MTYPE_MAX,
    _CKPT_PREAMBLE_SIG,
    _LOG_HEADER_SIZE,
    _read_log_header,
)
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402

_U32 = struct.Struct("<I")
_U16 = struct.Struct("<H")

_DEFAULT_BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"


def _is_page_chunk(ch: bytes) -> bool:
    return (
        len(ch) >= 96
        and ch[_OFF_HEADER_VERSION] == _HEADER_VERSION
        and 1 <= ch[1] <= _PAGE_MTYPE_MAX
    )


def main(bak_path: Path) -> None:
    bak_bytes = bak_path.read_bytes()

    # ------------------------------------------------------------------
    # Step 1: identify the missing (straddle) ids from the scanner output
    # ------------------------------------------------------------------
    lb_map = scan_cfp_log_records(bak_bytes)
    if not lb_map:
        print("scan_cfp_log_records found nothing — wrong fixture?")
        return

    store = PageStore.from_bak(str(bak_path))
    schema = recover_schema(store)
    xtp_tables = [t for t in schema.tables if t.is_memory_optimized]
    if not xtp_tables:
        print("No XTP tables in fixture")
        return

    lb0_seqs = {seq for seq, _ in lb_map[0]}
    # Determine approximate row count from stats (or seq max)
    row_count = max(lb0_seqs)
    missing_seqs = sorted(set(range(1, row_count + 1)) - lb0_seqs)
    print(f"Scanner recovered: {len(lb0_seqs)} records from LB=0x00")
    print(f"Missing seq values: {len(missing_seqs)}")
    print(f"First 5: {missing_seqs[:5]}")
    print(f"Last 5:  {missing_seqs[-5:]}\n")

    # ------------------------------------------------------------------
    # Step 2: build byte patterns for the missing ids (id LE prefix search)
    # The seq for a missing row == its id (IDENTITY insert in seq order,
    # assuming sequential inserts — seq is the XTP insert seq counter).
    # We search for the 4-byte LE id as the first bytes of the payload.
    # ------------------------------------------------------------------
    missing_ids_patterns: list[tuple[int, bytes]] = [
        (seq, struct.pack("<I", seq)) for seq in missing_seqs
    ]

    # ------------------------------------------------------------------
    # Step 3: iterate ALL decompressed chunks; classify and search
    # ------------------------------------------------------------------
    chunks: list[tuple[int, bool, bytes]] = []  # (chunk_idx, is_page, data)
    for idx, ch in enumerate(_iter_dc(bak_bytes)):
        chunks.append((idx, _is_page_chunk(ch), ch))

    total_page = sum(1 for _, pg, _ in chunks if pg)
    total_nonpage = sum(1 for _, pg, _ in chunks if not pg)
    total_bytes_page = sum(len(d) for _, pg, d in chunks if pg)
    total_bytes_nonpage = sum(len(d) for _, pg, d in chunks if not pg)
    print(
        f"Decompressed chunks: {len(chunks)} total  "
        f"({total_nonpage} non-page={total_bytes_nonpage//1024}KB, "
        f"{total_page} page={total_bytes_page//1024}KB)"
    )
    print()

    # ------------------------------------------------------------------
    # Step 4: for each missing id, search in three regions:
    #   A) page-classified chunks (the region the scanner drops)
    #   B) non-page segments (the region the scanner uses)
    #   C) inside the dropped clobbered record's known payload prefix
    # ------------------------------------------------------------------
    # We also check: does the straddle record itself (with _CKPT_PREAMBLE_SIG
    # in its payload) appear in the non-page region?
    nonpage_blob = b"".join(d for _, pg, d in chunks if not pg)
    page_blob = b"".join(d for _, pg, d in chunks if pg)

    print(f"{'id':>8}  {'in_nonpage':>10}  {'in_pageclf':>10}  "
          f"{'nonpage_off':>12}  {'pageclf_off':>12}  notes")
    print("-" * 80)

    for id_val, pat in missing_ids_patterns:
        np_off = nonpage_blob.find(pat)
        pg_off = page_blob.find(pat)

        notes = []
        if np_off >= 0:
            # Check if the record at np_off is the clobbered straddle
            # (its payload should contain _CKPT_PREAMBLE_SIG)
            # Try to find a log header 20 bytes before np_off
            candidate_hdr = max(0, np_off - _LOG_HEADER_SIZE)
            hv = _read_log_header(nonpage_blob, candidate_hdr, len(nonpage_blob))
            if hv:
                p_size, lb = hv
                cand_seq = _U32.unpack_from(nonpage_blob, candidate_hdr + 8)[0]
                payload = nonpage_blob[candidate_hdr + _LOG_HEADER_SIZE:
                                       candidate_hdr + _LOG_HEADER_SIZE + p_size]
                if _CKPT_PREAMBLE_SIG in payload:
                    notes.append(f"clobbered_in_logstream(seq={cand_seq},lb={lb})")
                else:
                    notes.append(f"intact_in_logstream(seq={cand_seq},lb={lb})")
            else:
                notes.append("nonpage_no_hdr_at_-20")

        if pg_off >= 0:
            # Find which chunk contains this offset
            running = 0
            for ci, pg, cd in chunks:
                if pg:
                    if running <= pg_off < running + len(cd):
                        local_off = pg_off - running
                        chunk_hdr = cd[:16].hex()
                        notes.append(
                            f"page_chunk#{ci}[0x{local_off:x}] "
                            f"mtype={cd[1] if len(cd)>1 else '?'} "
                            f"hdr={chunk_hdr}"
                        )
                        break
                    running += len(cd)

        print(
            f"{id_val:>8}  "
            f"{'Y' if np_off >= 0 else 'N':>10}  "
            f"{'Y' if pg_off >= 0 else 'N':>10}  "
            f"{np_off:>12}  "
            f"{pg_off:>12}  "
            f"{'; '.join(notes) if notes else ''}"
        )

    # ------------------------------------------------------------------
    # Step 5: characterise the page-classified chunks that contain straddle ids
    # ------------------------------------------------------------------
    print("\n--- Page-classified chunks containing straddle rows ---")
    straddle_page_chunks: set[int] = set()
    for id_val, pat in missing_ids_patterns:
        running = 0
        for ci, pg, cd in chunks:
            if pg:
                if pat in cd:
                    straddle_page_chunks.add(ci)
                running += len(cd)

    for ci in sorted(straddle_page_chunks):
        cd = chunks[ci][2]
        print(
            f"  chunk#{ci:4d}: len={len(cd)} "
            f"byte0={cd[0]:02x} byte1={cd[1]:02x} "
            f"first32={cd[:32].hex()}"
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bak", type=Path, default=_DEFAULT_BAK, help="Path to .bak file")
    args = ap.parse_args()
    main(args.bak)
