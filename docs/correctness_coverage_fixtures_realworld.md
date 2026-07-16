# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld`.

**49 fixtures · 49 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 1445/1445 pass · **Columns:** 12619/12619 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** ✓

Column key:

| Column | Meaning |
|--------|----------|
| Stage | Pipeline edge being compared (e.g. mssql→arrow = extraction correctness) |
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

| Backup | Stage | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |
|--------|-------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|
| `AdventureWorks2008R2.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorks2008R2.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2008R2.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorks2008R2.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2008R2.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2012.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2012.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2014.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2014.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2016.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2016.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | mssql→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→delta | 1,378,717 | 732 | **89/89** | **701/701** | **1384/1384** | **89/89** | — | ✓ |
| `AdventureWorks2016_EXT.bak` | delta→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→pg_dir | 1,378,717 | 732 | **89/89** | **701/701** | 1378/1384 ⚠ | **89/89** | — | ✗ |
| `AdventureWorks2016_EXT.bak` | pg_dir→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | digest | ✓ |
| `AdventureWorks2017.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2017.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2017.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2017.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2017.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2019.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2019.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2022.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2022.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | mssql→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | arrow→delta | 760,167 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2025.bak` | delta→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | arrow→pg_dir | 760,167 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2025.bak` | pg_dir→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | mssql→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→delta | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | delta→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→pg_dir | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | pg_dir→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | digest | ✓ |
| `AdventureWorksDW2012.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2012.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2012.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2012.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2012.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2014.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2014.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2014.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2014.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2014.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2016.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2016.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2016.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2016.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2016.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2016_EXT.bak` | mssql→arrow | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | digest | ✓ |
| `AdventureWorksDW2016_EXT.bak` | arrow→delta | 24,400,096 | 413 | **33/33** | **414/414** | **816/816** | **33/33** | — | ✓ |
| `AdventureWorksDW2016_EXT.bak` | delta→arrow | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | digest | ✓ |
| `AdventureWorksDW2016_EXT.bak` | arrow→pg_dir | 24,400,096 | 413 | **33/33** | **414/414** | **816/816** | **33/33** | — | ✓ |
| `AdventureWorksDW2016_EXT.bak` | pg_dir→arrow | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | digest | ✓ |
| `AdventureWorksDW2017.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2017.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2017.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2017.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2017.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2019.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2019.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2019.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2019.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2019.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2022.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2022.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2022.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2022.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2022.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | digest | ✓ |
| `AdventureWorksDW2025.bak` | mssql→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | digest | ✓ |
| `AdventureWorksDW2025.bak` | arrow→delta | 1,047,563 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2025.bak` | delta→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | digest | ✓ |
| `AdventureWorksDW2025.bak` | arrow→pg_dir | 1,047,563 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2025.bak` | pg_dir→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | digest | ✓ |
| `AdventureWorksLT2012.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2012.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2012.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | digest | ✓ |
| `BaseballData.bak` | mssql→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | digest | ✓ |
| `BaseballData.bak` | arrow→delta | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | — | ✓ |
| `BaseballData.bak` | delta→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | digest | ✓ |
| `BaseballData.bak` | arrow→pg_dir | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | — | ✓ |
| `BaseballData.bak` | pg_dir→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | digest | ✓ |
| `Chinook-id-pk.bak` | mssql→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `Chinook-id-pk.bak` | arrow→delta | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook-id-pk.bak` | delta→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `Chinook-id-pk.bak` | arrow→pg_dir | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook-id-pk.bak` | pg_dir→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `Chinook.bak` | mssql→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `Chinook.bak` | arrow→delta | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook.bak` | delta→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `Chinook.bak` | arrow→pg_dir | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook.bak` | pg_dir→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | digest | ✓ |
| `ContosoRetailDW.bak` | mssql→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | digest | ✓ |
| `ContosoRetailDW.bak` | arrow→delta | 34,326,475 | 384 | **25/25** | **396/396** | **766/766** | **25/25** | — | ✓ |
| `ContosoRetailDW.bak` | delta→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | digest | ✓ |
| `ContosoRetailDW.bak` | arrow→pg_dir | 34,326,475 | 384 | **25/25** | **396/396** | **766/766** | **25/25** | — | ✓ |
| `ContosoRetailDW.bak` | pg_dir→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | digest | ✓ |
| `CreditBackup100.bak` | mssql→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | digest | ✓ |
| `CreditBackup100.bak` | arrow→delta | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | — | ✓ |
| `CreditBackup100.bak` | delta→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | digest | ✓ |
| `CreditBackup100.bak` | arrow→pg_dir | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | — | ✓ |
| `CreditBackup100.bak` | pg_dir→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | digest | ✓ |
| `data.gov.bak` | mssql→arrow | 150,482 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `data.gov.bak` | arrow→delta | 150,482 | 5 | **1/1** | **17/17** | **34/34** | **1/1** | — | ✓ |
| `data.gov.bak` | delta→arrow | 150,482 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `data.gov.bak` | arrow→pg_dir | 150,482 | 5 | **1/1** | **17/17** | **34/34** | **1/1** | — | ✓ |
| `data.gov.bak` | pg_dir→arrow | 150,482 | 5 | **1/1** | **5/5** | **10/10** | **1/1** | digest | ✓ |
| `dba.stackexchange.com.bak` | mssql→arrow | 2,968,576 | 63 | **8/8** | **63/63** | **122/122** | **8/8** | digest | ✓ |
| `dba.stackexchange.com.bak` | arrow→delta | 2,968,576 | 63 | **8/8** | **63/63** | **124/124** | **8/8** | — | ✓ |
| `dba.stackexchange.com.bak` | delta→arrow | 2,968,576 | 63 | **8/8** | **63/63** | **122/122** | **8/8** | digest | ✓ |
| `dba.stackexchange.com.bak` | arrow→pg_dir | 2,968,576 | 63 | **8/8** | **63/63** | **124/124** | **8/8** | — | ✓ |
| `dba.stackexchange.com.bak` | pg_dir→arrow | 2,968,576 | 63 | **8/8** | **63/63** | **122/122** | **8/8** | digest | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | mssql→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | digest | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | arrow→delta | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | — | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | delta→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | digest | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | arrow→pg_dir | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | — | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | pg_dir→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | digest | ✓ |
| `GeneralHospital.bak` | mssql→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `GeneralHospital.bak` | arrow→delta | 2,175,940 | 67 | **13/13** | **197/197** | **394/394** | **13/13** | — | ✓ |
| `GeneralHospital.bak` | delta→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `GeneralHospital.bak` | arrow→pg_dir | 2,175,940 | 67 | **13/13** | **197/197** | **394/394** | **13/13** | — | ✓ |
| `GeneralHospital.bak` | pg_dir→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `IndexInternals2008.bak` | mssql→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `IndexInternals2008.bak` | arrow→delta | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `IndexInternals2008.bak` | delta→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `IndexInternals2008.bak` | arrow→pg_dir | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `IndexInternals2008.bak` | pg_dir→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | digest | ✓ |
| `Northwinds.bak` | mssql→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | digest | ✓ |
| `Northwinds.bak` | arrow→delta | 1,153 | 83 | **11/11** | **84/84** | **168/168** | **11/11** | — | ✓ |
| `Northwinds.bak` | delta→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | digest | ✓ |
| `Northwinds.bak` | arrow→pg_dir | 1,153 | 83 | **11/11** | **84/84** | **168/168** | **11/11** | — | ✓ |
| `Northwinds.bak` | pg_dir→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | digest | ✓ |
| `NYCTaxi_Sample.bak` | mssql→arrow | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest | ✓ |
| `NYCTaxi_Sample.bak` | arrow→delta | 1,703,957 | 25 | **1/1** | **23/23** | **46/46** | **1/1** | — | ✓ |
| `NYCTaxi_Sample.bak` | delta→arrow | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest | ✓ |
| `NYCTaxi_Sample.bak` | arrow→pg_dir | 1,703,957 | 25 | **1/1** | **23/23** | **46/46** | **1/1** | — | ✓ |
| `NYCTaxi_Sample.bak` | pg_dir→arrow | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest | ✓ |
| `Pubs.bak` | mssql→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | digest | ✓ |
| `Pubs.bak` | arrow→delta | 255 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Pubs.bak` | delta→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | digest | ✓ |
| `Pubs.bak` | arrow→pg_dir | 255 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Pubs.bak` | pg_dir→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | digest | ✓ |
| `SalesDB2014.bak` | mssql→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `SalesDB2014.bak` | arrow→delta | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `SalesDB2014.bak` | delta→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `SalesDB2014.bak` | arrow→pg_dir | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `SalesDB2014.bak` | pg_dir→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | digest | ✓ |
| `SalesDBOriginal.bak` | mssql→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | digest | ✓ |
| `SalesDBOriginal.bak` | arrow→delta | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | — | ✓ |
| `SalesDBOriginal.bak` | delta→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | digest | ✓ |
| `SalesDBOriginal.bak` | arrow→pg_dir | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | — | ✓ |
| `SalesDBOriginal.bak` | pg_dir→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | digest | ✓ |
| `StackOverflowMini.bak` | mssql→arrow | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | digest | ✓ |
| `StackOverflowMini.bak` | arrow→delta | 8,097,337 | 61 | **8/8** | **56/56** | **108/108** | **8/8** | — | ✓ |
| `StackOverflowMini.bak` | delta→arrow | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | digest | ✓ |
| `StackOverflowMini.bak` | arrow→pg_dir | 8,097,337 | 61 | **8/8** | **56/56** | **108/108** | **8/8** | — | ✓ |
| `StackOverflowMini.bak` | pg_dir→arrow | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | digest | ✓ |
| `tpcxbb_1gb.bak` | mssql→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | digest | ✓ |
| `tpcxbb_1gb.bak` | arrow→delta | 34,001,580 | 394 | **30/30** | **394/394** | **776/776** | **30/30** | — | ✓ |
| `tpcxbb_1gb.bak` | delta→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | digest | ✓ |
| `tpcxbb_1gb.bak` | arrow→pg_dir | 34,001,580 | 394 | **30/30** | **394/394** | **776/776** | **30/30** | — | ✓ |
| `tpcxbb_1gb.bak` | pg_dir→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | digest | ✓ |
| `TutorialDB.bak` | mssql→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→delta | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | delta→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→pg_dir | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | pg_dir→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `WideWorldImporters-Full.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | pg_dir→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard_old.bak` | pg_dir→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImportersDW-Full.bak` | mssql→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |
| `WideWorldImportersDW-Full.bak` | arrow→delta | 922,709 | 50 | **16/16** | **194/194** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Full.bak` | delta→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |
| `WideWorldImportersDW-Full.bak` | arrow→pg_dir | 922,709 | 50 | **16/16** | **194/194** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Full.bak` | pg_dir→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |
| `WideWorldImportersDW-Standard.bak` | mssql→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |
| `WideWorldImportersDW-Standard.bak` | arrow→delta | 922,709 | 50 | **16/16** | **188/188** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Standard.bak` | delta→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |
| `WideWorldImportersDW-Standard.bak` | arrow→pg_dir | 922,709 | 50 | **16/16** | **188/188** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Standard.bak` | pg_dir→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | digest | ✓ |

## Per-fixture detail

### `AdventureWorks2008R2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 181.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.897 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.594 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 46.491 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2016_EXT.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | **26/26** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | **52/52** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | **26/26** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | **52/52** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `HumanResources.Employee_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | — | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `AdventureWorks2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.957 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 199.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 200.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorks2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 47.902 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **48/48** | ✓ |  |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | 6/8 ⚠ | ✓ |  |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **14/14** | ✓ |  |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ |  |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | 6/10 ⚠ | ✓ |  |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `HumanResources.Shift` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Person.Address` | rowstore | 19,614 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Person.AddressType` | rowstore | 6 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Person.BusinessEntity` | rowstore | 20,777 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `Person.BusinessEntityAddress` | rowstore | 19,614 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.BusinessEntityContact` | rowstore | 909 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.ContactType` | rowstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.CountryRegion` | rowstore | 238 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Password` | rowstore | 19,972 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | — | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | — | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.ProductSubcategory` | rowstore | 37 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Production.ScrapReason` | rowstore | 16 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.TransactionHistory` | rowstore | 113,443 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.TransactionHistoryArchive` | rowstore | 89,253 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.UnitMeasure` | rowstore | 38 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ProductVendor` | rowstore | 460 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.ShipMethod` | rowstore | 5 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | — | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2008R2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 74.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |

