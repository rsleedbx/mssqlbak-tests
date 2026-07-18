# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2019`.

**132 fixtures · 127 pass · 1 xfail (known gap) · 4 fail**

**Tables:** 1812/1924 pass · **Columns:** 19169/19793 pass

**Row count:** 112 fail · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** 112 fail · **Cells:** ✓

**Edges:** mssql→arrow ✓ · arrow→delta ✓ · delta→arrow ✓ · arrow→pg_dir 4 fail · pg_dir→arrow 4 fail

Column key:

| Column | Meaning |
|--------|----------|
| Stage | Pipeline edge being compared (e.g. mssql→arrow = extraction correctness) |
| Source rows | Total rows in all non-empty tables per SQL Server ground truth |
| Source cols | Total columns tracked across all non-empty tables |
| Row count | `matched/total` tables with correct row count |
| Null count | `matched/total` columns with correct null count |
| Min/max | `matched/total` comparable min/max checks; `sql_variant` and `uniqueidentifier` skipped (non-lexicographic ordering) |
| Col count | `matched/total` tables with ≥ expected column count |
| Cells | Row-level cell verification across tables with `<backup>.bak.cells/_manifest.json` |
| Status | ✓ = all match · ~ = xfail (known gap) · ✗ = mismatch |

Memory-optimized (In-Memory OLTP / XTP) tables store their data in XTP checkpoint file pairs (CFPs) rather than 8 KB pages.  mssqlbak decodes their rows from compact and WAL-style CFP blocks embedded in the backup, so they are scored normally against ground truth.

**Metadata:** 1170/1170 fixture-categories pass (constraints: 130/130, indexes: 130/130, extended_properties: 130/130, modules: 130/130, schema_objects: 130/130, security: 130/130, statistics: 130/130, plan_guides: 130/130, query_store: 130/130)

## Summary

