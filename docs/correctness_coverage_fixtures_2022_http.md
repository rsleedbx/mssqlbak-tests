# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2022`.

**146 fixtures · 145 pass · 0 xfail (known gap) · 1 fail**

**Tables:** 463/463 pass · **Columns:** 4204/4204 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** ✓

Column key:

| Column | Meaning |
|--------|----------|
| Source rows | Total rows in all non-empty tables per SQL Server ground truth |
| Source cols | Total columns tracked across all non-empty tables |
| Row count | `matched/total` tables with correct row count |
| Null count | `matched/total` columns with correct null count |
| Min/max | `matched/total` comparable min/max checks; `sql_variant` and `uniqueidentifier` skipped (non-lexicographic ordering) |
| Col count | `matched/total` tables with ≥ expected column count |
| Cells | Row-level cell verification across tables with `<backup>.bak.cells/_manifest.json` |
| Status | ✓ = all match · ~ = xfail (known gap) · ✗ = mismatch |

Memory-optimized (In-Memory OLTP / XTP) tables store their data in XTP checkpoint file pairs (CFPs) rather than 8 KB pages.  mssqlbak decodes their rows from compact and WAL-style CFP blocks embedded in the backup, so they are scored normally against ground truth.

## Summary

| Backup | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |
|--------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|
| `alias_types_full.bak` | 3 | 9 | **1/1** | **9/9** | — | **1/1** | **24/24** | ✓ |
| `archive_columnstore_partition_full.bak` | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | digest | ✓ |
| `archive_columnstore_types_full.bak` | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_random_full.bak` | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_single_chunk_full.bak` | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_random_full.bak` | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archivenull_full.bak` | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `backup_blocksize_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `boundarycoverage_datetime_full.bak` | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | **21600/21600** | ✓ |
| `boundarycoverage_full.bak` | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | **19200/19200** | ✓ |
| `catalog_ss2022.bak` | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **3/3** | ✓ |
| `cci_binary_varbinary_compare_full.bak` | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | 4,400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_full.bak` | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_btree_nci_full.bak` | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_computed_full.bak` | 2,400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_full.bak` | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_matrix_full.bak` | 531,071 | 15 | **8/8** | **15/15** | **30/30** | **8/8** | digest | ✓ |
| `cci_extended_full.bak` | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | digest | ✓ |
| `cci_lob_full.bak` | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | digest | ✓ |
| `cci_reorganize_full.bak` | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | digest | ✓ |
| `cci_string_dict_regression_full.bak` | 24,576 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_string_minmax_full.bak` | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_switch_full.bak` | 2,400 | 7 | **3/3** | **4/4** | **8/8** | **3/3** | digest | ✓ |
| `cci_types_large_full.bak` | 6,000 | 10 | **5/5** | **10/10** | **18/18** | **5/5** | digest | ✓ |
| `cci_varbinary_micro_full.bak` | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_probe_full.bak` | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `columnstore_minimal.bak` | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | digest | ✓ |
| `compressed_nvarchar_full.bak` | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **8/8** | ✓ |
| `compressioncoverage_full.bak` | 1,994 | 239 | **19/19** | **239/239** | **464/464** | **19/19** | **17902/17902** | ✓ |
| `computedcoverage_full.bak` | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | **18/18** | ✓ |
| `constraintcoverage_full.bak` | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | **54/54** | ✓ |
| `corrupt_metadata_confidence_full.bak` | — | — | — | — | — | — | confidence fail (catalog_consistency: schema recovery failed: 'corrupt_metadata_confidence_full.bak' is too small to contain an MDF page image.) · constraints: 3 total · 2 pass · 1 fail  [catalog_consistency: 1F] | ✗ |
| `covering_index_full.bak` | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | **3000/3000** | ✓ |
| `cs_lob_preamble.bak` | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5000/5000** | ✓ |
| `cs_lob_preamble2.bak` | 1,200 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **1200/1200** | ✓ |
| `delta_rowgroup_full.bak` | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_aborted_xact.bak` | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **40/40** | ✓ |
| `dirtycoverage_addcol.bak` | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **180/180** | ✓ |
| `dirtycoverage_addnotnull.bak` | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **180/180** | ✓ |
| `dirtycoverage_alldirty.bak` | 0 | 3 | **1/1** | — | — | **1/1** | empty | ✓ |
| `dirtycoverage_altercol.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **120/120** | ✓ |
| `dirtycoverage_alterdb.bak` | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **300/300** | ✓ |
| `dirtycoverage_cci_delete.bak` | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_update.bak` | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_delete.bak` | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **400/400** | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | 250,500 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | **251000/251000** | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | 200 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | **5200/5200** | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | 9,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | **28000/28000** | ✓ |
| `dirtycoverage_committed_update.bak` | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **400/400** | ✓ |
| `dirtycoverage_committed_update_v2.bak` | 300,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600000/600000** | ✓ |
| `dirtycoverage_committed_update_v3.bak` | 300 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | **7800/7800** | ✓ |
| `dirtycoverage_committed_update_v4.bak` | 10,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | **35000/35000** | ✓ |
| `dirtycoverage_compress_update.bak` | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **150/150** | ✓ |
| `dirtycoverage_concurrent.bak` | 114 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **342/342** | ✓ |
| `dirtycoverage_createidx.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `dirtycoverage_createtable.bak` | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **300/300** | ✓ |
| `dirtycoverage_delete.bak` | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **140/140** | ✓ |
| `dirtycoverage_dropcol.bak` | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **120/120** | ✓ |
| `dirtycoverage_dropidx.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `dirtycoverage_droptable.bak` | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | **1200/1200** | ✓ |
| `dirtycoverage_heap_forward.bak` | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_insert_update.bak` | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **150/150** | ✓ |
| `dirtycoverage_large_dirty.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_lob_update.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `dirtycoverage_maxrow.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
| `dirtycoverage_multi_update.bak` | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **150/150** | ✓ |
| `dirtycoverage_nchar_delete.bak` | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **60/60** | ✓ |
| `dirtycoverage_nested.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_null_update.bak` | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **40/40** | ✓ |
| `dirtycoverage_rebuildidx.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `dirtycoverage_rich_insert.bak` | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_rich_update.bak` | 20 | 10 | **1/1** | **10/10** | **18/18** | **1/1** | digest | ✓ |
| `dirtycoverage_savepoint.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_snapshot_update.bak` | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **20/20** | ✓ |
| `dirtycoverage_switch.bak` | 200 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | **400/400** | ✓ |
| `dirtycoverage_temporal_update.bak` | 20 | 8 | **2/2** | **4/4** | **8/8** | **2/2** | **60/60** | ✓ |
| `dirtycoverage_truncate.bak` | 500 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **1000/1000** | ✓ |
| `dirtycoverage_two_tx.bak` | 30 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **60/60** | ✓ |
| `dirtycoverage_uncommitted.bak` | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **150/150** | ✓ |
| `dirtycoverage_update.bak` | 50 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **150/150** | ✓ |
| `dirtycoverage_wide.bak` | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **10/10** | ✓ |
| `featurecoverage_full.bak` | 1,124 | 43 | **10/10** | **31/31** | **62/62** | **10/10** | **3298/3298** | ✓ |
| `filtered_ncci_full.bak` | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | **800/800** | ✓ |
| `float_extreme_full.bak` | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **10/10** | ✓ |
| `forwarded_records_full.bak` | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **1000/1000** | ✓ |
| `geocoverage_full.bak` | 27 | 25 | **7/7** | **25/25** | **50/50** | **7/7** | **73/73** | ✓ |
| `geotest.bak` | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **44/44** | ✓ |
| `ghost_records_full.bak` | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `heapcoverage_large.bak` | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | **2000/2000** | ✓ |
| `heapcoverage_large_50000.bak` | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | **100000/100000** | ✓ |
| `hierarchyid_extract_full.bak` | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **6/6** | ✓ |
| `high_slot_density_full.bak` | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | digest | ✓ |
| `incrementalcoverage_diff_01.bak` | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **45/45** | ✓ |
| `incrementalcoverage_diff_02.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `incrementalcoverage_diff_03.bak` | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **75/75** | ✓ |
| `incrementalcoverage_diff_04.bak` | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **90/90** | ✓ |
| `incrementalcoverage_diff_05.bak` | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **105/105** | ✓ |
| `incrementalcoverage_diff_06.bak` | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **120/120** | ✓ |
| `incrementalcoverage_full.bak` | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **30/30** | ✓ |
| `layoutcoverage_full.bak` | 171 | 2,421 | **57/57** | **2421/2421** | **740/740** | **57/57** | **7092/7092** | ✓ |
| `legacytext.bak` | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **9/9** | ✓ |
| `max_row_width_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `mixed_collation_full.bak` | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | **12/12** | ✓ |
| `multi_rowgroup_full.bak` | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_types_full.bak` | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | **22857/22857** | ✓ |
| `ndfcoverage_full.bak` | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **20/20** | ✓ |
| `nvarchar_max_u21_full.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
| `ordered_cci_full.bak` | 3,600 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `pagecomp_anchor_full.bak` | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | **35000/35000** | ✓ |
| `pagecomp_long_prefix_full.bak` | 100 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **100/100** | ✓ |
| `pfor_columnstore_full.bak` | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_random_full.bak` | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `realworld_numeric_digest_full.bak` | 4,800 | 22 | **4/4** | **22/22** | **44/44** | **4/4** | **14400/14400** | ✓ |
| `rowboundary_full.bak` | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `rowstore_hash_pii_full.bak` | 4 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **12/12** | ✓ |
| `rowstore_lob_image_full.bak` | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | **12/12** | ✓ |
| `rowstore_lob_markup_full.bak` | 5 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **15/15** | ✓ |
| `rowversion_extract_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `sparse_full.bak` | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | **50000/50000** | ✓ |
| `spatial_edge_full.bak` | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **14/14** | ✓ |
| `spatial_index_full.bak` | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **400/400** | ✓ |
| `sql_variant_extract_full.bak` | 10 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | **10/10** | ✓ |
| `striped_full_1.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `striped_single.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `surrogate_pairs_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `tabletype_cci_large_full.bak` | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest | ✓ |
| `tabletypecoverage_diff.bak` | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **198/198** | ✓ |
| `tabletypecoverage_full.bak` | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **132/132** | ✓ |
| `temporal_hidden_full.bak` | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **30/30** | ✓ |
| `torn_page_full.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `typecoverage_full.bak` | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | **321/321** | ✓ |
| `typecoverage_full_compressed.bak` | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | **321/321** | ✓ |
| `typed_xml_full.bak` | 8 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **8/8** | ✓ |
| `unicode_codepage_coverage.bak` | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | **45/45** | ✓ |
| `utf8_collation_full.bak` | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **14/14** | ✓ |
| `xml_index_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `xmlcoverage_full.bak` | 13 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **26/26** | ✓ |
| `xmlheap_full.bak` | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | **1200/1200** | ✓ |
| `xtp_checkpoint_straddle_full.bak` | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xtp_probe_full.bak` | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **9/9** | — | ✓ | cells **24/24** ✓ |

