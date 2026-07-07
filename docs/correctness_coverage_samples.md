# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage`.

**45 fixtures · 37 pass · 0 xfail (known gap) · 8 fail**

Column key:

| Column | Meaning |
|--------|----------|
| Source rows | Total rows in all non-empty tables per SQL Server ground truth |
| Source cols | Total columns tracked across all non-empty tables |
| Row count | `matched/total` tables with correct row count |
| Null count | `matched/total` columns with correct null count |
| Min/max | `matched/total` comparable min/max checks; `sql_variant` and `uniqueidentifier` skipped (non-lexicographic ordering) |
| Col count | `matched/total` tables with ≥ expected column count |
| Status | ✓ = all match · ~ = xfail (known gap) · ✗ = mismatch |

## Summary

| Backup | Source rows | Source cols | Row count | Null count | Min/max | Col count | Status |
|--------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|--------|
| `AdventureWorks2008R2.bak` | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | ✓ |
| `AdventureWorks2012.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorks2014.bak` | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorks2016.bak` | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorks2016_EXT.bak` | 1,378,717 | 732 | 85/92 ⚠ ⚠ (`Demo.DemoSalesOrderDetailSeed`, `Demo.DemoSalesOrderHeaderSeed`, `Production.Product_inmem`, `Sales.SalesOrderDetail_inmem`, `Sales.SalesOrderHeader_inmem`, `Sales.SpecialOffer_inmem`, `Sales.SpecialOfferProduct_inmem`) | **617/617** | **860/860** | 85/92 ⚠ | ✗ |
| `AdventureWorks2017.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorks2019.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorks2022.bak` | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | ✓ |
| `AdventureWorksDW2008R2.bak` | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | ✓ |
| `AdventureWorksDW2012.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksDW2014.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksDW2016.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksDW2016_EXT.bak` | 24,400,096 | 413 | **33/33** | **413/413** | 804/814 ⚠ | **33/33** | ✗ |
| `AdventureWorksDW2017.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksDW2019.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksDW2022.bak` | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | ✓ |
| `AdventureWorksLT2012.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `AdventureWorksLT2014.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `AdventureWorksLT2016.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `AdventureWorksLT2017.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `AdventureWorksLT2019.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `AdventureWorksLT2022.bak` | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | ✓ |
| `BaseballData.bak` | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | ✓ |
| `Chinook-id-pk.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | ✓ |
| `Chinook.bak` | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | ✓ |
| `ContosoRetailDW.bak` | 34,326,475 | 384 | **26/26** | **379/379** | 688/736 ⚠ | **26/26** | ✗ |
| `CreditBackup100.bak` | 1,656,574 | 93 | 9/10 ⚠ ⚠ (`dbo.charge`) | 80/93 ⚠ | 181/182 ⚠ | 4/10 ⚠ | ✗ |
| `EmployeeCaseStudySampleDB2012.bak` | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | ✓ |
| `GeneralHospital.bak` | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | ✓ |
| `IndexInternals2008.bak` | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | ✓ |
| `NYCTaxi_Sample.bak` | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | ✓ |
| `Pubs.bak` | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | ✓ |
| `SalesDB2014.bak` | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | ✓ |
| `SalesDBOriginal.bak` | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | ✓ |
| `StackOverflowMini.bak` | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | ✓ |
| `TutorialDB.bak` | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | ✓ |
| `WideWorldImporters-Full.bak` | 4,713,833 | 549 | 46/48 ⚠ ⚠ (`Warehouse.ColdRoomTemperatures`, `Warehouse.VehicleTemperatures`) | 522/525 ⚠ | 973/1004 ⚠ | 46/48 ⚠ | ✗ |
| `WideWorldImporters-Full_old.bak` | 4,713,832 | 549 | 46/48 ⚠ ⚠ (`Warehouse.ColdRoomTemperatures`, `Warehouse.VehicleTemperatures`) | 522/525 ⚠ | 973/1004 ⚠ | 46/48 ⚠ | ✗ |
| `WideWorldImporters-Standard.bak` | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | ✓ |
| `WideWorldImporters-Standard_old.bak` | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | ✓ |
| `WideWorldImportersDW-Full.bak` | 922,709 | 50 | **24/24** | **24/24** | 42/46 ⚠ | **24/24** | ✗ |
| `WideWorldImportersDW-Standard.bak` | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | ✓ |
| `data.gov.bak` | 150,482 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | ✓ |
| `dba.stackexchange.com.bak` | 2,968,576 | 63 | **8/8** | **63/63** | **122/122** | **8/8** | ✓ |
| `tpcxbb_1gb.bak` | 34,001,580 | 394 | 28/30 ⚠ ⚠ (`dbo.inventory`, `dbo.web_clickstreams`) | 349/394 ⚠ | 755/774 ⚠ | **30/30** | ✗ |

