# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld tests/fixtures_realworld/Chinook.bak tests/fixtures_realworld/BaseballData.bak tests/fixtures_realworld/NYCTaxi_Sample.bak`.

**3 fixtures · 3 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 38/38 pass · **Columns:** 442/442 pass

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
| `BaseballData.bak` | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | **8129498/8129498** | ✓ |
| `Chinook.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `NYCTaxi_Sample.bak` | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest | ✓ |

## Per-fixture detail

### `BaseballData.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 114.171 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells **24170/24170** ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells **1644529/1644529** ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells **312/312** ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells **11838/11838** ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells **1116/1116** ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells **19593/19593** ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells **2028600/2028600** ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells **199690/199690** ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells **1570/1570** ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells **2021726/2021726** ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells **36084/36084** ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells **145379/145379** ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells **23298/23298** ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells **23142/23142** ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells **558/558** ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells **1130139/1130139** ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells **124524/124524** ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells **530048/530048** ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells **23141/23141** ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells **2996/2996** ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells **12294/12294** ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells **1904/1904** ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells **122175/122175** ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells **360/360** ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells **312/312** ✓ |

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

### `NYCTaxi_Sample.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `BaseballData.bak` | 9.476s | 25.411s | 34.887s |
| `Chinook.bak` | 0.12s | 0.313s | 0.433s |
| `NYCTaxi_Sample.bak` | 15.247s | 47.253s | 62.5s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-10 · 3 fixtures · 3 pass · 0 xfail · 0 fail_
