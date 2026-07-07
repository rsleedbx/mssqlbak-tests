#!/usr/bin/env python3
"""Print cs_100 column types from columnstore_minimal.bak."""
from __future__ import annotations

from pathlib import Path

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore

FIXTURE = Path(__file__).parent.parent.parent / "tests" / "fixtures_2022" / "columnstore_minimal.bak"


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    for tbl in schema.tables:
        if tbl.name == "cs_100":
            for col in tbl.columns:
                print(f"  {col.name}: type_id={col.type_id} max_length={col.max_length} scale={col.scale}")


if __name__ == "__main__":
    main()
