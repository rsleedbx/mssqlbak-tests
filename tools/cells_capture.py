#!/usr/bin/env python3
"""Capture per-cell ground truth for a restored .bak into a ``<bak>.cells/`` sidecar.

For every user table this restores-and-reads (the DB is already restored by
``register_bak``), it:

1. resolves a stable key (PK -> unique index -> identity -> digest-only),
2. SELECTs every column, canonicalizes each cell via the
   :func:`tools.cell_canon.canon` SSOT,
3. writes ``<fqn>.parquet`` for full/sample tables (canonical strings,
   key-sorted) or, for keyless ``digest-only`` tables, each column's
   binary-sorted non-null canonical values (the exact set ``column_digest``
   hashes) so digest mismatches are diagnosable offline without a SQL restore,
   and
4. records a ``_manifest.json`` entry with the per-column
   :func:`tools.cell_canon.column_digest` over the FULL column.

The parquet holds canonical strings (not typed values) so the per-cell compare
and the digest use the exact same bytes — ``tools/value_verify.py`` consumes both.
Connection is the typed ``mssql_python`` TCP path (``fixture_utils.connect``).
"""

from __future__ import annotations

import datetime
import json
import math
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import fixture_utils
from tools.cell_canon import _base_type, canon, clr_text_method, column_digest

if TYPE_CHECKING:
    import mssql_python as _mssql

MANIFEST_NAME = "_manifest.json"


