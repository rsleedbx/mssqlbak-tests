# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld tests/fixtures_realworld/ContosoRetailDW.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 26/26 pass · **Columns:** 384/384 pass

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
| `ContosoRetailDW.bak` | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | **15668757/15668757** | ✓ |

## Per-fixture detail

### `ContosoRetailDW.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 629.956 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells **288/288** ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells **24/24** ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells **168/168** ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells **528332/528332** ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells **71568/71568** ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells **7618/7618** ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells **5052/5052** ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells **6066/6066** ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells **132872/132872** ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells **3030/3030** ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells **78027/78027** ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells **48/48** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells **308/308** ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells **364/364** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells **3710/3710** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells **18/18** ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells **7344/7344** ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells **5411/5411** ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells **2931630/2931630** ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells **162981/162981** ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells **49250/49250** ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells **3946140/3946140** ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells **3406104/3406104** ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells **2357664/2357664** ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells **1964740/1964740** ✓ |
| `dbo.sysdiagrams` | rowstore | 0 | — | — | — | — |  |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `ContosoRetailDW.bak` | 74.37s | 731.307s | 805.677s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-10 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
