# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2022`.

**131 fixtures · 127 pass · 2 xfail (known gap) · 2 fail**

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

Memory-optimized (In-Memory OLTP / XTP) tables store their data in checkpoint files rather than 8 KB pages, so they are inherently absent from extraction output.  Their row/column counts are scored as `—` (expected skip), not as a mismatch.

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
| `boundarycoverage_datetime_full.bak` | 10,800 | 27 | 8/9 ⚠ ⚠ (`dbo.tb_datetimeoffset_3`) | **24/24** | **48/48** | 8/9 ⚠ | 18001/19200 ⚠ | ✗ |
| `boundarycoverage_full.bak` | 9,600 | 24 | **8/8** | **24/24** | **48/48** | **8/8** | **19200/19200** | ✓ |
| `catalog_ss2022.bak` | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **3/3** | ✓ |
| `cci_binary_varbinary_compare_full.bak` | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
| `cci_bitpack_probe_bigint_full.bak` | 4,400,000 | 3 | 1/2 ⚠ ⚠ (`dbo.cci_bitpack_probe_bigint`) | **3/3** | **6/6** | **2/2** | digest ⚠ | ~ |
| `cci_bitpack_probe_full.bak` | 400,000 | 6 | **2/2** | **6/6** | **12/12** | **2/2** | digest | ✓ |
| `cci_bitpack_probe_highbase_full.bak` | 400,000 | 3 | **2/2** | **3/3** | **6/6** | **2/2** | digest | ✓ |
| `cci_btree_nci_full.bak` | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_computed_full.bak` | 2,400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `cci_enc5_largepool_full.bak` | 160,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest ⚠ | ~ |
| `cci_extended_full.bak` | 6,000 | 10 | **5/5** | **10/10** | **20/20** | **5/5** | digest | ✓ |
| `cci_lob_full.bak` | 4,796 | 7 | **4/4** | **7/7** | **14/14** | **4/4** | digest | ✓ |
| `cci_reorganize_full.bak` | 3,200 | 5 | **3/3** | **5/5** | **10/10** | **3/3** | digest | ✓ |
| `cci_string_minmax_full.bak` | 2,400 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
| `cci_switch_full.bak` | 2,400 | 7 | **3/3** | **4/4** | **8/8** | **3/3** | digest | ✓ |
| `cci_types_large_full.bak` | 6,000 | 10 | **5/5** | **10/10** | **18/18** | **5/5** | digest | ✓ |
| `cci_varbinary_micro_full.bak` | 48 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `cci_varbinary_probe_full.bak` | 2,528 | 6 | **3/3** | **6/6** | **12/12** | **3/3** | digest | ✓ |
| `columnstore_minimal.bak` | 11,111 | 60 | **5/5** | **60/60** | **120/120** | **5/5** | digest | ✓ |
| `compressioncoverage_full.bak` | 1,994 | 239 | **19/19** | **239/239** | **464/464** | **19/19** | **17902/17902** | ✓ |
| `computedcoverage_full.bak` | 6 | 8 | **2/2** | **8/8** | **16/16** | **2/2** | **18/18** | ✓ |
| `constraintcoverage_full.bak` | 27 | 27 | **9/9** | **27/27** | **54/54** | **9/9** | **54/54** | ✓ |
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
| `featurecoverage_full.bak` | 1,124 | 43 | **10/10** | **29/29** | **58/58** | **10/10** | **3298/3298** | ✓ |
| `filtered_ncci_full.bak` | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | **800/800** | ✓ |
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
| `ordered_cci_full.bak` | 3,600 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `pagecomp_anchor_full.bak` | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | **35000/35000** | ✓ |
| `pfor_columnstore_full.bak` | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `pfor_columnstore_random_full.bak` | 400,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `rowboundary_full.bak` | 230 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `rowstore_lob_image_full.bak` | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | **12/12** | ✓ |
| `rowversion_extract_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `sparse_full.bak` | 10,000 | 6 | **1/1** | **6/6** | **10/10** | **1/1** | **50000/50000** | ✓ |
| `spatial_edge_full.bak` | 8 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **8/8** | ✓ |
| `spatial_index_full.bak` | 400 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **400/400** | ✓ |
| `sql_variant_extract_full.bak` | 6 | 2 | **1/1** | **2/2** | **2/2** | **1/1** | **6/6** | ✓ |
| `striped_full_1.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `striped_single.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `surrogate_pairs_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `tabletype_cci_large_full.bak` | 1,200 | 25 | **1/1** | **25/25** | **48/48** | **1/1** | digest ⚠ | ✗ |
| `tabletypecoverage_diff.bak` | 30 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **198/198** | ✓ |
| `tabletypecoverage_full.bak` | 20 | 161 | **5/5** | **161/161** | **272/272** | **5/5** | **132/132** | ✓ |
| `temporal_hidden_full.bak` | 14 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **30/30** | ✓ |
| `typecoverage_full.bak` | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | **321/321** | ✓ |
| `typecoverage_full_compressed.bak` | 162 | 101 | **34/34** | **101/101** | **198/198** | **34/34** | **321/321** | ✓ |
| `typed_xml_full.bak` | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **3/3** | ✓ |
| `unicode_codepage_coverage.bak` | 15 | 52 | **13/13** | **52/52** | **104/104** | **13/13** | **45/45** | ✓ |
| `utf8_collation_full.bak` | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **14/14** | ✓ |
| `xml_index_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `xmlcoverage_full.bak` | 13 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **26/26** | ✓ |
| `xmlheap_full.bak` | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | **1200/1200** | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.044s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | 3 | ✓ | **6/6** | — | ✓ | cells **15/15** ✓ |