| Backup | Stage | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |
|--------|-------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|
| `alias_types_full.bak` | mssql→arrow | 3 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `alias_types_full.bak` | arrow→delta | 3 | 6 | **1/1** | **6/6** | **12/12** | **1/1** | — | ✓ |
| `alias_types_full.bak` | delta→arrow | 3 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `alias_types_full.bak` | arrow→pg_dir | 3 | 6 | **1/1** | **6/6** | **12/12** | **1/1** | — | ✓ |
| `alias_types_full.bak` | pg_dir→arrow | 3 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `archive_columnstore_partition_full.bak` | mssql→arrow | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | digest | ✓ |
| `archive_columnstore_partition_full.bak` | arrow→delta | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | — | ✓ |
| `archive_columnstore_partition_full.bak` | delta→arrow | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | digest | ✓ |
| `archive_columnstore_partition_full.bak` | arrow→pg_dir | 560,000 | 12 | 1/4 ⚠ ⚠ (`dbo.archive_part_mixed`, `dbo.archive_part_roundtrip`, `dbo.archive_part_single`) | **3/3** | **6/6** | 1/4 ⚠ | — | ✗ |
| `archive_columnstore_partition_full.bak` | pg_dir→arrow | 560,000 | 12 | 1/4 ⚠ ⚠ (`dbo.archive_part_mixed`, `dbo.archive_part_roundtrip`, `dbo.archive_part_single`) | **3/3** | **6/6** | 1/4 ⚠ | digest | ✗ |
| `archive_columnstore_types_full.bak` | mssql→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_full.bak` | arrow→delta | 245,000 | 14 | **7/7** | **14/14** | **28/28** | **7/7** | — | ✓ |
| `archive_columnstore_types_full.bak` | delta→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_full.bak` | arrow→pg_dir | 245,000 | 14 | 0/7 ⚠ ⚠ (`dbo.archive_binary10`, `dbo.archive_char10`, `dbo.archive_nchar10`, `dbo.archive_nvarchar20`, `dbo.archive_uuid`, `dbo.archive_varbinary20`, `dbo.archive_varchar20`) | — | — | 0/7 ⚠ | — | ✗ |
| `archive_columnstore_types_full.bak` | pg_dir→arrow | 245,000 | 14 | 0/7 ⚠ ⚠ (`dbo.archive_binary10`, `dbo.archive_char10`, `dbo.archive_nchar10`, `dbo.archive_nvarchar20`, `dbo.archive_uuid`, `dbo.archive_varbinary20`, `dbo.archive_varchar20`) | — | — | 0/7 ⚠ | — | ✗ |
| `archive_columnstore_types_random_full.bak` | mssql→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_random_full.bak` | arrow→delta | 245,000 | 14 | **7/7** | **14/14** | **28/28** | **7/7** | — | ✓ |
| `archive_columnstore_types_random_full.bak` | delta→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_random_full.bak` | arrow→pg_dir | 245,000 | 14 | **7/7** | **14/14** | **28/28** | **7/7** | — | ✓ |
| `archive_columnstore_types_random_full.bak` | pg_dir→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_single_chunk_full.bak` | mssql→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_full.bak` | arrow→delta | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `archive_single_chunk_full.bak` | delta→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_full.bak` | arrow→pg_dir | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `archive_single_chunk_full.bak` | pg_dir→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_random_full.bak` | mssql→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_random_full.bak` | arrow→delta | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `archive_single_chunk_random_full.bak` | delta→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_random_full.bak` | arrow→pg_dir | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `archive_single_chunk_random_full.bak` | pg_dir→arrow | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archivenull_full.bak` | mssql→arrow | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `archivenull_full.bak` | arrow→delta | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `archivenull_full.bak` | delta→arrow | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `archivenull_full.bak` | arrow→pg_dir | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `archivenull_full.bak` | pg_dir→arrow | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `backup_blocksize_full.bak` | mssql→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `backup_blocksize_full.bak` | arrow→delta | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `backup_blocksize_full.bak` | delta→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `backup_blocksize_full.bak` | arrow→pg_dir | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `backup_blocksize_full.bak` | pg_dir→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `boundarycoverage_datetime_full.bak` | mssql→arrow | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `boundarycoverage_datetime_full.bak` | arrow→delta | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | — | ✓ |
| `boundarycoverage_datetime_full.bak` | delta→arrow | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `boundarycoverage_datetime_full.bak` | arrow→pg_dir | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | — | ✓ |
| `boundarycoverage_datetime_full.bak` | pg_dir→arrow | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `boundarycoverage_full.bak` | mssql→arrow | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | digest | ✓ |
| `boundarycoverage_full.bak` | arrow→delta | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | — | ✓ |
| `boundarycoverage_full.bak` | delta→arrow | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | digest | ✓ |
| `boundarycoverage_full.bak` | arrow→pg_dir | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | — | ✓ |
| `boundarycoverage_full.bak` | pg_dir→arrow | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | digest | ✓ |
| `catalog_ss2019.bak` | mssql→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `catalog_ss2019.bak` | arrow→delta | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `catalog_ss2019.bak` | delta→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `catalog_ss2019.bak` | arrow→pg_dir | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `catalog_ss2019.bak` | pg_dir→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `cci_binary_varbinary_compare_full.bak` | mssql→arrow | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `cci_binary_varbinary_compare_full.bak` | arrow→delta | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `cci_binary_varbinary_compare_full.bak` | delta→arrow | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `cci_binary_varbinary_compare_full.bak` | arrow→pg_dir | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `cci_binary_varbinary_compare_full.bak` | pg_dir→arrow | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | mssql→arrow | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | arrow→delta | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | — | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | delta→arrow | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | arrow→pg_dir | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | — | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | pg_dir→arrow | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_full.bak` | mssql→arrow | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_full.bak` | arrow→delta | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `cci_bitpack_probe_full.bak` | delta→arrow | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_full.bak` | arrow→pg_dir | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `cci_bitpack_probe_full.bak` | pg_dir→arrow | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | mssql→arrow | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | arrow→delta | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | — | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | delta→arrow | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | arrow→pg_dir | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | — | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | pg_dir→arrow | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_btree_nci_full.bak` | mssql→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_btree_nci_full.bak` | arrow→delta | 2,400 | 5 | **2/2** | **6/6** | **10/10** | **2/2** | — | ✓ |
| `cci_btree_nci_full.bak` | delta→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_btree_nci_full.bak` | arrow→pg_dir | 2,400 | 5 | **2/2** | **6/6** | **10/10** | **2/2** | — | ✓ |
| `cci_btree_nci_full.bak` | pg_dir→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_computed_full.bak` | mssql→arrow | 2,400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_computed_full.bak` | arrow→delta | 2,400 | 4 | **2/2** | **5/5** | **8/8** | **2/2** | — | ✓ |
| `cci_computed_full.bak` | delta→arrow | 2,400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_computed_full.bak` | arrow→pg_dir | 2,400 | 4 | **2/2** | **5/5** | **8/8** | **2/2** | — | ✓ |
| `cci_computed_full.bak` | pg_dir→arrow | 2,400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_full.bak` | mssql→arrow | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_full.bak` | arrow→delta | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `cci_enc5_largepool_full.bak` | delta→arrow | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_full.bak` | arrow→pg_dir | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `cci_enc5_largepool_full.bak` | pg_dir→arrow | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | — | — | — | — | — | — | — | — | ✓ |
| `cci_extended_full.bak` | mssql→arrow | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | digest | ✓ |
| `cci_extended_full.bak` | arrow→delta | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | — | ✓ |
| `cci_extended_full.bak` | delta→arrow | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | digest | ✓ |
| `cci_extended_full.bak` | arrow→pg_dir | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | — | ✓ |
| `cci_extended_full.bak` | pg_dir→arrow | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | digest | ✓ |
| `cci_lob_full.bak` | mssql→arrow | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | digest | ✓ |
| `cci_lob_full.bak` | arrow→delta | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | — | ✓ |
| `cci_lob_full.bak` | delta→arrow | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | digest | ✓ |
| `cci_lob_full.bak` | arrow→pg_dir | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | — | ✓ |
| `cci_lob_full.bak` | pg_dir→arrow | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | digest | ✓ |
| `cci_reorganize_full.bak` | mssql→arrow | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | digest | ✓ |
| `cci_reorganize_full.bak` | arrow→delta | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | — | ✓ |
| `cci_reorganize_full.bak` | delta→arrow | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | digest | ✓ |
| `cci_reorganize_full.bak` | arrow→pg_dir | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | — | ✓ |
| `cci_reorganize_full.bak` | pg_dir→arrow | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | digest | ✓ |
| `cci_string_dict_regression_full.bak` | mssql→arrow | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_dict_regression_full.bak` | arrow→delta | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `cci_string_dict_regression_full.bak` | delta→arrow | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_dict_regression_full.bak` | arrow→pg_dir | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `cci_string_dict_regression_full.bak` | pg_dir→arrow | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_minmax_full.bak` | mssql→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_minmax_full.bak` | arrow→delta | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `cci_string_minmax_full.bak` | delta→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_minmax_full.bak` | arrow→pg_dir | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `cci_string_minmax_full.bak` | pg_dir→arrow | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_switch_full.bak` | mssql→arrow | 2,400 | 7 | **3/3** | **4/4** | **8/8** | **3/3** | digest | ✓ |
| `cci_switch_full.bak` | arrow→delta | 2,400 | 7 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `cci_switch_full.bak` | delta→arrow | 2,400 | 7 | **3/3** | **4/4** | **8/8** | **3/3** | digest | ✓ |
| `cci_switch_full.bak` | arrow→pg_dir | 2,400 | 7 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `cci_switch_full.bak` | pg_dir→arrow | 2,400 | 7 | **3/3** | **4/4** | **8/8** | **3/3** | digest | ✓ |
| `cci_types_large_full.bak` | mssql→arrow | 6,000 | 10 | **5/5** | **10/10** | **18/18** | **5/5** | digest | ✓ |
| `cci_types_large_full.bak` | arrow→delta | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | — | ✓ |
| `cci_types_large_full.bak` | delta→arrow | 6,000 | 10 | **5/5** | **10/10** | **18/18** | **5/5** | digest | ✓ |
| `cci_types_large_full.bak` | arrow→pg_dir | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | — | ✓ |
| `cci_types_large_full.bak` | pg_dir→arrow | 6,000 | 10 | **5/5** | **10/10** | **18/18** | **5/5** | digest | ✓ |
| `cci_varbinary_micro_full.bak` | mssql→arrow | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_micro_full.bak` | arrow→delta | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | — | ✓ |
| `cci_varbinary_micro_full.bak` | delta→arrow | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_micro_full.bak` | arrow→pg_dir | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | — | ✓ |
| `cci_varbinary_micro_full.bak` | pg_dir→arrow | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_probe_full.bak` | mssql→arrow | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_probe_full.bak` | arrow→delta | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | — | ✓ |
| `cci_varbinary_probe_full.bak` | delta→arrow | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_probe_full.bak` | arrow→pg_dir | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | — | ✓ |
| `cci_varbinary_probe_full.bak` | pg_dir→arrow | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `columnstore_minimal.bak` | mssql→arrow | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | digest | ✓ |
| `columnstore_minimal.bak` | arrow→delta | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | — | ✓ |
| `columnstore_minimal.bak` | delta→arrow | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | digest | ✓ |
| `columnstore_minimal.bak` | arrow→pg_dir | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | — | ✓ |
| `columnstore_minimal.bak` | pg_dir→arrow | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | digest | ✓ |
| `compressed_nvarchar_full.bak` | mssql→arrow | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `compressed_nvarchar_full.bak` | arrow→delta | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `compressed_nvarchar_full.bak` | delta→arrow | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `compressed_nvarchar_full.bak` | arrow→pg_dir | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `compressed_nvarchar_full.bak` | pg_dir→arrow | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `compressioncoverage_full.bak` | mssql→arrow | 1,994 | 239 | **19/19** | **239/239** | **464/464** | **19/19** | digest | ✓ |
| `compressioncoverage_full.bak` | arrow→delta | 1,994 | 239 | **19/19** | **239/239** | **478/478** | **19/19** | — | ✓ |
| `compressioncoverage_full.bak` | delta→arrow | 1,994 | 239 | **19/19** | **239/239** | **464/464** | **19/19** | digest | ✓ |
| `compressioncoverage_full.bak` | arrow→pg_dir | 1,994 | 239 | 10/19 ⚠ ⚠ (`dbo.cmp_row_lob`, `dbo.cmp_row_variant`, `dbo.cmp_row_wide`, `dbo.cs_probe`, `dbo.fwd_heap`, `dbo.ghost_heap`, `dbo.sparse_cols`, `dbo.uniquifier_none`, `dbo.uniquifier_row`) | **172/172** | **344/344** | 10/19 ⚠ | — | ✗ |
| `compressioncoverage_full.bak` | pg_dir→arrow | 1,994 | 239 | 10/19 ⚠ ⚠ (`dbo.cmp_row_lob`, `dbo.cmp_row_variant`, `dbo.cmp_row_wide`, `dbo.cs_probe`, `dbo.fwd_heap`, `dbo.ghost_heap`, `dbo.sparse_cols`, `dbo.uniquifier_none`, `dbo.uniquifier_row`) | **172/172** | **332/332** | 10/19 ⚠ | digest | ✗ |
| `computedcoverage_full.bak` | mssql→arrow | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | digest | ✓ |
| `computedcoverage_full.bak` | arrow→delta | 6 | 8 | **2/2** | **10/10** | **20/20** | **2/2** | — | ✓ |
| `computedcoverage_full.bak` | delta→arrow | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | digest | ✓ |
| `computedcoverage_full.bak` | arrow→pg_dir | 6 | 8 | **2/2** | **10/10** | **20/20** | **2/2** | — | ✓ |
| `computedcoverage_full.bak` | pg_dir→arrow | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | digest | ✓ |
| `constraintcoverage_full.bak` | mssql→arrow | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `constraintcoverage_full.bak` | arrow→delta | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | — | ✓ |
| `constraintcoverage_full.bak` | delta→arrow | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `constraintcoverage_full.bak` | arrow→pg_dir | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | — | ✓ |
| `constraintcoverage_full.bak` | pg_dir→arrow | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | digest | ✓ |
| `covering_index_full.bak` | mssql→arrow | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `covering_index_full.bak` | arrow→delta | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `covering_index_full.bak` | delta→arrow | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `covering_index_full.bak` | arrow→pg_dir | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `covering_index_full.bak` | pg_dir→arrow | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cs_lob_preamble.bak` | mssql→arrow | 1,400 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `cs_lob_preamble.bak` | arrow→delta | 1,400 | 2 | **1/1** | **3/3** | **4/4** | **1/1** | — | ✓ |
| `cs_lob_preamble.bak` | delta→arrow | 1,400 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `cs_lob_preamble.bak` | arrow→pg_dir | 1,400 | 2 | **1/1** | **3/3** | **4/4** | **1/1** | — | ✓ |
| `cs_lob_preamble.bak` | pg_dir→arrow | 1,400 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `delta_rowgroup_full.bak` | mssql→arrow | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `delta_rowgroup_full.bak` | arrow→delta | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `delta_rowgroup_full.bak` | delta→arrow | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `delta_rowgroup_full.bak` | arrow→pg_dir | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `delta_rowgroup_full.bak` | pg_dir→arrow | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_aborted_xact.bak` | mssql→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_aborted_xact.bak` | arrow→delta | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_aborted_xact.bak` | delta→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_aborted_xact.bak` | arrow→pg_dir | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_aborted_xact.bak` | pg_dir→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_addcol.bak` | mssql→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_addcol.bak` | arrow→delta | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_addcol.bak` | delta→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_addcol.bak` | arrow→pg_dir | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_addcol.bak` | pg_dir→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_addnotnull.bak` | mssql→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_addnotnull.bak` | arrow→delta | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_addnotnull.bak` | delta→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_addnotnull.bak` | arrow→pg_dir | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_addnotnull.bak` | pg_dir→arrow | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_alldirty.bak` | mssql→arrow | 0 | 3 | **1/1** | — | — | **1/1** | empty | ✓ |
| `dirtycoverage_alldirty.bak` | arrow→delta | 0 | 3 | — | — | — | — | — | ✓ |
| `dirtycoverage_alldirty.bak` | delta→arrow | 0 | 3 | **1/1** | — | — | **1/1** | empty | ✓ |
| `dirtycoverage_alldirty.bak` | arrow→pg_dir | 0 | 3 | — | — | — | — | — | ✓ |
| `dirtycoverage_alldirty.bak` | pg_dir→arrow | 0 | 3 | **1/1** | — | — | **1/1** | empty | ✓ |
| `dirtycoverage_altercol.bak` | mssql→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_altercol.bak` | arrow→delta | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_altercol.bak` | delta→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_altercol.bak` | arrow→pg_dir | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_altercol.bak` | pg_dir→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | mssql→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | arrow→delta | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | delta→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | arrow→pg_dir | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | pg_dir→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_alterdb.bak` | mssql→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_alterdb.bak` | arrow→delta | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_alterdb.bak` | delta→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_alterdb.bak` | arrow→pg_dir | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_alterdb.bak` | pg_dir→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_cci_delete.bak` | mssql→arrow | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_delete.bak` | arrow→delta | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_delete.bak` | delta→arrow | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_delete.bak` | arrow→pg_dir | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_delete.bak` | pg_dir→arrow | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_update.bak` | mssql→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_update.bak` | arrow→delta | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_update.bak` | delta→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_update.bak` | arrow→pg_dir | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_update.bak` | pg_dir→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_delete.bak` | mssql→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete.bak` | arrow→delta | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete.bak` | delta→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete.bak` | arrow→pg_dir | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete.bak` | pg_dir→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | mssql→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | arrow→delta | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | delta→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | arrow→pg_dir | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | pg_dir→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | mssql→arrow | 200 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | arrow→delta | 200 | 27 | **1/1** | **27/27** | **54/54** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | delta→arrow | 200 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | arrow→pg_dir | 200 | 27 | **1/1** | **27/27** | **54/54** | **1/1** | — | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | pg_dir→arrow | 200 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | mssql→arrow | 9,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | arrow→delta | 9,000 | 9 | **2/2** | **9/9** | **18/18** | **2/2** | — | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | delta→arrow | 9,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | arrow→pg_dir | 9,000 | 9 | **2/2** | **9/9** | **18/18** | **2/2** | — | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | pg_dir→arrow | 9,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_update.bak` | mssql→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update.bak` | arrow→delta | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update.bak` | delta→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update.bak` | arrow→pg_dir | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update.bak` | pg_dir→arrow | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v2.bak` | mssql→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v2.bak` | arrow→delta | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update_v2.bak` | delta→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v2.bak` | arrow→pg_dir | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update_v2.bak` | pg_dir→arrow | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v3.bak` | mssql→arrow | 300 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v3.bak` | arrow→delta | 300 | 27 | **1/1** | **27/27** | **54/54** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update_v3.bak` | delta→arrow | 300 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v3.bak` | arrow→pg_dir | 300 | 27 | **1/1** | **27/27** | **54/54** | **1/1** | — | ✓ |
| `dirtycoverage_committed_update_v3.bak` | pg_dir→arrow | 300 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | digest | ✓ |
| `dirtycoverage_committed_update_v4.bak` | mssql→arrow | 10,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_update_v4.bak` | arrow→delta | 10,000 | 9 | **2/2** | **9/9** | **18/18** | **2/2** | — | ✓ |
| `dirtycoverage_committed_update_v4.bak` | delta→arrow | 10,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_update_v4.bak` | arrow→pg_dir | 10,000 | 9 | **2/2** | **9/9** | **18/18** | **2/2** | — | ✓ |
| `dirtycoverage_committed_update_v4.bak` | pg_dir→arrow | 10,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | digest | ✓ |
| `dirtycoverage_concurrent.bak` | mssql→arrow | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_concurrent.bak` | arrow→delta | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_concurrent.bak` | delta→arrow | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_concurrent.bak` | arrow→pg_dir | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_concurrent.bak` | pg_dir→arrow | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_createidx.bak` | mssql→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_createidx.bak` | arrow→delta | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_createidx.bak` | delta→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_createidx.bak` | arrow→pg_dir | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_createidx.bak` | pg_dir→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_createtable.bak` | mssql→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_createtable.bak` | arrow→delta | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_createtable.bak` | delta→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_createtable.bak` | arrow→pg_dir | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_createtable.bak` | pg_dir→arrow | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_delete.bak` | mssql→arrow | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_delete.bak` | arrow→delta | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_delete.bak` | delta→arrow | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_delete.bak` | arrow→pg_dir | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_delete.bak` | pg_dir→arrow | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropcol.bak` | mssql→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropcol.bak` | arrow→delta | 60 | 3 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_dropcol.bak` | delta→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropcol.bak` | arrow→pg_dir | 60 | 3 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_dropcol.bak` | pg_dir→arrow | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropidx.bak` | mssql→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropidx.bak` | arrow→delta | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_dropidx.bak` | delta→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_dropidx.bak` | arrow→pg_dir | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_dropidx.bak` | pg_dir→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_droptable.bak` | mssql→arrow | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_droptable.bak` | arrow→delta | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_droptable.bak` | delta→arrow | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_droptable.bak` | arrow→pg_dir | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_droptable.bak` | pg_dir→arrow | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_heap_forward.bak` | mssql→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_heap_forward.bak` | arrow→delta | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_heap_forward.bak` | delta→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_heap_forward.bak` | arrow→pg_dir | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_heap_forward.bak` | pg_dir→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_large_dirty.bak` | mssql→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_large_dirty.bak` | arrow→delta | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_large_dirty.bak` | delta→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_large_dirty.bak` | arrow→pg_dir | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_large_dirty.bak` | pg_dir→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_lob_update.bak` | mssql→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_lob_update.bak` | arrow→delta | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_lob_update.bak` | delta→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_lob_update.bak` | arrow→pg_dir | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_lob_update.bak` | pg_dir→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_maxrow.bak` | mssql→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_maxrow.bak` | arrow→delta | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_maxrow.bak` | delta→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_maxrow.bak` | arrow→pg_dir | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_maxrow.bak` | pg_dir→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_nchar_delete.bak` | mssql→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_nchar_delete.bak` | arrow→delta | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_nchar_delete.bak` | delta→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_nchar_delete.bak` | arrow→pg_dir | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_nchar_delete.bak` | pg_dir→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_nested.bak` | mssql→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_nested.bak` | arrow→delta | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_nested.bak` | delta→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_nested.bak` | arrow→pg_dir | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_nested.bak` | pg_dir→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_null_update.bak` | mssql→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_null_update.bak` | arrow→delta | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_null_update.bak` | delta→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_null_update.bak` | arrow→pg_dir | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_null_update.bak` | pg_dir→arrow | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_rebuildidx.bak` | mssql→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_rebuildidx.bak` | arrow→delta | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_rebuildidx.bak` | delta→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_rebuildidx.bak` | arrow→pg_dir | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_rebuildidx.bak` | pg_dir→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_insert.bak` | mssql→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_insert.bak` | arrow→delta | 20 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `dirtycoverage_rich_insert.bak` | delta→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_insert.bak` | arrow→pg_dir | 20 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `dirtycoverage_rich_insert.bak` | pg_dir→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_update.bak` | mssql→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_update.bak` | arrow→delta | 20 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `dirtycoverage_rich_update.bak` | delta→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_update.bak` | arrow→pg_dir | 20 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `dirtycoverage_rich_update.bak` | pg_dir→arrow | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_savepoint.bak` | mssql→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_savepoint.bak` | arrow→delta | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_savepoint.bak` | delta→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_savepoint.bak` | arrow→pg_dir | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_savepoint.bak` | pg_dir→arrow | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_snapshot_update.bak` | mssql→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_snapshot_update.bak` | arrow→delta | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_snapshot_update.bak` | delta→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_snapshot_update.bak` | arrow→pg_dir | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `dirtycoverage_snapshot_update.bak` | pg_dir→arrow | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_switch.bak` | mssql→arrow | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `dirtycoverage_switch.bak` | arrow→delta | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `dirtycoverage_switch.bak` | delta→arrow | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `dirtycoverage_switch.bak` | arrow→pg_dir | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `dirtycoverage_switch.bak` | pg_dir→arrow | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `dirtycoverage_temporal_update.bak` | mssql→arrow | 20 | 8 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `dirtycoverage_temporal_update.bak` | arrow→delta | 20 | 8 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_temporal_update.bak` | delta→arrow | 20 | 8 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `dirtycoverage_temporal_update.bak` | arrow→pg_dir | 20 | 8 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_temporal_update.bak` | pg_dir→arrow | 20 | 8 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `dirtycoverage_truncate.bak` | mssql→arrow | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_truncate.bak` | arrow→delta | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_truncate.bak` | delta→arrow | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_truncate.bak` | arrow→pg_dir | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_truncate.bak` | pg_dir→arrow | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_two_tx.bak` | mssql→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_two_tx.bak` | arrow→delta | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_two_tx.bak` | delta→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_two_tx.bak` | arrow→pg_dir | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `dirtycoverage_two_tx.bak` | pg_dir→arrow | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `dirtycoverage_uncommitted.bak` | mssql→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_uncommitted.bak` | arrow→delta | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_uncommitted.bak` | delta→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_uncommitted.bak` | arrow→pg_dir | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_uncommitted.bak` | pg_dir→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_update.bak` | mssql→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_update.bak` | arrow→delta | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_update.bak` | delta→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `dirtycoverage_update.bak` | arrow→pg_dir | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `dirtycoverage_update.bak` | pg_dir→arrow | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `filtered_ncci_full.bak` | mssql→arrow | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `filtered_ncci_full.bak` | arrow→delta | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | — | ✓ |
| `filtered_ncci_full.bak` | delta→arrow | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `filtered_ncci_full.bak` | arrow→pg_dir | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | — | ✓ |
| `filtered_ncci_full.bak` | pg_dir→arrow | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `float_extreme_full.bak` | mssql→arrow | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `float_extreme_full.bak` | arrow→delta | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `float_extreme_full.bak` | delta→arrow | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `float_extreme_full.bak` | arrow→pg_dir | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `float_extreme_full.bak` | pg_dir→arrow | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `forwarded_records_full.bak` | mssql→arrow | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `forwarded_records_full.bak` | arrow→delta | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `forwarded_records_full.bak` | delta→arrow | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `forwarded_records_full.bak` | arrow→pg_dir | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `forwarded_records_full.bak` | pg_dir→arrow | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ghost_records_full.bak` | mssql→arrow | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `ghost_records_full.bak` | arrow→delta | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `ghost_records_full.bak` | delta→arrow | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `ghost_records_full.bak` | arrow→pg_dir | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `ghost_records_full.bak` | pg_dir→arrow | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `heapcoverage_large.bak` | mssql→arrow | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `heapcoverage_large.bak` | arrow→delta | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `heapcoverage_large.bak` | delta→arrow | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `heapcoverage_large.bak` | arrow→pg_dir | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `heapcoverage_large.bak` | pg_dir→arrow | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `heapcoverage_large_50000.bak` | mssql→arrow | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `heapcoverage_large_50000.bak` | arrow→delta | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `heapcoverage_large_50000.bak` | delta→arrow | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `heapcoverage_large_50000.bak` | arrow→pg_dir | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | — | ✓ |
| `heapcoverage_large_50000.bak` | pg_dir→arrow | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `hierarchyid_extract_full.bak` | mssql→arrow | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `hierarchyid_extract_full.bak` | arrow→delta | 6 | 2 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `hierarchyid_extract_full.bak` | delta→arrow | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `hierarchyid_extract_full.bak` | arrow→pg_dir | 6 | 2 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `hierarchyid_extract_full.bak` | pg_dir→arrow | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `high_slot_density_full.bak` | mssql→arrow | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | digest | ✓ |
| `high_slot_density_full.bak` | arrow→delta | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | — | ✓ |
| `high_slot_density_full.bak` | delta→arrow | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | digest | ✓ |
| `high_slot_density_full.bak` | arrow→pg_dir | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | — | ✓ |
| `high_slot_density_full.bak` | pg_dir→arrow | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | digest | ✓ |
| `identity_coverage_full.bak` | mssql→arrow | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | digest | ✓ |
| `identity_coverage_full.bak` | arrow→delta | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | — | ✓ |
| `identity_coverage_full.bak` | delta→arrow | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | digest | ✓ |
| `identity_coverage_full.bak` | arrow→pg_dir | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | — | ✓ |
| `identity_coverage_full.bak` | pg_dir→arrow | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | digest | ✓ |
| `incrementalcoverage_diff_01.bak` | mssql→arrow | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_01.bak` | arrow→delta | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_01.bak` | delta→arrow | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_01.bak` | arrow→pg_dir | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_01.bak` | pg_dir→arrow | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_02.bak` | mssql→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_02.bak` | arrow→delta | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_02.bak` | delta→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_02.bak` | arrow→pg_dir | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_02.bak` | pg_dir→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_03.bak` | mssql→arrow | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_03.bak` | arrow→delta | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_03.bak` | delta→arrow | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_03.bak` | arrow→pg_dir | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_03.bak` | pg_dir→arrow | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_04.bak` | mssql→arrow | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_04.bak` | arrow→delta | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_04.bak` | delta→arrow | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_04.bak` | arrow→pg_dir | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_04.bak` | pg_dir→arrow | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_05.bak` | mssql→arrow | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_05.bak` | arrow→delta | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_05.bak` | delta→arrow | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_05.bak` | arrow→pg_dir | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_05.bak` | pg_dir→arrow | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_06.bak` | mssql→arrow | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_06.bak` | arrow→delta | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_06.bak` | delta→arrow | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_diff_06.bak` | arrow→pg_dir | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_diff_06.bak` | pg_dir→arrow | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_full.bak` | mssql→arrow | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_full.bak` | arrow→delta | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_full.bak` | delta→arrow | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `incrementalcoverage_full.bak` | arrow→pg_dir | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `incrementalcoverage_full.bak` | pg_dir→arrow | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `layoutcoverage_full.bak` | mssql→arrow | 171 | 2,421 | **57/57** | **2421/2421** | **4834/4834** | **57/57** | digest | ✓ |
| `layoutcoverage_full.bak` | arrow→delta | 171 | 2,421 | **57/57** | **2421/2421** | **4842/4842** | **57/57** | — | ✓ |
| `layoutcoverage_full.bak` | delta→arrow | 171 | 2,421 | **57/57** | **2421/2421** | **4834/4834** | **57/57** | digest | ✓ |
| `layoutcoverage_full.bak` | arrow→pg_dir | 171 | 2,421 | 20/57 ⚠ ⚠ (`dbo.layout_pk_date_penult`, `dbo.layout_pk_datetime2_first`, `dbo.layout_pk_datetime2_last`, `dbo.layout_pk_datetime2_penult`, `dbo.layout_pk_datetime2_second`, `dbo.layout_pk_decimal18_first`, `dbo.layout_pk_decimal18_last`, `dbo.layout_pk_decimal18_penult`, `dbo.layout_pk_decimal18_second`, `dbo.layout_pk_int_first`, `dbo.layout_pk_int_last`, `dbo.layout_pk_int_penult`, `dbo.layout_pk_int_second`, `dbo.layout_pk_nchar10_first`, `dbo.layout_pk_nchar10_last`, `dbo.layout_pk_nchar10_penult`, `dbo.layout_pk_nchar10_second`, `dbo.layout_pk_nvarchar50_first`, `dbo.layout_pk_nvarchar50_last`, `dbo.layout_pk_nvarchar50_penult`, `dbo.layout_pk_nvarchar50_second`, `dbo.layout_pk_smallint_first`, `dbo.layout_pk_smallint_last`, `dbo.layout_pk_smallint_penult`, `dbo.layout_pk_smallint_second`, `dbo.layout_pk_tinyint_first`, `dbo.layout_pk_tinyint_last`, `dbo.layout_pk_tinyint_penult`, `dbo.layout_pk_tinyint_second`, `dbo.layout_pk_uniqueidentifier_first`, `dbo.layout_pk_uniqueidentifier_last`, `dbo.layout_pk_uniqueidentifier_penult`, `dbo.layout_pk_uniqueidentifier_second`, `dbo.layout_pk_varchar100_first`, `dbo.layout_pk_varchar100_last`, `dbo.layout_pk_varchar100_penult`, `dbo.layout_pk_varchar100_second`) | **2199/2199** | **4398/4398** | 20/57 ⚠ | — | ✗ |
| `layoutcoverage_full.bak` | pg_dir→arrow | 171 | 2,421 | 20/57 ⚠ ⚠ (`dbo.layout_pk_date_penult`, `dbo.layout_pk_datetime2_first`, `dbo.layout_pk_datetime2_last`, `dbo.layout_pk_datetime2_penult`, `dbo.layout_pk_datetime2_second`, `dbo.layout_pk_decimal18_first`, `dbo.layout_pk_decimal18_last`, `dbo.layout_pk_decimal18_penult`, `dbo.layout_pk_decimal18_second`, `dbo.layout_pk_int_first`, `dbo.layout_pk_int_last`, `dbo.layout_pk_int_penult`, `dbo.layout_pk_int_second`, `dbo.layout_pk_nchar10_first`, `dbo.layout_pk_nchar10_last`, `dbo.layout_pk_nchar10_penult`, `dbo.layout_pk_nchar10_second`, `dbo.layout_pk_nvarchar50_first`, `dbo.layout_pk_nvarchar50_last`, `dbo.layout_pk_nvarchar50_penult`, `dbo.layout_pk_nvarchar50_second`, `dbo.layout_pk_smallint_first`, `dbo.layout_pk_smallint_last`, `dbo.layout_pk_smallint_penult`, `dbo.layout_pk_smallint_second`, `dbo.layout_pk_tinyint_first`, `dbo.layout_pk_tinyint_last`, `dbo.layout_pk_tinyint_penult`, `dbo.layout_pk_tinyint_second`, `dbo.layout_pk_uniqueidentifier_first`, `dbo.layout_pk_uniqueidentifier_last`, `dbo.layout_pk_uniqueidentifier_penult`, `dbo.layout_pk_uniqueidentifier_second`, `dbo.layout_pk_varchar100_first`, `dbo.layout_pk_varchar100_last`, `dbo.layout_pk_varchar100_penult`, `dbo.layout_pk_varchar100_second`) | **2199/2199** | **4398/4398** | 20/57 ⚠ | digest | ✗ |
| `max_row_width_full.bak` | mssql→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `max_row_width_full.bak` | arrow→delta | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `max_row_width_full.bak` | delta→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `max_row_width_full.bak` | arrow→pg_dir | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `max_row_width_full.bak` | pg_dir→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | mssql→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | arrow→delta | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | — | ✓ |
| `mixed_collation_full.bak` | delta→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | arrow→pg_dir | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | — | ✓ |
| `mixed_collation_full.bak` | pg_dir→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `multi_rowgroup_full.bak` | mssql→arrow | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `multi_rowgroup_full.bak` | arrow→delta | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `multi_rowgroup_full.bak` | delta→arrow | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `multi_rowgroup_full.bak` | arrow→pg_dir | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `multi_rowgroup_full.bak` | pg_dir→arrow | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | mssql→arrow | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | arrow→delta | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `ncci_heap_full.bak` | delta→arrow | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | arrow→pg_dir | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `ncci_heap_full.bak` | pg_dir→arrow | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_types_full.bak` | mssql→arrow | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | digest | ✓ |
| `ncci_types_full.bak` | arrow→delta | 24,057 | 39 | **20/20** | **39/39** | **78/78** | **20/20** | — | ✓ |
| `ncci_types_full.bak` | delta→arrow | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | digest | ✓ |
| `ncci_types_full.bak` | arrow→pg_dir | 24,057 | 39 | **20/20** | **39/39** | **78/78** | **20/20** | — | ✓ |
| `ncci_types_full.bak` | pg_dir→arrow | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | digest | ✓ |
| `ndfcoverage_full.bak` | mssql→arrow | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ndfcoverage_full.bak` | arrow→delta | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `ndfcoverage_full.bak` | delta→arrow | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ndfcoverage_full.bak` | arrow→pg_dir | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `ndfcoverage_full.bak` | pg_dir→arrow | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `nvarchar_max_u21_full.bak` | mssql→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `nvarchar_max_u21_full.bak` | arrow→delta | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `nvarchar_max_u21_full.bak` | delta→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `nvarchar_max_u21_full.bak` | arrow→pg_dir | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `nvarchar_max_u21_full.bak` | pg_dir→arrow | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `pagecomp_anchor_full.bak` | mssql→arrow | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | digest | ✓ |
| `pagecomp_anchor_full.bak` | arrow→delta | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | — | ✓ |
| `pagecomp_anchor_full.bak` | delta→arrow | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | digest | ✓ |
| `pagecomp_anchor_full.bak` | arrow→pg_dir | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | — | ✓ |
| `pagecomp_anchor_full.bak` | pg_dir→arrow | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | digest | ✓ |
| `pagecomp_long_prefix_full.bak` | mssql→arrow | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `pagecomp_long_prefix_full.bak` | arrow→delta | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `pagecomp_long_prefix_full.bak` | delta→arrow | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `pagecomp_long_prefix_full.bak` | arrow→pg_dir | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `pagecomp_long_prefix_full.bak` | pg_dir→arrow | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `pfor_columnstore_full.bak` | mssql→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_full.bak` | arrow→delta | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `pfor_columnstore_full.bak` | delta→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_full.bak` | arrow→pg_dir | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `pfor_columnstore_full.bak` | pg_dir→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_random_full.bak` | mssql→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_random_full.bak` | arrow→delta | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `pfor_columnstore_random_full.bak` | delta→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_random_full.bak` | arrow→pg_dir | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `pfor_columnstore_random_full.bak` | pg_dir→arrow | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `realworld_numeric_digest_full.bak` | mssql→arrow | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | digest | ✓ |
| `realworld_numeric_digest_full.bak` | arrow→delta | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | — | ✓ |
| `realworld_numeric_digest_full.bak` | delta→arrow | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | digest | ✓ |
| `realworld_numeric_digest_full.bak` | arrow→pg_dir | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | — | ✓ |
| `realworld_numeric_digest_full.bak` | pg_dir→arrow | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | digest | ✓ |
| `rowboundary_full.bak` | mssql→arrow | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `rowboundary_full.bak` | arrow→delta | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | — | ✓ |
| `rowboundary_full.bak` | delta→arrow | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `rowboundary_full.bak` | arrow→pg_dir | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | — | ✓ |
| `rowboundary_full.bak` | pg_dir→arrow | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `rowstore_hash_pii_full.bak` | mssql→arrow | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowstore_hash_pii_full.bak` | arrow→delta | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `rowstore_hash_pii_full.bak` | delta→arrow | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowstore_hash_pii_full.bak` | arrow→pg_dir | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `rowstore_hash_pii_full.bak` | pg_dir→arrow | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowstore_lob_image_full.bak` | mssql→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `rowstore_lob_image_full.bak` | arrow→delta | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | — | ✓ |
| `rowstore_lob_image_full.bak` | delta→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `rowstore_lob_image_full.bak` | arrow→pg_dir | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | — | ✓ |
| `rowstore_lob_image_full.bak` | pg_dir→arrow | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `rowstore_lob_markup_full.bak` | mssql→arrow | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowstore_lob_markup_full.bak` | arrow→delta | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `rowstore_lob_markup_full.bak` | delta→arrow | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowstore_lob_markup_full.bak` | arrow→pg_dir | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `rowstore_lob_markup_full.bak` | pg_dir→arrow | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `rowversion_extract_full.bak` | mssql→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `rowversion_extract_full.bak` | arrow→delta | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `rowversion_extract_full.bak` | delta→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `rowversion_extract_full.bak` | arrow→pg_dir | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `rowversion_extract_full.bak` | pg_dir→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `sparse_full.bak` | mssql→arrow | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `sparse_full.bak` | arrow→delta | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | — | ✓ |
| `sparse_full.bak` | delta→arrow | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `sparse_full.bak` | arrow→pg_dir | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | — | ✓ |
| `sparse_full.bak` | pg_dir→arrow | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | digest | ✓ |
| `spatial_edge_full.bak` | mssql→arrow | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `spatial_edge_full.bak` | arrow→delta | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `spatial_edge_full.bak` | delta→arrow | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `spatial_edge_full.bak` | arrow→pg_dir | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `spatial_edge_full.bak` | pg_dir→arrow | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `spatial_index_full.bak` | mssql→arrow | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `spatial_index_full.bak` | arrow→delta | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `spatial_index_full.bak` | delta→arrow | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `spatial_index_full.bak` | arrow→pg_dir | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `spatial_index_full.bak` | pg_dir→arrow | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `sql_variant_extract_full.bak` | mssql→arrow | 6 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | digest | ✓ |
| `sql_variant_extract_full.bak` | arrow→delta | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `sql_variant_extract_full.bak` | delta→arrow | 6 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | digest | ✓ |
| `sql_variant_extract_full.bak` | arrow→pg_dir | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `sql_variant_extract_full.bak` | pg_dir→arrow | 6 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | digest | ✓ |
| `striped_full_1.bak` | mssql→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `striped_full_1.bak` | arrow→delta | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `striped_full_1.bak` | delta→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `striped_full_1.bak` | arrow→pg_dir | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `striped_full_1.bak` | pg_dir→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `striped_single.bak` | mssql→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `striped_single.bak` | arrow→delta | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `striped_single.bak` | delta→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `striped_single.bak` | arrow→pg_dir | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `striped_single.bak` | pg_dir→arrow | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `surrogate_pairs_full.bak` | mssql→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `surrogate_pairs_full.bak` | arrow→delta | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `surrogate_pairs_full.bak` | delta→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `surrogate_pairs_full.bak` | arrow→pg_dir | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `surrogate_pairs_full.bak` | pg_dir→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `tabletype_cci_large_full.bak` | mssql→arrow | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest | ✓ |
| `tabletype_cci_large_full.bak` | arrow→delta | 1,200 | 25 | **1/1** | **25/25** | **50/50** | **1/1** | — | ✓ |
| `tabletype_cci_large_full.bak` | delta→arrow | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest | ✓ |
| `tabletype_cci_large_full.bak` | arrow→pg_dir | 1,200 | 25 | **1/1** | **25/25** | **50/50** | **1/1** | — | ✓ |
| `tabletype_cci_large_full.bak` | pg_dir→arrow | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest | ✓ |
| `tabletypecoverage_diff.bak` | mssql→arrow | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tabletypecoverage_diff.bak` | arrow→delta | 30 | 161 | **5/5** | **162/162** | **282/282** | **5/5** | — | ✓ |
| `tabletypecoverage_diff.bak` | delta→arrow | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tabletypecoverage_diff.bak` | arrow→pg_dir | 30 | 161 | **5/5** | **162/162** | **282/282** | **5/5** | — | ✓ |
| `tabletypecoverage_diff.bak` | pg_dir→arrow | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tabletypecoverage_full.bak` | mssql→arrow | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tabletypecoverage_full.bak` | arrow→delta | 20 | 161 | **5/5** | **162/162** | **282/282** | **5/5** | — | ✓ |
| `tabletypecoverage_full.bak` | delta→arrow | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tabletypecoverage_full.bak` | arrow→pg_dir | 20 | 161 | **5/5** | **162/162** | **282/282** | **5/5** | — | ✓ |
| `tabletypecoverage_full.bak` | pg_dir→arrow | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | digest | ✓ |
| `tde_full.bak` | — | — | — | — | — | — | — | — | ✓ |
| `temporal_hidden_full.bak` | mssql→arrow | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `temporal_hidden_full.bak` | arrow→delta | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `temporal_hidden_full.bak` | delta→arrow | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `temporal_hidden_full.bak` | arrow→pg_dir | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `temporal_hidden_full.bak` | pg_dir→arrow | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `torn_page_full.bak` | mssql→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `torn_page_full.bak` | arrow→delta | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `torn_page_full.bak` | delta→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `torn_page_full.bak` | arrow→pg_dir | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `torn_page_full.bak` | pg_dir→arrow | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `typecoverage_full.bak` | mssql→arrow | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | digest | ✓ |
| `typecoverage_full.bak` | arrow→delta | 162 | 101 | **34/34** | **101/101** | **202/202** | **34/34** | — | ✓ |
| `typecoverage_full.bak` | delta→arrow | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | digest | ✓ |
| `typecoverage_full.bak` | arrow→pg_dir | 162 | 101 | **34/34** | **101/101** | **202/202** | **34/34** | — | ✓ |
| `typecoverage_full.bak` | pg_dir→arrow | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | digest | ✓ |
| `typed_xml_full.bak` | mssql→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `typed_xml_full.bak` | arrow→delta | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `typed_xml_full.bak` | delta→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `typed_xml_full.bak` | arrow→pg_dir | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `typed_xml_full.bak` | pg_dir→arrow | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `unicode_codepage_coverage.bak` | mssql→arrow | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | digest | ✓ |
| `unicode_codepage_coverage.bak` | arrow→delta | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | — | ✓ |
| `unicode_codepage_coverage.bak` | delta→arrow | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | digest | ✓ |
| `unicode_codepage_coverage.bak` | arrow→pg_dir | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | — | ✓ |
| `unicode_codepage_coverage.bak` | pg_dir→arrow | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | digest | ✓ |
| `utf8_collation_full.bak` | mssql→arrow | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `utf8_collation_full.bak` | arrow→delta | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `utf8_collation_full.bak` | delta→arrow | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `utf8_collation_full.bak` | arrow→pg_dir | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `utf8_collation_full.bak` | pg_dir→arrow | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xml_index_full.bak` | mssql→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xml_index_full.bak` | arrow→delta | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `xml_index_full.bak` | delta→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xml_index_full.bak` | arrow→pg_dir | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `xml_index_full.bak` | pg_dir→arrow | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xmlcoverage_full.bak` | mssql→arrow | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `xmlcoverage_full.bak` | arrow→delta | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `xmlcoverage_full.bak` | delta→arrow | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `xmlcoverage_full.bak` | arrow→pg_dir | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | — | ✓ |
| `xmlcoverage_full.bak` | pg_dir→arrow | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `xmlheap_full.bak` | mssql→arrow | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | digest | ✓ |
| `xmlheap_full.bak` | arrow→delta | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | — | ✓ |
| `xmlheap_full.bak` | delta→arrow | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | digest | ✓ |
| `xmlheap_full.bak` | arrow→pg_dir | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | — | ✓ |
| `xmlheap_full.bak` | pg_dir→arrow | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | digest | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `archive_columnstore_partition_full.bak` — 2019 — ✗ fail

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 13.121 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_part_single` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_part_single` | columnstore | 140,000 | ✗ | — | — | ✗ | missing from output |

### `archive_columnstore_types_full.bak` — 2019 — ✗ fail

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_char10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_uuid` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_char10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_uuid` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✗ | — | — | ✗ | missing from output |

### `archive_columnstore_types_random_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `boundarycoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `catalog_ss2019.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_binary_varbinary_compare_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_bigint_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 41.148 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 8.121 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_highbase_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 8.121 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.363 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **4/4** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **4/4** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — ✓ pass

