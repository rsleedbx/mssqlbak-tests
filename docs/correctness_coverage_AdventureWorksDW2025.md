# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/AdventureWorksDW2025.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 31/31 pass · **Columns:** 359/359 pass

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
| `AdventureWorksDW2025.bak` | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | **7877562/7877562** | ✓ |

## Per-fixture detail

### `AdventureWorksDW2025.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 24.133 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **12/12** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells **1911/1911** ✓ |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `AdventureWorksDW2025.bak` | 35.775s |

---

_Generated 2026-07-01 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