### `archive_columnstore_partition_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.121 MB · extracted in 1.007s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.117 MB · extracted in 0.373s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_columnstore_types_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.117 MB · extracted in 0.368s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_binary10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_char10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nchar10` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_nvarchar20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_uuid` | 35,000 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.archive_varbinary20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.archive_varchar20` | 35,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB · extracted in 0.049s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB · extracted in 0.061s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.117 MB · extracted in 0.14s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB · extracted in 0.128s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells ✗ (cells 1201/2400; bad: v, digest:v) |
| `dbo.tb_date` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | 1,200 | ✗ | — | — | ✗ | missing from output; cells ✗ () |
| `dbo.tb_decimal_18_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB · extracted in 0.103s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bigint` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_float` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_int` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_money` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_real` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smallint` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smallmoney` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_tinyint` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `catalog_ss2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB · extracted in 0.038s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `cci_binary_varbinary_compare_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB · extracted in 0.053s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_bigint_full.bak` — ~ xfail

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 43.148 MB · extracted in 0.818s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | 2,200,000 | ✗ | **2/2** | **4/4** | ✓ | cells ✗ (bad: digest:pk, digest:dt) |
| `dbo.fkr__seed` | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB · extracted in 0.207s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_highbase_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB · extracted in 0.196s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB · extracted in 0.067s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.052s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — ~ xfail

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB · extracted in 0.247s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells ✗ (bad: digest:login, digest:code) |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB · extracted in 0.089s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB · extracted in 0.067s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB · extracted in 0.058s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB · extracted in 0.052s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB · extracted in 0.055s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB · extracted in 0.091s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB · extracted in 0.06s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB · extracted in 0.06s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB · extracted in 0.174s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressioncoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB · extracted in 0.126s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cmp_columnstore` | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_columnstore_archive` | 200 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `dbo.cmp_none` | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_page` | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_page_floats` | 7 | ✓ | **4/4** | **8/8** | ✓ | cells **21/21** ✓ |
| `dbo.cmp_page_lob` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.cmp_page_variant` | 9 | ✓ | **2/2** | **2/2** | ✓ | cells **9/9** ✓ |
| `dbo.cmp_page_wide` | 50 | ✓ | **41/41** | **82/82** | ✓ | cells **2000/2000** ✓ |
| `dbo.cmp_row` | 200 | ✓ | **23/23** | **44/44** | ✓ | cells **4400/4400** ✓ |
| `dbo.cmp_row_floats` | 7 | ✓ | **4/4** | **8/8** | ✓ | cells **21/21** ✓ |
| `dbo.cmp_row_lob` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.cmp_row_variant` | 9 | ✓ | **2/2** | **2/2** | ✓ | cells **9/9** ✓ |
| `dbo.cmp_row_wide` | 50 | ✓ | **41/41** | **82/82** | ✓ | cells **2000/2000** ✓ |
| `dbo.cs_probe` | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |
| `dbo.fwd_heap` | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.ghost_heap` | 250 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.sparse_cols` | 200 | ✓ | **4/4** | **8/8** | ✓ | cells **600/600** ✓ |
| `dbo.uniquifier_none` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.uniquifier_row` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `computedcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.039s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB · extracted in 0.056s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cc_check_constraint` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_default_constraint` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_fk_child` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_fk_parent` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_index_nonclustered` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_pk` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_pk_nonclustered` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_unique_constraint` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.cc_unique_index` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |

### `covering_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.195 MB · extracted in 0.119s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells **5000/5000** ✓ |

