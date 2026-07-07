#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Show first/last 15 row id+code pairs for archive_part_mixed to see pairing pattern."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == "archive_part_mixed")
    rows = list(read_table_rows(store, tbl, schema.obj_to_name))

    print(f"Total rows: {len(rows)}")

    # Show rows where id is near 35001 (partition 2 boundary)
    print("\nRows where 35000 <= id <= 35015:")
    for i, r in enumerate(rows):
        rid = r.get("id")
        if rid is not None and 35000 <= rid <= 35015:
            cval = r.get("code")
            cval_s = None if cval is None else repr(cval.rstrip())
            print(f"  [{i}]: id={rid} code={cval_s}")

    # Show first 10 rows overall
    print("\nFirst 10 rows:")
    for i, r in enumerate(rows[:10]):
        cval = r.get("code")
        cval_s = None if cval is None else repr(cval.rstrip())
        print(f"  [{i}]: id={r.get('id')} code={cval_s}")

    # Show rows around 35001
    by_id = {r["id"]: r for r in rows if r.get("id") is not None}
    print("\nby_id[35001]:", repr(by_id.get(35001, {}).get("code")))
    print("by_id[40001]:", repr(by_id.get(40001, {}).get("code")))

    # Check if partition 2 (35001..70000) is archive or standard columnstore
    # by looking at enc type used
    from mssqlbak.columnstore import (  # type: ignore[attr-defined]
        _bootstrap,
        _collect_blobs,
        _enc5_archive_has_compressed_subblocks,
        _read_column_segments,
        _unwrap_archive_blob,
    )

    boot = _bootstrap(store)
    rowset_ids = {au.rowset_id for au in tbl.alloc_units}
    segs = _read_column_segments(store, boot, rowset_ids)
    all_blobs = _collect_blobs(store)

    print("\nSegments for archive_part_mixed:")
    for seg in segs:
        if seg.col_id == 3:
            raw = all_blobs.get(seg.blob_id, b"")
            inner = _unwrap_archive_blob(raw)
            has_xpress = _enc5_archive_has_compressed_subblocks(inner)
            print(
                f"  col_id={seg.col_id} enc={seg.enc_type} n_rows={seg.n_rows:6d}"
                f"  hobt={seg.hobt_id}  xpress={has_xpress}"
            )


if __name__ == "__main__":
    main()
