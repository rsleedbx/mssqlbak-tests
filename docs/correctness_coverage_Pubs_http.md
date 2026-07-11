# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld tests/fixtures_realworld/Pubs.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 11/11 pass · **Columns:** 64/64 pass

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
| `Pubs.bak` | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | **880/880** | ✓ |

## Per-fixture detail

### `Pubs.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.5 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells **184/184** ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells **301/301** ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells **42/42** ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells **16/16** ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells **63/63** ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells **30/30** ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **50/50** ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells **162/162** ✓ |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `Pubs.bak` | 0.131s | 0.116s | 0.247s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-10 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
