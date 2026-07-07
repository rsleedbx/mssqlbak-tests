#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

COLUMN_KEYS = ("name", "sql_type", "null_count", "min_val", "max_val")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare matching JSON files across two fixture directories and fail "
            "if any name/sql_type/null_count/min_val/max_val values differ."
        )
    )
    parser.add_argument("--dir1", required=True, type=Path, help="First directory")
    parser.add_argument("--dir2", required=True, type=Path, help="Second directory")
    return parser.parse_args()


def _json_files(base_dir: Path) -> dict[Path, Path]:
    return {
        path.relative_to(base_dir): path
        for path in sorted(base_dir.rglob("*.json"))
        if path.is_file()
    }


def _extract_column_fields(node: Any) -> dict[str, Any]:
    """Extract comparable fields using schema.table.column identity keys.

    Output keys are formatted as:
    ``<schema>.<table>.<column>.<field>``.
    """
    out: dict[str, Any] = {}
    if not isinstance(node, dict):
        return out

    tables = node.get("tables")
    if not isinstance(tables, list):
        return out

    for t_idx, table in enumerate(tables):
        if not isinstance(table, dict):
            continue
        schema = str(table.get("schema", f"<schema_{t_idx}>"))
        table_name = str(table.get("name", f"<table_{t_idx}>"))
        table_id = f"{schema}.{table_name}"

        columns = table.get("columns")
        if not isinstance(columns, list):
            continue

        for c_idx, column in enumerate(columns):
            if not isinstance(column, dict):
                continue
            column_name = str(column.get("name", f"<column_{c_idx}>"))
            column_id = f"{table_id}.{column_name}"
            for field in COLUMN_KEYS:
                if field in column:
                    out[f"{column_id}.{field}"] = column[field]
    return out


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    args = _parse_args()
    dir1 = args.dir1.resolve()
    dir2 = args.dir2.resolve()

    if not dir1.is_dir():
        print(f"error: --dir1 is not a directory: {dir1}")
        return 2
    if not dir2.is_dir():
        print(f"error: --dir2 is not a directory: {dir2}")
        return 2

    files1 = _json_files(dir1)
    files2 = _json_files(dir2)
    rel1 = set(files1)
    rel2 = set(files2)

    only1 = sorted(rel1 - rel2)
    only2 = sorted(rel2 - rel1)
    common = sorted(rel1 & rel2)

    failures = 0

    if only1:
        failures += len(only1)
        print("json files only in --dir1:")
        for rel in only1:
            print(f"  {rel}")
    if only2:
        failures += len(only2)
        print("json files only in --dir2:")
        for rel in only2:
            print(f"  {rel}")

    for rel in common:
        data1 = _load_json(files1[rel])
        data2 = _load_json(files2[rel])
        fields1 = _extract_column_fields(data1)
        fields2 = _extract_column_fields(data2)

        paths1 = set(fields1)
        paths2 = set(fields2)
        all_paths = sorted(paths1 | paths2)
        file_had_diff = False

        for field_path in all_paths:
            in1 = field_path in fields1
            in2 = field_path in fields2
            if not in1 or not in2:
                if not file_had_diff:
                    print(f"\ndifferences in {rel}:")
                    file_had_diff = True
                failures += 1
                if in1:
                    print(f"  {field_path}: missing in --dir2, dir1={fields1[field_path]!r}")
                else:
                    print(f"  {field_path}: missing in --dir1, dir2={fields2[field_path]!r}")
                continue

            if fields1[field_path] != fields2[field_path]:
                if not file_had_diff:
                    print(f"\ndifferences in {rel}:")
                    file_had_diff = True
                failures += 1
                print(
                    f"  {field_path}: dir1={fields1[field_path]!r} != dir2={fields2[field_path]!r}"
                )

    if failures:
        print(f"\nFAIL: found {failures} mismatch(es)")
        return 1

    print(f"OK: compared {len(common)} common JSON file(s), no target-field differences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
