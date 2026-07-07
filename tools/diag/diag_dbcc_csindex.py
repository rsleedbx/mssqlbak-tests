"""DBCC CSINDEX capture diagnostic for empirical RE of [EMPIRICAL] columnstore formats.

Runs ``DBCC CSINDEX(object_type=1, ...)`` against a live SQL Server container
and captures the output alongside ``sys.column_store_segments``,
``sys.column_store_dictionaries``, and ``sys.column_store_row_groups`` DMV data
into a JSON sidecar for offline analysis.

This is the primary tool for the Phase 5 empirical RE protocol:

    1. Create a targeted fixture for the format under investigation
       (e.g. enc=5 Format A-D, ARCHIVE sub-block, large v4 dict edge cases).
    2. Run this script to capture the DBCC CSINDEX verifier output.
    3. Compare the DBCC output to the decoder's assumptions to find the gap.
    4. Fix the decoder, run tests, promote the BAK_FORMAT_SPEC §7.x tag.

Usage::

    python -m tools.diag.diag_dbcc_csindex \\
        --db <DbName> \\
        --table dbo.my_table \\
        --out /tmp/csindex_MyTable.json \\
        [--container mssql2022] \\
        [--password <SA_PASSWORD>] \\
        [--column-id 3 --row-group-id 1 --start 4300 --end 4380]

Output is a JSON file with:

    {
      "table": "dbo.my_table",
      "db": "DbName",
      "segments": [...],     // sys.column_store_segments rows
      "row_groups": [...],   // sys.column_store_row_groups rows
      "dictionaries": [...], // sys.column_store_dictionaries rows
      "csindex_raw": "..."   // raw DBCC CSINDEX output text
    }

The captured JSON can be cross-referenced against the decoder via
``tools.diag.diag_columnstore`` which reads the same table from the .bak.

Empirical RE targets (from the BAK_FORMAT_SPEC §7 [EMPIRICAL] tags):

- enc=5 Format A: item_size > 0, no sentinel (``feff == -1``), uncompressed.
  Observed: ``h92 > 0``, values at ``_ENC5_DATA_OFFSET``.
  Gap: exact header layout when ``item_size == 0`` (MAX off-row path).
- enc=5 Format B: item_size > 0, sentinel present (``feff >= 0``).
  Observed: fixed-width layout confirmed.
  Gap: BINARY/VARBINARY pool+index variant path.
- enc=5 Format C: compressed (``h92 == 0 or 0xFFFF``), single-chunk XPRESS.
  Observed: ``u16@38 == n_rows`` → pool+index in one XPRESS chunk.
  Gap: exact sub-chunk boundary when n_rows > 32767 → Format D / multichunk.
- enc=5 Format D (multichunk XPRESS): ``u32@38 == n_rows``, multiple chunks.
  Observed: chunk decompresses to 65 536 bytes + n_rows index.
  Gap: overflow-row layout in pre_meta regions.
- ARCHIVE sub-block: inner sub-block is itself XPRESS-compressed.
  Observed: ``marker in [0xFFF0, 0xFFFE]`` → compressed sub-block variant.
  Gap: exact pre_meta layout for overflow rows in compressed mode.
- v4 Huffman dict large page count: pages > 1 in the 128-entry page tree.
  Observed: standard 1-page decode confirmed.
  Gap: multi-page decode when entry count > 128.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import fixture_credentials  # noqa: E402


def _run_sql(container: str, password: str, db: str, sql: str) -> str:
    """Execute T-SQL against the container and return stdout."""
    result = subprocess.run(
        [
            "podman", "exec", container,
            "/opt/mssql-tools18/bin/sqlcmd",
            "-S", "localhost", "-U", "sa", "-P", password,
            "-d", db,
            "-Q", sql,
            "-o", "/dev/stdout",
            "-s", "|",
            "-W",
            "-C",   # trust server certificate
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _fetch_dmv_segments(container: str, password: str, db: str, table: str) -> list[dict]:
    """Fetch sys.column_store_segments rows for *table*."""
    schema, name = table.split(".") if "." in table else ("dbo", table)
    sql = f"""
SELECT
    p.object_id,
    s.name   AS schema_name,
    t.name   AS table_name,
    c.name   AS column_name,
    ty.name  AS sql_type,
    css.column_id,
    css.segment_id,
    css.version,
    css.encoding_type,
    css.row_count,
    css.has_nulls,
    css.base_id,
    css.magnitude,
    css.primary_dictionary_id,
    css.secondary_dictionary_id,
    css.min_data_id,
    css.max_data_id,
    css.null_value,
    css.on_disk_size
