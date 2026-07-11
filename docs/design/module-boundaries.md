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

## Deferred (out of scope for this pass)

| Module | Lines | Reason deferred |
|---|---|---|
| `rows.py` | ~860 | Core hot path — splitting risks performance regression without profiling |
| `extract.py` | ~500 | Thin orchestration layer; acceptable as a single file |
| `pages.py` | ~300 | Stable, rarely changed; splitting adds indirection without clear gain |

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
