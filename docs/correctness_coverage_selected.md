# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_2022 tests/fixtures_2017/alias_types_full.bak tests/fixtures_2017/archive_columnstore_partition_full.bak tests/fixtures_2017/archive_columnstore_types_full.bak tests/fixtures_2017/archive_columnstore_types_random_full.bak tests/fixtures_2017/archive_single_chunk_full.bak tests/fixtures_2017/archive_single_chunk_random_full.bak tests/fixtures_2017/archivenull_full.bak tests/fixtures_2017/backup_blocksize_full.bak tests/fixtures_2017/boundarycoverage_datetime_full.bak tests/fixtures_2017/boundarycoverage_full.bak tests/fixtures_2017/cci_binary_varbinary_compare_full.bak tests/fixtures_2017/cci_btree_nci_full.bak tests/fixtures_2017/cci_computed_full.bak tests/fixtures_2017/cci_enc5_largepool_full.bak tests/fixtures_2017/cci_enc5_largepool_matrix_full.bak tests/fixtures_2017/cci_extended_full.bak tests/fixtures_2017/cci_lob_full.bak tests/fixtures_2017/cci_reorganize_full.bak tests/fixtures_2017/cci_string_dict_regression_full.bak tests/fixtures_2017/cci_string_minmax_full.bak tests/fixtures_2017/cci_switch_full.bak tests/fixtures_2017/cci_types_large_full.bak tests/fixtures_2017/cci_varbinary_micro_full.bak tests/fixtures_2017/cci_varbinary_probe_full.bak tests/fixtures_2017/columnstore_minimal.bak tests/fixtures_2017/compressed_nvarchar_full.bak tests/fixtures_2017/compressioncoverage_full.bak tests/fixtures_2017/computedcoverage_full.bak tests/fixtures_2017/constraintcoverage_full.bak tests/fixtures_2017/covering_index_full.bak tests/fixtures_2017/cs_lob_preamble.bak tests/fixtures_2017/delta_rowgroup_full.bak tests/fixtures_2017/dirtycoverage_aborted_xact.bak tests/fixtures_2017/dirtycoverage_addcol.bak tests/fixtures_2017/dirtycoverage_addnotnull.bak tests/fixtures_2017/dirtycoverage_alldirty.bak tests/fixtures_2017/dirtycoverage_altercol.bak tests/fixtures_2017/dirtycoverage_altercol_rewrite.bak tests/fixtures_2017/dirtycoverage_alterdb.bak tests/fixtures_2017/dirtycoverage_cci_delete.bak tests/fixtures_2017/dirtycoverage_cci_update.bak tests/fixtures_2017/dirtycoverage_committed_delete.bak tests/fixtures_2017/dirtycoverage_committed_delete_v2.bak tests/fixtures_2017/dirtycoverage_committed_delete_v3.bak tests/fixtures_2017/dirtycoverage_committed_delete_v4.bak tests/fixtures_2017/dirtycoverage_committed_update.bak tests/fixtures_2017/dirtycoverage_committed_update_v2.bak tests/fixtures_2017/dirtycoverage_committed_update_v3.bak tests/fixtures_2017/dirtycoverage_committed_update_v4.bak tests/fixtures_2017/dirtycoverage_concurrent.bak tests/fixtures_2017/dirtycoverage_createidx.bak tests/fixtures_2017/dirtycoverage_createtable.bak tests/fixtures_2017/dirtycoverage_delete.bak tests/fixtures_2017/dirtycoverage_dropcol.bak tests/fixtures_2017/dirtycoverage_dropidx.bak tests/fixtures_2017/dirtycoverage_droptable.bak tests/fixtures_2017/dirtycoverage_heap_forward.bak tests/fixtures_2017/dirtycoverage_large_dirty.bak tests/fixtures_2017/dirtycoverage_lob_update.bak tests/fixtures_2017/dirtycoverage_maxrow.bak tests/fixtures_2017/dirtycoverage_nchar_delete.bak tests/fixtures_2017/dirtycoverage_nested.bak tests/fixtures_2017/dirtycoverage_null_update.bak tests/fixtures_2017/dirtycoverage_rebuildidx.bak tests/fixtures_2017/dirtycoverage_rich_insert.bak tests/fixtures_2017/dirtycoverage_rich_update.bak tests/fixtures_2017/dirtycoverage_savepoint.bak tests/fixtures_2017/dirtycoverage_snapshot_update.bak tests/fixtures_2017/dirtycoverage_switch.bak tests/fixtures_2017/dirtycoverage_temporal_update.bak tests/fixtures_2017/dirtycoverage_truncate.bak tests/fixtures_2017/dirtycoverage_two_tx.bak tests/fixtures_2017/dirtycoverage_uncommitted.bak tests/fixtures_2017/dirtycoverage_update.bak tests/fixtures_2017/filtered_ncci_full.bak tests/fixtures_2017/float_extreme_full.bak tests/fixtures_2017/forwarded_records_full.bak tests/fixtures_2017/ghost_records_full.bak tests/fixtures_2017/heapcoverage_large.bak tests/fixtures_2017/heapcoverage_large_50000.bak tests/fixtures_2017/hierarchyid_extract_full.bak tests/fixtures_2017/high_slot_density_full.bak tests/fixtures_2017/incrementalcoverage_diff_01.bak tests/fixtures_2017/incrementalcoverage_diff_02.bak tests/fixtures_2017/incrementalcoverage_diff_03.bak tests/fixtures_2017/incrementalcoverage_diff_04.bak tests/fixtures_2017/incrementalcoverage_diff_05.bak tests/fixtures_2017/incrementalcoverage_diff_06.bak tests/fixtures_2017/incrementalcoverage_full.bak tests/fixtures_2017/layoutcoverage_full.bak tests/fixtures_2017/max_row_width_full.bak tests/fixtures_2017/mixed_collation_full.bak tests/fixtures_2017/multi_rowgroup_full.bak tests/fixtures_2017/ncci_heap_full.bak tests/fixtures_2017/ncci_types_full.bak tests/fixtures_2017/ndfcoverage_full.bak tests/fixtures_2017/nvarchar_max_u21_full.bak tests/fixtures_2017/pagecomp_anchor_full.bak tests/fixtures_2017/pfor_columnstore_full.bak tests/fixtures_2017/pfor_columnstore_random_full.bak tests/fixtures_2017/realworld_numeric_digest_full.bak tests/fixtures_2017/rowboundary_full.bak tests/fixtures_2017/rowstore_hash_pii_full.bak tests/fixtures_2017/rowstore_lob_image_full.bak tests/fixtures_2017/rowstore_lob_markup_full.bak tests/fixtures_2017/rowversion_extract_full.bak tests/fixtures_2017/sparse_full.bak tests/fixtures_2017/spatial_edge_full.bak tests/fixtures_2017/spatial_index_full.bak tests/fixtures_2017/sql_variant_extract_full.bak tests/fixtures_2017/striped_full_1.bak tests/fixtures_2017/striped_full_2.bak tests/fixtures_2017/striped_single.bak tests/fixtures_2017/surrogate_pairs_full.bak tests/fixtures_2017/tabletype_cci_large_full.bak tests/fixtures_2017/tabletypecoverage_diff.bak tests/fixtures_2017/tabletypecoverage_full.bak tests/fixtures_2017/tde_full.bak tests/fixtures_2017/temporal_hidden_full.bak tests/fixtures_2017/torn_page_full.bak tests/fixtures_2017/typecoverage_full.bak tests/fixtures_2017/typed_xml_full.bak tests/fixtures_2017/unicode_codepage_coverage.bak tests/fixtures_2017/xml_index_full.bak tests/fixtures_2017/xmlcoverage_full.bak tests/fixtures_2017/xmlheap_full.bak tests/fixtures_2017/xtp_probe_full.bak tests/fixtures_2017/xtp_rich_full.bak tests/fixtures_2017/xtp_simple_full.bak tests/fixtures_2019/alias_types_full.bak tests/fixtures_2019/archive_columnstore_partition_full.bak tests/fixtures_2019/archive_columnstore_types_full.bak tests/fixtures_2019/archive_columnstore_types_random_full.bak tests/fixtures_2019/archive_single_chunk_full.bak tests/fixtures_2019/archive_single_chunk_random_full.bak tests/fixtures_2019/archivenull_full.bak tests/fixtures_2019/backup_blocksize_full.bak tests/fixtures_2019/boundarycoverage_datetime_full.bak tests/fixtures_2019/boundarycoverage_full.bak tests/fixtures_2019/catalog_ss2019.bak tests/fixtures_2019/cci_binary_varbinary_compare_full.bak tests/fixtures_2019/cci_btree_nci_full.bak tests/fixtures_2019/cci_computed_full.bak tests/fixtures_2019/cci_enc5_largepool_full.bak tests/fixtures_2019/cci_enc5_largepool_matrix_full.bak tests/fixtures_2019/cci_extended_full.bak tests/fixtures_2019/cci_lob_full.bak tests/fixtures_2019/cci_reorganize_full.bak tests/fixtures_2019/cci_string_dict_regression_full.bak tests/fixtures_2019/cci_string_minmax_full.bak tests/fixtures_2019/cci_switch_full.bak tests/fixtures_2019/cci_types_large_full.bak tests/fixtures_2019/cci_varbinary_micro_full.bak tests/fixtures_2019/cci_varbinary_probe_full.bak tests/fixtures_2019/columnstore_minimal.bak tests/fixtures_2019/compressed_nvarchar_full.bak tests/fixtures_2019/compressioncoverage_full.bak tests/fixtures_2019/computedcoverage_full.bak tests/fixtures_2019/constraintcoverage_full.bak tests/fixtures_2019/covering_index_full.bak tests/fixtures_2019/cs_lob_preamble.bak tests/fixtures_2019/delta_rowgroup_full.bak tests/fixtures_2019/dirtycoverage_aborted_xact.bak tests/fixtures_2019/dirtycoverage_addcol.bak tests/fixtures_2019/dirtycoverage_addnotnull.bak tests/fixtures_2019/dirtycoverage_alldirty.bak tests/fixtures_2019/dirtycoverage_altercol.bak tests/fixtures_2019/dirtycoverage_altercol_rewrite.bak tests/fixtures_2019/dirtycoverage_alterdb.bak tests/fixtures_2019/dirtycoverage_cci_delete.bak tests/fixtures_2019/dirtycoverage_cci_update.bak tests/fixtures_2019/dirtycoverage_committed_delete.bak tests/fixtures_2019/dirtycoverage_committed_delete_v2.bak tests/fixtures_2019/dirtycoverage_committed_delete_v3.bak tests/fixtures_2019/dirtycoverage_committed_delete_v4.bak tests/fixtures_2019/dirtycoverage_committed_update.bak tests/fixtures_2019/dirtycoverage_committed_update_v2.bak tests/fixtures_2019/dirtycoverage_committed_update_v3.bak tests/fixtures_2019/dirtycoverage_committed_update_v4.bak tests/fixtures_2019/dirtycoverage_concurrent.bak tests/fixtures_2019/dirtycoverage_createidx.bak tests/fixtures_2019/dirtycoverage_createtable.bak tests/fixtures_2019/dirtycoverage_delete.bak tests/fixtures_2019/dirtycoverage_dropcol.bak tests/fixtures_2019/dirtycoverage_dropidx.bak tests/fixtures_2019/dirtycoverage_droptable.bak tests/fixtures_2019/dirtycoverage_heap_forward.bak tests/fixtures_2019/dirtycoverage_large_dirty.bak tests/fixtures_2019/dirtycoverage_lob_update.bak tests/fixtures_2019/dirtycoverage_maxrow.bak tests/fixtures_2019/dirtycoverage_nchar_delete.bak tests/fixtures_2019/dirtycoverage_nested.bak tests/fixtures_2019/dirtycoverage_null_update.bak tests/fixtures_2019/dirtycoverage_rebuildidx.bak tests/fixtures_2019/dirtycoverage_rich_insert.bak tests/fixtures_2019/dirtycoverage_rich_update.bak tests/fixtures_2019/dirtycoverage_savepoint.bak tests/fixtures_2019/dirtycoverage_snapshot_update.bak tests/fixtures_2019/dirtycoverage_switch.bak tests/fixtures_2019/dirtycoverage_temporal_update.bak tests/fixtures_2019/dirtycoverage_truncate.bak tests/fixtures_2019/dirtycoverage_two_tx.bak tests/fixtures_2019/dirtycoverage_uncommitted.bak tests/fixtures_2019/dirtycoverage_update.bak tests/fixtures_2019/filtered_ncci_full.bak tests/fixtures_2019/float_extreme_full.bak tests/fixtures_2019/forwarded_records_full.bak tests/fixtures_2019/ghost_records_full.bak tests/fixtures_2019/heapcoverage_large.bak tests/fixtures_2019/heapcoverage_large_50000.bak tests/fixtures_2019/hierarchyid_extract_full.bak tests/fixtures_2019/high_slot_density_full.bak tests/fixtures_2019/incrementalcoverage_diff_01.bak tests/fixtures_2019/incrementalcoverage_diff_02.bak tests/fixtures_2019/incrementalcoverage_diff_03.bak tests/fixtures_2019/incrementalcoverage_diff_04.bak tests/fixtures_2019/incrementalcoverage_diff_05.bak tests/fixtures_2019/incrementalcoverage_diff_06.bak tests/fixtures_2019/incrementalcoverage_full.bak tests/fixtures_2019/layoutcoverage_full.bak tests/fixtures_2019/max_row_width_full.bak tests/fixtures_2019/mixed_collation_full.bak tests/fixtures_2019/multi_rowgroup_full.bak tests/fixtures_2019/ncci_heap_full.bak tests/fixtures_2019/ncci_types_full.bak tests/fixtures_2019/ndfcoverage_full.bak tests/fixtures_2019/nvarchar_max_u21_full.bak tests/fixtures_2019/pagecomp_anchor_full.bak tests/fixtures_2019/pfor_columnstore_full.bak tests/fixtures_2019/pfor_columnstore_random_full.bak tests/fixtures_2019/realworld_numeric_digest_full.bak tests/fixtures_2019/rowboundary_full.bak tests/fixtures_2019/rowstore_hash_pii_full.bak tests/fixtures_2019/rowstore_lob_image_full.bak tests/fixtures_2019/rowstore_lob_markup_full.bak tests/fixtures_2019/rowversion_extract_full.bak tests/fixtures_2019/sparse_full.bak tests/fixtures_2019/spatial_edge_full.bak tests/fixtures_2019/spatial_index_full.bak tests/fixtures_2019/sql_variant_extract_full.bak tests/fixtures_2019/striped_full_1.bak tests/fixtures_2019/striped_full_2.bak tests/fixtures_2019/striped_single.bak tests/fixtures_2019/surrogate_pairs_full.bak tests/fixtures_2019/tabletype_cci_large_full.bak tests/fixtures_2019/tabletypecoverage_diff.bak tests/fixtures_2019/tabletypecoverage_full.bak tests/fixtures_2019/tde_full.bak tests/fixtures_2019/temporal_hidden_full.bak tests/fixtures_2019/torn_page_full.bak tests/fixtures_2019/typecoverage_full.bak tests/fixtures_2019/typed_xml_full.bak tests/fixtures_2019/unicode_codepage_coverage.bak tests/fixtures_2019/utf8_collation_full.bak tests/fixtures_2019/xml_index_full.bak tests/fixtures_2019/xmlcoverage_full.bak tests/fixtures_2019/xmlheap_full.bak tests/fixtures_2022/alias_types_full.bak tests/fixtures_2022/archive_columnstore_partition_full.bak tests/fixtures_2022/archive_columnstore_types_full.bak tests/fixtures_2022/archive_columnstore_types_random_full.bak tests/fixtures_2022/archive_single_chunk_full.bak tests/fixtures_2022/archive_single_chunk_random_full.bak tests/fixtures_2022/archivenull_full.bak tests/fixtures_2022/backup_blocksize_full.bak tests/fixtures_2022/boundarycoverage_datetime_full.bak tests/fixtures_2022/boundarycoverage_full.bak tests/fixtures_2022/catalog_ss2022.bak tests/fixtures_2022/cci_binary_varbinary_compare_full.bak tests/fixtures_2022/cci_bitpack_probe_bigint_full.bak tests/fixtures_2022/cci_bitpack_probe_full.bak tests/fixtures_2022/cci_bitpack_probe_highbase_full.bak tests/fixtures_2022/cci_btree_nci_full.bak tests/fixtures_2022/cci_computed_full.bak tests/fixtures_2022/cci_enc5_largepool_full.bak tests/fixtures_2022/cci_enc5_largepool_matrix_full.bak tests/fixtures_2022/cci_extended_full.bak tests/fixtures_2022/cci_lob_full.bak tests/fixtures_2022/cci_reorganize_full.bak tests/fixtures_2022/cci_string_dict_regression_full.bak tests/fixtures_2022/cci_string_minmax_full.bak tests/fixtures_2022/cci_switch_full.bak tests/fixtures_2022/cci_types_large_full.bak tests/fixtures_2022/cci_varbinary_micro_full.bak tests/fixtures_2022/cci_varbinary_probe_full.bak tests/fixtures_2022/columnstore_minimal.bak tests/fixtures_2022/compressed_nvarchar_full.bak tests/fixtures_2022/compressioncoverage_full.bak tests/fixtures_2022/computedcoverage_full.bak tests/fixtures_2022/constraintcoverage_full.bak tests/fixtures_2022/corrupt_metadata_confidence_full.bak tests/fixtures_2022/covering_index_full.bak tests/fixtures_2022/cs_lob_preamble.bak tests/fixtures_2022/cs_lob_preamble2.bak tests/fixtures_2022/delta_rowgroup_full.bak tests/fixtures_2022/dirtycoverage_aborted_xact.bak tests/fixtures_2022/dirtycoverage_addcol.bak tests/fixtures_2022/dirtycoverage_addnotnull.bak tests/fixtures_2022/dirtycoverage_alldirty.bak tests/fixtures_2022/dirtycoverage_altercol.bak tests/fixtures_2022/dirtycoverage_altercol_rewrite.bak tests/fixtures_2022/dirtycoverage_alterdb.bak tests/fixtures_2022/dirtycoverage_cci_delete.bak tests/fixtures_2022/dirtycoverage_cci_update.bak tests/fixtures_2022/dirtycoverage_committed_delete.bak tests/fixtures_2022/dirtycoverage_committed_delete_v2.bak tests/fixtures_2022/dirtycoverage_committed_delete_v3.bak tests/fixtures_2022/dirtycoverage_committed_delete_v4.bak tests/fixtures_2022/dirtycoverage_committed_update.bak tests/fixtures_2022/dirtycoverage_committed_update_v2.bak tests/fixtures_2022/dirtycoverage_committed_update_v3.bak tests/fixtures_2022/dirtycoverage_committed_update_v4.bak tests/fixtures_2022/dirtycoverage_compress_update.bak tests/fixtures_2022/dirtycoverage_concurrent.bak tests/fixtures_2022/dirtycoverage_createidx.bak tests/fixtures_2022/dirtycoverage_createtable.bak tests/fixtures_2022/dirtycoverage_delete.bak tests/fixtures_2022/dirtycoverage_dropcol.bak tests/fixtures_2022/dirtycoverage_dropidx.bak tests/fixtures_2022/dirtycoverage_droptable.bak tests/fixtures_2022/dirtycoverage_heap_forward.bak tests/fixtures_2022/dirtycoverage_insert_update.bak tests/fixtures_2022/dirtycoverage_large_dirty.bak tests/fixtures_2022/dirtycoverage_lob_update.bak tests/fixtures_2022/dirtycoverage_maxrow.bak tests/fixtures_2022/dirtycoverage_multi_update.bak tests/fixtures_2022/dirtycoverage_nchar_delete.bak tests/fixtures_2022/dirtycoverage_nested.bak tests/fixtures_2022/dirtycoverage_null_update.bak tests/fixtures_2022/dirtycoverage_rebuildidx.bak tests/fixtures_2022/dirtycoverage_rich_insert.bak tests/fixtures_2022/dirtycoverage_rich_update.bak tests/fixtures_2022/dirtycoverage_savepoint.bak tests/fixtures_2022/dirtycoverage_snapshot_update.bak tests/fixtures_2022/dirtycoverage_switch.bak tests/fixtures_2022/dirtycoverage_temporal_update.bak tests/fixtures_2022/dirtycoverage_truncate.bak tests/fixtures_2022/dirtycoverage_two_tx.bak tests/fixtures_2022/dirtycoverage_uncommitted.bak tests/fixtures_2022/dirtycoverage_update.bak tests/fixtures_2022/dirtycoverage_wide.bak tests/fixtures_2022/featurecoverage_full.bak tests/fixtures_2022/filtered_ncci_full.bak tests/fixtures_2022/float_extreme_full.bak tests/fixtures_2022/forwarded_records_full.bak tests/fixtures_2022/geocoverage_full.bak tests/fixtures_2022/geotest.bak tests/fixtures_2022/ghost_records_full.bak tests/fixtures_2022/heapcoverage_large.bak tests/fixtures_2022/heapcoverage_large_50000.bak tests/fixtures_2022/hierarchyid_extract_full.bak tests/fixtures_2022/high_slot_density_full.bak tests/fixtures_2022/incrementalcoverage_diff_01.bak tests/fixtures_2022/incrementalcoverage_diff_02.bak tests/fixtures_2022/incrementalcoverage_diff_03.bak tests/fixtures_2022/incrementalcoverage_diff_04.bak tests/fixtures_2022/incrementalcoverage_diff_05.bak tests/fixtures_2022/incrementalcoverage_diff_06.bak tests/fixtures_2022/incrementalcoverage_full.bak tests/fixtures_2022/layoutcoverage_full.bak tests/fixtures_2022/legacytext.bak tests/fixtures_2022/max_row_width_full.bak tests/fixtures_2022/mixed_collation_full.bak tests/fixtures_2022/multi_rowgroup_full.bak tests/fixtures_2022/ncci_heap_full.bak tests/fixtures_2022/ncci_types_full.bak tests/fixtures_2022/ndfcoverage_full.bak tests/fixtures_2022/nvarchar_max_u21_full.bak tests/fixtures_2022/ordered_cci_full.bak tests/fixtures_2022/pagecomp_anchor_full.bak tests/fixtures_2022/pfor_columnstore_full.bak tests/fixtures_2022/pfor_columnstore_random_full.bak tests/fixtures_2022/realworld_numeric_digest_full.bak tests/fixtures_2022/rowboundary_full.bak tests/fixtures_2022/rowstore_hash_pii_full.bak tests/fixtures_2022/rowstore_lob_image_full.bak tests/fixtures_2022/rowstore_lob_markup_full.bak tests/fixtures_2022/rowversion_extract_full.bak tests/fixtures_2022/sparse_full.bak tests/fixtures_2022/spatial_edge_full.bak tests/fixtures_2022/spatial_index_full.bak tests/fixtures_2022/sql_variant_extract_full.bak tests/fixtures_2022/striped_full_1.bak tests/fixtures_2022/striped_full_2.bak tests/fixtures_2022/striped_single.bak tests/fixtures_2022/surrogate_pairs_full.bak tests/fixtures_2022/tabletype_cci_large_full.bak tests/fixtures_2022/tabletypecoverage_diff.bak tests/fixtures_2022/tabletypecoverage_full.bak tests/fixtures_2022/tde_full.bak tests/fixtures_2022/temporal_hidden_full.bak tests/fixtures_2022/torn_page_full.bak tests/fixtures_2022/typecoverage_full.bak tests/fixtures_2022/typecoverage_full_compressed.bak tests/fixtures_2022/typed_xml_full.bak tests/fixtures_2022/unicode_codepage_coverage.bak tests/fixtures_2022/utf8_collation_full.bak tests/fixtures_2022/xml_index_full.bak tests/fixtures_2022/xmlcoverage_full.bak tests/fixtures_2022/xmlheap_full.bak tests/fixtures_2022/xtp_probe_full.bak tests/fixtures_2022/xtp_rich_full.bak tests/fixtures_2022/xtp_simple_full.bak tests/fixtures_2025/alias_types_full.bak tests/fixtures_2025/archive_columnstore_partition_full.bak tests/fixtures_2025/archive_columnstore_types_full.bak tests/fixtures_2025/archive_columnstore_types_random_full.bak tests/fixtures_2025/archive_single_chunk_full.bak tests/fixtures_2025/archive_single_chunk_random_full.bak tests/fixtures_2025/archivenull_full.bak tests/fixtures_2025/backup_blocksize_full.bak tests/fixtures_2025/boundarycoverage_datetime_full.bak tests/fixtures_2025/boundarycoverage_full.bak tests/fixtures_2025/cci_binary_varbinary_compare_full.bak tests/fixtures_2025/cci_btree_nci_full.bak tests/fixtures_2025/cci_computed_full.bak tests/fixtures_2025/cci_enc5_largepool_full.bak tests/fixtures_2025/cci_enc5_largepool_matrix_full.bak tests/fixtures_2025/cci_extended_full.bak tests/fixtures_2025/cci_lob_full.bak tests/fixtures_2025/cci_reorganize_full.bak tests/fixtures_2025/cci_string_dict_regression_full.bak tests/fixtures_2025/cci_string_minmax_full.bak tests/fixtures_2025/cci_switch_full.bak tests/fixtures_2025/cci_types_large_full.bak tests/fixtures_2025/cci_varbinary_micro_full.bak tests/fixtures_2025/cci_varbinary_probe_full.bak tests/fixtures_2025/columnstore_minimal.bak tests/fixtures_2025/compressed_nvarchar_full.bak tests/fixtures_2025/compressioncoverage_full.bak tests/fixtures_2025/computedcoverage_full.bak tests/fixtures_2025/constraintcoverage_full.bak tests/fixtures_2025/covering_index_full.bak tests/fixtures_2025/cs_lob_preamble.bak tests/fixtures_2025/delta_rowgroup_full.bak tests/fixtures_2025/dirtycoverage_aborted_xact.bak tests/fixtures_2025/dirtycoverage_addcol.bak tests/fixtures_2025/dirtycoverage_addnotnull.bak tests/fixtures_2025/dirtycoverage_alldirty.bak tests/fixtures_2025/dirtycoverage_altercol.bak tests/fixtures_2025/dirtycoverage_altercol_rewrite.bak tests/fixtures_2025/dirtycoverage_alterdb.bak tests/fixtures_2025/dirtycoverage_cci_delete.bak tests/fixtures_2025/dirtycoverage_cci_update.bak tests/fixtures_2025/dirtycoverage_committed_delete.bak tests/fixtures_2025/dirtycoverage_committed_delete_v2.bak tests/fixtures_2025/dirtycoverage_committed_delete_v3.bak tests/fixtures_2025/dirtycoverage_committed_delete_v4.bak tests/fixtures_2025/dirtycoverage_committed_update.bak tests/fixtures_2025/dirtycoverage_committed_update_v2.bak tests/fixtures_2025/dirtycoverage_committed_update_v3.bak tests/fixtures_2025/dirtycoverage_committed_update_v4.bak tests/fixtures_2025/dirtycoverage_concurrent.bak tests/fixtures_2025/dirtycoverage_createidx.bak tests/fixtures_2025/dirtycoverage_createtable.bak tests/fixtures_2025/dirtycoverage_delete.bak tests/fixtures_2025/dirtycoverage_dropcol.bak tests/fixtures_2025/dirtycoverage_dropidx.bak tests/fixtures_2025/dirtycoverage_droptable.bak tests/fixtures_2025/dirtycoverage_heap_forward.bak tests/fixtures_2025/dirtycoverage_large_dirty.bak tests/fixtures_2025/dirtycoverage_lob_update.bak tests/fixtures_2025/dirtycoverage_maxrow.bak tests/fixtures_2025/dirtycoverage_nchar_delete.bak tests/fixtures_2025/dirtycoverage_nested.bak tests/fixtures_2025/dirtycoverage_null_update.bak tests/fixtures_2025/dirtycoverage_rebuildidx.bak tests/fixtures_2025/dirtycoverage_rich_insert.bak tests/fixtures_2025/dirtycoverage_rich_update.bak tests/fixtures_2025/dirtycoverage_savepoint.bak tests/fixtures_2025/dirtycoverage_snapshot_update.bak tests/fixtures_2025/dirtycoverage_switch.bak tests/fixtures_2025/dirtycoverage_temporal_update.bak tests/fixtures_2025/dirtycoverage_truncate.bak tests/fixtures_2025/dirtycoverage_two_tx.bak tests/fixtures_2025/dirtycoverage_uncommitted.bak tests/fixtures_2025/dirtycoverage_update.bak tests/fixtures_2025/featurecoverage_full.bak tests/fixtures_2025/filtered_ncci_full.bak tests/fixtures_2025/float_extreme_full.bak tests/fixtures_2025/forwarded_records_full.bak tests/fixtures_2025/ghost_records_full.bak tests/fixtures_2025/heapcoverage_large.bak tests/fixtures_2025/heapcoverage_large_50000.bak tests/fixtures_2025/hierarchyid_extract_full.bak tests/fixtures_2025/high_slot_density_full.bak tests/fixtures_2025/incrementalcoverage_diff_01.bak tests/fixtures_2025/incrementalcoverage_diff_02.bak tests/fixtures_2025/incrementalcoverage_diff_03.bak tests/fixtures_2025/incrementalcoverage_diff_04.bak tests/fixtures_2025/incrementalcoverage_diff_05.bak tests/fixtures_2025/incrementalcoverage_diff_06.bak tests/fixtures_2025/incrementalcoverage_full.bak tests/fixtures_2025/layoutcoverage_full.bak tests/fixtures_2025/max_row_width_full.bak tests/fixtures_2025/mixed_collation_full.bak tests/fixtures_2025/multi_rowgroup_full.bak tests/fixtures_2025/native_json_full.bak tests/fixtures_2025/ncci_heap_full.bak tests/fixtures_2025/ncci_types_full.bak tests/fixtures_2025/ndfcoverage_full.bak tests/fixtures_2025/nvarchar_max_u21_full.bak tests/fixtures_2025/ordered_cci_full.bak tests/fixtures_2025/pagecomp_anchor_full.bak tests/fixtures_2025/pfor_columnstore_full.bak tests/fixtures_2025/pfor_columnstore_random_full.bak tests/fixtures_2025/realworld_numeric_digest_full.bak tests/fixtures_2025/rowboundary_full.bak tests/fixtures_2025/rowstore_hash_pii_full.bak tests/fixtures_2025/rowstore_lob_image_full.bak tests/fixtures_2025/rowstore_lob_markup_full.bak tests/fixtures_2025/rowversion_extract_full.bak tests/fixtures_2025/sparse_full.bak tests/fixtures_2025/spatial_edge_full.bak tests/fixtures_2025/spatial_index_full.bak tests/fixtures_2025/sql_variant_extract_full.bak tests/fixtures_2025/striped_full_1.bak tests/fixtures_2025/striped_full_2.bak tests/fixtures_2025/striped_single.bak tests/fixtures_2025/surrogate_pairs_full.bak tests/fixtures_2025/tabletype_cci_large_full.bak tests/fixtures_2025/tabletypecoverage_diff.bak tests/fixtures_2025/tabletypecoverage_full.bak tests/fixtures_2025/tde_full.bak tests/fixtures_2025/temporal_hidden_full.bak tests/fixtures_2025/torn_page_full.bak tests/fixtures_2025/typecoverage_full.bak tests/fixtures_2025/typed_xml_full.bak tests/fixtures_2025/unicode_codepage_coverage.bak tests/fixtures_2025/utf8_collation_full.bak tests/fixtures_2025/vector_full.bak tests/fixtures_2025/xml_index_full.bak tests/fixtures_2025/xmlcoverage_full.bak tests/fixtures_2025/xmlheap_full.bak tests/fixtures_2025/xtp_probe_full.bak tests/fixtures_2025/xtp_rich_full.bak tests/fixtures_2025/xtp_simple_full.bak`.