### `AdventureWorksDW2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.766 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.41 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.443 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2016_EXT.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 883.324 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **28/28** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **28/28** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactResellerSalesXL_PageCompressed` | rowstore | 11,669,638 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

### `AdventureWorksDW2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 22.351 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksDW2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 24.133 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ |  |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ |  |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells digest ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `AdventureWorksLT2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.426 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.336 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `AdventureWorksLT2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.684 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **30/30** | ✓ |  |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **32/32** | ✓ |  |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ |  |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **10/10** | ✓ |  |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells digest ✓ |

### `BaseballData.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 114.171 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells digest ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells digest ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells digest ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells digest ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells digest ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ |  |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ |  |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ |  |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ |  |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ |  |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ |  |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells digest ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells digest ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells digest ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells digest ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells digest ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ |  |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ |  |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ |  |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ |  |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ |  |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ |  |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells digest ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells digest ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells digest ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells digest ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells digest ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells digest ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

### `Chinook-id-pk.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.257 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

### `Chinook.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.098 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

### `ContosoRetailDW.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 629.956 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells digest ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells digest ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ |  |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **32/32** | **64/64** | ✓ |  |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **28/28** | **56/56** | ✓ |  |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **16/16** | **30/30** | ✓ |  |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **19/19** | **30/30** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ |  |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells digest ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells digest ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ |  |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **32/32** | **64/64** | ✓ |  |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ |  |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **28/28** | **56/56** | ✓ |  |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **16/16** | **30/30** | ✓ |  |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ |  |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **19/19** | **30/30** | ✓ |  |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ |  |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ |  |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells digest ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells digest ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells digest ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells digest ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 0 | — | — | — | — |  |

