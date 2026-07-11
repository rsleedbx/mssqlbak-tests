# Module boundaries

## Summary

The `mssqlbak` decoder package was progressively refactored from a set of
large flat files into layered sub-packages. Each split is a mechanical
reorganisation with no behaviour changes; all existing import call sites
continue to work unchanged via re-export shims in the package `__init__.py`.

---

## Completed splits

### `mssqlbak/logtail/` (was `logtail.py`, ~2949 lines)

```
logtail/
  __init__.py     re-export shim (full symbol surface)
  constants.py    LOP_*, _OFF_*, _BLOCK_*, _DISCRIM_*, _APAD/_MSLS
  byteutil.py     _xb_*, _log_byte, _log_block_sector_byte, _read_log_payload,
                  sector-status helpers, _clobber_offsets
  records.py      find_log_range, iter_log_sectors/records, LogRecord,
                  _iter_cont_records, _apad_has_log_blocks, _has_dml_sub4
  patches.py      ModifyImagePatch, TemporalHistoryPatch, ModifyRedoPatch*,
                  collect_before_image_patches, collect_redo_patches,
                  collect_temporal_history_patches, _decode_cd_nvarchar_to_utf16,
                  _extract_cross
  slots.py        build_uncommitted_set, collect_dirty/restore/modified_slots,
                  collect_redo/restore_rows, collect_committed_delete_slots,
                  collect_dirty_row_bytes, _collect_cont_block_dml
  api.py          LogTailResult, logtail_from_bytes/reader/bak/baks,
                  dirty_slots_from_bak, _logtail_from_data
```

**Layering:** `api` → `slots`/`patches` → `records` → `byteutil`/`constants`

**External consumers:** `extract.py` (patch collectors + `logtail_from_*`),
`rows.py` (`ModifyImagePatch`, `ModifyRedoPatch`, `TemporalHistoryPatch`)

---

### `mssqlbak/catalog/` (was `catalog.py`, ~2471 lines)

```
catalog/
  __init__.py     re-export shim (full symbol surface)
  model.py        Column, AllocUnit, Table, Schema*, Sequence, Synonym,
                  Principal, ObjectPermission, Index, Constraint, ForeignKey,
                  CatalogObjects, CatalogError, DbInfoLsns
  columns.py      _layout, compression_name, _is_ae_column, _graph_col_type,
                  _parse_default_literal, _reconstruct_legacy_rscols,
                  _infer_dropped_col_offsets, _assign_bit_shifts, _decode_idtval,
                  _u/_s/_ptr, all _SYS*_COLS base-table schema lists,
                  ALLOC_*/GRAPH_*/COMPRESSION_* constants
  lob.py          _read_lob_node_c, _follow_lob, LOB struct constants
  bootstrap.py    _Bootstrap, _bootstrap, _bootstrap_cache,
                  _catalog_iam_pages, _primary_records_from_page, _walk_leaf,
                  _decode_table, _find_sysallocunits_first_page,
                  read_dbinfo_lsns, read_dbi_collation, _dbi_collation_from_boot_record
  recover.py      recover_schema, recover_catalog_objects,
                  recover_module_definitions, recover_schemas,
                  recover_user_table_types, recover_sequences/synonyms/
                  principals/object_permissions, _read_default_definitions,
                  INDEX_*/CONSTRAINT_* constants
```

**Layering:** `recover` → `bootstrap`/`columns`/`lob` → `model`

**External consumers:** `columnstore/__init__.py` (`_bootstrap`),
`columnstore/storage/segment_meta.py` (`_walk_leaf`), `rows.py`, `extract.py`,
`ddl.py`, `inspect.py`, `confidence.py`, `_cli.py`

---

### `mssqlbak/types/` (was `types.py`, ~1161 lines)

```
types/
  __init__.py     re-export shim (full symbol surface)
  scalars.py      SQL Server type-id constants (TINYINT…NATIVE_VECTOR),
                  SUPPORTED_TYPE_IDS, int/bit/decimal/money/float/date/time/
                  datetime*/char/nchar/uuid/sql_variant/vector decoders,
                  collation helpers (_codec_for_collation, is_known_collation_sortid,
                  classic_datetime_from_parts, decode_vector)
  native_json.py  decode_native_json + all _msjson_* helpers
  dispatch.py     _dv_* per-type shims, _DECODERS dispatch table,
                  decode_value, _decode_clr_udt, column_supported,
                  _TIME_FIELD_META sentinel
  arrow.py        arrow_type, arrow_schema_for
```

