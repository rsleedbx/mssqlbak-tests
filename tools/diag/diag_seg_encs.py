#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Show all column segment encodings for archive_part_roundtrip."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.catalog import recover_schema
from mssqlbak.columnstore import _bootstrap, _read_column_segments  # type: ignore[attr-defined]
from mssqlbak.pages import PageStore

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "fixtures_2022"
    / "archive_columnstore_partition_full.bak"
)


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    boot = _bootstrap(store)

    for tbl in schema.tables:
        if tbl.name not in ("archive_part_roundtrip", "archive_part_single"):
            continue
        rowset_ids = {au.rowset_id for au in tbl.alloc_units}
        segs = _read_column_segments(store, boot, rowset_ids)

        print(f"\n=== {tbl.name} ===")
        for seg in segs:
            print(
                f"  col_id={seg.col_id:2d}  enc={seg.enc_type}  n_rows={seg.n_rows:6d}"
                f"  hobt={seg.hobt_id}  blob_id={seg.blob_id}"
            )


if __name__ == "__main__":
    main()
