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
| `AdventureWorks2016_EXT.bak` | 1,378,717 | 732 | **92/92** | **675/675** | **974/974** | **92/92** | **10486082/10486082** | ✓ |

## Per-fixture detail

### `AdventureWorks2016_EXT.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | 179 | ✓ | **8/8** | **14/14** | ✓ | cells **1253/1253** ✓ |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | 538 | ✓ | **5/5** | **10/10** | ✓ | cells **2152/2152** ✓ |
| `Demo.DemoSalesOrderHeaderSeed` | 31,465 | ✓ | **7/7** | **14/14** | ✓ | cells **188790/188790** ✓ |
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
| `Production.Product_inmem` | 504 | ✓ | **24/24** | **46/46** | ✓ | cells **11592/11592** ✓ |
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
| `Sales.SalesOrderDetail_inmem` | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells **849219/849219** ✓ |
| `Sales.SalesOrderDetail_ondisk` | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells **849219/849219** ✓ |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeader_inmem` | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells **692230/692230** ✓ |
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
| `Sales.SpecialOffer_inmem` | 16 | ✓ | **10/10** | **20/20** | ✓ | cells **144/144** ✓ |
| `Sales.SpecialOffer_ondisk` | 16 | ✓ | **10/10** | **20/20** | ✓ | cells **144/144** ✓ |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.SpecialOfferProduct_inmem` | 538 | ✓ | **3/3** | **6/6** | ✓ | cells **538/538** ✓ |
| `Sales.SpecialOfferProduct_ondisk` | 538 | ✓ | **3/3** | **6/6** | ✓ | cells **538/538** ✓ |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |
| `Sales.TrackingEvent` | 7 | ✓ | **2/2** | **4/4** | ✓ | cells **7/7** ✓ |


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `AdventureWorks2016_EXT.bak` | 87.206s |

---

_Generated 2026-07-04 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
