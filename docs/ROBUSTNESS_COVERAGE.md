# Robustness & skip coverage

What happens when a backup contains something the row reader does not handle.  The contract is: **extract every supported table; for everything else, inspect and skip it with a recorded reason — never crash the run and never emit silently-wrong data.**  **Generated** in part by `python -m tools.robustness_coverage`; `tests/test_robustness.py` fails if the classifier regresses or this file drifts.

Sibling coverage docs: [TYPE_COVERAGE.md](TYPE_COVERAGE.md), [CONSTRAINT_COVERAGE.md](CONSTRAINT_COVERAGE.md), [METADATA_COVERAGE.md](METADATA_COVERAGE.md), [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md), anchored by [BYTE_MAP.md](BYTE_MAP.md).

## Three layers of defence

1. **Inventory** — `mssqlbak.inspect.recover_object_inventory` lists every object in the backup (tables, views, procedures, triggers, functions, constraints, queues, internal/system tables) so nothing is invisible.
2. **Pre-flight classification** — `classify_table` decides, from catalog metadata alone, whether each user table can be read, and if not, why. Skips are *known* before any page is touched.
3. **Per-table safety net** — `extract_bak_to_delta` isolates each table; an unanticipated structure raises, is caught, and is recorded as a skip rather than aborting the whole extraction.

## What is extracted vs skipped

| Backup content | Behaviour | How |
|----------------|-----------|-----|
| Clustered user tables + rows (incl. LOB / row-overflow / legacy text) | **extracted** | row reader |
| Persisted computed columns | **extracted** | stored like a regular column (has a `sysrscols` row) |
| Non-persisted computed columns | excluded from output | no `sysrscols` storage row; dropped from the record layout so offsets stay aligned |
| Views, stored procedures, triggers, functions, defaults (programmability) | not enumerated as data | only `type='U'` objects with a data rowset are read |
| Security: users, roles, permissions | not enumerated as data | live in system schemas (`sys`), never emitted |
| Nonclustered / unique / full-text indexes, statistics | not read as rows | index pages classified skippable in the byte map |
| PK / FK / UNIQUE / CHECK / DEFAULT / cascade rules | decoded for inspection, ignored for data | catalog-only metadata |
| Heap table (no clustered index) | **extracted** | row reader walks the IAM extent bitmap, filtered by page `obj_id` |
| Sparse large-database layout (omitted unallocated extents) | **extracted** | each page is placed at `page_id*8192`, so gaps zero-fill (seen in AdventureWorks2022) |
| Empty heap (no allocated pages / no IAM) | **extracted** (0 rows) | recognised as empty rather than a locate failure (ETL staging tables) |
| Multi-file DB (data on secondary `file_id≠1`) | **extracted** | every data file is reconstructed per `file_id`; the catalog's page locators resolve onto the right file (seen in WideWorldImporters) |
| ROW / PAGE data-compressed table | **skip + report** | `classify_table` → `compressed` (sysrowsets `cmprlevel`) |
| Columnstore table | **skip + report** | column-segment storage, not FixedVar row pages |
| Partitioned table (>1 data partition) | **skip + report** | `classify_table` → `partitioned` |
| Data on a `file_id` absent from the backup | **skip + report** | `classify_table` → `multi-file` (referenced file not in the image) |
| Column of an undecodable type | **skip + report** | `classify_table` → `unsupported-type` |
| Any other unanticipated structure | **skip + report** | per-table safety net catches the error |
| TDE-encrypted backup | rejected at file level | container demux refuses to proceed |

`recover_object_inventory` enumerates **every** `sysschobjs` object; the constraint fixture has 25 user objects and 2768 system objects, each tagged with its type and schema.

**Coverage across committed fixtures:** 64 table(s) extract, 0 skip with an explicit reason; none crash the run.

## Per-table outcomes (from the fixtures)

