#!/usr/bin/env python3
"""Generate ``docs/type_mapping_delta.md`` — how each SQL Server type is converted.

The **SQL type -> Arrow type -> Delta type** columns are derived from code:
``mssqlbak.types.arrow_type`` for the Arrow type and ``deltalake``'s own
Arrow->Delta conversion for the Delta type. They therefore cannot drift from
what the extractor actually writes. The **value rule** column is a curated note
(kept in :data:`VALUE_RULES`) describing any representation change applied by
``mssqlbak.extract._coerce`` / the decoder; ``tests/test_type_mapping.py`` fails
if the committed doc is stale, so the notes cannot silently diverge either.

Regenerate:  ``python -m tools.type_mapping``
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pyarrow as pa  # noqa: E402
from deltalake import Schema  # noqa: E402

from mssqlbak.catalog import Column  # noqa: E402
from mssqlbak.types import SUPPORTED_TYPE_IDS, arrow_type  # noqa: E402
from tools.type_coverage import CANONICAL_TYPES  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "type_mapping_delta.md"

# Representative (precision, scale) for the types whose Arrow type depends on
# them; everything else ignores these fields.
_PREC_SCALE: dict[int, tuple[int, int]] = {
    106: (38, 10),  # decimal
    108: (18, 4),   # numeric
}

# Curated value-conversion note per xtype. Describes any representation change
# between the on-disk value and the value written to Delta.
VALUE_RULES: dict[int, str] = {
    104: "bit -> bool.",
    48: "unsigned 0..255 widened to signed int16 (Delta has no uint8); value preserved.",
    52: "verbatim.",
    56: "verbatim.",
    127: "verbatim.",
    106: "verbatim; precision/scale preserved as decimal128.",
    108: "verbatim; precision/scale preserved as decimal128.",
    122: "scaled integer (1e-4 units) -> decimal(10,4).",
    60: "scaled integer (1e-4 units) -> decimal(19,4).",
    59: "IEEE-754 float32, verbatim.",
    62: "IEEE-754 float64, verbatim.",
    40: "verbatim (date32).",
    41: "no Delta time-of-day type -> ISO string `HH:MM:SS[.ffffff]`; 100ns ticks floored to microseconds.",
    58: "-> timestamp(us), no time zone.",
    61: "-> timestamp(us), no time zone.",
    42: "-> timestamp(us); 100ns ticks floored to microseconds.",
    43: "instant -> timestamp(us) normalized to UTC; 100ns floored to microseconds; original zone offset not retained.",
    175: "fixed-width; trailing space padding preserved -> string.",
    167: "single-byte code page decoded -> string.",
    35: "off-row LOB stitched -> string.",
    239: "UTF-16; trailing space padding preserved -> string.",
    231: "UTF-16 -> string.",
    99: "off-row LOB stitched -> string.",
    173: "fixed-width; trailing zero padding preserved -> binary.",
    165: "LOB / row-overflow stitched to full size -> binary.",
    34: "off-row LOB stitched -> binary.",
    36: "-> canonical UUID string (e.g. `3f2504e0-...`).",
    189: "8 opaque engine-assigned bytes -> binary.",
    241: "tokenised binary-XML re-serialised to XML text -> string.",
    98: "decoded to its stored base-type Python value, then rendered to a string (bytes as hex).",
    240: "CLR UDT (by user_type_id): geometry/geography -> OGC WKT string; hierarchyid -> canonical path string.",
    244: "SS2025 native JSON (MSJSONB binary) decoded to compact UTF-8 JSON text -> string.",
}


def _representative_column(xtype: int) -> Column:
    prec, scale = _PREC_SCALE.get(xtype, (0, 0))
    return Column(
        name="v",
        colid=1,
        type_id=xtype,
        max_length=0,
        precision=prec,
        scale=scale,
        nullable=True,
        leaf_offset=0,
        is_variable=False,
    )


def _delta_types(arrow_fields: list[tuple[str, pa.DataType]]) -> dict[str, str]:
    """Map each field name to its Delta type string via deltalake's converter."""
    schema = Schema.from_arrow(pa.schema([(name, t) for name, t in arrow_fields]))
    return {fld.name: fld.type.type for fld in schema.fields}


