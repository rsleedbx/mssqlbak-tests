# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2017`.

**133 fixtures · 133 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 402/402 pass · **Columns:** 3992/3992 pass

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
| `alias_types_full.bak` | 3 | 6 | **1/1** | **6/6** | — | **1/1** | **15/15** | ✓ |
| `archive_columnstore_partition_full.bak` | 560,000 | 12 | **4/4** | **12/12** | **24/24** | **4/4** | digest | ✓ |
| `archive_columnstore_types_full.bak` | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_columnstore_types_random_full.bak` | 245,000 | 14 | **7/7** | **14/14** | **26/26** | **7/7** | digest | ✓ |
| `archive_single_chunk_full.bak` | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archive_single_chunk_random_full.bak` | 5,000 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `archivenull_full.bak` | 50,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `backup_blocksize_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `boundarycoverage_datetime_full.bak` | 10,800 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | **21600/21600** | ✓ |
| `boundarycoverage_full.bak` | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | **19200/19200** | ✓ |
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
| `covering_index_full.bak` | 2,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | **3000/3000** | ✓ |
| `cs_lob_preamble.bak` | 1,400 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **1400/1400** | ✓ |
| `delta_rowgroup_full.bak` | 180 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_aborted_xact.bak` | 20 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **40/40** | ✓ |
| `dirtycoverage_addcol.bak` | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **180/180** | ✓ |
| `dirtycoverage_addnotnull.bak` | 60 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **180/180** | ✓ |
| `dirtycoverage_alldirty.bak` | 0 | 3 | **1/1** | — | — | **1/1** | empty | ✓ |
| `dirtycoverage_altercol.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **120/120** | ✓ |
| `dirtycoverage_alterdb.bak` | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **300/300** | ✓ |
| `dirtycoverage_cci_delete.bak` | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_cci_update.bak` | 14,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `dirtycoverage_committed_delete.bak` | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **400/400** | ✓ |
| `dirtycoverage_committed_delete_v2.bak` | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **2000/2000** | ✓ |
| `dirtycoverage_committed_delete_v3.bak` | 200 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | **5200/5200** | ✓ |
| `dirtycoverage_committed_delete_v4.bak` | 9,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | **28000/28000** | ✓ |
| `dirtycoverage_committed_update.bak` | 200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **400/400** | ✓ |
| `dirtycoverage_committed_update_v2.bak` | 1,000 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **2000/2000** | ✓ |
| `dirtycoverage_committed_update_v3.bak` | 300 | 27 | **1/1** | **27/27** | **50/50** | **1/1** | **7800/7800** | ✓ |
| `dirtycoverage_committed_update_v4.bak` | 10,000 | 9 | **2/2** | **9/9** | **16/16** | **2/2** | **35000/35000** | ✓ |
| `dirtycoverage_concurrent.bak` | 113 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **339/339** | ✓ |
| `dirtycoverage_createidx.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `dirtycoverage_createtable.bak` | 300 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **300/300** | ✓ |
| `dirtycoverage_delete.bak` | 70 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **140/140** | ✓ |
| `dirtycoverage_dropcol.bak` | 60 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **120/120** | ✓ |
| `dirtycoverage_dropidx.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `dirtycoverage_droptable.bak` | 700 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | **1200/1200** | ✓ |
| `dirtycoverage_heap_forward.bak` | 20 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `dirtycoverage_large_dirty.bak` | 50 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **100/100** | ✓ |
| `dirtycoverage_lob_update.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `dirtycoverage_maxrow.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
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
| `filtered_ncci_full.bak` | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | **800/800** | ✓ |
| `float_extreme_full.bak` | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **10/10** | ✓ |
| `forwarded_records_full.bak` | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **1000/1000** | ✓ |
| `ghost_records_full.bak` | 800 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | digest | ✓ |
| `heapcoverage_large.bak` | 2,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | **2000/2000** | ✓ |
| `heapcoverage_large_50000.bak` | 100,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | **100000/100000** | ✓ |
| `hierarchyid_extract_full.bak` | 6 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **6/6** | ✓ |
| `high_slot_density_full.bak` | 200,000 | 2 | **2/2** | **2/2** | **4/4** | **2/2** | digest | ✓ |
| `identity_coverage_full.bak` | 35 | 13 | **7/7** | **13/13** | **26/26** | **7/7** | **30/30** | ✓ |
| `incrementalcoverage_diff_01.bak` | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **45/45** | ✓ |
| `incrementalcoverage_diff_02.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `incrementalcoverage_diff_03.bak` | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **75/75** | ✓ |
| `incrementalcoverage_diff_04.bak` | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **90/90** | ✓ |
| `incrementalcoverage_diff_05.bak` | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **105/105** | ✓ |
| `incrementalcoverage_diff_06.bak` | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **120/120** | ✓ |
| `incrementalcoverage_full.bak` | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **30/30** | ✓ |
| `layoutcoverage_full.bak` | 171 | 2,421 | **57/57** | **1398/1398** | **740/740** | **57/57** | **7092/7092** | ✓ |
| `max_row_width_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `mixed_collation_full.bak` | 3 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **9/9** | ✓ |
| `multi_rowgroup_full.bak` | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_types_full.bak` | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | **22857/22857** | ✓ |
| `ndfcoverage_full.bak` | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **20/20** | ✓ |
| `nvarchar_max_u21_full.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
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
| `spatial_edge_full.bak` | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **8/8** | ✓ |
| `spatial_index_full.bak` | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **400/400** | ✓ |
| `sql_variant_extract_full.bak` | 6 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | **6/6** | ✓ |
| `striped_full_1.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `striped_single.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `surrogate_pairs_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `tabletype_cci_large_full.bak` | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest | ✓ |
| `tabletypecoverage_diff.bak` | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **198/198** | ✓ |
| `tabletypecoverage_full.bak` | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **132/132** | ✓ |
| `temporal_hidden_full.bak` | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **20/20** | ✓ |
| `torn_page_full.bak` | 300 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **600/600** | ✓ |
| `typecoverage_full.bak` | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | **321/321** | ✓ |
| `typed_xml_full.bak` | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **3/3** | ✓ |
| `unicode_codepage_coverage.bak` | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | **45/45** | ✓ |
| `xml_index_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `xmlcoverage_full.bak` | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **24/24** | ✓ |
| `xmlheap_full.bak` | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | **1200/1200** | ✓ |
| `xtp_checkpoint_straddle_full.bak` | 200,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `xtp_probe_full.bak` | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | rowstore | 3 | ✓ | **6/6** | — | ✓ | cells **15/15** ✓ |

