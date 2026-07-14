# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld`.

**49 fixtures · 45 pass · 0 xfail (known gap) · 4 fail**

**Tables:** 1415/1445 pass · **Columns:** 12216/12619 pass

**Row count:** 30 fail · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** 30 fail · **Cells:** ✓

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
| `AdventureWorks2008R2.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2008R2.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2008R2.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5644994/5644994** | ✓ |
| `AdventureWorks2008R2.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2008R2.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2012.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2012.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2012.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644987/5644987** | ✓ |
| `AdventureWorks2012.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2012.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2014.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2014.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2014.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644994/5644994** | ✓ |
| `AdventureWorks2014.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2014.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2016.bak` | mssql→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2016.bak` | arrow→delta | 760,838 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2016.bak` | delta→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644994/5644994** | ✓ |
| `AdventureWorks2016.bak` | arrow→pg_dir | 760,838 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2016.bak` | pg_dir→arrow | 760,838 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644995/5644995** | ✓ |
| `AdventureWorks2016_EXT.bak` | mssql→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | **11178312/11178312** | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→delta | 1,378,717 | 732 | **89/89** | **701/701** | **1384/1384** | **89/89** | — | ✓ |
| `AdventureWorks2016_EXT.bak` | delta→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | **11178311/11178311** | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→pg_dir | 1,378,717 | 732 | **89/89** | **701/701** | 1378/1384 ⚠ | **89/89** | — | ✗ |
| `AdventureWorks2016_EXT.bak` | pg_dir→arrow | 1,378,717 | 732 | **92/92** | **698/698** | **1018/1018** | **92/92** | **11178312/11178312** | ✓ |
| `AdventureWorks2017.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2017.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2017.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644987/5644987** | ✓ |
| `AdventureWorks2017.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2017.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2019.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2019.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2019.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644987/5644987** | ✓ |
| `AdventureWorks2019.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2019.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2022.bak` | mssql→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2022.bak` | arrow→delta | 760,837 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2022.bak` | delta→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644987/5644987** | ✓ |
| `AdventureWorks2022.bak` | arrow→pg_dir | 760,837 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2022.bak` | pg_dir→arrow | 760,837 | 475 | **71/71** | **466/466** | **684/684** | **71/71** | **5644988/5644988** | ✓ |
| `AdventureWorks2025.bak` | mssql→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5640293/5640293** | ✓ |
| `AdventureWorks2025.bak` | arrow→delta | 760,167 | 475 | **70/70** | **468/468** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2025.bak` | delta→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5640292/5640292** | ✓ |
| `AdventureWorks2025.bak` | arrow→pg_dir | 760,167 | 475 | **70/70** | **468/468** | 926/932 ⚠ | **70/70** | — | ✗ |
| `AdventureWorks2025.bak` | pg_dir→arrow | 760,167 | 475 | **71/71** | **466/466** | **678/678** | **71/71** | **5640293/5640293** | ✓ |
| `AdventureWorksDW2008R2.bak` | mssql→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | **3543730/3543730** | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→delta | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | delta→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | **3543730/3543730** | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→pg_dir | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | pg_dir→arrow | 282,030 | 327 | **28/28** | **327/327** | **572/572** | **28/28** | **3543730/3543730** | ✓ |
| `AdventureWorksDW2012.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2012.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2012.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2012.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2012.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2014.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2014.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2014.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2014.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2014.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2016.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2016.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2016.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2016.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2016.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2016_EXT.bak` | mssql→arrow | 24,400,096 | 413 | 32/33 ⚠ ⚠ (`dbo.FactResellerSalesXL_CCI`) | **386/386** | **760/760** | 32/33 ⚠ | **7823359/7823359** | ✗ |
| `AdventureWorksDW2016_EXT.bak` | arrow→delta | 24,400,096 | 413 | **32/32** | **386/386** | **762/762** | **32/32** | — | ✓ |
| `AdventureWorksDW2016_EXT.bak` | delta→arrow | 24,400,096 | 413 | 32/33 ⚠ ⚠ (`dbo.FactResellerSalesXL_CCI`) | **386/386** | **760/760** | 32/33 ⚠ | **7823359/7823359** | ✗ |
| `AdventureWorksDW2016_EXT.bak` | arrow→pg_dir | 24,400,096 | 413 | **32/32** | **386/386** | **762/762** | **32/32** | — | ✓ |
| `AdventureWorksDW2016_EXT.bak` | pg_dir→arrow | 24,400,096 | 413 | **33/33** | **413/413** | **814/814** | **33/33** | **7823359/7823359** | ✓ |
| `AdventureWorksDW2017.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2017.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2017.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2017.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2017.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2019.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2019.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2019.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2019.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2019.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2022.bak` | mssql→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2022.bak` | arrow→delta | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2022.bak` | delta→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2022.bak` | arrow→pg_dir | 1,060,820 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2022.bak` | pg_dir→arrow | 1,060,820 | 359 | **31/31** | **359/359** | **706/706** | **31/31** | **7890819/7890819** | ✓ |
| `AdventureWorksDW2025.bak` | mssql→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | **7877562/7877562** | ✓ |
| `AdventureWorksDW2025.bak` | arrow→delta | 1,047,563 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2025.bak` | delta→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | **7877562/7877562** | ✓ |
| `AdventureWorksDW2025.bak` | arrow→pg_dir | 1,047,563 | 359 | **31/31** | **359/359** | **708/708** | **31/31** | — | ✓ |
| `AdventureWorksDW2025.bak` | pg_dir→arrow | 1,047,563 | 359 | **31/31** | **359/359** | **704/704** | **31/31** | **7877562/7877562** | ✓ |
| `AdventureWorksLT2012.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2012.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2012.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2014.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2014.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2014.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2016.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2016.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2016.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2017.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2017.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2017.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2019.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2019.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2019.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2022.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2022.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2022.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **104/104** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2025.bak` | mssql→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | **29778/29778** | ✓ |
| `AdventureWorksLT2025.bak` | arrow→delta | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | delta→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | **29777/29777** | ✓ |
| `AdventureWorksLT2025.bak` | arrow→pg_dir | 4,277 | 105 | **11/11** | **97/97** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | pg_dir→arrow | 4,277 | 105 | **12/12** | **96/96** | **102/102** | **12/12** | **29778/29778** | ✓ |
| `BaseballData.bak` | mssql→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | **8129498/8129498** | ✓ |
| `BaseballData.bak` | arrow→delta | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | — | ✓ |
| `BaseballData.bak` | delta→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | **8129498/8129498** | ✓ |
| `BaseballData.bak` | arrow→pg_dir | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | — | ✓ |
| `BaseballData.bak` | pg_dir→arrow | 493,104 | 353 | **25/25** | **353/353** | **698/698** | **25/25** | **8129498/8129498** | ✓ |
| `Chinook-id-pk.bak` | mssql→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook-id-pk.bak` | arrow→delta | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook-id-pk.bak` | delta→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook-id-pk.bak` | arrow→pg_dir | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook-id-pk.bak` | pg_dir→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook.bak` | mssql→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook.bak` | arrow→delta | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook.bak` | delta→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `Chinook.bak` | arrow→pg_dir | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Chinook.bak` | pg_dir→arrow | 16,075 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | **44173/44173** | ✓ |
| `ContosoRetailDW.bak` | mssql→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | **15668757/15668757** | ✓ |
| `ContosoRetailDW.bak` | arrow→delta | 34,326,475 | 384 | **25/25** | **396/396** | **766/766** | **25/25** | — | ✓ |
| `ContosoRetailDW.bak` | delta→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | **15668757/15668757** | ✓ |
| `ContosoRetailDW.bak` | arrow→pg_dir | 34,326,475 | 384 | **25/25** | **396/396** | **766/766** | **25/25** | — | ✓ |
| `ContosoRetailDW.bak` | pg_dir→arrow | 34,326,475 | 384 | **26/26** | **379/379** | **736/736** | **26/26** | **15668757/15668757** | ✓ |
| `CreditBackup100.bak` | mssql→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | **1928363/1928363** | ✓ |
| `CreditBackup100.bak` | arrow→delta | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | — | ✓ |
| `CreditBackup100.bak` | delta→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | **1928363/1928363** | ✓ |
| `CreditBackup100.bak` | arrow→pg_dir | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | — | ✓ |
| `CreditBackup100.bak` | pg_dir→arrow | 1,656,574 | 93 | **10/10** | **93/93** | **182/182** | **10/10** | **1928363/1928363** | ✓ |
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
| `EmployeeCaseStudySampleDB2012.bak` | mssql→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | **1760000/1760000** | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | arrow→delta | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | — | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | delta→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | **1760000/1760000** | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | arrow→pg_dir | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | — | ✓ |
| `EmployeeCaseStudySampleDB2012.bak` | pg_dir→arrow | 160,000 | 24 | **2/2** | **24/24** | **48/48** | **2/2** | **1760000/1760000** | ✓ |
| `GeneralHospital.bak` | mssql→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `GeneralHospital.bak` | arrow→delta | 2,175,940 | 67 | **13/13** | **197/197** | **394/394** | **13/13** | — | ✓ |
| `GeneralHospital.bak` | delta→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `GeneralHospital.bak` | arrow→pg_dir | 2,175,940 | 67 | **13/13** | **197/197** | **394/394** | **13/13** | — | ✓ |
| `GeneralHospital.bak` | pg_dir→arrow | 2,175,940 | 67 | **13/13** | **67/67** | **128/128** | **13/13** | digest | ✓ |
| `IndexInternals2008.bak` | mssql→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | **800000/800000** | ✓ |
| `IndexInternals2008.bak` | arrow→delta | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `IndexInternals2008.bak` | delta→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | **800000/800000** | ✓ |
| `IndexInternals2008.bak` | arrow→pg_dir | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | — | ✓ |
| `IndexInternals2008.bak` | pg_dir→arrow | 160,000 | 12 | **2/2** | **12/12** | **24/24** | **2/2** | **800000/800000** | ✓ |
| `Northwinds.bak` | mssql→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | **13005/13005** | ✓ |
| `Northwinds.bak` | arrow→delta | 1,153 | 83 | **11/11** | **84/84** | **168/168** | **11/11** | — | ✓ |
| `Northwinds.bak` | delta→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | **13005/13005** | ✓ |
| `Northwinds.bak` | arrow→pg_dir | 1,153 | 83 | **11/11** | **84/84** | **168/168** | **11/11** | — | ✓ |
| `Northwinds.bak` | pg_dir→arrow | 1,153 | 83 | **12/12** | **79/79** | **158/158** | **12/12** | **13005/13005** | ✓ |
| `NYCTaxi_Sample.bak` | mssql→arrow | 1,703,957 | 25 | 1/2 ⚠ ⚠ (`dbo.nyctaxi_sample`) | — | — | 1/2 ⚠ | — | ✗ |
| `NYCTaxi_Sample.bak` | arrow→delta | 1,703,957 | 25 | — | — | — | — | — | ✓ |
| `NYCTaxi_Sample.bak` | delta→arrow | 1,703,957 | 25 | 1/2 ⚠ ⚠ (`dbo.nyctaxi_sample`) | — | — | 1/2 ⚠ | — | ✗ |
| `NYCTaxi_Sample.bak` | arrow→pg_dir | 1,703,957 | 25 | — | — | — | — | — | ✓ |
| `NYCTaxi_Sample.bak` | pg_dir→arrow | 1,703,957 | 25 | **2/2** | **23/23** | **46/46** | **2/2** | digest | ✓ |
| `Pubs.bak` | mssql→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | **880/880** | ✓ |
| `Pubs.bak` | arrow→delta | 255 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Pubs.bak` | delta→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | **880/880** | ✓ |
| `Pubs.bak` | arrow→pg_dir | 255 | 64 | **11/11** | **64/64** | **128/128** | **11/11** | — | ✓ |
| `Pubs.bak` | pg_dir→arrow | 255 | 64 | **11/11** | **64/64** | **126/126** | **11/11** | **880/880** | ✓ |
| `SalesDB2014.bak` | mssql→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **850382/850382** | ✓ |
| `SalesDB2014.bak` | arrow→delta | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `SalesDB2014.bak` | delta→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **850382/850382** | ✓ |
| `SalesDB2014.bak` | arrow→pg_dir | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | — | ✓ |
| `SalesDB2014.bak` | pg_dir→arrow | 6,735,507 | 16 | **4/4** | **16/16** | **32/32** | **4/4** | **850382/850382** | ✓ |
| `SalesDBOriginal.bak` | mssql→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | **850386/850386** | ✓ |
| `SalesDBOriginal.bak` | arrow→delta | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | — | ✓ |
| `SalesDBOriginal.bak` | delta→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | **850386/850386** | ✓ |
| `SalesDBOriginal.bak` | arrow→pg_dir | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | — | ✓ |
| `SalesDBOriginal.bak` | pg_dir→arrow | 6,735,508 | 21 | **5/5** | **21/21** | **42/42** | **5/5** | **850386/850386** | ✓ |
| `StackOverflowMini.bak` | mssql→arrow | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | **8290987/8290987** | ✓ |
| `StackOverflowMini.bak` | arrow→delta | 8,097,337 | 61 | **8/8** | **56/56** | **108/108** | **8/8** | — | ✓ |
| `StackOverflowMini.bak` | delta→arrow | 8,097,337 | 61 | **9/9** | **56/56** | **106/106** | **9/9** | **8290987/8290987** | ✓ |
| `StackOverflowMini.bak` | arrow→pg_dir | 8,097,337 | 61 | 1/8 ⚠ ⚠ (`dbo.Comments`, `dbo.LinkTypes`, `dbo.PostTypes`, `dbo.Posts`, `dbo.Users`, `dbo.VoteTypes`, `dbo.Votes`) | **4/4** | **8/8** | 1/8 ⚠ | — | ✗ |
| `StackOverflowMini.bak` | pg_dir→arrow | 8,097,337 | 61 | 2/9 ⚠ ⚠ (`dbo.Comments`, `dbo.LinkTypes`, `dbo.Posts`, `dbo.PostTypes`, `dbo.Users`, `dbo.Votes`, `dbo.VoteTypes`) | **4/4** | **8/8** | 2/9 ⚠ | **1332219/1332219** | ✗ |
| `tpcxbb_1gb.bak` | mssql→arrow | 34,001,580 | 394 | 7/30 ⚠ ⚠ (`dbo.customer`, `dbo.customer_address`, `dbo.customer_demographics`, `dbo.date_dim`, `dbo.household_demographics`, `dbo.income_band`, `dbo.inventory`, `dbo.item`, `dbo.item_marketprices`, `dbo.product_reviews`, `dbo.promotion`, `dbo.reason`, `dbo.ship_mode`, `dbo.store`, `dbo.store_returns`, `dbo.store_sales`, `dbo.time_dim`, `dbo.warehouse`, `dbo.web_clickstreams`, `dbo.web_page`, `dbo.web_returns`, `dbo.web_sales`, `dbo.web_site`) | **50/50** | **94/94** | 7/30 ⚠ | **156/156** | ✗ |
| `tpcxbb_1gb.bak` | arrow→delta | 34,001,580 | 394 | **7/7** | **50/50** | **96/96** | **7/7** | — | ✓ |
| `tpcxbb_1gb.bak` | delta→arrow | 34,001,580 | 394 | 7/30 ⚠ ⚠ (`dbo.customer`, `dbo.customer_address`, `dbo.customer_demographics`, `dbo.date_dim`, `dbo.household_demographics`, `dbo.income_band`, `dbo.inventory`, `dbo.item`, `dbo.item_marketprices`, `dbo.product_reviews`, `dbo.promotion`, `dbo.reason`, `dbo.ship_mode`, `dbo.store`, `dbo.store_returns`, `dbo.store_sales`, `dbo.time_dim`, `dbo.warehouse`, `dbo.web_clickstreams`, `dbo.web_page`, `dbo.web_returns`, `dbo.web_sales`, `dbo.web_site`) | **50/50** | **94/94** | 7/30 ⚠ | **156/156** | ✗ |
| `tpcxbb_1gb.bak` | arrow→pg_dir | 34,001,580 | 394 | **7/7** | **50/50** | **96/96** | **7/7** | — | ✓ |
| `tpcxbb_1gb.bak` | pg_dir→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | **156/156** | ✓ |
| `TutorialDB.bak` | mssql→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→delta | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | delta→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→pg_dir | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | pg_dir→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `WideWorldImporters-Full.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **543/543** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | pg_dir→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **542/542** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard_old.bak` | pg_dir→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | **12398661/12398661** | ✓ |
| `WideWorldImportersDW-Full.bak` | mssql→arrow | 922,709 | 50 | 19/24 ⚠ ⚠ (`Fact.Movement`, `Fact.Order`, `Fact.Purchase`, `Fact.Sale`, `Fact.Transaction`) | **15/15** | **28/28** | 19/24 ⚠ | **1536907/1536907** | ✗ |
| `WideWorldImportersDW-Full.bak` | arrow→delta | 922,709 | 50 | **10/10** | **99/99** | **194/194** | **10/10** | — | ✓ |
| `WideWorldImportersDW-Full.bak` | delta→arrow | 922,709 | 50 | 19/24 ⚠ ⚠ (`Fact.Movement`, `Fact.Order`, `Fact.Purchase`, `Fact.Sale`, `Fact.Transaction`) | **15/15** | **28/28** | 19/24 ⚠ | ERROR (5 tables) | ✗ |
| `WideWorldImportersDW-Full.bak` | arrow→pg_dir | 922,709 | 50 | **10/10** | **99/99** | **194/194** | **10/10** | — | ✓ |
| `WideWorldImportersDW-Full.bak` | pg_dir→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | **13606612/13606612** | ✓ |
| `WideWorldImportersDW-Standard.bak` | mssql→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | **14410908/14410908** | ✓ |
| `WideWorldImportersDW-Standard.bak` | arrow→delta | 922,709 | 50 | **16/16** | **188/188** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Standard.bak` | delta→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | ERROR (10 tables) | ✗ |
| `WideWorldImportersDW-Standard.bak` | arrow→pg_dir | 922,709 | 50 | **16/16** | **188/188** | **372/372** | **16/16** | — | ✓ |
| `WideWorldImportersDW-Standard.bak` | pg_dir→arrow | 922,709 | 50 | **24/24** | **24/24** | **46/46** | **24/24** | **14410908/14410908** | ✓ |

## Per-fixture detail

### `AdventureWorks2008R2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 181.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **12/12** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.897 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 44.594 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 46.491 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **14/14** | ✓ | cells **11179/11179** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2016_EXT.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 125.034 MB_

