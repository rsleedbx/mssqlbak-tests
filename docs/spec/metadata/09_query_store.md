## Query Store metadata — Phase D `[EMPIRICAL]`

### Scope
Query Store settings, query texts, plans, runtime statistics, runtime stats
intervals, and wait statistics.  Recovered from the `plan_persist_*` internal
tables inside the database.

---

### Source tables (internal, user-space)

Query Store uses ordinary user-space tables in the `sys` schema.  They are
located by name via `resolve_internal_table_page` / `resolve_internal_table_rows`
in `catalog/recover.py`.

| Internal table name | Constant | Content |
|--------------------|----------|---------|
| `plan_persist_query_text` | `_QS_TABLE_QUERY_TEXT` | Query SQL texts + statement handles |
| `plan_persist_query` | `_QS_TABLE_QUERY` | Query metadata (compile count, last execution time) |
| `plan_persist_plan` | `_QS_TABLE_PLAN` | Execution plans (compressed showplan XML) |
| `plan_persist_runtime_stats` | `_QS_TABLE_RUNTIME_STATS` | Aggregated runtime metrics per plan per interval |
| `plan_persist_runtime_stats_interval` | `_QS_TABLE_RUNTIME_INTERVAL` | Aggregation interval boundaries |
| `plan_persist_wait_stats` | `_QS_TABLE_WAIT_STATS` | Wait category breakdown per plan per interval |

Column layout constants are defined in `mssqlbak/perf.py`:
`_QS_QUERY_TEXT_COLS`, `_QS_QUERY_COLS`, `_QS_PLAN_COLS`,
`_QS_RUNTIME_STATS_COLS`, `_QS_RUNTIME_INTERVAL_COLS`, `_QS_WAIT_STATS_COLS`.

---

### QS enabled detection `[EMPIRICAL]`

Source: `mssqlbak/perf.py: _recover_qs_options`

`desired_state == 0` means Query Store is explicitly disabled; no
`plan_persist_*` rowsets will exist.  Current implementation probes for the
presence of `plan_persist_query_text` as a proxy for QS enabled.  When the
table is present, `desired_state=2` (READ_WRITE) is returned as a conservative
default (full boot-page option decode is a pending TODO).

---

### Plan XML decompression `[EMPIRICAL]`

Source: `mssqlbak/perf.py: _decompress_plan_xml`

`plan_persist_plan.query_plan` is stored as compressed XML.  Decode order:
1. Try UTF-16-LE plain XML.
2. Try UTF-8 plain XML.
3. Try XPRESS decompression (`mssqlbak.xpress.decompress`) then UTF-16-LE.

---

### Data model

Source: `mssqlbak/catalog/model.py`

```
QueryStoreData
  ├── options:        QueryStoreOptions
  ├── query_texts:    list[QSQueryText]
  ├── queries:        list[QSQuery]
  ├── plans:          list[QSPlan]
  ├── intervals:      list[QSRuntimeStatsInterval]
  ├── runtime_stats:  list[QSRuntimeStats]
  └── wait_stats:     list[QSWaitStats]
```

`QueryStoreData.enabled` returns `True` when `options.desired_state != 0`.

---

### Verification model

Source: `metadata_verify.py: verify_query_store`

Only the **enabled flag** is compared.  Query text comparison is unreliable
because GT (`register_bak.py`) captures SQL texts that the registration process
itself caused SQL Server to record in QS **after** the backup was taken.

Special case: `GT.enabled=True` + `Rec.enabled=False` is accepted as an
expected structural difference (SQL Server 2022 defaults QS on, but the QS
tables may not have been populated before the backup was created).

---

### Emit

Source: `mssqlbak/perf.py: emit_perf_scripts`, `emit_perf_tabular`

- Scripts: T-SQL to re-enable QS, re-apply forced plans, and optionally flush
  the in-memory QS data.
- Tabular: Arrow tables keyed by `"query_store_queries"`, `"query_store_plans"`,
  `"query_store_runtime_stats"`, `"query_store_wait_stats"`.
