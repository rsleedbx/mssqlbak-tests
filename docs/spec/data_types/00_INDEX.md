# SQL Server Data Types — Index

_Part of the [mssqlbak spec suite](../00_MASTER.md). All layouts are little-endian unless noted. Confirmed against `typecoverage_full.bak` (SQL Server 2022) unless stated otherwise._

---

## Overview

SQL Server exposes **41 system data types** via `sys.types` (all rows where `is_user_defined = 0`). Of these:

- **37 are `Supported`** — mssqlbak decodes the on-disk bytes and emits an Arrow value.
- **4 are `Alias`** — they share a wire format (same `system_type_id`) with a Supported type; the parser handles them transparently via `max_length = -1` (MAX variants) or the same xtype (deprecated synonyms).
- **2 are `Not extractable`** — `cursor` and `table` are procedure-only types that never appear in `syscolpars` for a user table column and therefore cannot be extracted; see [`18_non_extractable.md`](18_non_extractable.md).

**Total supported or alias-handled: 39 of 41.**

---

## Status legend

| Status | Meaning |
|---|---|
| `Supported` | Full on-disk decode; Arrow value emitted |
| `Alias` | Same `system_type_id` as a Supported type; handled by the same decoder via `max_length = -1` (LOB MAX variants) or identical xtype (deprecated synonyms) |
| `Not extractable` | Procedure-only type; cannot appear as a user table column |

---

## Full type inventory