#### Stage: mssql→arrow

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
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

### `AdventureWorks2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.957 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 199.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 200.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **14/14** | ✓ | cells **11172/11172** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells **156/156** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorks2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 47.902 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells **6489/6489** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells **144/144** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells **6489/6489** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells **144/144** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

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
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **14/14** | ✓ | cells **6489/6489** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells **48/48** ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | — | ✓ | cells **4060/4060** ✓ |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ | cells **592/592** ✓ |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ | cells **948/948** ✓ |
| `HumanResources.JobCandidate` | rowstore | 13 | ✓ | **4/4** | **6/6** | ✓ | cells **39/39** ✓ |
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
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells **19972/19972** ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells **6/6** ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | — | ✓ | cells **1267/1267** ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells **21432/21432** ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells **16/16** ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **22/22** | ✓ | cells **144/144** ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells **10/10** ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | — | ✓ | cells **12096/12096** ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells **12/12** ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells **32/32** ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells **5345/5345** ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells **1185/1185** ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **6/6** | ✓ | cells **640/640** ✓ |
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
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells **19118/19118** ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells **970536/970536** ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | — | ✓ | cells **723695/723695** ✓ |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ | cells **27647/27647** ✓ |
| `Sales.SalesPerson` | rowstore | 17 | ✓ | **9/9** | **16/16** | ✓ | cells **136/136** ✓ |
| `Sales.SalesPersonQuotaHistory` | rowstore | 163 | ✓ | **5/5** | **8/8** | ✓ | cells **489/489** ✓ |
| `Sales.SalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `Sales.SalesTaxRate` | rowstore | 29 | ✓ | **7/7** | **12/12** | ✓ | cells **174/174** ✓ |
| `Sales.SalesTerritory` | rowstore | 10 | ✓ | **10/10** | **18/18** | ✓ | cells **90/90** ✓ |
| `Sales.SalesTerritoryHistory` | rowstore | 17 | ✓ | **6/6** | **10/10** | ✓ | cells **51/51** ✓ |
| `Sales.ShoppingCartItem` | rowstore | 3 | ✓ | **6/6** | **12/12** | ✓ | cells **15/15** ✓ |
| `Sales.SpecialOffer` | rowstore | 16 | ✓ | **11/11** | **20/20** | ✓ | cells **160/160** ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells **1076/1076** ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells **3505/3505** ✓ |

### `AdventureWorksDW2008R2.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 74.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells **805/805** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells **21384/21384** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells **8584/8584** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells **5895/5895** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells **44/44** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells **1440/1440** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells **28528/28528** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells **236454/236454** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells **1268358/1268358** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells **1338810/1338810** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells **815/815** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells **16362/16362** ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells **805/805** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells **21384/21384** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells **8584/8584** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells **5895/5895** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells **44/44** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells **1440/1440** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells **28528/28528** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells **236454/236454** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells **1268358/1268358** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells **1338810/1338810** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells **815/815** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells **16362/16362** ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **14/14** | ✓ | cells **805/805** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells **21384/21384** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells **8584/8584** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells **5895/5895** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | — | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **5/5** | **10/10** | ✓ | cells **44/44** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **13/13** | **26/26** | ✓ | cells **1440/1440** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **4/4** | **8/8** | ✓ | cells **28528/28528** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **7/7** | **14/14** | ✓ | cells **236454/236454** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **23/23** | **42/42** | ✓ | cells **1268358/1268358** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **24/24** | **48/48** | ✓ | cells **1338810/1338810** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **6/6** | **12/12** | ✓ | cells **815/815** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **7/7** | **14/14** | ✓ | cells **16362/16362** ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |

