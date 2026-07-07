#!/usr/bin/env python3
"""Build a type-coverage BACPAC fixture from a live SQL Server container.

Reuses the TypeCoverage database created by ``tools/make_fixture.py`` (same
schema and data) but exports the result as a BACPAC archive rather than a
``.bak`` file.  BACPAC = ZIP + ``model.xml`` (DACPAC schema) + one
``Data/<Schema>.<Table>/TableData-000-00000.BCP`` file per table in SQL Server
BCP native format.

The ``bcp`` utility inside the container exports each table.  Tables whose
type cannot be exported in native format (``sql_variant``, and deprecated
``text``/``ntext``/``image`` which BCP does not export via ``-n``) are omitted
from the BCP data but still appear in ``model.xml`` — matching real BACPAC
behaviour (Azure SQL simply writes no BCP files for empty-or-unsupported
tables).

Usage::

    python -m tools.make_bacpac_fixture
    # or supply credentials explicitly:
    FIXTURE_DBA_PASSWORD=YourPass python tools/make_bacpac_fixture.py

The BACPAC is written to ``tests/fixtures/typecoverage.bacpac``.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import Any

# Put repo root first so the script works both as __main__ and as a module.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_fixture import (  # noqa: E402
    DB_NAME,
    build_sql,
    discover_container,
    sqlcmd_base,
)

# --------------------------------------------------------------------------- #
# Paths                                                                         #
# --------------------------------------------------------------------------- #

FIXTURES_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).resolve().parent.parent / "tests" / "fixtures")))
OUT_PATH = FIXTURES_DIR / "typecoverage.bacpac"

# --------------------------------------------------------------------------- #
# BCP export                                                                    #
# --------------------------------------------------------------------------- #

# Types that bcp -n cannot export in a BACPAC-compatible native stream.
# They still appear in model.xml but get no BCP file (zero rows in BACPAC).
_BCP_UNSUPPORTED = frozenset({"sql_variant", "text", "ntext", "image"})


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def _bcp_export(
    container: str,
    password: str,
    db: str,
    schema: str,
    table: str,
    container_out: str,
) -> bool:
    """Export *schema.table* from *db* to *container_out* using bcp -n.

    Returns True on success, False if bcp reports an error (unsupported type
    or empty table).
    """
    from tools.make_fixture import discover_sqlcmd_path
    bcp_cmd = [
        discover_sqlcmd_path(container, binary="bcp"),
        f"{db}.{schema}.{table}",
        "out", container_out,
        "-n",                      # native format
        "-S", "localhost",
        "-U", "sa",
        "-P", password,
        "-u",                      # trust server certificate (self-signed)
        "-b", "10000",             # batch size
    ]
    proc = _run(["podman", "exec", container, *bcp_cmd])
    if proc.returncode != 0 or "Error" in proc.stdout:
        return False
    # bcp writes "N rows copied." — treat 0 rows as success (empty BCP file).
    return True


# --------------------------------------------------------------------------- #
# model.xml generation                                                          #
# --------------------------------------------------------------------------- #

_NS = "http://schemas.microsoft.com/sqlserver/dac/Serialization/2012/02"
_DSP = "Microsoft.Data.Tools.Schema.Sql.Sql160DatabaseSchemaProvider"

# System-namespace types that appear as [sys].[name] in DACPAC References.
_SYS_TYPES = frozenset({"geography", "geometry", "hierarchyid"})


def _dacpac_type_ref(type_name: str) -> str:
    if type_name in _SYS_TYPES:
        return f"[sys].[{type_name}]"
    # rowversion is stored as 'timestamp' in sys.types
    if type_name == "timestamp":
        return "[rowversion]"
    return f"[{type_name}]"


def _has_length(type_name: str) -> bool:
    return type_name in {
        "char", "nchar", "varchar", "nvarchar", "binary", "varbinary",
        "text", "ntext", "image",
    }


def _has_precision(type_name: str) -> bool:
    return type_name in {"decimal", "numeric"}


def _has_datetime_scale(type_name: str) -> bool:
    return type_name in {"datetime2", "time", "datetimeoffset"}


def _indent(text: str, n: int) -> str:
    return textwrap.indent(text, "\t" * n)


def _col_xml(
    schema: str,
    table: str,
    col_name: str,
    is_nullable: bool,
    type_name: str,
    max_length: int,
    precision: int,
    scale: int,
) -> str:
    """Return the XML fragment for one SqlSimpleColumn."""
    nullable_val = "True" if is_nullable else "False"
    type_ref = _dacpac_type_ref(type_name)

    type_props: list[str] = []

    if _has_length(type_name) and max_length != -1:
        # nchar/nvarchar: max_length is bytes, DACPAC Length is char count
        char_len = max_length // 2 if type_name in ("nchar", "nvarchar") else max_length
        type_props.append(f'<Property Name="Length" Value="{char_len}" />')
    elif _has_precision(type_name):
        type_props.append(f'<Property Name="Precision" Value="{precision}" />')
        type_props.append(f'<Property Name="Scale" Value="{scale}" />')
    elif _has_datetime_scale(type_name):
        type_props.append(f'<Property Name="Scale" Value="{scale}" />')

    type_props_str = "\n".join(type_props)
    if type_props_str:
        type_props_xml = _indent(type_props_str + "\n", 7)
    else:
        type_props_xml = ""

    return f"""\
