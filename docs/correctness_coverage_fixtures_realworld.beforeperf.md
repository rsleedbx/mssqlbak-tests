# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld`.

**59 fixtures · 51 pass · 0 xfail (known gap) · 8 fail**

**Tables:** 1426/1433 pass · **Columns:** 12526/12536 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** 7 fail

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
| `AdventureWorksDW2016_EXT.bak` | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | **7823359/7823359** | ✓ |
| `tpcxbb_1gb.bak` | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | 156/156 ⚠ | ✗ |
| `StackOverflowMini.bak` | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | 8290987/8290987 ⚠ | ✗ |
| `WideWorldImporters-Full.bak` | 4,713,833 | 549 | **48/48** | **525/525** | **1004/1004** | **48/48** | **11936655/11936655** | ✓ |
| `WideWorldImporters-Standard.bak` | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard_old.bak` | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full_old.bak` | 4,713,832 | 549 | **48/48** | **525/525** | **1004/1004** | **48/48** | **11936655/11936655** | ✓ |
| `NYCTaxi_Sample.bak` | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest ⚠ | ✗ |
| `WideWorldImportersDW-Full.bak` | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | **13606612/13606612** | ✓ |
| `GeneralHospital.bak` | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest ⚠ | ✗ |
| `WideWorldImportersDW-Standard.bak` | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | **14410908/14410908** | ✓ |
| `dba.stackexchange.com.bak` | 2,968,576 | 63 | **8/8** | **63/63** | **122/122** | **8/8** | digest ⚠ | ✗ |
| `AdventureWorks2016_EXT.bak` | 1,378,717 | 732 | **92/92** | **617/617** | **860/860** | **92/92** | **9433647/9433647** | ✓ |
| `SalesDB2014.bak` | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **850382/850382** | ✓ |
| `SalesDBOriginal.bak` | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | **850386/850386** | ✓ |
| `CreditBackup100.bak` | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | **1928363/1928363** | ✓ |
| `AdventureWorks2016.bak` | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2012.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2022.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2008R2.bak` | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2019.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorksDW2012.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorks2014.bak` | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2017.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorksDW2019.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorks2025.bak` | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5640293/5640293** | ✓ |
| `AdventureWorksDW2022.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2014.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2016.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2017.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2025.bak` | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | 7852154/7877562 ⚠ | ✗ |
| `BaseballData.bak` | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | **8129498/8129498** | ✓ |
| `CorruptDemoDataPurity.bak` | — | — | — | — | — | — | confidence pass · constraints: 50 total · 50 pass · 0 fail | ✓ |
| `CorruptDemoNCIndex.bak` | — | — | — | — | — | — | confidence pass · constraints: 50 total · 50 pass · 0 fail | ✓ |
| `AdventureWorksDW2008R2.bak` | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | **3543730/3543730** | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | **1760000/1760000** | ✓ |
| `AdventureWorks2014_Corrupt2.bak` | — | — | — | — | — | — | confidence pass · constraints: 1130 total · 1130 pass · 0 fail | ✓ |
| `AdventureWorks2014_Corrupt.bak` | — | — | — | — | — | — | confidence pass · constraints: 1130 total · 1130 pass · 0 fail | ✓ |
| `IndexInternals2008.bak` | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | **800000/800000** | ✓ |
| `data.gov.bak` | 150,482 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `Chinook-id-pk.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `AdventureWorksLT2025.bak` | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2012.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2022.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2014.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2019.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2016.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2017.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `Pubs.bak` | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | **880/880** | ✓ |
| `TutorialDB.bak` | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `CorruptDemoRestoreOrRepair.bak` | — | — | — | — | — | — | confidence fail (row_count_consistency: decoded row count differs from catalog) · constraints: 15 total · 14 pass · 1 fail  [row_count_consistency: 1F] | ✗ |
| `CorruptDemoFatalCorruption2.bak` | — | — | — | — | — | — | confidence pass · constraints: 4 total · 4 pass · 0 fail | ✓ |
| `Corrupt2008DemoFatalCorruption1.bak` | — | — | — | — | — | — | confidence pass · constraints: 4 total · 4 pass · 0 fail | ✓ |
| `Corrupt2008DemoFatalCorruption2.bak` | — | — | — | — | — | — | confidence pass · constraints: 4 total · 4 pass · 0 fail | ✓ |
| `CorruptDemoFatalCorruption1.bak` | — | — | — | — | — | — | confidence pass · constraints: 4 total · 4 pass · 0 fail | ✓ |
| `DemoCorruptMetadata2008R2.bak` | — | — | — | — | — | — | confidence pass · constraints: 4 total · 4 pass · 0 fail | ✓ |
| `DemoCorruptMetadata2000.bak` | — | — | — | — | — | — | confidence fail (catalog_consistency: schema recovery failed: could not locate sysallocunits from the boot page; the backup may be compressed, encrypted, or an unsupported layout) · constraints: 3 total · 2 pass · 1 fail  [catalog_consistency: 1F] | ✗ |

