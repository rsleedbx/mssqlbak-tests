# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures`.

**31 fixtures · 31 pass · 0 xfail (known gap) · 0 fail**

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
| `dirtycoverage_addcol.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_addnotnull.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_alldirty.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_altercol.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_alterdb.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_concurrent.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_createidx.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_createtable.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_delete.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_dropcol.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_dropidx.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_droptable.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_heap_forward.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_large_dirty.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_lob_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_maxrow.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_nchar_delete.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_nested.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_null_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_rebuildidx.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_rich_insert.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_rich_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_savepoint.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_snapshot_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_switch.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_temporal_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_truncate.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_two_tx.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_uncommitted.bak` | — | — | — | — | — | — | confidence pass | ✓ |
| `dirtycoverage_update.bak` | — | — | — | — | — | — | confidence pass | ✓ |

## Per-fixture detail

### `dirtycoverage_addcol.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_addnotnull.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_alldirty.bak` — confidence pass

_SQL Server  · 3.301 MB_

_confidence pass._

### `dirtycoverage_altercol.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_altercol_rewrite.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_alterdb.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_concurrent.bak` — confidence pass

_SQL Server  · 3.863 MB_

_confidence pass._

### `dirtycoverage_createidx.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_createtable.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_delete.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_dropcol.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_dropidx.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_droptable.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_heap_forward.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_large_dirty.bak` — confidence pass

_SQL Server  · 4.176 MB_

_confidence pass._

### `dirtycoverage_lob_update.bak` — confidence pass

_SQL Server  · 3.363 MB_

_confidence pass._

### `dirtycoverage_maxrow.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_nchar_delete.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_nested.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_null_update.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_rebuildidx.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_rich_insert.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_rich_update.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_savepoint.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_snapshot_update.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_switch.bak` — confidence pass

_SQL Server  · 3.926 MB_

_confidence pass._

### `dirtycoverage_temporal_update.bak` — confidence pass

_SQL Server  · 3.301 MB_

_confidence pass._

### `dirtycoverage_truncate.bak` — confidence pass

_SQL Server  · 3.613 MB_

_confidence pass._

### `dirtycoverage_two_tx.bak` — confidence pass

_SQL Server  · 3.238 MB_

_confidence pass._

### `dirtycoverage_uncommitted.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._

### `dirtycoverage_update.bak` — confidence pass

_SQL Server  · 3.676 MB_

_confidence pass._


## Extraction timings

| Backup | Extract time |
|--------|-------------|
| `dirtycoverage_addcol.bak` | 0s |
| `dirtycoverage_addnotnull.bak` | 0s |
| `dirtycoverage_alldirty.bak` | 0s |
| `dirtycoverage_altercol.bak` | 0s |
| `dirtycoverage_altercol_rewrite.bak` | 0s |
| `dirtycoverage_alterdb.bak` | 0s |
| `dirtycoverage_concurrent.bak` | 0s |
| `dirtycoverage_createidx.bak` | 0s |
| `dirtycoverage_createtable.bak` | 0s |
| `dirtycoverage_delete.bak` | 0s |
| `dirtycoverage_dropcol.bak` | 0s |
| `dirtycoverage_dropidx.bak` | 0s |
| `dirtycoverage_droptable.bak` | 0s |
| `dirtycoverage_heap_forward.bak` | 0s |
| `dirtycoverage_large_dirty.bak` | 0s |
| `dirtycoverage_lob_update.bak` | 0s |
| `dirtycoverage_maxrow.bak` | 0s |
| `dirtycoverage_nchar_delete.bak` | 0s |
| `dirtycoverage_nested.bak` | 0s |
| `dirtycoverage_null_update.bak` | 0s |
| `dirtycoverage_rebuildidx.bak` | 0s |
| `dirtycoverage_rich_insert.bak` | 0s |
| `dirtycoverage_rich_update.bak` | 0s |
| `dirtycoverage_savepoint.bak` | 0s |
| `dirtycoverage_snapshot_update.bak` | 0s |
| `dirtycoverage_switch.bak` | 0s |
| `dirtycoverage_temporal_update.bak` | 0s |
| `dirtycoverage_truncate.bak` | 0s |
| `dirtycoverage_two_tx.bak` | 0s |
| `dirtycoverage_uncommitted.bak` | 0s |
| `dirtycoverage_update.bak` | 0s |

---

_Generated 2026-06-28 · 31 fixtures · 31 pass · 0 xfail · 0 fail_