**Layering:** `dispatch` → `scalars`/`native_json`; `arrow` → `dispatch`

**External consumers:** `rows.py`, `extract.py`, `ddl.py`, `inspect.py`,
`confidence.py`, `_cli.py`, `columnstore/` assembly

---

### `mssqlbak/pages/` (was `pages.py`, ~1317 lines)

```
pages/
  __init__.py     re-export shim (full symbol surface)
  header.py       PAGE_SIZE, HEADER_SIZE, _SLOT_SIZE, _H_* offset constants,
                  _FLAG_TORN_PAGE_DETECTION, _U16/_U32/_PAGE_POINTER/_LSN_UNPACK structs,
                  _ImageBuf alias, _slot_struct, page_lsn_tuple, restore_torn_page,
                  PageHeader, _LAZY_THRESHOLD, _ZERO_PAGE
  page.py         Page class (slot array access, record extraction)
  store.py        AnyPageStore protocol, eager PageStore with from_bak/from_diff_bak/
                  from_stripe/from_mirror/from_pages factories, io_stats property
  lazy.py         _LRUChunkCache (with hits/misses counters), LazyPageStore
                  (with prefetch_runs/coalesced_chunks/prefetch_bytes counters),
                  io_stats property, warm_file prefetch hit-rate logging
```

**Layering:** `lazy` → `store` → `page` → `header`

**External consumers:** `rows.py`, `extract/`, `columnstore/`, `confidence.py`,
`inspect.py`; `test_pages.py` imports `AnyPageStore, HEADER_SIZE, PAGE_SIZE, Page,
PageHeader, PageStore, restore_torn_page`

---

### `mssqlbak/extract/` (was `extract.py`, ~1432 lines)

```
extract/
  __init__.py         re-export shim (full public + private symbol surface)
  report.py           TableResult (strategy, pages_touched), ExtractReport (io_stats)
  classify.py         RsColInfo NamedTuple, _MixedCol alias, _FORCE_PYTHON_TYPES,
                      _MIXED_TYPES, _PYTHON_ONLY_TYPES, _CMPRS_MIXED_TYPES, _GRAPH_COMPUTED,
                      _IN_ROW_LIMIT, _HAS_RUST_LOB_IMAGES, BATCH,
                      _is_native_vector, _is_rust_bytes_redecode, _is_encrypted_string,
                      _rust_type_id, _row_overflow_possible, _build_rs_col_info,
                      _codepage_recode_cols
  rust_path.py        _buf_to_array, _run_rust_page_loop, _try_extract_table_rust,
                      _try_extract_table_rust_compressed
  columnstore_path.py _try_extract_table_columnstore
  xtp_path.py         _extract_xtp_table
  python_path.py      _identity, _col_coerce_fn, _redecode_mixed_cols,
                      _recode_codepage_cols, _extract_table
  driver.py           BakInput, extract_bak, extract_bak_to_delta, _extract_bak_inner,
                      _extract_table_threaded, _sink_wants_ddl, _finish_sink
```

**Layering:** `driver` → `rust_path`/`columnstore_path`/`xtp_path`/`python_path` →
`classify` → `report`

**External consumers:** `bacpac.py` (`ExtractReport`, `TableResult`), `_cli.py`
(`extract_bak`, `extract_bak_to_delta`, `BakInput`); test files import
`_build_rs_col_info`, `_is_rust_bytes_redecode`, `_redecode_mixed_cols`

---

### `mssqlbak/rows/` (was `rows.py`, ~1993 lines)