**533 fixtures · 532 pass · 0 xfail (known gap) · 1 fail**

**Tables:** 1636/1636 pass · **Columns:** 16147/16147 pass

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
| `striped_full_2.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
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
| `xtp_probe_full.bak` | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
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
| `catalog_ss2019.bak` | 3 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **3/3** | ✓ |
| `cci_binary_varbinary_compare_full.bak` | 1,200 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | digest | ✓ |
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
| `dirtycoverage_cci_delete.bak` | 13,000 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | digest | ✓ |
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
| `incrementalcoverage_diff_01.bak` | 15 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **45/45** | ✓ |
| `incrementalcoverage_diff_02.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
| `incrementalcoverage_diff_03.bak` | 25 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **75/75** | ✓ |
| `incrementalcoverage_diff_04.bak` | 30 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **90/90** | ✓ |
| `incrementalcoverage_diff_05.bak` | 35 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **105/105** | ✓ |
| `incrementalcoverage_diff_06.bak` | 40 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **120/120** | ✓ |
| `incrementalcoverage_full.bak` | 10 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **30/30** | ✓ |
| `layoutcoverage_full.bak` | 171 | 2,421 | **57/57** | **2421/2421** | **4834/4834** | **57/57** | **7092/7092** | ✓ |
| `max_row_width_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `mixed_collation_full.bak` | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | **12/12** | ✓ |
| `multi_rowgroup_full.bak` | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_heap_full.bak` | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_types_full.bak` | 24,057 | 39 | **20/20** | **39/39** | **76/76** | **20/20** | **22857/22857** | ✓ |
| `ndfcoverage_full.bak` | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **20/20** | ✓ |
| `nvarchar_max_u21_full.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
| `pagecomp_anchor_full.bak` | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | **35000/35000** | ✓ |
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
| `striped_full_2.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
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
| `utf8_collation_full.bak` | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **14/14** | ✓ |
| `xml_index_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `xmlcoverage_full.bak` | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **24/24** | ✓ |
| `xmlheap_full.bak` | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | **1200/1200** | ✓ |
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
| `striped_full_2.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
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
| `xtp_probe_full.bak` | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |
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
| `dirtycoverage_concurrent.bak` | 114 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **342/342** | ✓ |
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
| `featurecoverage_full.bak` | 2,148 | 44 | **11/11** | **32/32** | **64/64** | **11/11** | **3298/3298** | ✓ |
| `filtered_ncci_full.bak` | 1,200 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | **800/800** | ✓ |
| `float_extreme_full.bak` | 5 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **10/10** | ✓ |
| `forwarded_records_full.bak` | 2,000 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **1000/1000** | ✓ |
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
| `layoutcoverage_full.bak` | 171 | 2,421 | **57/57** | **2421/2421** | **4834/4834** | **57/57** | **7092/7092** | ✓ |
| `max_row_width_full.bak` | 5 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **5/5** | ✓ |
| `mixed_collation_full.bak` | 3 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | **12/12** | ✓ |
| `multi_rowgroup_full.bak` | 3,300 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `native_json_full.bak` | 20 | 4 | **2/2** | **4/4** | **2/2** | **2/2** | **20/20** | ✓ |
| `ncci_heap_full.bak` | 800 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | digest | ✓ |
| `ncci_types_full.bak` | 24,057 | 39 | **20/20** | **39/39** | **68/68** | **20/20** | **22857/22857** | ✓ |
| `ndfcoverage_full.bak` | 20 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **20/20** | ✓ |
| `nvarchar_max_u21_full.bak` | 10 | 2 | **1/1** | **2/2** | **4/4** | **1/1** | **10/10** | ✓ |
| `ordered_cci_full.bak` | 3,600 | 7 | **3/3** | **7/7** | **14/14** | **3/3** | digest | ✓ |
| `pagecomp_anchor_full.bak` | 5,000 | 8 | **1/1** | **8/8** | **16/16** | **1/1** | **35000/35000** | ✓ |
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
| `striped_full_2.bak` | 20 | 4 | **1/1** | **4/4** | **8/8** | **1/1** | **60/60** | ✓ |
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
| `utf8_collation_full.bak` | 14 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **14/14** | ✓ |
| `vector_full.bak` | 20 | 4 | **2/2** | **4/4** | **2/2** | **2/2** | **20/20** | ✓ |
| `xml_index_full.bak` | 200 | 4 | **2/2** | **4/4** | **8/8** | **2/2** | **200/200** | ✓ |
| `xmlcoverage_full.bak` | 12 | 3 | **1/1** | **3/3** | **6/6** | **1/1** | **24/24** | ✓ |
| `xmlheap_full.bak` | 200 | 7 | **1/1** | **7/7** | **14/14** | **1/1** | **1200/1200** | ✓ |
| `xtp_probe_full.bak` | 7 | 8 | **5/5** | **8/8** | **14/14** | **5/5** | — | ✓ |
| `xtp_rich_full.bak` | 6 | 8 | **2/2** | **8/8** | **14/14** | **2/2** | — | ✓ |
| `xtp_simple_full.bak` | 6 | 5 | **2/2** | **5/5** | **10/10** | **2/2** | — | ✓ |

## Per-fixture detail

### `alias_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | 3 | ✓ | **6/6** | — | ✓ | cells **15/15** ✓ |