_SQL Server  · 0 MB_

_No non-empty tables._

### `cci_extended_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.238 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 9.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.426 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | columnstore | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | columnstore | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | columnstore | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.176 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.676 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.551 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `compressioncoverage_full.bak` — 2019 — ✗ fail

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ |  |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ |  |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ |  |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cmp_row_lob` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.cmp_row_variant` | rowstore | 9 | ✗ | — | — | ✗ | missing from output |
| `dbo.cmp_row_wide` | rowstore | 50 | ✗ | — | — | ✗ | missing from output |
| `dbo.cs_probe` | rowstore | 4 | ✗ | — | — | ✗ | missing from output |
| `dbo.fwd_heap` | rowstore | 2 | ✗ | — | — | ✗ | missing from output |
| `dbo.ghost_heap` | rowstore | 250 | ✗ | — | — | ✗ | missing from output |
| `dbo.sparse_cols` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |
| `dbo.uniquifier_none` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |
| `dbo.uniquifier_row` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cmp_row_lob` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.cmp_row_variant` | rowstore | 9 | ✗ | — | — | ✗ | missing from output |
| `dbo.cmp_row_wide` | rowstore | 50 | ✗ | — | — | ✗ | missing from output |
| `dbo.cs_probe` | rowstore | 4 | ✗ | — | — | ✗ | missing from output |
| `dbo.fwd_heap` | rowstore | 2 | ✗ | — | — | ✗ | missing from output |
| `dbo.ghost_heap` | rowstore | 250 | ✗ | — | — | ✗ | missing from output |
| `dbo.sparse_cols` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |
| `dbo.uniquifier_none` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |
| `dbo.uniquifier_row` | rowstore | 200 | ✗ | — | — | ✗ | missing from output |

