# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2017`.

**134 fixtures · 133 pass · 1 xfail (known gap) · 0 fail**

**Tables:** 2004/2004 pass · **Columns:** 19958/19958 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** ✓

**Edges:** mssql→arrow ✓ · arrow→delta ✓ · delta→arrow ✓ · arrow→pg_dir ✓ · pg_dir→arrow ✓

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

**Metadata:** 1161/1161 fixture-categories pass (constraints: 129/129, indexes: 129/129, extended_properties: 129/129, modules: 129/129, schema_objects: 129/129, security: 129/129, statistics: 129/129, plan_guides: 129/129, query_store: 129/129)

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
| `archive_columnstore_partition_full.bak` | arrow→pg_dir | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | — | ✓ |
| `archive_columnstore_partition_full.bak` | pg_dir→arrow | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | digest | ✓ |
| `archive_columnstore_types_full.bak` | mssql→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_full.bak` | arrow→delta | 245,000 | 14 | **7/7** | **14/14** | **28/28** | **7/7** | — | ✓ |
| `archive_columnstore_types_full.bak` | delta→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_full.bak` | arrow→pg_dir | 245,000 | 14 | **7/7** | **14/14** | **28/28** | **7/7** | — | ✓ |
| `archive_columnstore_types_full.bak` | pg_dir→arrow | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
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
| `cci_enc5_largepool_matrix_full.bak` | mssql→arrow | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | digest | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | arrow→delta | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | — | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | delta→arrow | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | digest | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | arrow→pg_dir | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | — | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | pg_dir→arrow | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | digest | ✓ |
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
| `compressioncoverage_full.bak` | arrow→pg_dir | 1,994 | 239 | **19/19** | **239/239** | **478/478** | **19/19** | — | ✓ |
| `compressioncoverage_full.bak` | pg_dir→arrow | 1,994 | 239 | **19/19** | **239/239** | **464/464** | **19/19** | digest | ✓ |
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
| `dirtycoverage_cci_delete.bak` | mssql→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_delete.bak` | arrow→delta | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_delete.bak` | delta→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_delete.bak` | arrow→pg_dir | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `dirtycoverage_cci_delete.bak` | pg_dir→arrow | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
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
| `layoutcoverage_full.bak` | arrow→pg_dir | 171 | 2,421 | **57/57** | **2421/2421** | **4842/4842** | **57/57** | — | ✓ |
| `layoutcoverage_full.bak` | pg_dir→arrow | 171 | 2,421 | **57/57** | **2421/2421** | **4834/4834** | **57/57** | digest | ✓ |
| `max_row_width_full.bak` | mssql→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `max_row_width_full.bak` | arrow→delta | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `max_row_width_full.bak` | delta→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `max_row_width_full.bak` | arrow→pg_dir | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | — | ✓ |
| `max_row_width_full.bak` | pg_dir→arrow | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | mssql→arrow | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | arrow→delta | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `mixed_collation_full.bak` | delta→arrow | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
| `mixed_collation_full.bak` | arrow→pg_dir | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | — | ✓ |
| `mixed_collation_full.bak` | pg_dir→arrow | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | digest | ✓ |
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
| `xtp_checkpoint_straddle_full.bak` | mssql→arrow | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xtp_checkpoint_straddle_full.bak` | arrow→delta | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `xtp_checkpoint_straddle_full.bak` | delta→arrow | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xtp_checkpoint_straddle_full.bak` | arrow→pg_dir | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | — | ✓ |
| `xtp_checkpoint_straddle_full.bak` | pg_dir→arrow | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xtp_probe_full.bak` | mssql→arrow | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_probe_full.bak` | arrow→delta | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_probe_full.bak` | delta→arrow | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_probe_full.bak` | arrow→pg_dir | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_probe_full.bak` | pg_dir→arrow | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | mssql→arrow | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_rich_full.bak` | arrow→delta | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | — | ✓ |
| `xtp_rich_full.bak` | delta→arrow | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_rich_full.bak` | arrow→pg_dir | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | — | ✓ |
| `xtp_rich_full.bak` | pg_dir→arrow | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | mssql→arrow | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | arrow→delta | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | delta→arrow | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | arrow→pg_dir | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | pg_dir→arrow | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `archive_columnstore_partition_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 12.117 MB_

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
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.113 MB_

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

### `archive_columnstore_types_random_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.113 MB_

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

### `archive_single_chunk_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

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

### `archive_single_chunk_random_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

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

### `archivenull_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.113 MB_

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

### `backup_blocksize_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `boundarycoverage_datetime_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.109 MB_

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

### `boundarycoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `cci_binary_varbinary_compare_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

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

### `cci_bitpack_probe_bigint_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 41.145 MB_

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

### `cci_bitpack_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.117 MB_

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

### `cci_bitpack_probe_highbase_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.117 MB_

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

### `cci_btree_nci_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.734 MB_

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

### `cci_computed_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.234 MB_

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

### `cci_enc5_largepool_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

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

### `cci_enc5_largepool_matrix_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 23.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | columnstore | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | columnstore | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | columnstore | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | columnstore | 32,767 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_32768_distinct_var` | columnstore | 32,768 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_65536_distinct_var` | columnstore | 65,536 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_fullwidth` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_lowcard_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.varchar_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | columnstore | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | columnstore | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | columnstore | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | columnstore | 32,767 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_32768_distinct_var` | columnstore | 32,768 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_65536_distinct_var` | columnstore | 65,536 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_fullwidth` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.char_80000_lowcard_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.varchar_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | columnstore | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | columnstore | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | columnstore | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | columnstore | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `cci_lob_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

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

### `cci_reorganize_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

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

### `cci_string_dict_regression_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 8.113 MB_

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

### `cci_string_minmax_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

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

### `cci_switch_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

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

### `cci_types_large_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

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

### `cci_varbinary_micro_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

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

### `cci_varbinary_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.422 MB_

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

### `columnstore_minimal.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `compressed_nvarchar_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `compressioncoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ |  |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ |  |

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
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells digest ✓ |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `computedcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `constraintcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.484 MB_

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

### `covering_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

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

### `cs_lob_preamble.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.543 MB_

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

### `delta_rowgroup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

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

### `dirtycoverage_aborted_xact.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_addcol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_addnotnull.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_alldirty.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `dirtycoverage_altercol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_altercol_rewrite.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_alterdb.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_cci_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

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

### `dirtycoverage_cci_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

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

### `dirtycoverage_committed_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `dirtycoverage_committed_delete_v2.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

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

### `dirtycoverage_committed_delete_v3.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

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

### `dirtycoverage_committed_delete_v4.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

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

### `dirtycoverage_committed_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `dirtycoverage_committed_update_v2.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

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

### `dirtycoverage_committed_update_v3.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

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

### `dirtycoverage_committed_update_v4.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

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

### `dirtycoverage_concurrent.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_createidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_createtable.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_dropcol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_dropidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_droptable.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_heap_forward.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_large_dirty.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

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

### `dirtycoverage_lob_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

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

### `dirtycoverage_maxrow.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `dirtycoverage_nchar_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_nested.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_null_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_rebuildidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_rich_insert.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_rich_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_savepoint.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_snapshot_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `dirtycoverage_switch.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

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

### `dirtycoverage_temporal_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

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

### `dirtycoverage_truncate.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_two_tx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `dirtycoverage_uncommitted.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `dirtycoverage_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `filtered_ncci_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

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

### `float_extreme_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `forwarded_records_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 14.113 MB_

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

### `ghost_records_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `heapcoverage_large.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

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

### `heapcoverage_large_50000.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 11.113 MB_

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

### `hierarchyid_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `high_slot_density_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.863 MB_

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

### `identity_coverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.109 MB_

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

### `incrementalcoverage_diff_01.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_diff_02.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_diff_03.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_diff_04.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_diff_05.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_diff_06.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

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

### `incrementalcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `layoutcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.734 MB_

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

### `max_row_width_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `mixed_collation_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `multi_rowgroup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.609 MB_

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

### `ncci_heap_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.109 MB_

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

### `ncci_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

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

### `ndfcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.113 MB_

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

### `nvarchar_max_u21_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `pagecomp_anchor_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

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

### `pagecomp_long_prefix_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `pfor_columnstore_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

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

### `pfor_columnstore_random_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

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

### `realworld_numeric_digest_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

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

### `rowboundary_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

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

### `rowstore_hash_pii_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `rowstore_lob_image_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `rowstore_lob_markup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `rowversion_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

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

### `sparse_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

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

### `spatial_edge_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

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

### `spatial_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

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

### `sql_variant_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `striped_full_1.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.18 MB_

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

### `striped_single.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.41 MB_

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

### `surrogate_pairs_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `tabletype_cci_large_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `tabletypecoverage_diff.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.109 MB_

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

### `tabletypecoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.109 MB_

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

### `temporal_hidden_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

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

### `torn_page_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `typecoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.547 MB_

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

### `typed_xml_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `unicode_codepage_coverage.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.234 MB_

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

### `xml_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

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

### `xmlcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

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

### `xmlheap_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.672 MB_

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