### `archive_columnstore_partition_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 12.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.113 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.113 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_date` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_18_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

### `cci_binary_varbinary_compare_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.734 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.234 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 23.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 8.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.422 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.484 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.543 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells **1400/1400** ✓ |

### `delta_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.047 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.359 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_concurrent.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 113 | ✓ | **4/4** | **8/8** | ✓ | cells **339/339** ✓ |

### `dirtycoverage_createidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_large_dirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.734 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_nchar_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `filtered_ncci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.297 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 14.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ghost_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.922 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 11.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 7.734 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | 3 | ✓ | — | — | ✓ | cells **3066/3066** ✓ |
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

### `max_row_width_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `multi_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.113 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `pagecomp_anchor_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pfor_columnstore_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.609 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.geometry_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |

### `spatial_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.797 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | 6 | ✓ | **2/2** | **2/2** | ✓ | cells **6/6** ✓ |

### `striped_full_1.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.18 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_full_2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.262 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 0.41 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 9.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.859 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **5/5** ✓ |
| `dbo.temporal_hidden_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.547 MB_

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

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `unicode_codepage_coverage.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 4.234 MB_

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

### `xml_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.984 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 2.547 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | 12 | ✓ | **3/3** | **6/6** | ✓ | cells **24/24** ✓ |