## Per-fixture detail

### `ContosoRetailDW.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 629.956 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | 24 | ✓ | **13/13** | **24/24** | ✓ | cells **288/288** ✓ |
| `dbo.DimChannel` | 4 | ✓ | **7/7** | **14/14** | ✓ | cells **24/24** ✓ |
| `dbo.DimCurrency` | 28 | ✓ | **7/7** | **14/14** | ✓ | cells **168/168** ✓ |
| `dbo.DimCustomer` | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells **528332/528332** ✓ |
| `dbo.DimDate` | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells **71568/71568** ✓ |
| `dbo.DimEmployee` | 293 | ✓ | **27/27** | **54/54** | ✓ | cells **7618/7618** ✓ |
| `dbo.DimEntity` | 421 | ✓ | **13/13** | **24/24** | ✓ | cells **5052/5052** ✓ |
| `dbo.DimGeography` | 674 | ✓ | **10/10** | **20/20** | ✓ | cells **6066/6066** ✓ |
| `dbo.DimMachine` | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells **132872/132872** ✓ |
| `dbo.DimOutage` | 303 | ✓ | **11/11** | **22/22** | ✓ | cells **3030/3030** ✓ |
| `dbo.DimProduct` | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells **78027/78027** ✓ |
| `dbo.DimProductCategory` | 8 | ✓ | **7/7** | **14/14** | ✓ | cells **48/48** ✓ |
| `dbo.DimProductSubcategory` | 44 | ✓ | **8/8** | **16/16** | ✓ | cells **308/308** ✓ |
| `dbo.DimPromotion` | 28 | ✓ | **14/14** | **24/24** | ✓ | cells **364/364** ✓ |
| `dbo.DimSalesTerritory` | 265 | ✓ | **15/15** | **28/28** | ✓ | cells **3710/3710** ✓ |
| `dbo.DimScenario` | 3 | ✓ | **7/7** | **14/14** | ✓ | cells **18/18** ✓ |
| `dbo.DimStore` | 306 | ✓ | **25/25** | **50/50** | ✓ | cells **7344/7344** ✓ |
| `dbo.FactExchangeRate` | 773 | ✓ | **8/8** | **16/16** | ✓ | cells **5411/5411** ✓ |
| `dbo.FactInventory` | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells **2931630/2931630** ✓ |
| `dbo.FactITMachine` | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells **162981/162981** ✓ |
| `dbo.FactITSLA` | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells **49250/49250** ✓ |
| `dbo.FactOnlineSales` | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells **3946140/3946140** ✓ |
| `dbo.FactSales` | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells **3406104/3406104** ✓ |
| `dbo.FactSalesQuota` | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells **2357664/2357664** ✓ |
| `dbo.FactStrategyPlan` | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells **1964740/1964740** ✓ |
| `dbo.sysdiagrams` | 0 | — | — | — | — |  |

### `AdventureWorksDW2016_EXT.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 883.324 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactResellerSalesXL_CCI` | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `tpcxbb_1gb.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 233.98 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | 99,000 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.customer_address` | 49,500 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.customer_book_clusters` | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.customer_return_clusters` | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | 109,573 | ✓ | **28/28** | **56/56** | ✓ | cells digest ✓ |
| `dbo.household_demographics` | 7,200 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.income_band` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.inventory` | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.item` | 17,820 | ✓ | **22/22** | **42/42** | ✓ | cells digest ✓ |
| `dbo.item_marketprices` | 89,100 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.product_reviews` | 89,991 | ✓ | **8/8** | **16/16** | ✓ | cells ✗ (bad: digest:pr_review_content) |
| `dbo.promotion` | 300 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.reason` | 35 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ship_mode` | 20 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.store` | 12 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `dbo.store_returns` | 37,902 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.store_sales` | 667,579 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |
| `dbo.time_dim` | 86,400 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.warehouse` | 5 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.web_clickstreams` | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.web_page` | 60 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `dbo.web_returns` | 38,487 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.web_sales` | 668,052 | ✓ | **34/34** | **68/68** | ✓ | cells digest ✓ |
| `dbo.web_site` | 30 | ✓ | **26/26** | **50/50** | ✓ | cells digest ✓ |
| `sqlr.model_scoring_history` | 1 | ✓ | **9/9** | **16/16** | ✓ | cells **8/8** ✓ |
| `sqlr.model_training_history` | 8 | ✓ | **14/14** | **26/26** | ✓ | cells **104/104** ✓ |
| `sqlr.models` | 4 | ✓ | **11/11** | **22/22** | ✓ | cells **40/40** ✓ |
| `sqlr.scripts` | 1 | ✓ | **6/6** | **10/10** | ✓ | cells **4/4** ✓ |