### `CreditBackup100.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 52.739 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ |  |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells digest ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `data.gov.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.047 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | rowstore | 150,482 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | rowstore | 150,482 | ✓ | **17/17** | **34/34** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | rowstore | 150,482 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | rowstore | 150,482 | ✓ | **17/17** | **34/34** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Electric_Vehicle_Population_Data` | rowstore | 150,482 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `dba.stackexchange.com.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 489.32 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | rowstore | 416,662 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 340,158 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostHistory` | rowstore | 814,930 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 24,460 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Posts` | rowstore | 238,555 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Tags` | rowstore | 1,217 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 240,423 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 892,171 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | rowstore | 416,662 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.Comments` | rowstore | 340,158 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.PostHistory` | rowstore | 814,930 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.PostLinks` | rowstore | 24,460 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.Posts` | rowstore | 238,555 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Tags` | rowstore | 1,217 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.Users` | rowstore | 240,423 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.Votes` | rowstore | 892,171 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | rowstore | 416,662 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 340,158 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostHistory` | rowstore | 814,930 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 24,460 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Posts` | rowstore | 238,555 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Tags` | rowstore | 1,217 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 240,423 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 892,171 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | rowstore | 416,662 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.Comments` | rowstore | 340,158 | ✓ | **7/7** | **14/14** | ✓ |  |
| `dbo.PostHistory` | rowstore | 814,930 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.PostLinks` | rowstore | 24,460 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.Posts` | rowstore | 238,555 | ✓ | **15/15** | **30/30** | ✓ |  |
| `dbo.Tags` | rowstore | 1,217 | ✓ | **6/6** | **10/10** | ✓ |  |
| `dbo.Users` | rowstore | 240,423 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.Votes` | rowstore | 892,171 | ✓ | **4/4** | **8/8** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badge` | rowstore | 416,662 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 340,158 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostHistory` | rowstore | 814,930 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 24,460 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Posts` | rowstore | 238,555 | ✓ | **15/15** | **30/30** | ✓ | cells digest ✓ |
| `dbo.Tags` | rowstore | 1,217 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 240,423 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 892,171 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |

### `EmployeeCaseStudySampleDB2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.293 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |

### `GeneralHospital.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 316.084 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | rowstore | 53,787 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Departments` | rowstore | 64 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Encounters` | rowstore | 12,457 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Hospitals` | rowstore | 124 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.OrdersProcedures` | rowstore | 1,342,130 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Patients` | rowstore | 7,096 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Physicians` | rowstore | 10,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Practices` | rowstore | 1,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.QualityMeasureData` | rowstore | 293,706 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Results` | rowstore | 224,724 | ✓ | **55/55** | **104/104** | ✓ | cells digest ✓ |
| `dbo.SurgicalCosts` | rowstore | 211,233 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.SurgicalEncounters` | rowstore | 9,403 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Vitals` | rowstore | 10,216 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | rowstore | 53,787 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.Departments` | rowstore | 64 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Encounters` | rowstore | 12,457 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.Hospitals` | rowstore | 124 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.OrdersProcedures` | rowstore | 1,342,130 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.Patients` | rowstore | 7,096 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.Physicians` | rowstore | 10,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Practices` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.QualityMeasureData` | rowstore | 293,706 | ✓ | **22/22** | **44/44** | ✓ |  |
| `dbo.Results` | rowstore | 224,724 | ✓ | **63/63** | **126/126** | ✓ |  |
| `dbo.SurgicalCosts` | rowstore | 211,233 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.SurgicalEncounters` | rowstore | 9,403 | ✓ | **17/17** | **34/34** | ✓ |  |
| `dbo.Vitals` | rowstore | 10,216 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | rowstore | 53,787 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Departments` | rowstore | 64 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Encounters` | rowstore | 12,457 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Hospitals` | rowstore | 124 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.OrdersProcedures` | rowstore | 1,342,130 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Patients` | rowstore | 7,096 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Physicians` | rowstore | 10,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Practices` | rowstore | 1,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.QualityMeasureData` | rowstore | 293,706 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Results` | rowstore | 224,724 | ✓ | **55/55** | **104/104** | ✓ | cells digest ✓ |
| `dbo.SurgicalCosts` | rowstore | 211,233 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.SurgicalEncounters` | rowstore | 9,403 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Vitals` | rowstore | 10,216 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | rowstore | 53,787 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.Departments` | rowstore | 64 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Encounters` | rowstore | 12,457 | ✓ | **16/16** | **32/32** | ✓ |  |
| `dbo.Hospitals` | rowstore | 124 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.OrdersProcedures` | rowstore | 1,342,130 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.Patients` | rowstore | 7,096 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.Physicians` | rowstore | 10,000 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Practices` | rowstore | 1,000 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.QualityMeasureData` | rowstore | 293,706 | ✓ | **22/22** | **44/44** | ✓ |  |
| `dbo.Results` | rowstore | 224,724 | ✓ | **63/63** | **126/126** | ✓ |  |
| `dbo.SurgicalCosts` | rowstore | 211,233 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.SurgicalEncounters` | rowstore | 9,403 | ✓ | **17/17** | **34/34** | ✓ |  |
| `dbo.Vitals` | rowstore | 10,216 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Accounts` | rowstore | 53,787 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Departments` | rowstore | 64 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Encounters` | rowstore | 12,457 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Hospitals` | rowstore | 124 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.OrdersProcedures` | rowstore | 1,342,130 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Patients` | rowstore | 7,096 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Physicians` | rowstore | 10,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Practices` | rowstore | 1,000 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.QualityMeasureData` | rowstore | 293,706 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Results` | rowstore | 224,724 | ✓ | **55/55** | **104/104** | ✓ | cells digest ✓ |
| `dbo.SurgicalCosts` | rowstore | 211,233 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.SurgicalEncounters` | rowstore | 9,403 | ✓ | — | — | ✓ | cells digest ✓ |
| `dbo.Vitals` | rowstore | 10,216 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |

### `IndexInternals2008.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.427 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |

### `Northwinds.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.816 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.CustomerCustomerDemo` | rowstore | 0 | — | — | — | — |  |
| `dbo.CustomerDemographics` | rowstore | 0 | — | — | — | — |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.Order Details` | rowstore | 2,155 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.CustomerCustomerDemo` | rowstore | 0 | — | — | — | — |  |
| `dbo.CustomerDemographics` | rowstore | 0 | — | — | — | — |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.Order Details` | rowstore | 2,155 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Categories` | rowstore | 8 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.CustomerCustomerDemo` | rowstore | 0 | — | — | — | — |  |
| `dbo.CustomerDemographics` | rowstore | 0 | — | — | — | — |  |
| `dbo.Customers` | rowstore | 91 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 9 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.EmployeeTerritories` | rowstore | 49 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Orders` | rowstore | 830 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 77 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.Region` | rowstore | 4 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Shippers` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Suppliers` | rowstore | 29 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Territories` | rowstore | 53 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |

### `NYCTaxi_Sample.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |

### `Pubs.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.5 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells digest ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

### `SalesDB2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 28.068 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `SalesDBOriginal.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 192.081 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |

### `StackOverflowMini.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 758.564 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells digest ✓ |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ |  |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells digest ✓ |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ |  |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells digest ✓ |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells digest ✓ |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `tpcxbb_1gb.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 233.98 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.customer_address` | columnstore | 49,500 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | columnstore | 109,573 | ✓ | **28/28** | **56/56** | ✓ | cells digest ✓ |
| `dbo.household_demographics` | columnstore | 7,200 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.income_band` | columnstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.inventory` | columnstore | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.item` | columnstore | 17,820 | ✓ | **22/22** | **42/42** | ✓ | cells digest ✓ |
| `dbo.item_marketprices` | columnstore | 89,100 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.product_reviews` | columnstore | 89,991 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.promotion` | columnstore | 300 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.reason` | columnstore | 35 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ship_mode` | columnstore | 20 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.store` | columnstore | 12 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `dbo.store_returns` | columnstore | 37,902 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.store_sales` | columnstore | 667,579 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |
| `dbo.time_dim` | columnstore | 86,400 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.warehouse` | columnstore | 5 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.web_page` | columnstore | 60 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `dbo.web_returns` | columnstore | 38,487 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.web_sales` | columnstore | 668,052 | ✓ | **34/34** | **68/68** | ✓ | cells digest ✓ |
| `dbo.web_site` | columnstore | 30 | ✓ | **26/26** | **50/50** | ✓ | cells digest ✓ |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.customer_address` | columnstore | 49,500 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.date_dim` | columnstore | 109,573 | ✓ | **28/28** | **56/56** | ✓ |  |
| `dbo.household_demographics` | columnstore | 7,200 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.income_band` | columnstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.inventory` | columnstore | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.item` | columnstore | 17,820 | ✓ | **22/22** | **42/42** | ✓ |  |
| `dbo.item_marketprices` | columnstore | 89,100 | ✓ | **6/6** | **12/12** | ✓ |  |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ |  |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ |  |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.product_reviews` | columnstore | 89,991 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.promotion` | columnstore | 300 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.reason` | columnstore | 35 | ✓ | **3/3** | **6/6** | ✓ |  |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.ship_mode` | columnstore | 20 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.store` | columnstore | 12 | ✓ | **29/29** | **56/56** | ✓ |  |
| `dbo.store_returns` | columnstore | 37,902 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.store_sales` | columnstore | 667,579 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.time_dim` | columnstore | 86,400 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.warehouse` | columnstore | 5 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.web_page` | columnstore | 60 | ✓ | **14/14** | **26/26** | ✓ |  |
| `dbo.web_returns` | columnstore | 38,487 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.web_sales` | columnstore | 668,052 | ✓ | **34/34** | **68/68** | ✓ |  |
| `dbo.web_site` | columnstore | 30 | ✓ | **26/26** | **50/50** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.customer_address` | columnstore | 49,500 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | columnstore | 109,573 | ✓ | **28/28** | **56/56** | ✓ | cells digest ✓ |
| `dbo.household_demographics` | columnstore | 7,200 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.income_band` | columnstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.inventory` | columnstore | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.item` | columnstore | 17,820 | ✓ | **22/22** | **42/42** | ✓ | cells digest ✓ |
| `dbo.item_marketprices` | columnstore | 89,100 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.product_reviews` | columnstore | 89,991 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.promotion` | columnstore | 300 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.reason` | columnstore | 35 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ship_mode` | columnstore | 20 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.store` | columnstore | 12 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `dbo.store_returns` | columnstore | 37,902 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.store_sales` | columnstore | 667,579 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |
| `dbo.time_dim` | columnstore | 86,400 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.warehouse` | columnstore | 5 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.web_page` | columnstore | 60 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `dbo.web_returns` | columnstore | 38,487 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.web_sales` | columnstore | 668,052 | ✓ | **34/34** | **68/68** | ✓ | cells digest ✓ |
| `dbo.web_site` | columnstore | 30 | ✓ | **26/26** | **50/50** | ✓ | cells digest ✓ |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✓ | **18/18** | **36/36** | ✓ |  |
| `dbo.customer_address` | columnstore | 49,500 | ✓ | **13/13** | **26/26** | ✓ |  |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.date_dim` | columnstore | 109,573 | ✓ | **28/28** | **56/56** | ✓ |  |
| `dbo.household_demographics` | columnstore | 7,200 | ✓ | **5/5** | **10/10** | ✓ |  |
| `dbo.income_band` | columnstore | 20 | ✓ | **3/3** | **6/6** | ✓ |  |
| `dbo.inventory` | columnstore | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.item` | columnstore | 17,820 | ✓ | **22/22** | **42/42** | ✓ |  |
| `dbo.item_marketprices` | columnstore | 89,100 | ✓ | **6/6** | **12/12** | ✓ |  |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ |  |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ |  |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ |  |
| `dbo.product_reviews` | columnstore | 89,991 | ✓ | **8/8** | **16/16** | ✓ |  |
| `dbo.promotion` | columnstore | 300 | ✓ | **19/19** | **38/38** | ✓ |  |
| `dbo.reason` | columnstore | 35 | ✓ | **3/3** | **6/6** | ✓ |  |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.ship_mode` | columnstore | 20 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.store` | columnstore | 12 | ✓ | **29/29** | **56/56** | ✓ |  |
| `dbo.store_returns` | columnstore | 37,902 | ✓ | **20/20** | **40/40** | ✓ |  |
| `dbo.store_sales` | columnstore | 667,579 | ✓ | **23/23** | **46/46** | ✓ |  |
| `dbo.time_dim` | columnstore | 86,400 | ✓ | **10/10** | **20/20** | ✓ |  |
| `dbo.warehouse` | columnstore | 5 | ✓ | **14/14** | **28/28** | ✓ |  |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.web_page` | columnstore | 60 | ✓ | **14/14** | **26/26** | ✓ |  |
| `dbo.web_returns` | columnstore | 38,487 | ✓ | **24/24** | **48/48** | ✓ |  |
| `dbo.web_sales` | columnstore | 668,052 | ✓ | **34/34** | **68/68** | ✓ |  |
| `dbo.web_site` | columnstore | 30 | ✓ | **26/26** | **50/50** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✓ | **18/18** | **36/36** | ✓ | cells digest ✓ |
| `dbo.customer_address` | columnstore | 49,500 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | columnstore | 109,573 | ✓ | **28/28** | **56/56** | ✓ | cells digest ✓ |
| `dbo.household_demographics` | columnstore | 7,200 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.income_band` | columnstore | 20 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.inventory` | columnstore | 23,255,100 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.item` | columnstore | 17,820 | ✓ | **22/22** | **42/42** | ✓ | cells digest ✓ |
| `dbo.item_marketprices` | columnstore | 89,100 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.product_reviews` | columnstore | 89,991 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.promotion` | columnstore | 300 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.reason` | columnstore | 35 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.ship_mode` | columnstore | 20 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.store` | columnstore | 12 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `dbo.store_returns` | columnstore | 37,902 | ✓ | **20/20** | **40/40** | ✓ | cells digest ✓ |
| `dbo.store_sales` | columnstore | 667,579 | ✓ | **23/23** | **46/46** | ✓ | cells digest ✓ |
| `dbo.time_dim` | columnstore | 86,400 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.warehouse` | columnstore | 5 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.web_page` | columnstore | 60 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `dbo.web_returns` | columnstore | 38,487 | ✓ | **24/24** | **48/48** | ✓ | cells digest ✓ |
| `dbo.web_sales` | columnstore | 668,052 | ✓ | **34/34** | **68/68** | ✓ | cells digest ✓ |
| `dbo.web_site` | columnstore | 30 | ✓ | **26/26** | **50/50** | ✓ | cells digest ✓ |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells digest ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |

### `TutorialDB.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 0.411 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | rowstore | 453 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | rowstore | 453 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | rowstore | 453 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | rowstore | 453 | ✓ | **10/10** | **20/20** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.rental_data` | rowstore | 453 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |

### `WideWorldImporters-Full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.223 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

### `WideWorldImporters-Full_old.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.171 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

### `WideWorldImporters-Standard.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.07 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

### `WideWorldImporters-Standard_old.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.058 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ |  |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ |  |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ |  |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ |  |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ |  |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ |  |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ |  |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **15/15** | **30/30** | ✓ |  |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ |  |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ |  |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells digest ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells digest ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells digest ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells digest ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells digest ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells digest ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells digest ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |

### `WideWorldImportersDW-Full.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.726 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | columnstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | memory-optimized | 0 | — | — | — | — |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Dimension.Customer` | rowstore | 403 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Integration.ETL Cutoff` | rowstore | 14 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Employee` | rowstore | 213 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Fact.Order` | columnstore | 231,412 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **22/22** | **42/42** | ✓ |  |
| `Fact.Stock Holding` | columnstore | 227 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | columnstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | memory-optimized | 0 | — | — | — | — |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Dimension.Customer` | rowstore | 403 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Integration.ETL Cutoff` | rowstore | 14 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Employee` | rowstore | 213 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Fact.Order` | columnstore | 231,412 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **12/12** | **22/22** | ✓ |  |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **22/22** | **42/42** | ✓ |  |
| `Fact.Stock Holding` | columnstore | 227 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | **19/19** | **36/36** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | columnstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | memory-optimized | 0 | — | — | — | — |  |

### `WideWorldImportersDW-Standard.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 51.37 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Dimension.Customer` | rowstore | 403 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Integration.ETL Cutoff` | rowstore | 14 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Employee` | rowstore | 213 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Order` | rowstore | 231,412 | ✓ | **19/19** | **38/38** | ✓ |  |
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **21/21** | **42/42** | ✓ |  |
| `Fact.Stock Holding` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | **18/18** | **36/36** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | rowstore | 0 | — | — | — | — |  |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Dimension.Customer` | rowstore | 403 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **14/14** | **28/28** | ✓ |  |
| `Integration.ETL Cutoff` | rowstore | 14 | ✓ | **2/2** | **4/4** | ✓ |  |
| `Dimension.Employee` | rowstore | 213 | ✓ | **9/9** | **16/16** | ✓ |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Order` | rowstore | 231,412 | ✓ | **19/19** | **38/38** | ✓ |  |
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **21/21** | **42/42** | ✓ |  |
| `Fact.Stock Holding` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | **18/18** | **36/36** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells digest ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells digest ✓ |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells digest ✓ |
| `Integration.Movement_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Order_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.PaymentMethod_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Purchase_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Sale_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockHolding_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.StockItem_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Supplier_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Transaction_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.TransactionType_Staging` | rowstore | 0 | — | — | — | — |  |


## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `AdventureWorks2008R2.bak` | 19.832s | 15.074s | 34.906s |
| `AdventureWorks2012.bak` | 34.677s | 23.464s | 58.141s |
| `AdventureWorks2014.bak` | 34.44s | 24.35s | 58.79s |
| `AdventureWorks2016.bak` | 34.076s | 23.469s | 57.545s |
| `AdventureWorks2016_EXT.bak` | 57.901s | 32.602s | 90.503s |
| `AdventureWorks2017.bak` | 33.928s | 24.8s | 58.728s |
| `AdventureWorks2019.bak` | 20.238s | 15.42s | 35.658s |
| `AdventureWorks2022.bak` | 26.575s | 19.787s | 46.362s |
| `AdventureWorks2025.bak` | 36.62s | 25.047s | 61.667s |
| `AdventureWorksDW2008R2.bak` | 4.1s | 6.017s | 10.117s |
| `AdventureWorksDW2012.bak` | 11.315s | 18.956s | 30.271s |
| `AdventureWorksDW2014.bak` | 11.619s | 19.985s | 31.604s |
| `AdventureWorksDW2016.bak` | 12.439s | 20.175s | 32.614s |
| `AdventureWorksDW2016_EXT.bak` | 91.537s | 66.204s | 157.741s |
| `AdventureWorksDW2017.bak` | 11.233s | 18.367s | 29.6s |
| `AdventureWorksDW2019.bak` | 9.287s | 18.129s | 27.416s |
| `AdventureWorksDW2022.bak` | 8.537s | 14.158s | 22.695s |
| `AdventureWorksDW2025.bak` | 11.137s | 19.429s | 30.566s |
| `AdventureWorksLT2012.bak` | 0.657s | 0.788s | 1.445s |
| `AdventureWorksLT2014.bak` | 0.652s | 1.135s | 1.787s |
| `AdventureWorksLT2016.bak` | 0.813s | 0.945s | 1.758s |
| `AdventureWorksLT2017.bak` | 0.601s | 0.788s | 1.389s |
| `AdventureWorksLT2019.bak` | 1.018s | 0.863s | 1.881s |
| `AdventureWorksLT2022.bak` | 0.697s | 0.985s | 1.682s |
| `AdventureWorksLT2025.bak` | 0.816s | 0.885s | 1.701s |
| `BaseballData.bak` | 16.997s | 7.991s | 24.988s |
| `Chinook-id-pk.bak` | 0.511s | 0.706s | 1.217s |
| `Chinook.bak` | 0.44s | 0.651s | 1.091s |
| `ContosoRetailDW.bak` | 272.737s | 386.457s | 659.194s |
| `CreditBackup100.bak` | 49.376s | 54.056s | 103.432s |
| `data.gov.bak` | 4.909s | 4.27s | 9.179s |
| `dba.stackexchange.com.bak` | 51.954s | 119.746s | 171.7s |
| `EmployeeCaseStudySampleDB2012.bak` | 7.774s | 5.147s | 12.921s |
| `GeneralHospital.bak` | 55.25s | 45.548s | 100.798s |
| `IndexInternals2008.bak` | 4.213s | 2.501s | 6.714s |
| `Northwinds.bak` | 0.572s | 0.636s | 1.208s |
| `NYCTaxi_Sample.bak` | 74.503s | 95.678s | 170.181s |
| `Pubs.bak` | 0.47s | 0.453s | 0.923s |
| `SalesDB2014.bak` | 15.992s | 22.857s | 38.849s |
| `SalesDBOriginal.bak` | 11.278s | 15.201s | 26.479s |
| `StackOverflowMini.bak` | 74.491s | 183.526s | 258.017s |
| `tpcxbb_1gb.bak` | 220.287s | 164.705s | 384.992s |
| `TutorialDB.bak` | 0.244s | 0.107s | 0.351s |
| `WideWorldImporters-Full.bak` | 75.066s | 64.482s | 139.548s |
| `WideWorldImporters-Full_old.bak` | 68.766s | 63.516s | 132.282s |
| `WideWorldImporters-Standard.bak` | 64.494s | 69.859s | 134.353s |
| `WideWorldImporters-Standard_old.bak` | 62.456s | 64.018s | 126.474s |
| `WideWorldImportersDW-Full.bak` | 19.504s | 17.337s | 36.841s |
| `WideWorldImportersDW-Standard.bak` | 16.656s | 15.76s | 32.416s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis). See **Sink read breakdown** below for the per-phase split._

## Extract phase breakdown