### `AdventureWorksDW2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.766 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.41 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 21.443 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2016_EXT.bak` — 2022 — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 883.324 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✗ | — | — | ✗ | missing from output |
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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactResellerSalesXL_CCI` | columnstore | 11,669,638 | ✗ | — | — | ✗ | missing from output |
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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **14/14** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 15,168 | ✓ | **3/3** | **6/6** | ✓ | cells **15168/15168** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksDW2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 24.133 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells **1911/1911** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells **1911/1911** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

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
| `dbo.DatabaseLog` | rowstore | 96 | ✓ | **8/8** | **12/12** | ✓ | cells **672/672** ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells **891/891** ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells **210/210** ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells **517552/517552** ✓ |
| `dbo.DimDate` | rowstore | 3,652 | ✓ | **19/19** | **38/38** | ✓ | cells **65736/65736** ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells **14/14** ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **31/31** | **60/60** | ✓ | cells **8880/8880** ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **11/11** | **22/22** | ✓ | cells **6550/6550** ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells **21210/21210** ✓ |
| `dbo.DimProductCategory` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 37 | ✓ | **6/6** | **12/12** | ✓ | cells **185/185** ✓ |
| `dbo.DimPromotion` | rowstore | 16 | ✓ | **16/16** | **32/32** | ✓ | cells **240/240** ✓ |
| `dbo.DimReseller` | rowstore | 701 | ✓ | **20/20** | **40/40** | ✓ | cells **13319/13319** ✓ |
| `dbo.DimSalesReason` | rowstore | 10 | ✓ | **4/4** | **8/8** | ✓ | cells **30/30** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 11 | ✓ | **6/6** | **12/12** | ✓ | cells **55/55** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **2/2** | **4/4** | ✓ | cells **3/3** ✓ |
| `dbo.FactAdditionalInternationalProductDescription` | rowstore | 1,911 | ✓ | **3/3** | **6/6** | ✓ | cells **1911/1911** ✓ |
| `dbo.FactCallCenter` | rowstore | 120 | ✓ | **14/14** | **28/28** | ✓ | cells **1560/1560** ✓ |
| `dbo.FactCurrencyRate` | rowstore | 14,264 | ✓ | **5/5** | **10/10** | ✓ | cells **42792/42792** ✓ |
| `dbo.FactFinance` | rowstore | 39,409 | ✓ | **8/8** | **16/16** | ✓ | cells **275863/275863** ✓ |
| `dbo.FactInternetSales` | rowstore | 60,398 | ✓ | **26/26** | **48/48** | ✓ | cells **1449552/1449552** ✓ |
| `dbo.FactInternetSalesReason` | rowstore | 64,515 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.FactProductInventory` | rowstore | 776,286 | ✓ | **7/7** | **14/14** | ✓ | cells **3881430/3881430** ✓ |
| `dbo.FactResellerSales` | rowstore | 60,855 | ✓ | **27/27** | **54/54** | ✓ | cells **1521375/1521375** ✓ |
| `dbo.FactSalesQuota` | rowstore | 163 | ✓ | **7/7** | **14/14** | ✓ | cells **978/978** ✓ |
| `dbo.FactSurveyResponse` | rowstore | 2,727 | ✓ | **8/8** | **16/16** | ✓ | cells **19089/19089** ✓ |
| `dbo.NewFactCurrencyRate` | rowstore | 50 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `dbo.ProspectiveBuyer` | rowstore | 2,059 | ✓ | **24/24** | **48/48** | ✓ | cells **47357/47357** ✓ |
| `dbo.sysdiagrams` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |

### `AdventureWorksLT2012.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.426 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 13.336 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `AdventureWorksLT2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 1.684 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **2/2** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

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
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **3/3** | **6/6** | ✓ | cells **3/3** ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells **3600/3600** ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | — | ✓ | cells **11858/11858** ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells **1251/1251** ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells **4720/4720** ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells **164/164** ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells **2286/2286** ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **6/6** | ✓ | cells **512/512** ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells **1524/1524** ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells **3252/3252** ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | — | ✓ | cells **608/608** ✓ |