### `archive_columnstore_partition_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.121 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_columnstore_types_random_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | columnstore | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | columnstore | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_date` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_18_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_float` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_int` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_money` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_real` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smallint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smallmoney` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_tinyint` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `catalog_ss2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `cci_binary_varbinary_compare_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_bigint_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 43.148 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_highbase_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 25.117 MB_

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

### `cci_extended_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 10.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | columnstore | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_columnstore_archive` | columnstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_none` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_page` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_page_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells **21/21** ✓ |
| `dbo.cmp_page_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.cmp_page_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells **9/9** ✓ |
| `dbo.cmp_page_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells **2000/2000** ✓ |
| `dbo.cmp_row` | rowstore | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_row_floats` | rowstore | 7 | ✓ | **4/4** | **8/8** | ✓ | cells **21/21** ✓ |
| `dbo.cmp_row_lob` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.cmp_row_variant` | rowstore | 9 | ✓ | **2/2** | **2/2** | ✓ | cells **9/9** ✓ |
| `dbo.cmp_row_wide` | rowstore | 50 | ✓ | **41/41** | **82/82** | ✓ | cells **2000/2000** ✓ |
| `dbo.cs_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |
| `dbo.fwd_heap` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ghost_heap` | rowstore | 250 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.sparse_cols` | rowstore | 200 | ✓ | **4/4** | **8/8** | ✓ | cells **600/600** ✓ |
| `dbo.uniquifier_none` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.uniquifier_row` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `computedcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_default_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_fk_child` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_fk_parent` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_index_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_pk` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_pk_nonclustered` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_unique_constraint` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_unique_index` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |

### `corrupt_metadata_confidence_full.bak` — confidence fail

_SQL Server  · 0.002 MB_

_confidence fail (catalog_consistency: schema recovery failed: 'corrupt_metadata_confidence_full.bak' is too small to contain an MDF page image.)._

### `covering_index_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.195 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells **5000/5000** ✓ |