| Backup | pagestore | schema | catalog | constraints | logtail | xtp | data decode (net) | sink write | arrow verify | sink finish |
|--------|----------:|-------:|--------:|------------:|--------:|---:|------------------:|-----------:|-------------:|------------:|
| `AdventureWorks2008R2.bak` | 0.454s | 0.051s | 0.0s | 0.0s | 0.239s | 0.0s | 18.295s | 3.238s | 6.53s | 0.698s |
| `AdventureWorks2012.bak` | 2.926s | 0.109s | 0.0s | 0.0s | 0.079s | 0.0s | 30.491s | 4.999s | 10.689s | 1.061s |
| `AdventureWorks2014.bak` | 2.964s | 0.15s | 0.0s | 0.0s | 0.087s | 0.0s | 29.958s | 4.566s | 10.692s | 1.267s |
| `AdventureWorks2016.bak` | 3.049s | 0.131s | 0.0s | 0.0s | 0.096s | 0.0s | 29.715s | 4.935s | 10.333s | 1.074s |
| `AdventureWorks2016_EXT.bak` | 7.252s | 0.089s | 0.0s | 0.0s | 0.147s | 14.737s | 34.629s | 5.717s | 14.058s | 1.009s |
| `AdventureWorks2017.bak` | 3.054s | 0.16s | 0.0s | 0.0s | 0.105s | 0.0s | 29.528s | 4.43s | 10.57s | 1.062s |
| `AdventureWorks2019.bak` | 0.463s | 0.067s | 0.0s | 0.0s | 0.264s | 0.0s | 18.632s | 3.453s | 6.789s | 0.709s |
| `AdventureWorks2022.bak` | 0.562s | 0.109s | 0.0s | 0.0s | 0.337s | 0.0s | 24.474s | 3.879s | 8.865s | 0.953s |
| `AdventureWorks2025.bak` | 3.14s | 0.168s | 0.0s | 0.0s | 0.07s | 0.0s | 31.901s | 4.762s | 11.06s | 1.324s |
| `AdventureWorksDW2008R2.bak` | 0.204s | 0.028s | 0.0s | 0.0s | 0.112s | 0.0s | 3.674s | 1.186s | 2.684s | 0.034s |
| `AdventureWorksDW2012.bak` | 1.346s | 0.069s | 0.0s | 0.0s | 0.043s | 0.0s | 9.789s | 3.193s | 7.796s | 0.05s |
| `AdventureWorksDW2014.bak` | 1.168s | 0.075s | 0.0s | 0.0s | 0.044s | 0.0s | 10.31s | 2.855s | 8.278s | 0.012s |
| `AdventureWorksDW2016.bak` | 1.525s | 0.098s | 0.0s | 0.0s | 0.058s | 0.0s | 10.722s | 3.256s | 8.557s | 0.019s |
| `AdventureWorksDW2016_EXT.bak` | 15.861s | 0.033s | 0.0s | 0.0s | 0.662s | 0.0s | 74.959s | 68.251s | 3.406s | 0.015s |
| `AdventureWorksDW2017.bak` | 1.525s | 0.077s | 0.0s | 0.0s | 0.034s | 0.0s | 9.573s | 2.524s | 7.681s | 0.011s |
| `AdventureWorksDW2019.bak` | 0.274s | 0.056s | 0.0s | 0.0s | 0.153s | 0.0s | 8.733s | 2.366s | 7.028s | 0.012s |
| `AdventureWorksDW2022.bak` | 0.304s | 0.09s | 0.0s | 0.0s | 0.209s | 0.0s | 7.84s | 2.028s | 6.35s | 0.008s |
| `AdventureWorksDW2025.bak` | 1.444s | 0.111s | 0.0s | 0.0s | 0.035s | 0.0s | 9.521s | 2.957s | 7.662s | 0.012s |
| `AdventureWorksLT2012.bak` | 0.027s | 0.059s | 0.0s | 0.0s | 0.039s | 0.0s | 0.49s | 0.303s | 0.322s | 0.027s |
| `AdventureWorksLT2014.bak` | 0.027s | 0.063s | 0.0s | 0.0s | 0.039s | 0.0s | 0.459s | 0.33s | 0.284s | 0.049s |
| `AdventureWorksLT2016.bak` | 0.031s | 0.067s | 0.0s | 0.0s | 0.019s | 0.0s | 0.645s | 0.525s | 0.323s | 0.034s |
| `AdventureWorksLT2017.bak` | 0.03s | 0.066s | 0.0s | 0.0s | 0.019s | 0.0s | 0.455s | 0.275s | 0.309s | 0.015s |
| `AdventureWorksLT2019.bak` | 0.037s | 0.072s | 0.0s | 0.0s | 0.037s | 0.0s | 0.817s | 0.671s | 0.382s | 0.04s |
| `AdventureWorksLT2022.bak` | 0.038s | 0.092s | 0.0s | 0.0s | 0.018s | 0.0s | 0.502s | 0.357s | 0.301s | 0.029s |
| `AdventureWorksLT2025.bak` | 0.162s | 0.084s | 0.0s | 0.0s | 0.009s | 0.0s | 0.512s | 0.352s | 0.303s | 0.037s |
| `BaseballData.bak` | 0.168s | 0.067s | 0.0s | 0.0s | 0.268s | 0.0s | 16.402s | 2.596s | 3.06s | 0.011s |
| `Chinook-id-pk.bak` | 0.04s | 0.093s | 0.0s | 0.0s | 0.052s | 0.0s | 0.274s | 0.187s | 0.225s | 0.022s |
| `Chinook.bak` | 0.026s | 0.081s | 0.0s | 0.0s | 0.013s | 0.0s | 0.272s | 0.181s | 0.221s | 0.029s |
| `ContosoRetailDW.bak` | 16.44s | 0.025s | 0.0s | 0.0s | 0.68s | 0.0s | 255.583s | 62.118s | 200.976s | 0.001s |
| `CreditBackup100.bak` | 2.14s | 0.025s | 0.0s | 0.0s | 0.093s | 0.0s | 47.101s | 5.929s | 23.003s | 0.008s |
| `data.gov.bak` | 0.909s | 0.063s | 0.0s | 0.0s | 0.025s | 0.0s | 2.609s | 1.317s | 1.215s | 1.292s |
| `dba.stackexchange.com.bak` | 13.051s | 0.025s | 0.0s | 0.0s | 0.363s | 0.0s | 37.038s | 14.478s | 17.157s | 1.47s |
| `EmployeeCaseStudySampleDB2012.bak` | 1.091s | 0.051s | 0.0s | 0.0s | 0.026s | 0.0s | 5.779s | 0.958s | 1.516s | 0.818s |
| `GeneralHospital.bak` | 0.765s | 0.039s | 0.0s | 0.0s | 0.412s | 0.0s | 53.452s | 15.573s | 13.258s | 0.219s |
| `IndexInternals2008.bak` | 0.772s | 0.023s | 0.0s | 0.0s | 0.018s | 0.0s | 3.043s | 0.617s | 0.689s | 0.346s |
| `Northwinds.bak` | 0.113s | 0.066s | 0.0s | 0.0s | 0.005s | 0.0s | 0.346s | 0.222s | 0.223s | 0.025s |
| `NYCTaxi_Sample.bak` | 0.284s | 0.041s | 0.0s | 0.0s | 0.145s | 0.0s | 31.351s | 12.995s | 40.903s | 42.62s |
| `Pubs.bak` | 0.072s | 0.062s | 0.0s | 0.0s | 0.007s | 0.0s | 0.301s | 0.181s | 0.238s | 0.017s |
| `SalesDB2014.bak` | 1.318s | 0.045s | 0.0s | 0.0s | 0.045s | 0.0s | 4.279s | 4.871s | 10.341s | 10.298s |
| `SalesDBOriginal.bak` | 0.454s | 0.008s | 0.0s | 0.0s | 0.222s | 0.0s | 10.397s | 3.481s | 7.439s | 0.004s |
| `StackOverflowMini.bak` | 17.494s | 0.029s | 0.0s | 0.0s | 0.567s | 0.0s | 48.682s | 24.159s | 41.842s | 7.71s |
| `tpcxbb_1gb.bak` | 6.601s | 0.078s | 0.0s | 0.0s | 0.397s | 0.0s | 212.573s | 33.744s | 92.749s | 0.629s |
| `TutorialDB.bak` | 0.067s | 0.053s | 0.0s | 0.0s | 0.005s | 0.0s | 0.002s | 0.066s | 0.099s | 0.103s |
| `WideWorldImporters-Full.bak` | 7.499s | 0.088s | 0.0s | 0.0s | 0.19s | 9.51s | 57.374s | 10.877s | 34.489s | 0.386s |
| `WideWorldImporters-Full_old.bak` | 5.884s | 0.065s | 0.0s | 0.0s | 0.158s | 7.738s | 54.436s | 9.725s | 32.877s | 0.465s |
| `WideWorldImporters-Standard.bak` | 6.045s | 0.072s | 0.0s | 0.0s | 0.179s | 0.0s | 57.734s | 9.434s | 32.467s | 0.455s |
| `WideWorldImporters-Standard_old.bak` | 6.289s | 0.072s | 0.0s | 0.0s | 0.181s | 0.0s | 55.532s | 9.795s | 31.598s | 0.373s |
| `WideWorldImportersDW-Full.bak` | 2.586s | 0.072s | 0.0s | 0.0s | 0.073s | 2.299s | 14.462s | 2.787s | 7.897s | 0.002s |
| `WideWorldImportersDW-Standard.bak` | 2.772s | 0.058s | 0.0s | 0.0s | 0.079s | 0.0s | 13.736s | 2.511s | 7.7s | 0.002s |