### `xmlheap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 6.672 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `xtp_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.242 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2017 (RTM-CU31-GDR) (KB5090354) - 14.0.3530.2 (X64) · 5.18 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

### `alias_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | 3 | ✓ | **6/6** | — | ✓ | cells **15/15** ✓ |

### `archive_columnstore_partition_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 13.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.117 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.117 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_date` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_18_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

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

### `catalog_ss2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `cci_binary_varbinary_compare_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 24.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 9.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.551 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.613 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.574 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells **1400/1400** ✓ |

### `delta_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_concurrent.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 113 | ✓ | **4/4** | **8/8** | ✓ | cells **339/339** ✓ |

### `dirtycoverage_createidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_large_dirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_nchar_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `filtered_ncci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 15.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ghost_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 12.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.055 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 8.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ | cells **3066/3066** ✓ |
| `dbo.layout_cols_1024` | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ | cells **3069/3069** ✓ |
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

### `max_row_width_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `multi_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.117 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `pagecomp_anchor_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pfor_columnstore_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 7.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 5.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.geometry_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |

### `spatial_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | 6 | ✓ | **2/2** | **2/2** | ✓ | cells **6/6** ✓ |

### `striped_full_1.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.266 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_full_2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.191 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 0.434 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 10.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **5/5** ✓ |
| `dbo.temporal_hidden_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.676 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `unicode_codepage_coverage.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 4.363 MB_

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

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |
| `dbo.utf8_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `xml_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | 12 | ✓ | **3/3** | **6/6** | ✓ | cells **24/24** ✓ |

### `xmlheap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2019 (RTM-CU32-GDR) (KB5090407) - 15.0.4470.1 (X64) · 6.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `alias_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | 3 | ✓ | **9/9** | — | ✓ | cells **24/24** ✓ |

### `archive_columnstore_partition_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.117 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.117 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_date` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_18_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cat_probe` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `cci_binary_varbinary_compare_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_bigint_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 43.148 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_bigint` | 2,200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 2,200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe` | 200,000 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_bitpack_probe_highbase_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 9.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_bitpack_probe_highbase` | 200,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 200,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 25.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 10.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB_

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

### `corrupt_metadata_confidence_full.bak` — confidence fail

_SQL Server  · 0.002 MB_

_confidence fail (catalog_consistency: schema recovery failed: 'corrupt_metadata_confidence_full.bak' is too small to contain an MDF page image.)._

### `covering_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.195 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells **5000/5000** ✓ |

### `cs_lob_preamble2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.605 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells **1200/1200** ✓ |

### `delta_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 6,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 56.434 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.padding_fill` | 250,000 | ✓ | **2/2** | **4/4** | ✓ | cells **250000/250000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 115.879 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 300,000 | ✓ | **3/3** | **6/6** | ✓ | cells **600000/600000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_compress_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_concurrent.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 114 | ✓ | **4/4** | **8/8** | ✓ | cells **342/342** ✓ |

### `dirtycoverage_createidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_insert_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.iu_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_large_dirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_multi_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.multi_update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_nchar_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_wide.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide2_test` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `featurecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_col` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `dbo.graph_follows` | 2 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.graph_person` | 3 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.ledger_account` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **6/6** ✓ |
| `dbo.long_text` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `dbo.memory_oltp` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_table` | 1,024 | ✓ | **4/4** | **8/8** | ✓ | cells **3072/3072** ✓ |
| `dbo.temporal_current` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |
| `dbo.temporal_history` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.utf8_collation` | 6 | ✓ | **4/4** | **8/8** | ✓ | cells **18/18** ✓ |

### `filtered_ncci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 16.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `geocoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Locations` | 5 | ✓ | **5/5** | **10/10** | ✓ | cells **20/20** ✓ |
| `dbo.LocationsNone` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.LocationsRow` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.spatial_lob_test` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |

### `ghost_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.93 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.051 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.legacy_lob` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `max_row_width_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `multi_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `ncci_heap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.117 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 5.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `ordered_cci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ordered_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.regular_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `pagecomp_anchor_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pfor_columnstore_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.geometry_edge` | 9 | ✓ | **2/2** | **4/4** | ✓ | cells **9/9** ✓ |

### `spatial_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | 10 | ✓ | **2/2** | **2/2** | ✓ | cells **10/10** ✓ |

### `striped_full_1.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.266 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_full_2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.242 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.484 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 11.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_hidden_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.551 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 1.535 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 2.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `unicode_codepage_coverage.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 4.551 MB_

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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |
| `dbo.utf8_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `xml_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | 13 | ✓ | **3/3** | **6/6** | ✓ | cells **26/26** ✓ |

### `xmlheap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `xtp_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 6.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |

### `alias_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alias_probe` | 3 | ✓ | **6/6** | — | ✓ | cells **15/15** ✓ |

### `archive_columnstore_partition_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 14.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_part_all` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_mixed` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_roundtrip` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.archive_part_single` | 140,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `archive_columnstore_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 8.117 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 9.117 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archive_single_chunk_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_single_chunk` | 5,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `archivenull_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.archive_null` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `backup_blocksize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.blksz_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `boundarycoverage_datetime_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tb_bit` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_date` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetime2_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_datetimeoffset_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_18_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_decimal_9_4` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_smalldatetime` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |
| `dbo.tb_time_3` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells **2400/2400** ✓ |

### `boundarycoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.113 MB_

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