### `cs_lob_preamble2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.605 MB · extracted in 0.072s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells **1200/1200** ✓ |

### `delta_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB · extracted in 0.049s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.066s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.04s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB · extracted in 0.059s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.04s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.238 MB · extracted in 0.107s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.301 MB · extracted in 0.207s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.042s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 56.434 MB · extracted in 0.632s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.padding_fill` | 250,000 | ✓ | **2/2** | **4/4** | ✓ | cells **250000/250000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB · extracted in 0.054s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.301 MB · extracted in 0.155s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.036s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 115.879 MB · extracted in 9.463s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 300,000 | ✓ | **3/3** | **6/6** | ✓ | cells **600000/600000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB · extracted in 0.056s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.113 MB · extracted in 0.11s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_compress_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.075s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_concurrent.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 114 | ✓ | **4/4** | **8/8** | ✓ | cells **342/342** ✓ |

### `dirtycoverage_createidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.072s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.044s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.048s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.065s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_insert_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.073s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.iu_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_large_dirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB · extracted in 0.331s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB · extracted in 0.085s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.043s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_multi_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.074s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.multi_update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_nchar_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.07s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.072s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.071s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.068s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.072s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.071s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.066s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB · extracted in 0.047s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB · extracted in 0.068s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB · extracted in 0.067s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.071s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.074s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_wide.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.071s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide2_test` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `featurecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.246 MB · extracted in 0.115s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_col` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `dbo.graph_follows` | 2 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.graph_person` | 3 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.ledger_account` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **6/6** ✓ |
| `dbo.long_text` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `dbo.memory_oltp` | 3 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `dbo.ncci_table` | 1,024 | ✓ | **4/4** | **8/8** | ✓ | cells **3072/3072** ✓ |
| `dbo.temporal_current` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |
| `dbo.temporal_history` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.utf8_collation` | 6 | ✓ | **4/4** | **8/8** | ✓ | cells **18/18** ✓ |

### `filtered_ncci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB · extracted in 0.05s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `forwarded_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 16.117 MB · extracted in 0.094s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `geocoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB · extracted in 0.074s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Locations` | 5 | ✓ | **5/5** | **10/10** | ✓ | cells **20/20** ✓ |
| `dbo.LocationsNone` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.LocationsRow` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.spatial_lob_test` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.SpatialCurves` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.SpatialLob` | 2 | ✓ | **2/2** | **4/4** | ✓ | cells **2/2** ✓ |
| `dbo.SpatialZM` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `geotest.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB · extracted in 0.05s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Locations` | 5 | ✓ | **5/5** | **10/10** | ✓ | cells **20/20** ✓ |
| `dbo.LocationsNone` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.LocationsRow` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.spatial_lob_test` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |

### `ghost_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.043s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB · extracted in 0.047s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.117 MB · extracted in 0.119s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.93 MB · extracted in 0.08s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.176 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB · extracted in 0.047s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB · extracted in 0.05s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.738 MB · extracted in 0.055s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB · extracted in 0.04s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.051 MB · extracted in 0.283s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | 3 | ✓ | **1023/1023** | — | ✓ | cells **3066/3066** ✓ |
| `dbo.layout_cols_1024` | 3 | ✓ | **1024/1024** | — | ✓ | cells **3069/3069** ✓ |
| `dbo.layout_cols_30` | 3 | ✓ | **30/30** | **60/60** | ✓ | cells **87/87** ✓ |
| `dbo.layout_cols_31` | 3 | ✓ | **31/31** | **62/62** | ✓ | cells **90/90** ✓ |
| `dbo.layout_pk_bigint_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_bigint_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_binary16_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_char10_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_date_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_datetime2_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_decimal18_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_int_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nchar10_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_nvarchar50_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_smallint_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_tinyint_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_first` | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_last` | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_penult` | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_uniqueidentifier_second` | 3 | ✓ | **6/6** | **10/10** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_first` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_last` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_penult` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `dbo.layout_pk_varchar100_second` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |

### `legacytext.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB · extracted in 0.051s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.legacy_lob` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `max_row_width_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `multi_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB · extracted in 0.059s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB · extracted in 0.116s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_binary` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_bit` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_char` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_date` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetime2` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetimeoffset` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_float` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_money` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_nchar` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_nvarchar` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_real` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_smallint` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_smallmoney` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_time` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_tinyint` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_uuid` | 1,203 | ✓ | **2/2** | **2/2** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_varbinary` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_varchar` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |

### `ndfcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.117 MB · extracted in 0.045s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `ordered_cci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB · extracted in 0.055s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ordered_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.regular_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `pagecomp_anchor_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB · extracted in 0.126s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pfor_columnstore_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB · extracted in 0.302s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB · extracted in 0.315s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `rowboundary_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB · extracted in 0.147s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_lob_image_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB · extracted in 0.043s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowversion_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB · extracted in 0.097s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB · extracted in 0.048s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.geometry_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |

### `spatial_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB · extracted in 0.053s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.043s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | 6 | ✓ | **2/2** | **2/2** | ✓ | cells **6/6** ✓ |

### `striped_full_1.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.266 MB · extracted in 0.06s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB · extracted in 0.057s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB · extracted in 0.041s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB · extracted in 0.065s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells ✗ (bad: digest:c_bit) |

### `tabletypecoverage_diff.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB · extracted in 0.125s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.113 MB · extracted in 0.093s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_hidden_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `typecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.551 MB · extracted in 0.164s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.t_bigint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_binary_8` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_bit` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_char_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_date` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime2_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetimeoffset_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_decimal_38_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_float` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_geography` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `dbo.t_geometry` | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.t_hierarchyid` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.t_image` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_int` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_money` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nchar_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_ntext` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_numeric_18_4` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nvarchar_50` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_real` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_rowversion` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.t_smalldatetime` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallmoney` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_sql_variant` | 16 | ✓ | **3/3** | **4/4** | ✓ | cells **32/32** ✓ |
| `dbo.t_text` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_time_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_tinyint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_uniqueidentifier` | 4 | ✓ | **3/3** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.t_varbinary_max` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_varchar_max` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_xml` | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |

### `typecoverage_full_compressed.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.535 MB · extracted in 0.146s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_links` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.t_bigint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_binary_8` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_bit` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_char_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_date` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetime2_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_datetimeoffset_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_decimal_38_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_float` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_geography` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `dbo.t_geometry` | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.t_hierarchyid` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.t_image` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_int` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_money` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nchar_10` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_ntext` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_numeric_18_4` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_nvarchar_50` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_real` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_rowversion` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.t_smalldatetime` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_smallmoney` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_sql_variant` | 16 | ✓ | **3/3** | **4/4** | ✓ | cells **32/32** ✓ |
| `dbo.t_text` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_time_7` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_tinyint` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_uniqueidentifier` | 4 | ✓ | **3/3** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.t_varbinary_max` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_varchar_max` | 4 | ✓ | **3/3** | **6/6** | ✓ | cells **8/8** ✓ |
| `dbo.t_xml` | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |

### `typed_xml_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB · extracted in 0.046s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `unicode_codepage_coverage.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.551 MB · extracted in 0.088s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cp_cp1250` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1251` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells **6/6** ✓ |
| `dbo.cp_cp1253` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1254` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1255` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1256` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1257` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp1258` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp874` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp932` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells **6/6** ✓ |
| `dbo.cp_cp936` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp949` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |
| `dbo.cp_cp950` | 1 | ✓ | **4/4** | **8/8** | ✓ | cells **3/3** ✓ |

### `utf8_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB · extracted in 0.044s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |
| `dbo.utf8_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `xml_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB · extracted in 0.048s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB · extracted in 0.043s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | 13 | ✓ | **3/3** | **6/6** | ✓ | cells **26/26** ✓ |

### `xmlheap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.176 MB · extracted in 0.057s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

---

_Generated 2026-06-27 · 131 fixtures · 127 pass · 2 xfail · 2 fail_