### `BaseballData.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 114.171 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells **24170/24170** ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells **1644529/1644529** ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells **312/312** ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells **11838/11838** ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells **1116/1116** ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells **19593/19593** ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells **2028600/2028600** ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells **199690/199690** ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells **1570/1570** ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells **2021726/2021726** ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells **36084/36084** ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells **145379/145379** ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells **23298/23298** ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells **23142/23142** ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells **558/558** ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells **1130139/1130139** ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells **124524/124524** ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells **530048/530048** ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells **23141/23141** ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells **2996/2996** ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells **12294/12294** ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells **1904/1904** ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells **122175/122175** ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells **360/360** ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells **312/312** ✓ |

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
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells **24170/24170** ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells **1644529/1644529** ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells **312/312** ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells **11838/11838** ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells **1116/1116** ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells **19593/19593** ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells **2028600/2028600** ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells **199690/199690** ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells **1570/1570** ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells **2021726/2021726** ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells **36084/36084** ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells **145379/145379** ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells **23298/23298** ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells **23142/23142** ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells **558/558** ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells **1130139/1130139** ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells **124524/124524** ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells **530048/530048** ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells **23141/23141** ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells **2996/2996** ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells **12294/12294** ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells **1904/1904** ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells **122175/122175** ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells **360/360** ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells **312/312** ✓ |

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
| `dbo.allstarfull` | rowstore | 4,834 | ✓ | **8/8** | **16/16** | ✓ | cells **24170/24170** ✓ |
| `dbo.appearances` | rowstore | 96,737 | ✓ | **20/20** | **40/40** | ✓ | cells **1644529/1644529** ✓ |
| `dbo.awardsmanagers` | rowstore | 156 | ✓ | **6/6** | **10/10** | ✓ | cells **312/312** ✓ |
| `dbo.awardsplayers` | rowstore | 5,919 | ✓ | **6/6** | **12/12** | ✓ | cells **11838/11838** ✓ |
| `dbo.awardssharemanagers` | rowstore | 372 | ✓ | **7/7** | **14/14** | ✓ | cells **1116/1116** ✓ |
| `dbo.awardsshareplayers` | rowstore | 6,531 | ✓ | **7/7** | **14/14** | ✓ | cells **19593/19593** ✓ |
| `dbo.batting` | rowstore | 96,600 | ✓ | **24/24** | **48/48** | ✓ | cells **2028600/2028600** ✓ |
| `dbo.battingpost` | rowstore | 10,510 | ✓ | **22/22** | **44/44** | ✓ | cells **199690/199690** ✓ |
| `dbo.els_teamnames` | rowstore | 314 | ✓ | **6/6** | **12/12** | ✓ | cells **1570/1570** ✓ |
| `dbo.fielding` | rowstore | 144,409 | ✓ | **18/18** | **36/36** | ✓ | cells **2021726/2021726** ✓ |
| `dbo.fieldingof` | rowstore | 12,028 | ✓ | **6/6** | **12/12** | ✓ | cells **36084/36084** ✓ |
| `dbo.fieldingpost` | rowstore | 11,183 | ✓ | **17/17** | **34/34** | ✓ | cells **145379/145379** ✓ |
| `dbo.halloffame` | rowstore | 3,883 | ✓ | **8/8** | **16/16** | ✓ | cells **23298/23298** ✓ |
| `dbo.managers` | rowstore | 3,306 | ✓ | **10/10** | **20/20** | ✓ | cells **23142/23142** ✓ |
| `dbo.managershalf` | rowstore | 93 | ✓ | **10/10** | **20/20** | ✓ | cells **558/558** ✓ |
| `dbo.pitching` | rowstore | 41,857 | ✓ | **30/30** | **54/54** | ✓ | cells **1130139/1130139** ✓ |
| `dbo.pitchingpost` | rowstore | 4,612 | ✓ | **30/30** | **60/60** | ✓ | cells **124524/124524** ✓ |
| `dbo.players` | rowstore | 16,564 | ✓ | **33/33** | **66/66** | ✓ | cells **530048/530048** ✓ |
| `dbo.salaries` | rowstore | 23,141 | ✓ | **5/5** | **10/10** | ✓ | cells **23141/23141** ✓ |
| `dbo.schools` | rowstore | 749 | ✓ | **5/5** | **10/10** | ✓ | cells **2996/2996** ✓ |
| `dbo.schoolsplayers` | rowstore | 6,147 | ✓ | **4/4** | **8/8** | ✓ | cells **12294/12294** ✓ |
| `dbo.seriespost` | rowstore | 272 | ✓ | **9/9** | **18/18** | ✓ | cells **1904/1904** ✓ |
| `dbo.teams` | rowstore | 2,715 | ✓ | **48/48** | **96/96** | ✓ | cells **122175/122175** ✓ |
| `dbo.teamsfranchises` | rowstore | 120 | ✓ | **4/4** | **8/8** | ✓ | cells **360/360** ✓ |
| `dbo.teamshalf` | rowstore | 52 | ✓ | **10/10** | **20/20** | ✓ | cells **312/312** ✓ |

### `Chinook-id-pk.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 12.257 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

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
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

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
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

### `Chinook.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 6.098 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

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
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

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
| `dbo.Album` | rowstore | 347 | ✓ | **3/3** | **6/6** | ✓ | cells **694/694** ✓ |
| `dbo.Artist` | rowstore | 275 | ✓ | **2/2** | **4/4** | ✓ | cells **275/275** ✓ |
| `dbo.Customer` | rowstore | 59 | ✓ | **13/13** | **26/26** | ✓ | cells **708/708** ✓ |
| `dbo.Employee` | rowstore | 8 | ✓ | **15/15** | **30/30** | ✓ | cells **112/112** ✓ |
| `dbo.Genre` | rowstore | 25 | ✓ | **2/2** | **4/4** | ✓ | cells **25/25** ✓ |
| `dbo.Invoice` | rowstore | 458 | ✓ | **9/9** | **18/18** | ✓ | cells **3664/3664** ✓ |
| `dbo.InvoiceLine` | rowstore | 2,662 | ✓ | **5/5** | **10/10** | ✓ | cells **10648/10648** ✓ |
| `dbo.MediaType` | rowstore | 5 | ✓ | **2/2** | **4/4** | ✓ | cells **5/5** ✓ |
| `dbo.Playlist` | rowstore | 18 | ✓ | **2/2** | **4/4** | ✓ | cells **18/18** ✓ |
| `dbo.PlaylistTrack` | rowstore | 8,715 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.Track` | rowstore | 3,503 | ✓ | **9/9** | **18/18** | ✓ | cells **28024/28024** ✓ |

### `ContosoRetailDW.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 629.956 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells **288/288** ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells **24/24** ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells **168/168** ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells **528332/528332** ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells **71568/71568** ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells **7618/7618** ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells **5052/5052** ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells **6066/6066** ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells **132872/132872** ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells **3030/3030** ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells **78027/78027** ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells **48/48** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells **308/308** ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells **364/364** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells **3710/3710** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells **18/18** ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells **7344/7344** ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells **5411/5411** ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells **2931630/2931630** ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells **162981/162981** ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells **49250/49250** ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells **3946140/3946140** ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells **3406104/3406104** ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells **2357664/2357664** ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells **1964740/1964740** ✓ |
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
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells **288/288** ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells **24/24** ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells **168/168** ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells **528332/528332** ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells **71568/71568** ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells **7618/7618** ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells **5052/5052** ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells **6066/6066** ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells **132872/132872** ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells **3030/3030** ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells **78027/78027** ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells **48/48** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells **308/308** ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells **364/364** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells **3710/3710** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells **18/18** ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells **7344/7344** ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells **5411/5411** ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells **2931630/2931630** ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells **162981/162981** ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells **49250/49250** ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells **3946140/3946140** ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells **3406104/3406104** ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells **2357664/2357664** ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells **1964740/1964740** ✓ |
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
| `dbo.DimAccount` | rowstore | 24 | ✓ | **13/13** | **24/24** | ✓ | cells **288/288** ✓ |
| `dbo.DimChannel` | rowstore | 4 | ✓ | **7/7** | **14/14** | ✓ | cells **24/24** ✓ |
| `dbo.DimCurrency` | rowstore | 28 | ✓ | **7/7** | **14/14** | ✓ | cells **168/168** ✓ |
| `dbo.DimCustomer` | rowstore | 18,869 | ✓ | **29/29** | **58/58** | ✓ | cells **528332/528332** ✓ |
| `dbo.DimDate` | rowstore | 2,556 | ✓ | **29/29** | **58/58** | ✓ | cells **71568/71568** ✓ |
| `dbo.DimEmployee` | rowstore | 293 | ✓ | **27/27** | **54/54** | ✓ | cells **7618/7618** ✓ |
| `dbo.DimEntity` | rowstore | 421 | ✓ | **13/13** | **24/24** | ✓ | cells **5052/5052** ✓ |
| `dbo.DimGeography` | rowstore | 674 | ✓ | **10/10** | **20/20** | ✓ | cells **6066/6066** ✓ |
| `dbo.DimMachine` | rowstore | 7,816 | ✓ | **18/18** | **36/36** | ✓ | cells **132872/132872** ✓ |
| `dbo.DimOutage` | rowstore | 303 | ✓ | **11/11** | **22/22** | ✓ | cells **3030/3030** ✓ |
| `dbo.DimProduct` | rowstore | 2,517 | ✓ | **32/32** | **58/58** | ✓ | cells **78027/78027** ✓ |
| `dbo.DimProductCategory` | rowstore | 8 | ✓ | **7/7** | **14/14** | ✓ | cells **48/48** ✓ |
| `dbo.DimProductSubcategory` | rowstore | 44 | ✓ | **8/8** | **16/16** | ✓ | cells **308/308** ✓ |
| `dbo.DimPromotion` | rowstore | 28 | ✓ | **14/14** | **24/24** | ✓ | cells **364/364** ✓ |
| `dbo.DimSalesTerritory` | rowstore | 265 | ✓ | **15/15** | **28/28** | ✓ | cells **3710/3710** ✓ |
| `dbo.DimScenario` | rowstore | 3 | ✓ | **7/7** | **14/14** | ✓ | cells **18/18** ✓ |
| `dbo.DimStore` | rowstore | 306 | ✓ | **25/25** | **50/50** | ✓ | cells **7344/7344** ✓ |
| `dbo.FactExchangeRate` | rowstore | 773 | ✓ | **8/8** | **16/16** | ✓ | cells **5411/5411** ✓ |
| `dbo.FactInventory` | rowstore | 8,013,099 | ✓ | **16/16** | **32/32** | ✓ | cells **2931630/2931630** ✓ |
| `dbo.FactITMachine` | rowstore | 23,283 | ✓ | **8/8** | **16/16** | ✓ | cells **162981/162981** ✓ |
| `dbo.FactITSLA` | rowstore | 4,925 | ✓ | **11/11** | **22/22** | ✓ | cells **49250/49250** ✓ |
| `dbo.FactOnlineSales` | rowstore | 12,627,608 | ✓ | **21/21** | **36/36** | ✓ | cells **3946140/3946140** ✓ |
| `dbo.FactSales` | rowstore | 3,406,089 | ✓ | **19/19** | **38/38** | ✓ | cells **3406104/3406104** ✓ |
| `dbo.FactSalesQuota` | rowstore | 7,465,911 | ✓ | **13/13** | **26/26** | ✓ | cells **2357664/2357664** ✓ |
| `dbo.FactStrategyPlan` | rowstore | 2,750,628 | ✓ | **11/11** | **22/22** | ✓ | cells **1964740/1964740** ✓ |
| `dbo.sysdiagrams` | rowstore | 0 | — | — | — | — |  |