## Per-fixture detail

### `AdventureWorks2008R2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 181.109 MB · extracted in 8.848s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **12/12** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **6/6** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **6/6** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.897 MB · extracted in 10.159s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.594 MB · extracted in 9.916s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 46.491 MB · extracted in 9.861s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,597 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2016_EXT.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB · extracted in 15.686s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 179 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | 538 | ✗ | — | — | ✗ | missing from output |
| `Demo.DemoSalesOrderHeaderSeed` | 31,465 | ✗ | — | — | ✗ | missing from output |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.Employee_Temporal` | 290 | ✓ | **13/13** | **26/26** | ✓ |  |
| `HumanResources.Employee_Temporal_History` | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.Person_json` | 19,972 | ✓ | **15/15** | — | ✓ |  |
| `Person.Person_Temporal` | 19,972 | ✓ | **11/11** | — | ✓ |  |
| `Person.Person_Temporal_History` | 0 | — | — | — | — |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.Product_inmem` | 504 | ✗ | — | — | ✗ | missing from output |
| `Production.Product_ondisk` | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.CustomerPII` | 19,118 | ✓ | **8/8** | — | ✓ |  |
| `Sales.OrderTracking` | 188,790 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrder_json` | 31,465 | ✓ | **27/27** | — | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_inmem` | 121,317 | ✗ | — | — | ✗ | missing from output |
| `Sales.SalesOrderDetail_ondisk` | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeader_inmem` | 31,465 | ✗ | — | — | ✗ | missing from output |
| `Sales.SalesOrderHeader_ondisk` | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_inmem` | 16 | ✗ | — | — | ✗ | missing from output |
| `Sales.SpecialOffer_ondisk` | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.SpecialOfferProduct_inmem` | 538 | ✗ | — | — | ✗ | missing from output |
| `Sales.SpecialOfferProduct_ondisk` | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.TrackingEvent` | 7 | ✓ | **2/2** | **4/4** | ✓ |  |

### `AdventureWorks2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.957 MB · extracted in 9.914s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 199.117 MB · extracted in 8.873s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorks2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 200.117 MB · extracted in 8.831s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DatabaseLog` | 1,596 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `HumanResources.Department` | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Employee` | 290 | ✓ | **15/15** | — | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.JobCandidate` | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `HumanResources.Shift` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Address` | 19,614 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Person.AddressType` | 6 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Person.BusinessEntity` | 20,777 | ✓ | **3/3** | **4/4** | ✓ |  |
| `Person.BusinessEntityAddress` | 19,614 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.BusinessEntityContact` | 909 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.ContactType` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.EmailAddress` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Password` | 19,972 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Person.Person` | 19,972 | ✓ | **13/13** | — | ✓ |  |
| `Person.PersonPhone` | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.StateProvince` | 181 | ✓ | **8/8** | — | ✓ |  |
| `Production.BillOfMaterials` | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.Culture` | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Document` | 13 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Production.Illustration` | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Location` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Product` | 504 | ✓ | **25/25** | — | ✓ |  |
| `Production.ProductCategory` | 4 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductCostHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Production.ProductDocument` | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | 1,069 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Production.ProductListPriceHistory` | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | 128 | ✓ | **6/6** | **8/8** | ✓ |  |
| `Production.ProductModelIllustration` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | 504 | ✓ | **4/4** | — | ✓ |  |
| `Production.ProductReview` | 4 | ✓ | **8/8** | **14/14** | ✓ |  |
| `Production.ProductSubcategory` | 37 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Production.ScrapReason` | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.TransactionHistory` | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.WorkOrder` | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ProductVendor` | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | 4,012 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.ShipMethod` | 5 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Purchasing.Vendor` | 104 | ✓ | **8/8** | — | ✓ |  |
| `Sales.CountryRegionCurrency` | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.Currency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | 19,820 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.PersonCreditCard` | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderDetail` | 121,317 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | 31,465 | ✓ | **24/24** | — | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | 17 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | 163 | ✓ | **5/5** | **8/8** | ✓ |  |
| `Sales.SalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | 29 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.SalesTerritory` | 10 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Sales.SalesTerritoryHistory` | 17 | ✓ | **6/6** | **10/10** | ✓ |  |
| `Sales.ShoppingCartItem` | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | 16 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SpecialOfferProduct` | 538 | ✓ | **4/4** | **6/6** | ✓ |  |
| `Sales.Store` | 701 | ✓ | **6/6** | **10/10** | ✓ |  |

### `AdventureWorksDW2008R2.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 74.109 MB · extracted in 0.787s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 115 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 1,188 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **30/30** | **58/58** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | — | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **23/23** | **42/42** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |

### `AdventureWorksDW2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.766 MB · extracted in 1.534s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.41 MB · extracted in 1.545s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.443 MB · extracted in 1.536s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2016_EXT.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 883.324 MB · extracted in 267.638s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_CCI` | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | 11,669,638 | ✓ | **27/27** | 44/54 ⚠ | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 22.351 MB · extracted in 1.594s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB · extracted in 1.205s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB · extracted in 1.201s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | 96 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.DimAccount` | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksLT2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.426 MB · extracted in 0.118s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `AdventureWorksLT2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.336 MB · extracted in 0.132s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `AdventureWorksLT2016.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB · extracted in 0.123s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `AdventureWorksLT2017.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB · extracted in 0.117s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `AdventureWorksLT2019.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB · extracted in 0.121s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `AdventureWorksLT2022.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB · extracted in 0.123s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | 1 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.ErrorLog` | 0 | — | — | — | — |  |
| `SalesLT.Address` | 450 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.Customer` | 847 | ✓ | **15/15** | — | ✓ |  |
| `SalesLT.CustomerAddress` | 417 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.Product` | 295 | ✓ | **17/17** | **30/30** | ✓ |  |
| `SalesLT.ProductCategory` | 41 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductDescription` | 762 | ✓ | **4/4** | **6/6** | ✓ |  |
| `SalesLT.ProductModel` | 128 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | 762 | ✓ | **5/5** | **8/8** | ✓ |  |
| `SalesLT.SalesOrderDetail` | 542 | ✓ | **8/8** | **14/14** | ✓ |  |
| `SalesLT.SalesOrderHeader` | 32 | ✓ | **20/20** | — | ✓ |  |

### `BaseballData.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 114.171 MB · extracted in 6.74s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | 4,834 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.appearances` | 96,737 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.awardsmanagers` | 156 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.awardsplayers` | 5,919 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.awardssharemanagers` | 372 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.awardsshareplayers` | 6,531 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.batting` | 96,600 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.battingpost` | 10,510 | ✓ | **22/22** | **44/44** | ✓ |  |
| `dbo.els_teamnames` | 314 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fielding` | 144,409 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.fieldingof` | 12,028 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fieldingpost` | 11,183 | ✓ | **17/17** | **34/34** | ✓ |  |
| `dbo.halloffame` | 3,883 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.managers` | 3,306 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.managershalf` | 93 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.pitching` | 41,857 | ✓ | **30/30** | **54/54** | ✓ |  |
| `dbo.pitchingpost` | 4,612 | ✓ | **30/30** | **60/60** | ✓ |  |
| `dbo.players` | 16,564 | ✓ | **33/33** | **66/66** | ✓ |  |
| `dbo.salaries` | 23,141 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schools` | 749 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schoolsplayers` | 6,147 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.seriespost` | 272 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.teams` | 2,715 | ✓ | **48/48** | **96/96** | ✓ |  |
| `dbo.teamsfranchises` | 120 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.teamshalf` | 52 | ✓ | **10/10** | **20/20** | ✓ |  |

### `Chinook-id-pk.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.257 MB · extracted in 0.075s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

### `Chinook.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.098 MB · extracted in 0.079s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

