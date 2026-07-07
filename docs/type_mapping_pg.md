# pgdump — SQL Server .bak → PostgreSQL pg_dump

Reads a SQL Server `.bak` backup file and writes a PostgreSQL-compatible
`pg_dump` plain text SQL file, without a running SQL Server or PostgreSQL
instance.

The same `--sink` flag also writes Delta Lake tables, or both formats
simultaneously.

---

## Prerequisites

- Python 3.11+
- `mssqlbak` package installed (both `mssqlbak` and `pgdump` are part of this
  package)

```bash
pip install mssqlbak
```

The `pgdump` CLI entry point is registered by the package. After installation:

```bash
pgdump --help
```

> The CLI is built with [Typer](https://typer.tiangolo.com/). All commands
> accept `--help`.

---

## Main use case: .bak → pg_dump SQL

```bash
pgdump from-bak mydb.bak --out mydb.sql
```

Writes one `CREATE TABLE` block and one `COPY ... FROM stdin` block per
extracted table. The output is loadable with `psql`:

```bash
psql -d targetdb -f mydb.sql
```

### Options

| Flag | Default | Description |
|---|---|---|
| `BAK` | — | Path to the SQL Server `.bak` file |
| `--out / -o` | required | Output path — `.sql` file for `pgdump`, directory for `delta` or `both` |
| `--sink / -s` | `pgdump` | Output format: `pgdump`, `delta`, or `both` |
| `--verbose / -v` | off | Print per-table progress to stderr |

### Output format variants

```bash
# pg_dump SQL (default)
pgdump from-bak mydb.bak --out mydb.sql

# Delta Lake tables
pgdump from-bak mydb.bak --out /tmp/delta --sink delta

# Both simultaneously — Delta tables in /tmp/out/, pg_dump SQL at /tmp/out/dump.sql
pgdump from-bak mydb.bak --out /tmp/out --sink both
```

---

## Python API

```python
from pgdump.bak_convert import bak_to_pgdump, bak_to_delta, bak_to_both

# .bak → pg_dump SQL
report = bak_to_pgdump("mydb.bak", "mydb.sql")

# .bak → Delta Lake
report = bak_to_delta("mydb.bak", "/tmp/delta")

# .bak → both
report = bak_to_both("mydb.bak", out_dir="/tmp/out", out_sql="/tmp/out/dump.sql")

print(f"{len(report.extracted)} tables, {report.total_rows} rows")
for r in report.skipped:
    print(f"skipped {r.name}: {r.skip_reason}")
```

The `BakConvertReport` fields:

| Field | Type | Description |
|---|---|---|
| `extracted` | `list[BakConvertResult]` | Tables successfully written |
| `skipped` | `list[BakConvertResult]` | Tables not written, with reason |
| `total_rows` | `int` | Total rows written across all extracted tables |
| `elapsed_s` | `float` | Wall-clock seconds |

---

## What is extracted

The same tables that `mssqlbak extract` extracts: clustered user tables in the
`dbo` schema that pass `classify_table`. The classification rules are owned by
mssqlbak and applied before any output is written.

Tables written to the pg_dump file appear under their original schema name
(e.g. `dbo`). To rename the schema on load, use `psql` with `SET search_path`
or `ALTER SCHEMA` after loading.

## What is skipped

Tables skipped by `mssqlbak` (heaps, partitioned tables, tables with
undecodable column types, etc.) are also skipped here. The `BakConvertReport`
lists every skipped table with the reason from `classify_table`.

---

## Type mapping

SQL Server → Arrow → PostgreSQL. The Arrow type comes from `mssqlbak.types.arrow_type`; the PostgreSQL DDL type is produced by `pgdump.pg_sink._arrow_to_pg_type`. Values are written in COPY text format.

| SQL Server type | xtype | Arrow type | PostgreSQL type | Value rule |
|-----------------|-------|------------|-----------------|------------|
| bit | 104 | `int8` | `boolean` | int8 used to avoid a delta-rs bit-packed bool/decimal128 bug; pg sink maps int8 → boolean and writes `t`/`f` in COPY format. |
| tinyint | 48 | `int16` | `smallint` | unsigned 0..255 widened to signed int16; value preserved. |
| smallint | 52 | `int16` | `smallint` | verbatim. |
| int | 56 | `int32` | `integer` | verbatim. |
| bigint | 127 | `int64` | `bigint` | verbatim. |
| decimal | 106 | `decimal128(38,10)` | `numeric(38,10)` | verbatim; precision/scale from column definition. |
| numeric | 108 | `decimal128(18,4)` | `numeric(18,4)` | verbatim; precision/scale from column definition. |
| smallmoney | 122 | `decimal128(10,4)` | `numeric(10,4)` | scaled integer (1e-4 units) → decimal(10,4). |
| money | 60 | `decimal128(19,4)` | `numeric(19,4)` | scaled integer (1e-4 units) → decimal(19,4). |
| real | 59 | `float` | `real` | IEEE-754 float32, verbatim. |
| float | 62 | `double` | `double precision` | IEEE-754 float64, verbatim. |
| date | 40 | `date32[day]` | `date` | verbatim. |
| time | 41 | `string` | `time without time zone` | no Delta time-of-day type → Arrow `string`; pg sink reads `ss_type=time` field metadata and emits `time without time zone`; ISO COPY value is accepted by PostgreSQL. |
| smalldatetime | 58 | `timestamp[us]` | `timestamp without time zone` | → timestamp(us), no time zone. |
| datetime | 61 | `timestamp[us]` | `timestamp without time zone` | → timestamp(us), no time zone. |
| datetime2 | 42 | `timestamp[us]` | `timestamp without time zone` | 100ns ticks floored to microseconds. |
| datetimeoffset | 43 | `timestamp[us, tz=UTC]` | `timestamp with time zone` | instant normalized to UTC; 100ns floored to microseconds; original zone offset not retained. |
| char | 175 | `string` | `text` | fixed-width; trailing space padding preserved. |
| varchar / varchar(max) | 167 | `string` | `text` | single-byte code page decoded. |
| text | 35 | `string` | `text` | off-row LOB stitched. |
| nchar | 239 | `string` | `text` | UTF-16; trailing space padding preserved. |
| nvarchar / nvarchar(max) | 231 | `string` | `text` | UTF-16 decoded. |
| ntext | 99 | `string` | `text` | off-row LOB stitched. |
| binary | 173 | `binary` | `bytea` | fixed-width; trailing zero padding preserved; COPY hex format `\x…`. |
| varbinary / varbinary(max) | 165 | `binary` | `bytea` | LOB / row-overflow stitched; COPY hex format `\x…`. |
| image | 34 | `binary` | `bytea` | off-row LOB stitched; COPY hex format `\x…`. |
| uniqueidentifier | 36 | `string` | `text` | → canonical UUID string (e.g. `3f2504e0-…`). |
| rowversion / timestamp | 189 | `binary` | `bytea` | 8 opaque engine-assigned bytes; COPY hex format `\x…`. |
| xml | 241 | `string` | `text` | tokenised binary-XML re-serialised to XML text. |
| sql_variant | 98 | `string` | `text` | decoded to base-type Python value, then `str()` (bytes as `0x…` hex). |
| geometry / geography / hierarchyid | 240 | `string` | `text` | CLR UDT: geometry/geography → OGC WKT string; hierarchyid → canonical path string. |

---

## pg_dump source: extract a pg_dump file

The `extract` command reads a PostgreSQL `pg_dump` plain text file (the output
of `pg_dump --format=plain`) and writes to Delta Lake, pg_dump, or both.

```bash
# pg_dump SQL → Delta Lake
pgdump extract mydb.sql --out /tmp/delta

# pg_dump SQL → normalized pg_dump SQL
pgdump extract mydb.sql --out mydb_out.sql --sink pgdump

# pg_dump SQL → both
pgdump extract mydb.sql --out /tmp/out --sink both
```

Custom-format dumps (`pg_dump --format=custom`) are not supported. Convert
first:

```bash
pg_restore --format=plain -f mydb.sql mydb.pgc
```

---

## Inspect a .bak or pg_dump file

```bash
# SQL Server .bak — list tables and row counts
mssqlbak inspect mydb.bak

# pg_dump SQL — list tables and row counts
pgdump inspect mydb.sql
```