\t\t\t\t<Entry>
\t\t\t\t\t<Element Type="SqlSimpleColumn" Name="[{schema}].[{table}].[{col_name}]">
\t\t\t\t\t\t<Property Name="IsNullable" Value="{nullable_val}" />
\t\t\t\t\t\t<Relationship Name="TypeSpecifier">
\t\t\t\t\t\t\t<Entry>
\t\t\t\t\t\t\t\t<Element Type="SqlTypeSpecifier">
{type_props_xml}\t\t\t\t\t\t\t\t\t<Relationship Name="Type">
\t\t\t\t\t\t\t\t\t\t<Entry>
\t\t\t\t\t\t\t\t\t\t\t<References ExternalSource="BuiltIns" Name="{type_ref}" />
\t\t\t\t\t\t\t\t\t\t</Entry>
\t\t\t\t\t\t\t\t\t</Relationship>
\t\t\t\t\t\t\t\t</Element>
\t\t\t\t\t\t\t</Entry>
\t\t\t\t\t\t</Relationship>
\t\t\t\t\t</Element>
\t\t\t\t</Entry>"""


def _table_xml(
    schema: str,
    table: str,
    columns: list[dict[str, Any]],
) -> str:
    """Return the XML fragment for one SqlTable."""
    col_entries = "\n".join(
        _col_xml(
            schema, table,
            c["col_name"],
            bool(c["is_nullable"]),
            c["type_name"],
            c["max_length"],
            c["precision"],
            c["scale"],
        )
        for c in columns
    )
    return f"""\
\t\t<Element Type="SqlTable" Name="[{schema}].[{table}]">
\t\t\t<Property Name="IsAnsiNullsOn" Value="True" />
\t\t\t<Relationship Name="Columns">
{col_entries}
\t\t\t</Relationship>
\t\t</Element>"""


def build_model_xml(schema_rows: list[dict[str, Any]]) -> bytes:
    """Build a minimal DACPAC ``model.xml`` from *schema_rows*."""
    from itertools import groupby

    # Group by (schema, table)
    table_xmls: list[str] = []
    schemas_seen: set[str] = set()
    schema_xml_parts: list[str] = []

    schema_sorted = sorted(schema_rows, key=lambda r: (r["schema_name"], r["table_name"], r["column_id"]))
    for (sch, tbl), cols in groupby(schema_sorted, key=lambda r: (r["schema_name"], r["table_name"])):
        if sch not in schemas_seen:
            schemas_seen.add(sch)
            schema_xml_parts.append(f"""\