### `computedcoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `constraintcoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.613 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `covering_index_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.574 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **3/3** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **3/3** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `delta_rowgroup_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_addcol.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `dirtycoverage_addnotnull.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `dirtycoverage_alldirty.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_altercol_rewrite.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_alterdb.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_delete.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.676 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete_v2.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete_v3.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **54/54** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **54/54** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete_v4.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update_v2.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update_v3.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **54/54** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **54/54** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update_v4.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_concurrent.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `dirtycoverage_createidx.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_createtable.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_delete.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_dropcol.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_dropidx.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_droptable.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_heap_forward.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_large_dirty.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_lob_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_maxrow.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_nchar_delete.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_nested.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_null_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_rebuildidx.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_insert.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_snapshot_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_switch.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.176 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_temporal_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_test_history` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_test_history` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_test_history` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_two_tx.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_uncommitted.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `dirtycoverage_update.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `filtered_ncci_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.426 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `forwarded_records_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 15.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ghost_records_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 12.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `high_slot_density_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.055 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `identity_coverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.238 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_02.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_03.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_04.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_05.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_06.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `incrementalcoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `layoutcoverage_full.bak` — 2019 — ✗ fail

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 8.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ | cells digest ✓ |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ |  |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ |  |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ |  |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ |  |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ | cells digest ✓ |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ |  |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ |  |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ |  |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ |  |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ | cells digest ✓ |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✗ | — | — | ✗ | missing from output |

### `max_row_width_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `mixed_collation_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `multi_rowgroup_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.238 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ndfcoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `nvarchar_max_u21_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `pagecomp_anchor_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.176 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |

### `pagecomp_long_prefix_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `pfor_columnstore_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.121 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.121 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |

### `rowboundary_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `rowstore_lob_image_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `rowstore_lob_markup_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `rowversion_extract_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `sparse_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `spatial_edge_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `spatial_index_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.926 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `sql_variant_extract_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |

### `striped_full_1.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.266 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `striped_single.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.434 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `surrogate_pairs_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `tabletype_cci_large_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **50/50** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **50/50** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **35/35** | **58/58** | ✓ |  |
| `dbo.tt_column` | columnstore | 6 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **35/35** | **58/58** | ✓ |  |
| `dbo.tt_column` | columnstore | 6 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **58/58** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

### `tabletypecoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **35/35** | **58/58** | ✓ |  |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **35/35** | **58/58** | ✓ |  |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **58/58** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |

### `tde_full.bak` — ✓ pass

_SQL Server  · 0 MB_

_No non-empty tables._

### `temporal_hidden_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `typecoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.676 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `typed_xml_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `unicode_codepage_coverage.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.363 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `utf8_collation_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `xml_index_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `xmlcoverage_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `xmlheap_full.bak` — 2019 — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.801 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |


## Metadata validation

Metadata ground truth is collected from the live SQL Server restore into `<bak>.metadata.json` by `python -m tools.fixture_run register-metadata-all`. Only fixtures with a sidecar are scored here; others show `—` (unscored).

| Backup | constraints | indexes | extended_properties | modules | schema_objects | security | statistics | plan_guides | query_store |
|--------|:---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------:|
| `alias_types_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archive_columnstore_partition_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archive_columnstore_types_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archive_columnstore_types_random_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archive_single_chunk_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archive_single_chunk_random_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `archivenull_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `backup_blocksize_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `boundarycoverage_datetime_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `boundarycoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `catalog_ss2019.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_binary_varbinary_compare_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_btree_nci_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_computed_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_enc5_largepool_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_extended_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_lob_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_reorganize_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_string_dict_regression_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_string_minmax_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_switch_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_types_large_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_varbinary_micro_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_varbinary_probe_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `columnstore_minimal.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `compressed_nvarchar_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `compressioncoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `computedcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `constraintcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `covering_index_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cs_lob_preamble.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `delta_rowgroup_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_aborted_xact.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_addcol.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_addnotnull.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_alldirty.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_altercol.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_alterdb.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_cci_delete.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_cci_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_delete.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_update_v2.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_update_v3.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_committed_update_v4.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_concurrent.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_createidx.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_createtable.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_delete.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_dropcol.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_dropidx.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_droptable.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_heap_forward.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_large_dirty.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_lob_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_maxrow.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_nchar_delete.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_nested.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_null_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_rebuildidx.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_rich_insert.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_rich_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_savepoint.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_snapshot_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_switch.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_temporal_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_truncate.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_two_tx.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_uncommitted.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dirtycoverage_update.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `filtered_ncci_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `float_extreme_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `forwarded_records_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ghost_records_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `heapcoverage_large.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `heapcoverage_large_50000.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `hierarchyid_extract_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `high_slot_density_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `identity_coverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_01.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_02.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_03.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_04.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_05.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_diff_06.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incrementalcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `layoutcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `max_row_width_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `mixed_collation_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `multi_rowgroup_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ncci_heap_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ncci_types_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ndfcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `nvarchar_max_u21_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pagecomp_anchor_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pagecomp_long_prefix_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pfor_columnstore_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pfor_columnstore_random_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `realworld_numeric_digest_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rowboundary_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rowstore_hash_pii_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rowstore_lob_image_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rowstore_lob_markup_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rowversion_extract_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `sparse_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spatial_edge_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `spatial_index_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `sql_variant_extract_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `striped_full_1.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `striped_single.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `surrogate_pairs_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tabletype_cci_large_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tabletypecoverage_diff.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tabletypecoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `temporal_hidden_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `torn_page_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `typecoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `typed_xml_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `unicode_codepage_coverage.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `utf8_collation_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `xml_index_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `xmlcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `xmlheap_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `alias_types_full.bak` | 0.22s | 0.629s | 0.849s |
| `archive_columnstore_partition_full.bak` | 3.772s | 1.833s | 5.605s |
| `archive_columnstore_types_full.bak` | 1.705s | 0.923s | 2.628s |
| `archive_columnstore_types_random_full.bak` | 1.752s | 2.588s | 4.34s |
| `archive_single_chunk_full.bak` | 0.336s | 0.7s | 1.036s |
| `archive_single_chunk_random_full.bak` | 0.335s | 0.446s | 0.781s |
| `archivenull_full.bak` | 0.542s | 0.777s | 1.319s |
| `backup_blocksize_full.bak` | 0.284s | 0.767s | 1.051s |
| `boundarycoverage_datetime_full.bak` | 1.894s | 1.673s | 3.567s |
| `boundarycoverage_full.bak` | 0.295s | 0.461s | 0.756s |
| `catalog_ss2019.bak` | 0.213s | 0.732s | 0.945s |
| `cci_binary_varbinary_compare_full.bak` | 0.267s | 0.611s | 0.878s |
| `cci_bitpack_probe_bigint_full.bak` | 5.196s | 3.642s | 8.838s |
| `cci_bitpack_probe_full.bak` | 0.893s | 1.411s | 2.304s |
| `cci_bitpack_probe_highbase_full.bak` | 0.439s | 0.512s | 0.951s |
| `cci_btree_nci_full.bak` | 0.602s | 0.661s | 1.263s |
| `cci_computed_full.bak` | 0.293s | 0.724s | 1.017s |
| `cci_enc5_largepool_full.bak` | 1.565s | 1.154s | 2.719s |
| `cci_extended_full.bak` | 0.459s | 0.346s | 0.805s |
| `cci_lob_full.bak` | 0.3s | 0.638s | 0.938s |
| `cci_reorganize_full.bak` | 0.665s | 0.665s | 1.33s |
| `cci_string_dict_regression_full.bak` | 1.44s | 0.862s | 2.302s |
| `cci_string_minmax_full.bak` | 0.266s | 0.698s | 0.964s |
| `cci_switch_full.bak` | 0.41s | 0.74s | 1.15s |
| `cci_types_large_full.bak` | 0.295s | 0.894s | 1.189s |
| `cci_varbinary_micro_full.bak` | 0.169s | 0.397s | 0.566s |
| `cci_varbinary_probe_full.bak` | 0.368s | 0.742s | 1.11s |
| `columnstore_minimal.bak` | 9.88s | 7.722s | 17.602s |
| `compressed_nvarchar_full.bak` | 0.232s | 0.605s | 0.837s |
| `compressioncoverage_full.bak` | 1.045s | 1.941s | 2.986s |
| `computedcoverage_full.bak` | 0.246s | 0.681s | 0.927s |
| `constraintcoverage_full.bak` | 0.364s | 0.68s | 1.044s |
| `covering_index_full.bak` | 0.244s | 0.634s | 0.878s |
| `cs_lob_preamble.bak` | 0.288s | 0.805s | 1.093s |
| `delta_rowgroup_full.bak` | 0.236s | 0.81s | 1.046s |
| `dirtycoverage_aborted_xact.bak` | 0.386s | 0.544s | 0.93s |
| `dirtycoverage_addcol.bak` | 0.189s | 0.541s | 0.73s |
| `dirtycoverage_addnotnull.bak` | 0.255s | 0.76s | 1.015s |
| `dirtycoverage_alldirty.bak` | 0.28s | 0.368s | 0.648s |
| `dirtycoverage_altercol.bak` | 0.244s | 0.56s | 0.804s |
| `dirtycoverage_altercol_rewrite.bak` | 0.236s | 0.544s | 0.78s |
| `dirtycoverage_alterdb.bak` | 0.189s | 0.716s | 0.905s |
| `dirtycoverage_cci_delete.bak` | 0.595s | 0.526s | 1.121s |
| `dirtycoverage_cci_update.bak` | 1.453s | 0.779s | 2.232s |
| `dirtycoverage_committed_delete.bak` | 0.312s | 0.54s | 0.852s |
| `dirtycoverage_committed_delete_v2.bak` | 0.295s | 0.567s | 0.862s |
| `dirtycoverage_committed_delete_v3.bak` | 0.438s | 0.753s | 1.191s |
| `dirtycoverage_committed_delete_v4.bak` | 0.743s | 0.808s | 1.551s |
| `dirtycoverage_committed_update.bak` | 0.303s | 0.493s | 0.796s |
| `dirtycoverage_committed_update_v2.bak` | 0.294s | 0.623s | 0.917s |
| `dirtycoverage_committed_update_v3.bak` | 0.451s | 0.824s | 1.275s |
| `dirtycoverage_committed_update_v4.bak` | 0.868s | 0.742s | 1.61s |
| `dirtycoverage_concurrent.bak` | 0.198s | 0.666s | 0.864s |
| `dirtycoverage_createidx.bak` | 0.211s | 0.554s | 0.765s |
| `dirtycoverage_createtable.bak` | 0.291s | 0.617s | 0.908s |
| `dirtycoverage_delete.bak` | 0.35s | 0.689s | 1.039s |
| `dirtycoverage_dropcol.bak` | 0.258s | 0.603s | 0.861s |
| `dirtycoverage_dropidx.bak` | 0.259s | 0.569s | 0.828s |
| `dirtycoverage_droptable.bak` | 0.238s | 0.756s | 0.994s |
| `dirtycoverage_heap_forward.bak` | 0.384s | 0.602s | 0.986s |
| `dirtycoverage_large_dirty.bak` | 1.143s | 0.601s | 1.744s |
| `dirtycoverage_lob_update.bak` | 0.392s | 0.614s | 1.006s |
| `dirtycoverage_maxrow.bak` | 0.256s | 0.677s | 0.933s |
| `dirtycoverage_nchar_delete.bak` | 0.208s | 0.672s | 0.88s |
| `dirtycoverage_nested.bak` | 0.335s | 0.679s | 1.014s |
| `dirtycoverage_null_update.bak` | 0.316s | 0.54s | 0.856s |
| `dirtycoverage_rebuildidx.bak` | 0.287s | 0.59s | 0.877s |
| `dirtycoverage_rich_insert.bak` | 0.553s | 0.518s | 1.071s |
| `dirtycoverage_rich_update.bak` | 0.494s | 0.491s | 0.985s |
| `dirtycoverage_savepoint.bak` | 0.358s | 0.654s | 1.012s |
| `dirtycoverage_snapshot_update.bak` | 0.324s | 0.597s | 0.921s |
| `dirtycoverage_switch.bak` | 0.235s | 0.663s | 0.898s |
| `dirtycoverage_temporal_update.bak` | 0.449s | 0.524s | 0.973s |
| `dirtycoverage_truncate.bak` | 0.203s | 0.577s | 0.78s |
| `dirtycoverage_two_tx.bak` | 0.331s | 0.622s | 0.953s |
| `dirtycoverage_uncommitted.bak` | 0.354s | 0.478s | 0.832s |
| `dirtycoverage_update.bak` | 0.336s | 0.598s | 0.934s |
| `filtered_ncci_full.bak` | 0.32s | 0.619s | 0.939s |
| `float_extreme_full.bak` | 0.232s | 0.507s | 0.739s |
| `forwarded_records_full.bak` | 0.601s | 0.548s | 1.149s |
| `ghost_records_full.bak` | 0.349s | 0.559s | 0.908s |
| `heapcoverage_large.bak` | 0.322s | 0.681s | 1.003s |
| `heapcoverage_large_50000.bak` | 0.8s | 1.176s | 1.976s |
| `hierarchyid_extract_full.bak` | 0.209s | 0.495s | 0.704s |
| `high_slot_density_full.bak` | 0.354s | 0.728s | 1.082s |
| `identity_coverage_full.bak` | 0.314s | 0.75s | 1.064s |
| `incrementalcoverage_diff_01.bak` | 0.498s | 0.575s | 1.073s |
| `incrementalcoverage_diff_02.bak` | 0.361s | 0.678s | 1.039s |
| `incrementalcoverage_diff_03.bak` | 0.329s | 0.551s | 0.88s |
| `incrementalcoverage_diff_04.bak` | 0.331s | 0.797s | 1.128s |
| `incrementalcoverage_diff_05.bak` | 0.318s | 0.711s | 1.029s |
| `incrementalcoverage_diff_06.bak` | 0.307s | 0.5s | 0.807s |
| `incrementalcoverage_full.bak` | 0.2s | 0.631s | 0.831s |
| `layoutcoverage_full.bak` | 1.897s | 4.575s | 6.472s |
| `max_row_width_full.bak` | 0.2s | 0.563s | 0.763s |
| `mixed_collation_full.bak` | 0.196s | 0.566s | 0.762s |
| `multi_rowgroup_full.bak` | 0.379s | 0.636s | 1.015s |
| `ncci_heap_full.bak` | 0.269s | 0.93s | 1.199s |
| `ncci_types_full.bak` | 1.33s | 2.007s | 3.337s |
| `ndfcoverage_full.bak` | 0.279s | 0.654s | 0.933s |
| `nvarchar_max_u21_full.bak` | 0.229s | 0.738s | 0.967s |
| `pagecomp_anchor_full.bak` | 0.933s | 0.711s | 1.644s |
| `pagecomp_long_prefix_full.bak` | 0.269s | 0.572s | 0.841s |
| `pfor_columnstore_full.bak` | 0.982s | 1.738s | 2.72s |
| `pfor_columnstore_random_full.bak` | 1.117s | 1.843s | 2.96s |
| `realworld_numeric_digest_full.bak` | 0.454s | 0.946s | 1.4s |
| `rowboundary_full.bak` | 0.362s | 0.53s | 0.892s |
| `rowstore_hash_pii_full.bak` | 0.237s | 0.762s | 0.999s |
| `rowstore_lob_image_full.bak` | 0.198s | 0.546s | 0.744s |
| `rowstore_lob_markup_full.bak` | 0.347s | 0.609s | 0.956s |
| `rowversion_extract_full.bak` | 0.335s | 0.576s | 0.911s |
| `sparse_full.bak` | 0.52s | 0.746s | 1.266s |
| `spatial_edge_full.bak` | 0.219s | 0.706s | 0.925s |
| `spatial_index_full.bak` | 0.231s | 0.675s | 0.906s |
| `sql_variant_extract_full.bak` | 0.21s | 0.644s | 0.854s |
| `striped_full_1.bak` | 0.389s | 0.589s | 0.978s |
| `striped_single.bak` | 0.268s | 0.582s | 0.85s |
| `surrogate_pairs_full.bak` | 0.265s | 0.562s | 0.827s |
| `tabletype_cci_large_full.bak` | 0.557s | 1.059s | 1.616s |
| `tabletypecoverage_diff.bak` | 0.758s | 2.04s | 2.798s |
| `tabletypecoverage_full.bak` | 0.754s | 1.533s | 2.287s |
| `tde_full.bak` | 0s | 0.054s | 0.054s |
| `temporal_hidden_full.bak` | 0.889s | 0.593s | 1.482s |
| `torn_page_full.bak` | 0.166s | 0.608s | 0.774s |
| `typecoverage_full.bak` | 0.697s | 2.316s | 3.013s |
| `typed_xml_full.bak` | 0.26s | 0.61s | 0.87s |
| `unicode_codepage_coverage.bak` | 0.55s | 1.27s | 1.82s |
| `utf8_collation_full.bak` | 0.275s | 0.724s | 0.999s |
| `xml_index_full.bak` | 0.28s | 0.809s | 1.089s |
| `xmlcoverage_full.bak` | 0.177s | 0.623s | 0.8s |
| `xmlheap_full.bak` | 0.454s | 0.7s | 1.154s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis). See **Sink read breakdown** below for the per-phase split._