def build_report() -> str:
    # Several CLR types (hierarchyid / geometry / geography) share xtype 240, so
    # group display names by xtype to emit one row per distinct type id.
    names_by_xtype: dict[int, list[str]] = {}
    for name, xtype, _case in CANONICAL_TYPES:
        names_by_xtype.setdefault(xtype, []).append(name)

    arrow_fields: list[tuple[str, pa.DataType]] = []
    rows: list[tuple[str, int, pa.DataType]] = []
    for xtype, names in names_by_xtype.items():
        if xtype not in SUPPORTED_TYPE_IDS:
            continue
        atype = arrow_type(_representative_column(xtype))
        field_name = f"f{xtype}"
        arrow_fields.append((field_name, atype))
        rows.append((" / ".join(names), xtype, atype))

    delta = _delta_types(arrow_fields)

    lines: list[str] = [
        "# Type & value conversion: SQL Server -> Delta",
        "",
        "How the `.bak` -> Delta extractor maps every supported SQL Server type to a",
        "Delta column type, and any change in value representation along the way.",
        "**Generated** by `python -m tools.type_mapping`: the *Arrow type* and *Delta",
        "type* columns come straight from `mssqlbak.types.arrow_type` and `deltalake`'s",
        "Arrow->Delta conversion (so they match what is actually written);",
        "`tests/test_type_mapping.py` fails if this file is out of date.",
        "",
        "Not every SQL Server type has a native Delta equivalent. Where Delta has no",
        "matching type the value is converted to a lossless string or binary form",
        "(noted below). Sub-microsecond precision is the only value-narrowing case",
        "(Python/Arrow resolve to microseconds; SQL Server stores 100 ns ticks).",
        "",
        "| SQL Server type | xtype | Arrow type | Delta type | Value rule |",
        "|-----------------|-------|------------|------------|------------|",
    ]
    for name, xtype, atype in rows:
        rule = VALUE_RULES.get(xtype, "verbatim.")
        lines.append(f"| {name} | {xtype} | `{atype}` | `{delta[f'f{xtype}']}` | {rule} |")

    lines += [
        "",
        "## Column names and identifiers",
        "",
        "Column and table names are written **verbatim** — the SQL Server column name",
        "becomes the Delta field name unchanged (`mssqlbak.types.arrow_schema_for`),",
        "and each table is written to `out/<schema>/<table>`. There is currently **no**",
        "name sanitisation, renaming, or Delta column-mapping mode: a source column",
        "whose name contains characters Delta/Parquet disallow (spaces or any of",
        "`` ,;{}()\\n\\t= ``) is passed through as-is rather than remapped.",
        "",
        "## Length and nullability",
        "",
        "- Declared lengths (`varchar(50)`, `binary(8)`, ...) are **not** enforced or",
        "  recorded on the Delta side: Delta `string`/`binary` are unbounded. Fixed-width",
        "  `char(n)`/`nchar(n)`/`binary(n)` padding is preserved as stored.",
        "- Column nullability is carried through to the Delta field.",
        "",
        "## Unsupported types",
        "",
        "A type with no decoder raises `NotImplementedError` on extract (fail-loud, no",
        "silent corruption). See [TYPE_COVERAGE.md](TYPE_COVERAGE.md) for the supported",
        "set. None of the above is parameterised today; the mapping and value rules are",
        "fixed in code.",
        "",
        "See [README](../README.md) and [TYPE_COVERAGE.md](TYPE_COVERAGE.md).",
        "",
    ]
    return "\n".join(lines)


def write_report() -> Path:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(build_report())
    return DOC_PATH


def main() -> int:
    path = write_report()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