### `CreditBackup100.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 52.739 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells **1400000/1400000** ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells **5000/5000** ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells **77770/77770** ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells **5500/5500** ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells **72/72** ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells **100000/100000** ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells **1/1** ✓ |

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
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells **1400000/1400000** ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells **5000/5000** ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells **77770/77770** ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells **5500/5500** ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells **72/72** ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells **100000/100000** ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells **1/1** ✓ |

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
| `dbo.category` | rowstore | 10 | ✓ | **3/3** | **6/6** | ✓ | cells **20/20** ✓ |
| `dbo.charge` | rowstore | 1,600,000 | ✓ | **8/8** | **16/16** | ✓ | cells **1400000/1400000** ✓ |
| `dbo.corporation` | rowstore | 500 | ✓ | **11/11** | **22/22** | ✓ | cells **5000/5000** ✓ |
| `dbo.member` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.member2` | rowstore | 10,000 | ✓ | **18/18** | **34/34** | ✓ | cells **170000/170000** ✓ |
| `dbo.payment` | rowstore | 15,554 | ✓ | **6/6** | **12/12** | ✓ | cells **77770/77770** ✓ |
| `dbo.provider` | rowstore | 500 | ✓ | **12/12** | **24/24** | ✓ | cells **5500/5500** ✓ |
| `dbo.region` | rowstore | 9 | ✓ | **9/9** | **18/18** | ✓ | cells **72/72** ✓ |
| `dbo.statement` | rowstore | 20,000 | ✓ | **6/6** | **12/12** | ✓ | cells **100000/100000** ✓ |
| `dbo.status` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells **1/1** ✓ |

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
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **12/12** | **24/24** | ✓ | cells **880000/880000** ✓ |

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
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Employee` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |
| `dbo.EmployeeHeap` | rowstore | 80,000 | ✓ | **6/6** | **12/12** | ✓ | cells **400000/400000** ✓ |

### `Northwinds.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 0.816 MB_

#### Stage: mssql→arrow

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

### `NYCTaxi_Sample.bak` — 2022 — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 97.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✗ | — | — | ✗ | missing from output |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.nyc_taxi_models` | rowstore | 0 | — | — | — | — |  |
| `dbo.nyctaxi_sample` | columnstore | 1,703,957 | ✗ | — | — | ✗ | missing from output |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|

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
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells **184/184** ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells **301/301** ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells **42/42** ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells **16/16** ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells **63/63** ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells **30/30** ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **50/50** ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells **162/162** ✓ |

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
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells **184/184** ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells **301/301** ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells **42/42** ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells **16/16** ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells **63/63** ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells **30/30** ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **50/50** ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells **162/162** ✓ |

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
| `dbo.authors` | rowstore | 23 | ✓ | **9/9** | **18/18** | ✓ | cells **184/184** ✓ |
| `dbo.discounts` | rowstore | 3 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.employee` | rowstore | 43 | ✓ | **8/8** | **16/16** | ✓ | cells **301/301** ✓ |
| `dbo.jobs` | rowstore | 14 | ✓ | **4/4** | **8/8** | ✓ | cells **42/42** ✓ |
| `dbo.pub_info` | rowstore | 8 | ✓ | **3/3** | **4/4** | ✓ | cells **16/16** ✓ |
| `dbo.publishers` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `dbo.roysched` | rowstore | 86 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.sales` | rowstore | 21 | ✓ | **6/6** | **12/12** | ✓ | cells **63/63** ✓ |
| `dbo.stores` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ | cells **30/30** ✓ |
| `dbo.titleauthor` | rowstore | 25 | ✓ | **4/4** | **8/8** | ✓ | cells **50/50** ✓ |
| `dbo.titles` | rowstore | 18 | ✓ | **10/10** | **20/20** | ✓ | cells **162/162** ✓ |

### `SalesDB2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 28.068 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |

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
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |

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
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |

### `SalesDBOriginal.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 192.081 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells **4/4** ✓ |

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
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells **4/4** ✓ |

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
| `dbo.Customers` | rowstore | 19,759 | ✓ | **4/4** | **8/8** | ✓ | cells **59277/59277** ✓ |
| `dbo.Employees` | rowstore | 23 | ✓ | **4/4** | **8/8** | ✓ | cells **69/69** ✓ |
| `dbo.Products` | rowstore | 504 | ✓ | **3/3** | **6/6** | ✓ | cells **1008/1008** ✓ |
| `dbo.Sales` | rowstore | 6,715,221 | ✓ | **5/5** | **10/10** | ✓ | cells **790028/790028** ✓ |
| `dbo.sysdiagrams` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells **4/4** ✓ |