### `StackOverflowMini.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 758.564 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells **1332219/1332219** ✓ |
| `dbo.Comments` | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells **981255/981255** ✓ |
| `dbo.LinkTypes` | 2 | ✓ | **2/2** | **4/4** | ✓ | cells **2/2** ✓ |
| `dbo.PostLinks` | 0 | — | — | — | — |  |
| `dbo.Posts` | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells ✗ (cells 3717901/3717901; bad: digest:Body) |
| `dbo.PostTypes` | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.Users` | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells **1298297/1298297** ✓ |
| `dbo.Votes` | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells **961290/961290** ✓ |
| `dbo.VoteTypes` | 15 | ✓ | **2/2** | **4/4** | ✓ | cells **15/15** ✓ |

### `WideWorldImporters-Full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.223 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | 4 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | 65,998 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |

### `WideWorldImporters-Standard.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.07 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImporters-Standard_old.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.058 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImporters-Full_old.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.171 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | 4 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | 65,998 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |

### `NYCTaxi_Sample.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ | cells ✗ (bad: digest:pickup_longitude, digest:pickup_latitude, digest:dropoff_longitude, digest:dropoff_latitude) |

### `WideWorldImportersDW-Full.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.726 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells **2130003/2130003** ✓ |
| `Fact.Order` | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells **3934004/3934004** ✓ |
| `Fact.Purchase` | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells **75303/75303** ✓ |
| `Fact.Sale` | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells **4337035/4337035** ✓ |
| `Fact.Transaction` | 99,585 | ✓ | — | — | ✓ | cells **1593360/1593360** ✓ |
| `Integration.City_Staging` | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | 0 | — | — | — | — |  |
| `Integration.Lineage` | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
| `Integration.Movement_Staging` | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | 0 | — | — | — | — |  |

### `GeneralHospital.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 316.084 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | 53,787 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Departments` | 64 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Encounters` | 12,457 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Hospitals` | 124 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.OrdersProcedures` | 1,342,130 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Patients` | 7,096 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Physicians` | 10,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Practices` | 1,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.QualityMeasureData` | 293,706 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Results` | 224,724 | ✓ | **55/55** | **104/104** | ✓ | cells digest ✓ |
| `dbo.SurgicalCosts` | 211,233 | ✓ | — | — | ✓ | cells ✗ (bad: digest:Surgical Resource Cost) |
| `dbo.SurgicalEncounters` | 9,403 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Vitals` | 10,216 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

### `WideWorldImportersDW-Standard.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 51.37 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells **2366670/2366670** ✓ |
| `Fact.Order` | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells **4165416/4165416** ✓ |
| `Fact.Purchase` | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells **83670/83670** ✓ |
| `Fact.Sale` | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells **4565300/4565300** ✓ |
| `Fact.Transaction` | 99,585 | ✓ | — | — | ✓ | cells **1692945/1692945** ✓ |
| `Integration.City_Staging` | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | 0 | — | — | — | — |  |
| `Integration.Lineage` | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
| `Integration.Movement_Staging` | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | 0 | — | — | — | — |  |

