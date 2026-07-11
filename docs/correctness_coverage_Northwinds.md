# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/Northwinds.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 12/12 pass · **Columns:** 83/83 pass

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
| `Northwinds.bak` | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | **13005/13005** | ✓ |

## Per-fixture detail

### `Northwinds.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.816 MB_

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ | cells **24/24** ✓ |
| `dbo.CustomerCustomerDemo` | rowstore | 0 | — | — | — | — |  |
| `dbo.CustomerDemographics` | rowstore | 0 | — | — | — | — |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ | cells **910/910** ✓ |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ | cells **153/153** ✓ |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ | cells **10790/10790** ✓ |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ | cells **693/693** ✓ |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells **4/4** ✓ |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ | cells **319/319** ✓ |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ | cells **106/106** ✓ |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `Northwinds.bak` | 0.097s | 2.699s | 2.796s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

---

_Generated 2026-07-11 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
