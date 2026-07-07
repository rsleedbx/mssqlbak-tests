# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/GeneralHospital.bak`.

**1 fixtures · 1 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 13/13 pass · **Columns:** 67/67 pass

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
| `GeneralHospital.bak` | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |

## Per-fixture detail

### `GeneralHospital.bak` — ✓ pass

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
| `dbo.SurgicalCosts` | 211,233 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.SurgicalEncounters` | 9,403 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Vitals` | 10,216 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `GeneralHospital.bak` | 60.399s |

---

_Generated 2026-07-01 · 1 fixtures · 1 pass · 0 xfail · 0 fail_