FROM sys.column_store_segments css
JOIN sys.partitions p ON p.partition_id = css.partition_id
JOIN sys.columns c ON c.object_id = p.object_id AND c.column_id = css.column_id
JOIN sys.types ty ON ty.user_type_id = c.user_type_id
JOIN sys.tables t ON t.object_id = p.object_id
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE s.name = '{schema}' AND t.name = '{name}'
ORDER BY css.segment_id, css.column_id
"""
    raw = _run_sql(container, password, db, sql)
    rows = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 19 or parts[0] in ("object_id", "-" * 9, ""):
            continue
        try:
            rows.append({
                "object_id":                int(parts[0]),
                "schema_name":              parts[1],
                "table_name":               parts[2],
                "column_name":              parts[3],
                "sql_type":                 parts[4],
                "column_id":                int(parts[5]),
                "segment_id":               int(parts[6]),
                "version":                  int(parts[7]),
                "encoding_type":            int(parts[8]),
                "row_count":                int(parts[9]),
                "has_nulls":                parts[10] == "1",
                "base_id":                  int(parts[11]) if parts[11] not in ("NULL", "") else None,
                "magnitude":                float(parts[12]) if parts[12] not in ("NULL", "") else None,
                "primary_dictionary_id":    int(parts[13]) if parts[13] not in ("NULL", "-1", "") else None,
                "secondary_dictionary_id":  int(parts[14]) if parts[14] not in ("NULL", "-1", "") else None,
                "min_data_id":              int(parts[15]) if parts[15] not in ("NULL", "") else None,
                "max_data_id":              int(parts[16]) if parts[16] not in ("NULL", "") else None,
                "null_value":               int(parts[17]) if parts[17] not in ("NULL", "") else None,
                "on_disk_size":             int(parts[18]) if parts[18] not in ("NULL", "") else None,
            })
        except (ValueError, IndexError):
            continue
    return rows


def _fetch_dmv_row_groups(container: str, password: str, db: str, table: str) -> list[dict]:
    """Fetch sys.column_store_row_groups rows for *table*."""
    schema, name = table.split(".") if "." in table else ("dbo", table)
    sql = f"""
SELECT
    csr.object_id,
    csr.row_group_id,
    csr.state_description,
    csr.total_rows,
    csr.deleted_rows,
    csr.size_in_bytes
FROM sys.column_store_row_groups csr
JOIN sys.tables t ON t.object_id = csr.object_id
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE s.name = '{schema}' AND t.name = '{name}'
ORDER BY csr.row_group_id
"""
    raw = _run_sql(container, password, db, sql)
    rows = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6 or parts[0] in ("object_id", "-" * 9, ""):
            continue
        try:
            rows.append({
                "object_id":   int(parts[0]),
                "row_group_id": int(parts[1]),
                "state_desc":  parts[2],
                "total_rows":  int(parts[3]),
                "deleted_rows": int(parts[4]) if parts[4] not in ("NULL", "") else 0,
                "size_in_bytes": int(parts[5]) if parts[5] not in ("NULL", "") else None,
            })
        except (ValueError, IndexError):
            continue
    return rows


def _fetch_dmv_dictionaries(container: str, password: str, db: str, table: str) -> list[dict]:
    """Fetch sys.column_store_dictionaries rows for *table*."""
    schema, name = table.split(".") if "." in table else ("dbo", table)
    sql = f"""
SELECT
    csd.object_id,
    c.name AS column_name,
    csd.column_id,
    csd.dictionary_id,
    csd.type,
    csd.rows_count,
    csd.on_disk_size
FROM sys.column_store_dictionaries csd
JOIN sys.columns c ON c.object_id = csd.object_id AND c.column_id = csd.column_id
JOIN sys.tables t ON t.object_id = csd.object_id
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE s.name = '{schema}' AND t.name = '{name}'
ORDER BY csd.column_id, csd.dictionary_id
"""
    raw = _run_sql(container, password, db, sql)
    rows = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7 or parts[0] in ("object_id", "-" * 9, ""):
            continue
        try:
            rows.append({
                "object_id":    int(parts[0]),
                "column_name":  parts[1],
                "column_id":    int(parts[2]),
                "dictionary_id": int(parts[3]),
                "type":         int(parts[4]),
                "rows_count":   int(parts[5]) if parts[5] not in ("NULL", "") else None,
                "on_disk_size": int(parts[6]) if parts[6] not in ("NULL", "") else None,
            })
        except (ValueError, IndexError):
            continue
    return rows


def _build_dbcc_csindex_sql(
    *,
    table: str,
    column_id: int,
    row_group_id: int,
    object_type: int,
    print_option: int,
    start: int | None = None,
    end: int | None = None,
) -> str:
    """Build a bounded DBCC CSINDEX command for one columnstore segment."""
    range_args = ""
    if start is not None or end is not None:
        if start is None or end is None:
            raise ValueError("start and end must be provided together")
        range_args = f", {start}, {end}"

    return f"""
