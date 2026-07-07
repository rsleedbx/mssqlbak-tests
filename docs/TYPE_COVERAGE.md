# Data-type coverage

Status of every SQL Server scalar type for the `.bak` -> Delta parser.
**Generated** by `python -m tools.type_coverage` from the reference value
matrix and the committed fixture; `tests/test_type_coverage.py` fails if this
file is out of date, so it stays in sync with the tests.

This is the **data** slice of the byte-complete [BYTE_MAP.md](BYTE_MAP.md) (the master coverage doc); the metadata slice is [METADATA_COVERAGE.md](METADATA_COVERAGE.md). Which backup *types* can be restored is tracked in [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md).

**Reference matrix:** 34/34 type cases pass (each case checks low / high / mid / NULL values).

Validation layers for every `PASS` type:

1. **Reference matrix** — decoded values equal known inputs (`tests/test_records.py`), including a 1 MB off-row LOB.
2. **Engine diff** — decoded values equal a live SQL Server's query results, row-for-row (`tests/test_engine_diff.py`, when an engine is available).

**Scope vs. all native types:** of SQL Server's native data types, `cursor`, `table` can never be a table column (excluded). The CLR types `hierarchyid`, `geometry`, `geography` (all `system_type_id` 240, distinguished by `user_type_id`) are decoded to text — spatial to OGC WKT, hierarchyid to its canonical path string. Every column-storable native type is covered below.

| SQL Server type | xtype | Decoder | Result | Notes |
|-----------------|-------|---------|--------|-------|
| bit | 104 | yes | PASS | reference case `bit` |
| tinyint | 48 | yes | PASS | reference case `tinyint` |
| smallint | 52 | yes | PASS | reference case `smallint` |
| int | 56 | yes | PASS | reference case `int` |
| bigint | 127 | yes | PASS | reference case `bigint` |
| decimal | 106 | yes | PASS | reference case `decimal(38,10)` |
| numeric | 108 | yes | PASS | reference case `numeric(18,4)` |
| smallmoney | 122 | yes | PASS | reference case `smallmoney` |
| money | 60 | yes | PASS | reference case `money` |
| real | 59 | yes | PASS | reference case `real` |
| float | 62 | yes | PASS | reference case `float` |
| date | 40 | yes | PASS | reference case `date` |
| time | 41 | yes | PASS | reference case `time(7)` |
| smalldatetime | 58 | yes | PASS | reference case `smalldatetime` |
| datetime | 61 | yes | PASS | reference case `datetime` |
| datetime2 | 42 | yes | PASS | reference case `datetime2(7)` |
| datetimeoffset | 43 | yes | PASS | reference case `datetimeoffset(7)` |
| char | 175 | yes | PASS | reference case `char(10)` |
| varchar / varchar(max) | 167 | yes | PASS | reference case `varchar(max)` |
| text | 35 | yes | PASS | reference case `text` |
| nchar | 239 | yes | PASS | reference case `nchar(10)` |
| nvarchar / nvarchar(max) | 231 | yes | PASS | reference case `nvarchar(50)` |
| ntext | 99 | yes | PASS | reference case `ntext` |
| binary | 173 | yes | PASS | reference case `binary(8)` |
| varbinary / varbinary(max) | 165 | yes | PASS | reference case `varbinary(max)` |
| image | 34 | yes | PASS | reference case `image` |
| uniqueidentifier | 36 | yes | PASS | reference case `uniqueidentifier` |
| rowversion / timestamp | 189 | yes | PASS | engine-populated `rowversion`; validated by engine-diff only |
| xml | 241 | yes | PASS | reference case `xml` |
| sql_variant | 98 | yes | PASS | reference case `sql_variant` |
| hierarchyid | 240 | yes | PASS | reference case `hierarchyid` |
| geometry | 240 | yes | PASS | reference case `geometry` |
| geography | 240 | yes | PASS | reference case `geography` |

## Legend

- **PASS** — covered by a reference case and decoded values matched exactly.
- **FAIL** — covered by a reference case but values did not match (a bug).
- **UNTESTED** — the decoder has a code path but no dedicated reference
  case. Treated as a coverage gap (untested is unsupported);
  `tests/test_type_coverage.py` fails until a reference case is added.
- **not supported** — `decode_value` raises `NotImplementedError`; extracting
  a table with this column type fails loudly rather than emitting wrong data.

## Not-yet-supported types

These raise on extract (no silent corruption). Add a reference case to
`tools/typematrix.py` and a decoder branch in `mssqlbak/types.py` to cover one:

- (none)

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.