### `dba.stackexchange.com.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 489.32 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | 416,662 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.Comments` | 340,158 | ✓ | **7/7** | **14/14** | ✓ | cells ✗ (bad: digest:Text) |
| `dbo.PostHistory` | 814,930 | ✓ | **8/8** | **14/14** | ✓ | cells ✗ (bad: digest:Text) |
| `dbo.PostLinks` | 24,460 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Posts` | 238,555 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Tags` | 1,217 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Users` | 240,423 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | 892,171 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `AdventureWorks2016_EXT.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 179 | ✓ | **8/8** | **14/14** | ✓ | cells **1253/1253** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | 538 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Demo.DemoSalesOrderHeaderSeed` | 31,465 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.Employee_Temporal` | 290 | ✓ | **13/13** | **26/26** | ✓ | cells **3480/3480** ✓ |
| `HumanResources.Employee_Temporal_History` | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.Person_json` | 19,972 | ✓ | **15/15** | — | ✓ | cells **279608/279608** ✓ |
| `Person.Person_Temporal` | 19,972 | ✓ | **11/11** | — | ✓ | cells **199720/199720** ✓ |
| `Person.Person_Temporal_History` | 0 | — | — | — | — |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.Product_inmem` | 504 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Production.Product_ondisk` | 504 | ✓ | **24/24** | **46/46** | ✓ | cells **11592/11592** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.CustomerPII` | 19,118 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells **943950/943950** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrder_json` | 31,465 | ✓ | **27/27** | — | ✓ | cells **818090/818090** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderDetail_inmem` | 121,317 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Sales.SalesOrderDetail_ondisk` | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells **849219/849219** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeader_inmem` | 31,465 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Sales.SalesOrderHeader_ondisk` | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells **692230/692230** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOffer_inmem` | 16 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Sales.SpecialOffer_ondisk` | 16 | ✓ | **10/10** | **20/20** | ✓ | cells **144/144** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.SpecialOfferProduct_inmem` | 538 | — | — | — | — | memory-optimized (XTP) — data in checkpoint files, expected absent |
| `Sales.SpecialOfferProduct_ondisk` | 538 | ✓ | **3/3** | **6/6** | ✓ | cells **538/538** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |
| `Sales.TrackingEvent` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |

### `SalesDB2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 28.068 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |

### `SalesDBOriginal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 192.081 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |
| `dbo.sysdiagrams` | 1 | ✓ | **5/5** | **10/10** | ✓ | cells **4/4** ✓ |

### `CreditBackup100.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 52.739 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.charge` | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells **1400000/1400000** ✓ |
| `dbo.corporation` | 500 | ✓ | **11/11** | **22/22** | ✓ | cells **5000/5000** ✓ |
| `dbo.member` | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.member2` | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.payment` | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells **77770/77770** ✓ |
| `dbo.provider` | 500 | ✓ | **12/12** | **24/24** | ✓ | cells **5500/5500** ✓ |
| `dbo.region` | 9 | ✓ | **9/9** | **18/18** | ✓ | cells **72/72** ✓ |
| `dbo.statement` | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells **100000/100000** ✓ |
| `dbo.status` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells **1/1** ✓ |

### `AdventureWorks2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 46.491 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.897 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 200.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2008R2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 181.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 199.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorksDW2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.766 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorks2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.594 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.957 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorksDW2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorks2025.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 47.902 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 927 | ✓ | **8/8** | **14/14** | ✓ | cells **6489/6489** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | 12 | ✓ | **13/13** | **22/22** | ✓ | cells **144/144** ✓ |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorksDW2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorksDW2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.41 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorksDW2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.443 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorksDW2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 22.351 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
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
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
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

### `AdventureWorksDW2025.bak` — ✗ fail

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
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells ✗ (cells 17384/42792; bad: AverageRate, EndOfDayRate, digest:AverageRate, digest:EndOfDayRate) |
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

### `BaseballData.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 114.171 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells **24170/24170** ✓ |
| `dbo.appearances` | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells **1644529/1644529** ✓ |
| `dbo.awardsmanagers` | 156 | ✓ | **6/6** | **10/10** | ✓ | cells **312/312** ✓ |
| `dbo.awardsplayers` | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells **11838/11838** ✓ |
| `dbo.awardssharemanagers` | 372 | ✓ | **7/7** | **14/14** | ✓ | cells **1116/1116** ✓ |
| `dbo.awardsshareplayers` | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells **19593/19593** ✓ |
| `dbo.batting` | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells **2028600/2028600** ✓ |
| `dbo.battingpost` | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells **199690/199690** ✓ |
| `dbo.els_teamnames` | 314 | ✓ | **6/6** | **12/12** | ✓ | cells **1570/1570** ✓ |
| `dbo.fielding` | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells **2021726/2021726** ✓ |
| `dbo.fieldingof` | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells **36084/36084** ✓ |
| `dbo.fieldingpost` | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells **145379/145379** ✓ |
| `dbo.halloffame` | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells **23298/23298** ✓ |
| `dbo.managers` | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells **23142/23142** ✓ |
| `dbo.managershalf` | 93 | ✓ | **10/10** | **20/20** | ✓ | cells **558/558** ✓ |
| `dbo.pitching` | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells **1130139/1130139** ✓ |
| `dbo.pitchingpost` | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells **124524/124524** ✓ |
| `dbo.players` | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells **530048/530048** ✓ |
| `dbo.salaries` | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells **23141/23141** ✓ |
| `dbo.schools` | 749 | ✓ | **5/5** | **10/10** | ✓ | cells **2996/2996** ✓ |
| `dbo.schoolsplayers` | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells **12294/12294** ✓ |
| `dbo.seriespost` | 272 | ✓ | **9/9** | **18/18** | ✓ | cells **1904/1904** ✓ |
| `dbo.teams` | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells **122175/122175** ✓ |
| `dbo.teamsfranchises` | 120 | ✓ | **4/4** | **8/8** | ✓ | cells **360/360** ✓ |
| `dbo.teamshalf` | 52 | ✓ | **10/10** | **20/20** | ✓ | cells **312/312** ✓ |