### `archive_columnstore_partition_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 12.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | columnstore | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.113 MB_

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

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | columnstore | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | columnstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.109 MB_

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

### `boundarycoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `cci_binary_varbinary_compare_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_bigint_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 41.145 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | columnstore | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | columnstore | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_highbase_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | columnstore | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.734 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.234 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | columnstore | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 23.113 MB_

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

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | columnstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 8.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | columnstore | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | columnstore | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | columnstore | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | columnstore | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | columnstore | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | columnstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | columnstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | columnstore | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.422 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | columnstore | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | columnstore | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | columnstore | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | columnstore | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | columnstore | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | columnstore | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | columnstore | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `computedcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.484 MB_

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

### `covering_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | rowstore | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | rowstore | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.543 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | columnstore | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells **1400/1400** ✓ |

### `delta_rowgroup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | columnstore | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | columnstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | rowstore | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | columnstore | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | rowstore | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | rowstore | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | rowstore | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_concurrent.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 113 | ✓ | **4/4** | **8/8** | ✓ | cells **339/339** ✓ |

### `dirtycoverage_createidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | rowstore | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | rowstore | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | rowstore | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | rowstore | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_large_dirty.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_nchar_delete.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | rowstore | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | rowstore | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | rowstore | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | rowstore | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | rowstore | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | rowstore | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | rowstore | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | rowstore | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `filtered_ncci_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 14.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ghost_records_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | rowstore | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | rowstore | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 11.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | rowstore | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | rowstore | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.863 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `identity_coverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.bigint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.decimal_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.fkr__seed` | rowstore | 5 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.int_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.numeric_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.smallint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.tinyint_identity` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `incrementalcoverage_diff_01.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.734 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | rowstore | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | rowstore | 3 | ✓ | — | — | ✓ | cells **3066/3066** ✓ |
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

### `max_row_width_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | rowstore | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `multi_rowgroup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | columnstore | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | rowstore | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

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

### `ndfcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.113 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | rowstore | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `pagecomp_anchor_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | rowstore | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pagecomp_long_prefix_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.long_prefix_probe` | rowstore | 100 | ✓ | **2/2** | **4/4** | ✓ | cells **100/100** ✓ |

### `pfor_columnstore_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | columnstore | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | columnstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | rowstore | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | rowstore | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | rowstore | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | rowstore | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.geometry_edge` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |

### `spatial_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | rowstore | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | rowstore | 6 | ✓ | **2/2** | **2/2** | ✓ | cells **6/6** ✓ |

### `striped_full_1.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.18 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.41 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | rowstore | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | columnstore | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | rowstore | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.109 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | columnstore | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | rowstore | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **5/5** ✓ |
| `dbo.temporal_hidden_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | rowstore | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | rowstore | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | rowstore | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.547 MB_

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

### `typed_xml_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `unicode_codepage_coverage.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.234 MB_

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

### `xml_index_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | rowstore | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | rowstore | 12 | ✓ | **3/3** | **6/6** | ✓ | cells **24/24** ✓ |

### `xmlheap_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.672 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | rowstore | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `xtp_checkpoint_straddle_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.52 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | rowstore | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xtp_ckpt` | memory-optimized | 100,000 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_probe_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.242 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | memory-optimized | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | memory-optimized | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | memory-optimized | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | memory-optimized | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | memory-optimized | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — 2017 — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | memory-optimized | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | memory-optimized | 3 | ✓ | **2/2** | **4/4** | ✓ |  |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `alias_types_full.bak` | 0.027s | 0.03s | 0.057s |
| `archive_columnstore_partition_full.bak` | 0.957s | 0.699s | 1.656s |
| `archive_columnstore_types_full.bak` | 0.324s | 0.685s | 1.009s |
| `archive_columnstore_types_random_full.bak` | 0.308s | 0.677s | 0.985s |
| `archive_single_chunk_full.bak` | 0.042s | 0.042s | 0.084s |
| `archive_single_chunk_random_full.bak` | 0.04s | 0.04s | 0.08s |
| `archivenull_full.bak` | 0.124s | 0.204s | 0.328s |
| `backup_blocksize_full.bak` | 0.029s | 0.029s | 0.058s |
| `boundarycoverage_datetime_full.bak` | 0.063s | 0.134s | 0.197s |
| `boundarycoverage_full.bak` | 0.047s | 0.052s | 0.099s |
| `cci_binary_varbinary_compare_full.bak` | 0.033s | 0.031s | 0.064s |
| `cci_bitpack_probe_bigint_full.bak` | 0.357s | 3.791s | 4.148s |
| `cci_bitpack_probe_full.bak` | 0.074s | 0.641s | 0.715s |
| `cci_bitpack_probe_highbase_full.bak` | 0.072s | 0.446s | 0.518s |
| `cci_btree_nci_full.bak` | 0.042s | 0.038s | 0.08s |
| `cci_computed_full.bak` | 0.049s | 0.039s | 0.088s |
| `cci_enc5_largepool_full.bak` | 0.315s | 0.435s | 0.75s |
| `cci_enc5_largepool_matrix_full.bak` | 7.185s | 1.235s | 8.42s |
| `cci_extended_full.bak` | 0.039s | 0.031s | 0.07s |
| `cci_lob_full.bak` | 0.054s | 0.038s | 0.092s |
| `cci_reorganize_full.bak` | 0.047s | 0.04s | 0.087s |
| `cci_string_dict_regression_full.bak` | 0.293s | 0.137s | 0.43s |
| `cci_string_minmax_full.bak` | 0.043s | 0.039s | 0.082s |
| `cci_switch_full.bak` | 0.053s | 0.033s | 0.086s |
| `cci_types_large_full.bak` | 0.039s | 0.039s | 0.078s |
| `cci_varbinary_micro_full.bak` | 0.05s | 0.031s | 0.081s |
| `cci_varbinary_probe_full.bak` | 0.052s | 0.041s | 0.093s |
| `columnstore_minimal.bak` | 0.116s | 1.029s | 1.145s |
| `compressed_nvarchar_full.bak` | 0.034s | 0.032s | 0.066s |
| `compressioncoverage_full.bak` | 0.08s | 0.175s | 0.255s |
| `computedcoverage_full.bak` | 0.036s | 0.041s | 0.077s |
| `constraintcoverage_full.bak` | 0.042s | 0.043s | 0.085s |
| `covering_index_full.bak` | 0.051s | 0.037s | 0.088s |
| `cs_lob_preamble.bak` | 0.074s | 0.05s | 0.124s |
| `delta_rowgroup_full.bak` | 0.04s | 0.038s | 0.078s |
| `dirtycoverage_aborted_xact.bak` | 0.046s | 0.036s | 0.082s |
| `dirtycoverage_addcol.bak` | 0.054s | 0.036s | 0.09s |
| `dirtycoverage_addnotnull.bak` | 0.043s | 0.03s | 0.073s |
| `dirtycoverage_alldirty.bak` | 0.052s | 0.031s | 0.083s |
| `dirtycoverage_altercol.bak` | 0.031s | 0.032s | 0.063s |
| `dirtycoverage_altercol_rewrite.bak` | 0.043s | 0.029s | 0.072s |
| `dirtycoverage_alterdb.bak` | 0.044s | 0.03s | 0.074s |
| `dirtycoverage_cci_delete.bak` | 0.074s | 0.087s | 0.161s |
| `dirtycoverage_cci_update.bak` | 0.079s | 0.085s | 0.164s |
| `dirtycoverage_committed_delete.bak` | 0.028s | 0.036s | 0.064s |
| `dirtycoverage_committed_delete_v2.bak` | 0.03s | 0.032s | 0.062s |
| `dirtycoverage_committed_delete_v3.bak` | 0.035s | 0.05s | 0.085s |
| `dirtycoverage_committed_delete_v4.bak` | 0.15s | 0.061s | 0.211s |
| `dirtycoverage_committed_update.bak` | 0.039s | 0.03s | 0.069s |
| `dirtycoverage_committed_update_v2.bak` | 0.029s | 0.043s | 0.072s |
| `dirtycoverage_committed_update_v3.bak` | 0.045s | 0.054s | 0.099s |
| `dirtycoverage_committed_update_v4.bak` | 0.16s | 0.065s | 0.225s |
| `dirtycoverage_concurrent.bak` | 0.054s | 0.029s | 0.083s |
| `dirtycoverage_createidx.bak` | 0.052s | 0.03s | 0.082s |
| `dirtycoverage_createtable.bak` | 0.044s | 0.029s | 0.073s |
| `dirtycoverage_delete.bak` | 0.048s | 0.03s | 0.078s |
| `dirtycoverage_dropcol.bak` | 0.057s | 0.037s | 0.094s |
| `dirtycoverage_dropidx.bak` | 0.048s | 0.029s | 0.077s |
| `dirtycoverage_droptable.bak` | 0.047s | 0.031s | 0.078s |
| `dirtycoverage_heap_forward.bak` | 0.05s | 0.03s | 0.08s |
| `dirtycoverage_large_dirty.bak` | 0.325s | 0.032s | 0.357s |
| `dirtycoverage_lob_update.bak` | 0.064s | 0.038s | 0.102s |
| `dirtycoverage_maxrow.bak` | 0.029s | 0.03s | 0.059s |
| `dirtycoverage_nchar_delete.bak` | 0.047s | 0.029s | 0.076s |
| `dirtycoverage_nested.bak` | 0.052s | 0.028s | 0.08s |
| `dirtycoverage_null_update.bak` | 0.045s | 0.036s | 0.081s |
| `dirtycoverage_rebuildidx.bak` | 0.053s | 0.038s | 0.091s |
| `dirtycoverage_rich_insert.bak` | 0.047s | 0.032s | 0.079s |
| `dirtycoverage_rich_update.bak` | 0.045s | 0.033s | 0.078s |
| `dirtycoverage_savepoint.bak` | 0.052s | 0.035s | 0.087s |
| `dirtycoverage_snapshot_update.bak` | 0.044s | 0.027s | 0.071s |
| `dirtycoverage_switch.bak` | 0.06s | 0.031s | 0.091s |
| `dirtycoverage_temporal_update.bak` | 0.054s | 0.03s | 0.084s |
| `dirtycoverage_truncate.bak` | 0.061s | 0.03s | 0.091s |
| `dirtycoverage_two_tx.bak` | 0.048s | 0.029s | 0.077s |
| `dirtycoverage_uncommitted.bak` | 0.062s | 0.031s | 0.093s |
| `dirtycoverage_update.bak` | 0.047s | 0.029s | 0.076s |
| `filtered_ncci_full.bak` | 0.048s | 0.033s | 0.081s |
| `float_extreme_full.bak` | 0.028s | 0.033s | 0.061s |
| `forwarded_records_full.bak` | 0.064s | 0.045s | 0.109s |
| `ghost_records_full.bak` | 0.037s | 0.039s | 0.076s |
| `heapcoverage_large.bak` | 0.028s | 0.044s | 0.072s |
| `heapcoverage_large_50000.bak` | 0.096s | 0.321s | 0.417s |
| `hierarchyid_extract_full.bak` | 0.029s | 0.035s | 0.064s |
| `high_slot_density_full.bak` | 0.04s | 0.18s | 0.22s |
| `identity_coverage_full.bak` | 0.047s | 0.032s | 0.079s |
| `incrementalcoverage_diff_01.bak` | 0.04s | 0.015s | 0.055s |
| `incrementalcoverage_diff_02.bak` | 0.04s | 0.01s | 0.05s |
| `incrementalcoverage_diff_03.bak` | 0.043s | 0.014s | 0.057s |
| `incrementalcoverage_diff_04.bak` | 0.049s | 0.019s | 0.068s |
| `incrementalcoverage_diff_05.bak` | 0.053s | 0.017s | 0.07s |
| `incrementalcoverage_diff_06.bak` | 0.053s | 0.01s | 0.063s |
| `incrementalcoverage_full.bak` | 0.033s | 0.024s | 0.057s |
| `layoutcoverage_full.bak` | 0.149s | 0.38s | 0.529s |
| `max_row_width_full.bak` | 0.032s | 0.03s | 0.062s |
| `mixed_collation_full.bak` | 0.028s | 0.03s | 0.058s |
| `multi_rowgroup_full.bak` | 0.031s | 0.038s | 0.069s |
| `ncci_heap_full.bak` | 0.045s | 0.031s | 0.076s |
| `ncci_types_full.bak` | 0.068s | 0.17s | 0.238s |
| `ndfcoverage_full.bak` | 0.039s | 0.034s | 0.073s |
| `nvarchar_max_u21_full.bak` | 0.029s | 0.034s | 0.063s |
| `pagecomp_anchor_full.bak` | 0.12s | 0.084s | 0.204s |
| `pagecomp_long_prefix_full.bak` | 0.036s | 0.029s | 0.065s |
| `pfor_columnstore_full.bak` | 0.093s | 0.826s | 0.919s |
| `pfor_columnstore_random_full.bak` | 0.093s | 0.82s | 0.913s |
| `realworld_numeric_digest_full.bak` | 0.06s | 0.074s | 0.134s |
| `rowboundary_full.bak` | 0.034s | 0.041s | 0.075s |
| `rowstore_hash_pii_full.bak` | 0.028s | 0.03s | 0.058s |
| `rowstore_lob_image_full.bak` | 0.033s | 0.031s | 0.064s |
| `rowstore_lob_markup_full.bak` | 0.03s | 0.036s | 0.066s |
| `rowversion_extract_full.bak` | 0.028s | 0.032s | 0.06s |
| `sparse_full.bak` | 0.076s | 0.079s | 0.155s |
| `spatial_edge_full.bak` | 0.041s | 0.052s | 0.093s |
| `spatial_index_full.bak` | 0.048s | 0.033s | 0.081s |
| `sql_variant_extract_full.bak` | 0.035s | 0.036s | 0.071s |
| `striped_full_1.bak` | 0.041s | 0.016s | 0.057s |
| `striped_single.bak` | 0.051s | 0.041s | 0.092s |
| `surrogate_pairs_full.bak` | 0.029s | 0.03s | 0.059s |
| `tabletype_cci_large_full.bak` | 0.044s | 0.051s | 0.095s |
| `tabletypecoverage_diff.bak` | 0.135s | 0.067s | 0.202s |
| `tabletypecoverage_full.bak` | 0.085s | 0.094s | 0.179s |
| `temporal_hidden_full.bak` | 0.039s | 0.041s | 0.08s |
| `torn_page_full.bak` | 0.027s | 0.033s | 0.06s |
| `typecoverage_full.bak` | 0.06s | 0.051s | 0.111s |
| `typed_xml_full.bak` | 0.038s | 0.03s | 0.068s |
| `unicode_codepage_coverage.bak` | 0.049s | 0.042s | 0.091s |
| `xml_index_full.bak` | 0.053s | 0.031s | 0.084s |
| `xmlcoverage_full.bak` | 0.038s | 0.04s | 0.078s |
| `xmlheap_full.bak` | 0.045s | 0.047s | 0.092s |
| `xtp_checkpoint_straddle_full.bak` | 1.92s | 0.353s | 2.273s |
| `xtp_probe_full.bak` | 0.076s | 0.039s | 0.115s |
| `xtp_rich_full.bak` | 0.061s | 0.036s | 0.097s |
| `xtp_simple_full.bak` | 0.058s | 0.038s | 0.096s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-13 · 133 fixtures · 133 pass · 0 xfail · 0 fail_