### `cs_lob_preamble2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.605 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells **1200/1200** ✓ |

### `delta_rowgroup_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.301 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 56.434 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.padding_fill` | rowstore | 250,000 | ✓ | **2/2** | **4/4** | ✓ | cells **250000/250000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.301 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 115.879 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 300,000 | ✓ | **3/3** | **6/6** | ✓ | cells **600000/600000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_compress_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_concurrent.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 114 | ✓ | **4/4** | **8/8** | ✓ | cells **342/342** ✓ |

### `dirtycoverage_createidx.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_insert_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.iu_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_large_dirty.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_multi_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.multi_update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_nchar_delete.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_wide.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide2_test` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `featurecoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.246 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_col` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `dbo.graph_follows` | rowstore | 2 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.graph_person` | rowstore | 3 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.ledger_account` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **6/6** ✓ |
| `dbo.long_text` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `dbo.memory_oltp` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_table` | rowstore | 1,024 | ✓ | **4/4** | **8/8** | ✓ | cells **3072/3072** ✓ |
| `dbo.temporal_current` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |
| `dbo.temporal_history` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.utf8_collation` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ | cells **18/18** ✓ |

### `filtered_ncci_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 16.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `geocoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Locations` | rowstore | 5 | ✓ | **5/5** | **10/10** | ✓ | cells **20/20** ✓ |
| `dbo.LocationsNone` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.LocationsRow` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.spatial_lob_test` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.SpatialCurves` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.SpatialLob` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells **2/2** ✓ |
| `dbo.SpatialZM` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `geotest.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Locations` | rowstore | 5 | ✓ | **5/5** | **10/10** | ✓ | cells **20/20** ✓ |
| `dbo.LocationsNone` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.LocationsRow` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.spatial_lob_test` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |

### `ghost_records_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.93 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.051 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | **1023/1023** | — | ✓ | cells **3066/3066** ✓ |
| `dbo.layout_cols_1024` | rowstore | 3 | ✓ | **1024/1024** | — | ✓ | cells **3069/3069** ✓ |
| `dbo.layout_cols_30` | rowstore | 3 | ✓ | **30/30** | **60/60** | ✓ | cells **87/87** ✓ |
| `dbo.layout_cols_31` | rowstore | 3 | ✓ | **31/31** | **62/62** | ✓ | cells **90/90** ✓ |
| `dbo.layout_pk_bigint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_first` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_last` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_penult` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_second` | rowstore | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_first` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_last` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_penult` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_second` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |

### `legacytext.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.legacy_lob` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `max_row_width_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `multi_rowgroup_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_binary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_bit` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_char` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_date` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetime2` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetimeoffset` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_float` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_money` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_nchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_nvarchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_real` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_smallint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_smallmoney` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_time` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_tinyint` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_uuid` | rowstore | 1,203 | ✓ | **2/2** | **2/2** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_varbinary` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_varchar` | rowstore | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |

### `ndfcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `ordered_cci_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ordered_cci` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.regular_cci` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `pagecomp_anchor_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pagecomp_long_prefix_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ | cells **100/100** ✓ |

