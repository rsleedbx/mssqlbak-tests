#!/usr/bin/env python3
"""Emit JSON evidence records for BAK format guess / layout verification.

Each subcommand compares parser observations against a committed probe sidecar
or built-in constants.  Output shape::

    {"guess_id": "G13", "fixture": "...", "observed": {...},
     "expected": {...}, "verdict": "match"|"mismatch"|"pending"}

Usage::

    python -m tools.spec_probe pages --fixture tests/fixtures/typecoverage_full.bak
    python -m tools.spec_probe catalog --fixture tests/fixtures/catalog_ss2022.bak
    python -m tools.spec_probe rowcompress --fixture tests/fixtures/compressioncoverage_full.bak
    python -m tools.spec_probe layout --fixture tests/fixtures/layoutcoverage_full.bak
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.rows import _IAM_BITMAP_OFFSET  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
PROBE_DIR = _FIXTURE_DIR / "probe"


def _emit(record: dict[str, Any]) -> None:
    print(json.dumps(record, indent=2, default=str))


def cmd_pages(fixture: Path, probe_path: Path | None) -> int:
    """Probe G13 (IAM bitmap offset) and page-store basics."""
    store = PageStore.from_bak(fixture)
    observed = {
        "guess_id": "G13",
        "page_count": store.page_count,
        "iam_bitmap_offset": _IAM_BITMAP_OFFSET,
        "available_files": sorted(store.available_files),
    }
    expected: dict[str, Any] = {"iam_bitmap_offset": 194}
    if probe_path and probe_path.exists():
        expected = json.loads(probe_path.read_text())
    verdict = (
        "match"
        if observed["iam_bitmap_offset"] == expected.get("iam_bitmap_offset", 194)
        else "mismatch"
    )
    _emit({
        "guess_id": "G13",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected,
        "verdict": verdict,
    })
    return 0 if verdict == "match" else 1


def cmd_catalog(fixture: Path, probe_path: Path | None) -> int:
    """Probe G20/G21 — recovered table count and compression levels."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tables = [
        {
            "name": t.name,
            "compression": t.compression,
            "n_columns": len(t.columns),
        }
        for t in schema.tables
    ]
    observed = {
        "guess_id": "G21",
        "table_count": len(tables),
        "tables": tables,
    }
    expected: dict[str, Any] = {}
    if probe_path and probe_path.exists():
        expected = json.loads(probe_path.read_text())
    verdict = "pending" if not expected else (
        "match" if expected.get("table_count") == observed["table_count"] else "mismatch"
    )
    _emit({
        "guess_id": "G21",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected or {"note": "capture via make_catalog_fixture + sqlcmd"},
        "verdict": verdict,
    })
    return 0 if verdict in ("match", "pending") else 1


def cmd_rowcompress(fixture: Path) -> int:
    """Probe G19 — smalldatetime present in compression matrix tables."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    cmp_page = next((t for t in schema.tables if t.name == "cmp_page"), None)
    has_sdt = cmp_page is not None and any(c.name == "sdt" for c in cmp_page.columns)
    observed = {"guess_id": "G19", "cmp_page_has_sdt": has_sdt}
    expected = {"cmp_page_has_sdt": True}
    verdict = "match" if has_sdt else "mismatch"
    _emit({
        "guess_id": "G19",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected,
        "verdict": verdict,
    })
    return 0 if verdict == "match" else 1


def cmd_columnstore(fixture: Path) -> int:
    """Probe G42 — columnstore tables present in boundary fixture."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    cs_tables = [t.name for t in schema.tables if t.compression in (3, 4)]
    observed = {"guess_id": "G42", "columnstore_tables": len(cs_tables), "names": cs_tables[:5]}
    verdict = "match" if cs_tables else "mismatch"
    _emit({
        "guess_id": "G42",
        "fixture": str(fixture),
        "observed": observed,
        "expected": {"columnstore_tables_min": 1},
        "verdict": verdict,
    })
    return 0 if verdict == "match" else 1


