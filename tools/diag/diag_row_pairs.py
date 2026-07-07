#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Show first/last 10 row id+code pairs for archive_part_roundtrip partition 1.

Uses the FULL mssqlbak decoder to show what id and code values are paired.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mssqlbak.pages import PageStore
from mssqlbak.catalog import recover_schema
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
    tbl = next(t for t in schema.tables if t.name == "archive_part_roundtrip")
    rows = list(read_table_rows(store, tbl, schema.obj_to_name))

    print(f"Total rows: {len(rows)}")

    # Show first 15 rows
    print("\nFirst 15 rows (id, code):")
    for i, r in enumerate(rows[:15]):
        cval = r.get("code")
        cval_s = None if cval is None else repr(cval.rstrip())
        print(f"  [{i}]: id={r.get('id')} code={cval_s}")

    # Show rows around id=1
    print("\nRows where id <= 10:")
    for i, r in enumerate(rows):
        rid = r.get("id")
        if rid is not None and rid <= 10:
            cval = r.get("code")
            cval_s = None if cval is None else repr(cval.rstrip())
            print(f"  [{i}]: id={rid} code={cval_s}")

    # Show last 15 rows
    print(f"\nLast 15 rows (id, code) [positions {len(rows)-15}..{len(rows)-1}]:")
    for i, r in enumerate(rows[-15:]):
        cval = r.get("code")
        cval_s = None if cval is None else repr(cval.rstrip())
        print(f"  [{len(rows)-15+i}]: id={r.get('id')} code={cval_s}")


if __name__ == "__main__":
    main()