### `cci_binary_varbinary_compare_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary_varbinary_compare` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `cci_btree_nci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_with_btree` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_computed_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_computed` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 11.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_char_pool` | 80,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_enc5_largepool_matrix_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 25.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.char_32767_distinct_var` | 32,767 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_32768_distinct_var` | 32,768 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_65536_distinct_var` | 65,536 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_fullwidth` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.char_80000_lowcard_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 80,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.varchar_80000_distinct_var` | 80,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_extended_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary4` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char10_varied` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_int` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_nvarchar50_sparse` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar50` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_lob_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_nvarchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varchar_max` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,196 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_reorganize_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_deleted_no_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_deleted_reorg` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_dict_regression_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 10.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_string_dict_regression` | 16,384 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 8,192 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_string_minmax_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_str_minmax` | 1,200 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_switch_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_switch_dst` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.cci_switch_src` | 0 | — | — | — | — |  |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cci_types_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_binary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_bit` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_char` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_uuid` | 1,200 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_micro_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_micro` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_1byte` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_micro_nullonly` | 21 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `cci_varbinary_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cci_varbinary_maxwidth` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_narrowmax` | 1,200 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cci_varbinary_small_rowgroup` | 128 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `columnstore_minimal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_1` | 1 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10` | 10 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_100` | 100 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_1000` | 1,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.cs_10000` | 10,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `compressed_nvarchar_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compressed_nvar` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |

### `compressioncoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.113 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.comp_nonpersisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |
| `dbo.comp_persisted` | 3 | ✓ | **4/4** | **8/8** | ✓ | cells **9/9** ✓ |

### `constraintcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.covering_base` | 1,000 | ✓ | **4/4** | **8/8** | ✓ | cells **3000/3000** ✓ |
| `dbo.fkr__seed` | 1,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `cs_lob_preamble.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 0.566 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_lob_preamble` | 1,400 | ✓ | **2/2** | **4/4** | ✓ | cells **1400/1400** ✓ |

### `delta_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.051 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_delta_only` | 30 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.cs_mixed` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `dirtycoverage_aborted_xact.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.aborted_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_addcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addcol_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_addnotnull.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.addnotnull_test` | 60 | ✓ | **4/4** | **8/8** | ✓ | cells **180/180** ✓ |

### `dirtycoverage_alldirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alldirty_test` | 0 | — | — | — | — |  |

### `dirtycoverage_altercol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.altercol_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_altercol_rewrite.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rewrite_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_alterdb.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.alterdb_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_cci_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.801 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_cci_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 5.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_cci` | 7,000 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 7,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_delete_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_delete_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_delete_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 200 | ✓ | **27/27** | **50/50** | ✓ | cells **5200/5200** ✓ |

### `dirtycoverage_committed_delete_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 4,000 | ✓ | **8/8** | **14/14** | ✓ | cells **28000/28000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_committed_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `dirtycoverage_committed_update_v2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.committed_update_test` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |

### `dirtycoverage_committed_update_v3.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.all_types_test` | 300 | ✓ | **27/27** | **50/50** | ✓ | cells **7800/7800** ✓ |

### `dirtycoverage_committed_update_v4.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_v4` | 5,000 | ✓ | **8/8** | **14/14** | ✓ | cells **35000/35000** ✓ |
| `dbo.fkr__seed` | 5,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `dirtycoverage_concurrent.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 114 | ✓ | **4/4** | **8/8** | ✓ | cells **342/342** ✓ |

### `dirtycoverage_createidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_createtable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.stable_test` | 300 | ✓ | **2/2** | **4/4** | ✓ | cells **300/300** ✓ |

### `dirtycoverage_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.delete_test` | 70 | ✓ | **3/3** | **6/6** | ✓ | cells **140/140** ✓ |

### `dirtycoverage_dropcol.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dropcol_test` | 60 | ✓ | **3/3** | **6/6** | ✓ | cells **120/120** ✓ |

### `dirtycoverage_dropidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.kidx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_droptable.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.drop_target` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |
| `dbo.survivor_test` | 200 | ✓ | **2/2** | **4/4** | ✓ | cells **200/200** ✓ |

### `dirtycoverage_heap_forward.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_forward_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `dirtycoverage_large_dirty.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.large_dirty_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_lob_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_update_test` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `dirtycoverage_maxrow.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.maxrow_test` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `dirtycoverage_nchar_delete.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nchar_delete_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_nested.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nested_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_null_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.null_update_test` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |

### `dirtycoverage_rebuildidx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ridx_test` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `dirtycoverage_rich_insert.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.551 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_rich_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rich_update_test` | 20 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |

### `dirtycoverage_savepoint.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.savepoint_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_snapshot_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.488 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.snapshot_update_test` | 20 | ✓ | **2/2** | **4/4** | ✓ | cells **20/20** ✓ |

### `dirtycoverage_switch.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.part_test` | 150 | ✓ | **3/3** | **6/6** | ✓ | cells **300/300** ✓ |
| `dbo.staging_test` | 50 | ✓ | **3/3** | **6/6** | ✓ | cells **100/100** ✓ |

### `dirtycoverage_temporal_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.551 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_test` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |
| `dbo.temporal_test_history` | 0 | — | — | — | — |  |

### `dirtycoverage_truncate.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.trunc_test` | 500 | ✓ | **3/3** | **6/6** | ✓ | cells **1000/1000** ✓ |

### `dirtycoverage_two_tx.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.551 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.two_tx_test` | 30 | ✓ | **3/3** | **6/6** | ✓ | cells **60/60** ✓ |

### `dirtycoverage_uncommitted.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.dirty_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `dirtycoverage_update.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.update_test` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |

### `featurecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 9.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.compress_col` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `dbo.fkr__seed` | 1,024 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.graph_follows` | 2 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.graph_person` | 3 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.ledger_account` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **6/6** ✓ |
| `dbo.long_text` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `dbo.memory_oltp` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.ncci_table` | 1,024 | ✓ | **4/4** | **8/8** | ✓ | cells **3072/3072** ✓ |
| `dbo.temporal_current` | 50 | ✓ | **4/4** | **8/8** | ✓ | cells **150/150** ✓ |
| `dbo.temporal_history` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.utf8_collation` | 6 | ✓ | **4/4** | **8/8** | ✓ | cells **18/18** ✓ |

### `filtered_ncci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.filtered_ncci_base` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells **800/800** ✓ |
| `dbo.filtered_ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `float_extreme_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.float_extreme` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |

### `forwarded_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 16.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fwd_control` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells **1000/1000** ✓ |
| `dbo.fwd_heap` | 1,000 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `ghost_records_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.ghost_heap` | 800 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `heapcoverage_large.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells **2000/2000** ✓ |
| `dbo.heap_plain` | 1,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `heapcoverage_large_50000.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 13.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.heap_clustered` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells **100000/100000** ✓ |
| `dbo.heap_plain` | 50,000 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `hierarchyid_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.org` | 6 | ✓ | **2/2** | **4/4** | ✓ | cells **6/6** ✓ |

### `high_slot_density_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.555 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.tiny_row` | 100,000 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `incrementalcoverage_diff_01.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 15 | ✓ | **4/4** | **8/8** | ✓ | cells **45/45** ✓ |

### `incrementalcoverage_diff_02.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `incrementalcoverage_diff_03.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **75/75** ✓ |

### `incrementalcoverage_diff_04.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 30 | ✓ | **4/4** | **8/8** | ✓ | cells **90/90** ✓ |

### `incrementalcoverage_diff_05.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 35 | ✓ | **4/4** | **8/8** | ✓ | cells **105/105** ✓ |

### `incrementalcoverage_diff_06.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.863 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 40 | ✓ | **4/4** | **8/8** | ✓ | cells **120/120** ✓ |

### `incrementalcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sync_batch` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |

### `layoutcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 10.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.layout_cols_1` | 3 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.layout_cols_1023` | 3 | ✓ | **1023/1023** | **2046/2046** | ✓ | cells **3066/3066** ✓ |
| `dbo.layout_cols_1024` | 3 | ✓ | **1024/1024** | **2048/2048** | ✓ | cells **3069/3069** ✓ |
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

### `max_row_width_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.wide_row` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `mixed_collation_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.collation_mix` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `multi_rowgroup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.cs_multi` | 2,100 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |

### `native_json_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 10 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.json_docs` | 10 | ✓ | **3/3** | — | ✓ | cells **20/20** ✓ |

### `ncci_heap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 400 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_heap` | 400 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `ncci_types_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 11.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ncci_bigint` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_binary` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_bit` | 1,203 | ✓ | **2/2** | — | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_char` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_date` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetime2` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_datetimeoffset` | 1,203 | ✓ | **2/2** | **4/4** | ✓ | cells **1203/1203** ✓ |
| `dbo.ncci_float` | 1,203 | ✓ | **2/2** | — | ✓ | cells **1203/1203** ✓ |
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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 5.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.primary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |
| `dbo.secondary_tbl` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `nvarchar_max_u21_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvarchar_max_u21probe` | 10 | ✓ | **2/2** | **4/4** | ✓ | cells **10/10** ✓ |

### `ordered_cci_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.ordered_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.regular_cci` | 1,200 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `pagecomp_anchor_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pagecomp_anchor` | 5,000 | ✓ | **8/8** | **16/16** | ✓ | cells **35000/35000** ✓ |

### `pfor_columnstore_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 8.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `pfor_columnstore_random_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 9.121 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.pfor_archive` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.pfor_plain` | 200,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `realworld_numeric_digest_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 1,200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.numeric_cci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.numeric_ncci` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |
| `dbo.numeric_rowstore` | 1,200 | ✓ | **7/7** | **14/14** | ✓ | cells **7200/7200** ✓ |

### `rowboundary_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.613 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rb_lob` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.rb_overflow` | 9 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.rb_page_fill` | 216 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `rowstore_hash_pii_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.hash_pii_probe` | 4 | ✓ | **4/4** | **8/8** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_image_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.301 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_image_probe` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |

### `rowstore_lob_markup_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.lob_markup_probe` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |

### `rowversion_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.rv_tbl` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `sparse_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sparse_wide` | 10,000 | ✓ | **6/6** | **10/10** | ✓ | cells **50000/50000** ✓ |

### `spatial_edge_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.926 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.geography_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.geometry_edge` | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |

### `spatial_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.988 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 200 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.spatial_pts` | 200 | ✓ | **3/3** | **6/6** | ✓ | cells **400/400** ✓ |

### `sql_variant_extract_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sv` | 6 | ✓ | **2/2** | **2/2** | ✓ | cells **6/6** ✓ |

### `striped_full_1.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 0.238 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_full_2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 0.293 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `striped_single.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 0.508 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe` | 20 | ✓ | **4/4** | **8/8** | ✓ | cells **60/60** ✓ |

### `surrogate_pairs_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.176 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.sc_tbl` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |

### `tabletype_cci_large_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 6.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_column` | 1,200 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |

### `tabletypecoverage_diff.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 6 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 6 | ✓ | **34/34** | **56/56** | ✓ | cells **198/198** ✓ |

### `tabletypecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 11.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tt_cluster` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_column` | 4 | ✓ | **25/25** | **48/48** | ✓ | cells digest ✓ |
| `dbo.tt_heap` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_partition` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells digest ✓ |
| `dbo.tt_plain` | 4 | ✓ | **34/34** | **56/56** | ✓ | cells **132/132** ✓ |

### `temporal_hidden_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.551 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.temporal_hidden` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **5/5** ✓ |
| `dbo.temporal_hidden_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.temporal_visible` | 5 | ✓ | **4/4** | **8/8** | ✓ | cells **15/15** ✓ |
| `dbo.temporal_visible_history` | 2 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `torn_page_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.tpd_probe` | 300 | ✓ | **3/3** | **6/6** | ✓ | cells **600/600** ✓ |

### `typecoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.113 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.typed_xml_docs` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |

### `unicode_codepage_coverage.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 4.863 MB_

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

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.738 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nvar_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |
| `dbo.utf8_tbl` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `vector_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 10 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.vec_tbl` | 10 | ✓ | **3/3** | — | ✓ | cells **20/20** ✓ |

