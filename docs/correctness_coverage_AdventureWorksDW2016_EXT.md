# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/AdventureWorksDW2016_EXT.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 33/33 pass · **Columns:** 413/413 pass

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
| `AdventureWorksDW2016_EXT.bak` | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | **7823359/7823359** | ✓ |

## Per-fixture detail

### `AdventureWorksDW2016_EXT.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 883.324 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `AdventureWorksDW2016_EXT.bak` | 56.319s | 49.995s | 106.314s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-09 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
