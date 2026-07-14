#!/usr/bin/env python3
"""Dump all sysxprops rows from a .bak fixture.

sysxprops (object_id=49) is the internal base table that backs
sys.extended_properties.  Its columns are:
  class (tinyint), id (int), subid (int), name (nvarchar), value (sql_variant)

Usage:
    .venv/bin/python tools/diag/dump_sysxprops.py
    .venv/bin/python tools/diag/dump_sysxprops.py --fixture tests/fixtures_2022/extended_properties_full.bak
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, open_store, hexdump, REPO_ROOT  # noqa: E402

sys.path.insert(0, str(REPO_ROOT))

from mssqlbak.catalog.columns import _layout, _PARTITION_SHIFT  # noqa: E402
from mssqlbak.catalog.bootstrap import _bootstrap, _decode_table  # noqa: E402
from mssqlbak.catalog.lob import _follow_lob                       # noqa: E402
from mssqlbak.catalog.columns import _u as _col_u                 # noqa: E402

_OBJID_SYSXPROPS = 49

# sysxprops column layout — based on sys.all_columns query:
#   class(tinyint) id(int) subid(int) name(nvarchar=sysname) value(sql_variant=varbinary)
# sql_variant is stored on disk as a varbinary blob with a type header.
_SYSXPROPS_COLS = _layout(
    [
        ("class",  "tinyint"),   # extended-property class: 1=OBJECT_OR_COLUMN, 3=SCHEMA
        ("id",     "int"),       # major_id (object_id or schema_id)
        ("subid",  "int"),       # minor_id (colid for column-level, 0 for object-level)
        ("name",   "sysname"),   # property name (nvarchar128 stored as variable-length)
        ("value",  "varbinary"), # sql_variant stored as raw bytes
    ]
)


_CLASS_DESC = {
    0: "DATABASE",
    1: "OBJECT_OR_COLUMN",
    2: "PARAMETER",
    3: "SCHEMA",
    4: "DATABASE_USER",
    5: "ROLE",
    6: "VARBINARY_USER_DEFINED_TYPE",
    7: "ROLE_MEMBER",
    10: "TYPE",
    11: "INDEX",
    12: "XML_SCHEMA_COLLECTION",
    13: "MESSAGE_TYPE",
    14: "SERVICE_CONTRACT",
    15: "SERVICE",
    16: "REMOTE_SERVICE_BINDING",
    17: "ROUTE",
    18: "DATASPACE",
    19: "PARTITION_FUNCTION",
    20: "DATABASE_PRINCIPAL",
    21: "SYNONYM",
    22: "SEQUENCE_OBJECT",
}


def _decode_sql_variant(data: bytes) -> str:
    """Attempt to decode a sql_variant blob to a display string."""
    if not data:
        return "<NULL>"
    if len(data) < 2:
        return f"<too-short: {data.hex()}>"
    # sql_variant layout: type_tag(1 byte) + metadata + value
    # Common text type: 231 = nvarchar, 167 = varchar
    # First byte is the SQL Server system type id
    type_id = data[0]
    # For nvarchar (231): 1-byte typeid + 5-byte metadata (collation info + max_len) + nvarchar bytes
    if type_id == 231:  # nvarchar
        # metadata is 5 bytes: 4-byte collation + 2-byte max_len
        if len(data) >= 7:
            payload = data[7:]
            try:
                return repr(payload.decode("utf-16-le"))
            except Exception:  # noqa: BLE001
                pass
    # For varchar (167) or char (175): 1-byte typeid + 5-byte metadata + bytes
    if type_id in (167, 175):  # varchar / char
        if len(data) >= 7:
            payload = data[7:]
            try:
                return repr(payload.decode("cp1252"))
            except Exception:  # noqa: BLE001
                pass
    # Generic fallback: hex + try text
    hex_str = data[:48].hex(" ")
    try:
        txt = data[1:].decode("utf-16-le")
        if all(32 <= ord(c) < 0x10000 for c in txt[:40]):
            return f"type={type_id} text={repr(txt[:40])}"
    except Exception:  # noqa: BLE001
        pass
    return f"type={type_id} hex={hex_str}"


def _decode_name(data: bytes | None) -> str:
    """Decode a sysname (nvarchar) stored as raw bytes."""
    if not data:
        return "<empty>"
    try:
        return data.decode("utf-16-le")
    except Exception:  # noqa: BLE001
        try:
            return data.decode("latin-1")
        except Exception:  # noqa: BLE001
            return data.hex()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", default=None,
                    help="path to .bak fixture (default: extended_properties_full.bak)")
    ap.add_argument("--hex-limit", type=int, default=64)
    ap.add_argument("--all-hex", action="store_true", help="show full hex of value column")
    args = ap.parse_args()

    if args.fixture:
        p = Path(args.fixture)
        if not p.is_absolute():
            p = REPO_ROOT / p
    else:
        p = fixture("2022", "extended_properties_full.bak")

    if not p.exists():
        sys.exit(f"fixture not found: {p}")

    store, _schema, boot_obj, _blobs = open_store(p)
    boot = _bootstrap(store)

    # Find sysxprops page using the same method as other system tables
    try:
        rowset_id = _OBJID_SYSXPROPS << _PARTITION_SHIFT
        from mssqlbak.catalog.bootstrap import _find_first_page
        pg = _find_first_page(store, rowset_id)
    except Exception as exc:  # noqa: BLE001
        # Fall back to object_table_first_page
        try:
            pg = boot.object_table_first_page(_OBJID_SYSXPROPS)
        except Exception as exc2:  # noqa: BLE001
            sys.exit(f"cannot find sysxprops page: {exc}; {exc2}")

    try:
        rows = _decode_table(store, pg, _SYSXPROPS_COLS)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"cannot decode sysxprops table: {exc}")

    total = 0
    for r in rows:
        total += 1
        cls = int.from_bytes(bytes(r.get("class") or b"\x00"), "little")
        obj_id = int.from_bytes(bytes(r.get("id") or b"\x00\x00\x00\x00"), "little", signed=True)
        subid = int.from_bytes(bytes(r.get("subid") or b"\x00\x00\x00\x00"), "little", signed=True)

        name_raw = r.get("name")
        name_bytes = b""
        if name_raw:
            try:
                name_bytes = _follow_lob(store, name_raw)
            except Exception:  # noqa: BLE001
                name_bytes = bytes(name_raw) if isinstance(name_raw, (bytes, bytearray)) else b""
        name_str = _decode_name(name_bytes)

        value_raw = r.get("value")
        value_bytes = b""
        if value_raw:
            try:
                value_bytes = _follow_lob(store, value_raw)
            except Exception:  # noqa: BLE001
                value_bytes = bytes(value_raw) if isinstance(value_raw, (bytes, bytearray)) else b""
        value_str = _decode_sql_variant(value_bytes)

        cls_name = _CLASS_DESC.get(cls, f"?({cls})")
        print(f"\n{'='*72}")
        print(f"  class={cls} ({cls_name})  id={obj_id}  subid={subid}")
        print(f"  name: {repr(name_str)}")
        if args.all_hex:
            print(f"  value raw ({len(value_bytes)} bytes): {value_bytes.hex(' ')}")
        else:
            print(f"  value raw ({len(value_bytes)} bytes): {value_bytes[:args.hex_limit].hex(' ')}")
        print(f"  value decoded: {value_str}")

    print(f"\n{'='*72}")
    print(f"Total rows in sysxprops: {total}")


if __name__ == "__main__":
    main()