| Type | Category | xtype (system_type_id) | user_type_id | Notes | Arrow output | Detail file | Status |
|---|---|---|---|---|---|---|---|
| `tinyint` | Exact numeric | 48 | — | 1-byte unsigned | `pa.int16()` (widened for unsigned range) | [01_integer.md](01_integer.md) | Supported |
| `smallint` | Exact numeric | 52 | — | 2-byte signed | `pa.int16()` | [01_integer.md](01_integer.md) | Supported |
| `int` | Exact numeric | 56 | — | 4-byte signed | `pa.int32()` | [01_integer.md](01_integer.md) | Supported |
| `bigint` | Exact numeric | 127 | — | 8-byte signed | `pa.int64()` | [01_integer.md](01_integer.md) | Supported |
| `bit` | Exact numeric | 104 | — | 1 byte, bit 0; emitted as int8 (not bool) | `pa.int8()` | [01_integer.md](01_integer.md) | Supported |
| `decimal(p,s)` | Exact numeric | 106 | — | sign + LE magnitude | `pa.decimal128(p, s)` | [02_decimal.md](02_decimal.md) | Supported |
| `numeric(p,s)` | Exact numeric | 108 | — | identical wire format to decimal | `pa.decimal128(p, s)` | [02_decimal.md](02_decimal.md) | Supported |
| `money` | Exact numeric | 60 | — | int64 LE × 10⁻⁴ | `pa.decimal128(19, 4)` | [02_decimal.md](02_decimal.md) | Supported |
| `smallmoney` | Exact numeric | 122 | — | int32 LE × 10⁻⁴ | `pa.decimal128(10, 4)` | [02_decimal.md](02_decimal.md) | Supported |
| `float` | Approx numeric | 62 | — | IEEE-754 float64 LE | `pa.float64()` | [03_float.md](03_float.md) | Supported |
| `real` | Approx numeric | 59 | — | IEEE-754 float32 LE | `pa.float32()` | [03_float.md](03_float.md) | Supported |
| `date` | Date/time | 40 | — | 3-byte day count from 0001-01-01 | `pa.date32()` | [04_date.md](04_date.md) | Supported |
| `time(n)` | Date/time | 41 | — | n-scaled ticks, 3–5 bytes | `pa.string()` + field metadata | [05_time.md](05_time.md) | Supported |
| `smalldatetime` | Date/time | 58 | — | uint16 minutes + uint16 days from 1900 | `pa.timestamp("us")` | [06_datetime.md](06_datetime.md) | Supported |
| `datetime` | Date/time | 61 | — | uint32 1/300s ticks + int32 days from 1900 | `pa.timestamp("us")` | [06_datetime.md](06_datetime.md) | Supported |
| `datetime2(n)` | Date/time | 42 | — | n-scaled ticks + 3-byte date, 6–8 bytes | `pa.timestamp("us")` | [07_datetime2.md](07_datetime2.md) | Supported |
| `datetimeoffset(n)` | Date/time | 43 | — | datetime2 + int16 offset minutes | `pa.timestamp("us", tz="UTC")` | [08_datetimeoffset.md](08_datetimeoffset.md) | Supported |
| `char(n)` | Character | 175 | — | n bytes, code page from collation | `pa.string()` | [09_char_varchar.md](09_char_varchar.md) | Supported |
| `varchar(n)` | Character | 167 | — | variable, same encoding as char | `pa.string()` | [09_char_varchar.md](09_char_varchar.md) | Supported |
| `text` | Character | 35 | — | 16-byte LOB pointer; cp1252 content | `pa.string()` | [09_char_varchar.md](09_char_varchar.md) | Supported |
| `varchar(max)` | Character | 167 | — | max_length = -1; same decoder, LOB off-row path | `pa.string()` | [09_char_varchar.md](09_char_varchar.md) | Alias |
| `sysname` | Character | 231 | — | nvarchar(128) alias; max_length = 256; used by system catalogs | `pa.string()` | [10_nchar_nvarchar.md](10_nchar_nvarchar.md) | Alias |
| `nchar(n)` | Unicode | 239 | — | 2n bytes UTF-16-LE | `pa.string()` | [10_nchar_nvarchar.md](10_nchar_nvarchar.md) | Supported |
| `nvarchar(n)` | Unicode | 231 | — | variable UTF-16-LE | `pa.string()` | [10_nchar_nvarchar.md](10_nchar_nvarchar.md) | Supported |
| `ntext` | Unicode | 99 | — | 16-byte LOB pointer; UTF-16-LE content | `pa.string()` | [10_nchar_nvarchar.md](10_nchar_nvarchar.md) | Supported |
| `nvarchar(max)` | Unicode | 231 | — | max_length = -1; same decoder, LOB off-row path | `pa.string()` | [10_nchar_nvarchar.md](10_nchar_nvarchar.md) | Alias |
| `binary(n)` | Binary | 173 | — | n bytes raw | `pa.binary()` | [11_binary.md](11_binary.md) | Supported |
| `varbinary(n)` | Binary | 165 | — | variable raw bytes | `pa.binary()` | [11_binary.md](11_binary.md) | Supported |
| `image` | Binary | 34 | — | 16-byte LOB pointer; raw byte content | `pa.binary()` | [11_binary.md](11_binary.md) | Supported |
| `varbinary(max)` | Binary | 165 | — | max_length = -1; same decoder, LOB off-row path | `pa.binary()` | [11_binary.md](11_binary.md) | Alias |
| `rowversion` | Other | 189 | — | 8 opaque engine-assigned bytes | `pa.binary()` | [11_binary.md](11_binary.md) | Supported |
| `timestamp` | Other | 189 | — | deprecated synonym for rowversion; identical wire format | `pa.binary()` | [11_binary.md](11_binary.md) | Alias |
| `uniqueidentifier` | Other | 36 | — | 16 bytes, mixed-endian UUID | `pa.string()` | [12_uniqueidentifier.md](12_uniqueidentifier.md) | Supported |
| `sql_variant` | Other | 98 | — | base-type dispatch header + value | `pa.string()` | [13_sql_variant.md](13_sql_variant.md) | Supported |
| `xml` | Other | 241 | — | MS-BINXML binary blob → text | `pa.string()` | [14_xml.md](14_xml.md) | Supported |
| `hierarchyid` | Other / CLR UDT | 240 | 128 | ORDPATH binary; rendered as path string | `pa.string()` | [15_clr_udt.md](15_clr_udt.md) | Supported |
| `cursor` | Other | — | — | procedure-only; no user-table xtype | N/A | [18_non_extractable.md](18_non_extractable.md) | Not extractable |
| `table` | Other | — | — | procedure-only variable type | N/A | [18_non_extractable.md](18_non_extractable.md) | Not extractable |
| `geography` | Spatial CLR UDT | 240 | 130 | WKB-like bytes; rendered as OGC WKT | `pa.string()` | [15_clr_udt.md](15_clr_udt.md) | Supported |
| `geometry` | Spatial CLR UDT | 240 | 129 | WKB bytes; rendered as OGC WKT | `pa.string()` | [15_clr_udt.md](15_clr_udt.md) | Supported |
| `json` | SS2025 | 244 | — | MSJSONB binary blob → UTF-8 text | `pa.string()` | [16_json.md](16_json.md) | Supported |
| `vector(N)` | SS2025 | 165 | 255 | float32 array; physically varbinary | `pa.string()` | [17_vector.md](17_vector.md) | Supported |

---

## Notes on counts

The 41-type total matches the `sys.types` row count for `is_user_defined = 0` on SQL Server 2022+ (including SS2025 `json` and `vector`). The four `Alias` entries (`varchar(max)`, `nvarchar(max)`, `varbinary(max)`, `timestamp`) share a `system_type_id` with a Supported type and are handled by the same decoder; they are counted separately because they appear as distinct named types in `sys.types` and T-SQL documentation.

Source: `mssqlbak/types/scalars.py: SUPPORTED_TYPE_IDS`, `SUPPORTED_UDT_TYPE_IDS`