_data decode (net) = data\_decode\_s (raw loop wall; sink writes and arrow verify overlap decode on a background writer thread and are drained in sink finish). catalog = recover\_catalog\_objects (indexes/FKs/constraints, pg\_dir only). arrow verify = cell verification run inside extraction (_StreamingStatsSink). verify=digest: per-column SHA-256 aggregate hash — fast, no GT parquet read, catches multiset-level corruption; also runs key-ordered digest (catches row transposition) when ordered\_digest is present in the manifest (populated by backfill\_ordered\_digest). Mismatches show as digest:col (multiset) or order:col (transposition). verify=full: exhaustive keyed row compare — also catches value-preserving row misalignment._

## Sink write timings

| Backup | delta write | delta read | pg_dir write | pg_dir read |
|--------|-------:| ------: | -------:| ------:|
| `AdventureWorks2008R2.bak` | 0.774s | 6.915s | 2.464s | 8.067s |
| `AdventureWorks2012.bak` | 1.387s | 10.732s | 3.612s | 12.561s |
| `AdventureWorks2014.bak` | 1.442s | 11.101s | 3.124s | 13.075s |
| `AdventureWorks2016.bak` | 1.35s | 11.01s | 3.585s | 12.276s |
| `AdventureWorks2016_EXT.bak` | 1.674s | 13.905s | 4.043s | 18.547s |
| `AdventureWorks2017.bak` | 1.308s | 11.435s | 3.122s | 12.945s |
| `AdventureWorks2019.bak` | 0.812s | 6.888s | 2.641s | 8.443s |
| `AdventureWorks2022.bak` | 1.026s | 9.627s | 2.853s | 10.038s |
| `AdventureWorks2025.bak` | 1.486s | 11.29s | 3.276s | 13.505s |
| `AdventureWorksDW2008R2.bak` | 0.405s | 2.696s | 0.781s | 3.26s |
| `AdventureWorksDW2012.bak` | 1.143s | 8.785s | 2.05s | 10.002s |
| `AdventureWorksDW2014.bak` | 1.158s | 8.696s | 1.697s | 11.19s |
| `AdventureWorksDW2016.bak` | 1.515s | 8.604s | 1.741s | 11.436s |
| `AdventureWorksDW2016_EXT.bak` | 23.48s | 8.023s | 44.771s | 58.023s |
| `AdventureWorksDW2017.bak` | 0.991s | 7.68s | 1.533s | 10.579s |
| `AdventureWorksDW2019.bak` | 0.821s | 6.768s | 1.545s | 11.255s |
| `AdventureWorksDW2022.bak` | 0.729s | 5.983s | 1.299s | 8.071s |
| `AdventureWorksDW2025.bak` | 1.137s | 8.316s | 1.82s | 11.002s |
| `AdventureWorksLT2012.bak` | 0.166s | 0.353s | 0.137s | 0.367s |
| `AdventureWorksLT2014.bak` | 0.18s | 0.616s | 0.15s | 0.429s |
| `AdventureWorksLT2016.bak` | 0.391s | 0.451s | 0.134s | 0.431s |
| `AdventureWorksLT2017.bak` | 0.168s | 0.341s | 0.107s | 0.383s |
| `AdventureWorksLT2019.bak` | 0.422s | 0.411s | 0.249s | 0.391s |
| `AdventureWorksLT2022.bak` | 0.264s | 0.433s | 0.093s | 0.478s |
| `AdventureWorksLT2025.bak` | 0.227s | 0.379s | 0.125s | 0.414s |
| `BaseballData.bak` | 0.536s | 3.322s | 2.06s | 4.604s |
| `Chinook-id-pk.bak` | 0.14s | 0.336s | 0.047s | 0.301s |
| `Chinook.bak` | 0.139s | 0.331s | 0.042s | 0.255s |
| `ContosoRetailDW.bak` | 25.427s | 188.665s | 36.691s | 197.583s |
| `CreditBackup100.bak` | 1.266s | 26.324s | 4.663s | 27.681s |
| `data.gov.bak` | 0.193s | 1.302s | 1.124s | 2.937s |
| `dba.stackexchange.com.bak` | 4.065s | 18.166s | 10.413s | 101.541s |
| `EmployeeCaseStudySampleDB2012.bak` | 0.304s | 1.857s | 0.654s | 3.249s |
| `GeneralHospital.bak` | 1.887s | 13.724s | 13.686s | 31.78s |
| `IndexInternals2008.bak` | 0.127s | 0.787s | 0.49s | 1.678s |
| `Northwinds.bak` | 0.118s | 0.318s | 0.104s | 0.249s |
| `NYCTaxi_Sample.bak` | 2.282s | 39.562s | 10.713s | 56.071s |
| `Pubs.bak` | 0.11s | 0.211s | 0.071s | 0.18s |
| `SalesDB2014.bak` | 2.463s | 10.742s | 2.408s | 12.044s |
| `SalesDBOriginal.bak` | 1.774s | 7.222s | 1.707s | 7.929s |
| `StackOverflowMini.bak` | 7.354s | 38.651s | 16.805s | 144.803s |
| `tpcxbb_1gb.bak` | 8.304s | 87.453s | 25.44s | 77.156s |
| `TutorialDB.bak` | 0.024s | 0.033s | 0.042s | 0.03s |
| `WideWorldImporters-Full.bak` | 3.472s | 29.733s | 7.405s | 34.603s |
| `WideWorldImporters-Full_old.bak` | 2.602s | 31.395s | 7.123s | 32.007s |
| `WideWorldImporters-Standard.bak` | 2.439s | 32.978s | 6.995s | 36.764s |
| `WideWorldImporters-Standard_old.bak` | 2.58s | 29.345s | 7.215s | 34.567s |
| `WideWorldImportersDW-Full.bak` | 0.605s | 8.094s | 2.182s | 9.195s |
| `WideWorldImportersDW-Standard.bak` | 0.622s | 7.335s | 1.889s | 8.378s |

_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._

## Sink read breakdown

