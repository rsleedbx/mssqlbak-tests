## Statistics metadata — Phase B `[EMPIRICAL]`

### Scope
User-visible statistics objects (existence, key columns, raw STATS_STREAM blob).
Auto-created statistics (`_WA_Sys_*`), spatial/XML index internal statistics
(`si_*`, `pxi_*`, `sxi_*`, `PXML_*`, `XMLPATH_*`, `XMLPROPERTY_*`,
`XMLVALUE_*`), and statistics on indexed views are excluded.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysidxstats` | 54 | `catalog/columns.py: _SYSIDXSTATS_COLS` |
| `sysiscols` | 55 | `catalog/columns.py: _SYSISCOLS_COLS` |
| `sysobjvalues` | 60 | `catalog/columns.py: _SYSOBJVALUES_COLS` (STATS_STREAM blob) |

---

### Recovery

Source: `mssqlbak/perf.py: recover_statistics`

**Step 1 — key columns** (`sysiscols`):
Each `(idmajor, idminor)` pair → ordered list of `intprop` column ids (sorted by `subid`).

**Step 2 — STATS_STREAM blobs** (`sysobjvalues`):
Rows with `valclass == 40` (`_VALCLASS_STATS_STREAM = 40`); keyed by
`(objid, subobjid)` where `subobjid` is the stat's `indid`.  The raw blob
is followed through LOB pages if required.

**Step 3 — statistics rows** (`sysidxstats`):
All rows with `indid > 0` (skip `indid=0` heaps).  `indid 1..255` = index-backed
stats; `indid >= 256` = statistics-only objects.

The `auto_created` flag is decoded from `status & _STAT_STATUS_AUTO_CREATED`.
The `no_recompute` flag from `status & _STAT_STATUS_NO_RECOMPUTE`.

---

### Histogram decode `[EMPIRICAL]`

Source: `mssqlbak/perf.py: _decode_histogram`

STATS_STREAM format (version 2, little-endian, SQL Server 2012+):

```
[0:2]   version   uint16 LE  (0x0200 = v2)
[2:4]   num_steps uint16 LE
[4:8]   num_density_cols uint32 LE
...     density vector (num_density_cols × 8 bytes each)
...     histogram steps: range_hi_key + 4 × float64 metrics
```

Versions 0x0100, 0x0200, 0x0300 are recognised.  Full per-step key-type decode
requires the column's SQL type (not yet wired in); `stats_stream` raw bytes are
preserved in `Statistic.stats_stream` for pass-through `UPDATE STATISTICS … WITH
STATS_STREAM` re-application.

---

### Verification natural key and compared fields

Natural key: `(table FQN, stat name)`.

Compared field: `key_columns` (list of column names).

Auto-created statistics are excluded by the verifier (GT filters `auto_created=0`
from `sys.stats`).  Internal stat name prefixes are also excluded on the
recovered side (see scope).

Source: `metadata_verify.py: verify_statistics`.

---

### Scoping filter (base tables)

GT collects statistics via `JOIN sys.tables` (base tables only).  Statistics on
indexed views are never in GT.  The verifier skips any statistic whose
`object_id` is not in `rm.base_table_ids`.

---

### Data model

Source: `mssqlbak/catalog/model.py: Statistic`

```python
@dataclass
class Statistic:
    name:            str
    object_id:       int
    stat_id:         int        # sysidxstats.indid
    key_column_ids:  list[int]
    auto_created:    bool
    no_recompute:    bool
    stats_stream:    bytes | None   # raw STATS_STREAM blob
    histogram:       list[HistogramStep]
```

`perf.py: emit_perf_scripts` emits an `UPDATE STATISTICS … WITH STATS_STREAM`
T-SQL script using the raw blob.  `emit_perf_tabular` returns the histogram steps
as an Arrow table for analytical use.
