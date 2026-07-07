# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld tests/fixtures_realworld/WideWorldImportersDW-Full.bak`.

**1 fixtures · 0 pass · 0 xfail (known gap) · 1 fail**

**Tables:** 23/24 pass · **Columns:** 50/50 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** 1 fail

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
| `WideWorldImportersDW-Full.bak` | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | 13604540/13606612 ⚠ | ✗ |

## Per-fixture detail

### `WideWorldImportersDW-Full.bak` — ✗ fail

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
| `Fact.Transaction` | 99,585 | ✓ | — | — | ✓ | cells ✗ (cells 1591288/1593360; bad: Supplier Invoice Number, digest:Supplier Invoice Number) |
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


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `WideWorldImportersDW-Full.bak` | 71.169s |

---

_Generated 2026-06-30 · 1 fixtures · 0 pass · 0 xfail · 1 fail_