### `CorruptDemoDataPurity.bak` — confidence pass

_SQL Server  · 192.081 MB_

_confidence pass._

### `CorruptDemoNCIndex.bak` — confidence pass

_SQL Server  · 192.081 MB_

_confidence pass._

### `AdventureWorksDW2008R2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 74.109 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | 115 | ✓ | **8/8** | **14/14** | ✓ | cells **805/805** ✓ |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells **21384/21384** ✓ |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | 296 | ✓ | **30/30** | **58/58** | ✓ | cells **8584/8584** ✓ |
| `dbo.DimGeography` | 655 | ✓ | **10/10** | **20/20** | ✓ | cells **5895/5895** ✓ |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | — | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | 11 | ✓ | **5/5** | **10/10** | ✓ | cells **44/44** ✓ |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | 120 | ✓ | **13/13** | **26/26** | ✓ | cells **1440/1440** ✓ |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells **28528/28528** ✓ |
| `dbo.FactFinance` | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells **236454/236454** ✓ |
| `dbo.FactInternetSales` | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells **1268358/1268358** ✓ |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells **1338810/1338810** ✓ |
| `dbo.FactSalesQuota` | 163 | ✓ | **6/6** | **12/12** | ✓ | cells **815/815** ✓ |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells **16362/16362** ✓ |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |

### `EmployeeCaseStudySampleDB2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.293 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |
| `dbo.EmployeeHeap` | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |

### `AdventureWorks2014_Corrupt2.bak` — confidence pass

_SQL Server  · 331.084 MB_

_confidence pass._

### `AdventureWorks2014_Corrupt.bak` — confidence pass

_SQL Server  · 331.084 MB_

_confidence pass._

### `IndexInternals2008.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.427 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |
| `dbo.EmployeeHeap` | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |

### `data.gov.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.047 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | 150,482 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `Chinook-id-pk.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.257 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

### `Chinook.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.098 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

### `AdventureWorksLT2025.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.684 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **6/6** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.426 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.336 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `Pubs.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.5 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | 23 | ✓ | **9/9** | **18/18** | ✓ | cells **184/184** ✓ |
| `dbo.discounts` | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | 43 | ✓ | **8/8** | **16/16** | ✓ | cells **301/301** ✓ |
| `dbo.jobs` | 14 | ✓ | **4/4** | **8/8** | ✓ | cells **42/42** ✓ |
| `dbo.pub_info` | 8 | ✓ | **3/3** | **4/4** | ✓ | cells **16/16** ✓ |
| `dbo.publishers` | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `dbo.roysched` | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | 21 | ✓ | **6/6** | **12/12** | ✓ | cells **63/63** ✓ |
| `dbo.stores` | 6 | ✓ | **6/6** | **12/12** | ✓ | cells **30/30** ✓ |
| `dbo.titleauthor` | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **50/50** ✓ |
| `dbo.titles` | 18 | ✓ | **10/10** | **20/20** | ✓ | cells **162/162** ✓ |

### `TutorialDB.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.411 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | 453 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

### `CorruptDemoRestoreOrRepair.bak` — confidence fail

_SQL Server  · 1.52 MB_

_confidence fail (row_count_consistency: decoded row count differs from catalog)._

### `CorruptDemoFatalCorruption2.bak` — confidence pass

_SQL Server  · 1.395 MB_

_confidence pass._

### `Corrupt2008DemoFatalCorruption1.bak` — confidence pass

_SQL Server  · 1.395 MB_

