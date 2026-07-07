"""Probe enc=5 decode for one column of a real-world columnstore table."""

from __future__ import annotations

import sys

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import (  # type: ignore[attr-defined]
    _bootstrap,
    _collect_blobs,
    _decode_enc5,
    _decode_enc5_archive,
    _enc5_item_size,
    _read_column_segments,
    _unwrap_archive_blob,
)
from mssqlbak.pages import PageStore


def main(argv: list[str]) -> int:
    path = argv[1]
    table = argv[2]
    col_id = int(argv[3])

    store = PageStore.from_bak(path)
    schema = recover_schema(store)
    boot = _bootstrap(store)
    blobs = _collect_blobs(store)

    tbl = next(t for t in schema.tables if t.name == table)
    col = next(c for c in tbl.columns if c.colid == col_id)
    print(f"col {col.name} type_id={col.type_id} max_len={col.max_length} nullable={col.nullable}")

    rowset_ids = {au.rowset_id for au in tbl.alloc_units}
    segs = [s for s in _read_column_segments(store, boot, rowset_ids) if s.col_id == col_id]
    print(f"{len(segs)} segments")
    for i, seg in enumerate(segs):
        raw = blobs.get(seg.blob_id, b"")
        blob = _unwrap_archive_blob(raw)
        vals = _decode_enc5(seg, blob, col)
        nnull = sum(1 for v in vals if v is None)
        sample = [v for v in vals[:6]]
        print(f"  seg[{i}] enc={seg.enc_type} n_rows={seg.n_rows} blob={seg.blob_id} "
              f"raw_len={len(raw)} unwrap_len={len(blob)} has_null={seg.has_null} "
              f"-> decoded {len(vals)} nulls={nnull}")
        print(f"          sample: {sample}")
        cw = _enc5_item_size(col)
        arch = _decode_enc5_archive(blob, seg.n_rows, cw)
        anull = sum(1 for v in arch if v is None)
        print(f"          ARCHIVE(cw={cw}): nulls={anull} sample={[bytes(v) if v else None for v in arch[:4]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