def _build_sql_type(base: str, max_length: int, precision: int, scale: int) -> str:
    """Reconstruct a readable type string; only decimal scale affects canon()."""
    b = base.lower()
    if b in ("decimal", "numeric"):
        return f"{b}({precision},{scale})"
    if b in ("char", "varchar", "binary", "varbinary"):
        n = "max" if max_length == -1 else str(max_length)
        return f"{b}({n})"
    if b in ("nchar", "nvarchar"):
        n = "max" if max_length == -1 else str(max_length // 2)
        return f"{b}({n})"
    return b


def _select_expr(col: str, sql_type: str) -> str:
    """Projection for one column: canonical-string method call for CLR UDTs.

    hierarchyid / geometry / geography are returned by the driver as raw UDT
    bytes, which ``canon`` cannot turn into the path / WKT string mssqlbak
    decodes them to.  Project them through ``.ToString()`` / ``.AsTextZM()``
    (NVARCHAR(MAX) to avoid truncating LOB spatial) so the captured ground truth
    matches the decoder.  All other columns are selected as-is.
    """
    method = clr_text_method(_base_type(sql_type))
    if method is not None:
        return f"CAST([{col}].{method} AS NVARCHAR(MAX)) AS [{col}]"
    if _base_type(sql_type) == "sql_variant":
        # mssql_python can fail fetching heterogeneous sql_variant columns via
        # SQLGetData.  A plain CAST(sql_variant AS NVARCHAR) is lossy for dates,
        # times, binary, and scale-bearing numerics, so project stable text by
        # the stored base type before the Python-side canon() pass.
        q = f"[{col}]"
        base = f"LOWER(CONVERT(NVARCHAR(128), SQL_VARIANT_PROPERTY({q}, 'BaseType')))"
        return (
            "CASE "
            f"WHEN {base} = 'uniqueidentifier' THEN LOWER(CONVERT(NVARCHAR(36), TRY_CONVERT(uniqueidentifier, {q}))) "
            f"WHEN {base} IN ('binary', 'varbinary') THEN LOWER(CONVERT(VARCHAR(MAX), TRY_CONVERT(VARBINARY(MAX), {q}), 1)) "
            f"WHEN {base} = 'date' THEN CONVERT(NVARCHAR(30), TRY_CONVERT(date, {q}), 23) "
            f"WHEN {base} IN ('datetime', 'smalldatetime') THEN CONVERT(NVARCHAR(30), TRY_CONVERT(datetime2(0), {q}), 120) "
            f"WHEN {base} = 'datetime2' THEN REPLACE(CONVERT(NVARCHAR(33), TRY_CONVERT(datetime2(7), {q}), 126), 'T', ' ') "
            f"WHEN {base} = 'time' THEN CONVERT(NVARCHAR(32), TRY_CONVERT(time(7), {q})) "
            f"WHEN {base} = 'datetimeoffset' THEN REPLACE(CONVERT(NVARCHAR(40), TRY_CONVERT(datetimeoffset(7), {q}), 126), 'T', ' ') "
            f"ELSE CAST({q} AS NVARCHAR(MAX)) "
            f"END AS [{col}]"
        )
    return f"[{col}]"


def _columns(cur: "_mssql.Cursor", schema: str, table: str) -> list[dict[str, str]]:
    cur.execute(
        """
        SELECT
          c.name,
          ty.name,
          COALESCE(base_ty.name, ty.name) AS base_type_name,
          c.max_length,
          c.precision,
          c.scale
        FROM sys.columns c
        JOIN sys.types ty ON ty.user_type_id = c.user_type_id
        LEFT JOIN sys.types base_ty
          ON base_ty.user_type_id = c.system_type_id
         AND base_ty.system_type_id = c.system_type_id
        JOIN sys.tables tbl ON tbl.object_id = c.object_id
        JOIN sys.schemas s ON s.schema_id = tbl.schema_id
        WHERE s.name = ? AND tbl.name = ?
          AND c.is_computed = 0
          AND c.is_hidden = 0
          AND c.name NOT LIKE '$node[_]id[_]%'
          AND c.name NOT LIKE '$edge[_]id[_]%'
          AND c.name NOT LIKE '$from[_]id[_]%'
          AND c.name NOT LIKE '$to[_]id[_]%'
        ORDER BY c.column_id;
        """,
        [schema, table],
    )
    cols = []
    for row in cur.fetchall():
        sql_type = _build_sql_type(row[1], int(row[3]), int(row[4]), int(row[5]))
        base_sql_type = _build_sql_type(row[2], int(row[3]), int(row[4]), int(row[5]))
        col = {"name": row[0], "sql_type": sql_type}
        if base_sql_type != sql_type:
            col["base_sql_type"] = base_sql_type
        cols.append(col)
    return cols


def _resolve_key(
    cur: "_mssql.Cursor", schema: str, table: str, col_names: set[str]
) -> list[str]:
    """Stable key: primary key -> unique index -> identity -> [] (digest-only)."""
    # Primary key columns, in key order.
    cur.execute(
        """
        SELECT col.name
        FROM sys.key_constraints kc
        JOIN sys.tables t ON t.object_id = kc.parent_object_id
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        JOIN sys.index_columns ic
          ON ic.object_id = kc.parent_object_id AND ic.index_id = kc.unique_index_id
        JOIN sys.columns col
          ON col.object_id = ic.object_id AND col.column_id = ic.column_id
        WHERE kc.type = 'PK' AND s.name = ? AND t.name = ?
        ORDER BY ic.key_ordinal;
        """,
        [schema, table],
    )
    pk = [r[0] for r in cur.fetchall() if r[0] in col_names]
    if pk:
        return pk

    # First unique (non-PK) index, in key order.
    cur.execute(
        """
        SELECT TOP 1 i.index_id
        FROM sys.indexes i
        JOIN sys.tables t ON t.object_id = i.object_id
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        WHERE i.is_unique = 1 AND i.is_primary_key = 0 AND i.type IN (1, 2)
          AND s.name = ? AND t.name = ?
        ORDER BY i.index_id;
        """,
        [schema, table],
    )
    row = cur.fetchone()
    if row is not None:
        idx_id = int(row[0])
        cur.execute(
            """
            SELECT col.name
            FROM sys.index_columns ic
            JOIN sys.columns col
              ON col.object_id = ic.object_id AND col.column_id = ic.column_id
            JOIN sys.tables t ON t.object_id = ic.object_id
            JOIN sys.schemas s ON s.schema_id = t.schema_id
            WHERE ic.object_id = OBJECT_ID(? + '.' + ?) AND ic.index_id = ?
              AND ic.is_included_column = 0
            ORDER BY ic.key_ordinal;
            """,
            [schema, table, idx_id],
        )
        uq = [r[0] for r in cur.fetchall() if r[0] in col_names]
        if uq:
            return uq

    # Identity column.
    cur.execute(
        """
        SELECT col.name
        FROM sys.identity_columns col
        JOIN sys.tables t ON t.object_id = col.object_id
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        WHERE s.name = ? AND t.name = ?;
        """,
        [schema, table],
    )
    ident = [r[0] for r in cur.fetchall() if r[0] in col_names]
    if ident:
        return ident

    return []


def capture_cells(
    container: str,
    password: str,
    db_name: str,
    out_dir: Path,
    *,
    user: str = "sa",
    sample_threshold: int = 1_000_000,
    sample_n: int = 200_000,
    digest_values_cap: int = 100_000,
    key_overrides: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Write the ``.cells/`` sidecar for the restored *db_name*; return the manifest."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    key_overrides = key_overrides or {}
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = fixture_utils.connect(container, user, password)
    cur = conn.cursor()
    cur.execute(f"USE [{db_name}];")

    cur.execute(
        """
        SELECT s.name, t.name
        FROM sys.tables t
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        WHERE t.is_ms_shipped = 0
          AND t.is_memory_optimized = 0
        ORDER BY s.name, t.name;
        """
    )
    table_list = [(r[0], r[1]) for r in cur.fetchall()]

    tables_out: list[dict[str, Any]] = []
    for schema, table in table_list:
        fqn = f"{schema}.{table}"
        cols = _columns(cur, schema, table)
        if not cols:
            continue
        col_names = [c["name"] for c in cols]
        sql_types = {c["name"]: c["sql_type"] for c in cols}
        canon_types = {c["name"]: c.get("base_sql_type", c["sql_type"]) for c in cols}

        cur.execute(f"SELECT COUNT_BIG(*) FROM [{schema}].[{table}];")
        rc_row = cur.fetchone()
        row_count = int(rc_row[0]) if rc_row is not None else 0
        if row_count == 0:
            continue  # mssqlbak skips empty tables — nothing to verify

        key_cols = key_overrides.get(fqn) or _resolve_key(cur, schema, table, set(col_names))
        mode = "digest-only" if not key_cols else ("full" if row_count <= sample_threshold else "sample")

        select_cols = ", ".join(_select_expr(c, canon_types[c]) for c in col_names)
        # ORDER BY references the raw columns (not the projected text) so a
        # CLR UDT key (e.g. hierarchyid) still sorts in native engine order.
        order = f" ORDER BY {', '.join(f'[{c}]' for c in key_cols)}" if key_cols else ""
        cur.execute(f"SELECT {select_cols} FROM [{schema}].[{table}]{order};")

        # Canonicalize column-wise over ALL rows (digest covers the full column).
        canon_cols: dict[str, list[str | None]] = {c: [] for c in col_names}
        null_counts: dict[str, int] = {c: 0 for c in col_names}
        for row in cur.fetchall():
            for ci, cname in enumerate(col_names):
                v = row[ci]
                cv = canon(v, canon_types[cname])
                canon_cols[cname].append(cv)
                if cv is None:
                    null_counts[cname] += 1

        columns_meta = []
        for c in col_names:
            meta = {
                "name": c,
                "sql_type": sql_types[c],
                "digest": column_digest(canon_cols[c]),
                "null_count": null_counts[c],
            }
            if canon_types[c] != sql_types[c]:
                meta["base_sql_type"] = canon_types[c]
            columns_meta.append(meta)

        entry: dict[str, Any] = {
            "fqn": fqn,
            "row_count": row_count,
            "key_columns": key_cols,
            "mode": mode,
            "columns": columns_meta,
        }

        if mode in ("full", "sample"):
            if mode == "sample":
                step = max(1, math.ceil(row_count / sample_n))
                idx = list(range(0, row_count, step))
                entry["sample_n"] = len(idx)
            else:
                idx = list(range(row_count))
            table_data = {
                c: pa.array([canon_cols[c][i] for i in idx], pa.string()) for c in col_names
            }
            pq.write_table(pa.table(table_data), out_dir / f"{fqn}.parquet")
        elif mode == "digest-only":
            # Keyless tables have no stable row order, so we cannot store
            # row-aligned cells. Instead persist each column's binary-sorted
            # non-null canonical values — the exact set that column_digest()
            # hashes — so a digest mismatch is diagnosable offline via a
            # per-column set diff (which values the decoder got wrong) without
            # a fresh SQL Server restore. Independent per-column sort is
            # deterministic, so the parquet does not churn across recaptures.
            sorted_cols = {
                c: sorted(v for v in canon_cols[c] if v is not None)[:digest_values_cap]
                for c in col_names
            }
            max_len = max((len(v) for v in sorted_cols.values()), default=0)
            if max_len > 0:
                table_data = {
                    c: pa.array(
                        sorted_cols[c] + [None] * (max_len - len(sorted_cols[c])),
                        pa.string(),
                    )
                    for c in col_names
                }
                pq.write_table(pa.table(table_data), out_dir / f"{fqn}.parquet")
                entry["values_sorted"] = True
                if any(len(sorted_cols[c]) >= digest_values_cap for c in col_names):
                    entry["values_capped"] = digest_values_cap

        tables_out.append(entry)
        print(f"  cells: {fqn} [{mode}] {row_count} rows, key={key_cols or '-'}", file=sys.stderr)

    conn.close()

    # Stable write: reuse the prior captured_at when the canonical content
    # (per-table digests/keys/modes) is unchanged, so committed manifests do not
    # churn on the volatile timestamp. The parquet output is deterministic for a
    # given canon + pyarrow version, so it stays byte-identical on its own.
    captured_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    mpath = out_dir / MANIFEST_NAME
    if mpath.exists():
        try:
            old = json.loads(mpath.read_text())
            if old.get("tables") == tables_out:
                captured_at = old.get("captured_at", captured_at)
        except (json.JSONDecodeError, OSError):
            pass

    manifest = {
        "bak": out_dir.name.removesuffix(".cells"),
        "captured_at": captured_at,
        "tables": tables_out,
    }
    mpath.write_text(json.dumps(manifest, indent=2))
    print(f"==> wrote {out_dir}/ ({len(tables_out)} tables)", file=sys.stderr)
    return manifest
