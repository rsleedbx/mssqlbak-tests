# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/AdventureWorks2016_EXT.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 92/92 pass · **Columns:** 732/732 pass

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
| `AdventureWorks2016_EXT.bak` | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | **11178312/11178312** | ✓ |

## Per-fixture detail

### `AdventureWorks2016_EXT.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **14/14** | ✓ | cells **1253/1253** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ | cells **2152/2152** ✓ |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ | cells **188790/188790** ✓ |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ | cells **3480/3480** ✓ |
| `HumanResources.Employee_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells **39/39** ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells **12/12** ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells **156912/156912** ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells **18/18** ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells **41554/41554** ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells **39228/39228** ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells **1818/1818** ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells **40/40** ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells **476/476** ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **59916/59916** ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells **79888/79888** ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells **239664/239664** ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | — | ✓ | cells **279608/279608** ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | — | ✓ | cells **199720/199720** ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ | cells **11592/11592** ✓ |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells **11592/11592** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells **640/640** ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **7/7** ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells **762/762** ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells **505/505** ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells **1008/1008** ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells **28/28** ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells **148/148** ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells **907544/907544** ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells **714024/714024** ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells **76/76** ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells **580728/580728** ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells **604179/604179** ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells **4140/4140** ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells **61915/61915** ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells **44132/44132** ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells **25/25** ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells **728/728** ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells **109/109** ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells **95590/95590** ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells **81192/81192** ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells **99100/99100** ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells **943950/943950** ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | — | ✓ | cells **818090/818090** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells **849219/849219** ✓ |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells **849219/849219** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells **692230/692230** ✓ |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells **692230/692230** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ | cells **144/144** ✓ |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells **144/144** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ | cells **538/538** ✓ |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ | cells **538/538** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `AdventureWorks2016_EXT.bak` | 21.98s | 46.533s | 68.513s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-10 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
