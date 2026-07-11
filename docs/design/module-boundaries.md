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

## Deferred (out of scope for this pass)

| Module | Lines | Reason deferred |
|---|---|---|
| `rows.py` | ~860 | Core hot path — splitting risks performance regression without profiling |

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