\t\t<Element Type="SqlSchema" Name="[{sch}]">
\t\t\t<Relationship Name="Authorizer">
\t\t\t\t<Entry>
\t\t\t\t\t<References ExternalSource="BuiltIns" Name="[dbo]" />
\t\t\t\t</Entry>
\t\t\t</Relationship>
\t\t</Element>""")
        table_xmls.append(_table_xml(sch, tbl, list(cols)))

    all_elements = "\n".join(schema_xml_parts + table_xmls)
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<DataSchemaModel FileFormatVersion="1.2" SchemaVersion="2.9" '
        f'DspName="{_DSP}" CollationLcid="1033" CollationCaseSensitive="False" '
        f'xmlns="{_NS}">\n'
        f'\t<Model>\n'
        f'{all_elements}\n'
        f'\t</Model>\n'
        f'</DataSchemaModel>\n'
    )
    return xml.encode("utf-8")


# --------------------------------------------------------------------------- #
# Schema query                                                                  #
# --------------------------------------------------------------------------- #

_SCHEMA_SQL = """\
USE [{db}];
SELECT
    s.name AS schema_name,
    t.name AS table_name,
    c.name AS col_name,
    c.column_id,
    CAST(c.is_nullable AS int) AS is_nullable,
    ty.name AS type_name,
    CAST(c.max_length AS int) AS max_length,
    CAST(c.precision AS int) AS precision,
    CAST(c.scale AS int) AS scale
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.columns c ON t.object_id = c.object_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
WHERE t.is_ms_shipped = 0
ORDER BY s.name, t.name, c.column_id;
"""

_SEP = "\t"


def _query_schema(container: str, sqlcmd: list[str], db: str) -> list[dict[str, Any]]:
    """Return one dict per column in the TypeCoverage database."""
    sql = _SCHEMA_SQL.format(db=db)

    # Write SQL to container then execute.
    tmp_sql = f"/tmp/schema_query_{db}.sql"
    proc = _run(["podman", "exec", "-i", container, "tee", tmp_sql], input=sql)
    if proc.returncode != 0:
        raise RuntimeError(f"failed to write schema SQL: {proc.stderr}")

    proc = _run(["podman", "exec", container, *sqlcmd, "-i", tmp_sql, "-s", "\t", "-W", "-h", "-1"])
    if proc.returncode != 0:
        raise RuntimeError(f"schema query failed:\n{proc.stdout}\n{proc.stderr}")

    rows: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(_SEP)
        if len(parts) < 9:
            continue
        try:
            rows.append({
                "schema_name": parts[0],
                "table_name":  parts[1],
                "col_name":    parts[2],
                "column_id":   int(parts[3]),
                "is_nullable": int(parts[4]),
                "type_name":   parts[5],
                "max_length":  int(parts[6]),
                "precision":   int(parts[7]),
                "scale":       int(parts[8]),
            })
        except (ValueError, IndexError):
            continue
    return rows


# --------------------------------------------------------------------------- #
# BACPAC ZIP assembly                                                           #
# --------------------------------------------------------------------------- #

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="xml" ContentType="text/xml" />'
    '<Default Extension="BCP" ContentType="application/octet-stream" />'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
    '</Types>'
)

_DAC_METADATA = """\
<?xml version="1.0" encoding="utf-8"?>
<DacType xmlns="http://schemas.microsoft.com/sqlserver/dac/Serialization/2012/02">
  <Name>TypeCoverage</Name>
  <Version>0.0.0.0</Version>
</DacType>
"""

_ORIGIN = """\
<?xml version="1.0" encoding="utf-8"?>
<DacOrigin xmlns="http://schemas.microsoft.com/sqlserver/dac/Serialization/2012/02">
  <PackageProperties>
    <Version>3.1.0.0</Version>
    <ContainsExportedData>true</ContainsExportedData>
    <StreamVersions>
      <Version StreamName="Data">2.0.0.0</Version>
    </StreamVersions>
  </PackageProperties>
</DacOrigin>
"""

_RELS = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '</Relationships>'
)


def build_bacpac(
    model_xml: bytes,
    bcp_files: dict[str, bytes],  # zip_entry_path → bcp_bytes
) -> bytes:
    """Assemble and return a BACPAC archive as bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("model.xml", model_xml)
        zf.writestr("DacMetadata.xml", _DAC_METADATA.encode("utf-8"))
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES.encode("utf-8"))
        zf.writestr("_rels/.rels", _RELS.encode("utf-8"))
        zf.writestr("Origin.xml", _ORIGIN.encode("utf-8"))
        for entry_path, data in sorted(bcp_files.items()):
            zf.writestr(entry_path, data)
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# Main                                                                          #
# --------------------------------------------------------------------------- #