### `pfor_columnstore_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.geometry_edge` | rowstore | 9 | ✓ | **2/2** | **4/4** | ✓ | cells **9/9** ✓ |

### `spatial_index_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 10 | ✓ | **2/2** | **2/2** | ✓ | cells **10/10** ✓ |

### `striped_full_1.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.266 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | rowstore | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.738 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.551 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **4/4** | ✓ | cells **32/32** ✓ |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |

### `typecoverage_full_compressed.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.535 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.t_bigint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_binary_8` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_bit` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_char_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_date` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime2_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetimeoffset_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_decimal_38_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_float` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_geography` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `dbo.t_geometry` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.t_hierarchyid` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.t_image` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_int` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_money` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nchar_10` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_ntext` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_numeric_18_4` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nvarchar_50` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_real` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_rowversion` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.t_smalldatetime` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallmoney` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_sql_variant` | rowstore | 16 | ✓ | **3/3** | **4/4** | ✓ | cells **32/32** ✓ |
| `dbo.t_text` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_time_7` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_tinyint` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_uniqueidentifier` | rowstore | 4 | ✓ | **3/3** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.t_varbinary_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_varchar_max` | rowstore | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_xml` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |

### `typed_xml_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `unicode_codepage_coverage.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.551 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1251` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells **6/6** ✓ |
| `dbo.cp_cp1253` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1254` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1255` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1256` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1257` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1258` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp874` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp932` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells **6/6** ✓ |
| `dbo.cp_cp936` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp949` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp950` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |

### `utf8_collation_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |
| `dbo.utf8_tbl` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `xml_index_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 13 | ✓ | **3/3** | **6/6** | ✓ | cells **26/26** ✓ |

### `xmlheap_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.176 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `xtp_checkpoint_straddle_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.711 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_probe_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.246 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.246 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.246 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `alias_types_full.bak` | 0.105s |
| `archive_columnstore_partition_full.bak` | 2.563s |
| `archive_columnstore_types_full.bak` | 1.396s |
| `archive_columnstore_types_random_full.bak` | 1.392s |
| `archive_single_chunk_full.bak` | 0.119s |
| `archive_single_chunk_random_full.bak` | 0.11s |
| `archivenull_full.bak` | 0.317s |
| `backup_blocksize_full.bak` | 0.118s |
| `boundarycoverage_datetime_full.bak` | 0.444s |
| `boundarycoverage_full.bak` | 0.212s |
| `catalog_ss2022.bak` | 0.107s |
| `cci_binary_varbinary_compare_full.bak` | 0.12s |
| `cci_bitpack_probe_bigint_full.bak` | 8.52s |
| `cci_bitpack_probe_full.bak` | 1.766s |
| `cci_bitpack_probe_highbase_full.bak` | 1.305s |
| `cci_btree_nci_full.bak` | 0.11s |
| `cci_computed_full.bak` | 0.103s |
| `cci_enc5_largepool_full.bak` | 1.277s |
| `cci_enc5_largepool_matrix_full.bak` | 9.632s |
| `cci_extended_full.bak` | 0.126s |
| `cci_lob_full.bak` | 0.118s |
| `cci_reorganize_full.bak` | 0.107s |
| `cci_string_dict_regression_full.bak` | 0.568s |
| `cci_string_minmax_full.bak` | 0.113s |
| `cci_switch_full.bak` | 0.126s |
| `cci_types_large_full.bak` | 0.13s |
| `cci_varbinary_micro_full.bak` | 0.103s |
| `cci_varbinary_probe_full.bak` | 0.111s |
| `columnstore_minimal.bak` | 1.26s |
| `compressed_nvarchar_full.bak` | 0.109s |
| `compressioncoverage_full.bak` | 0.384s |
| `computedcoverage_full.bak` | 0.099s |
| `constraintcoverage_full.bak` | 0.143s |
| `corrupt_metadata_confidence_full.bak` | 0.005s |
| `covering_index_full.bak` | 0.138s |
| `cs_lob_preamble.bak` | 0.277s |
| `cs_lob_preamble2.bak` | 0.185s |
| `delta_rowgroup_full.bak` | 0.11s |
| `dirtycoverage_aborted_xact.bak` | 0.123s |
| `dirtycoverage_addcol.bak` | 0.108s |
| `dirtycoverage_addnotnull.bak` | 0.126s |
| `dirtycoverage_alldirty.bak` | 0.117s |
| `dirtycoverage_altercol.bak` | 0.116s |
| `dirtycoverage_altercol_rewrite.bak` | 0.099s |
| `dirtycoverage_alterdb.bak` | 0.118s |
| `dirtycoverage_cci_delete.bak` | 0.226s |
| `dirtycoverage_cci_update.bak` | 0.341s |
| `dirtycoverage_committed_delete.bak` | 0.097s |
| `dirtycoverage_committed_delete_v2.bak` | 3.024s |
| `dirtycoverage_committed_delete_v3.bak` | 0.173s |
| `dirtycoverage_committed_delete_v4.bak` | 0.357s |
| `dirtycoverage_committed_update.bak` | 0.1s |
| `dirtycoverage_committed_update_v2.bak` | 13.246s |
| `dirtycoverage_committed_update_v3.bak` | 0.189s |
| `dirtycoverage_committed_update_v4.bak` | 0.341s |
| `dirtycoverage_compress_update.bak` | 0.136s |
| `dirtycoverage_concurrent.bak` | 0.107s |
| `dirtycoverage_createidx.bak` | 0.099s |
| `dirtycoverage_createtable.bak` | 0.1s |
| `dirtycoverage_delete.bak` | 0.128s |
| `dirtycoverage_dropcol.bak` | 0.104s |
| `dirtycoverage_dropidx.bak` | 0.106s |
| `dirtycoverage_droptable.bak` | 0.113s |
| `dirtycoverage_heap_forward.bak` | 0.12s |
| `dirtycoverage_insert_update.bak` | 0.137s |
| `dirtycoverage_large_dirty.bak` | 0.443s |
| `dirtycoverage_lob_update.bak` | 0.144s |
| `dirtycoverage_maxrow.bak` | 0.108s |
| `dirtycoverage_multi_update.bak` | 0.128s |
| `dirtycoverage_nchar_delete.bak` | 0.118s |
| `dirtycoverage_nested.bak` | 0.126s |
| `dirtycoverage_null_update.bak` | 0.119s |
| `dirtycoverage_rebuildidx.bak` | 0.169s |
| `dirtycoverage_rich_insert.bak` | 0.149s |
| `dirtycoverage_rich_update.bak` | 0.132s |
| `dirtycoverage_savepoint.bak` | 0.122s |
| `dirtycoverage_snapshot_update.bak` | 0.114s |
| `dirtycoverage_switch.bak` | 0.104s |
| `dirtycoverage_temporal_update.bak` | 0.116s |
| `dirtycoverage_truncate.bak` | 0.104s |
| `dirtycoverage_two_tx.bak` | 0.116s |
| `dirtycoverage_uncommitted.bak` | 0.122s |
| `dirtycoverage_update.bak` | 0.129s |
| `dirtycoverage_wide.bak` | 0.126s |
| `featurecoverage_full.bak` | 0.201s |
| `filtered_ncci_full.bak` | 0.139s |
| `float_extreme_full.bak` | 0.117s |
| `forwarded_records_full.bak` | 0.228s |
| `geocoverage_full.bak` | 0.11s |
| `geotest.bak` | 0.121s |
| `ghost_records_full.bak` | 0.092s |
| `heapcoverage_large.bak` | 0.114s |
| `heapcoverage_large_50000.bak` | 1.084s |
| `hierarchyid_extract_full.bak` | 0.097s |
| `high_slot_density_full.bak` | 0.58s |
| `incrementalcoverage_diff_01.bak` | 0.103s |
| `incrementalcoverage_diff_02.bak` | 0.11s |
| `incrementalcoverage_diff_03.bak` | 0.11s |
| `incrementalcoverage_diff_04.bak` | 0.089s |
| `incrementalcoverage_diff_05.bak` | 0.116s |
| `incrementalcoverage_diff_06.bak` | 0.099s |
| `incrementalcoverage_full.bak` | 0.092s |
| `layoutcoverage_full.bak` | 0.388s |
| `legacytext.bak` | 0.148s |
| `max_row_width_full.bak` | 0.091s |
| `mixed_collation_full.bak` | 0.146s |
| `multi_rowgroup_full.bak` | 0.104s |
| `ncci_heap_full.bak` | 0.095s |
| `ncci_types_full.bak` | 0.568s |
| `ndfcoverage_full.bak` | 0.107s |
| `nvarchar_max_u21_full.bak` | 0.096s |
| `ordered_cci_full.bak` | 0.119s |
| `pagecomp_anchor_full.bak` | 0.387s |
| `pagecomp_long_prefix_full.bak` | 0.12s |
| `pfor_columnstore_full.bak` | 2.295s |
| `pfor_columnstore_random_full.bak` | 2.289s |
| `realworld_numeric_digest_full.bak` | 0.222s |
| `rowboundary_full.bak` | 0.122s |
| `rowstore_hash_pii_full.bak` | 0.089s |
| `rowstore_lob_image_full.bak` | 0.166s |
| `rowstore_lob_markup_full.bak` | 0.095s |
| `rowversion_extract_full.bak` | 0.091s |
| `sparse_full.bak` | 0.316s |
| `spatial_edge_full.bak` | 0.109s |
| `spatial_index_full.bak` | 0.113s |
| `sql_variant_extract_full.bak` | 0.096s |
| `striped_full_1.bak` | 0.116s |
| `striped_single.bak` | 0.151s |
| `surrogate_pairs_full.bak` | 0.096s |
| `tabletype_cci_large_full.bak` | 0.146s |
| `tabletypecoverage_diff.bak` | 0.207s |
| `tabletypecoverage_full.bak` | 0.206s |
| `temporal_hidden_full.bak` | 0.153s |
| `torn_page_full.bak` | 0.082s |
| `typecoverage_full.bak` | 0.182s |
| `typecoverage_full_compressed.bak` | 0.265s |
| `typed_xml_full.bak` | 0.102s |
| `unicode_codepage_coverage.bak` | 0.131s |
| `utf8_collation_full.bak` | 0.114s |
| `xml_index_full.bak` | 0.109s |
| `xmlcoverage_full.bak` | 0.114s |
| `xmlheap_full.bak` | 0.169s |
| `xtp_checkpoint_straddle_full.bak` | 3.034s |
| `xtp_probe_full.bak` | 0.181s |
| `xtp_rich_full.bak` | 0.172s |
| `xtp_simple_full.bak` | 0.148s |

---

_Generated 2026-07-09 · 146 fixtures · 145 pass · 0 xfail · 1 fail_