## Extract phase breakdown

| Backup | pagestore | schema | catalog | constraints | logtail | xtp | data decode (net) | sink write | arrow verify | sink finish |
|--------|----------:|-------:|--------:|------------:|--------:|---:|------------------:|-----------:|-------------:|------------:|
| `alias_types_full.bak` | 0.046s | 0.043s | 0.0s | 0.0s | 0.004s | 0.0s | 0.01s | 0.038s | 0.029s | 0.039s |
| `archive_columnstore_partition_full.bak` | 0.088s | 0.032s | 0.0s | 0.0s | 0.024s | 0.0s | 3.312s | 0.855s | 0.36s | 0.057s |
| `archive_columnstore_types_full.bak` | 0.068s | 0.05s | 0.0s | 0.0s | 0.006s | 0.0s | 1.466s | 0.469s | 0.687s | 0.056s |
| `archive_columnstore_types_random_full.bak` | 0.117s | 0.108s | 0.0s | 0.0s | 0.013s | 0.0s | 1.281s | 0.649s | 0.763s | 0.221s |
| `archive_single_chunk_full.bak` | 0.038s | 0.028s | 0.0s | 0.0s | 0.091s | 0.0s | 0.033s | 0.059s | 0.045s | 0.059s |
| `archive_single_chunk_random_full.bak` | 0.04s | 0.132s | 0.0s | 0.0s | 0.009s | 0.0s | 0.061s | 0.081s | 0.076s | 0.081s |
| `archivenull_full.bak` | 0.047s | 0.059s | 0.0s | 0.0s | 0.01s | 0.0s | 0.233s | 0.076s | 0.063s | 0.114s |
| `backup_blocksize_full.bak` | 0.049s | 0.063s | 0.0s | 0.0s | 0.013s | 0.0s | 0.114s | 0.121s | 0.11s | 0.022s |
| `boundarycoverage_datetime_full.bak` | 0.065s | 0.089s | 0.0s | 0.0s | 0.02s | 0.0s | 1.579s | 1.51s | 0.82s | 0.077s |
| `boundarycoverage_full.bak` | 0.044s | 0.026s | 0.0s | 0.0s | 0.011s | 0.0s | 0.134s | 0.178s | 0.03s | 0.07s |
| `catalog_ss2019.bak` | 0.057s | 0.028s | 0.0s | 0.0s | 0.009s | 0.0s | 0.001s | 0.029s | 0.025s | 0.03s |
| `cci_binary_varbinary_compare_full.bak` | 0.037s | 0.142s | 0.0s | 0.0s | 0.003s | 0.0s | 0.023s | 0.028s | 0.03s | 0.047s |
| `cci_bitpack_probe_bigint_full.bak` | 0.202s | 0.028s | 0.0s | 0.0s | 1.512s | 0.0s | 2.978s | 2.498s | 1.847s | 0.439s |
| `cci_bitpack_probe_full.bak` | 0.055s | 0.075s | 0.0s | 0.0s | 0.023s | 0.0s | 0.611s | 0.132s | 0.459s | 0.084s |
| `cci_bitpack_probe_highbase_full.bak` | 0.07s | 0.105s | 0.0s | 0.0s | 0.015s | 0.0s | 0.187s | 0.099s | 0.114s | 0.05s |
| `cci_btree_nci_full.bak` | 0.04s | 0.328s | 0.0s | 0.0s | 0.009s | 0.0s | 0.199s | 0.028s | 0.051s | 0.015s |
| `cci_computed_full.bak` | 0.042s | 0.086s | 0.0s | 0.0s | 0.012s | 0.0s | 0.058s | 0.051s | 0.038s | 0.01s |
| `cci_enc5_largepool_full.bak` | 0.057s | 0.059s | 0.0s | 0.0s | 0.016s | 0.0s | 1.379s | 0.135s | 0.451s | 0.02s |
| `cci_extended_full.bak` | 0.079s | 0.049s | 0.0s | 0.0s | 0.014s | 0.0s | 0.146s | 0.173s | 0.026s | 0.075s |
| `cci_lob_full.bak` | 0.04s | 0.104s | 0.0s | 0.0s | 0.012s | 0.0s | 0.1s | 0.078s | 0.047s | 0.026s |
| `cci_reorganize_full.bak` | 0.041s | 0.148s | 0.0s | 0.0s | 0.061s | 0.0s | 0.278s | 0.137s | 0.102s | 0.028s |
| `cci_string_dict_regression_full.bak` | 0.089s | 0.024s | 0.0s | 0.0s | 0.032s | 0.0s | 1.209s | 0.096s | 0.32s | 0.035s |
| `cci_string_minmax_full.bak` | 0.061s | 0.079s | 0.0s | 0.0s | 0.017s | 0.0s | 0.046s | 0.07s | 0.019s | 0.052s |
| `cci_switch_full.bak` | 0.066s | 0.092s | 0.0s | 0.0s | 0.014s | 0.0s | 0.105s | 0.082s | 0.033s | 0.099s |
| `cci_types_large_full.bak` | 0.038s | 0.08s | 0.0s | 0.0s | 0.014s | 0.0s | 0.144s | 0.099s | 0.031s | 0.01s |
| `cci_varbinary_micro_full.bak` | 0.042s | 0.022s | 0.0s | 0.0s | 0.015s | 0.0s | 0.057s | 0.064s | 0.022s | 0.023s |
| `cci_varbinary_probe_full.bak` | 0.098s | 0.061s | 0.0s | 0.0s | 0.013s | 0.0s | 0.127s | 0.111s | 0.114s | 0.061s |
| `columnstore_minimal.bak` | 0.052s | 0.053s | 0.0s | 0.0s | 0.014s | 0.0s | 1.551s | 8.986s | 6.639s | 8.188s |
| `compressed_nvarchar_full.bak` | 0.094s | 0.087s | 0.0s | 0.0s | 0.009s | 0.0s | 0.001s | 0.034s | 0.025s | 0.034s |
| `compressioncoverage_full.bak` | 0.041s | 0.061s | 0.0s | 0.0s | 0.014s | 0.0s | 0.882s | 0.572s | 0.577s | 0.022s |
| `computedcoverage_full.bak` | 0.04s | 0.035s | 0.0s | 0.0s | 0.111s | 0.0s | 0.034s | 0.051s | 0.028s | 0.019s |
| `constraintcoverage_full.bak` | 0.039s | 0.031s | 0.0s | 0.0s | 0.009s | 0.0s | 0.158s | 0.175s | 0.054s | 0.039s |
| `covering_index_full.bak` | 0.035s | 0.108s | 0.0s | 0.0s | 0.015s | 0.0s | 0.064s | 0.049s | 0.056s | 0.017s |
| `cs_lob_preamble.bak` | 0.09s | 0.049s | 0.0s | 0.0s | 0.005s | 0.0s | 0.078s | 0.03s | 0.02s | 0.03s |
| `delta_rowgroup_full.bak` | 0.048s | 0.052s | 0.0s | 0.0s | 0.019s | 0.0s | 0.044s | 0.06s | 0.019s | 0.038s |
| `dirtycoverage_aborted_xact.bak` | 0.043s | 0.172s | 0.0s | 0.0s | 0.111s | 0.0s | 0.013s | 0.032s | 0.029s | 0.032s |
| `dirtycoverage_addcol.bak` | 0.032s | 0.067s | 0.0s | 0.0s | 0.013s | 0.0s | 0.007s | 0.022s | 0.021s | 0.045s |
| `dirtycoverage_addnotnull.bak` | 0.04s | 0.04s | 0.0s | 0.0s | 0.011s | 0.0s | 0.03s | 0.062s | 0.089s | 0.09s |
| `dirtycoverage_alldirty.bak` | 0.044s | 0.085s | 0.0s | 0.0s | 0.072s | 0.0s | 0.015s | 0.007s | 0.0s | 0.015s |
| `dirtycoverage_altercol.bak` | 0.043s | 0.125s | 0.0s | 0.0s | 0.018s | 0.0s | 0.001s | 0.036s | 0.033s | 0.037s |
| `dirtycoverage_altercol_rewrite.bak` | 0.038s | 0.115s | 0.0s | 0.0s | 0.024s | 0.0s | 0.002s | 0.038s | 0.034s | 0.039s |
| `dirtycoverage_alterdb.bak` | 0.039s | 0.066s | 0.0s | 0.0s | 0.013s | 0.0s | 0.002s | 0.03s | 0.024s | 0.06s |
| `dirtycoverage_cci_delete.bak` | 0.07s | 0.054s | 0.0s | 0.0s | 0.16s | 0.0s | 0.285s | 0.129s | 0.174s | 0.017s |
| `dirtycoverage_cci_update.bak` | 0.087s | 0.064s | 0.0s | 0.0s | 0.517s | 0.0s | 0.746s | 0.144s | 0.167s | 0.026s |
| `dirtycoverage_committed_delete.bak` | 0.034s | 0.134s | 0.0s | 0.0s | 0.008s | 0.0s | 0.001s | 0.083s | 0.122s | 0.125s |
| `dirtycoverage_committed_delete_v2.bak` | 0.034s | 0.085s | 0.0s | 0.0s | 0.023s | 0.0s | 0.012s | 0.081s | 0.089s | 0.093s |
| `dirtycoverage_committed_delete_v3.bak` | 0.078s | 0.068s | 0.0s | 0.0s | 0.009s | 0.0s | 0.066s | 0.079s | 0.201s | 0.209s |
| `dirtycoverage_committed_delete_v4.bak` | 0.04s | 0.111s | 0.0s | 0.0s | 0.275s | 0.0s | 0.302s | 0.03s | 0.211s | 0.008s |
| `dirtycoverage_committed_update.bak` | 0.038s | 0.04s | 0.0s | 0.0s | 0.018s | 0.0s | 0.005s | 0.041s | 0.05s | 0.088s |
| `dirtycoverage_committed_update_v2.bak` | 0.066s | 0.121s | 0.0s | 0.0s | 0.011s | 0.0s | 0.002s | 0.029s | 0.022s | 0.029s |
| `dirtycoverage_committed_update_v3.bak` | 0.037s | 0.083s | 0.0s | 0.0s | 0.017s | 0.0s | 0.018s | 0.113s | 0.234s | 0.275s |
| `dirtycoverage_committed_update_v4.bak` | 0.087s | 0.101s | 0.0s | 0.0s | 0.22s | 0.0s | 0.439s | 0.047s | 0.268s | 0.01s |
| `dirtycoverage_concurrent.bak` | 0.039s | 0.087s | 0.0s | 0.0s | 0.012s | 0.0s | 0.003s | 0.028s | 0.023s | 0.029s |
| `dirtycoverage_createidx.bak` | 0.039s | 0.064s | 0.0s | 0.0s | 0.013s | 0.0s | 0.002s | 0.058s | 0.067s | 0.071s |
| `dirtycoverage_createtable.bak` | 0.044s | 0.098s | 0.0s | 0.0s | 0.035s | 0.0s | 0.016s | 0.067s | 0.075s | 0.079s |
| `dirtycoverage_delete.bak` | 0.04s | 0.098s | 0.0s | 0.0s | 0.106s | 0.0s | 0.024s | 0.044s | 0.059s | 0.06s |
| `dirtycoverage_dropcol.bak` | 0.036s | 0.026s | 0.0s | 0.0s | 0.073s | 0.0s | 0.002s | 0.022s | 0.023s | 0.047s |
| `dirtycoverage_dropidx.bak` | 0.065s | 0.101s | 0.0s | 0.0s | 0.007s | 0.0s | 0.004s | 0.053s | 0.047s | 0.053s |
| `dirtycoverage_droptable.bak` | 0.039s | 0.066s | 0.0s | 0.0s | 0.021s | 0.0s | 0.072s | 0.04s | 0.068s | 0.018s |
| `dirtycoverage_heap_forward.bak` | 0.044s | 0.138s | 0.0s | 0.0s | 0.07s | 0.0s | 0.009s | 0.075s | 0.115s | 0.118s |
| `dirtycoverage_large_dirty.bak` | 0.04s | 0.098s | 0.0s | 0.0s | 0.942s | 0.0s | 0.007s | 0.024s | 0.04s | 0.041s |
| `dirtycoverage_lob_update.bak` | 0.038s | 0.104s | 0.0s | 0.0s | 0.169s | 0.0s | 0.004s | 0.047s | 0.032s | 0.048s |
| `dirtycoverage_maxrow.bak` | 0.053s | 0.121s | 0.0s | 0.0s | 0.021s | 0.0s | 0.004s | 0.049s | 0.039s | 0.049s |
| `dirtycoverage_nchar_delete.bak` | 0.036s | 0.035s | 0.0s | 0.0s | 0.041s | 0.0s | 0.005s | 0.078s | 0.031s | 0.081s |
| `dirtycoverage_nested.bak` | 0.052s | 0.132s | 0.0s | 0.0s | 0.096s | 0.0s | 0.004s | 0.028s | 0.023s | 0.028s |
| `dirtycoverage_null_update.bak` | 0.041s | 0.138s | 0.0s | 0.0s | 0.067s | 0.0s | 0.003s | 0.041s | 0.03s | 0.041s |
| `dirtycoverage_rebuildidx.bak` | 0.042s | 0.133s | 0.0s | 0.0s | 0.011s | 0.0s | 0.002s | 0.023s | 0.021s | 0.09s |
| `dirtycoverage_rich_insert.bak` | 0.037s | 0.109s | 0.0s | 0.0s | 0.072s | 0.0s | 0.001s | 0.048s | 0.318s | 0.32s |
| `dirtycoverage_rich_update.bak` | 0.045s | 0.079s | 0.0s | 0.0s | 0.079s | 0.0s | 0.003s | 0.062s | 0.272s | 0.278s |
| `dirtycoverage_savepoint.bak` | 0.037s | 0.148s | 0.0s | 0.0s | 0.052s | 0.0s | 0.055s | 0.02s | 0.031s | 0.052s |
| `dirtycoverage_snapshot_update.bak` | 0.041s | 0.119s | 0.0s | 0.0s | 0.092s | 0.0s | 0.002s | 0.058s | 0.06s | 0.063s |
| `dirtycoverage_switch.bak` | 0.038s | 0.105s | 0.0s | 0.0s | 0.012s | 0.0s | 0.034s | 0.052s | 0.028s | 0.023s |
| `dirtycoverage_temporal_update.bak` | 0.046s | 0.078s | 0.0s | 0.0s | 0.074s | 0.0s | 0.206s | 0.059s | 0.196s | 0.002s |
| `dirtycoverage_truncate.bak` | 0.041s | 0.091s | 0.0s | 0.0s | 0.013s | 0.0s | 0.005s | 0.025s | 0.02s | 0.026s |
| `dirtycoverage_two_tx.bak` | 0.055s | 0.024s | 0.0s | 0.0s | 0.097s | 0.0s | 0.003s | 0.028s | 0.059s | 0.063s |
| `dirtycoverage_uncommitted.bak` | 0.038s | 0.049s | 0.0s | 0.0s | 0.174s | 0.0s | 0.01s | 0.018s | 0.039s | 0.053s |
| `dirtycoverage_update.bak` | 0.037s | 0.029s | 0.0s | 0.0s | 0.095s | 0.0s | 0.005s | 0.037s | 0.095s | 0.111s |
| `filtered_ncci_full.bak` | 0.042s | 0.104s | 0.0s | 0.0s | 0.021s | 0.0s | 0.134s | 0.059s | 0.037s | 0.012s |
| `float_extreme_full.bak` | 0.055s | 0.073s | 0.0s | 0.0s | 0.015s | 0.0s | 0.001s | 0.077s | 0.069s | 0.078s |
| `forwarded_records_full.bak` | 0.059s | 0.103s | 0.0s | 0.0s | 0.02s | 0.0s | 0.158s | 0.082s | 0.269s | 0.222s |
| `ghost_records_full.bak` | 0.043s | 0.035s | 0.0s | 0.0s | 0.012s | 0.0s | 0.003s | 0.037s | 0.104s | 0.105s |
| `heapcoverage_large.bak` | 0.055s | 0.123s | 0.0s | 0.0s | 0.005s | 0.0s | 0.073s | 0.088s | 0.122s | 0.062s |
| `heapcoverage_large_50000.bak` | 0.083s | 0.1s | 0.0s | 0.0s | 0.017s | 0.0s | 0.266s | 0.095s | 0.405s | 0.324s |
| `hierarchyid_extract_full.bak` | 0.053s | 0.074s | 0.0s | 0.0s | 0.014s | 0.0s | 0.009s | 0.028s | 0.023s | 0.028s |
| `high_slot_density_full.bak` | 0.092s | 0.101s | 0.0s | 0.0s | 0.011s | 0.0s | 0.051s | 0.067s | 0.106s | 0.089s |
| `identity_coverage_full.bak` | 0.041s | 0.101s | 0.0s | 0.0s | 0.01s | 0.0s | 0.106s | 0.091s | 0.068s | 0.035s |
| `incrementalcoverage_diff_01.bak` | 0.211s | 0.191s | 0.0s | 0.0s | 0.045s | 0.0s | 0.001s | 0.032s | 0.026s | 0.032s |
| `incrementalcoverage_diff_02.bak` | 0.153s | 0.114s | 0.0s | 0.0s | 0.052s | 0.0s | 0.001s | 0.023s | 0.021s | 0.025s |
| `incrementalcoverage_diff_03.bak` | 0.2s | 0.033s | 0.0s | 0.0s | 0.02s | 0.0s | 0.002s | 0.023s | 0.019s | 0.023s |
| `incrementalcoverage_diff_04.bak` | 0.156s | 0.069s | 0.0s | 0.0s | 0.013s | 0.0s | 0.001s | 0.041s | 0.062s | 0.064s |
| `incrementalcoverage_diff_05.bak` | 0.144s | 0.057s | 0.0s | 0.0s | 0.021s | 0.0s | 0.001s | 0.084s | 0.024s | 0.084s |
| `incrementalcoverage_diff_06.bak` | 0.135s | 0.054s | 0.0s | 0.0s | 0.045s | 0.0s | 0.001s | 0.058s | 0.052s | 0.058s |
| `incrementalcoverage_full.bak` | 0.049s | 0.088s | 0.0s | 0.0s | 0.003s | 0.0s | 0.003s | 0.027s | 0.028s | 0.031s |
| `layoutcoverage_full.bak` | 0.063s | 0.206s | 0.0s | 0.0s | 0.013s | 0.0s | 1.561s | 1.155s | 0.402s | 0.017s |
| `max_row_width_full.bak` | 0.045s | 0.104s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.035s | 0.021s | 0.035s |
| `mixed_collation_full.bak` | 0.043s | 0.035s | 0.0s | 0.0s | 0.01s | 0.0s | 0.004s | 0.053s | 0.028s | 0.091s |
| `multi_rowgroup_full.bak` | 0.181s | 0.037s | 0.0s | 0.0s | 0.013s | 0.0s | 0.068s | 0.043s | 0.035s | 0.041s |
| `ncci_heap_full.bak` | 0.041s | 0.159s | 0.0s | 0.0s | 0.007s | 0.0s | 0.023s | 0.047s | 0.02s | 0.028s |
| `ncci_types_full.bak` | 0.051s | 0.027s | 0.0s | 0.0s | 0.019s | 0.0s | 1.148s | 1.145s | 0.662s | 0.03s |
| `ndfcoverage_full.bak` | 0.04s | 0.126s | 0.0s | 0.0s | 0.012s | 0.0s | 0.068s | 0.064s | 0.066s | 0.02s |
| `nvarchar_max_u21_full.bak` | 0.039s | 0.141s | 0.0s | 0.0s | 0.012s | 0.0s | 0.002s | 0.025s | 0.02s | 0.025s |
| `pagecomp_anchor_full.bak` | 0.042s | 0.122s | 0.0s | 0.0s | 0.009s | 0.0s | 0.361s | 0.055s | 0.322s | 0.326s |
| `pagecomp_long_prefix_full.bak` | 0.042s | 0.108s | 0.0s | 0.0s | 0.008s | 0.0s | 0.001s | 0.093s | 0.089s | 0.094s |
| `pfor_columnstore_full.bak` | 0.042s | 0.059s | 0.0s | 0.0s | 0.006s | 0.0s | 0.526s | 0.155s | 0.707s | 0.341s |
| `pfor_columnstore_random_full.bak` | 0.044s | 0.057s | 0.0s | 0.0s | 0.011s | 0.0s | 0.524s | 0.156s | 0.806s | 0.471s |
| `realworld_numeric_digest_full.bak` | 0.04s | 0.108s | 0.0s | 0.0s | 0.01s | 0.0s | 0.249s | 0.133s | 0.142s | 0.022s |
| `rowboundary_full.bak` | 0.039s | 0.087s | 0.0s | 0.0s | 0.013s | 0.0s | 0.139s | 0.104s | 0.183s | 0.073s |
| `rowstore_hash_pii_full.bak` | 0.039s | 0.051s | 0.0s | 0.0s | 0.009s | 0.0s | 0.001s | 0.075s | 0.048s | 0.075s |
| `rowstore_lob_image_full.bak` | 0.048s | 0.094s | 0.0s | 0.0s | 0.011s | 0.0s | 0.003s | 0.032s | 0.021s | 0.033s |
| `rowstore_lob_markup_full.bak` | 0.045s | 0.25s | 0.0s | 0.0s | 0.008s | 0.0s | 0.003s | 0.031s | 0.026s | 0.031s |
| `rowversion_extract_full.bak` | 0.039s | 0.124s | 0.0s | 0.0s | 0.014s | 0.0s | 0.101s | 0.137s | 0.099s | 0.041s |
| `sparse_full.bak` | 0.045s | 0.045s | 0.0s | 0.0s | 0.016s | 0.0s | 0.192s | 0.057s | 0.198s | 0.207s |
| `spatial_edge_full.bak` | 0.043s | 0.088s | 0.0s | 0.0s | 0.006s | 0.0s | 0.058s | 0.041s | 0.055s | 0.015s |
| `spatial_index_full.bak` | 0.04s | 0.107s | 0.0s | 0.0s | 0.014s | 0.0s | 0.029s | 0.04s | 0.025s | 0.029s |
| `sql_variant_extract_full.bak` | 0.034s | 0.093s | 0.0s | 0.0s | 0.01s | 0.0s | 0.002s | 0.032s | 0.027s | 0.033s |
| `striped_full_1.bak` | 0.038s | 0.07s | 0.0s | 0.0s | 0.01s | 0.0s | 0.001s | 0.253s | 0.093s | 0.253s |
| `striped_single.bak` | 0.059s | 0.035s | 0.0s | 0.0s | 0.036s | 0.0s | 0.001s | 0.073s | 0.124s | 0.13s |
| `surrogate_pairs_full.bak` | 0.049s | 0.048s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.058s | 0.055s | 0.059s |
| `tabletype_cci_large_full.bak` | 0.045s | 0.125s | 0.0s | 0.0s | 0.01s | 0.0s | 0.07s | 0.06s | 0.206s | 0.288s |
| `tabletypecoverage_diff.bak` | 0.12s | 0.076s | 0.0s | 0.0s | 0.022s | 0.0s | 0.502s | 0.121s | 0.34s | 0.027s |
| `tabletypecoverage_full.bak` | 0.045s | 0.111s | 0.0s | 0.0s | 0.014s | 0.0s | 0.542s | 0.162s | 0.388s | 0.023s |
| `temporal_hidden_full.bak` | 0.042s | 0.147s | 0.0s | 0.0s | 0.009s | 0.0s | 0.529s | 0.192s | 0.525s | 0.017s |
| `torn_page_full.bak` | 0.04s | 0.055s | 0.0s | 0.0s | 0.014s | 0.0s | 0.002s | 0.027s | 0.038s | 0.04s |
| `typecoverage_full.bak` | 0.044s | 0.035s | 0.0s | 0.0s | 0.013s | 0.0s | 0.576s | 0.527s | 0.14s | 0.015s |
| `typed_xml_full.bak` | 0.042s | 0.125s | 0.0s | 0.0s | 0.029s | 0.0s | 0.001s | 0.046s | 0.017s | 0.046s |
| `unicode_codepage_coverage.bak` | 0.039s | 0.156s | 0.0s | 0.0s | 0.011s | 0.0s | 0.317s | 0.298s | 0.032s | 0.015s |
| `utf8_collation_full.bak` | 0.078s | 0.109s | 0.0s | 0.0s | 0.008s | 0.0s | 0.028s | 0.04s | 0.029s | 0.013s |
| `xml_index_full.bak` | 0.095s | 0.041s | 0.0s | 0.0s | 0.044s | 0.0s | 0.035s | 0.058s | 0.047s | 0.026s |
| `xmlcoverage_full.bak` | 0.033s | 0.073s | 0.0s | 0.0s | 0.008s | 0.0s | 0.003s | 0.038s | 0.037s | 0.038s |
| `xmlheap_full.bak` | 0.155s | 0.051s | 0.0s | 0.0s | 0.023s | 0.0s | 0.016s | 0.045s | 0.153s | 0.16s |

