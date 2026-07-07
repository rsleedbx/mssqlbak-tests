#!/usr/bin/env python3
"""Identify which row is missing when extract_bak_to_delta processes 2017 temporal_update."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak import extract_bak_to_delta  # type: ignore[attr-defined]
from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]

FIXTURE = fixture("2017", "dirtycoverage_temporal_update.bak")


def via_read_table(table: str) -> list[dict]:  # type: ignore[type-arg]
    store, schema, _boot, _blobs = open_store(FIXTURE)
    tbl = find_table(schema, table)
    if tbl is None:
        return []
    return list(read_table_rows(store, tbl, schema.obj_to_name))  # type: ignore[union-attr]


def via_delta(table: str) -> list[dict]:  # type: ignore[type-arg]
    import deltalake  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(FIXTURE, tmp)
        for schema_dir in sorted(Path(tmp).iterdir()):
            for tbl_dir in sorted(schema_dir.iterdir()):
                if tbl_dir.name == table:
                    dt = deltalake.DeltaTable(str(tbl_dir))
                    pa_tbl = dt.to_pyarrow_table()
                    return pa_tbl.to_pylist()  # type: ignore[no-any-return]
    return []


def main() -> None:
    rows_api = via_read_table("temporal_test")
    rows_delta = via_delta("temporal_test")

    ids_api = {r["id"] for r in rows_api}
    ids_delta = {r["id"] for r in rows_delta}

    print(f"read_table_rows: {len(rows_api)} rows  ids={sorted(ids_api)}")
    print(f"extract_bak_to_delta: {len(rows_delta)} rows  ids={sorted(ids_delta)}")
    missing = ids_api - ids_delta
    extra = ids_delta - ids_api
    if missing:
        print(f"\nMissing in delta (present in read_table): {sorted(missing)}")
        for r in rows_api:
            if r["id"] in missing:
                print(f"  {r}")
    if extra:
        print(f"\nExtra in delta (not in read_table): {sorted(extra)}")


if __name__ == "__main__":
    main()
