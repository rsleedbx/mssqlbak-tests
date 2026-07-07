#!/usr/bin/env python3
"""Compare read_table_rows vs extract_bak_to_delta row counts for 2017 temporal_update."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, find_table, open_store

from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]
from mssqlbak import extract_bak_to_delta  # type: ignore[attr-defined]

FIXTURE_2017 = fixture("2017", "dirtycoverage_temporal_update.bak")
FIXTURE_2019 = fixture("2019", "dirtycoverage_temporal_update.bak")


def count_via_rows(path: Path, table: str) -> int:
    store, schema, _boot, _blobs = open_store(path)
    tbl = find_table(schema, table)
    if tbl is None:
        return -1
    return len(list(read_table_rows(store, tbl, schema.obj_to_name)))  # type: ignore[union-attr]


def count_via_delta(path: Path, table: str) -> int:
    import deltalake  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(path), tmp)
        for schema_dir in sorted(Path(tmp).iterdir()):
            for tbl_dir in sorted(schema_dir.iterdir()):
                if tbl_dir.name == table:
                    try:
                        dt = deltalake.DeltaTable(str(tbl_dir))
                        return len(dt.to_pyarrow_table())
                    except Exception:
                        return -999


    return -2


def main() -> None:
    for version, path in (("2017", FIXTURE_2017), ("2019", FIXTURE_2019)):
        for tbl in ("temporal_test", "temporal_test_history"):
            via_rows = count_via_rows(path, tbl)
            via_delta = count_via_delta(path, tbl)
            match = "✓" if via_rows == via_delta else "✗"
            print(f"{version}  {tbl:<30}  read_table_rows={via_rows:4d}  delta={via_delta:4d}  {match}")


if __name__ == "__main__":
    main()