_data decode (net) = data\_decode\_s (raw loop wall; sink writes and arrow verify overlap decode on a background writer thread and are drained in sink finish). catalog = recover\_catalog\_objects (indexes/FKs/constraints, pg\_dir only). arrow verify = cell verification run inside extraction (_StreamingStatsSink). verify=digest: per-column SHA-256 aggregate hash — fast, no GT parquet read, catches multiset-level corruption; also runs key-ordered digest (catches row transposition) when ordered\_digest is present in the manifest (populated by backfill\_ordered\_digest). Mismatches show as digest:col (multiset) or order:col (transposition). verify=full: exhaustive keyed row compare — also catches value-preserving row misalignment._

## Sink write timings

| Backup | delta write | delta read | pg_dir write | pg_dir read |
|--------|-------:| ------: | -------:| ------:|
| `alias_types_full.bak` | 0.026s | 0.213s | 0.012s | 0.017s |
| `archive_columnstore_partition_full.bak` | 0.298s | 0.805s | 0.557s | 0.637s |
| `archive_columnstore_types_full.bak` | 0.162s | 0.599s | 0.307s | 0.003s |
| `archive_columnstore_types_random_full.bak` | 0.209s | 0.989s | 0.44s | 1.259s |
| `archive_single_chunk_full.bak` | 0.046s | 0.093s | 0.013s | 0.012s |
| `archive_single_chunk_random_full.bak` | 0.073s | 0.116s | 0.008s | 0.01s |
| `archivenull_full.bak` | 0.019s | 0.167s | 0.057s | 0.135s |
| `backup_blocksize_full.bak` | 0.029s | 0.152s | 0.092s | 0.063s |
| `boundarycoverage_datetime_full.bak` | 0.152s | 0.769s | 1.358s | 0.599s |
| `boundarycoverage_full.bak` | 0.145s | 0.188s | 0.033s | 0.073s |
| `catalog_ss2019.bak` | 0.023s | 0.069s | 0.006s | 0.011s |
| `cci_binary_varbinary_compare_full.bak` | 0.018s | 0.058s | 0.01s | 0.109s |
| `cci_bitpack_probe_bigint_full.bak` | 1.561s | 1.941s | 0.937s | 1.393s |
| `cci_bitpack_probe_full.bak` | 0.058s | 0.583s | 0.074s | 0.353s |
| `cci_bitpack_probe_highbase_full.bak` | 0.054s | 0.124s | 0.045s | 0.134s |
| `cci_btree_nci_full.bak` | 0.019s | 0.18s | 0.009s | 0.081s |
| `cci_computed_full.bak` | 0.034s | 0.095s | 0.017s | 0.135s |
| `cci_enc5_largepool_full.bak` | 0.064s | 0.381s | 0.071s | 0.463s |
| `cci_extended_full.bak` | 0.155s | 0.105s | 0.018s | 0.046s |
| `cci_lob_full.bak` | 0.07s | 0.092s | 0.008s | 0.033s |
| `cci_reorganize_full.bak` | 0.13s | 0.235s | 0.007s | 0.041s |
| `cci_string_dict_regression_full.bak` | 0.048s | 0.208s | 0.048s | 0.285s |
| `cci_string_minmax_full.bak` | 0.063s | 0.149s | 0.007s | 0.085s |
| `cci_switch_full.bak` | 0.048s | 0.142s | 0.034s | 0.105s |
| `cci_types_large_full.bak` | 0.071s | 0.195s | 0.028s | 0.177s |
| `cci_varbinary_micro_full.bak` | 0.039s | 0.085s | 0.025s | 0.047s |
| `cci_varbinary_probe_full.bak` | 0.079s | 0.143s | 0.032s | 0.097s |
| `columnstore_minimal.bak` | 0.13s | 3.498s | 8.856s | 3.753s |
| `compressed_nvarchar_full.bak` | 0.027s | 0.127s | 0.007s | 0.012s |
| `compressioncoverage_full.bak` | 0.286s | 0.895s | 0.286s | 0.572s |
| `computedcoverage_full.bak` | 0.035s | 0.149s | 0.016s | 0.047s |
| `constraintcoverage_full.bak` | 0.14s | 0.248s | 0.035s | 0.168s |
| `covering_index_full.bak` | 0.034s | 0.134s | 0.015s | 0.018s |
| `cs_lob_preamble.bak` | 0.022s | 0.254s | 0.008s | 0.016s |
| `delta_rowgroup_full.bak` | 0.053s | 0.235s | 0.007s | 0.019s |
| `dirtycoverage_aborted_xact.bak` | 0.01s | 0.092s | 0.022s | 0.013s |
| `dirtycoverage_addcol.bak` | 0.016s | 0.066s | 0.006s | 0.098s |
| `dirtycoverage_addnotnull.bak` | 0.022s | 0.127s | 0.04s | 0.044s |
| `dirtycoverage_alldirty.bak` | 0.0s | 0.0s | 0.007s | 0.001s |
| `dirtycoverage_altercol.bak` | 0.03s | 0.048s | 0.006s | 0.065s |
| `dirtycoverage_altercol_rewrite.bak` | 0.01s | 0.047s | 0.028s | 0.095s |
| `dirtycoverage_alterdb.bak` | 0.023s | 0.047s | 0.007s | 0.008s |
| `dirtycoverage_cci_delete.bak` | 0.037s | 0.153s | 0.092s | 0.106s |
| `dirtycoverage_cci_update.bak` | 0.104s | 0.206s | 0.04s | 0.146s |
| `dirtycoverage_committed_delete.bak` | 0.077s | 0.075s | 0.006s | 0.009s |
| `dirtycoverage_committed_delete_v2.bak` | 0.012s | 0.064s | 0.069s | 0.09s |
| `dirtycoverage_committed_delete_v3.bak` | 0.016s | 0.177s | 0.063s | 0.106s |
| `dirtycoverage_committed_delete_v4.bak` | 0.019s | 0.153s | 0.011s | 0.153s |
| `dirtycoverage_committed_update.bak` | 0.029s | 0.046s | 0.012s | 0.059s |
| `dirtycoverage_committed_update_v2.bak` | 0.019s | 0.111s | 0.01s | 0.015s |
| `dirtycoverage_committed_update_v3.bak` | 0.016s | 0.243s | 0.097s | 0.138s |
| `dirtycoverage_committed_update_v4.bak` | 0.029s | 0.157s | 0.018s | 0.126s |
| `dirtycoverage_concurrent.bak` | 0.021s | 0.085s | 0.007s | 0.011s |
| `dirtycoverage_createidx.bak` | 0.022s | 0.038s | 0.036s | 0.008s |
| `dirtycoverage_createtable.bak` | 0.022s | 0.112s | 0.045s | 0.014s |
| `dirtycoverage_delete.bak` | 0.033s | 0.086s | 0.011s | 0.016s |
| `dirtycoverage_dropcol.bak` | 0.014s | 0.057s | 0.008s | 0.008s |
| `dirtycoverage_dropidx.bak` | 0.035s | 0.166s | 0.018s | 0.011s |
| `dirtycoverage_droptable.bak` | 0.035s | 0.071s | 0.005s | 0.125s |
| `dirtycoverage_heap_forward.bak` | 0.069s | 0.023s | 0.006s | 0.018s |
| `dirtycoverage_large_dirty.bak` | 0.012s | 0.083s | 0.012s | 0.016s |
| `dirtycoverage_lob_update.bak` | 0.02s | 0.15s | 0.027s | 0.01s |
| `dirtycoverage_maxrow.bak` | 0.044s | 0.124s | 0.005s | 0.026s |
| `dirtycoverage_nchar_delete.bak` | 0.071s | 0.168s | 0.007s | 0.079s |
| `dirtycoverage_nested.bak` | 0.019s | 0.127s | 0.009s | 0.017s |
| `dirtycoverage_null_update.bak` | 0.036s | 0.126s | 0.005s | 0.018s |
| `dirtycoverage_rebuildidx.bak` | 0.017s | 0.054s | 0.006s | 0.009s |
| `dirtycoverage_rich_insert.bak` | 0.014s | 0.026s | 0.034s | 0.051s |
| `dirtycoverage_rich_update.bak` | 0.05s | 0.037s | 0.012s | 0.042s |
| `dirtycoverage_savepoint.bak` | 0.015s | 0.049s | 0.005s | 0.111s |
| `dirtycoverage_snapshot_update.bak` | 0.041s | 0.057s | 0.017s | 0.007s |
| `dirtycoverage_switch.bak` | 0.029s | 0.138s | 0.023s | 0.018s |
| `dirtycoverage_temporal_update.bak` | 0.054s | 0.062s | 0.005s | 0.048s |
| `dirtycoverage_truncate.bak` | 0.017s | 0.131s | 0.008s | 0.086s |
| `dirtycoverage_two_tx.bak` | 0.022s | 0.052s | 0.006s | 0.011s |
| `dirtycoverage_uncommitted.bak` | 0.013s | 0.101s | 0.005s | 0.016s |
| `dirtycoverage_update.bak` | 0.02s | 0.142s | 0.017s | 0.01s |
| `filtered_ncci_full.bak` | 0.048s | 0.132s | 0.011s | 0.033s |
| `float_extreme_full.bak` | 0.056s | 0.057s | 0.021s | 0.014s |
| `forwarded_records_full.bak` | 0.037s | 0.145s | 0.045s | 0.142s |
| `ghost_records_full.bak` | 0.031s | 0.034s | 0.006s | 0.063s |
| `heapcoverage_large.bak` | 0.064s | 0.1s | 0.024s | 0.02s |
| `heapcoverage_large_50000.bak` | 0.056s | 0.25s | 0.039s | 0.52s |
| `hierarchyid_extract_full.bak` | 0.024s | 0.048s | 0.004s | 0.01s |
| `high_slot_density_full.bak` | 0.031s | 0.176s | 0.036s | 0.117s |
| `identity_coverage_full.bak` | 0.078s | 0.192s | 0.013s | 0.127s |
| `incrementalcoverage_diff_01.bak` | 0.024s | 0.065s | 0.008s | 0.028s |
| `incrementalcoverage_diff_02.bak` | 0.016s | 0.158s | 0.007s | 0.008s |
| `incrementalcoverage_diff_03.bak` | 0.018s | 0.091s | 0.005s | 0.009s |
| `incrementalcoverage_diff_04.bak` | 0.031s | 0.103s | 0.01s | 0.016s |
| `incrementalcoverage_diff_05.bak` | 0.032s | 0.106s | 0.052s | 0.026s |
| `incrementalcoverage_diff_06.bak` | 0.046s | 0.055s | 0.012s | 0.005s |
| `incrementalcoverage_full.bak` | 0.016s | 0.043s | 0.011s | 0.087s |
| `layoutcoverage_full.bak` | 0.898s | 2.462s | 0.257s | 0.695s |
| `max_row_width_full.bak` | 0.025s | 0.113s | 0.01s | 0.026s |
| `mixed_collation_full.bak` | 0.034s | 0.144s | 0.019s | 0.012s |
| `multi_rowgroup_full.bak` | 0.037s | 0.129s | 0.006s | 0.012s |
| `ncci_heap_full.bak` | 0.039s | 0.204s | 0.008s | 0.053s |
| `ncci_types_full.bak` | 0.378s | 0.719s | 0.767s | 0.826s |
| `ndfcoverage_full.bak` | 0.052s | 0.126s | 0.012s | 0.013s |
| `nvarchar_max_u21_full.bak` | 0.018s | 0.055s | 0.007s | 0.081s |
| `pagecomp_anchor_full.bak` | 0.043s | 0.162s | 0.012s | 0.124s |
| `pagecomp_long_prefix_full.bak` | 0.081s | 0.045s | 0.012s | 0.006s |
| `pfor_columnstore_full.bak` | 0.058s | 0.726s | 0.097s | 0.658s |
| `pfor_columnstore_random_full.bak` | 0.051s | 0.801s | 0.105s | 0.712s |
| `realworld_numeric_digest_full.bak` | 0.077s | 0.279s | 0.056s | 0.201s |
| `rowboundary_full.bak` | 0.043s | 0.063s | 0.061s | 0.033s |
| `rowstore_hash_pii_full.bak` | 0.058s | 0.195s | 0.017s | 0.007s |
| `rowstore_lob_image_full.bak` | 0.027s | 0.067s | 0.005s | 0.025s |
| `rowstore_lob_markup_full.bak` | 0.01s | 0.068s | 0.021s | 0.014s |
| `rowversion_extract_full.bak` | 0.123s | 0.057s | 0.014s | 0.025s |
| `sparse_full.bak` | 0.044s | 0.114s | 0.013s | 0.14s |
| `spatial_edge_full.bak` | 0.024s | 0.166s | 0.017s | 0.023s |
| `spatial_index_full.bak` | 0.026s | 0.119s | 0.014s | 0.056s |
| `sql_variant_extract_full.bak` | 0.022s | 0.148s | 0.01s | 0.096s |
| `striped_full_1.bak` | 0.157s | 0.089s | 0.096s | 0.025s |
| `striped_single.bak` | 0.063s | 0.074s | 0.01s | 0.067s |
| `surrogate_pairs_full.bak` | 0.022s | 0.067s | 0.036s | 0.007s |
| `tabletype_cci_large_full.bak` | 0.043s | 0.195s | 0.017s | 0.389s |
| `tabletypecoverage_diff.bak` | 0.057s | 0.431s | 0.064s | 1.016s |
| `tabletypecoverage_full.bak` | 0.114s | 0.352s | 0.048s | 0.835s |
| `temporal_hidden_full.bak` | 0.065s | 0.078s | 0.127s | 0.06s |
| `torn_page_full.bak` | 0.02s | 0.203s | 0.007s | 0.012s |
| `typecoverage_full.bak` | 0.449s | 0.884s | 0.078s | 0.868s |
| `typed_xml_full.bak` | 0.041s | 0.079s | 0.005s | 0.011s |
| `unicode_codepage_coverage.bak` | 0.228s | 0.447s | 0.07s | 0.359s |
| `utf8_collation_full.bak` | 0.032s | 0.133s | 0.008s | 0.108s |
| `xml_index_full.bak` | 0.028s | 0.137s | 0.03s | 0.064s |
| `xmlcoverage_full.bak` | 0.02s | 0.134s | 0.018s | 0.008s |
| `xmlheap_full.bak` | 0.033s | 0.11s | 0.012s | 0.059s |