### `xtp_checkpoint_straddle_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.52 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.242 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |


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
| `cci_binary_varbinary_compare_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_btree_nci_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_computed_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_enc5_largepool_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
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
| `xml_index_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `xmlcoverage_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `xmlheap_full.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `alias_types_full.bak` | 0.096s | 0.184s | 0.28s |
| `archive_columnstore_partition_full.bak` | 1.209s | 1.117s | 2.326s |
| `archive_columnstore_types_full.bak` | 0.799s | 1.064s | 1.863s |
| `archive_columnstore_types_random_full.bak` | 0.935s | 1.064s | 1.999s |
| `archive_single_chunk_full.bak` | 0.11s | 0.204s | 0.314s |
| `archive_single_chunk_random_full.bak` | 0.112s | 0.206s | 0.318s |
| `archivenull_full.bak` | 0.305s | 0.359s | 0.664s |
| `backup_blocksize_full.bak` | 0.094s | 0.195s | 0.289s |
| `boundarycoverage_datetime_full.bak` | 0.434s | 0.514s | 0.948s |
| `boundarycoverage_full.bak` | 0.139s | 0.304s | 0.443s |
| `cci_binary_varbinary_compare_full.bak` | 0.113s | 0.198s | 0.311s |
| `cci_bitpack_probe_bigint_full.bak` | 2.278s | 1.893s | 4.171s |
| `cci_bitpack_probe_full.bak` | 0.336s | 0.6s | 0.936s |
| `cci_bitpack_probe_highbase_full.bak` | 0.26s | 0.391s | 0.651s |
| `cci_btree_nci_full.bak` | 0.11s | 0.223s | 0.333s |
| `cci_computed_full.bak` | 0.123s | 0.207s | 0.33s |
| `cci_enc5_largepool_full.bak` | 0.602s | 0.512s | 1.114s |
| `cci_enc5_largepool_matrix_full.bak` | 8.125s | 1.543s | 9.668s |
| `cci_extended_full.bak` | 0.14s | 0.25s | 0.39s |
| `cci_lob_full.bak` | 0.145s | 0.229s | 0.374s |
| `cci_reorganize_full.bak` | 0.126s | 0.222s | 0.348s |
| `cci_string_dict_regression_full.bak` | 0.579s | 0.417s | 0.996s |
| `cci_string_minmax_full.bak` | 0.108s | 0.205s | 0.313s |
| `cci_switch_full.bak` | 0.116s | 0.199s | 0.315s |
| `cci_types_large_full.bak` | 0.14s | 0.282s | 0.422s |
| `cci_varbinary_micro_full.bak` | 0.133s | 0.222s | 0.355s |
| `cci_varbinary_probe_full.bak` | 0.159s | 0.22s | 0.379s |
| `columnstore_minimal.bak` | 1.93s | 1.776s | 3.706s |
| `compressed_nvarchar_full.bak` | 0.095s | 0.197s | 0.292s |
| `compressioncoverage_full.bak` | 0.475s | 0.66s | 1.135s |
| `computedcoverage_full.bak` | 0.096s | 0.205s | 0.301s |
| `constraintcoverage_full.bak` | 0.139s | 0.301s | 0.44s |
| `covering_index_full.bak` | 0.112s | 0.203s | 0.315s |
| `cs_lob_preamble.bak` | 0.188s | 0.209s | 0.397s |
| `delta_rowgroup_full.bak` | 0.098s | 0.196s | 0.294s |
| `dirtycoverage_aborted_xact.bak` | 0.126s | 0.192s | 0.318s |
| `dirtycoverage_addcol.bak` | 0.112s | 0.185s | 0.297s |
| `dirtycoverage_addnotnull.bak` | 0.11s | 0.194s | 0.304s |
| `dirtycoverage_alldirty.bak` | 0.103s | 0.167s | 0.27s |
| `dirtycoverage_altercol.bak` | 0.094s | 0.342s | 0.436s |
| `dirtycoverage_altercol_rewrite.bak` | 0.103s | 0.19s | 0.293s |
| `dirtycoverage_alterdb.bak` | 0.123s | 0.198s | 0.321s |
| `dirtycoverage_cci_delete.bak` | 0.217s | 0.246s | 0.463s |
| `dirtycoverage_cci_update.bak` | 0.22s | 0.238s | 0.458s |
| `dirtycoverage_committed_delete.bak` | 0.103s | 0.19s | 0.293s |
| `dirtycoverage_committed_delete_v2.bak` | 0.119s | 0.197s | 0.316s |
| `dirtycoverage_committed_delete_v3.bak` | 0.192s | 0.253s | 0.445s |
| `dirtycoverage_committed_delete_v4.bak` | 0.294s | 0.245s | 0.539s |
| `dirtycoverage_committed_update.bak` | 0.101s | 0.183s | 0.284s |
| `dirtycoverage_committed_update_v2.bak` | 0.098s | 0.191s | 0.289s |
| `dirtycoverage_committed_update_v3.bak` | 0.186s | 0.258s | 0.444s |
| `dirtycoverage_committed_update_v4.bak` | 0.313s | 0.258s | 0.571s |
| `dirtycoverage_concurrent.bak` | 0.111s | 0.182s | 0.293s |
| `dirtycoverage_createidx.bak` | 0.123s | 0.19s | 0.313s |
| `dirtycoverage_createtable.bak` | 0.12s | 0.191s | 0.311s |
| `dirtycoverage_delete.bak` | 0.109s | 0.184s | 0.293s |
| `dirtycoverage_dropcol.bak` | 0.114s | 0.198s | 0.312s |
| `dirtycoverage_dropidx.bak` | 0.111s | 0.203s | 0.314s |
| `dirtycoverage_droptable.bak` | 0.114s | 0.207s | 0.321s |
| `dirtycoverage_heap_forward.bak` | 0.128s | 0.173s | 0.301s |
| `dirtycoverage_large_dirty.bak` | 0.466s | 0.195s | 0.661s |
| `dirtycoverage_lob_update.bak` | 0.131s | 0.183s | 0.314s |
| `dirtycoverage_maxrow.bak` | 0.099s | 0.193s | 0.292s |
| `dirtycoverage_nchar_delete.bak` | 0.134s | 0.193s | 0.327s |
| `dirtycoverage_nested.bak` | 0.11s | 0.191s | 0.301s |
| `dirtycoverage_null_update.bak` | 0.111s | 0.188s | 0.299s |
| `dirtycoverage_rebuildidx.bak` | 0.132s | 0.196s | 0.328s |
| `dirtycoverage_rich_insert.bak` | 0.164s | 0.172s | 0.336s |
| `dirtycoverage_rich_update.bak` | 0.183s | 0.173s | 0.356s |
| `dirtycoverage_savepoint.bak` | 0.117s | 0.185s | 0.302s |
| `dirtycoverage_snapshot_update.bak` | 0.108s | 0.183s | 0.291s |
| `dirtycoverage_switch.bak` | 0.136s | 0.232s | 0.368s |
| `dirtycoverage_temporal_update.bak` | 0.152s | 0.185s | 0.337s |
| `dirtycoverage_truncate.bak` | 0.105s | 0.187s | 0.292s |
| `dirtycoverage_two_tx.bak` | 0.112s | 0.183s | 0.295s |
| `dirtycoverage_uncommitted.bak` | 0.113s | 0.192s | 0.305s |
| `dirtycoverage_update.bak` | 0.116s | 0.187s | 0.303s |
| `filtered_ncci_full.bak` | 0.137s | 0.212s | 0.349s |
| `float_extreme_full.bak` | 0.091s | 0.197s | 0.288s |
| `forwarded_records_full.bak` | 0.477s | 0.424s | 0.901s |
| `ghost_records_full.bak` | 0.128s | 0.17s | 0.298s |
| `heapcoverage_large.bak` | 0.12s | 0.195s | 0.315s |
| `heapcoverage_large_50000.bak` | 0.455s | 0.567s | 1.022s |
| `hierarchyid_extract_full.bak` | 0.097s | 0.18s | 0.277s |
| `high_slot_density_full.bak` | 0.158s | 0.263s | 0.421s |
| `identity_coverage_full.bak` | 0.144s | 0.287s | 0.431s |
| `incrementalcoverage_diff_01.bak` | 0.106s | 0.218s | 0.324s |
| `incrementalcoverage_diff_02.bak` | 0.091s | 0.216s | 0.307s |
| `incrementalcoverage_diff_03.bak` | 0.072s | 0.222s | 0.294s |
| `incrementalcoverage_diff_04.bak` | 0.102s | 0.214s | 0.316s |
| `incrementalcoverage_diff_05.bak` | 0.072s | 0.229s | 0.301s |
| `incrementalcoverage_diff_06.bak` | 0.075s | 0.389s | 0.464s |
| `incrementalcoverage_full.bak` | 0.088s | 0.192s | 0.28s |
| `layoutcoverage_full.bak` | 0.754s | 1.499s | 2.253s |
| `max_row_width_full.bak` | 0.094s | 0.19s | 0.284s |
| `mixed_collation_full.bak` | 0.092s | 0.198s | 0.29s |
| `multi_rowgroup_full.bak` | 0.099s | 0.202s | 0.301s |
| `ncci_heap_full.bak` | 0.12s | 0.247s | 0.367s |
| `ncci_types_full.bak` | 0.522s | 0.717s | 1.239s |
| `ndfcoverage_full.bak` | 0.119s | 0.208s | 0.327s |
| `nvarchar_max_u21_full.bak` | 0.102s | 0.194s | 0.296s |
| `pagecomp_anchor_full.bak` | 0.275s | 0.256s | 0.531s |
| `pagecomp_long_prefix_full.bak` | 0.092s | 0.212s | 0.304s |
| `pfor_columnstore_full.bak` | 0.496s | 0.844s | 1.34s |
| `pfor_columnstore_random_full.bak` | 0.488s | 0.823s | 1.311s |
| `realworld_numeric_digest_full.bak` | 0.212s | 0.292s | 0.504s |
| `rowboundary_full.bak` | 0.125s | 0.216s | 0.341s |
| `rowstore_hash_pii_full.bak` | 0.095s | 0.361s | 0.456s |
| `rowstore_lob_image_full.bak` | 0.108s | 0.203s | 0.311s |
| `rowstore_lob_markup_full.bak` | 0.107s | 0.19s | 0.297s |
| `rowversion_extract_full.bak` | 0.098s | 0.2s | 0.298s |
| `sparse_full.bak` | 0.226s | 0.243s | 0.469s |
| `spatial_edge_full.bak` | 0.099s | 0.205s | 0.304s |
| `spatial_index_full.bak` | 0.125s | 0.197s | 0.322s |
| `sql_variant_extract_full.bak` | 0.119s | 0.197s | 0.316s |
| `striped_full_1.bak` | 0.08s | 0.18s | 0.26s |
| `striped_single.bak` | 0.145s | 0.183s | 0.328s |
| `surrogate_pairs_full.bak` | 0.094s | 0.193s | 0.287s |
| `tabletype_cci_large_full.bak` | 0.209s | 0.319s | 0.528s |
| `tabletypecoverage_diff.bak` | 0.373s | 0.969s | 1.342s |
| `tabletypecoverage_full.bak` | 0.469s | 0.92s | 1.389s |
| `tde_full.bak` | 0s | 1.599s | 1.599s |
| `temporal_hidden_full.bak` | 0.186s | 0.241s | 0.427s |
| `torn_page_full.bak` | 0.092s | 0.284s | 0.376s |
| `typecoverage_full.bak` | 0.384s | 0.81s | 1.194s |
| `typed_xml_full.bak` | 0.092s | 0.191s | 0.283s |
| `unicode_codepage_coverage.bak` | 0.237s | 0.455s | 0.692s |
| `xml_index_full.bak` | 0.113s | 0.197s | 0.31s |
| `xmlcoverage_full.bak` | 0.107s | 0.191s | 0.298s |
| `xmlheap_full.bak` | 0.24s | 0.243s | 0.483s |
| `xtp_checkpoint_straddle_full.bak` | 2.125s | 0.186s | 2.311s |
| `xtp_probe_full.bak` | 0.196s | 0.116s | 0.312s |
| `xtp_rich_full.bak` | 0.134s | 0.085s | 0.219s |
| `xtp_simple_full.bak` | 0.132s | 0.083s | 0.215s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis). See **Sink read breakdown** below for the per-phase split._