| Fixture | Table | Result | Reason |
|---------|-------|--------|--------|
| `typecoverage_full.bak` | `lob_links` | OK | — |
| `typecoverage_full.bak` | `t_bigint` | OK | — |
| `typecoverage_full.bak` | `t_binary_8` | OK | — |
| `typecoverage_full.bak` | `t_bit` | OK | — |
| `typecoverage_full.bak` | `t_char_10` | OK | — |
| `typecoverage_full.bak` | `t_date` | OK | — |
| `typecoverage_full.bak` | `t_datetime` | OK | — |
| `typecoverage_full.bak` | `t_datetime2_7` | OK | — |
| `typecoverage_full.bak` | `t_datetimeoffset_7` | OK | — |
| `typecoverage_full.bak` | `t_decimal_38_10` | OK | — |
| `typecoverage_full.bak` | `t_float` | OK | — |
| `typecoverage_full.bak` | `t_geography` | OK | — |
| `typecoverage_full.bak` | `t_geometry` | OK | — |
| `typecoverage_full.bak` | `t_hierarchyid` | OK | — |
| `typecoverage_full.bak` | `t_image` | OK | — |
| `typecoverage_full.bak` | `t_int` | OK | — |
| `typecoverage_full.bak` | `t_money` | OK | — |
| `typecoverage_full.bak` | `t_nchar_10` | OK | — |
| `typecoverage_full.bak` | `t_ntext` | OK | — |
| `typecoverage_full.bak` | `t_numeric_18_4` | OK | — |
| `typecoverage_full.bak` | `t_nvarchar_50` | OK | — |
| `typecoverage_full.bak` | `t_real` | OK | — |
| `typecoverage_full.bak` | `t_rowversion` | OK | — |
| `typecoverage_full.bak` | `t_smalldatetime` | OK | — |
| `typecoverage_full.bak` | `t_smallint` | OK | — |
| `typecoverage_full.bak` | `t_smallmoney` | OK | — |
| `typecoverage_full.bak` | `t_sql_variant` | OK | — |
| `typecoverage_full.bak` | `t_text` | OK | — |
| `typecoverage_full.bak` | `t_time_7` | OK | — |
| `typecoverage_full.bak` | `t_tinyint` | OK | — |
| `typecoverage_full.bak` | `t_uniqueidentifier` | OK | — |
| `typecoverage_full.bak` | `t_varbinary_max` | OK | — |
| `typecoverage_full.bak` | `t_varchar_max` | OK | — |
| `typecoverage_full.bak` | `t_xml` | OK | — |
| `constraintcoverage_full.bak` | `cc_check_constraint` | OK | — |
| `constraintcoverage_full.bak` | `cc_default_constraint` | OK | — |
| `constraintcoverage_full.bak` | `cc_fk_child` | OK | — |
| `constraintcoverage_full.bak` | `cc_fk_parent` | OK | — |
| `constraintcoverage_full.bak` | `cc_index_nonclustered` | OK | — |
| `constraintcoverage_full.bak` | `cc_pk` | OK | — |
| `constraintcoverage_full.bak` | `cc_pk_nonclustered` | OK | — |
| `constraintcoverage_full.bak` | `cc_unique_constraint` | OK | — |
| `constraintcoverage_full.bak` | `cc_unique_index` | OK | — |
| `compressioncoverage_full.bak` | `cmp_columnstore` | OK | — |
| `compressioncoverage_full.bak` | `cmp_columnstore_archive` | OK | — |
| `compressioncoverage_full.bak` | `cmp_none` | OK | — |
| `compressioncoverage_full.bak` | `cmp_page` | OK | — |
| `compressioncoverage_full.bak` | `cmp_page_floats` | OK | — |
| `compressioncoverage_full.bak` | `cmp_page_lob` | OK | — |
| `compressioncoverage_full.bak` | `cmp_page_variant` | OK | — |
| `compressioncoverage_full.bak` | `cmp_page_wide` | OK | — |
| `compressioncoverage_full.bak` | `cmp_row` | OK | — |
| `compressioncoverage_full.bak` | `cmp_row_floats` | OK | — |
| `compressioncoverage_full.bak` | `cmp_row_lob` | OK | — |
| `compressioncoverage_full.bak` | `cmp_row_variant` | OK | — |
| `compressioncoverage_full.bak` | `cmp_row_wide` | OK | — |
| `compressioncoverage_full.bak` | `cs_probe` | OK | — |
| `compressioncoverage_full.bak` | `fwd_heap` | OK | — |
| `compressioncoverage_full.bak` | `ghost_heap` | OK | — |
| `compressioncoverage_full.bak` | `sparse_cols` | OK | — |
| `compressioncoverage_full.bak` | `uniquifier_none` | OK | — |
| `compressioncoverage_full.bak` | `uniquifier_row` | OK | — |
| `computedcoverage_full.bak` | `comp_nonpersisted` | OK | — |
| `computedcoverage_full.bak` | `comp_persisted` | OK | — |

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.
