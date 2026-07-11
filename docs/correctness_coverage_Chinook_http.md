# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld tests/fixtures_realworld/Chinook.bak`.

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
| `Chinook.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |

## Per-fixture detail

### `Chinook.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.098 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `Chinook.bak` | 0.088s | 0.308s | 0.396s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-10 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