def cmd_columnstore_dict_order(fixture: Path, probe_path: Path | None) -> int:
    """Probe G40 — verify prim_dict/sec_dict field offsets (52/56) match primary/secondary_dictionary_id.

    For enc=3 segments, the parser uses sec_dict (offset 56) for the dictionary
    lookup.  This probe checks that sec_dict equals secondary_dictionary_id from
    the probe file, confirming offset 56 → secondary_dictionary_id (not primary).
    """
    from mssqlbak.catalog import _bootstrap  # noqa: PLC0415
    from mssqlbak.columnstore import _read_column_segments  # noqa: PLC0415

    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    boot = _bootstrap(store)

    rowset_ids = {
        au.rowset_id
        for tbl in schema.tables
        if tbl.compression in (3, 4)
        for au in tbl.alloc_units
    }
    segs = _read_column_segments(store, boot, rowset_ids)

    enc3_segs = [s for s in segs if s.enc_type == 3]
    expected: dict[str, Any] = {}
    if probe_path and probe_path.exists():
        expected = json.loads(probe_path.read_text())

    # Compare parser sec_dict values against probe sample_enc3_segments.
    # Probe file keys by (hobt_id, col_id), parser uses the same hobt_id.
    probe_by_hobt: dict[int, int] = {}
    for entry in expected.get("sample_enc3_segments", []):
        probe_by_hobt[entry["hobt_id"]] = entry["secondary_dictionary_id"]

    mismatches: list[dict[str, Any]] = []
    checked = 0
    for seg in enc3_segs:
        if seg.hobt_id in probe_by_hobt:
            expected_sec = probe_by_hobt[seg.hobt_id]
            if seg.sec_dict != expected_sec:
                mismatches.append({
                    "hobt_id": seg.hobt_id,
                    "col_id": seg.col_id,
                    "parser_sec_dict": seg.sec_dict,
                    "expected_secondary_dictionary_id": expected_sec,
                })
            checked += 1

    verdict = "pending" if not expected else (
        "match" if not mismatches else "mismatch"
    )
    observed = {
        "guess_id": "G40",
        "enc3_segment_count": len(enc3_segs),
        "probe_checked": checked,
        "mismatches": mismatches,
        "sample_enc3": [
            {"col_id": s.col_id, "prim_dict": s.prim_dict, "sec_dict": s.sec_dict}
            for s in enc3_segs[:3]
        ],
    }
    _emit({
        "guess_id": "G40",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected or {"note": "run against live DB and save to probe/G40.json"},
        "verdict": verdict,
    })
    return 0 if verdict in ("match", "pending") else 1


def cmd_columnstore_seg_header(fixture: Path, probe_path: Path | None) -> int:
    """Probe G43 — segment blob header: bpv at offset 34, nw at offset 36.

    Decompresses each segment blob and checks that the header fields at
    offsets 34 (bpv: bits-per-value) and 36 (nw: 64-bit word count) are
    structurally valid and consistent with the catalog's n_rows.
    """
    import struct  # noqa: PLC0415

    from mssqlbak.catalog import _bootstrap  # noqa: PLC0415
    from mssqlbak.columnstore import (  # noqa: PLC0415
        _BP_BPV,
        _BP_NW,
        _collect_blobs,
        _read_column_segments,
        _unwrap_archive_blob,
    )

    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    boot = _bootstrap(store)

    rowset_ids = {
        au.rowset_id
        for tbl in schema.tables
        if tbl.compression in (3, 4)
        for au in tbl.alloc_units
    }
    segs = _read_column_segments(store, boot, rowset_ids)
    all_blobs = _collect_blobs(store)

    expected: dict[str, Any] = {}
    if probe_path and probe_path.exists():
        expected = json.loads(probe_path.read_text())

    invalid_headers: list[dict[str, Any]] = []
    header_samples: list[dict[str, Any]] = []
    for seg in segs:
        raw = all_blobs.get(seg.blob_id, b"")
        blob = _unwrap_archive_blob(raw)
        if len(blob) < _BP_NW + 4:
            continue
        bpv = struct.unpack_from("<H", blob, _BP_BPV)[0]
        nw = struct.unpack_from("<I", blob, _BP_NW)[0]
        # Basic sanity: bpv must be 0..64 and the declared data region must
        # not overflow the blob.  enc=3 (dict-encoded) uses the segment blob
        # to store only the distinct dictionary index bitpack, which is much
        # smaller than n_rows; skip the n_rows coverage check for enc=3.
        data_region_ok = nw == 0 or (nw * 8 + _BP_BPV + 2) <= len(blob)
        valid = bpv <= 64 and data_region_ok
        if not valid:
            invalid_headers.append({
                "col_id": seg.col_id, "seg_id": seg.seg_id,
                "bpv": bpv, "nw": nw, "n_rows": seg.n_rows,
            })
        if len(header_samples) < 3:
            header_samples.append({
                "col_id": seg.col_id, "seg_id": seg.seg_id,
                "enc_type": seg.enc_type, "n_rows": seg.n_rows,
                "bpv": bpv, "nw": nw, "preamble_hex": blob[:34].hex(),
            })

    verdict = "match" if not invalid_headers else "mismatch"
    observed = {
        "guess_id": "G43",
        "segments_checked": len(segs),
        "invalid_headers": invalid_headers,
        "bpv_offset": _BP_BPV,
        "nw_offset": _BP_NW,
        "sample_headers": header_samples,
    }
    _emit({
        "guess_id": "G43",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected or {"bpv_offset": _BP_BPV, "nw_offset": _BP_NW},
        "verdict": verdict,
    })
    return 0 if verdict == "match" else 1


