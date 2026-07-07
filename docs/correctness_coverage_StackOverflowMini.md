# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage tests/fixtures_realworld/StackOverflowMini.bak`.

**1 fixtures · 0 pass · 0 xfail (known gap) · 1 fail**

**Tables:** 8/9 pass · **Columns:** 60/61 pass

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
| `StackOverflowMini.bak` | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | 8290987/8290987 ⚠ | ✗ |

## Per-fixture detail

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


## Extraction timings

| Backup | Wall time |
|--------|-------------|
| `StackOverflowMini.bak` | 146.991s |

---

_Generated 2026-07-01 · 1 fixtures · 0 pass · 0 xfail · 1 fail_