def main() -> int:
    password = os.environ.get("FIXTURE_DBA_PASSWORD", "")
    if not password:
        print("error: set FIXTURE_DBA_PASSWORD", file=sys.stderr)
        return 1

    container = discover_container()
    print(f"container: {container}")

    sqlcmd = sqlcmd_base("sa", password, container)

    # ── 1. Create / refresh the TypeCoverage database ─────────────────────
    print("creating TypeCoverage database …")
    # build_sql() returns DDL + DML + BACKUP DATABASE; strip the backup statement.
    full_sql = build_sql()
    # The backup statement starts at the last BACKUP keyword; trim it.
    backup_idx = full_sql.upper().rfind("\nBACKUP DATABASE")
    setup_sql = full_sql[:backup_idx] if backup_idx != -1 else full_sql

    tmp_sql = f"/tmp/setup_{DB_NAME}.sql"
    proc = subprocess.run(
        ["podman", "exec", "-i", container, "tee", tmp_sql],
        input=setup_sql, text=True, capture_output=True,
    )
    if proc.returncode != 0:
        print(f"error writing setup SQL: {proc.stderr}", file=sys.stderr)
        return 1

    proc = subprocess.run(
        ["podman", "exec", container, *sqlcmd, "-i", tmp_sql],
        text=True, capture_output=True,
    )
    if proc.returncode != 0:
        print(f"error setting up database:\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
        return 1
    print("database ready")

    # ── 2. Query schema ───────────────────────────────────────────────────
    print("querying schema …")
    schema_rows = _query_schema(container, sqlcmd, DB_NAME)
    if not schema_rows:
        print("error: schema query returned no rows", file=sys.stderr)
        return 1
    print(f"  {len(schema_rows)} columns across {len({r['table_name'] for r in schema_rows})} tables")

    # ── 3. Export BCP data for each table ────────────────────────────────
    tables = sorted({(r["schema_name"], r["table_name"]) for r in schema_rows})
    bcp_files: dict[str, bytes] = {}

    # Check which tables have types bcp -n cannot export
    table_types: dict[tuple[str, str], set[str]] = {}
    for r in schema_rows:
        key = (r["schema_name"], r["table_name"])
        table_types.setdefault(key, set()).add(r["type_name"])

    for schema, table in tables:
        tbl_types = table_types.get((schema, table), set())
        if tbl_types & _BCP_UNSUPPORTED:
            print(f"  skip bcp {schema}.{table} (unsupported types: {tbl_types & _BCP_UNSUPPORTED})")
            continue

        container_bcp = f"/tmp/{DB_NAME}_{schema}_{table}.bcp"
        ok = _bcp_export(container, password, DB_NAME, schema, table, container_bcp)
        if not ok:
            print(f"  warn: bcp failed for {schema}.{table}; skipping BCP data")
            continue

        # Copy BCP file out of container (into fixtures dir — sandbox allows writes there)
        local_bcp = FIXTURES_DIR / "_fixture_bcp_tmp.bcp"
        proc = subprocess.run(
            ["podman", "cp", f"{container}:{container_bcp}", str(local_bcp)],
            capture_output=True,
        )
        if proc.returncode != 0:
            print(f"  warn: podman cp failed for {schema}.{table}; skipping")
            continue

        data = local_bcp.read_bytes()
        try:
            local_bcp.unlink(missing_ok=True)
        except OSError:
            pass
        if not data:
            print(f"  skip {schema}.{table} (empty BCP output)")
            continue

        zip_entry = f"Data/{schema}.{table}/TableData-000-00000.BCP"
        bcp_files[zip_entry] = data
        print(f"  exported {schema}.{table}: {len(data):,} bytes")

    # ── 4. Build model.xml ────────────────────────────────────────────────
    print("building model.xml …")
    model_xml = build_model_xml(schema_rows)

    # ── 5. Assemble and write BACPAC ──────────────────────────────────────
    print("assembling BACPAC …")
    bacpac_bytes = build_bacpac(model_xml, bcp_files)
    OUT_PATH.write_bytes(bacpac_bytes)
    print(f"written: {OUT_PATH}  ({len(bacpac_bytes):,} bytes)")
    print(f"  {len(bcp_files)} tables with BCP data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