```
rows/
  __init__.py   re-export shim (full public + private symbol surface)
  synth.py      _record_columns, _decode_sparse_vector, _synth_column_set,
                _GraphColsResolved, _resolve_graph_cols, _apply_graph_ids,
                _synth_graph_ids
  pagewalk.py   _cd_index_pointer, _leftmost_leaf, IAM constants
                (_IAM_BITMAP_OFFSET, _IAM_SPA_OFFSET, _IAM_SPA_SLOTS,
                _IAM_SPA_STRUCT, _PAGE_POINTER, _DATA_PAGE, _EXTENT_PAGES,
                _CD_INDEX_TYPE, _CD_NIBBLE_BYTES),
                _heap_pages_for_unit*, _heap_data_pages, _data_pages_with_page,
                _data_pages_raw, _data_pages
  patch.py      _last_var_end, _recover_clobbered*, _apply_before_image(_cd),
                _apply_temporal_history_patch, _afterimage_present,
                _apply_redo_patch(_cd)
  lob.py        blob/text constants, _lob_page, _apply_before_image_lob,
                _stitch_lob, _read_lob_node, _stitch_text_pointer, _read_text_node
  reader.py     read_table_rows (public), _read_compressed, _page_ci;
                imports patch as _patch_mod for monkeypatch compatibility
```

**Layering:** `reader` → `{synth, pagewalk, patch, lob}`; `lob` → `patch`

**External consumers:** `extract/`, `inspect.py`, `confidence.py`, `columnstore/`
(lazy import); `tools/diag/_diag_nul.py` + `_diag_beforeimg.py` monkeypatch
`mssqlbak.rows.patch` directly (updated in this split).

**Deep pass:** phase-boundary INFO logging in `read_table_rows`/`_read_compressed`;
DEBUG for B-tree descent and LOB stitch fallbacks; monkeypatch caveat resolved via
`reader.py` calling patched functions through `_patch_mod` module object.

---

### `mssqlbak/columnstore/decode/enc5/` (was `enc5_raw.py`, ~1984 lines)

```
columnstore/decode/
  enc5_raw.py         re-export shim (full symbol surface via enc5/ package)
  enc5/
    __init__.py       dispatcher: _decode_enc5, _enc5_archive_to_python;
                      re-exports full private surface from all sub-modules
    _const.py         shared constants (_ENC5_SENTINEL, _ENC5_DATA_OFFSET,
                      _ENC5_HDR_ITEM_SZ, _ENC5_HDR_N_NONNULL, _DT2_TIME_LEN_MAP,
                      _ARCHIVE_SUBBLOCK_OUT, _ARCHIVE_NULL_SENTINEL,
                      _MULTICHUNK_XPRESS_FULL_SZ, _ARCHIVE_COMPRESSED_MARKER_LO),
                      _find_enc5_xpress_marker, _enc5_item_size, _enc5_item_to_python
    archive.py        _decode_enc5_archive*, _enc5_archive_has_compressed_subblocks,
                      _looks_numeric_suffix_join, _variable_text_pool_map (~620 lines)
    multichunk.py     _multichunk_xpress_header, _enc5_solve_chunk_pool_sz,
                      _decode_enc5_multichunk_xpress
    formats.py        _enc5_formatc_varlen, _decode_enc5_small_varbinary_xpress,
                      _decode_enc5_compressed, _find_enc5_vld_pages,
                      _find_enc5_vld_rle, _decode_enc5_formatd_vld,
                      _decode_enc5_formatb_fixed
```

**Layering:** `__init__` → `{archive, multichunk, formats}` → `_const`

**External consumers:** `decode/dict_string.py` (`_enc5_item_size`,
`_enc5_item_to_python`); `columnstore/__init__.py` (14 names via `enc5_raw` shim);
all remain importable unchanged.

---

### `mssqlbak/xtp/` (was `xtp.py`, ~1471 lines)

```
xtp/
  __init__.py   re-export shim (full public + private symbol surface)
  _const.py     all numeric/bytes constants: block type magics, struct objects
                (_U32/_U16/_U64), date epoch, type-id frozensets, log/ckpt
                framing constants (_LOG_HEADER_SIZE, _CKPT_PREAMBLE_SIG, …)
  blocks.py     _find_block_sig, _next_run_candidate, _is_compact_data_block,
                scan_compact_blocks, _is_wal_data_block, decode_wal_block,
                scan_wal_blocks
  payload.py    _decode_xtp_date_col, _xtp_is_variable/_fixed_width/_fixed_cols/
                _fixed_align/_var_cols/_null_bitmap_bytes/_var_array_offset,
                _decode_xtp_numeric_col, _nullable_cols_in_order,
                _row_honors_not_null, _apply_null_bitmap, _decode_payload,
                decode_compact_block
  logscan.py    _record_payload, _validate_log_header, _detect_block_size,
                _read_ckpt_payload, _read_ckpt_record,
                _singleton_has_trusted_successor, scan_cfp_log_records
  landing.py    _identity_column, _dense_identity_rows, _xtp_fully_decodable,
                _xtp_fixed_record_consistent, _xtp_var_record_consistent,
                _seq_complete_rows, decode_cfp_log_records
  entry.py      read_xtp_rows (public entry point)
```