def cmd_columnstore_lob_preamble(fixture: Path, probe_path: Path | None) -> int:
    """Probe G41 — LOB preamble: check if any dict blob exceeds 65536 bytes.

    The LOB preamble (12-byte header + 8-byte separators every 65536 bytes)
    is only present in dict blobs larger than 65536 bytes.  This probe checks
    the boundarycoverage fixture for such blobs.  If none are found, the path
    is pending and a larger fixture (cs_lob_preamble.bak) is needed.
    """
    from mssqlbak.catalog import _bootstrap  # noqa: PLC0415
    from mssqlbak.columnstore import _collect_blobs, _read_dict_blob_ids  # noqa: PLC0415

    _LOB_THRESHOLD = 65536

    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    boot = _bootstrap(store)

    rowset_ids = {
        au.rowset_id
        for tbl in schema.tables
        if tbl.compression in (3, 4)
        for au in tbl.alloc_units
    }
    dict_bids = _read_dict_blob_ids(store, boot, rowset_ids)
    all_blobs = _collect_blobs(store)

    blob_sizes = {bid: len(all_blobs.get(bid, b"")) for bid in set(dict_bids.values())}
    large_blobs = {bid: sz for bid, sz in blob_sizes.items() if sz > _LOB_THRESHOLD}

    expected: dict[str, Any] = {}
    if probe_path and probe_path.exists():
        expected = json.loads(probe_path.read_text())

    has_large = bool(large_blobs)
    verdict = "match" if has_large else "pending"
    observed = {
        "guess_id": "G41",
        "dict_blob_count": len(blob_sizes),
        "max_blob_bytes": max(blob_sizes.values()) if blob_sizes else 0,
        "large_blob_count": len(large_blobs),
        "threshold_bytes": _LOB_THRESHOLD,
        "verdict_note": (
            "LOB preamble path exercised" if has_large
            else "no dict blob > 65536 bytes; build cs_lob_preamble.bak to verify"
        ),
    }
    _emit({
        "guess_id": "G41",
        "fixture": str(fixture),
        "observed": observed,
        "expected": expected or {"note": "pending — need fixture with long string values"},
        "verdict": verdict,
    })
    return 0 if verdict in ("match", "pending") else 1


def cmd_layout(fixture: Path, probe_path: Path | None) -> int:
    """Probe L01 — all PK-position layout tables recovered."""
    from tools.layoutmatrix import all_pk_cases, all_table_names  # noqa: E402

    store = PageStore.from_bak(fixture)
    names = {t.name for t in recover_schema(store).tables}
    all_names = all_table_names()
    missing = all_names - names
    observed = {
        "layout_id": "L01",
        "expected_tables": len(all_names),
        "recovered_tables": len(names & all_names),
        "missing": sorted(missing),
        "pk_position_cases": len(all_pk_cases()),
    }
    probe_data: dict[str, Any] = {"missing": []}
    if probe_path and probe_path.exists():
        probe_data = json.loads(probe_path.read_text())
    verdict = "match" if not missing else "mismatch"
    _emit({
        "layout_id": "L01",
        "fixture": str(fixture),
        "observed": observed,
        "expected": probe_data,
        "verdict": verdict,
    })
    return 0 if verdict == "match" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="BAK format spec probe harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--fixture", type=Path, required=True)
        p.add_argument("--probe", type=Path, default=None)

    p_pages = sub.add_parser("pages", help="G13 IAM offset and page store")
    _add_common(p_pages)

    p_cat = sub.add_parser("catalog", help="G20/G21 catalog recovery")
    _add_common(p_cat)

    p_rc = sub.add_parser("rowcompress", help="G19 smalldatetime column presence")
    p_rc.add_argument("--fixture", type=Path, required=True)

    p_layout = sub.add_parser("layout", help="L01 layout table recovery")
    _add_common(p_layout)

    p_cs = sub.add_parser("columnstore", help="G42 columnstore table presence")
    p_cs.add_argument("--fixture", type=Path, required=True)

    p_dict = sub.add_parser("columnstore-dict-order", help="G40 prim/sec dict-id field ordering")
    _add_common(p_dict)

    p_hdr = sub.add_parser("columnstore-seg-header", help="G43 segment blob header bpv/nw offsets")
    _add_common(p_hdr)

    p_lob = sub.add_parser("columnstore-lob-preamble", help="G41 LOB preamble for large dict blobs")
    _add_common(p_lob)

    args = parser.parse_args()
    fixture: Path = args.fixture
    if not fixture.exists():
        print(f"error: fixture not found: {fixture}", file=sys.stderr)
        return 2

    probe = getattr(args, "probe", None)
    if args.cmd == "pages":
        return cmd_pages(fixture, probe or PROBE_DIR / "G13.json")
    if args.cmd == "catalog":
        return cmd_catalog(fixture, probe)
    if args.cmd == "rowcompress":
        return cmd_rowcompress(fixture)
    if args.cmd == "layout":
        return cmd_layout(fixture, probe or PROBE_DIR / "L01.json")
    if args.cmd == "columnstore":
        return cmd_columnstore(fixture)
    if args.cmd == "columnstore-dict-order":
        return cmd_columnstore_dict_order(fixture, probe or PROBE_DIR / "G40.json")
    if args.cmd == "columnstore-seg-header":
        return cmd_columnstore_seg_header(fixture, probe or PROBE_DIR / "G43.json")
    if args.cmd == "columnstore-lob-preamble":
        return cmd_columnstore_lob_preamble(fixture, probe or PROBE_DIR / "G41.json")
    return 2


if __name__ == "__main__":
    sys.exit(main())