### `StackOverflowMini.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 758.564 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells **1332219/1332219** ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells **981255/981255** ✓ |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells **2/2** ✓ |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells **3717901/3717901** ✓ |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells **1298297/1298297** ✓ |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells **961290/961290** ✓ |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ | cells **15/15** ✓ |

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
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells **1332219/1332219** ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✓ | **6/6** | **12/12** | ✓ | cells **981255/981255** ✓ |
| `dbo.LinkTypes` | rowstore | 2 | ✓ | **2/2** | **4/4** | ✓ | cells **2/2** ✓ |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✓ | **20/20** | **38/38** | ✓ | cells **3717901/3717901** ✓ |
| `dbo.PostTypes` | rowstore | 8 | ✓ | **2/2** | **4/4** | ✓ | cells **8/8** ✓ |
| `dbo.Users` | rowstore | 99,869 | ✓ | **14/14** | **24/24** | ✓ | cells **1298297/1298297** ✓ |
| `dbo.Votes` | rowstore | 4,614,189 | ✓ | **6/6** | **12/12** | ✓ | cells **961290/961290** ✓ |
| `dbo.VoteTypes` | rowstore | 15 | ✓ | **2/2** | **4/4** | ✓ | cells **15/15** ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ |  |
| `dbo.Comments` | rowstore | 1,373,756 | ✗ | — | — | ✗ | missing from output |
| `dbo.LinkTypes` | rowstore | 2 | ✗ | — | — | ✗ | missing from output |
| `dbo.PostTypes` | rowstore | 8 | ✗ | — | — | ✗ | missing from output |
| `dbo.Posts` | rowstore | 1,565,425 | ✗ | — | — | ✗ | missing from output |
| `dbo.Users` | rowstore | 99,869 | ✗ | — | — | ✗ | missing from output |
| `dbo.VoteTypes` | rowstore | 15 | ✗ | — | — | ✗ | missing from output |
| `dbo.Votes` | rowstore | 4,614,189 | ✗ | — | — | ✗ | missing from output |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.Badges` | rowstore | 444,073 | ✓ | **4/4** | **8/8** | ✓ | cells **1332219/1332219** ✓ |
| `dbo.Comments` | rowstore | 1,373,756 | ✗ | — | — | ✗ | missing from output |
| `dbo.LinkTypes` | rowstore | 2 | ✗ | — | — | ✗ | missing from output |
| `dbo.PostLinks` | rowstore | 0 | — | — | — | — |  |
| `dbo.Posts` | rowstore | 1,565,425 | ✗ | — | — | ✗ | missing from output |
| `dbo.PostTypes` | rowstore | 8 | ✗ | — | — | ✗ | missing from output |
| `dbo.Users` | rowstore | 99,869 | ✗ | — | — | ✗ | missing from output |
| `dbo.Votes` | rowstore | 4,614,189 | ✗ | — | — | ✗ | missing from output |
| `dbo.VoteTypes` | rowstore | 15 | ✗ | — | — | ✗ | missing from output |

### `tpcxbb_1gb.bak` — 2022 — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 233.98 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_address` | columnstore | 49,500 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | columnstore | 109,573 | ✗ | — | — | ✗ | missing from output |
| `dbo.household_demographics` | columnstore | 7,200 | ✗ | — | — | ✗ | missing from output |
| `dbo.income_band` | columnstore | 20 | ✗ | — | — | ✗ | missing from output |
| `dbo.inventory` | columnstore | 23,255,100 | ✗ | — | — | ✗ | missing from output |
| `dbo.item` | columnstore | 17,820 | ✗ | — | — | ✗ | missing from output |
| `dbo.item_marketprices` | columnstore | 89,100 | ✗ | — | — | ✗ | missing from output |
| `dbo.product_reviews` | columnstore | 89,991 | ✗ | — | — | ✗ | missing from output |
| `dbo.promotion` | columnstore | 300 | ✗ | — | — | ✗ | missing from output |
| `dbo.reason` | columnstore | 35 | ✗ | — | — | ✗ | missing from output |
| `dbo.ship_mode` | columnstore | 20 | ✗ | — | — | ✗ | missing from output |
| `dbo.store` | columnstore | 12 | ✗ | — | — | ✗ | missing from output |
| `dbo.store_returns` | columnstore | 37,902 | ✗ | — | — | ✗ | missing from output |
| `dbo.store_sales` | columnstore | 667,579 | ✗ | — | — | ✗ | missing from output |
| `dbo.time_dim` | columnstore | 86,400 | ✗ | — | — | ✗ | missing from output |
| `dbo.warehouse` | columnstore | 5 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_page` | columnstore | 60 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_returns` | columnstore | 38,487 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_sales` | columnstore | 668,052 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_site` | columnstore | 30 | ✗ | — | — | ✗ | missing from output |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells **8/8** ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells **104/104** ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells **40/40** ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells **4/4** ✓ |