_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._

## Sink read breakdown

| Backup | arrow verify | delta read | delta stats | delta verify | pg_dir read | pg_dir stats | pg_dir verify |
|--------| -------: | -------: | -------: | -------: | -------: | -------: | -------:|
| `alias_types_full.bak` | 0.029s | 0.198s | 0.0s | 0.002s | 0.006s | 0.0s | 0.001s |
| `archive_columnstore_partition_full.bak` | 0.36s | 0.254s | 0.021s | 0.453s | 0.379s | 0.151s | 0.1s |
| `archive_columnstore_types_full.bak` | 0.687s | 0.067s | 0.009s | 0.456s | 0.0s | 0.0s | 0.0s |
| `archive_columnstore_types_random_full.bak` | 0.763s | 0.164s | 0.008s | 0.723s | 0.345s | 0.005s | 0.75s |
| `archive_single_chunk_full.bak` | 0.045s | 0.084s | 0.0s | 0.001s | 0.005s | 0.0s | 0.001s |
| `archive_single_chunk_random_full.bak` | 0.076s | 0.106s | 0.0s | 0.002s | 0.004s | 0.0s | 0.001s |
| `archivenull_full.bak` | 0.063s | 0.099s | 0.002s | 0.059s | 0.087s | 0.005s | 0.036s |
| `backup_blocksize_full.bak` | 0.11s | 0.092s | 0.0s | 0.001s | 0.026s | 0.0s | 0.002s |
| `boundarycoverage_datetime_full.bak` | 0.82s | 0.186s | 0.008s | 0.462s | 0.044s | 0.002s | 0.473s |
| `boundarycoverage_full.bak` | 0.03s | 0.101s | 0.001s | 0.009s | 0.015s | 0.001s | 0.007s |
| `catalog_ss2019.bak` | 0.025s | 0.059s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_binary_varbinary_compare_full.bak` | 0.03s | 0.043s | 0.0s | 0.003s | 0.086s | 0.0s | 0.002s |
| `cci_bitpack_probe_bigint_full.bak` | 1.847s | 0.2s | 0.003s | 1.72s | 0.193s | 0.006s | 1.178s |
| `cci_bitpack_probe_full.bak` | 0.459s | 0.047s | 0.001s | 0.465s | 0.031s | 0.001s | 0.304s |
| `cci_bitpack_probe_highbase_full.bak` | 0.114s | 0.044s | 0.0s | 0.061s | 0.026s | 0.0s | 0.083s |
| `cci_btree_nci_full.bak` | 0.051s | 0.143s | 0.0s | 0.002s | 0.004s | 0.0s | 0.002s |
| `cci_computed_full.bak` | 0.038s | 0.076s | 0.0s | 0.002s | 0.05s | 0.0s | 0.001s |
| `cci_enc5_largepool_full.bak` | 0.451s | 0.11s | 0.002s | 0.251s | 0.099s | 0.004s | 0.339s |
| `cci_extended_full.bak` | 0.026s | 0.063s | 0.001s | 0.004s | 0.007s | 0.0s | 0.004s |
| `cci_lob_full.bak` | 0.047s | 0.057s | 0.0s | 0.003s | 0.007s | 0.0s | 0.003s |
| `cci_reorganize_full.bak` | 0.102s | 0.189s | 0.001s | 0.001s | 0.012s | 0.0s | 0.002s |
| `cci_string_dict_regression_full.bak` | 0.32s | 0.047s | 0.003s | 0.121s | 0.066s | 0.003s | 0.2s |
| `cci_string_minmax_full.bak` | 0.019s | 0.132s | 0.0s | 0.001s | 0.005s | 0.001s | 0.001s |
| `cci_switch_full.bak` | 0.033s | 0.123s | 0.0s | 0.002s | 0.005s | 0.0s | 0.002s |
| `cci_types_large_full.bak` | 0.031s | 0.147s | 0.001s | 0.008s | 0.072s | 0.001s | 0.028s |
| `cci_varbinary_micro_full.bak` | 0.022s | 0.059s | 0.0s | 0.001s | 0.004s | 0.0s | 0.001s |
| `cci_varbinary_probe_full.bak` | 0.114s | 0.06s | 0.005s | 0.019s | 0.01s | 0.0s | 0.015s |
| `columnstore_minimal.bak` | 6.639s | 0.119s | 0.004s | 3.327s | 0.063s | 0.035s | 3.594s |
| `compressed_nvarchar_full.bak` | 0.025s | 0.119s | 0.0s | 0.0s | 0.002s | 0.0s | 0.001s |
| `compressioncoverage_full.bak` | 0.577s | 0.372s | 0.011s | 0.294s | 0.053s | 0.019s | 0.396s |
| `computedcoverage_full.bak` | 0.028s | 0.12s | 0.0s | 0.003s | 0.008s | 0.0s | 0.001s |
| `constraintcoverage_full.bak` | 0.054s | 0.14s | 0.001s | 0.006s | 0.048s | 0.001s | 0.008s |
| `covering_index_full.bak` | 0.056s | 0.069s | 0.001s | 0.002s | 0.005s | 0.0s | 0.002s |
| `cs_lob_preamble.bak` | 0.02s | 0.247s | 0.001s | 0.001s | 0.003s | 0.0s | 0.002s |
| `delta_rowgroup_full.bak` | 0.019s | 0.189s | 0.003s | 0.002s | 0.006s | 0.0s | 0.001s |
| `dirtycoverage_aborted_xact.bak` | 0.029s | 0.079s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_addcol.bak` | 0.021s | 0.057s | 0.0s | 0.0s | 0.003s | 0.039s | 0.004s |
| `dirtycoverage_addnotnull.bak` | 0.089s | 0.12s | 0.0s | 0.001s | 0.032s | 0.0s | 0.0s |
| `dirtycoverage_alldirty.bak` | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s |
| `dirtycoverage_altercol.bak` | 0.033s | 0.037s | 0.0s | 0.001s | 0.052s | 0.0s | 0.001s |
| `dirtycoverage_altercol_rewrite.bak` | 0.034s | 0.036s | 0.0s | 0.001s | 0.088s | 0.0s | 0.0s |
| `dirtycoverage_alterdb.bak` | 0.024s | 0.038s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `dirtycoverage_cci_delete.bak` | 0.174s | 0.094s | 0.001s | 0.038s | 0.01s | 0.0s | 0.071s |
| `dirtycoverage_cci_update.bak` | 0.167s | 0.036s | 0.001s | 0.116s | 0.012s | 0.0s | 0.097s |
| `dirtycoverage_committed_delete.bak` | 0.122s | 0.066s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_committed_delete_v2.bak` | 0.089s | 0.052s | 0.0s | 0.002s | 0.073s | 0.004s | 0.003s |
| `dirtycoverage_committed_delete_v3.bak` | 0.201s | 0.049s | 0.001s | 0.094s | 0.015s | 0.001s | 0.084s |
| `dirtycoverage_committed_delete_v4.bak` | 0.211s | 0.095s | 0.001s | 0.028s | 0.05s | 0.001s | 0.064s |
| `dirtycoverage_committed_update.bak` | 0.05s | 0.035s | 0.0s | 0.001s | 0.006s | 0.0s | 0.002s |
| `dirtycoverage_committed_update_v2.bak` | 0.022s | 0.102s | 0.0s | 0.002s | 0.007s | 0.0s | 0.002s |
| `dirtycoverage_committed_update_v3.bak` | 0.234s | 0.108s | 0.001s | 0.098s | 0.028s | 0.004s | 0.101s |
| `dirtycoverage_committed_update_v4.bak` | 0.268s | 0.065s | 0.001s | 0.044s | 0.033s | 0.001s | 0.055s |
| `dirtycoverage_concurrent.bak` | 0.023s | 0.072s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `dirtycoverage_createidx.bak` | 0.067s | 0.03s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `dirtycoverage_createtable.bak` | 0.075s | 0.102s | 0.0s | 0.0s | 0.003s | 0.0s | 0.0s |
| `dirtycoverage_delete.bak` | 0.059s | 0.071s | 0.0s | 0.004s | 0.004s | 0.0s | 0.0s |
| `dirtycoverage_dropcol.bak` | 0.023s | 0.05s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `dirtycoverage_dropidx.bak` | 0.047s | 0.043s | 0.0s | 0.0s | 0.003s | 0.0s | 0.001s |
| `dirtycoverage_droptable.bak` | 0.068s | 0.048s | 0.0s | 0.001s | 0.065s | 0.001s | 0.002s |
| `dirtycoverage_heap_forward.bak` | 0.115s | 0.012s | 0.0s | 0.005s | 0.004s | 0.0s | 0.004s |
| `dirtycoverage_large_dirty.bak` | 0.04s | 0.076s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_lob_update.bak` | 0.032s | 0.143s | 0.0s | 0.001s | 0.003s | 0.0s | 0.0s |
| `dirtycoverage_maxrow.bak` | 0.039s | 0.116s | 0.0s | 0.001s | 0.016s | 0.0s | 0.001s |
| `dirtycoverage_nchar_delete.bak` | 0.031s | 0.16s | 0.0s | 0.0s | 0.069s | 0.0s | 0.001s |
| `dirtycoverage_nested.bak` | 0.023s | 0.045s | 0.005s | 0.061s | 0.005s | 0.0s | 0.0s |
| `dirtycoverage_null_update.bak` | 0.03s | 0.1s | 0.0s | 0.0s | 0.006s | 0.001s | 0.003s |
| `dirtycoverage_rebuildidx.bak` | 0.021s | 0.048s | 0.0s | 0.0s | 0.003s | 0.0s | 0.0s |
| `dirtycoverage_rich_insert.bak` | 0.318s | 0.014s | 0.0s | 0.005s | 0.034s | 0.001s | 0.006s |
| `dirtycoverage_rich_update.bak` | 0.272s | 0.024s | 0.0s | 0.004s | 0.015s | 0.0s | 0.014s |
| `dirtycoverage_savepoint.bak` | 0.031s | 0.038s | 0.0s | 0.001s | 0.103s | 0.0s | 0.0s |
| `dirtycoverage_snapshot_update.bak` | 0.06s | 0.047s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_switch.bak` | 0.028s | 0.12s | 0.001s | 0.001s | 0.005s | 0.0s | 0.001s |
| `dirtycoverage_temporal_update.bak` | 0.196s | 0.051s | 0.0s | 0.001s | 0.023s | 0.008s | 0.003s |
| `dirtycoverage_truncate.bak` | 0.02s | 0.122s | 0.0s | 0.001s | 0.039s | 0.0s | 0.01s |
| `dirtycoverage_two_tx.bak` | 0.059s | 0.043s | 0.0s | 0.001s | 0.003s | 0.0s | 0.0s |
| `dirtycoverage_uncommitted.bak` | 0.039s | 0.092s | 0.0s | 0.0s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_update.bak` | 0.095s | 0.133s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `filtered_ncci_full.bak` | 0.037s | 0.106s | 0.001s | 0.002s | 0.006s | 0.0s | 0.005s |
| `float_extreme_full.bak` | 0.069s | 0.042s | 0.0s | 0.001s | 0.006s | 0.0s | 0.0s |
| `forwarded_records_full.bak` | 0.269s | 0.036s | 0.001s | 0.086s | 0.075s | 0.001s | 0.051s |
| `ghost_records_full.bak` | 0.104s | 0.018s | 0.0s | 0.006s | 0.042s | 0.0s | 0.013s |
| `heapcoverage_large.bak` | 0.122s | 0.078s | 0.0s | 0.007s | 0.003s | 0.0s | 0.004s |
| `heapcoverage_large_50000.bak` | 0.405s | 0.033s | 0.004s | 0.198s | 0.134s | 0.014s | 0.283s |
| `hierarchyid_extract_full.bak` | 0.023s | 0.039s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `high_slot_density_full.bak` | 0.106s | 0.08s | 0.0s | 0.028s | 0.012s | 0.0s | 0.06s |
| `identity_coverage_full.bak` | 0.068s | 0.095s | 0.001s | 0.003s | 0.025s | 0.001s | 0.002s |
| `incrementalcoverage_diff_01.bak` | 0.026s | 0.055s | 0.0s | 0.0s | 0.015s | 0.0s | 0.0s |
| `incrementalcoverage_diff_02.bak` | 0.021s | 0.149s | 0.0s | 0.0s | 0.003s | 0.0s | 0.0s |
| `incrementalcoverage_diff_03.bak` | 0.019s | 0.081s | 0.001s | 0.001s | 0.002s | 0.0s | 0.001s |
| `incrementalcoverage_diff_04.bak` | 0.062s | 0.093s | 0.0s | 0.001s | 0.006s | 0.0s | 0.0s |
| `incrementalcoverage_diff_05.bak` | 0.024s | 0.047s | 0.0s | 0.0s | 0.016s | 0.0s | 0.001s |
| `incrementalcoverage_diff_06.bak` | 0.052s | 0.047s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `incrementalcoverage_full.bak` | 0.028s | 0.036s | 0.0s | 0.0s | 0.063s | 0.0s | 0.001s |
| `layoutcoverage_full.bak` | 0.402s | 1.595s | 0.033s | 0.117s | 0.253s | 0.027s | 0.166s |
| `max_row_width_full.bak` | 0.021s | 0.057s | 0.0s | 0.001s | 0.015s | 0.0s | 0.001s |
| `mixed_collation_full.bak` | 0.028s | 0.111s | 0.002s | 0.001s | 0.004s | 0.0s | 0.0s |
| `multi_rowgroup_full.bak` | 0.035s | 0.111s | 0.0s | 0.002s | 0.002s | 0.0s | 0.001s |
| `ncci_heap_full.bak` | 0.02s | 0.169s | 0.0s | 0.001s | 0.005s | 0.001s | 0.001s |
| `ncci_types_full.bak` | 0.662s | 0.225s | 0.003s | 0.299s | 0.152s | 0.004s | 0.434s |
| `ndfcoverage_full.bak` | 0.066s | 0.064s | 0.0s | 0.001s | 0.003s | 0.0s | 0.0s |
| `nvarchar_max_u21_full.bak` | 0.02s | 0.043s | 0.0s | 0.001s | 0.073s | 0.0s | 0.0s |
| `pagecomp_anchor_full.bak` | 0.322s | 0.076s | 0.001s | 0.037s | 0.013s | 0.0s | 0.098s |
| `pagecomp_long_prefix_full.bak` | 0.089s | 0.036s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `pfor_columnstore_full.bak` | 0.707s | 0.078s | 0.001s | 0.599s | 0.052s | 0.006s | 0.585s |
| `pfor_columnstore_random_full.bak` | 0.806s | 0.162s | 0.003s | 0.603s | 0.058s | 0.002s | 0.622s |
| `realworld_numeric_digest_full.bak` | 0.142s | 0.136s | 0.001s | 0.083s | 0.008s | 0.001s | 0.111s |
| `rowboundary_full.bak` | 0.183s | 0.031s | 0.0s | 0.008s | 0.006s | 0.0s | 0.008s |
| `rowstore_hash_pii_full.bak` | 0.048s | 0.185s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `rowstore_lob_image_full.bak` | 0.021s | 0.057s | 0.0s | 0.001s | 0.006s | 0.001s | 0.001s |
| `rowstore_lob_markup_full.bak` | 0.026s | 0.059s | 0.0s | 0.001s | 0.003s | 0.0s | 0.0s |
| `rowversion_extract_full.bak` | 0.099s | 0.043s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `sparse_full.bak` | 0.198s | 0.059s | 0.0s | 0.046s | 0.02s | 0.0s | 0.055s |
| `spatial_edge_full.bak` | 0.055s | 0.148s | 0.0s | 0.002s | 0.004s | 0.0s | 0.001s |
| `spatial_index_full.bak` | 0.025s | 0.101s | 0.001s | 0.002s | 0.011s | 0.0s | 0.002s |
| `sql_variant_extract_full.bak` | 0.027s | 0.095s | 0.0s | 0.035s | 0.012s | 0.0s | 0.001s |
| `striped_full_1.bak` | 0.093s | 0.073s | 0.0s | 0.001s | 0.013s | 0.0s | 0.004s |
| `striped_single.bak` | 0.124s | 0.048s | 0.001s | 0.001s | 0.046s | 0.0s | 0.003s |
| `surrogate_pairs_full.bak` | 0.055s | 0.059s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `tabletype_cci_large_full.bak` | 0.206s | 0.105s | 0.002s | 0.014s | 0.246s | 0.073s | 0.062s |
| `tabletypecoverage_diff.bak` | 0.34s | 0.215s | 0.013s | 0.154s | 0.639s | 0.094s | 0.222s |
| `tabletypecoverage_full.bak` | 0.388s | 0.161s | 0.013s | 0.133s | 0.578s | 0.015s | 0.193s |
| `temporal_hidden_full.bak` | 0.525s | 0.027s | 0.001s | 0.009s | 0.006s | 0.001s | 0.007s |
| `torn_page_full.bak` | 0.038s | 0.184s | 0.001s | 0.007s | 0.004s | 0.0s | 0.001s |
| `typecoverage_full.bak` | 0.14s | 0.462s | 0.011s | 0.033s | 0.354s | 0.015s | 0.113s |
| `typed_xml_full.bak` | 0.017s | 0.07s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `unicode_codepage_coverage.bak` | 0.032s | 0.229s | 0.004s | 0.008s | 0.077s | 0.004s | 0.012s |
| `utf8_collation_full.bak` | 0.029s | 0.117s | 0.0s | 0.001s | 0.007s | 0.0s | 0.001s |
| `xml_index_full.bak` | 0.047s | 0.116s | 0.0s | 0.008s | 0.001s | 0.0s | 0.001s |
| `xmlcoverage_full.bak` | 0.037s | 0.12s | 0.0s | 0.004s | 0.002s | 0.0s | 0.0s |
| `xmlheap_full.bak` | 0.153s | 0.046s | 0.0s | 0.012s | 0.016s | 0.0s | 0.016s |

_arrow verify = cell verification folded into extract_s. Sink read = pure I/O + decode. Stats = min/max/null compute. Sink verify = cell verification on the round-tripped data. Remainder of readback_s is GC / other._

---

_Generated 2026-07-17 · 132 fixtures · 127 pass · 1 xfail · 4 fail_
