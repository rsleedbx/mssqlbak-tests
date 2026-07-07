"""Columnstore segment diagnostics — run without sandbox prompts.

Usage:
    .venv/bin/python tools/diag_columnstore.py [BAK] [TABLE]

Defaults:
    BAK   = tests/fixtures_2022/columnstore_minimal.bak
    TABLE = cs_1000  (use "all" to check all cs_* tables)

Prints, per table and per column:
  • encoding type, bpv, nw, n_stored
  • null counts from mssqlbak vs SQL Server ground-truth stats.json
  • hex-dump of the dictionary blob (first 256 bytes) for string columns
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import tempfile

import pyarrow as pa
import pyarrow.dataset as ds

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (
    _bootstrap,
    _collect_blobs,
    _deinterleave_column_lob,
    _parse_dict_strings,
    _read_column_segments,
    _read_dict_blob_ids,
    _unwrap_archive_blob,
)
from mssqlbak.extract import extract_bak
from mssqlbak.pages import PageStore
from mssqlbak.sink import DeltaSink
from mssqlbak.types import NCHAR, NTEXT, NVARCHAR


def _hexdump(data: bytes, limit: int = 256, indent: str = "  ") -> None:
    for i in range(0, min(len(data), limit), 16):
        chunk = data[i : i + 16]
        print(f"{indent}[{i:4d}] {chunk.hex()}")


def _null_counts_from_extraction(bak: pathlib.Path) -> dict[str, dict[str, int]]:
    results: dict[str, list[pa.Table]] = {}

    class _Sink:
        def open_table(self, fqname: str, schema: pa.Schema) -> None:
            self._cur = fqname

        def write_batch(self, batch: pa.RecordBatch) -> None:
            results.setdefault(self._cur, []).append(batch.to_pydict())

        def close_table(self) -> None:
            pass

        def close(self) -> None:
            pass

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak(bak, DeltaSink(pathlib.Path(tmp)))
        out: dict[str, dict[str, int]] = {}
        for schema_dir in sorted(pathlib.Path(tmp).iterdir()):
            for tbl_dir in sorted(schema_dir.iterdir()):
                t = ds.dataset(tbl_dir, format="parquet").to_table()
                key = f"dbo.{tbl_dir.name}"
                out[key] = {c: t.column(c).null_count for c in t.schema.names}
    return out


def _load_stats(bak: pathlib.Path) -> dict[str, dict[str, int]]:
    stats_path = bak.with_suffix(".bak.stats.json")
    if not stats_path.exists():
        return {}
    data = json.loads(stats_path.read_text())
    result: dict[str, dict[str, int]] = {}
    for tbl in data.get("tables", []):
        key = f"{tbl['schema']}.{tbl['name']}"
        result[key] = {col["name"]: col["null_count"] for col in tbl.get("columns", [])}
    return result


def diag(bak: pathlib.Path, table_filter: str = "cs_1000") -> None:
    print(f"\n{'='*70}")
    print(f"BAK: {bak}")
    print(f"{'='*70}")

    store = PageStore.from_bak(bak)
    boot = _bootstrap(store)
    schema = recover_schema(store)
    all_blobs = _collect_blobs(store)

    print("\n[1] Extracting via mssqlbak …", flush=True)
    extracted = _null_counts_from_extraction(bak)

    print("[2] Loading ground-truth stats …", flush=True)
    ground_truth = _load_stats(bak)

    for t in schema.tables:
        if table_filter != "all" and t.name != table_filter:
            continue
        key = f"dbo.{t.name}"
        print(f"\n{'─'*60}")
        print(f"TABLE: {t.name}")

        rowset_ids = {au.rowset_id for au in t.alloc_units}
        segs = list(_read_column_segments(store, boot, rowset_ids))
        col_by_id = {col.colid + 1: col for col in t.columns}
        dict_bids = _read_dict_blob_ids(store, boot, rowset_ids)
        hobt = segs[0].hobt_id if segs else 0

        ext_nc = extracted.get(key, {})
        gt_nc = ground_truth.get(key, {})

        for s in sorted(segs, key=lambda s: s.col_id):
            col = col_by_id.get(s.col_id)
            if col is None:
                continue
            blob_raw = all_blobs.get(s.blob_id, b"")
            blob = _unwrap_archive_blob(blob_raw)
            bpv = struct.unpack_from("<H", blob, 34)[0] if len(blob) > 36 else 0
            nw = struct.unpack_from("<I", blob, 36)[0] if len(blob) > 40 else 0
            vpw = 64 // bpv if bpv > 0 else 0
            n_stored = nw * vpw

            got = ext_nc.get(col.name, "?")
            want = gt_nc.get(col.name, "?")
            mismatch = " *** MISMATCH" if got != want else ""
            print(
                f"  {col.name:12s} enc={s.enc_type} bpv={bpv:3d} nw={nw:6d}"
                f" n_stored={n_stored:7d} n={s.n_rows}"
                f"  null: mssqlbak={got} expected={want}{mismatch}"
            )

            # For enc=3 columns, dump the dictionary blob.
            if s.enc_type == 3 or mismatch:
                dict_id = (
                    s.sec_dict
                    if s.sec_dict >= 0
                    else (s.prim_dict if s.prim_dict >= 0 else 0)
                )
                dict_bid = dict_bids.get((hobt, s.col_id, dict_id))
                if dict_bid is not None:
                    raw_dict = _unwrap_archive_blob(all_blobs.get(dict_bid, b""))
                    dil = _deinterleave_column_lob(raw_dict)
                    is_unicode = col.type_id in (NVARCHAR, NCHAR, NTEXT)
                    dictionary = _parse_dict_strings(
                        dil,
                        as_bytes=False,
                        store=store,
                        unicode_first=is_unicode,
                    )
                    print(
                        f"    dict blob: raw={len(raw_dict)}B dil={len(dil)}B"
                        f" entries={len(dictionary)}: {dictionary[:6]}"
                    )
                    if mismatch:
                        print("    dict blob hex (first 256 B):")
                        _hexdump(dil)

            # For enc=5 columns with mismatch, dump full blob and find sentinel.
            if s.enc_type == 5 and mismatch:
                sentinel = b"\xfe\xff"
                feff = blob.find(sentinel)
                print(f"    enc=5 blob: len={len(blob)}  sentinel @ {feff}")
                # Header fields at [92-95] and [86-87]
                if len(blob) >= 96:
                    h92 = struct.unpack_from("<H", blob, 92)[0]
                    h94 = struct.unpack_from("<H", blob, 94)[0]
                    h86 = struct.unpack_from("<H", blob, 86)[0]
                    h82 = struct.unpack_from("<H", blob, 82)[0]
                    print(f"    hdr[82]={h82} hdr[86]={h86} hdr[92]={h92} hdr[94]={h94}")
                _hexdump(blob, limit=len(blob))  # full blob


def main() -> None:
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    bak_arg = sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures_2022/columnstore_minimal.bak"
    table_arg = sys.argv[2] if len(sys.argv) > 2 else "cs_1000"
    bak = repo_root / bak_arg if not pathlib.Path(bak_arg).is_absolute() else pathlib.Path(bak_arg)
    diag(bak, table_arg)


if __name__ == "__main__":
    main()
