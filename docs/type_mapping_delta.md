# Type & value conversion: SQL Server -> Delta

How the `.bak` -> Delta extractor maps every supported SQL Server type to a
Delta column type, and any change in value representation along the way.
**Generated** by `python -m tools.type_mapping`: the *Arrow type* and *Delta
type* columns come straight from `mssqlbak.types.arrow_type` and `deltalake`'s
Arrow->Delta conversion (so they match what is actually written);
`tests/test_type_mapping.py` fails if this file is out of date.

Not every SQL Server type has a native Delta equivalent. Where Delta has no
matching type the value is converted to a lossless string or binary form
(noted below). Sub-microsecond precision is the only value-narrowing case
(Python/Arrow resolve to microseconds; SQL Server stores 100 ns ticks).

| SQL Server type | xtype | Arrow type | Delta type | Value rule |
|-----------------|-------|------------|------------|------------|
| bit | 104 | `int8` | `byte` | bit -> bool. |
| tinyint | 48 | `int16` | `short` | unsigned 0..255 widened to signed int16 (Delta has no uint8); value preserved. |
| smallint | 52 | `int16` | `short` | verbatim. |
| int | 56 | `int32` | `integer` | verbatim. |
| bigint | 127 | `int64` | `long` | verbatim. |
| decimal | 106 | `decimal128(38, 10)` | `decimal(38,10)` | verbatim; precision/scale preserved as decimal128. |
| numeric | 108 | `decimal128(18, 4)` | `decimal(18,4)` | verbatim; precision/scale preserved as decimal128. |
| smallmoney | 122 | `decimal128(10, 4)` | `decimal(10,4)` | scaled integer (1e-4 units) -> decimal(10,4). |
| money | 60 | `decimal128(19, 4)` | `decimal(19,4)` | scaled integer (1e-4 units) -> decimal(19,4). |
| real | 59 | `float` | `float` | IEEE-754 float32, verbatim. |
| float | 62 | `double` | `double` | IEEE-754 float64, verbatim. |
| date | 40 | `date32[day]` | `date` | verbatim (date32). |
| time | 41 | `string` | `string` | no Delta time-of-day type -> ISO string `HH:MM:SS[.ffffff]`; 100ns ticks floored to microseconds. |
| smalldatetime | 58 | `timestamp[us]` | `timestamp_ntz` | -> timestamp(us), no time zone. |
| datetime | 61 | `timestamp[us]` | `timestamp_ntz` | -> timestamp(us), no time zone. |
| datetime2 | 42 | `timestamp[us]` | `timestamp_ntz` | -> timestamp(us); 100ns ticks floored to microseconds. |
| datetimeoffset | 43 | `timestamp[us, tz=UTC]` | `timestamp` | instant -> timestamp(us) normalized to UTC; 100ns floored to microseconds; original zone offset not retained. |
| char | 175 | `string` | `string` | fixed-width; trailing space padding preserved -> string. |
| varchar / varchar(max) | 167 | `string` | `string` | single-byte code page decoded -> string. |
| text | 35 | `string` | `string` | off-row LOB stitched -> string. |
| nchar | 239 | `string` | `string` | UTF-16; trailing space padding preserved -> string. |
| nvarchar / nvarchar(max) | 231 | `string` | `string` | UTF-16 -> string. |
| ntext | 99 | `string` | `string` | off-row LOB stitched -> string. |
| binary | 173 | `binary` | `binary` | fixed-width; trailing zero padding preserved -> binary. |
| varbinary / varbinary(max) | 165 | `binary` | `binary` | LOB / row-overflow stitched to full size -> binary. |
| image | 34 | `binary` | `binary` | off-row LOB stitched -> binary. |
| uniqueidentifier | 36 | `string` | `string` | -> canonical UUID string (e.g. `3f2504e0-...`). |
| rowversion / timestamp | 189 | `binary` | `binary` | 8 opaque engine-assigned bytes -> binary. |
| xml | 241 | `string` | `string` | tokenised binary-XML re-serialised to XML text -> string. |
| sql_variant | 98 | `string` | `string` | decoded to its stored base-type Python value, then rendered to a string (bytes as hex). |
| hierarchyid / geometry / geography | 240 | `string` | `string` | CLR UDT (by user_type_id): geometry/geography -> OGC WKT string; hierarchyid -> canonical path string. |

## Column names and identifiers

Column and table names are written **verbatim** — the SQL Server column name
becomes the Delta field name unchanged (`mssqlbak.types.arrow_schema_for`),
and each table is written to `out/<schema>/<table>`. There is currently **no**
name sanitisation, renaming, or Delta column-mapping mode: a source column
whose name contains characters Delta/Parquet disallow (spaces or any of
`` ,;{}()\n\t= ``) is passed through as-is rather than remapped.

## Length and nullability

- Declared lengths (`varchar(50)`, `binary(8)`, ...) are **not** enforced or
  recorded on the Delta side: Delta `string`/`binary` are unbounded. Fixed-width
  `char(n)`/`nchar(n)`/`binary(n)` padding is preserved as stored.
- Column nullability is carried through to the Delta field.

## Unsupported types

A type with no decoder raises `NotImplementedError` on extract (fail-loud, no
silent corruption). See [TYPE_COVERAGE.md](TYPE_COVERAGE.md) for the supported
set. None of the above is parameterised today; the mapping and value rules are
fixed in code.

See [README](../README.md) and [TYPE_COVERAGE.md](TYPE_COVERAGE.md).