### `ContosoRetailDW.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 629.956 MB · extracted in 56.746s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | 24 | ✓ | **13/13** | **24/24** | ✓ |  |
| `dbo.DimChannel` | 4 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCurrency` | 28 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCustomer` | 18,869 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | 2,556 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimEmployee` | 293 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.DimEntity` | 421 | ✓ | **13/13** | **24/24** | ✓ |  |
| `dbo.DimGeography` | 674 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.DimMachine` | 7,816 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.DimOutage` | 303 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimProduct` | 2,517 | ✓ | **32/32** | 54/58 ⚠ | ✓ |  |
| `dbo.DimProductCategory` | 8 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimProductSubcategory` | 44 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimPromotion` | 28 | ✓ | **14/14** | **24/24** | ✓ |  |
| `dbo.DimSalesTerritory` | 265 | ✓ | **15/15** | **28/28** | ✓ |  |
| `dbo.DimScenario` | 3 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimStore` | 306 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.FactExchangeRate` | 773 | ✓ | **8/8** | 13/16 ⚠ | ✓ |  |
| `dbo.FactInventory` | 8,013,099 | ✓ | **16/16** | 25/32 ⚠ | ✓ |  |
| `dbo.FactITMachine` | 23,283 | ✓ | **8/8** | 14/16 ⚠ | ✓ |  |
| `dbo.FactITSLA` | 4,925 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.FactOnlineSales` | 12,627,608 | ✓ | **21/21** | 22/36 ⚠ | ✓ |  |
| `dbo.FactSales` | 3,406,089 | ✓ | **19/19** | 28/38 ⚠ | ✓ |  |
| `dbo.FactSalesQuota` | 7,465,911 | ✓ | **13/13** | 21/26 ⚠ | ✓ |  |
| `dbo.FactStrategyPlan` | 2,750,628 | ✓ | **11/11** | 19/22 ⚠ | ✓ |  |
| `dbo.sysdiagrams` | 0 | — | — | — | — |  |

### `CreditBackup100.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 52.739 MB · extracted in 13.05s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | 10 | ✓ | 2/3 ⚠ | **6/6** | ✓ |  |
| `dbo.charge` | 1,600,000 | ✗ | 6/8 ⚠ | 15/16 ⚠ | ✗ |  |
| `dbo.corporation` | 500 | ✓ | 9/11 ⚠ | **22/22** | ✗ |  |
| `dbo.member` | 10,000 | ✓ | 15/18 ⚠ | **34/34** | ✗ |  |
| `dbo.member2` | 10,000 | ✓ | 15/18 ⚠ | **34/34** | ✗ |  |
| `dbo.payment` | 15,554 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.provider` | 500 | ✓ | 11/12 ⚠ | **24/24** | ✗ |  |
| `dbo.region` | 9 | ✓ | 8/9 ⚠ | **18/18** | ✗ |  |
| `dbo.statement` | 20,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.status` | 1 | ✓ | **2/2** | **4/4** | ✓ |  |

### `EmployeeCaseStudySampleDB2012.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.293 MB · extracted in 2.298s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.EmployeeHeap` | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |

### `GeneralHospital.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 316.084 MB · extracted in 6.003s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | 53,787 | ✓ | — | — | ✓ |  |
| `dbo.Departments` | 64 | ✓ | — | — | ✓ |  |
| `dbo.Encounters` | 12,457 | ✓ | — | — | ✓ |  |
| `dbo.Hospitals` | 124 | ✓ | — | — | ✓ |  |
| `dbo.OrdersProcedures` | 1,342,130 | ✓ | — | — | ✓ |  |
| `dbo.Patients` | 7,096 | ✓ | — | — | ✓ |  |
| `dbo.Physicians` | 10,000 | ✓ | — | — | ✓ |  |
| `dbo.Practices` | 1,000 | ✓ | — | — | ✓ |  |
| `dbo.QualityMeasureData` | 293,706 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Results` | 224,724 | ✓ | **55/55** | **104/104** | ✓ |  |
| `dbo.SurgicalCosts` | 211,233 | ✓ | — | — | ✓ |  |
| `dbo.SurgicalEncounters` | 9,403 | ✓ | — | — | ✓ |  |
| `dbo.Vitals` | 10,216 | ✓ | **9/9** | **18/18** | ✓ |  |

### `IndexInternals2008.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.427 MB · extracted in 1.365s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.EmployeeHeap` | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |

### `NYCTaxi_Sample.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB · extracted in 7.404s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ |  |

### `Pubs.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.5 MB · extracted in 0.085s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | 23 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.discounts` | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.employee` | 43 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.jobs` | 14 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.pub_info` | 8 | ✓ | **3/3** | **4/4** | ✓ |  |
| `dbo.publishers` | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.roysched` | 86 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.sales` | 21 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.stores` | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.titleauthor` | 25 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.titles` | 18 | ✓ | **10/10** | **20/20** | ✓ |  |

### `SalesDB2014.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 28.068 MB · extracted in 3.297s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |

### `SalesDBOriginal.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 192.081 MB · extracted in 3.352s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.sysdiagrams` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |

### `StackOverflowMini.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 758.564 MB · extracted in 36.935s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | 444,073 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Comments` | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.LinkTypes` | 2 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PostLinks` | 0 | — | — | — | — |  |
| `dbo.Posts` | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ |  |
| `dbo.PostTypes` | 8 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Users` | 99,869 | ✓ | **14/14** | **24/24** | ✓ |  |
| `dbo.Votes` | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.VoteTypes` | 15 | ✓ | **2/2** | **4/4** | ✓ |  |

### `TutorialDB.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.411 MB · extracted in 0.052s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | 453 | ✓ | **10/10** | **20/20** | ✓ |  |

### `WideWorldImporters-Full.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.223 MB · extracted in 16.942s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | 37 | ✓ | 13/14 ⚠ | 25/28 ⚠ | ✓ |  |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Application.People_Archive` | 961 | ✓ | **21/21** | 37/40 ⚠ | ✓ |  |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | 104 | ✓ | 9/10 ⚠ | 15/20 ⚠ | ✓ |  |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | 4 | ✗ | — | — | ✗ | missing from output |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | 9/12 ⚠ | ✓ |  |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | 34/46 ⚠ | ✓ |  |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | 10/11 ⚠ | 17/22 ⚠ | ✓ |  |
| `Warehouse.VehicleTemperatures` | 65,998 | ✗ | — | — | ✗ | missing from output |

### `WideWorldImporters-Full_old.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.171 MB · extracted in 16.572s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | 36 | ✓ | 13/14 ⚠ | 25/28 ⚠ | ✓ |  |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Application.People_Archive` | 961 | ✓ | **21/21** | 37/40 ⚠ | ✓ |  |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | 104 | ✓ | 9/10 ⚠ | 15/20 ⚠ | ✓ |  |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | 4 | ✗ | — | — | ✗ | missing from output |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | 9/12 ⚠ | ✓ |  |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | 34/46 ⚠ | ✓ |  |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | 10/11 ⚠ | 17/22 ⚠ | ✓ |  |
| `Warehouse.VehicleTemperatures` | 65,998 | ✗ | — | — | ✗ | missing from output |

### `WideWorldImporters-Standard.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.07 MB · extracted in 19.27s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | 37 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.VehicleTemperatures` | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

### `WideWorldImporters-Standard_old.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.058 MB · extracted in 18.856s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Countries` | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | 36 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.DeliveryMethods` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | 1,111 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Application.People_Archive` | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Application.StateProvinces` | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.SystemParameters` | 1 | ✓ | **13/13** | **24/24** | ✓ |  |
| `Application.TransactionTypes` | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Purchasing.SupplierCategories` | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.Suppliers` | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Purchasing.SupplierTransactions` | 2,438 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.BuyingGroups` | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.BuyingGroups_Archive` | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.Customers` | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Sales.CustomerTransactions` | 97,147 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.InvoiceLines` | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Sales.SpecialDeals` | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes` | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.PackageTypes_Archive` | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItems` | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Warehouse.StockItemStockGroups` | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.VehicleTemperatures` | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

### `WideWorldImportersDW-Full.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.726 MB · extracted in 7.782s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | 116,295 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Dimension.Customer` | 403 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Date` | 1,461 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Dimension.Employee` | 213 | ✓ | **2/2** | **2/2** | ✓ |  |
| `Dimension.Supplier` | 28 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Fact.Movement` | 236,667 | ✓ | **1/1** | 1/2 ⚠ | ✓ |  |
| `Fact.Order` | 231,412 | ✓ | **3/3** | 5/6 ⚠ | ✓ |  |
| `Fact.Purchase` | 8,367 | ✓ | **1/1** | **2/2** | ✓ |  |
| `Fact.Sale` | 228,265 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Fact.Transaction` | 99,585 | ✓ | — | — | ✓ |  |
| `Integration.City_Staging` | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | 0 | — | — | — | — |  |
| `Integration.Lineage` | 13 | ✓ | — | — | ✓ |  |
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