_confidence pass._

### `Corrupt2008DemoFatalCorruption2.bak` — confidence pass

_SQL Server  · 1.395 MB_

_confidence pass._

### `CorruptDemoFatalCorruption1.bak` — confidence pass

_SQL Server  · 1.395 MB_

_confidence pass._

### `DemoCorruptMetadata2008R2.bak` — confidence pass

_SQL Server  · 1.277 MB_

_confidence pass._

### `DemoCorruptMetadata2000.bak` — confidence fail

_SQL Server  · 0.704 MB_

_confidence fail (catalog_consistency: schema recovery failed: could not locate sysallocunits from the boot page; the backup may be compressed, encrypted, or an unsupported layout)._


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `ContosoRetailDW.bak` | 1413.647s |
| `AdventureWorksDW2016_EXT.bak` | 556.777s |
| `tpcxbb_1gb.bak` | 321.994s |
| `StackOverflowMini.bak` | 187.917s |
| `WideWorldImporters-Full.bak` | 120.315s |
| `WideWorldImporters-Standard.bak` | 118.37s |
| `WideWorldImporters-Standard_old.bak` | 119.065s |
| `WideWorldImporters-Full_old.bak` | 121.671s |
| `NYCTaxi_Sample.bak` | 86.734s |
| `WideWorldImportersDW-Full.bak` | 74.519s |
| `GeneralHospital.bak` | 73.53s |
| `WideWorldImportersDW-Standard.bak` | 71.629s |
| `dba.stackexchange.com.bak` | 71.449s |
| `AdventureWorks2016_EXT.bak` | 69.388s |
| `SalesDB2014.bak` | 63.435s |
| `SalesDBOriginal.bak` | 76.685s |
| `CreditBackup100.bak` | 54.597s |
| `AdventureWorks2016.bak` | 48.063s |
| `AdventureWorks2012.bak` | 47.568s |
| `AdventureWorks2022.bak` | 45.741s |
| `AdventureWorks2008R2.bak` | 44.184s |
| `AdventureWorks2019.bak` | 41.587s |
| `AdventureWorksDW2012.bak` | 40.731s |
| `AdventureWorks2014.bak` | 41.967s |
| `AdventureWorks2017.bak` | 42.161s |
| `AdventureWorksDW2019.bak` | 40.849s |
| `AdventureWorks2025.bak` | 42.471s |
| `AdventureWorksDW2022.bak` | 41.392s |
| `AdventureWorksDW2014.bak` | 41.72s |
| `AdventureWorksDW2016.bak` | 41.536s |
| `AdventureWorksDW2017.bak` | 42.095s |
| `AdventureWorksDW2025.bak` | 41.838s |
| `BaseballData.bak` | 39.165s |
| `CorruptDemoDataPurity.bak` | 36.051s |
| `CorruptDemoNCIndex.bak` | 36.712s |
| `AdventureWorksDW2008R2.bak` | 19.547s |
| `EmployeeCaseStudySampleDB2012.bak` | 12.509s |
| `AdventureWorks2014_Corrupt2.bak` | 11.028s |
| `AdventureWorks2014_Corrupt.bak` | 10.551s |
| `IndexInternals2008.bak` | 5.883s |
| `data.gov.bak` | 4.887s |
| `Chinook-id-pk.bak` | 0.494s |
| `Chinook.bak` | 0.439s |
| `AdventureWorksLT2025.bak` | 0.483s |
| `AdventureWorksLT2012.bak` | 0.467s |
| `AdventureWorksLT2022.bak` | 0.413s |
| `AdventureWorksLT2014.bak` | 0.44s |
| `AdventureWorksLT2019.bak` | 0.417s |
| `AdventureWorksLT2016.bak` | 0.4s |
| `AdventureWorksLT2017.bak` | 0.405s |
| `Pubs.bak` | 0.179s |
| `TutorialDB.bak` | 0.08s |
| `CorruptDemoRestoreOrRepair.bak` | 0.03s |
| `CorruptDemoFatalCorruption2.bak` | 0.019s |
| `Corrupt2008DemoFatalCorruption1.bak` | 0.021s |
| `Corrupt2008DemoFatalCorruption2.bak` | 0.021s |
| `CorruptDemoFatalCorruption1.bak` | 0.021s |
| `DemoCorruptMetadata2008R2.bak` | 0.018s |
| `DemoCorruptMetadata2000.bak` | 0.009s |

---

_Generated 2026-07-01 · 59 fixtures · 51 pass · 0 xfail · 8 fail_
