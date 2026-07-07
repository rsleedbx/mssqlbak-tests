# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/WideWorldImporters-Full.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 48/48 pass · **Columns:** 549/549 pass

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
| `WideWorldImporters-Full.bak` | 4,713,833 | 549 | **48/48** | **525/525** | **1004/1004** | **48/48** | **11936655/11936655** | ✓ |

## Per-fixture detail

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


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `WideWorldImporters-Full.bak` | 110.424s |

---

_Generated 2026-07-01 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