#### Stage: arrow→delta

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ |  |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ |  |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ |  |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ |  |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer` | columnstore | 99,000 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_address` | columnstore | 49,500 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.customer_demographics` | columnstore | 1,920,800 | ✗ | — | — | ✗ | missing from output |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `dbo.date_dim` | columnstore | 109,573 | ✗ | — | — | ✗ | missing from output |
| `dbo.household_demographics` | columnstore | 7,200 | ✗ | — | — | ✗ | missing from output |
| `dbo.income_band` | columnstore | 20 | ✗ | — | — | ✗ | missing from output |
| `dbo.inventory` | columnstore | 23,255,100 | ✗ | — | — | ✗ | missing from output |
| `dbo.item` | columnstore | 17,820 | ✗ | — | — | ✗ | missing from output |
| `dbo.item_marketprices` | columnstore | 89,100 | ✗ | — | — | ✗ | missing from output |
| `dbo.product_reviews` | columnstore | 89,991 | ✗ | — | — | ✗ | missing from output |
| `dbo.promotion` | columnstore | 300 | ✗ | — | — | ✗ | missing from output |
| `dbo.reason` | columnstore | 35 | ✗ | — | — | ✗ | missing from output |
| `dbo.ship_mode` | columnstore | 20 | ✗ | — | — | ✗ | missing from output |
| `dbo.store` | columnstore | 12 | ✗ | — | — | ✗ | missing from output |
| `dbo.store_returns` | columnstore | 37,902 | ✗ | — | — | ✗ | missing from output |
| `dbo.store_sales` | columnstore | 667,579 | ✗ | — | — | ✗ | missing from output |
| `dbo.time_dim` | columnstore | 86,400 | ✗ | — | — | ✗ | missing from output |
| `dbo.warehouse` | columnstore | 5 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_clickstreams` | columnstore | 6,770,550 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_page` | columnstore | 60 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_returns` | columnstore | 38,487 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_sales` | columnstore | 668,052 | ✗ | — | — | ✗ | missing from output |
| `dbo.web_site` | columnstore | 30 | ✗ | — | — | ✗ | missing from output |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells **8/8** ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells **104/104** ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells **40/40** ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells **4/4** ✓ |

#### Stage: arrow→pg_dir

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.customer_book_clusters` | rowstore | 4,820 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_clusters` | rowstore | 51,874 | ✓ | **2/2** | **4/4** | ✓ |  |
| `dbo.customer_return_clusters` | rowstore | 37,336 | ✓ | **6/6** | **12/12** | ✓ |  |
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ |  |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ |  |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ |  |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **12/12** | ✓ |  |

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
| `sqlr.model_scoring_history` | rowstore | 1 | ✓ | **9/9** | **16/16** | ✓ | cells **8/8** ✓ |
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **14/14** | **26/26** | ✓ | cells **104/104** ✓ |
| `sqlr.models` | rowstore | 4 | ✓ | **11/11** | **22/22** | ✓ | cells **40/40** ✓ |
| `sqlr.scripts` | rowstore | 1 | ✓ | **6/6** | **10/10** | ✓ | cells **4/4** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImporters-Full_old.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.171 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | memory-optimized | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | columnstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | memory-optimized | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImporters-Standard.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.07 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 37 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImporters-Standard_old.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 121.058 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

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
| `Application.Cities` | rowstore | 37,940 | ✓ | **8/8** | **16/16** | ✓ | cells **265580/265580** ✓ |
| `Application.Cities_Archive` | rowstore | 28 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Application.Countries` | rowstore | 190 | ✓ | **14/14** | **28/28** | ✓ | cells **2470/2470** ✓ |
| `Application.Countries_Archive` | rowstore | 36 | ✓ | **14/14** | **28/28** | ✓ | cells digest ✓ |
| `Application.DeliveryMethods` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Application.DeliveryMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ | cells **16/16** ✓ |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Application.People` | rowstore | 1,111 | ✓ | **19/19** | **36/36** | ✓ | cells **19998/19998** ✓ |
| `Application.People_Archive` | rowstore | 961 | ✓ | **21/21** | **40/40** | ✓ | cells digest ✓ |
| `Application.StateProvinces` | rowstore | 53 | ✓ | **10/10** | **20/20** | ✓ | cells **477/477** ✓ |
| `Application.StateProvinces_Archive` | rowstore | 104 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Application.SystemParameters` | rowstore | 1 | ✓ | **13/13** | **24/24** | ✓ | cells **12/12** ✓ |
| `Application.TransactionTypes` | rowstore | 13 | ✓ | **5/5** | **10/10** | ✓ | cells **52/52** ✓ |
| `Application.TransactionTypes_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.PurchaseOrderLines` | rowstore | 8,367 | ✓ | **12/12** | **24/24** | ✓ | cells **92037/92037** ✓ |
| `Purchasing.PurchaseOrders` | rowstore | 2,074 | ✓ | **12/12** | **20/20** | ✓ | cells **22814/22814** ✓ |
| `Purchasing.SupplierCategories` | rowstore | 9 | ✓ | **5/5** | **10/10** | ✓ | cells **36/36** ✓ |
| `Purchasing.SupplierCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Purchasing.Suppliers` | rowstore | 13 | ✓ | **29/29** | **58/58** | ✓ | cells **364/364** ✓ |
| `Purchasing.Suppliers_Archive` | rowstore | 13 | ✓ | **29/29** | **56/56** | ✓ | cells digest ✓ |
| `Purchasing.SupplierTransactions` | rowstore | 2,438 | ✓ | **14/14** | **28/28** | ✓ | cells **31694/31694** ✓ |
| `Sales.BuyingGroups` | rowstore | 2 | ✓ | **5/5** | **10/10** | ✓ | cells **8/8** ✓ |
| `Sales.BuyingGroups_Archive` | rowstore | 0 | — | — | — | — |  |
| `Sales.CustomerCategories` | rowstore | 8 | ✓ | **5/5** | **10/10** | ✓ | cells **32/32** ✓ |
| `Sales.CustomerCategories_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Sales.Customers` | rowstore | 663 | ✓ | **31/31** | **62/62** | ✓ | cells **19890/19890** ✓ |
| `Sales.Customers_Archive` | rowstore | 51 | ✓ | **31/31** | **58/58** | ✓ | cells digest ✓ |
| `Sales.CustomerTransactions` | rowstore | 97,147 | ✓ | **13/13** | **26/26** | ✓ | cells **1165764/1165764** ✓ |
| `Sales.InvoiceLines` | rowstore | 228,265 | ✓ | **13/13** | **26/26** | ✓ | cells **2739180/2739180** ✓ |
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **23/23** | **40/40** | ✓ | cells **1551220/1551220** ✓ |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ | cells **2545532/2545532** ✓ |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ | cells **1103925/1103925** ✓ |
| `Sales.SpecialDeals` | rowstore | 2 | ✓ | **14/14** | **18/18** | ✓ | cells **26/26** ✓ |
| `Warehouse.ColdRoomTemperatures` | rowstore | 4 | ✓ | **6/6** | **12/12** | ✓ | cells **20/20** ✓ |
| `Warehouse.ColdRoomTemperatures_Archive` | rowstore | 3,654,736 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Warehouse.Colors` | rowstore | 36 | ✓ | **5/5** | **10/10** | ✓ | cells **144/144** ✓ |
| `Warehouse.Colors_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells **56/56** ✓ |
| `Warehouse.PackageTypes_Archive` | rowstore | 0 | — | — | — | — |  |
| `Warehouse.StockGroups` | rowstore | 10 | ✓ | **5/5** | **10/10** | ✓ | cells **40/40** ✓ |
| `Warehouse.StockGroups_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Warehouse.StockItemHoldings` | rowstore | 227 | ✓ | **9/9** | **18/18** | ✓ | cells **1816/1816** ✓ |
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **23/23** | **42/42** | ✓ | cells **4994/4994** ✓ |
| `Warehouse.StockItems_Archive` | rowstore | 444 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Warehouse.StockItemStockGroups` | rowstore | 442 | ✓ | **5/5** | **10/10** | ✓ | cells **1768/1768** ✓ |
| `Warehouse.StockItemTransactions` | rowstore | 236,667 | ✓ | **11/11** | **22/22** | ✓ | cells **2366670/2366670** ✓ |
| `Warehouse.VehicleTemperatures` | rowstore | 65,998 | ✓ | **8/8** | **14/14** | ✓ | cells **461986/461986** ✓ |

### `WideWorldImportersDW-Full.bak` — 2022 — ✗ fail

_SQL Server Microsoft SQL Server 2022 (RTM-CU25-GDR) (KB5095580) - 16.0.4260.1 (X64) · 47.726 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | columnstore | 236,667 | ✗ | — | — | ✗ | missing from output |
| `Fact.Order` | columnstore | 231,412 | ✗ | — | — | ✗ | missing from output |
| `Fact.Purchase` | columnstore | 8,367 | ✗ | — | — | ✗ | missing from output |
| `Fact.Sale` | columnstore | 228,265 | ✗ | — | — | ✗ | missing from output |
| `Fact.Transaction` | columnstore | 99,585 | ✗ | — | — | ✗ | missing from output |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
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
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells: ERROR (key columns ['City Key'] not in decoded table) |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells: ERROR (key columns ['Customer Key'] not in decoded table) |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **2922/2922** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells: ERROR (key columns ['Employee Key'] not in decoded table) |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells: ERROR (key columns ['Supplier Key'] not in decoded table) |
| `Fact.Movement` | columnstore | 236,667 | ✗ | — | — | ✗ | missing from output |
| `Fact.Order` | columnstore | 231,412 | ✗ | — | — | ✗ | missing from output |
| `Fact.Purchase` | columnstore | 8,367 | ✗ | — | — | ✗ | missing from output |
| `Fact.Sale` | columnstore | 228,265 | ✗ | — | — | ✗ | missing from output |
| `Fact.Transaction` | columnstore | 99,585 | ✗ | — | — | ✗ | missing from output |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells: ERROR (key columns ['Lineage Key'] not in decoded table) |
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
| `Dimension.Payment Method` | rowstore | 6 | ✓ | **6/6** | **12/12** | ✓ |  |
| `Dimension.Stock Item` | rowstore | 672 | ✓ | **20/20** | **38/38** | ✓ |  |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **11/11** | **22/22** | ✓ |  |
| `Dimension.Transaction Type` | rowstore | 15 | ✓ | **6/6** | **12/12** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | columnstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells **2130003/2130003** ✓ |
| `Fact.Order` | columnstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells **3934004/3934004** ✓ |
| `Fact.Purchase` | columnstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells **75303/75303** ✓ |
| `Fact.Sale` | columnstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells **4337035/4337035** ✓ |
| `Fact.Transaction` | columnstore | 99,585 | ✓ | — | — | ✓ | cells **1593360/1593360** ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | memory-optimized | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
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
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells **2366670/2366670** ✓ |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells **4165416/4165416** ✓ |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells **83670/83670** ✓ |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells **4565300/4565300** ✓ |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells **1692945/1692945** ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
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
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells: ERROR (key columns ['City Key'] not in decoded table) |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells: ERROR (key columns ['Customer Key'] not in decoded table) |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **2922/2922** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells: ERROR (key columns ['Employee Key'] not in decoded table) |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells: ERROR (key columns ['Supplier Key'] not in decoded table) |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells: ERROR (key columns ['Movement Key'] not in decoded table) |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells: ERROR (key columns ['Order Key'] not in decoded table) |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells: ERROR (key columns ['Purchase Key'] not in decoded table) |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells: ERROR (key columns ['Sale Key'] not in decoded table) |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells: ERROR (key columns ['Transaction Key'] not in decoded table) |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells: ERROR (key columns ['Lineage Key'] not in decoded table) |
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
| `Dimension.City` | rowstore | 116,295 | ✓ | **6/6** | **12/12** | ✓ | cells **1511835/1511835** ✓ |
| `Dimension.Customer` | rowstore | 403 | ✓ | **2/2** | **4/4** | ✓ | cells **4030/4030** ✓ |
| `Dimension.Date` | rowstore | 1,461 | ✓ | **3/3** | **6/6** | ✓ | cells **18993/18993** ✓ |
| `Dimension.Employee` | rowstore | 213 | ✓ | **2/2** | **2/2** | ✓ | cells **1704/1704** ✓ |
| `Dimension.Supplier` | rowstore | 28 | ✓ | **2/2** | **4/4** | ✓ | cells **280/280** ✓ |
| `Fact.Movement` | rowstore | 236,667 | ✓ | **1/1** | **2/2** | ✓ | cells **2366670/2366670** ✓ |
| `Fact.Order` | rowstore | 231,412 | ✓ | **3/3** | **6/6** | ✓ | cells **4165416/4165416** ✓ |
| `Fact.Purchase` | rowstore | 8,367 | ✓ | **1/1** | **2/2** | ✓ | cells **83670/83670** ✓ |
| `Fact.Sale` | rowstore | 228,265 | ✓ | **4/4** | **8/8** | ✓ | cells **4565300/4565300** ✓ |
| `Fact.Transaction` | rowstore | 99,585 | ✓ | — | — | ✓ | cells **1692945/1692945** ✓ |
| `Integration.City_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Customer_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Employee_Staging` | rowstore | 0 | — | — | — | — |  |
| `Integration.Lineage` | rowstore | 13 | ✓ | — | — | ✓ | cells **65/65** ✓ |
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
| `AdventureWorks2008R2.bak` | 28.052s | 23.006s | 51.058s |
| `AdventureWorks2012.bak` | 28.634s | 23.632s | 52.266s |
| `AdventureWorks2014.bak` | 28.745s | 23.603s | 52.348s |
| `AdventureWorks2016.bak` | 28.683s | 23.552s | 52.235s |
| `AdventureWorks2016_EXT.bak` | 58.666s | 41.108s | 99.774s |
| `AdventureWorks2017.bak` | 28.922s | 23.496s | 52.418s |
| `AdventureWorks2019.bak` | 28.346s | 22.693s | 51.039s |
| `AdventureWorks2022.bak` | 28.452s | 22.954s | 51.406s |
| `AdventureWorks2025.bak` | 28.276s | 23.046s | 51.322s |
| `AdventureWorksDW2008R2.bak` | 8.193s | 8.618s | 16.811s |
| `AdventureWorksDW2012.bak` | 20.483s | 24.399s | 44.882s |
| `AdventureWorksDW2014.bak` | 20.484s | 24.529s | 45.013s |
| `AdventureWorksDW2016.bak` | 20.236s | 24.062s | 44.298s |
| `AdventureWorksDW2016_EXT.bak` | 669.763s | 457.237s | 1127.0s |
| `AdventureWorksDW2017.bak` | 20.49s | 24.455s | 44.945s |
| `AdventureWorksDW2019.bak` | 22.294s | 23.902s | 46.196s |
| `AdventureWorksDW2022.bak` | 20.379s | 23.779s | 44.158s |
| `AdventureWorksDW2025.bak` | 20.258s | 24.08s | 44.338s |
| `AdventureWorksLT2012.bak` | 0.329s | 0.325s | 0.654s |
| `AdventureWorksLT2014.bak` | 0.334s | 0.349s | 0.683s |
| `AdventureWorksLT2016.bak` | 0.325s | 0.364s | 0.689s |
| `AdventureWorksLT2017.bak` | 0.332s | 0.363s | 0.695s |
| `AdventureWorksLT2019.bak` | 0.347s | 0.365s | 0.712s |
| `AdventureWorksLT2022.bak` | 0.35s | 0.366s | 0.716s |
| `AdventureWorksLT2025.bak` | 0.378s | 0.387s | 0.765s |
| `BaseballData.bak` | 19.556s | 12.74s | 32.296s |
| `Chinook-id-pk.bak` | 0.311s | 0.34s | 0.651s |
| `Chinook.bak` | 0.291s | 0.347s | 0.638s |
| `ContosoRetailDW.bak` | 963.111s | 1129.32s | 2092.431s |
| `CreditBackup100.bak` | 42.096s | 41.007s | 83.103s |
| `data.gov.bak` | 5.41s | 3.374s | 8.784s |
| `dba.stackexchange.com.bak` | 133.46s | 138.01s | 271.47s |
| `EmployeeCaseStudySampleDB2012.bak` | 7.361s | 2.481s | 9.842s |
| `GeneralHospital.bak` | 80.895s | 49.613s | 130.508s |
| `IndexInternals2008.bak` | 5.594s | 1.559s | 7.153s |
| `Northwinds.bak` | 0.299s | 0.338s | 0.637s |
| `NYCTaxi_Sample.bak` | 48.38s | 57.085s | 105.465s |
| `Pubs.bak` | 0.2s | 0.211s | 0.411s |
| `SalesDB2014.bak` | 50.038s | 54.171s | 104.209s |
| `SalesDBOriginal.bak` | 49.867s | 53.022s | 102.889s |
| `StackOverflowMini.bak` | 186.3s | 71.138s | 257.438s |
| `tpcxbb_1gb.bak` | 204.147s | 214.036s | 418.183s |
| `TutorialDB.bak` | 0.123s | 0.089s | 0.212s |
| `WideWorldImporters-Full.bak` | 100.474s | 97.896s | 198.37s |
| `WideWorldImporters-Full_old.bak` | 99.585s | 98.326s | 197.911s |
| `WideWorldImporters-Standard.bak` | 103.882s | 98.172s | 202.054s |
| `WideWorldImporters-Standard_old.bak` | 104.791s | 97.635s | 202.426s |
| `WideWorldImportersDW-Full.bak` | 19.706s | 21.79s | 41.496s |
| `WideWorldImportersDW-Standard.bak` | 28.364s | 20.627s | 48.991s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis; cell verification dominates for large fixtures)._

## Sink write timings

| Backup | delta write | delta read | pg_dir write | pg_dir read |
|--------|-------:| ------: | -------:| ------:|
| `AdventureWorks2008R2.bak` | 0.418s | 9.108s | 6.25s | 13.329s |
| `AdventureWorks2012.bak` | 0.439s | 9.025s | 6.194s | 13.375s |
| `AdventureWorks2014.bak` | 0.399s | 9.031s | 6.193s | 13.323s |
| `AdventureWorks2016.bak` | 0.401s | 9.047s | 6.246s | 13.192s |
| `AdventureWorks2016_EXT.bak` | 0.716s | 14.278s | 11.912s | 23.092s |
| `AdventureWorks2017.bak` | 0.431s | 9.009s | 6.274s | 13.143s |
| `AdventureWorks2019.bak` | 0.422s | 8.99s | 6.263s | 13.162s |
| `AdventureWorks2022.bak` | 0.422s | 9.104s | 6.287s | 13.267s |
| `AdventureWorks2025.bak` | 0.413s | 8.855s | 6.193s | 12.907s |
| `AdventureWorksDW2008R2.bak` | 0.182s | 3.02s | 3.035s | 5.382s |
| `AdventureWorksDW2012.bak` | 0.311s | 9.022s | 7.85s | 14.765s |
| `AdventureWorksDW2014.bak` | 0.311s | 8.973s | 7.827s | 14.96s |
| `AdventureWorksDW2016.bak` | 0.316s | 8.878s | 7.82s | 14.556s |
| `AdventureWorksDW2016_EXT.bak` | 16.169s | 10.842s | 550.324s | 429.58s |
| `AdventureWorksDW2017.bak` | 0.306s | 8.91s | 7.882s | 14.905s |
| `AdventureWorksDW2019.bak` | 0.321s | 8.965s | 7.883s | 14.658s |
| `AdventureWorksDW2022.bak` | 0.321s | 8.877s | 7.945s | 14.605s |
| `AdventureWorksDW2025.bak` | 0.318s | 8.922s | 7.796s | 14.516s |
| `AdventureWorksLT2012.bak` | 0.034s | 0.115s | 0.041s | 0.15s |
| `AdventureWorksLT2014.bak` | 0.034s | 0.117s | 0.041s | 0.159s |
| `AdventureWorksLT2016.bak` | 0.034s | 0.124s | 0.041s | 0.172s |
| `AdventureWorksLT2017.bak` | 0.035s | 0.122s | 0.04s | 0.17s |
| `AdventureWorksLT2019.bak` | 0.038s | 0.127s | 0.041s | 0.164s |
| `AdventureWorksLT2022.bak` | 0.035s | 0.123s | 0.041s | 0.166s |
| `AdventureWorksLT2025.bak` | 0.039s | 0.121s | 0.041s | 0.16s |
| `BaseballData.bak` | 0.245s | 4.338s | 5.995s | 8.201s |
| `Chinook-id-pk.bak` | 0.029s | 0.125s | 0.059s | 0.145s |
| `Chinook.bak` | 0.03s | 0.129s | 0.058s | 0.153s |
| `ContosoRetailDW.bak` | 16.071s | 381.259s | 478.263s | 735.101s |
| `CreditBackup100.bak` | 0.447s | 16.133s | 11.647s | 23.412s |
| `data.gov.bak` | 0.075s | 0.353s | 2.036s | 2.646s |
| `dba.stackexchange.com.bak` | 3.721s | 17.008s | 23.776s | 108.636s |
| `EmployeeCaseStudySampleDB2012.bak` | 0.108s | 0.383s | 1.619s | 1.643s |
| `GeneralHospital.bak` | 1.046s | 6.913s | 28.755s | 41.849s |
| `IndexInternals2008.bak` | 0.045s | 0.287s | 0.906s | 0.956s |
| `Northwinds.bak` | 0.034s | 0.118s | 0.03s | 0.123s |
| `NYCTaxi_Sample.bak` | 0.905s | 0.0s | 32.718s | 56.796s |
| `Pubs.bak` | 0.028s | 0.073s | 0.007s | 0.057s |
| `SalesDB2014.bak` | 1.257s | 18.711s | 24.067s | 34.463s |
| `SalesDBOriginal.bak` | 1.226s | 18.499s | 24.061s | 34.012s |
| `StackOverflowMini.bak` | 6.597s | 48.382s | 58.649s | 4.798s |
| `tpcxbb_1gb.bak` | 3.424s | 0.716s | 144.537s | 209.943s |
| `TutorialDB.bak` | 0.005s | 0.015s | 0.006s | 0.015s |
| `WideWorldImporters-Full.bak` | 1.262s | 35.806s | 35.73s | 58.918s |
| `WideWorldImporters-Full_old.bak` | 1.202s | 35.58s | 34.837s | 59.538s |
| `WideWorldImporters-Standard.bak` | 1.173s | 35.685s | 35.063s | 59.083s |
| `WideWorldImporters-Standard_old.bak` | 1.257s | 35.13s | 35.744s | 59.027s |
| `WideWorldImportersDW-Full.bak` | 0.307s | 0.123s | 11.716s | 20.372s |
| `WideWorldImportersDW-Standard.bak` | 0.355s | 0.265s | 11.698s | 18.827s |

_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._

---

_Generated 2026-07-14 · 49 fixtures · 45 pass · 0 xfail · 4 fail_