| Backup | arrow verify | delta read | delta stats | delta verify | pg_dir read | pg_dir stats | pg_dir verify |
|--------| -------: | -------: | -------: | -------: | -------: | -------: | -------:|
| `AdventureWorks2008R2.bak` | 6.53s | 0.274s | 0.047s | 6.161s | 1.437s | 0.048s | 6.124s |
| `AdventureWorks2012.bak` | 10.689s | 0.454s | 0.077s | 9.478s | 2.199s | 0.076s | 9.582s |
| `AdventureWorks2014.bak` | 10.692s | 0.414s | 0.073s | 9.961s | 2.249s | 0.079s | 9.802s |
| `AdventureWorks2016.bak` | 10.333s | 0.43s | 0.071s | 9.75s | 2.211s | 0.073s | 9.248s |
| `AdventureWorks2016_EXT.bak` | 14.058s | 0.434s | 0.113s | 12.682s | 5.226s | 0.117s | 12.437s |
| `AdventureWorks2017.bak` | 10.57s | 0.449s | 0.078s | 10.147s | 2.3s | 0.078s | 9.797s |
| `AdventureWorks2019.bak` | 6.789s | 0.266s | 0.047s | 6.178s | 1.535s | 0.051s | 6.4s |
| `AdventureWorks2022.bak` | 8.865s | 0.392s | 0.065s | 8.55s | 1.787s | 0.062s | 7.596s |
| `AdventureWorks2025.bak` | 11.06s | 0.468s | 0.081s | 9.998s | 2.165s | 0.081s | 10.515s |
| `AdventureWorksDW2008R2.bak` | 2.684s | 0.149s | 0.052s | 2.292s | 1.173s | 0.047s | 1.851s |
| `AdventureWorksDW2012.bak` | 7.796s | 0.415s | 0.099s | 7.701s | 2.969s | 0.105s | 6.536s |
| `AdventureWorksDW2014.bak` | 8.278s | 0.297s | 0.105s | 7.942s | 3.01s | 0.111s | 7.653s |
| `AdventureWorksDW2016.bak` | 8.557s | 0.313s | 0.1s | 7.798s | 3.019s | 0.11s | 7.857s |
| `AdventureWorksDW2016_EXT.bak` | 3.406s | 0.873s | 3.899s | 3.005s | 50.859s | 3.793s | 3.068s |
| `AdventureWorksDW2017.bak` | 7.681s | 0.209s | 0.093s | 7.095s | 2.836s | 0.102s | 7.319s |
| `AdventureWorksDW2019.bak` | 7.028s | 0.192s | 0.081s | 6.231s | 3.006s | 0.102s | 7.769s |
| `AdventureWorksDW2022.bak` | 6.35s | 0.161s | 0.071s | 5.536s | 2.129s | 0.076s | 5.606s |
| `AdventureWorksDW2025.bak` | 7.662s | 0.238s | 0.098s | 7.628s | 2.969s | 0.104s | 7.589s |
| `AdventureWorksLT2012.bak` | 0.322s | 0.118s | 0.005s | 0.1s | 0.153s | 0.005s | 0.101s |
| `AdventureWorksLT2014.bak` | 0.284s | 0.238s | 0.008s | 0.129s | 0.159s | 0.005s | 0.106s |
| `AdventureWorksLT2016.bak` | 0.323s | 0.154s | 0.007s | 0.113s | 0.158s | 0.005s | 0.097s |
| `AdventureWorksLT2017.bak` | 0.309s | 0.11s | 0.005s | 0.11s | 0.156s | 0.004s | 0.105s |
| `AdventureWorksLT2019.bak` | 0.382s | 0.147s | 0.006s | 0.116s | 0.156s | 0.005s | 0.101s |
| `AdventureWorksLT2022.bak` | 0.301s | 0.184s | 0.005s | 0.127s | 0.224s | 0.005s | 0.124s |
| `AdventureWorksLT2025.bak` | 0.303s | 0.134s | 0.005s | 0.091s | 0.149s | 0.005s | 0.093s |
| `BaseballData.bak` | 3.06s | 0.163s | 0.087s | 2.891s | 1.495s | 0.092s | 2.824s |
| `Chinook-id-pk.bak` | 0.225s | 0.135s | 0.004s | 0.047s | 0.052s | 0.003s | 0.048s |
| `Chinook.bak` | 0.221s | 0.146s | 0.004s | 0.045s | 0.036s | 0.004s | 0.048s |
| `ContosoRetailDW.bak` | 200.976s | 0.823s | 2.013s | 185.457s | 25.971s | 2.409s | 168.907s |
| `CreditBackup100.bak` | 23.003s | 0.208s | 0.154s | 25.803s | 2.703s | 0.163s | 24.72s |
| `data.gov.bak` | 1.215s | 0.083s | 0.075s | 1.132s | 1.776s | 0.078s | 1.072s |
| `dba.stackexchange.com.bak` | 17.157s | 0.349s | 0.149s | 17.518s | 86.48s | 0.168s | 14.807s |
| `EmployeeCaseStudySampleDB2012.bak` | 1.516s | 0.12s | 0.071s | 1.638s | 1.78s | 0.061s | 1.387s |
| `GeneralHospital.bak` | 13.258s | 0.136s | 0.868s | 12.628s | 18.591s | 0.923s | 12.165s |
| `IndexInternals2008.bak` | 0.689s | 0.08s | 0.035s | 0.648s | 0.975s | 0.037s | 0.645s |
| `Northwinds.bak` | 0.223s | 0.114s | 0.004s | 0.059s | 0.069s | 0.004s | 0.056s |
| `NYCTaxi_Sample.bak` | 40.903s | 0.112s | 0.525s | 38.901s | 14.208s | 0.534s | 41.313s |
| `Pubs.bak` | 0.238s | 0.062s | 0.004s | 0.026s | 0.035s | 0.003s | 0.024s |
| `SalesDB2014.bak` | 10.341s | 0.131s | 0.013s | 10.558s | 1.017s | 0.027s | 10.953s |
| `SalesDBOriginal.bak` | 7.439s | 0.09s | 0.011s | 7.085s | 0.696s | 0.016s | 7.179s |
| `StackOverflowMini.bak` | 41.842s | 0.468s | 0.298s | 37.686s | 105.936s | 0.297s | 38.263s |
| `tpcxbb_1gb.bak` | 92.749s | 0.585s | 1.102s | 85.362s | 12.958s | 0.861s | 62.996s |
| `TutorialDB.bak` | 0.099s | 0.011s | 0.001s | 0.012s | 0.004s | 0.0s | 0.011s |
| `WideWorldImporters-Full.bak` | 34.489s | 0.296s | 0.183s | 28.879s | 2.903s | 0.205s | 31.083s |
| `WideWorldImporters-Full_old.bak` | 32.877s | 0.307s | 0.194s | 30.523s | 2.721s | 0.195s | 28.663s |
| `WideWorldImporters-Standard.bak` | 32.467s | 0.337s | 0.207s | 32.047s | 3.09s | 0.218s | 33.025s |
| `WideWorldImporters-Standard_old.bak` | 31.598s | 0.288s | 0.177s | 28.544s | 2.634s | 0.178s | 31.415s |
| `WideWorldImportersDW-Full.bak` | 7.897s | 0.15s | 0.117s | 7.674s | 1.974s | 0.118s | 6.963s |
| `WideWorldImportersDW-Standard.bak` | 7.7s | 0.142s | 0.113s | 6.956s | 1.674s | 0.103s | 6.468s |

_arrow verify = cell verification folded into extract_s. Sink read = pure I/O + decode. Stats = min/max/null compute. Sink verify = cell verification on the round-tripped data. Remainder of readback_s is GC / other._

---

_Generated 2026-07-16 · 49 fixtures · 49 pass · 0 xfail · 0 fail_
