# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures`.

**31 fixtures · 31 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 0/0 pass · **Columns:** 0/0 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** ✓

**Edges:** mssql→arrow ✓

Column key:

| Column | Meaning |
|--------|----------|
| Stage | Pipeline edge being compared (e.g. mssql→arrow = extraction correctness) |
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

| Backup | Stage | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |
|--------|-------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|
| `dirtycoverage_addcol.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 17 total · 17 pass · 0 fail | ✓ |
| `dirtycoverage_addnotnull.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 16 total · 16 pass · 0 fail | ✓ |
| `dirtycoverage_alldirty.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_altercol.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 15 total · 15 pass · 0 fail | ✓ |
| `dirtycoverage_altercol_rewrite.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 15 total · 15 pass · 0 fail | ✓ |
| `dirtycoverage_alterdb.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 11 total · 11 pass · 0 fail | ✓ |
| `dirtycoverage_concurrent.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 16 total · 16 pass · 0 fail | ✓ |
| `dirtycoverage_createidx.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 13 total · 13 pass · 0 fail | ✓ |
| `dirtycoverage_createtable.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 11 total · 11 pass · 0 fail | ✓ |
| `dirtycoverage_delete.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_dropcol.bak` | — | — | — | — | — | — | — | confidence warn (collation_codepage: unrecognised collation SORTID; decoded as cp1252 (non-ASCII bytes may be wrong)) · constraints: 17 total · 16 pass · 0 fail | ~ |
| `dirtycoverage_dropidx.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 13 total · 13 pass · 0 fail | ✓ |
| `dirtycoverage_droptable.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 21 total · 21 pass · 0 fail | ✓ |
| `dirtycoverage_heap_forward.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 11 total · 11 pass · 0 fail | ✓ |
| `dirtycoverage_large_dirty.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 15 total · 15 pass · 0 fail | ✓ |
| `dirtycoverage_lob_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 12 total · 12 pass · 0 fail | ✓ |
| `dirtycoverage_maxrow.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 12 total · 12 pass · 0 fail | ✓ |
| `dirtycoverage_nchar_delete.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 13 total · 13 pass · 0 fail | ✓ |
| `dirtycoverage_nested.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_null_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_rebuildidx.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 13 total · 13 pass · 0 fail | ✓ |
| `dirtycoverage_rich_insert.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 26 total · 26 pass · 0 fail | ✓ |
| `dirtycoverage_rich_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 26 total · 26 pass · 0 fail | ✓ |
| `dirtycoverage_savepoint.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_snapshot_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 11 total · 11 pass · 0 fail | ✓ |
| `dirtycoverage_switch.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 24 total · 24 pass · 0 fail | ✓ |
| `dirtycoverage_temporal_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 25 total · 25 pass · 0 fail | ✓ |
| `dirtycoverage_truncate.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_two_tx.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 14 total · 14 pass · 0 fail | ✓ |
| `dirtycoverage_uncommitted.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 16 total · 16 pass · 0 fail | ✓ |
| `dirtycoverage_update.bak` | — | — | — | — | — | — | — | confidence pass · constraints: 16 total · 16 pass · 0 fail | ✓ |

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

### `dirtycoverage_dropcol.bak` — confidence warn

_SQL Server  · 3.613 MB_

_confidence warn (collation_codepage: unrecognised collation SORTID; decoded as cp1252 (non-ASCII bytes may be wrong))._

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

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `dirtycoverage_addcol.bak` | 0s | 0.147s | 0.147s |
| `dirtycoverage_addnotnull.bak` | 0s | 0.277s | 0.277s |
| `dirtycoverage_alldirty.bak` | 0s | 0.218s | 0.218s |
| `dirtycoverage_altercol.bak` | 0s | 0.173s | 0.173s |
| `dirtycoverage_altercol_rewrite.bak` | 0s | 0.236s | 0.236s |
| `dirtycoverage_alterdb.bak` | 0s | 0.32s | 0.32s |
| `dirtycoverage_concurrent.bak` | 0s | 0.303s | 0.303s |
| `dirtycoverage_createidx.bak` | 0s | 0.347s | 0.347s |
| `dirtycoverage_createtable.bak` | 0s | 0.554s | 0.554s |
| `dirtycoverage_delete.bak` | 0s | 0.396s | 0.396s |
| `dirtycoverage_dropcol.bak` | 0s | 0.268s | 0.268s |
| `dirtycoverage_dropidx.bak` | 0s | 0.315s | 0.315s |
| `dirtycoverage_droptable.bak` | 0s | 0.376s | 0.376s |
| `dirtycoverage_heap_forward.bak` | 0s | 0.404s | 0.404s |
| `dirtycoverage_large_dirty.bak` | 0s | 0.437s | 0.437s |
| `dirtycoverage_lob_update.bak` | 0s | 0.302s | 0.302s |
| `dirtycoverage_maxrow.bak` | 0s | 0.27s | 0.27s |
| `dirtycoverage_nchar_delete.bak` | 0s | 0.305s | 0.305s |
| `dirtycoverage_nested.bak` | 0s | 0.217s | 0.217s |
| `dirtycoverage_null_update.bak` | 0s | 0.294s | 0.294s |
| `dirtycoverage_rebuildidx.bak` | 0s | 0.266s | 0.266s |
| `dirtycoverage_rich_insert.bak` | 0s | 0.294s | 0.294s |
| `dirtycoverage_rich_update.bak` | 0s | 0.254s | 0.254s |
| `dirtycoverage_savepoint.bak` | 0s | 0.333s | 0.333s |
| `dirtycoverage_snapshot_update.bak` | 0s | 0.193s | 0.193s |
| `dirtycoverage_switch.bak` | 0s | 0.136s | 0.136s |
| `dirtycoverage_temporal_update.bak` | 0s | 0.077s | 0.077s |
| `dirtycoverage_truncate.bak` | 0s | 0.346s | 0.346s |
| `dirtycoverage_two_tx.bak` | 0s | 0.277s | 0.277s |
| `dirtycoverage_uncommitted.bak` | 0s | 0.187s | 0.187s |
| `dirtycoverage_update.bak` | 0s | 0.181s | 0.181s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis). See **Sink read breakdown** below for the per-phase split._

---

_Generated 2026-07-17 · 31 fixtures · 31 pass · 0 xfail · 0 fail_