**Layering:** `entry` → `{blocks, logscan, landing}`; `logscan` → `blocks`;
`blocks` → `payload`; `landing` → `{payload, logscan}`; all → `_const`

**Cleanup:** removed dead `_read_log_header` function (lines 808–822 of original).

**External consumers:** `extract/driver.py` (lazy import of `read_xtp_rows` only).

---

### `mssqlbak/compressed/` (was `compressed.py`, ~951 lines)

```
compressed/
  __init__.py   re-export shim (full public + private symbol surface)
  _detect.py    layout detection (_Layout, _V1, _V2, _layout_for, is_mssqlbak),
                header-walking (_kraft_complete, _is_record_header, _next_header),
                chunk decode (_decode_chunk), iterator (iter_decompressed_chunks),
                constants (PAGE_SIZE, EXTENT_PAGES, MSSQLBAK_MAGIC, _HUFFMAN_TABLE_BYTES, …)
  stream.py     catalog/page iteration (_CATALOG_EXIT_RUNS, _iter_pages, _CATALOG_MAX_PAGE_ID),
                MDF reconstruction (extract_mdf_files_compressed, extract_mdf_pages_compressed),
                MTF block iteration (_MTF_BLOCK_TYPES, _METADATA_PREFIX_BYTES,
                _iter_chunks_with_pages), random-access (decompress_chunk_bytes,
                fetch_chunk_pages, build_chunk_index), reader buffer (_ReaderBuffer),
                MTF descriptor scan (iter_mtf_descriptor_blocks)
```

**Layering:** `stream` → `_detect`

**External consumers:** `pages/lazy.py`, `pages/store.py`, `reader.py`, `mtf.py`,
`extract/driver.py`; `decoderlab/*` (where applicable).

---

### `mssqlbak/rowcompress/` (was `rowcompress.py`, ~794 lines)

```
rowcompress/
  __init__.py   re-export shim (full public + private symbol surface)
  _layout.py    CD constants (_CD_NULL/_ZERO/_LONG/_TRUE_BIT/_DICT, _CD_SHORT_LEN,
                _HDR_*, _CLUSTER, _EXCESS_INT_WIDTH, _LEADING_ZERO_WIDTH,
                _ROWVERSION_WIDTH, _NORMALIZE_TYPES), RowCompressionError,
                row_type_supported, _CDLayout, _parse_cd, _precompute_geometry,
                _short_value, _OffRowLob, _long_value, physical_columns,
                _short_region_pointers, _long_region, _SPECIAL_DECODERS dict
  page.py       _CI_HAS_ANCHOR, _CI_HAS_DICT, PageCompressionInfo, parse_page_ci,
                _expand_prefix, physical_columns_page
  decode.py     _excess_be, normalize_row_value, _temporal_width, _decode_vardecimal,
                _excess_be_int, _decode_compressed_datetime, _is_utf16le_not_scsu,
                _decode_compressed_nvarchar/_nchar/_clr_udt/_sql_variant/_lob_passthrough,
                _SPECIAL_DECODERS.update(…), decode_compressed_value
```

**Layering:** `decode` → `_layout`; `page` → `_layout`

**External consumers:** `rows/reader.py`, `inspect.py`, `logtail/patches.py`,
`columnstore/storage/segment_meta.py` (`_OffRowLob`, `physical_columns_page`).

---

### `mssqlbak/reader/` (was `reader.py`, ~976 lines)