### `WideWorldImportersDW-Standard.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 51.37 MB · extracted in 5.405s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | 116,295 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Dimension.Customer` | 403 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Date` | 1,461 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Dimension.Employee` | 213 | ✓ | **2/2** | **2/2** | ✓ |  |
| `Dimension.Supplier` | 28 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Fact.Movement` | 236,667 | ✓ | **1/1** | **2/2** | ✓ |  |
| `Fact.Order` | 231,412 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Fact.Purchase` | 8,367 | ✓ | **1/1** | **2/2** | ✓ |  |
| `Fact.Sale` | 228,265 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Fact.Transaction` | 99,585 | ✓ | — | — | ✓ |  |
| `Integration.City_Staging` | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | 0 | — | — | — | — |  |
| `Integration.Lineage` | 13 | ✓ | — | — | ✓ |  |
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

### `data.gov.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.047 MB · extracted in 0.845s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | 150,482 | ✓ | **5/5** | **10/10** | ✓ |  |

### `dba.stackexchange.com.bak` — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 489.32 MB · extracted in 21.927s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | 416,662 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.Comments` | 340,158 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.PostHistory` | 814,930 | ✓ | **8/8** | **14/14** | ✓ |  |
| `dbo.PostLinks` | 24,460 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.Posts` | 238,555 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Tags` | 1,217 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.Users` | 240,423 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.Votes` | 892,171 | ✓ | **4/4** | **8/8** | ✓ |  |

### `tpcxbb_1gb.bak` — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 233.98 MB · extracted in 26.442s_

| Table | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | 99,000 | ✓ | 10/18 ⚠ | **36/36** | ✓ |  |
| `dbo.customer_address` | 49,500 | ✓ | 8/13 ⚠ | 25/26 ⚠ | ✓ |  |
| `dbo.customer_book_clusters` | 4,820 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_clusters` | 51,874 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_demographics` | 1,920,800 | ✓ | 4/9 ⚠ | 17/18 ⚠ | ✓ |  |
| `dbo.customer_return_clusters` | 37,336 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.date_dim` | 109,573 | ✓ | 27/28 ⚠ | 52/56 ⚠ | ✓ |  |
| `dbo.household_demographics` | 7,200 | ✓ | 3/5 ⚠ | 9/10 ⚠ | ✓ |  |
| `dbo.income_band` | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.inventory` | 23,255,100 | ✗ | 3/4 ⚠ | 6/8 ⚠ | ✓ |  |
| `dbo.item` | 17,820 | ✓ | 20/22 ⚠ | **42/42** | ✓ |  |
| `dbo.item_marketprices` | 89,100 | ✓ | 5/6 ⚠ | 11/12 ⚠ | ✓ |  |
| `dbo.product_reviews` | 89,991 | ✓ | 7/8 ⚠ | **16/16** | ✓ |  |
| `dbo.promotion` | 300 | ✓ | 18/19 ⚠ | **38/38** | ✓ |  |
| `dbo.reason` | 35 | ✓ | 2/3 ⚠ | **6/6** | ✓ |  |
| `dbo.ship_mode` | 20 | ✓ | 5/6 ⚠ | **12/12** | ✓ |  |
| `dbo.store` | 12 | ✓ | 28/29 ⚠ | **56/56** | ✓ |  |
| `dbo.store_returns` | 37,902 | ✓ | 19/20 ⚠ | **40/40** | ✓ |  |
| `dbo.store_sales` | 667,579 | ✓ | **23/23** | 45/46 ⚠ | ✓ |  |
| `dbo.time_dim` | 86,400 | ✓ | 9/10 ⚠ | **20/20** | ✓ |  |
| `dbo.warehouse` | 5 | ✓ | 12/14 ⚠ | **28/28** | ✓ |  |
| `dbo.web_clickstreams` | 6,770,550 | ✗ | 5/6 ⚠ | 11/12 ⚠ | ✓ |  |
| `dbo.web_page` | 60 | ✓ | 13/14 ⚠ | **26/26** | ✓ |  |
| `dbo.web_returns` | 38,487 | ✓ | 22/24 ⚠ | 47/48 ⚠ | ✓ |  |
| `dbo.web_sales` | 668,052 | ✓ | 29/34 ⚠ | 62/68 ⚠ | ✓ |  |
| `dbo.web_site` | 30 | ✓ | 24/26 ⚠ | **50/50** | ✓ |  |
| `sqlr.model_scoring_history` | 1 | ✓ | **9/9** | **16/16** | ✓ |  |
| `sqlr.model_training_history` | 8 | ✓ | **14/14** | **26/26** | ✓ |  |
| `sqlr.models` | 4 | ✓ | **11/11** | **22/22** | ✓ |  |
| `sqlr.scripts` | 1 | ✓ | **6/6** | **10/10** | ✓ |  |

---

_Generated 2026-06-11 · 45 fixtures · 37 pass · 0 xfail · 8 fail_