### `xml_index_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.676 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.fkr__seed` | 100 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `dbo.xml_docs` | 100 | ✓ | **3/3** | **6/6** | ✓ | cells **200/200** ✓ |

### `xmlcoverage_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 3.363 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xmlcov` | 12 | ✓ | **3/3** | **6/6** | ✓ | cells **24/24** ✓ |

### `xmlheap_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xml_heap` | 200 | ✓ | **7/7** | **14/14** | ✓ | cells **1200/1200** ✓ |

### `xtp_probe_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.309 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.probe_1i1r` | 1 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_1i3r` | 3 | ✓ | **1/1** | **2/2** | ✓ |  |
| `dbo.probe_2i1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.probe_nv1r_null` | 1 | ✓ | **2/2** | **2/2** | ✓ |  |

### `xtp_rich_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_rich_fixed` | 3 | ✓ | **5/5** | **8/8** | ✓ |  |
| `dbo.xtp_rich_mixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |

### `xtp_simple_full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 7.246 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.xtp_fixed` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.xtp_var` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `alias_types_full.bak` | 0.291s |
| `archive_columnstore_partition_full.bak` | 2.467s |
| `archive_columnstore_types_full.bak` | 1.48s |
| `archive_columnstore_types_random_full.bak` | 1.485s |
| `archive_single_chunk_full.bak` | 0.06s |
| `archive_single_chunk_random_full.bak` | 0.054s |
| `archivenull_full.bak` | 0.398s |
| `backup_blocksize_full.bak` | 0.041s |
| `boundarycoverage_datetime_full.bak` | 0.376s |
| `boundarycoverage_full.bak` | 0.179s |
| `cci_binary_varbinary_compare_full.bak` | 0.047s |
| `cci_btree_nci_full.bak` | 0.057s |
| `cci_computed_full.bak` | 0.073s |
| `cci_enc5_largepool_full.bak` | 1.08s |
| `cci_enc5_largepool_matrix_full.bak` | 8.949s |
| `cci_extended_full.bak` | 0.085s |
| `cci_lob_full.bak` | 0.087s |
| `cci_reorganize_full.bak` | 0.075s |
| `cci_string_dict_regression_full.bak` | 0.446s |
| `cci_string_minmax_full.bak` | 0.058s |
| `cci_switch_full.bak` | 0.066s |
| `cci_types_large_full.bak` | 0.072s |
| `cci_varbinary_micro_full.bak` | 0.063s |
| `cci_varbinary_probe_full.bak` | 0.105s |
| `columnstore_minimal.bak` | 0.984s |
| `compressed_nvarchar_full.bak` | 0.031s |
| `compressioncoverage_full.bak` | 0.284s |
| `computedcoverage_full.bak` | 0.031s |
| `constraintcoverage_full.bak` | 0.039s |
| `covering_index_full.bak` | 0.073s |
| `cs_lob_preamble.bak` | 0.074s |
| `delta_rowgroup_full.bak` | 0.048s |
| `dirtycoverage_aborted_xact.bak` | 0.048s |
| `dirtycoverage_addcol.bak` | 0.047s |
| `dirtycoverage_addnotnull.bak` | 0.047s |
| `dirtycoverage_alldirty.bak` | 0.051s |
| `dirtycoverage_altercol.bak` | 0.039s |
| `dirtycoverage_altercol_rewrite.bak` | 0.051s |
| `dirtycoverage_alterdb.bak` | 0.048s |
| `dirtycoverage_cci_delete.bak` | 0.172s |
| `dirtycoverage_cci_update.bak` | 0.174s |
| `dirtycoverage_committed_delete.bak` | 0.033s |
| `dirtycoverage_committed_delete_v2.bak` | 0.044s |
| `dirtycoverage_committed_delete_v3.bak` | 0.089s |
| `dirtycoverage_committed_delete_v4.bak` | 0.29s |
| `dirtycoverage_committed_update.bak` | 0.034s |
| `dirtycoverage_committed_update_v2.bak` | 0.047s |
| `dirtycoverage_committed_update_v3.bak` | 0.117s |
| `dirtycoverage_committed_update_v4.bak` | 0.334s |
| `dirtycoverage_concurrent.bak` | 0.05s |
| `dirtycoverage_createidx.bak` | 0.05s |
| `dirtycoverage_createtable.bak` | 0.049s |
| `dirtycoverage_delete.bak` | 0.05s |
| `dirtycoverage_dropcol.bak` | 0.047s |
| `dirtycoverage_dropidx.bak` | 0.05s |
| `dirtycoverage_droptable.bak` | 0.057s |
| `dirtycoverage_heap_forward.bak` | 0.048s |
| `dirtycoverage_large_dirty.bak` | 0.319s |
| `dirtycoverage_lob_update.bak` | 0.066s |
| `dirtycoverage_maxrow.bak` | 0.031s |
| `dirtycoverage_nchar_delete.bak` | 0.049s |
| `dirtycoverage_nested.bak` | 0.049s |
| `dirtycoverage_null_update.bak` | 0.048s |
| `dirtycoverage_rebuildidx.bak` | 0.05s |
| `dirtycoverage_rich_insert.bak` | 0.05s |
| `dirtycoverage_rich_update.bak` | 0.05s |
| `dirtycoverage_savepoint.bak` | 0.051s |
| `dirtycoverage_snapshot_update.bak` | 0.046s |
| `dirtycoverage_switch.bak` | 0.056s |
| `dirtycoverage_temporal_update.bak` | 0.053s |
| `dirtycoverage_truncate.bak` | 0.058s |
| `dirtycoverage_two_tx.bak` | 0.053s |
| `dirtycoverage_uncommitted.bak` | 0.052s |
| `dirtycoverage_update.bak` | 0.051s |
| `filtered_ncci_full.bak` | 0.06s |
| `float_extreme_full.bak` | 0.031s |
| `forwarded_records_full.bak` | 0.118s |
| `ghost_records_full.bak` | 0.041s |
| `heapcoverage_large.bak` | 0.056s |
| `heapcoverage_large_50000.bak` | 0.878s |
| `hierarchyid_extract_full.bak` | 0.03s |
| `high_slot_density_full.bak` | 0.503s |
| `incrementalcoverage_diff_01.bak` | 0.033s |
| `incrementalcoverage_diff_02.bak` | 0.032s |
| `incrementalcoverage_diff_03.bak` | 0.032s |
| `incrementalcoverage_diff_04.bak` | 0.031s |
| `incrementalcoverage_diff_05.bak` | 0.034s |
| `incrementalcoverage_diff_06.bak` | 0.033s |
| `incrementalcoverage_full.bak` | 0.026s |
| `layoutcoverage_full.bak` | 0.253s |
| `max_row_width_full.bak` | 0.045s |
| `mixed_collation_full.bak` | 0.031s |
| `multi_rowgroup_full.bak` | 0.048s |
| `ncci_heap_full.bak` | 0.053s |
| `ncci_types_full.bak` | 0.437s |
| `ndfcoverage_full.bak` | 0.033s |
| `nvarchar_max_u21_full.bak` | 0.035s |
| `pagecomp_anchor_full.bak` | 0.321s |
| `pfor_columnstore_full.bak` | 2.124s |
| `pfor_columnstore_random_full.bak` | 2.122s |
| `realworld_numeric_digest_full.bak` | 0.169s |
| `rowboundary_full.bak` | 0.036s |
| `rowstore_hash_pii_full.bak` | 0.029s |
| `rowstore_lob_image_full.bak` | 0.032s |
| `rowstore_lob_markup_full.bak` | 0.031s |
| `rowversion_extract_full.bak` | 0.041s |
| `sparse_full.bak` | 0.249s |
| `spatial_edge_full.bak` | 0.037s |
| `spatial_index_full.bak` | 0.051s |
| `sql_variant_extract_full.bak` | 0.031s |
| `striped_full_1.bak` | 0.041s |
| `striped_full_2.bak` | 0.044s |
| `striped_single.bak` | 0.038s |
| `surrogate_pairs_full.bak` | 0.03s |
| `tabletype_cci_large_full.bak` | 0.059s |
| `tabletypecoverage_diff.bak` | 0.151s |
| `tabletypecoverage_full.bak` | 0.122s |
| `temporal_hidden_full.bak` | 0.033s |
| `torn_page_full.bak` | 0.033s |
| `typecoverage_full.bak` | 0.083s |
| `typed_xml_full.bak` | 0.03s |
| `unicode_codepage_coverage.bak` | 0.098s |
| `xml_index_full.bak` | 0.053s |
| `xmlcoverage_full.bak` | 0.031s |
| `xmlheap_full.bak` | 0.074s |
| `xtp_probe_full.bak` | 0.082s |
| `xtp_rich_full.bak` | 0.06s |
| `xtp_simple_full.bak` | 0.066s |
| `alias_types_full.bak` | 0.032s |
| `archive_columnstore_partition_full.bak` | 2.277s |
| `archive_columnstore_types_full.bak` | 1.248s |
| `archive_columnstore_types_random_full.bak` | 1.269s |
| `archive_single_chunk_full.bak` | 0.051s |
| `archive_single_chunk_random_full.bak` | 0.047s |
| `archivenull_full.bak` | 0.247s |
| `backup_blocksize_full.bak` | 0.042s |
| `boundarycoverage_datetime_full.bak` | 0.347s |
| `boundarycoverage_full.bak` | 0.162s |
| `catalog_ss2019.bak` | 0.033s |
| `cci_binary_varbinary_compare_full.bak` | 0.041s |
| `cci_btree_nci_full.bak` | 0.054s |
| `cci_computed_full.bak` | 0.048s |
| `cci_enc5_largepool_full.bak` | 1.075s |
| `cci_enc5_largepool_matrix_full.bak` | 8.941s |
| `cci_extended_full.bak` | 0.085s |
| `cci_lob_full.bak` | 0.057s |
| `cci_reorganize_full.bak` | 0.052s |
| `cci_string_dict_regression_full.bak` | 0.448s |
| `cci_string_minmax_full.bak` | 0.06s |
| `cci_switch_full.bak` | 0.051s |
| `cci_types_large_full.bak` | 0.074s |
| `cci_varbinary_micro_full.bak` | 0.057s |
| `cci_varbinary_probe_full.bak` | 0.062s |
| `columnstore_minimal.bak` | 0.981s |
| `compressed_nvarchar_full.bak` | 0.034s |
| `compressioncoverage_full.bak` | 0.272s |
| `computedcoverage_full.bak` | 0.033s |
| `constraintcoverage_full.bak` | 0.038s |
| `covering_index_full.bak` | 0.056s |
| `cs_lob_preamble.bak` | 0.074s |
| `delta_rowgroup_full.bak` | 0.042s |
| `dirtycoverage_aborted_xact.bak` | 0.056s |
| `dirtycoverage_addcol.bak` | 0.036s |
| `dirtycoverage_addnotnull.bak` | 0.035s |
| `dirtycoverage_alldirty.bak` | 0.056s |
| `dirtycoverage_altercol.bak` | 0.032s |
| `dirtycoverage_altercol_rewrite.bak` | 0.034s |
| `dirtycoverage_alterdb.bak` | 0.037s |
| `dirtycoverage_cci_delete.bak` | 0.17s |
| `dirtycoverage_cci_update.bak` | 0.285s |
| `dirtycoverage_committed_delete.bak` | 0.035s |
| `dirtycoverage_committed_delete_v2.bak` | 0.046s |
| `dirtycoverage_committed_delete_v3.bak` | 0.099s |
| `dirtycoverage_committed_delete_v4.bak` | 0.293s |
| `dirtycoverage_committed_update.bak` | 0.034s |
| `dirtycoverage_committed_update_v2.bak` | 0.046s |
| `dirtycoverage_committed_update_v3.bak` | 0.117s |
| `dirtycoverage_committed_update_v4.bak` | 0.323s |
| `dirtycoverage_concurrent.bak` | 0.042s |
| `dirtycoverage_createidx.bak` | 0.042s |
| `dirtycoverage_createtable.bak` | 0.043s |
| `dirtycoverage_delete.bak` | 0.06s |
| `dirtycoverage_dropcol.bak` | 0.037s |
| `dirtycoverage_dropidx.bak` | 0.039s |
| `dirtycoverage_droptable.bak` | 0.044s |
| `dirtycoverage_heap_forward.bak` | 0.056s |
| `dirtycoverage_large_dirty.bak` | 0.329s |
| `dirtycoverage_lob_update.bak` | 0.078s |
| `dirtycoverage_maxrow.bak` | 0.032s |
| `dirtycoverage_nchar_delete.bak` | 0.061s |
| `dirtycoverage_nested.bak` | 0.062s |
| `dirtycoverage_null_update.bak` | 0.055s |
| `dirtycoverage_rebuildidx.bak` | 0.039s |
| `dirtycoverage_rich_insert.bak` | 0.058s |
| `dirtycoverage_rich_update.bak` | 0.057s |
| `dirtycoverage_savepoint.bak` | 0.059s |
| `dirtycoverage_snapshot_update.bak` | 0.054s |
| `dirtycoverage_switch.bak` | 0.043s |
| `dirtycoverage_temporal_update.bak` | 0.06s |
| `dirtycoverage_truncate.bak` | 0.042s |
| `dirtycoverage_two_tx.bak` | 0.059s |
| `dirtycoverage_uncommitted.bak` | 0.058s |
| `dirtycoverage_update.bak` | 0.062s |
| `filtered_ncci_full.bak` | 0.044s |
| `float_extreme_full.bak` | 0.034s |
| `forwarded_records_full.bak` | 0.117s |
| `ghost_records_full.bak` | 0.039s |
| `heapcoverage_large.bak` | 0.053s |
| `heapcoverage_large_50000.bak` | 0.896s |
| `hierarchyid_extract_full.bak` | 0.039s |
| `high_slot_density_full.bak` | 0.512s |
| `incrementalcoverage_diff_01.bak` | 0.034s |
| `incrementalcoverage_diff_02.bak` | 0.046s |
| `incrementalcoverage_diff_03.bak` | 0.035s |
| `incrementalcoverage_diff_04.bak` | 0.034s |
| `incrementalcoverage_diff_05.bak` | 0.038s |
| `incrementalcoverage_diff_06.bak` | 0.056s |
| `incrementalcoverage_full.bak` | 0.037s |
| `layoutcoverage_full.bak` | 0.271s |
| `max_row_width_full.bak` | 0.04s |
| `mixed_collation_full.bak` | 0.037s |
| `multi_rowgroup_full.bak` | 0.058s |
| `ncci_heap_full.bak` | 0.041s |
| `ncci_types_full.bak` | 0.415s |
| `ndfcoverage_full.bak` | 0.041s |
| `nvarchar_max_u21_full.bak` | 0.04s |
| `pagecomp_anchor_full.bak` | 0.319s |
| `pfor_columnstore_full.bak` | 2.119s |
| `pfor_columnstore_random_full.bak` | 2.129s |
| `realworld_numeric_digest_full.bak` | 0.153s |
| `rowboundary_full.bak` | 0.041s |
| `rowstore_hash_pii_full.bak` | 0.031s |
| `rowstore_lob_image_full.bak` | 0.035s |
| `rowstore_lob_markup_full.bak` | 0.035s |
| `rowversion_extract_full.bak` | 0.037s |
| `sparse_full.bak` | 0.251s |
| `spatial_edge_full.bak` | 0.038s |
| `spatial_index_full.bak` | 0.042s |
| `sql_variant_extract_full.bak` | 0.03s |
| `striped_full_1.bak` | 0.042s |
| `striped_full_2.bak` | 0.041s |
| `striped_single.bak` | 0.04s |
| `surrogate_pairs_full.bak` | 0.03s |
| `tabletype_cci_large_full.bak` | 0.063s |
| `tabletypecoverage_diff.bak` | 0.143s |
| `tabletypecoverage_full.bak` | 0.106s |
| `temporal_hidden_full.bak` | 0.034s |
| `torn_page_full.bak` | 0.039s |
| `typecoverage_full.bak` | 0.084s |
| `typed_xml_full.bak` | 0.038s |
| `unicode_codepage_coverage.bak` | 0.06s |
| `utf8_collation_full.bak` | 0.032s |
| `xml_index_full.bak` | 0.038s |
| `xmlcoverage_full.bak` | 0.032s |
| `xmlheap_full.bak` | 0.074s |
| `alias_types_full.bak` | 0.046s |
| `archive_columnstore_partition_full.bak` | 2.322s |
| `archive_columnstore_types_full.bak` | 1.305s |
| `archive_columnstore_types_random_full.bak` | 1.322s |
| `archive_single_chunk_full.bak` | 0.067s |
| `archive_single_chunk_random_full.bak` | 0.054s |
| `archivenull_full.bak` | 0.249s |
| `backup_blocksize_full.bak` | 0.044s |
| `boundarycoverage_datetime_full.bak` | 0.354s |
| `boundarycoverage_full.bak` | 0.175s |
| `catalog_ss2022.bak` | 0.034s |
| `cci_binary_varbinary_compare_full.bak` | 0.048s |
| `cci_bitpack_probe_bigint_full.bak` | 7.926s |
| `cci_bitpack_probe_full.bak` | 1.656s |
| `cci_bitpack_probe_highbase_full.bak` | 1.19s |
| `cci_btree_nci_full.bak` | 0.064s |
| `cci_computed_full.bak` | 0.062s |
| `cci_enc5_largepool_full.bak` | 1.077s |
| `cci_enc5_largepool_matrix_full.bak` | 8.893s |
| `cci_extended_full.bak` | 0.088s |
| `cci_lob_full.bak` | 0.069s |
| `cci_reorganize_full.bak` | 0.057s |
| `cci_string_dict_regression_full.bak` | 0.447s |
| `cci_string_minmax_full.bak` | 0.063s |
| `cci_switch_full.bak` | 0.059s |
| `cci_types_large_full.bak` | 0.093s |
| `cci_varbinary_micro_full.bak` | 0.055s |
| `cci_varbinary_probe_full.bak` | 0.064s |
| `columnstore_minimal.bak` | 0.99s |
| `compressed_nvarchar_full.bak` | 0.038s |
| `compressioncoverage_full.bak` | 0.279s |
| `computedcoverage_full.bak` | 0.04s |
| `constraintcoverage_full.bak` | 0.044s |
| `corrupt_metadata_confidence_full.bak` | 0.0s |
| `covering_index_full.bak` | 0.058s |
| `cs_lob_preamble.bak` | 0.157s |
| `cs_lob_preamble2.bak` | 0.084s |
| `delta_rowgroup_full.bak` | 0.045s |
| `dirtycoverage_aborted_xact.bak` | 0.063s |
| `dirtycoverage_addcol.bak` | 0.044s |
| `dirtycoverage_addnotnull.bak` | 0.04s |
| `dirtycoverage_alldirty.bak` | 0.06s |
| `dirtycoverage_altercol.bak` | 0.039s |
| `dirtycoverage_altercol_rewrite.bak` | 0.04s |
| `dirtycoverage_alterdb.bak` | 0.04s |
| `dirtycoverage_cci_delete.bak` | 0.176s |
| `dirtycoverage_cci_update.bak` | 0.288s |
| `dirtycoverage_committed_delete.bak` | 0.038s |
| `dirtycoverage_committed_delete_v2.bak` | 2.521s |
| `dirtycoverage_committed_delete_v3.bak` | 0.113s |
| `dirtycoverage_committed_delete_v4.bak` | 0.297s |
| `dirtycoverage_committed_update.bak` | 0.042s |
| `dirtycoverage_committed_update_v2.bak` | 12.131s |
| `dirtycoverage_committed_update_v3.bak` | 0.133s |
| `dirtycoverage_committed_update_v4.bak` | 0.286s |
| `dirtycoverage_compress_update.bak` | 0.078s |
| `dirtycoverage_concurrent.bak` | 0.041s |
| `dirtycoverage_createidx.bak` | 0.047s |
| `dirtycoverage_createtable.bak` | 0.042s |
| `dirtycoverage_delete.bak` | 0.073s |
| `dirtycoverage_dropcol.bak` | 0.049s |
| `dirtycoverage_dropidx.bak` | 0.051s |
| `dirtycoverage_droptable.bak` | 0.049s |
| `dirtycoverage_heap_forward.bak` | 0.062s |
| `dirtycoverage_insert_update.bak` | 0.078s |
| `dirtycoverage_large_dirty.bak` | 0.341s |
| `dirtycoverage_lob_update.bak` | 0.088s |
| `dirtycoverage_maxrow.bak` | 0.036s |
| `dirtycoverage_multi_update.bak` | 0.072s |
| `dirtycoverage_nchar_delete.bak` | 0.071s |
| `dirtycoverage_nested.bak` | 0.078s |
| `dirtycoverage_null_update.bak` | 0.065s |
| `dirtycoverage_rebuildidx.bak` | 0.043s |
| `dirtycoverage_rich_insert.bak` | 0.064s |
| `dirtycoverage_rich_update.bak` | 0.069s |
| `dirtycoverage_savepoint.bak` | 0.069s |
| `dirtycoverage_snapshot_update.bak` | 0.061s |
| `dirtycoverage_switch.bak` | 0.048s |
| `dirtycoverage_temporal_update.bak` | 0.065s |
| `dirtycoverage_truncate.bak` | 0.05s |
| `dirtycoverage_two_tx.bak` | 0.061s |
| `dirtycoverage_uncommitted.bak` | 0.069s |
| `dirtycoverage_update.bak` | 0.071s |
| `dirtycoverage_wide.bak` | 0.067s |
| `featurecoverage_full.bak` | 0.124s |
| `filtered_ncci_full.bak` | 0.048s |
| `float_extreme_full.bak` | 0.035s |
| `forwarded_records_full.bak` | 0.129s |
| `geocoverage_full.bak` | 0.063s |
| `geotest.bak` | 0.041s |
| `ghost_records_full.bak` | 0.039s |
| `heapcoverage_large.bak` | 0.054s |
| `heapcoverage_large_50000.bak` | 0.885s |
| `hierarchyid_extract_full.bak` | 0.035s |
| `high_slot_density_full.bak` | 0.509s |
| `incrementalcoverage_diff_01.bak` | 0.055s |
| `incrementalcoverage_diff_02.bak` | 0.056s |
| `incrementalcoverage_diff_03.bak` | 0.054s |
| `incrementalcoverage_diff_04.bak` | 0.043s |
| `incrementalcoverage_diff_05.bak` | 0.039s |
| `incrementalcoverage_diff_06.bak` | 0.038s |
| `incrementalcoverage_full.bak` | 0.031s |
| `layoutcoverage_full.bak` | 0.251s |
| `legacytext.bak` | 0.045s |
| `max_row_width_full.bak` | 0.035s |
| `mixed_collation_full.bak` | 0.037s |
| `multi_rowgroup_full.bak` | 0.054s |
| `ncci_heap_full.bak` | 0.039s |
| `ncci_types_full.bak` | 0.41s |
| `ndfcoverage_full.bak` | 0.04s |
| `nvarchar_max_u21_full.bak` | 0.034s |
| `ordered_cci_full.bak` | 0.055s |
| `pagecomp_anchor_full.bak` | 0.315s |
| `pfor_columnstore_full.bak` | 2.132s |
| `pfor_columnstore_random_full.bak` | 2.125s |
| `realworld_numeric_digest_full.bak` | 0.164s |
| `rowboundary_full.bak` | 0.041s |
| `rowstore_hash_pii_full.bak` | 0.038s |
| `rowstore_lob_image_full.bak` | 0.044s |
| `rowstore_lob_markup_full.bak` | 0.04s |
| `rowversion_extract_full.bak` | 0.041s |
| `sparse_full.bak` | 0.255s |
| `spatial_edge_full.bak` | 0.046s |
| `spatial_index_full.bak` | 0.047s |
| `sql_variant_extract_full.bak` | 0.038s |
| `striped_full_1.bak` | 0.047s |
| `striped_full_2.bak` | 0.045s |
| `striped_single.bak` | 0.045s |
| `surrogate_pairs_full.bak` | 0.035s |
| `tabletype_cci_large_full.bak` | 0.071s |
| `tabletypecoverage_diff.bak` | 0.138s |
| `tabletypecoverage_full.bak` | 0.113s |
| `temporal_hidden_full.bak` | 0.045s |
| `torn_page_full.bak` | 0.035s |
| `typecoverage_full.bak` | 0.086s |
| `typecoverage_full_compressed.bak` | 0.105s |
| `typed_xml_full.bak` | 0.038s |
| `unicode_codepage_coverage.bak` | 0.049s |
| `utf8_collation_full.bak` | 0.041s |
| `xml_index_full.bak` | 0.054s |
| `xmlcoverage_full.bak` | 0.039s |
| `xmlheap_full.bak` | 0.079s |
| `xtp_probe_full.bak` | 0.099s |
| `xtp_rich_full.bak` | 0.095s |
| `xtp_simple_full.bak` | 0.088s |
| `alias_types_full.bak` | 0.04s |
| `archive_columnstore_partition_full.bak` | 2.25s |
| `archive_columnstore_types_full.bak` | 1.227s |
| `archive_columnstore_types_random_full.bak` | 1.225s |
| `archive_single_chunk_full.bak` | 0.062s |
| `archive_single_chunk_random_full.bak` | 0.057s |
| `archivenull_full.bak` | 0.396s |
| `backup_blocksize_full.bak` | 0.044s |
| `boundarycoverage_datetime_full.bak` | 0.373s |
| `boundarycoverage_full.bak` | 0.186s |
| `cci_binary_varbinary_compare_full.bak` | 0.052s |
| `cci_btree_nci_full.bak` | 0.075s |
| `cci_computed_full.bak` | 0.062s |
| `cci_enc5_largepool_full.bak` | 1.105s |
| `cci_enc5_largepool_matrix_full.bak` | 8.905s |
| `cci_extended_full.bak` | 0.09s |
| `cci_lob_full.bak` | 0.079s |
| `cci_reorganize_full.bak` | 0.069s |
| `cci_string_dict_regression_full.bak` | 0.477s |
| `cci_string_minmax_full.bak` | 0.067s |
| `cci_switch_full.bak` | 0.06s |
| `cci_types_large_full.bak` | 0.092s |
| `cci_varbinary_micro_full.bak` | 0.056s |
| `cci_varbinary_probe_full.bak` | 0.086s |
| `columnstore_minimal.bak` | 0.996s |
| `compressed_nvarchar_full.bak` | 0.039s |
| `compressioncoverage_full.bak` | 0.288s |
| `computedcoverage_full.bak` | 0.045s |
| `constraintcoverage_full.bak` | 0.053s |
| `covering_index_full.bak` | 0.067s |
| `cs_lob_preamble.bak` | 0.082s |
| `delta_rowgroup_full.bak` | 0.049s |
| `dirtycoverage_aborted_xact.bak` | 0.07s |
| `dirtycoverage_addcol.bak` | 0.046s |
| `dirtycoverage_addnotnull.bak` | 0.044s |
| `dirtycoverage_alldirty.bak` | 0.072s |
| `dirtycoverage_altercol.bak` | 0.042s |
| `dirtycoverage_altercol_rewrite.bak` | 0.042s |
| `dirtycoverage_alterdb.bak` | 0.045s |
| `dirtycoverage_cci_delete.bak` | 0.16s |
| `dirtycoverage_cci_update.bak` | 0.194s |
| `dirtycoverage_committed_delete.bak` | 0.044s |
| `dirtycoverage_committed_delete_v2.bak` | 0.051s |
| `dirtycoverage_committed_delete_v3.bak` | 0.103s |
| `dirtycoverage_committed_delete_v4.bak` | 0.299s |
| `dirtycoverage_committed_update.bak` | 0.038s |
| `dirtycoverage_committed_update_v2.bak` | 0.059s |
| `dirtycoverage_committed_update_v3.bak` | 0.136s |
| `dirtycoverage_committed_update_v4.bak` | 0.228s |
| `dirtycoverage_concurrent.bak` | 0.044s |
| `dirtycoverage_createidx.bak` | 0.048s |
| `dirtycoverage_createtable.bak` | 0.044s |
| `dirtycoverage_delete.bak` | 0.07s |
| `dirtycoverage_dropcol.bak` | 0.04s |
| `dirtycoverage_dropidx.bak` | 0.046s |
| `dirtycoverage_droptable.bak` | 0.051s |
| `dirtycoverage_heap_forward.bak` | 0.062s |
| `dirtycoverage_large_dirty.bak` | 0.359s |
| `dirtycoverage_lob_update.bak` | 0.089s |
| `dirtycoverage_maxrow.bak` | 0.047s |
| `dirtycoverage_nchar_delete.bak` | 0.084s |
| `dirtycoverage_nested.bak` | 0.082s |
| `dirtycoverage_null_update.bak` | 0.097s |
| `dirtycoverage_rebuildidx.bak` | 0.068s |
| `dirtycoverage_rich_insert.bak` | 0.103s |
| `dirtycoverage_rich_update.bak` | 0.081s |
| `dirtycoverage_savepoint.bak` | 0.086s |
| `dirtycoverage_snapshot_update.bak` | 0.075s |
| `dirtycoverage_switch.bak` | 0.055s |
| `dirtycoverage_temporal_update.bak` | 0.08s |
| `dirtycoverage_truncate.bak` | 0.058s |
| `dirtycoverage_two_tx.bak` | 0.087s |
| `dirtycoverage_uncommitted.bak` | 0.081s |
| `dirtycoverage_update.bak` | 0.076s |
| `featurecoverage_full.bak` | 0.144s |
| `filtered_ncci_full.bak` | 0.057s |
| `float_extreme_full.bak` | 0.046s |
| `forwarded_records_full.bak` | 0.14s |
| `ghost_records_full.bak` | 0.045s |
| `heapcoverage_large.bak` | 0.062s |
| `heapcoverage_large_50000.bak` | 0.935s |
| `hierarchyid_extract_full.bak` | 0.041s |
| `high_slot_density_full.bak` | 0.53s |
| `incrementalcoverage_diff_01.bak` | 0.045s |
| `incrementalcoverage_diff_02.bak` | 0.041s |
| `incrementalcoverage_diff_03.bak` | 0.04s |
| `incrementalcoverage_diff_04.bak` | 0.045s |
| `incrementalcoverage_diff_05.bak` | 0.048s |
| `incrementalcoverage_diff_06.bak` | 0.045s |
| `incrementalcoverage_full.bak` | 0.034s |
| `layoutcoverage_full.bak` | 0.282s |
| `max_row_width_full.bak` | 0.043s |
| `mixed_collation_full.bak` | 0.037s |
| `multi_rowgroup_full.bak` | 0.057s |
| `native_json_full.bak` | 0.041s |
| `ncci_heap_full.bak` | 0.043s |
| `ncci_types_full.bak` | 0.419s |
| `ndfcoverage_full.bak` | 0.048s |
| `nvarchar_max_u21_full.bak` | 0.04s |
| `ordered_cci_full.bak` | 0.063s |
| `pagecomp_anchor_full.bak` | 0.328s |
| `pfor_columnstore_full.bak` | 2.125s |
| `pfor_columnstore_random_full.bak` | 2.134s |
| `realworld_numeric_digest_full.bak` | 0.17s |
| `rowboundary_full.bak` | 0.051s |
| `rowstore_hash_pii_full.bak` | 0.04s |
| `rowstore_lob_image_full.bak` | 0.045s |
| `rowstore_lob_markup_full.bak` | 0.04s |
| `rowversion_extract_full.bak` | 0.046s |
| `sparse_full.bak` | 0.265s |
| `spatial_edge_full.bak` | 0.051s |
| `spatial_index_full.bak` | 0.056s |
| `sql_variant_extract_full.bak` | 0.05s |
| `striped_full_1.bak` | 0.054s |
| `striped_full_2.bak` | 0.048s |
| `striped_single.bak` | 0.052s |
| `surrogate_pairs_full.bak` | 0.035s |
| `tabletype_cci_large_full.bak` | 0.074s |
| `tabletypecoverage_diff.bak` | 0.141s |
| `tabletypecoverage_full.bak` | 0.115s |
| `temporal_hidden_full.bak` | 0.044s |
| `torn_page_full.bak` | 0.044s |
| `typecoverage_full.bak` | 0.085s |
| `typed_xml_full.bak` | 0.04s |
| `unicode_codepage_coverage.bak` | 0.053s |
| `utf8_collation_full.bak` | 0.038s |
| `vector_full.bak` | 0.041s |
| `xml_index_full.bak` | 0.045s |
| `xmlcoverage_full.bak` | 0.037s |
| `xmlheap_full.bak` | 0.09s |
| `xtp_probe_full.bak` | 0.11s |
| `xtp_rich_full.bak` | 0.096s |
| `xtp_simple_full.bak` | 0.098s |

---

_Generated 2026-07-01 · 533 fixtures · 532 pass · 0 xfail · 1 fail_