```
reader/
  __init__.py   re-export shim (full public + private symbol surface)
  _const.py     MTF block type identifiers (BLOCK_TAPE/SSET/…) and parsing
                constants (_MQCI_*, _LSN_STRUCT, _STR_*, _SSET_* flags)
  fields.py     _backup_type_label, common-header checksum+struct constants
                (_COMMON_HDR, _TAPE_NAME_ADDR, _SSET_ATTR, _DB_FILE_RE, …),
                _common_header_checksum_ok, _parse_mtf_date, _resolve_addr,
                _extract_db_files, _extract_server_name
  lsn.py        BackupLSNs (dataclass), lsn_triplet_to_decimal,
                lsn_decimal_to_triplet
  models.py     MediaInfo, BackupSetInfo, BakMetadata (dataclasses)
  framing.py    is_compressed_or_encrypted, _CANDIDATE_BLOCK_SIZES,
                _detect_block_size, _iter_blocks
  parse.py      _parse_tape, _parse_lsns_from_sset_block, _parse_sset,
                _read_metadata_blocks
  metadata.py   read_bak_metadata, _read_bak_metadata_from_reader,
                print_bak_info
  restore.py    _mssql_connect, build_restore_sql, restore_from_bak
```

**Layering:** `restore` → `metadata`; `metadata` → `{parse, framing}`;
`parse` → `{fields, lsn, models}`; `framing` → `{_const, fields}`;
`models` → `lsn`; `lsn`/`fields` → `_const`

**External consumers:** `mssqlbak/__init__.py` (public API), `confidence.py`,
`_cli.py`, `extract/driver.py`, `extract/report.py`, `bak_io.py`;
test files import `BackupLSNs`, `BakMetadata`, `read_bak_metadata`, etc.

---

## Deferred (pending future passes)

---

## Deep-pass conventions

These conventions were applied during the `pages/` and `extract/` splits and apply
to all future splits.

### Logging house style

- Use `from mssqlbak._log import logger` (configured `NullHandler` by default — silent
  unless the caller calls `enable_logging()`).
- **INFO** — real phase boundaries: store/reader creation, table extraction completion,
  end-of-run summary lines (IOStats, prefetch metrics).
- **DEBUG** — per-call detail: strategy selection per table, prefetch fetch/decode
  failures, best-effort probe failures (LSN, log tail, XTP scan).
- Never add per-page or per-row logging on the hot path.

### `RsColInfo` type

`classify.RsColInfo` is a `NamedTuple` (subclass of `tuple`) that carries the Rust
page-decoder column descriptor. It replaces the untyped `list[tuple]` return of
`_build_rs_col_info`. Rust FFI receives it as a plain tuple with no adaptation.
Fields: `type_id, scale, leaf_offset, size, is_variable, var_index, null_index,
collation_utf8, bit_shift, nullable`.

### Error-handling policy

- **Narrow** to the specific exception type(s) actually thrown (`struct.error`,
  `ValueError`, `OSError`, etc.) where the raised type is known and documented.
- **Keep broad** (`except Exception`) for deliberate resilience boundaries (per-table
  safety net in `driver.py`, best-effort probes for LSN/log-tail/XTP scan, prefetch
  fetch/decode silencing in `lazy.py`). Every broad catch must have:
  1. A comment beginning with `# Deliberate:` explaining why it is broad.
  2. A `logger.debug` or `logger.warning` call logging the exception and context.
- No new public exception types are needed; reuse existing `errors.py` / `CatalogError`
  where they are already raised.

### Diagnostic surfaces (new in this pass)

| Surface | Where | What it measures |
|---|---|---|
| `IOStats` | `readers/_iostats.py`, `readers/http.py` | HTTP requests, bytes read, retries, cumulative wait seconds |
| `ExtractReport.io_stats` | `extract/report.py` | `IOStats` for the run (None for local/mmap) |
| `LazyPageStore` prefetch metrics | `pages/lazy.py` | LRU hit/miss rate, prefetch runs, coalesced chunks, bytes fetched |
| `TableResult.strategy` | `extract/report.py` | Which decode path won: `rust`, `rust_compressed`, `columnstore`, `xtp`, `python` |
| `TableResult.pages_touched` | `extract/report.py` | 8 KB pages touched (populated by callers; defaults to 0) |

---

## Design principles

- **Re-export shims only.** Every `__init__.py` re-exports the full public and
  private symbol surface of the original flat module. No call site was changed.
- **One-direction layering.** Each package has a strict dependency order;
  circular imports were avoided by placing shared constants at the lowest layer.
- **No behaviour changes.** These splits are purely structural. No algorithms,
  signatures, or test expectations were modified.
- **Columnstore pattern.** All splits mirror the `mssqlbak/columnstore/`
  package, which was split in an earlier pass.