SET NOCOUNT ON;
DECLARE @db INT = DB_ID();
DECLARE @hobt BIGINT;
SELECT TOP 1 @hobt = p.hobt_id
FROM sys.partitions p
JOIN sys.indexes i ON i.object_id = p.object_id AND i.index_id = p.index_id
WHERE p.object_id = OBJECT_ID(N'{table}') AND i.type IN (5, 6)
ORDER BY p.partition_number;
DBCC TRACEON(3604);
DBCC CSINDEX(@db, @hobt, {column_id}, {row_group_id}, {object_type}, {print_option}{range_args}) WITH NO_INFOMSGS;
"""


def _run_dbcc_csindex(
    container: str,
    password: str,
    db: str,
    table: str,
    *,
    column_id: int | None = None,
    row_group_id: int = 0,
    object_type: int = 1,
    print_option: int = 0,
    start: int | None = None,
    end: int | None = None,
) -> str:
    """Run DBCC CSINDEX and return the raw text output.

    ``DBCC CSINDEX(object_type=1, ...)`` dumps the internal segment tree for
    the given columnstore object.  This is the primary RE tool for understanding
    the exact on-disk layout of enc=5 Format A-D, ARCHIVE sub-blocks, and v4
    Huffman dict pages.

    Requires SQL Server 2016+ with trace flag 2588 enabled (or SA permissions
    in SQL Server 2022+).
    """
    if column_id is None:
        return "-- DBCC CSINDEX: --column-id is required for the six-argument syntax"

    dbcc_sql = _build_dbcc_csindex_sql(
        table=table,
        column_id=column_id,
        row_group_id=row_group_id,
        object_type=object_type,
        print_option=print_option,
        start=start,
        end=end,
    )
    try:
        return _run_sql(container, password, db, dbcc_sql)
    except subprocess.CalledProcessError as exc:
        return f"-- DBCC CSINDEX failed: {exc.stderr}"


def capture_csindex(
    container: str,
    password: str,
    db: str,
    table: str,
    out_path: Path,
    *,
    column_id: int | None = None,
    row_group_id: int = 0,
    object_type: int = 1,
    print_option: int = 0,
    start: int | None = None,
    end: int | None = None,
) -> None:
    """Capture DBCC CSINDEX + DMV data for *table* into a JSON sidecar."""
    print(f"Capturing segments for {table} in {db}...", file=sys.stderr)
    segments = _fetch_dmv_segments(container, password, db, table)
    print(f"  {len(segments)} segment rows", file=sys.stderr)

    row_groups = _fetch_dmv_row_groups(container, password, db, table)
    print(f"  {len(row_groups)} row groups", file=sys.stderr)

    dicts = _fetch_dmv_dictionaries(container, password, db, table)
    print(f"  {len(dicts)} dictionary rows", file=sys.stderr)

    print("Running DBCC CSINDEX...", file=sys.stderr)
    csindex_raw = _run_dbcc_csindex(
        container,
        password,
        db,
        table,
        column_id=column_id,
        row_group_id=row_group_id,
        object_type=object_type,
        print_option=print_option,
        start=start,
        end=end,
    )

    out = {
        "table": table,
        "db": db,
        "csindex_args": {
            "column_id": column_id,
            "row_group_id": row_group_id,
            "object_type": object_type,
            "print_option": print_option,
            "start": start,
            "end": end,
        },
        "segments": segments,
        "row_groups": row_groups,
        "dictionaries": dicts,
        "csindex_raw": csindex_raw,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"==> {out_path}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture DBCC CSINDEX + DMV data for empirical RE of [EMPIRICAL] formats.",
    )
    parser.add_argument("--db", required=True, help="database name")
    parser.add_argument("--table", required=True, help="schema.table name, e.g. dbo.my_table")
    parser.add_argument("--out", type=Path, default=None,
                        help="output JSON path (default: /tmp/<table>_csindex.json)")
    parser.add_argument("--container", default=None,
                        help="Podman container name (default: from fixture_credentials)")
    parser.add_argument("--password", default=None,
                        help="SA password (default: from fixture_credentials)")
    parser.add_argument("--column-id", type=int, default=None,
                        help="DBCC CSINDEX column id; often DMV column_id + 1")
    parser.add_argument("--row-group-id", type=int, default=0,
                        help="columnstore segment/row group id")
    parser.add_argument("--object-type", type=int, default=1,
                        help="DBCC CSINDEX object type: 1=segment, 2=dictionary")
    parser.add_argument("--print-option", type=int, default=0,
                        help="DBCC CSINDEX print option")
    parser.add_argument("--start", type=int, default=None,
                        help="optional bounded start row/index")
    parser.add_argument("--end", type=int, default=None,
                        help="optional bounded end row/index")
    args = parser.parse_args(argv)

    _user, _password, _container = fixture_credentials()
    container = args.container or _container
    password = args.password or _password

    out_path = args.out or Path(f"/tmp/{args.table.replace('.', '_')}_csindex.json")
    capture_csindex(
        container,
        password,
        args.db,
        args.table,
        out_path,
        column_id=args.column_id,
        row_group_id=args.row_group_id,
        object_type=args.object_type,
        print_option=args.print_option,
        start=args.start,
        end=args.end,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