## Extract phase breakdown

| Backup | pagestore | schema | catalog | constraints | logtail | xtp | data decode (net) | sink write | arrow verify | sink finish |
|--------|----------:|-------:|--------:|------------:|--------:|---:|------------------:|-----------:|-------------:|------------:|
| `alias_types_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.02s | 0.016s | 0.02s |
| `archive_columnstore_partition_full.bak` | 0.124s | 0.033s | 0.0s | 0.0s | 0.025s | 0.0s | 0.96s | 0.555s | 0.161s | 0.049s |
| `archive_columnstore_types_full.bak` | 0.054s | 0.027s | 0.0s | 0.0s | 0.013s | 0.0s | 0.658s | 0.39s | 0.401s | 0.033s |
| `archive_columnstore_types_random_full.bak` | 0.049s | 0.027s | 0.0s | 0.0s | 0.012s | 0.0s | 0.801s | 0.486s | 0.476s | 0.033s |
| `archive_single_chunk_full.bak` | 0.039s | 0.027s | 0.0s | 0.0s | 0.008s | 0.0s | 0.006s | 0.017s | 0.014s | 0.018s |
| `archive_single_chunk_random_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.005s | 0.03s | 0.023s | 0.031s |
| `archivenull_full.bak` | 0.042s | 0.026s | 0.0s | 0.0s | 0.01s | 0.0s | 0.095s | 0.057s | 0.102s | 0.111s |
| `backup_blocksize_full.bak` | 0.028s | 0.024s | 0.0s | 0.0s | 0.006s | 0.0s | 0.018s | 0.023s | 0.018s | 0.007s |
| `boundarycoverage_datetime_full.bak` | 0.044s | 0.028s | 0.0s | 0.0s | 0.018s | 0.0s | 0.32s | 0.191s | 0.291s | 0.012s |
| `boundarycoverage_full.bak` | 0.041s | 0.028s | 0.0s | 0.0s | 0.009s | 0.0s | 0.04s | 0.045s | 0.023s | 0.01s |
| `cci_binary_varbinary_compare_full.bak` | 0.042s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.005s | 0.016s | 0.016s | 0.019s |
| `cci_bitpack_probe_bigint_full.bak` | 0.47s | 0.06s | 0.0s | 0.0s | 0.088s | 0.0s | 1.442s | 0.716s | 0.801s | 0.202s |
| `cci_bitpack_probe_full.bak` | 0.06s | 0.034s | 0.0s | 0.0s | 0.02s | 0.0s | 0.177s | 0.088s | 0.142s | 0.023s |
| `cci_bitpack_probe_highbase_full.bak` | 0.066s | 0.034s | 0.0s | 0.0s | 0.016s | 0.0s | 0.11s | 0.072s | 0.089s | 0.022s |
| `cci_btree_nci_full.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.008s | 0.0s | 0.024s | 0.022s | 0.013s | 0.01s |
| `cci_computed_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.027s | 0.0s | 0.022s | 0.027s | 0.02s | 0.008s |
| `cci_enc5_largepool_full.bak` | 0.086s | 0.032s | 0.0s | 0.0s | 0.02s | 0.0s | 0.439s | 0.065s | 0.166s | 0.01s |
| `cci_enc5_largepool_matrix_full.bak` | 0.25s | 0.054s | 0.0s | 0.0s | 0.045s | 0.0s | 7.662s | 0.582s | 0.556s | 0.098s |
| `cci_extended_full.bak` | 0.046s | 0.028s | 0.0s | 0.0s | 0.009s | 0.0s | 0.034s | 0.032s | 0.017s | 0.011s |
| `cci_lob_full.bak` | 0.037s | 0.027s | 0.0s | 0.0s | 0.03s | 0.0s | 0.032s | 0.033s | 0.015s | 0.007s |
| `cci_reorganize_full.bak` | 0.036s | 0.027s | 0.0s | 0.0s | 0.025s | 0.0s | 0.019s | 0.024s | 0.016s | 0.008s |
| `cci_string_dict_regression_full.bak` | 0.089s | 0.03s | 0.0s | 0.0s | 0.019s | 0.0s | 0.407s | 0.066s | 0.122s | 0.014s |
| `cci_string_minmax_full.bak` | 0.034s | 0.027s | 0.0s | 0.0s | 0.007s | 0.0s | 0.023s | 0.021s | 0.016s | 0.007s |
| `cci_switch_full.bak` | 0.031s | 0.026s | 0.0s | 0.0s | 0.026s | 0.0s | 0.015s | 0.017s | 0.015s | 0.007s |
| `cci_types_large_full.bak` | 0.036s | 0.027s | 0.0s | 0.0s | 0.009s | 0.0s | 0.044s | 0.052s | 0.02s | 0.013s |
| `cci_varbinary_micro_full.bak` | 0.036s | 0.027s | 0.0s | 0.0s | 0.027s | 0.0s | 0.025s | 0.025s | 0.013s | 0.006s |
| `cci_varbinary_probe_full.bak` | 0.038s | 0.027s | 0.0s | 0.0s | 0.026s | 0.0s | 0.049s | 0.027s | 0.044s | 0.006s |
| `columnstore_minimal.bak` | 0.05s | 0.029s | 0.0s | 0.0s | 0.023s | 0.0s | 0.308s | 1.093s | 1.71s | 1.503s |
| `compressed_nvarchar_full.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.02s | 0.015s | 0.02s |
| `compressioncoverage_full.bak` | 0.037s | 0.03s | 0.0s | 0.0s | 0.026s | 0.0s | 0.365s | 0.266s | 0.258s | 0.006s |
| `computedcoverage_full.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.006s | 0.0s | 0.017s | 0.021s | 0.014s | 0.005s |
| `constraintcoverage_full.bak` | 0.038s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.049s | 0.056s | 0.02s | 0.008s |
| `covering_index_full.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.02s | 0.0s | 0.022s | 0.021s | 0.017s | 0.003s |
| `cs_lob_preamble.bak` | 0.087s | 0.027s | 0.0s | 0.0s | 0.001s | 0.0s | 0.018s | 0.026s | 0.026s | 0.03s |
| `delta_rowgroup_full.bak` | 0.032s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.016s | 0.021s | 0.015s | 0.007s |
| `dirtycoverage_aborted_xact.bak` | 0.033s | 0.031s | 0.0s | 0.0s | 0.026s | 0.0s | 0.002s | 0.022s | 0.015s | 0.022s |
| `dirtycoverage_addcol.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.02s | 0.015s | 0.019s |
| `dirtycoverage_addnotnull.bak` | 0.032s | 0.026s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.017s | 0.014s | 0.016s |
| `dirtycoverage_alldirty.bak` | 0.033s | 0.027s | 0.0s | 0.0s | 0.029s | 0.0s | 0.001s | 0.003s | 0.0s | 0.003s |
| `dirtycoverage_altercol.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.018s | 0.015s | 0.018s |
| `dirtycoverage_altercol_rewrite.bak` | 0.03s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.014s | 0.014s | 0.014s |
| `dirtycoverage_alterdb.bak` | 0.043s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.018s | 0.017s | 0.018s |
| `dirtycoverage_cci_delete.bak` | 0.037s | 0.026s | 0.0s | 0.0s | 0.034s | 0.0s | 0.095s | 0.037s | 0.061s | 0.014s |
| `dirtycoverage_cci_update.bak` | 0.04s | 0.027s | 0.0s | 0.0s | 0.033s | 0.0s | 0.1s | 0.035s | 0.059s | 0.01s |
| `dirtycoverage_committed_delete.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.01s | 0.0s | 0.001s | 0.021s | 0.021s | 0.021s |
| `dirtycoverage_committed_delete_v2.bak` | 0.053s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.003s | 0.018s | 0.019s | 0.019s |
| `dirtycoverage_committed_delete_v3.bak` | 0.034s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.01s | 0.045s | 0.098s | 0.103s |
| `dirtycoverage_committed_delete_v4.bak` | 0.04s | 0.025s | 0.0s | 0.0s | 0.085s | 0.0s | 0.125s | 0.032s | 0.084s | 0.008s |
| `dirtycoverage_committed_update.bak` | 0.036s | 0.027s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.02s | 0.016s | 0.02s |
| `dirtycoverage_committed_update_v2.bak` | 0.032s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.003s | 0.017s | 0.018s | 0.019s |
| `dirtycoverage_committed_update_v3.bak` | 0.034s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.013s | 0.051s | 0.09s | 0.094s |
| `dirtycoverage_committed_update_v4.bak` | 0.039s | 0.026s | 0.0s | 0.0s | 0.092s | 0.0s | 0.138s | 0.031s | 0.087s | 0.004s |
| `dirtycoverage_concurrent.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.024s | 0.0s | 0.002s | 0.018s | 0.013s | 0.018s |
| `dirtycoverage_createidx.bak` | 0.042s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.017s | 0.016s | 0.017s |
| `dirtycoverage_createtable.bak` | 0.039s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.018s | 0.017s | 0.018s |
| `dirtycoverage_delete.bak` | 0.03s | 0.026s | 0.0s | 0.0s | 0.025s | 0.0s | 0.002s | 0.017s | 0.014s | 0.017s |
| `dirtycoverage_dropcol.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.024s | 0.0s | 0.002s | 0.02s | 0.016s | 0.021s |
| `dirtycoverage_dropidx.bak` | 0.03s | 0.025s | 0.0s | 0.0s | 0.022s | 0.0s | 0.002s | 0.019s | 0.015s | 0.019s |
| `dirtycoverage_droptable.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.02s | 0.02s | 0.016s | 0.003s |
| `dirtycoverage_heap_forward.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.025s | 0.0s | 0.001s | 0.021s | 0.034s | 0.034s |
| `dirtycoverage_large_dirty.bak` | 0.035s | 0.025s | 0.0s | 0.0s | 0.357s | 0.0s | 0.008s | 0.029s | 0.027s | 0.03s |
| `dirtycoverage_lob_update.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.044s | 0.0s | 0.002s | 0.018s | 0.017s | 0.018s |
| `dirtycoverage_maxrow.bak` | 0.032s | 0.027s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.02s | 0.02s | 0.02s |
| `dirtycoverage_nchar_delete.bak` | 0.049s | 0.027s | 0.0s | 0.0s | 0.027s | 0.0s | 0.001s | 0.018s | 0.018s | 0.019s |
| `dirtycoverage_nested.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.026s | 0.0s | 0.002s | 0.016s | 0.013s | 0.016s |
| `dirtycoverage_null_update.bak` | 0.032s | 0.025s | 0.0s | 0.0s | 0.025s | 0.0s | 0.002s | 0.015s | 0.012s | 0.015s |
| `dirtycoverage_rebuildidx.bak` | 0.045s | 0.029s | 0.0s | 0.0s | 0.023s | 0.0s | 0.002s | 0.016s | 0.015s | 0.016s |
| `dirtycoverage_rich_insert.bak` | 0.034s | 0.025s | 0.0s | 0.0s | 0.025s | 0.0s | 0.002s | 0.035s | 0.067s | 0.068s |
| `dirtycoverage_rich_update.bak` | 0.032s | 0.026s | 0.0s | 0.0s | 0.025s | 0.0s | 0.002s | 0.04s | 0.085s | 0.087s |
| `dirtycoverage_savepoint.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.027s | 0.0s | 0.002s | 0.018s | 0.013s | 0.018s |
| `dirtycoverage_snapshot_update.bak` | 0.029s | 0.025s | 0.0s | 0.0s | 0.025s | 0.0s | 0.001s | 0.017s | 0.014s | 0.017s |
| `dirtycoverage_switch.bak` | 0.041s | 0.026s | 0.0s | 0.0s | 0.027s | 0.0s | 0.019s | 0.02s | 0.015s | 0.005s |
| `dirtycoverage_temporal_update.bak` | 0.03s | 0.025s | 0.0s | 0.0s | 0.028s | 0.0s | 0.057s | 0.015s | 0.054s | 0.001s |
| `dirtycoverage_truncate.bak` | 0.03s | 0.025s | 0.0s | 0.0s | 0.022s | 0.0s | 0.003s | 0.014s | 0.014s | 0.014s |
| `dirtycoverage_two_tx.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.027s | 0.0s | 0.002s | 0.017s | 0.014s | 0.017s |
| `dirtycoverage_uncommitted.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.026s | 0.0s | 0.002s | 0.016s | 0.015s | 0.016s |
| `dirtycoverage_update.bak` | 0.03s | 0.027s | 0.0s | 0.0s | 0.029s | 0.0s | 0.002s | 0.017s | 0.014s | 0.017s |
| `filtered_ncci_full.bak` | 0.039s | 0.025s | 0.0s | 0.0s | 0.025s | 0.0s | 0.025s | 0.032s | 0.02s | 0.009s |
| `float_extreme_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.017s | 0.016s | 0.017s |
| `forwarded_records_full.bak` | 0.103s | 0.041s | 0.0s | 0.0s | 0.02s | 0.0s | 0.219s | 0.078s | 0.161s | 0.077s |
| `ghost_records_full.bak` | 0.035s | 0.025s | 0.0s | 0.0s | 0.016s | 0.0s | 0.001s | 0.025s | 0.038s | 0.039s |
| `heapcoverage_large.bak` | 0.031s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.021s | 0.029s | 0.042s | 0.025s |
| `heapcoverage_large_50000.bak` | 0.091s | 0.038s | 0.0s | 0.0s | 0.029s | 0.0s | 0.152s | 0.069s | 0.171s | 0.122s |
| `hierarchyid_extract_full.bak` | 0.031s | 0.026s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.022s | 0.015s | 0.022s |
| `high_slot_density_full.bak` | 0.05s | 0.028s | 0.0s | 0.0s | 0.011s | 0.0s | 0.042s | 0.031s | 0.042s | 0.016s |
| `identity_coverage_full.bak` | 0.034s | 0.026s | 0.0s | 0.0s | 0.021s | 0.0s | 0.045s | 0.049s | 0.014s | 0.006s |
| `incrementalcoverage_diff_01.bak` | 0.013s | 0.023s | 0.0s | 0.0s | 0.044s | 0.0s | 0.001s | 0.023s | 0.019s | 0.023s |
| `incrementalcoverage_diff_02.bak` | 0.014s | 0.024s | 0.0s | 0.0s | 0.024s | 0.0s | 0.001s | 0.025s | 0.02s | 0.025s |
| `incrementalcoverage_diff_03.bak` | 0.012s | 0.023s | 0.0s | 0.0s | 0.015s | 0.0s | 0.001s | 0.018s | 0.015s | 0.018s |
| `incrementalcoverage_diff_04.bak` | 0.015s | 0.047s | 0.0s | 0.0s | 0.017s | 0.0s | 0.001s | 0.019s | 0.015s | 0.02s |
| `incrementalcoverage_diff_05.bak` | 0.011s | 0.024s | 0.0s | 0.0s | 0.015s | 0.0s | 0.002s | 0.017s | 0.014s | 0.017s |
| `incrementalcoverage_diff_06.bak` | 0.012s | 0.022s | 0.0s | 0.0s | 0.018s | 0.0s | 0.001s | 0.019s | 0.018s | 0.019s |
| `incrementalcoverage_full.bak` | 0.029s | 0.026s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.017s | 0.014s | 0.017s |
| `layoutcoverage_full.bak` | 0.063s | 0.096s | 0.0s | 0.0s | 0.021s | 0.0s | 0.541s | 0.504s | 0.225s | 0.02s |
| `max_row_width_full.bak` | 0.033s | 0.026s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.016s | 0.015s | 0.016s |
| `mixed_collation_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.002s | 0.016s | 0.013s | 0.016s |
| `multi_rowgroup_full.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.008s | 0.0s | 0.016s | 0.019s | 0.015s | 0.006s |
| `ncci_heap_full.bak` | 0.04s | 0.025s | 0.0s | 0.0s | 0.023s | 0.0s | 0.018s | 0.018s | 0.014s | 0.003s |
| `ncci_types_full.bak` | 0.058s | 0.032s | 0.0s | 0.0s | 0.034s | 0.0s | 0.373s | 0.241s | 0.313s | 0.011s |
| `ndfcoverage_full.bak` | 0.033s | 0.026s | 0.0s | 0.0s | 0.01s | 0.0s | 0.02s | 0.03s | 0.019s | 0.012s |
| `nvarchar_max_u21_full.bak` | 0.045s | 0.025s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.016s | 0.012s | 0.016s |
| `pagecomp_anchor_full.bak` | 0.035s | 0.027s | 0.0s | 0.0s | 0.007s | 0.0s | 0.103s | 0.019s | 0.092s | 0.094s |
| `pagecomp_long_prefix_full.bak` | 0.032s | 0.024s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.017s | 0.016s | 0.017s |
| `pfor_columnstore_full.bak` | 0.065s | 0.029s | 0.0s | 0.0s | 0.012s | 0.0s | 0.216s | 0.142s | 0.308s | 0.16s |
| `pfor_columnstore_random_full.bak` | 0.062s | 0.029s | 0.0s | 0.0s | 0.013s | 0.0s | 0.214s | 0.139s | 0.308s | 0.161s |
| `realworld_numeric_digest_full.bak` | 0.047s | 0.025s | 0.0s | 0.0s | 0.031s | 0.0s | 0.081s | 0.069s | 0.076s | 0.012s |
| `rowboundary_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.042s | 0.03s | 0.04s | 0.006s |
| `rowstore_hash_pii_full.bak` | 0.034s | 0.025s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.018s | 0.017s | 0.018s |
| `rowstore_lob_image_full.bak` | 0.043s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.002s | 0.018s | 0.017s | 0.018s |
| `rowstore_lob_markup_full.bak` | 0.033s | 0.027s | 0.0s | 0.0s | 0.009s | 0.0s | 0.002s | 0.022s | 0.02s | 0.022s |
| `rowversion_extract_full.bak` | 0.033s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.017s | 0.021s | 0.016s | 0.005s |
| `sparse_full.bak` | 0.033s | 0.027s | 0.0s | 0.0s | 0.007s | 0.0s | 0.055s | 0.023s | 0.093s | 0.094s |
| `spatial_edge_full.bak` | 0.031s | 0.026s | 0.0s | 0.0s | 0.007s | 0.0s | 0.018s | 0.024s | 0.017s | 0.007s |
| `spatial_index_full.bak` | 0.036s | 0.025s | 0.0s | 0.0s | 0.02s | 0.0s | 0.027s | 0.019s | 0.016s | 0.004s |
| `sql_variant_extract_full.bak` | 0.043s | 0.028s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.02s | 0.015s | 0.021s |
| `striped_full_1.bak` | 0.027s | 0.023s | 0.0s | 0.0s | 0.005s | 0.0s | 0.001s | 0.021s | 0.016s | 0.021s |
| `striped_single.bak` | 0.079s | 0.025s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s | 0.017s | 0.012s | 0.017s |
| `surrogate_pairs_full.bak` | 0.033s | 0.025s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.016s | 0.015s | 0.016s |
| `tabletype_cci_large_full.bak` | 0.051s | 0.028s | 0.0s | 0.0s | 0.011s | 0.0s | 0.016s | 0.032s | 0.081s | 0.091s |
| `tabletypecoverage_diff.bak` | 0.02s | 0.026s | 0.0s | 0.0s | 0.037s | 0.0s | 0.249s | 0.117s | 0.217s | 0.038s |
| `tabletypecoverage_full.bak` | 0.101s | 0.035s | 0.0s | 0.0s | 0.036s | 0.0s | 0.26s | 0.098s | 0.215s | 0.024s |
| `temporal_hidden_full.bak` | 0.037s | 0.027s | 0.0s | 0.0s | 0.007s | 0.0s | 0.099s | 0.047s | 0.096s | 0.007s |
| `torn_page_full.bak` | 0.03s | 0.026s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.019s | 0.018s | 0.019s |
| `typecoverage_full.bak` | 0.05s | 0.029s | 0.0s | 0.0s | 0.016s | 0.0s | 0.265s | 0.209s | 0.108s | 0.008s |
| `typed_xml_full.bak` | 0.031s | 0.025s | 0.0s | 0.0s | 0.007s | 0.0s | 0.001s | 0.017s | 0.015s | 0.018s |
| `unicode_codepage_coverage.bak` | 0.038s | 0.028s | 0.0s | 0.0s | 0.01s | 0.0s | 0.125s | 0.148s | 0.02s | 0.026s |
| `xml_index_full.bak` | 0.031s | 0.026s | 0.0s | 0.0s | 0.022s | 0.0s | 0.018s | 0.022s | 0.014s | 0.005s |
| `xmlcoverage_full.bak` | 0.04s | 0.028s | 0.0s | 0.0s | 0.006s | 0.0s | 0.001s | 0.018s | 0.014s | 0.018s |
| `xmlheap_full.bak` | 0.054s | 0.031s | 0.0s | 0.0s | 0.011s | 0.0s | 0.04s | 0.021s | 0.091s | 0.092s |
| `xtp_checkpoint_straddle_full.bak` | 0.311s | 0.027s | 0.0s | 0.0s | 0.006s | 1.602s | 0.075s | 0.092s | 0.027s | 0.075s |
| `xtp_probe_full.bak` | 0.06s | 0.027s | 0.0s | 0.0s | 0.054s | 0.005s | 0.013s | 0.018s | 0.0s | 0.006s |
| `xtp_rich_full.bak` | 0.044s | 0.026s | 0.0s | 0.0s | 0.034s | 0.005s | 0.001s | 0.01s | 0.0s | 0.01s |
| `xtp_simple_full.bak` | 0.039s | 0.027s | 0.0s | 0.0s | 0.033s | 0.005s | 0.001s | 0.016s | 0.0s | 0.016s |

_data decode (net) = data\_decode\_s (raw loop wall; sink writes and arrow verify overlap decode on a background writer thread and are drained in sink finish). catalog = recover\_catalog\_objects (indexes/FKs/constraints, pg\_dir only). arrow verify = cell verification run inside extraction (_StreamingStatsSink). verify=digest: per-column SHA-256 aggregate hash — fast, no GT parquet read, catches multiset-level corruption; also runs key-ordered digest (catches row transposition) when ordered\_digest is present in the manifest (populated by backfill\_ordered\_digest). Mismatches show as digest:col (multiset) or order:col (transposition). verify=full: exhaustive keyed row compare — also catches value-preserving row misalignment._

## Sink write timings

| Backup | delta write | delta read | pg_dir write | pg_dir read |
|--------|-------:| ------: | -------:| ------:|
| `alias_types_full.bak` | 0.003s | 0.025s | 0.017s | 0.006s |
| `archive_columnstore_partition_full.bak` | 0.186s | 0.224s | 0.369s | 0.674s |
| `archive_columnstore_types_full.bak` | 0.057s | 0.382s | 0.333s | 0.511s |
| `archive_columnstore_types_random_full.bak` | 0.118s | 0.384s | 0.368s | 0.52s |
| `archive_single_chunk_full.bak` | 0.009s | 0.03s | 0.008s | 0.01s |
| `archive_single_chunk_random_full.bak` | 0.023s | 0.038s | 0.007s | 0.009s |
| `archivenull_full.bak` | 0.027s | 0.087s | 0.03s | 0.123s |
| `backup_blocksize_full.bak` | 0.01s | 0.036s | 0.013s | 0.01s |
| `boundarycoverage_datetime_full.bak` | 0.046s | 0.196s | 0.145s | 0.146s |
| `boundarycoverage_full.bak` | 0.027s | 0.087s | 0.018s | 0.054s |
| `cci_binary_varbinary_compare_full.bak` | 0.007s | 0.03s | 0.009s | 0.011s |
| `cci_bitpack_probe_bigint_full.bak` | 0.362s | 0.799s | 0.354s | 0.894s |
| `cci_bitpack_probe_full.bak` | 0.036s | 0.226s | 0.052s | 0.187s |
| `cci_bitpack_probe_highbase_full.bak` | 0.025s | 0.115s | 0.047s | 0.121s |
| `cci_btree_nci_full.bak` | 0.011s | 0.054s | 0.011s | 0.017s |
| `cci_computed_full.bak` | 0.017s | 0.044s | 0.01s | 0.009s |
| `cci_enc5_largepool_full.bak` | 0.027s | 0.145s | 0.038s | 0.21s |
| `cci_enc5_largepool_matrix_full.bak` | 0.095s | 0.609s | 0.487s | 0.76s |
| `cci_extended_full.bak` | 0.019s | 0.058s | 0.013s | 0.034s |
| `cci_lob_full.bak` | 0.014s | 0.052s | 0.019s | 0.021s |
| `cci_reorganize_full.bak` | 0.015s | 0.045s | 0.009s | 0.016s |
| `cci_string_dict_regression_full.bak` | 0.023s | 0.105s | 0.043s | 0.12s |
| `cci_string_minmax_full.bak` | 0.011s | 0.04s | 0.01s | 0.014s |
| `cci_switch_full.bak` | 0.008s | 0.04s | 0.009s | 0.01s |
| `cci_types_large_full.bak` | 0.023s | 0.082s | 0.029s | 0.04s |
| `cci_varbinary_micro_full.bak` | 0.015s | 0.049s | 0.01s | 0.019s |
| `cci_varbinary_probe_full.bak` | 0.02s | 0.032s | 0.007s | 0.028s |
| `columnstore_minimal.bak` | 0.034s | 0.88s | 1.059s | 0.74s |
| `compressed_nvarchar_full.bak` | 0.005s | 0.034s | 0.015s | 0.006s |
| `compressioncoverage_full.bak` | 0.082s | 0.248s | 0.184s | 0.231s |
| `computedcoverage_full.bak` | 0.009s | 0.04s | 0.012s | 0.012s |
| `constraintcoverage_full.bak` | 0.039s | 0.089s | 0.017s | 0.049s |
| `covering_index_full.bak` | 0.016s | 0.036s | 0.005s | 0.012s |
| `cs_lob_preamble.bak` | 0.012s | 0.035s | 0.014s | 0.01s |
| `delta_rowgroup_full.bak` | 0.009s | 0.034s | 0.012s | 0.011s |
| `dirtycoverage_aborted_xact.bak` | 0.018s | 0.03s | 0.004s | 0.006s |
| `dirtycoverage_addcol.bak` | 0.007s | 0.03s | 0.013s | 0.006s |
| `dirtycoverage_addnotnull.bak` | 0.009s | 0.029s | 0.008s | 0.007s |
| `dirtycoverage_alldirty.bak` | 0.0s | 0.0s | 0.003s | 0.001s |
| `dirtycoverage_altercol.bak` | 0.008s | 0.029s | 0.01s | 0.007s |
| `dirtycoverage_altercol_rewrite.bak` | 0.004s | 0.028s | 0.01s | 0.005s |
| `dirtycoverage_alterdb.bak` | 0.005s | 0.031s | 0.013s | 0.009s |
| `dirtycoverage_cci_delete.bak` | 0.013s | 0.044s | 0.024s | 0.045s |
| `dirtycoverage_cci_update.bak` | 0.012s | 0.043s | 0.023s | 0.043s |
| `dirtycoverage_committed_delete.bak` | 0.012s | 0.032s | 0.009s | 0.007s |
| `dirtycoverage_committed_delete_v2.bak` | 0.006s | 0.031s | 0.012s | 0.009s |
| `dirtycoverage_committed_delete_v3.bak` | 0.008s | 0.053s | 0.037s | 0.04s |
| `dirtycoverage_committed_delete_v4.bak` | 0.012s | 0.051s | 0.02s | 0.04s |
| `dirtycoverage_committed_update.bak` | 0.004s | 0.028s | 0.016s | 0.007s |
| `dirtycoverage_committed_update_v2.bak` | 0.008s | 0.032s | 0.009s | 0.009s |
| `dirtycoverage_committed_update_v3.bak` | 0.007s | 0.056s | 0.044s | 0.043s |
| `dirtycoverage_committed_update_v4.bak` | 0.011s | 0.058s | 0.02s | 0.044s |
| `dirtycoverage_concurrent.bak` | 0.005s | 0.027s | 0.013s | 0.006s |
| `dirtycoverage_createidx.bak` | 0.006s | 0.032s | 0.011s | 0.007s |
| `dirtycoverage_createtable.bak` | 0.009s | 0.027s | 0.009s | 0.008s |
| `dirtycoverage_delete.bak` | 0.006s | 0.029s | 0.011s | 0.008s |
| `dirtycoverage_dropcol.bak` | 0.017s | 0.036s | 0.003s | 0.01s |
| `dirtycoverage_dropidx.bak` | 0.015s | 0.042s | 0.004s | 0.006s |
| `dirtycoverage_droptable.bak` | 0.008s | 0.037s | 0.012s | 0.013s |
| `dirtycoverage_heap_forward.bak` | 0.005s | 0.008s | 0.016s | 0.007s |
| `dirtycoverage_large_dirty.bak` | 0.019s | 0.032s | 0.01s | 0.006s |
| `dirtycoverage_lob_update.bak` | 0.007s | 0.027s | 0.011s | 0.006s |
| `dirtycoverage_maxrow.bak` | 0.009s | 0.032s | 0.011s | 0.01s |
| `dirtycoverage_nchar_delete.bak` | 0.007s | 0.033s | 0.011s | 0.008s |
| `dirtycoverage_nested.bak` | 0.005s | 0.034s | 0.011s | 0.007s |
| `dirtycoverage_null_update.bak` | 0.007s | 0.027s | 0.008s | 0.007s |
| `dirtycoverage_rebuildidx.bak` | 0.004s | 0.032s | 0.012s | 0.008s |
| `dirtycoverage_rich_insert.bak` | 0.005s | 0.012s | 0.03s | 0.009s |
| `dirtycoverage_rich_update.bak` | 0.009s | 0.013s | 0.031s | 0.01s |
| `dirtycoverage_savepoint.bak` | 0.005s | 0.032s | 0.013s | 0.005s |
| `dirtycoverage_snapshot_update.bak` | 0.006s | 0.029s | 0.011s | 0.005s |
| `dirtycoverage_switch.bak` | 0.009s | 0.036s | 0.011s | 0.011s |
| `dirtycoverage_temporal_update.bak` | 0.005s | 0.028s | 0.01s | 0.007s |
| `dirtycoverage_truncate.bak` | 0.006s | 0.026s | 0.008s | 0.006s |
| `dirtycoverage_two_tx.bak` | 0.006s | 0.031s | 0.011s | 0.005s |
| `dirtycoverage_uncommitted.bak` | 0.005s | 0.029s | 0.011s | 0.009s |
| `dirtycoverage_update.bak` | 0.006s | 0.029s | 0.011s | 0.008s |
| `filtered_ncci_full.bak` | 0.014s | 0.039s | 0.018s | 0.015s |
| `float_extreme_full.bak` | 0.005s | 0.031s | 0.012s | 0.008s |
| `forwarded_records_full.bak` | 0.029s | 0.101s | 0.049s | 0.118s |
| `ghost_records_full.bak` | 0.006s | 0.01s | 0.019s | 0.008s |
| `heapcoverage_large.bak` | 0.015s | 0.025s | 0.014s | 0.017s |
| `heapcoverage_large_50000.bak` | 0.029s | 0.16s | 0.04s | 0.202s |
| `hierarchyid_extract_full.bak` | 0.01s | 0.027s | 0.012s | 0.005s |
| `high_slot_density_full.bak` | 0.014s | 0.068s | 0.017s | 0.045s |
| `identity_coverage_full.bak` | 0.029s | 0.082s | 0.02s | 0.038s |
| `incrementalcoverage_diff_01.bak` | 0.014s | 0.035s | 0.009s | 0.008s |
| `incrementalcoverage_diff_02.bak` | 0.016s | 0.034s | 0.009s | 0.006s |
| `incrementalcoverage_diff_03.bak` | 0.009s | 0.032s | 0.009s | 0.008s |
| `incrementalcoverage_diff_04.bak` | 0.01s | 0.036s | 0.009s | 0.007s |
| `incrementalcoverage_diff_05.bak` | 0.009s | 0.048s | 0.008s | 0.007s |
| `incrementalcoverage_diff_06.bak` | 0.008s | 0.029s | 0.011s | 0.007s |
| `incrementalcoverage_full.bak` | 0.005s | 0.03s | 0.012s | 0.007s |
| `layoutcoverage_full.bak` | 0.289s | 0.621s | 0.215s | 0.45s |
| `max_row_width_full.bak` | 0.007s | 0.029s | 0.009s | 0.007s |
| `mixed_collation_full.bak` | 0.007s | 0.03s | 0.009s | 0.009s |
| `multi_rowgroup_full.bak` | 0.008s | 0.036s | 0.011s | 0.011s |
| `ncci_heap_full.bak` | 0.008s | 0.036s | 0.01s | 0.014s |
| `ncci_types_full.bak` | 0.084s | 0.321s | 0.157s | 0.214s |
| `ndfcoverage_full.bak` | 0.019s | 0.041s | 0.011s | 0.011s |
| `nvarchar_max_u21_full.bak` | 0.008s | 0.029s | 0.008s | 0.007s |
| `pagecomp_anchor_full.bak` | 0.006s | 0.057s | 0.013s | 0.041s |
| `pagecomp_long_prefix_full.bak` | 0.005s | 0.045s | 0.012s | 0.01s |
| `pfor_columnstore_full.bak` | 0.049s | 0.345s | 0.093s | 0.343s |
| `pfor_columnstore_random_full.bak` | 0.048s | 0.337s | 0.091s | 0.333s |
| `realworld_numeric_digest_full.bak` | 0.028s | 0.066s | 0.041s | 0.055s |
| `rowboundary_full.bak` | 0.012s | 0.032s | 0.018s | 0.029s |
| `rowstore_hash_pii_full.bak` | 0.008s | 0.031s | 0.01s | 0.017s |
| `rowstore_lob_image_full.bak` | 0.006s | 0.031s | 0.012s | 0.009s |
| `rowstore_lob_markup_full.bak` | 0.012s | 0.03s | 0.01s | 0.007s |
| `rowversion_extract_full.bak` | 0.01s | 0.039s | 0.011s | 0.009s |
| `sparse_full.bak` | 0.008s | 0.053s | 0.015s | 0.039s |
| `spatial_edge_full.bak` | 0.013s | 0.039s | 0.011s | 0.009s |
| `spatial_index_full.bak` | 0.008s | 0.036s | 0.011s | 0.012s |
| `sql_variant_extract_full.bak` | 0.007s | 0.033s | 0.013s | 0.006s |
| `striped_full_1.bak` | 0.012s | 0.031s | 0.009s | 0.006s |
| `striped_single.bak` | 0.005s | 0.028s | 0.012s | 0.006s |
| `surrogate_pairs_full.bak` | 0.007s | 0.031s | 0.009s | 0.006s |
| `tabletype_cci_large_full.bak` | 0.014s | 0.052s | 0.018s | 0.094s |
| `tabletypecoverage_diff.bak` | 0.051s | 0.175s | 0.066s | 0.519s |
| `tabletypecoverage_full.bak` | 0.028s | 0.176s | 0.07s | 0.515s |
| `temporal_hidden_full.bak` | 0.023s | 0.04s | 0.024s | 0.034s |
| `torn_page_full.bak` | 0.009s | 0.031s | 0.01s | 0.007s |
| `typecoverage_full.bak` | 0.152s | 0.32s | 0.057s | 0.284s |
| `typed_xml_full.bak` | 0.006s | 0.03s | 0.011s | 0.008s |
| `unicode_codepage_coverage.bak` | 0.121s | 0.137s | 0.027s | 0.143s |
| `xml_index_full.bak` | 0.011s | 0.032s | 0.011s | 0.01s |
| `xmlcoverage_full.bak` | 0.012s | 0.029s | 0.006s | 0.007s |
| `xmlheap_full.bak` | 0.007s | 0.05s | 0.014s | 0.036s |
| `xtp_checkpoint_straddle_full.bak` | 0.019s | 0.055s | 0.073s | 0.11s |
| `xtp_probe_full.bak` | 0.014s | 0.063s | 0.004s | 0.026s |
| `xtp_rich_full.bak` | 0.007s | 0.051s | 0.003s | 0.013s |
| `xtp_simple_full.bak` | 0.007s | 0.054s | 0.009s | 0.009s |

_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._

## Sink read breakdown

| Backup | arrow verify | delta read | delta stats | delta verify | pg_dir read | pg_dir stats | pg_dir verify |
|--------| -------: | -------: | -------: | -------: | -------: | -------: | -------:|
| `alias_types_full.bak` | 0.016s | 0.019s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `archive_columnstore_partition_full.bak` | 0.161s | 0.043s | 0.016s | 0.139s | 0.476s | 0.021s | 0.151s |
| `archive_columnstore_types_full.bak` | 0.401s | 0.026s | 0.004s | 0.307s | 0.151s | 0.005s | 0.312s |
| `archive_columnstore_types_random_full.bak` | 0.476s | 0.023s | 0.004s | 0.313s | 0.159s | 0.005s | 0.311s |
| `archive_single_chunk_full.bak` | 0.014s | 0.022s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `archive_single_chunk_random_full.bak` | 0.023s | 0.03s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `archivenull_full.bak` | 0.102s | 0.005s | 0.001s | 0.067s | 0.064s | 0.002s | 0.051s |
| `backup_blocksize_full.bak` | 0.018s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `boundarycoverage_datetime_full.bak` | 0.291s | 0.042s | 0.001s | 0.098s | 0.01s | 0.001s | 0.084s |
| `boundarycoverage_full.bak` | 0.023s | 0.038s | 0.001s | 0.008s | 0.007s | 0.001s | 0.008s |
| `cci_binary_varbinary_compare_full.bak` | 0.016s | 0.022s | 0.0s | 0.002s | 0.004s | 0.0s | 0.002s |
| `cci_bitpack_probe_bigint_full.bak` | 0.801s | 0.053s | 0.002s | 0.729s | 0.166s | 0.004s | 0.711s |
| `cci_bitpack_probe_full.bak` | 0.142s | 0.042s | 0.0s | 0.163s | 0.023s | 0.001s | 0.145s |
| `cci_bitpack_probe_highbase_full.bak` | 0.089s | 0.027s | 0.0s | 0.056s | 0.038s | 0.001s | 0.069s |
| `cci_btree_nci_full.bak` | 0.013s | 0.039s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_computed_full.bak` | 0.02s | 0.03s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_enc5_largepool_full.bak` | 0.166s | 0.009s | 0.002s | 0.12s | 0.073s | 0.002s | 0.121s |
| `cci_enc5_largepool_matrix_full.bak` | 0.556s | 0.04s | 0.007s | 0.51s | 0.197s | 0.007s | 0.506s |
| `cci_extended_full.bak` | 0.017s | 0.03s | 0.0s | 0.003s | 0.006s | 0.0s | 0.003s |
| `cci_lob_full.bak` | 0.015s | 0.029s | 0.0s | 0.002s | 0.003s | 0.0s | 0.002s |
| `cci_reorganize_full.bak` | 0.016s | 0.026s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_string_dict_regression_full.bak` | 0.122s | 0.015s | 0.003s | 0.069s | 0.036s | 0.003s | 0.067s |
| `cci_string_minmax_full.bak` | 0.016s | 0.027s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `cci_switch_full.bak` | 0.015s | 0.025s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_types_large_full.bak` | 0.02s | 0.043s | 0.001s | 0.005s | 0.008s | 0.0s | 0.004s |
| `cci_varbinary_micro_full.bak` | 0.013s | 0.029s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cci_varbinary_probe_full.bak` | 0.044s | 0.007s | 0.0s | 0.008s | 0.005s | 0.0s | 0.008s |
| `columnstore_minimal.bak` | 1.71s | 0.04s | 0.013s | 0.792s | 0.034s | 0.003s | 0.672s |
| `compressed_nvarchar_full.bak` | 0.015s | 0.027s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `compressioncoverage_full.bak` | 0.258s | 0.051s | 0.005s | 0.094s | 0.02s | 0.005s | 0.112s |
| `computedcoverage_full.bak` | 0.014s | 0.026s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `constraintcoverage_full.bak` | 0.02s | 0.041s | 0.001s | 0.004s | 0.004s | 0.0s | 0.003s |
| `covering_index_full.bak` | 0.017s | 0.024s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `cs_lob_preamble.bak` | 0.026s | 0.026s | 0.0s | 0.002s | 0.003s | 0.0s | 0.001s |
| `delta_rowgroup_full.bak` | 0.015s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_aborted_xact.bak` | 0.015s | 0.024s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_addcol.bak` | 0.015s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_addnotnull.bak` | 0.014s | 0.02s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `dirtycoverage_alldirty.bak` | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s | 0.0s |
| `dirtycoverage_altercol.bak` | 0.015s | 0.022s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_altercol_rewrite.bak` | 0.014s | 0.022s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_alterdb.bak` | 0.017s | 0.022s | 0.0s | 0.0s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_cci_delete.bak` | 0.061s | 0.006s | 0.0s | 0.026s | 0.007s | 0.0s | 0.026s |
| `dirtycoverage_cci_update.bak` | 0.059s | 0.005s | 0.0s | 0.027s | 0.007s | 0.0s | 0.027s |
| `dirtycoverage_committed_delete.bak` | 0.021s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_committed_delete_v2.bak` | 0.019s | 0.023s | 0.0s | 0.003s | 0.003s | 0.0s | 0.002s |
| `dirtycoverage_committed_delete_v3.bak` | 0.098s | 0.023s | 0.001s | 0.021s | 0.005s | 0.001s | 0.025s |
| `dirtycoverage_committed_delete_v4.bak` | 0.084s | 0.024s | 0.0s | 0.017s | 0.01s | 0.0s | 0.019s |
| `dirtycoverage_committed_update.bak` | 0.016s | 0.022s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_committed_update_v2.bak` | 0.018s | 0.023s | 0.0s | 0.003s | 0.002s | 0.0s | 0.003s |
| `dirtycoverage_committed_update_v3.bak` | 0.09s | 0.022s | 0.001s | 0.028s | 0.005s | 0.001s | 0.029s |
| `dirtycoverage_committed_update_v4.bak` | 0.087s | 0.024s | 0.0s | 0.021s | 0.011s | 0.0s | 0.02s |
| `dirtycoverage_concurrent.bak` | 0.013s | 0.021s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_createidx.bak` | 0.016s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_createtable.bak` | 0.017s | 0.021s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_delete.bak` | 0.014s | 0.022s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_dropcol.bak` | 0.016s | 0.029s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `dirtycoverage_dropidx.bak` | 0.015s | 0.035s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_droptable.bak` | 0.016s | 0.025s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_heap_forward.bak` | 0.034s | 0.003s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_large_dirty.bak` | 0.027s | 0.026s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_lob_update.bak` | 0.017s | 0.021s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_maxrow.bak` | 0.02s | 0.024s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_nchar_delete.bak` | 0.018s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_nested.bak` | 0.013s | 0.025s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_null_update.bak` | 0.012s | 0.021s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_rebuildidx.bak` | 0.015s | 0.025s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_rich_insert.bak` | 0.067s | 0.003s | 0.0s | 0.002s | 0.001s | 0.0s | 0.002s |
| `dirtycoverage_rich_update.bak` | 0.085s | 0.004s | 0.0s | 0.002s | 0.002s | 0.0s | 0.003s |
| `dirtycoverage_savepoint.bak` | 0.013s | 0.024s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_snapshot_update.bak` | 0.014s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_switch.bak` | 0.015s | 0.023s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_temporal_update.bak` | 0.054s | 0.022s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_truncate.bak` | 0.014s | 0.021s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `dirtycoverage_two_tx.bak` | 0.014s | 0.024s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `dirtycoverage_uncommitted.bak` | 0.015s | 0.022s | 0.0s | 0.0s | 0.002s | 0.0s | 0.001s |
| `dirtycoverage_update.bak` | 0.014s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `filtered_ncci_full.bak` | 0.02s | 0.024s | 0.0s | 0.002s | 0.002s | 0.0s | 0.001s |
| `float_extreme_full.bak` | 0.016s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `forwarded_records_full.bak` | 0.161s | 0.014s | 0.001s | 0.068s | 0.03s | 0.001s | 0.07s |
| `ghost_records_full.bak` | 0.038s | 0.003s | 0.0s | 0.002s | 0.001s | 0.0s | 0.002s |
| `heapcoverage_large.bak` | 0.042s | 0.008s | 0.0s | 0.004s | 0.003s | 0.0s | 0.004s |
| `heapcoverage_large_50000.bak` | 0.171s | 0.011s | 0.002s | 0.129s | 0.054s | 0.007s | 0.126s |
| `hierarchyid_extract_full.bak` | 0.015s | 0.021s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `high_slot_density_full.bak` | 0.042s | 0.029s | 0.0s | 0.026s | 0.005s | 0.0s | 0.025s |
| `identity_coverage_full.bak` | 0.014s | 0.035s | 0.001s | 0.002s | 0.004s | 0.0s | 0.002s |
| `incrementalcoverage_diff_01.bak` | 0.019s | 0.026s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `incrementalcoverage_diff_02.bak` | 0.02s | 0.026s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `incrementalcoverage_diff_03.bak` | 0.015s | 0.025s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `incrementalcoverage_diff_04.bak` | 0.015s | 0.027s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `incrementalcoverage_diff_05.bak` | 0.014s | 0.042s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `incrementalcoverage_diff_06.bak` | 0.018s | 0.022s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `incrementalcoverage_full.bak` | 0.014s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `layoutcoverage_full.bak` | 0.225s | 0.216s | 0.027s | 0.084s | 0.058s | 0.022s | 0.079s |
| `max_row_width_full.bak` | 0.015s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `mixed_collation_full.bak` | 0.013s | 0.022s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `multi_rowgroup_full.bak` | 0.015s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `ncci_heap_full.bak` | 0.014s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `ncci_types_full.bak` | 0.313s | 0.068s | 0.002s | 0.127s | 0.017s | 0.001s | 0.1s |
| `ndfcoverage_full.bak` | 0.019s | 0.028s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `nvarchar_max_u21_full.bak` | 0.012s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `pagecomp_anchor_full.bak` | 0.092s | 0.022s | 0.0s | 0.028s | 0.006s | 0.0s | 0.029s |
| `pagecomp_long_prefix_full.bak` | 0.016s | 0.033s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `pfor_columnstore_full.bak` | 0.308s | 0.033s | 0.001s | 0.292s | 0.034s | 0.001s | 0.294s |
| `pfor_columnstore_random_full.bak` | 0.308s | 0.03s | 0.001s | 0.29s | 0.034s | 0.001s | 0.284s |
| `realworld_numeric_digest_full.bak` | 0.076s | 0.013s | 0.001s | 0.025s | 0.004s | 0.001s | 0.025s |
| `rowboundary_full.bak` | 0.04s | 0.008s | 0.0s | 0.005s | 0.005s | 0.0s | 0.005s |
| `rowstore_hash_pii_full.bak` | 0.017s | 0.023s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `rowstore_lob_image_full.bak` | 0.017s | 0.024s | 0.0s | 0.001s | 0.003s | 0.0s | 0.001s |
| `rowstore_lob_markup_full.bak` | 0.02s | 0.022s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `rowversion_extract_full.bak` | 0.016s | 0.025s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `sparse_full.bak` | 0.093s | 0.022s | 0.0s | 0.024s | 0.009s | 0.0s | 0.023s |
| `spatial_edge_full.bak` | 0.017s | 0.027s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `spatial_index_full.bak` | 0.016s | 0.025s | 0.0s | 0.001s | 0.002s | 0.0s | 0.001s |
| `sql_variant_extract_full.bak` | 0.015s | 0.026s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `striped_full_1.bak` | 0.016s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `striped_single.bak` | 0.012s | 0.021s | 0.0s | 0.001s | 0.001s | 0.0s | 0.0s |
| `surrogate_pairs_full.bak` | 0.015s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `tabletype_cci_large_full.bak` | 0.081s | 0.026s | 0.002s | 0.015s | 0.07s | 0.001s | 0.011s |
| `tabletypecoverage_diff.bak` | 0.217s | 0.024s | 0.005s | 0.121s | 0.344s | 0.006s | 0.136s |
| `tabletypecoverage_full.bak` | 0.215s | 0.024s | 0.005s | 0.12s | 0.351s | 0.007s | 0.128s |
| `temporal_hidden_full.bak` | 0.096s | 0.012s | 0.001s | 0.004s | 0.002s | 0.0s | 0.005s |
| `torn_page_full.bak` | 0.018s | 0.024s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `typecoverage_full.bak` | 0.108s | 0.109s | 0.005s | 0.034s | 0.083s | 0.003s | 0.031s |
| `typed_xml_full.bak` | 0.015s | 0.023s | 0.0s | 0.0s | 0.001s | 0.0s | 0.0s |
| `unicode_codepage_coverage.bak` | 0.02s | 0.065s | 0.001s | 0.005s | 0.009s | 0.001s | 0.007s |
| `xml_index_full.bak` | 0.014s | 0.022s | 0.0s | 0.001s | 0.001s | 0.0s | 0.001s |
| `xmlcoverage_full.bak` | 0.014s | 0.021s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s |
| `xmlheap_full.bak` | 0.091s | 0.022s | 0.0s | 0.021s | 0.009s | 0.0s | 0.02s |
| `xtp_checkpoint_straddle_full.bak` | 0.027s | 0.03s | 0.003s | 0.01s | 0.083s | 0.003s | 0.01s |
| `xtp_probe_full.bak` | 0.0s | 0.038s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `xtp_rich_full.bak` | 0.0s | 0.038s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |
| `xtp_simple_full.bak` | 0.0s | 0.043s | 0.0s | 0.0s | 0.002s | 0.0s | 0.0s |

_arrow verify = cell verification folded into extract_s. Sink read = pure I/O + decode. Stats = min/max/null compute. Sink verify = cell verification on the round-tripped data. Remainder of readback_s is GC / other._

---

_Generated 2026-07-21 · 134 fixtures · 133 pass · 1 xfail · 0 fail_
