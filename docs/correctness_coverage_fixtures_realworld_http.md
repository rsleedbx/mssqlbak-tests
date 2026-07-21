# Correctness coverage

Per-backup comparison of mssqlbak extraction against SQL Server ground truth.
Ground truth is recorded in `tests/fixtures/<name>.bak.stats.json` by
`python -m tools.fixture_run register-bak <name>.bak` on a live SQL Server instance.
**Generated** by `python -m tools.correctness_coverage --fixture-dir tests/fixtures_realworld`.

**49 fixtures · 49 pass · 0 xfail (known gap) · 0 fail**

**Tables:** 7133/7133 pass · **Columns:** 63913/63913 pass

**Row count:** ✓ · **Null count:** ✓ · **Min/max:** ✓ · **Col count:** ✓ · **Cells:** ✓

**Edges:** mssql→arrow ✓ · arrow→delta ✓ · delta→arrow ✓ · arrow→pg_dir ✓ · pg_dir→arrow ✓

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

**Metadata:** 153/153 fixture-categories pass (constraints: 17/17, indexes: 17/17, extended_properties: 17/17, modules: 17/17, schema_objects: 17/17, security: 17/17, statistics: 17/17, plan_guides: 17/17, query_store: 17/17)

## Summary

| Backup | Stage | Source rows | Source cols | Row count | Null count | Min/max | Col count | Cells | Status |
|--------|-------|------------:|------------:|:---------:|:----------:|:-------:|:---------:|:-----:|--------|
| `AdventureWorks2008R2.bak` | mssql→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2008R2.bak` | arrow→delta | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2008R2.bak` | delta→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2008R2.bak` | arrow→pg_dir | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2008R2.bak` | pg_dir→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | mssql→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | arrow→delta | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2012.bak` | delta→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2012.bak` | arrow→pg_dir | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2012.bak` | pg_dir→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | mssql→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | arrow→delta | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2014.bak` | delta→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2014.bak` | arrow→pg_dir | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2014.bak` | pg_dir→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | mssql→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | arrow→delta | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2016.bak` | delta→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2016.bak` | arrow→pg_dir | 760,838 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2016.bak` | pg_dir→arrow | 760,838 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | mssql→arrow | 1,378,717 | 731 | **92/92** | **697/697** | **1314/1314** | **92/92** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→delta | 1,378,717 | 731 | **89/89** | **713/713** | **1386/1386** | **89/89** | — | ✓ |
| `AdventureWorks2016_EXT.bak` | delta→arrow | 1,378,717 | 731 | **92/92** | **697/697** | **1314/1314** | **92/92** | digest | ✓ |
| `AdventureWorks2016_EXT.bak` | arrow→pg_dir | 1,378,717 | 731 | **89/89** | **713/713** | **1386/1386** | **89/89** | — | ✓ |
| `AdventureWorks2016_EXT.bak` | pg_dir→arrow | 1,378,717 | 731 | **92/92** | **697/697** | **1314/1314** | **92/92** | digest | ✓ |
| `AdventureWorks2017.bak` | mssql→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2017.bak` | arrow→delta | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2017.bak` | delta→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2017.bak` | arrow→pg_dir | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2017.bak` | pg_dir→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | mssql→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | arrow→delta | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2019.bak` | delta→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2019.bak` | arrow→pg_dir | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2019.bak` | pg_dir→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | mssql→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | arrow→delta | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2022.bak` | delta→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2022.bak` | arrow→pg_dir | 760,837 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2022.bak` | pg_dir→arrow | 760,837 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | mssql→arrow | 760,167 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | arrow→delta | 760,167 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2025.bak` | delta→arrow | 760,167 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorks2025.bak` | arrow→pg_dir | 760,167 | 476 | **70/70** | **477/477** | **932/932** | **70/70** | — | ✓ |
| `AdventureWorks2025.bak` | pg_dir→arrow | 760,167 | 476 | **71/71** | **467/467** | **872/872** | **71/71** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | mssql→arrow | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→delta | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | delta→arrow | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | digest | ✓ |
| `AdventureWorksDW2008R2.bak` | arrow→pg_dir | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | — | ✓ |
| `AdventureWorksDW2008R2.bak` | pg_dir→arrow | 282,030 | 327 | **28/28** | **327/327** | **646/646** | **28/28** | digest | ✓ |
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
| `AdventureWorksLT2012.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2012.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2012.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2012.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2014.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2014.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2016.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2016.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2017.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2017.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2019.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2019.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2022.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2022.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | mssql→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | arrow→delta | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | delta→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
| `AdventureWorksLT2025.bak` | arrow→pg_dir | 4,277 | 106 | **11/11** | **100/100** | **188/188** | **11/11** | — | ✓ |
| `AdventureWorksLT2025.bak` | pg_dir→arrow | 4,277 | 106 | **12/12** | **97/97** | **168/168** | **12/12** | digest | ✓ |
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
| `tpcxbb_1gb.bak` | arrow→delta | 34,001,580 | 394 | **30/30** | **395/395** | **776/776** | **30/30** | — | ✓ |
| `tpcxbb_1gb.bak` | delta→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | digest | ✓ |
| `tpcxbb_1gb.bak` | arrow→pg_dir | 34,001,580 | 394 | **30/30** | **395/395** | **776/776** | **30/30** | — | ✓ |
| `tpcxbb_1gb.bak` | pg_dir→arrow | 34,001,580 | 394 | **30/30** | **394/394** | **774/774** | **30/30** | digest | ✓ |
| `TutorialDB.bak` | mssql→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→delta | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | delta→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `TutorialDB.bak` | arrow→pg_dir | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | — | ✓ |
| `TutorialDB.bak` | pg_dir→arrow | 453 | 10 | **1/1** | **10/10** | **20/20** | **1/1** | digest | ✓ |
| `WideWorldImporters-Full.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **548/548** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **548/548** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **548/548** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Full_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **548/548** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Full_old.bak` | pg_dir→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | mssql→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→delta | 4,713,833 | 549 | **46/46** | **547/547** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | delta→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard.bak` | arrow→pg_dir | 4,713,833 | 549 | **46/46** | **547/547** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard.bak` | pg_dir→arrow | 4,713,833 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | mssql→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→delta | 4,713,832 | 549 | **46/46** | **547/547** | **1038/1038** | **46/46** | — | ✓ |
| `WideWorldImporters-Standard_old.bak` | delta→arrow | 4,713,832 | 549 | **48/48** | **539/539** | **1030/1030** | **48/48** | digest | ✓ |
| `WideWorldImporters-Standard_old.bak` | arrow→pg_dir | 4,713,832 | 549 | **46/46** | **547/547** | **1038/1038** | **46/46** | — | ✓ |
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

### `AdventureWorks2008R2.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 181.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

### `AdventureWorks2012.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 44.897 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

### `AdventureWorks2014.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 44.594 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

### `AdventureWorks2016.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU5) (KB5084896) - 17.0.4045.5 (X64) · 46.491 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,597 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 125.034 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
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
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **14/14** | **28/28** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **29/29** | **52/52** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
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
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **9/9** | **18/18** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
| `HumanResources.EmployeeDepartmentHistory` | rowstore | 296 | ✓ | **6/6** | **12/12** | ✓ |  |
| `HumanResources.EmployeePayHistory` | rowstore | 316 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee_Temporal` | rowstore | 290 | ✓ | **14/14** | **28/28** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
| `Sales.SalesOrderHeaderSalesReason` | rowstore | 27,647 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrderHeader_ondisk` | rowstore | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **29/29** | **52/52** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 179 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `Demo.DemoSalesOrderDetailSeed` | memory-optimized | 538 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Demo.DemoSalesOrderHeaderSeed` | memory-optimized | 31,465 | ✓ | **7/7** | **14/14** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_json` | rowstore | 19,972 | ✓ | **15/15** | **24/24** | ✓ | cells digest ✓ |
| `Person.Person_Temporal` | rowstore | 19,972 | ✓ | **11/11** | **22/22** | ✓ | cells digest ✓ |
| `Person.Person_Temporal_History` | rowstore | 0 | — | — | — | — |  |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.Product_inmem` | memory-optimized | 504 | ✓ | **24/24** | **46/46** | ✓ |  |
| `Production.Product_ondisk` | rowstore | 504 | ✓ | **24/24** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.CustomerPII` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.OrderTracking` | rowstore | 188,790 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrder_json` | rowstore | 31,465 | ✓ | **27/27** | **50/50** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail_inmem` | memory-optimized | 121,317 | ✓ | **9/9** | **18/18** | ✓ |  |
| `Sales.SalesOrderDetail_ondisk` | rowstore | 121,317 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader_inmem` | memory-optimized | 31,465 | ✓ | **23/23** | **44/44** | ✓ |  |
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
| `Sales.SpecialOffer_inmem` | memory-optimized | 16 | ✓ | **10/10** | **20/20** | ✓ |  |
| `Sales.SpecialOffer_ondisk` | rowstore | 16 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct` | rowstore | 538 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SpecialOfferProduct_inmem` | memory-optimized | 538 | ✓ | **3/3** | **6/6** | ✓ |  |
| `Sales.SpecialOfferProduct_ondisk` | rowstore | 538 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.Store` | rowstore | 701 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.TrackingEvent` | rowstore | 7 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |

### `AdventureWorks2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 47.957 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 199.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 200.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 13 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 1,596 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 13 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2025 (RTM-CU7) (KB5096981) - 17.0.4065.4 (X64) · 47.902 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 12 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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
| `Sales.Customer` | rowstore | 19,820 | ✓ | **7/7** | **12/12** | ✓ |  |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ |  |
| `Production.Document` | rowstore | 12 | ✓ | **14/14** | **26/26** | ✓ |  |
| `Person.EmailAddress` | rowstore | 19,972 | ✓ | **5/5** | **10/10** | ✓ |  |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **16/16** | **30/30** | ✓ |  |
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
| `Purchasing.PurchaseOrderDetail` | rowstore | 8,845 | ✓ | **11/11** | **18/18** | ✓ |  |
| `Purchasing.PurchaseOrderHeader` | rowstore | 4,012 | ✓ | **13/13** | **26/26** | ✓ |  |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **11/11** | **20/20** | ✓ |  |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **26/26** | **46/46** | ✓ |  |
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
| `Production.WorkOrder` | rowstore | 72,591 | ✓ | **10/10** | **18/18** | ✓ |  |
| `Production.WorkOrderRouting` | rowstore | 67,131 | ✓ | **12/12** | **24/24** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AWBuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 927 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `HumanResources.Department` | rowstore | 16 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `HumanResources.Employee` | rowstore | 290 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
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
| `Person.Person` | rowstore | 19,972 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Person.PersonPhone` | rowstore | 19,972 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Person.PhoneNumberType` | rowstore | 3 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Person.StateProvince` | rowstore | 181 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `Production.BillOfMaterials` | rowstore | 2,679 | ✓ | **9/9** | **18/18** | ✓ | cells digest ✓ |
| `Production.Culture` | rowstore | 8 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Document` | rowstore | 12 | ✓ | **13/13** | **24/24** | ✓ | cells digest ✓ |
| `Production.Illustration` | rowstore | 5 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.Location` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.Product` | rowstore | 504 | ✓ | **25/25** | **46/46** | ✓ | cells digest ✓ |
| `Production.ProductCategory` | rowstore | 4 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductCostHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductDocument` | rowstore | 32 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductInventory` | rowstore | 1,069 | ✓ | **7/7** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductListPriceHistory` | rowstore | 395 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModel` | rowstore | 128 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Production.ProductModelIllustration` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Production.ProductModelProductDescriptionCulture` | rowstore | 762 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductPhoto` | rowstore | 101 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Production.ProductProductPhoto` | rowstore | 504 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `Production.ProductReview` | rowstore | 4 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
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
| `Purchasing.Vendor` | rowstore | 104 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `Sales.CountryRegionCurrency` | rowstore | 109 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CreditCard` | rowstore | 19,118 | ✓ | **6/6** | **12/12** | ✓ | cells digest ✓ |
| `Sales.Currency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.CurrencyRate` | rowstore | 13,532 | ✓ | **7/7** | **14/14** | ✓ | cells digest ✓ |
| `Sales.Customer` | rowstore | 19,820 | ✓ | **6/6** | **10/10** | ✓ | cells digest ✓ |
| `Sales.PersonCreditCard` | rowstore | 19,118 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `Sales.SalesOrderDetail` | rowstore | 121,317 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `Sales.SalesOrderHeader` | rowstore | 31,465 | ✓ | **24/24** | **44/44** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 74.109 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.AdventureWorksDWBuildVersion` | rowstore | 1 | ✓ | **2/2** | **4/4** | ✓ | cells digest ✓ |
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
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
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
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
| `dbo.DatabaseLog` | rowstore | 115 | ✓ | **8/8** | **16/16** | ✓ | cells digest ✓ |
| `dbo.DimAccount` | rowstore | 99 | ✓ | **10/10** | **18/18** | ✓ | cells digest ✓ |
| `dbo.DimCurrency` | rowstore | 105 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimCustomer` | rowstore | 18,484 | ✓ | **29/29** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimDate` | rowstore | 1,188 | ✓ | **19/19** | **38/38** | ✓ | cells digest ✓ |
| `dbo.DimDepartmentGroup` | rowstore | 7 | ✓ | **3/3** | **6/6** | ✓ | cells digest ✓ |
| `dbo.DimEmployee` | rowstore | 296 | ✓ | **30/30** | **58/58** | ✓ | cells digest ✓ |
| `dbo.DimGeography` | rowstore | 655 | ✓ | **10/10** | **20/20** | ✓ | cells digest ✓ |
| `dbo.DimOrganization` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ | cells digest ✓ |
| `dbo.DimProduct` | rowstore | 606 | ✓ | **36/36** | **72/72** | ✓ | cells digest ✓ |
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

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.426 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2014.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 13.336 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2016.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2017.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 7.113 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2019.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2022.bak` — 2022 — ✓ pass

_SQL Server Microsoft SQL Server 2022 (RTM-CU24) (KB5080999) - 16.0.4245.2 (X64) · 8.117 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

### `AdventureWorksLT2025.bak` — 2025 — ✓ pass

_SQL Server Microsoft SQL Server 2025 (RTM-CU7) (KB5096981) - 17.0.4065.4 (X64) · 1.684 MB_

#### Stage: mssql→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: delta→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **9/9** | **16/16** | ✓ |  |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **22/22** | **36/36** | ✓ |  |

#### Stage: pg_dir→arrow

| Table | Type | Source rows | Row count | Null count | Min/max | Col count | Notes |
|-------|------|------------:|:---------:|:----------:|:-------:|:---------:|-------|
| `dbo.BuildVersion` | rowstore | 1 | ✓ | **4/4** | **8/8** | ✓ | cells digest ✓ |
| `dbo.ErrorLog` | rowstore | 0 | — | — | — | — |  |
| `SalesLT.Address` | rowstore | 450 | ✓ | **9/9** | **16/16** | ✓ | cells digest ✓ |
| `SalesLT.Customer` | rowstore | 847 | ✓ | **15/15** | **28/28** | ✓ | cells digest ✓ |
| `SalesLT.CustomerAddress` | rowstore | 417 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.Product` | rowstore | 295 | ✓ | **17/17** | **30/30** | ✓ | cells digest ✓ |
| `SalesLT.ProductCategory` | rowstore | 41 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductDescription` | rowstore | 762 | ✓ | **4/4** | **6/6** | ✓ | cells digest ✓ |
| `SalesLT.ProductModel` | rowstore | 128 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.ProductModelProductDescription` | rowstore | 762 | ✓ | **5/5** | **8/8** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderDetail` | rowstore | 542 | ✓ | **8/8** | **14/14** | ✓ | cells digest ✓ |
| `SalesLT.SalesOrderHeader` | rowstore | 32 | ✓ | **20/20** | **34/34** | ✓ | cells digest ✓ |

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
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **15/15** | **26/26** | ✓ |  |
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
| `sqlr.model_training_history` | rowstore | 8 | ✓ | **15/15** | **26/26** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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
| `Sales.Invoices` | rowstore | 70,510 | ✓ | **25/25** | **40/40** | ✓ |  |
| `Sales.OrderLines` | rowstore | 231,412 | ✓ | **12/12** | **24/24** | ✓ |  |
| `Sales.Orders` | rowstore | 73,595 | ✓ | **16/16** | **26/26** | ✓ |  |
| `Warehouse.PackageTypes` | rowstore | 14 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods` | rowstore | 4 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.PaymentMethods_Archive` | rowstore | 1 | ✓ | **5/5** | **10/10** | ✓ |  |
| `Application.People` | rowstore | 1,111 | ✓ | **21/21** | **38/38** | ✓ |  |
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
| `Warehouse.StockItems` | rowstore | 227 | ✓ | **25/25** | **42/42** | ✓ |  |
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


## Metadata validation

Metadata ground truth is collected from the live SQL Server restore into `<bak>.metadata.json` by `python -m tools.fixture_run register-metadata-all`. Only fixtures with a sidecar are scored here; others show `—` (unscored).

| Backup | constraints | indexes | extended_properties | modules | schema_objects | security | statistics | plan_guides | query_store |
|--------|:---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------: | :---------:|
| `AdventureWorks2008R2.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2012.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2014.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2016.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2016_EXT.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2017.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2019.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2022.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorks2025.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksDW2008R2.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2012.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2014.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2016.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2017.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2019.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2022.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AdventureWorksLT2025.bak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Extraction timings

| Backup | Extract | Verify | Wall time |
|--------|---------|--------|-----------|
| `AdventureWorks2008R2.bak` | 16.878s | 10.048s | 26.926s |
| `AdventureWorks2012.bak` | 17.736s | 10.525s | 28.261s |
| `AdventureWorks2014.bak` | 17.781s | 10.862s | 28.643s |
| `AdventureWorks2016.bak` | 18.023s | 10.834s | 28.857s |
| `AdventureWorks2016_EXT.bak` | 39.875s | 18.66s | 58.535s |
| `AdventureWorks2017.bak` | 17.879s | 10.651s | 28.53s |
| `AdventureWorks2019.bak` | 17.055s | 9.934s | 26.989s |
| `AdventureWorks2022.bak` | 16.986s | 9.906s | 26.892s |
| `AdventureWorks2025.bak` | 17.376s | 10.722s | 28.098s |
| `AdventureWorksDW2008R2.bak` | 3.257s | 3.132s | 6.389s |
| `AdventureWorksDW2012.bak` | 6.996s | 7.77s | 14.766s |
| `AdventureWorksDW2014.bak` | 7.024s | 7.606s | 14.63s |
| `AdventureWorksDW2016.bak` | 6.718s | 7.543s | 14.261s |
| `AdventureWorksDW2016_EXT.bak` | 103.778s | 60.51s | 164.288s |
| `AdventureWorksDW2017.bak` | 6.959s | 7.874s | 14.833s |
| `AdventureWorksDW2019.bak` | 8.445s | 7.69s | 16.135s |
| `AdventureWorksDW2022.bak` | 6.572s | 7.698s | 14.27s |
| `AdventureWorksDW2025.bak` | 6.67s | 7.506s | 14.176s |
| `AdventureWorksLT2012.bak` | 0.276s | 0.425s | 0.701s |
| `AdventureWorksLT2014.bak` | 0.342s | 0.461s | 0.803s |
| `AdventureWorksLT2016.bak` | 0.279s | 0.433s | 0.712s |
| `AdventureWorksLT2017.bak` | 0.324s | 0.454s | 0.778s |
| `AdventureWorksLT2019.bak` | 0.302s | 0.473s | 0.775s |
| `AdventureWorksLT2022.bak` | 0.306s | 0.467s | 0.773s |
| `AdventureWorksLT2025.bak` | 0.382s | 0.495s | 0.877s |
| `BaseballData.bak` | 11.075s | 4.551s | 15.626s |
| `Chinook-id-pk.bak` | 0.216s | 0.225s | 0.441s |
| `Chinook.bak` | 0.287s | 0.235s | 0.522s |
| `ContosoRetailDW.bak` | 248.882s | 372.934s | 621.816s |
| `CreditBackup100.bak` | 25.089s | 21.341s | 46.43s |
| `data.gov.bak` | 2.81s | 1.73s | 4.54s |
| `dba.stackexchange.com.bak` | 110.705s | 118.214s | 228.919s |
| `EmployeeCaseStudySampleDB2012.bak` | 6.26s | 1.95s | 8.21s |
| `GeneralHospital.bak` | 42.676s | 30.027s | 72.703s |
| `IndexInternals2008.bak` | 4.823s | 0.976s | 5.799s |
| `Northwinds.bak` | 0.292s | 0.252s | 0.544s |
| `NYCTaxi_Sample.bak` | 39.212s | 54.081s | 93.293s |
| `Pubs.bak` | 0.251s | 0.189s | 0.44s |
| `SalesDB2014.bak` | 11.871s | 11.141s | 23.012s |
| `SalesDBOriginal.bak` | 11.385s | 10.632s | 22.017s |
| `StackOverflowMini.bak` | 112.443s | 171.246s | 283.689s |
| `tpcxbb_1gb.bak` | 100.784s | 89.794s | 190.578s |
| `TutorialDB.bak` | 0.14s | 0.039s | 0.179s |
| `WideWorldImporters-Full.bak` | 48.62s | 39.363s | 87.983s |
| `WideWorldImporters-Full_old.bak` | 47.415s | 37.347s | 84.762s |
| `WideWorldImporters-Standard.bak` | 50.95s | 37.008s | 87.958s |
| `WideWorldImporters-Standard_old.bak` | 51.335s | 37.972s | 89.307s |
| `WideWorldImportersDW-Full.bak` | 11.011s | 9.387s | 20.398s |
| `WideWorldImportersDW-Standard.bak` | 9.819s | 9.651s | 19.47s |

_Verify = wall − extract (Arrow conversion, ground-truth compare, cell verification, and confidence analysis). See **Sink read breakdown** below for the per-phase split._

## Extract phase breakdown

| Backup | pagestore | schema | catalog | constraints | logtail | xtp | data decode (net) | sink write | arrow verify | sink finish |
|--------|----------:|-------:|--------:|------------:|--------:|---:|------------------:|-----------:|-------------:|------------:|
| `AdventureWorks2008R2.bak` | 0.667s | 0.133s | 0.0s | 0.0s | 0.121s | 0.0s | 15.533s | 4.245s | 3.577s | 0.405s |
| `AdventureWorks2012.bak` | 1.558s | 0.158s | 0.0s | 0.0s | 0.052s | 0.0s | 15.523s | 4.199s | 3.606s | 0.416s |
| `AdventureWorks2014.bak` | 1.532s | 0.164s | 0.0s | 0.0s | 0.051s | 0.0s | 15.598s | 4.533s | 3.652s | 0.411s |
| `AdventureWorks2016.bak` | 1.668s | 0.189s | 0.0s | 0.0s | 0.107s | 0.0s | 15.6s | 4.327s | 3.658s | 0.417s |
| `AdventureWorks2016_EXT.bak` | 4.489s | 0.207s | 0.0s | 0.0s | 0.251s | 8.002s | 26.451s | 6.057s | 5.163s | 0.427s |
| `AdventureWorks2017.bak` | 1.672s | 0.161s | 0.0s | 0.0s | 0.056s | 0.0s | 15.555s | 4.227s | 3.616s | 0.412s |
| `AdventureWorks2019.bak` | 0.729s | 0.168s | 0.0s | 0.0s | 0.122s | 0.0s | 15.611s | 4.567s | 3.572s | 0.405s |
| `AdventureWorks2022.bak` | 0.713s | 0.186s | 0.0s | 0.0s | 0.117s | 0.0s | 15.537s | 4.011s | 3.613s | 0.414s |
| `AdventureWorks2025.bak` | 1.596s | 0.167s | 0.0s | 0.0s | 0.054s | 0.0s | 15.122s | 4.237s | 3.526s | 0.408s |
| `AdventureWorksDW2008R2.bak` | 0.313s | 0.055s | 0.0s | 0.0s | 0.12s | 0.0s | 2.74s | 0.981s | 0.997s | 0.013s |
| `AdventureWorksDW2012.bak` | 0.815s | 0.083s | 0.0s | 0.0s | 0.025s | 0.0s | 6.044s | 1.42s | 3.086s | 0.005s |
| `AdventureWorksDW2014.bak` | 0.838s | 0.139s | 0.0s | 0.0s | 0.024s | 0.0s | 5.994s | 1.428s | 3.039s | 0.005s |
| `AdventureWorksDW2016.bak` | 0.813s | 0.078s | 0.0s | 0.0s | 0.028s | 0.0s | 5.768s | 1.429s | 3.004s | 0.006s |
| `AdventureWorksDW2016_EXT.bak` | 31.742s | 0.111s | 0.0s | 0.0s | 1.946s | 0.0s | 69.937s | 51.998s | 2.97s | 0.011s |
| `AdventureWorksDW2017.bak` | 0.869s | 0.088s | 0.0s | 0.0s | 0.026s | 0.0s | 5.943s | 1.445s | 3.007s | 0.006s |
| `AdventureWorksDW2019.bak` | 0.414s | 0.105s | 0.0s | 0.0s | 0.127s | 0.0s | 7.772s | 2.034s | 3.057s | 0.005s |
| `AdventureWorksDW2022.bak` | 0.411s | 0.105s | 0.0s | 0.0s | 0.123s | 0.0s | 5.906s | 1.439s | 2.991s | 0.005s |
| `AdventureWorksDW2025.bak` | 0.848s | 0.118s | 0.0s | 0.0s | 0.028s | 0.0s | 5.645s | 1.292s | 2.986s | 0.005s |
| `AdventureWorksLT2012.bak` | 0.044s | 0.032s | 0.0s | 0.0s | 0.024s | 0.0s | 0.15s | 0.112s | 0.074s | 0.008s |
| `AdventureWorksLT2014.bak` | 0.099s | 0.036s | 0.0s | 0.0s | 0.025s | 0.0s | 0.153s | 0.113s | 0.075s | 0.009s |
| `AdventureWorksLT2016.bak` | 0.042s | 0.037s | 0.0s | 0.0s | 0.015s | 0.0s | 0.162s | 0.121s | 0.08s | 0.009s |
| `AdventureWorksLT2017.bak` | 0.048s | 0.038s | 0.0s | 0.0s | 0.025s | 0.0s | 0.186s | 0.119s | 0.107s | 0.009s |
| `AdventureWorksLT2019.bak` | 0.057s | 0.039s | 0.0s | 0.0s | 0.018s | 0.0s | 0.165s | 0.12s | 0.081s | 0.01s |
| `AdventureWorksLT2022.bak` | 0.067s | 0.044s | 0.0s | 0.0s | 0.015s | 0.0s | 0.156s | 0.12s | 0.073s | 0.009s |
| `AdventureWorksLT2025.bak` | 0.123s | 0.045s | 0.0s | 0.0s | 0.004s | 0.0s | 0.161s | 0.117s | 0.081s | 0.009s |
| `BaseballData.bak` | 0.276s | 0.076s | 0.0s | 0.0s | 0.114s | 0.0s | 10.579s | 2.39s | 1.582s | 0.006s |
| `Chinook-id-pk.bak` | 0.042s | 0.039s | 0.0s | 0.0s | 0.022s | 0.0s | 0.086s | 0.062s | 0.069s | 0.008s |
| `Chinook.bak` | 0.041s | 0.052s | 0.0s | 0.0s | 0.024s | 0.0s | 0.139s | 0.092s | 0.122s | 0.009s |
| `ContosoRetailDW.bak` | 14.131s | 0.099s | 0.0s | 0.0s | 1.914s | 0.0s | 232.71s | 39.995s | 170.141s | 0.002s |
| `CreditBackup100.bak` | 1.511s | 0.03s | 0.0s | 0.0s | 0.065s | 0.0s | 23.439s | 4.057s | 10.354s | 0.009s |
| `data.gov.bak` | 0.509s | 0.053s | 0.0s | 0.0s | 0.014s | 0.0s | 1.708s | 0.323s | 0.467s | 0.496s |
| `dba.stackexchange.com.bak` | 15.364s | 0.073s | 0.0s | 0.0s | 0.968s | 0.0s | 92.959s | 13.327s | 16.408s | 1.312s |
| `EmployeeCaseStudySampleDB2012.bak` | 0.642s | 0.063s | 0.0s | 0.0s | 0.017s | 0.0s | 5.204s | 0.898s | 0.641s | 0.305s |
| `GeneralHospital.bak` | 1.136s | 0.073s | 0.0s | 0.0s | 0.157s | 0.0s | 41.151s | 8.247s | 8.597s | 0.135s |
| `IndexInternals2008.bak` | 0.464s | 0.029s | 0.0s | 0.0s | 0.008s | 0.0s | 4.163s | 0.536s | 0.258s | 0.128s |
| `Northwinds.bak` | 0.1s | 0.032s | 0.0s | 0.0s | 0.001s | 0.0s | 0.132s | 0.084s | 0.084s | 0.007s |
| `NYCTaxi_Sample.bak` | 2.406s | 0.065s | 0.0s | 0.0s | 0.119s | 0.0s | 12.666s | 8.596s | 22.96s | 23.94s |
| `Pubs.bak` | 0.084s | 0.028s | 0.0s | 0.0s | 0.001s | 0.0s | 0.111s | 0.082s | 0.086s | 0.006s |
| `SalesDB2014.bak` | 1.162s | 0.062s | 0.0s | 0.0s | 0.035s | 0.0s | 5.385s | 2.563s | 5.22s | 5.204s |
| `SalesDBOriginal.bak` | 0.661s | 0.03s | 0.0s | 0.0s | 0.131s | 0.0s | 10.535s | 2.487s | 5.123s | 0.005s |
| `StackOverflowMini.bak` | 22.013s | 0.074s | 0.0s | 0.0s | 1.749s | 0.0s | 81.48s | 18.992s | 37.921s | 7.098s |
| `tpcxbb_1gb.bak` | 11.188s | 0.085s | 0.0s | 0.0s | 0.556s | 0.0s | 88.672s | 15.131s | 41.216s | 0.255s |
| `TutorialDB.bak` | 0.055s | 0.024s | 0.0s | 0.0s | 0.001s | 0.0s | 0.001s | 0.023s | 0.037s | 0.038s |
| `WideWorldImporters-Full.bak` | 4.213s | 0.104s | 0.0s | 0.0s | 0.204s | 4.371s | 39.47s | 7.0s | 17.906s | 0.216s |
| `WideWorldImporters-Full_old.bak` | 4.154s | 0.101s | 0.0s | 0.0s | 0.204s | 4.207s | 38.503s | 7.059s | 17.5s | 0.213s |
| `WideWorldImporters-Standard.bak` | 4.435s | 0.104s | 0.0s | 0.0s | 0.211s | 0.0s | 45.97s | 7.489s | 17.065s | 0.206s |
| `WideWorldImporters-Standard_old.bak` | 4.371s | 0.104s | 0.0s | 0.0s | 0.205s | 0.0s | 46.417s | 7.443s | 17.324s | 0.213s |
| `WideWorldImportersDW-Full.bak` | 1.715s | 0.053s | 0.0s | 0.0s | 0.057s | 1.3s | 7.859s | 1.631s | 4.07s | 0.001s |
| `WideWorldImportersDW-Standard.bak` | 1.923s | 0.047s | 0.0s | 0.0s | 0.061s | 0.0s | 7.757s | 1.399s | 4.094s | 0.002s |

_data decode (net) = data\_decode\_s (raw loop wall; sink writes and arrow verify overlap decode on a background writer thread and are drained in sink finish). catalog = recover\_catalog\_objects (indexes/FKs/constraints, pg\_dir only). arrow verify = cell verification run inside extraction (_StreamingStatsSink). verify=digest: per-column SHA-256 aggregate hash — fast, no GT parquet read, catches multiset-level corruption; also runs key-ordered digest (catches row transposition) when ordered\_digest is present in the manifest (populated by backfill\_ordered\_digest). Mismatches show as digest:col (multiset) or order:col (transposition). verify=full: exhaustive keyed row compare — also catches value-preserving row misalignment._

## Sink write timings

| Backup | delta write | delta read | pg_dir write | pg_dir read |
|--------|-------:| ------: | -------:| ------:|
| `AdventureWorks2008R2.bak` | 1.022s | 4.146s | 3.223s | 5.161s |
| `AdventureWorks2012.bak` | 0.963s | 4.22s | 3.236s | 4.974s |
| `AdventureWorks2014.bak` | 0.997s | 4.375s | 3.536s | 5.099s |
| `AdventureWorks2016.bak` | 1.018s | 4.21s | 3.309s | 5.049s |
| `AdventureWorks2016_EXT.bak` | 1.452s | 5.973s | 4.605s | 8.782s |
| `AdventureWorks2017.bak` | 1.029s | 4.163s | 3.198s | 4.96s |
| `AdventureWorks2019.bak` | 0.988s | 4.11s | 3.579s | 5.106s |
| `AdventureWorks2022.bak` | 1.031s | 4.208s | 2.98s | 5.061s |
| `AdventureWorks2025.bak` | 0.954s | 4.165s | 3.283s | 4.995s |
| `AdventureWorksDW2008R2.bak` | 0.27s | 1.225s | 0.711s | 1.752s |
| `AdventureWorksDW2012.bak` | 0.417s | 3.299s | 1.003s | 4.42s |
| `AdventureWorksDW2014.bak` | 0.411s | 3.331s | 1.017s | 4.229s |
| `AdventureWorksDW2016.bak` | 0.446s | 3.234s | 0.983s | 4.258s |
| `AdventureWorksDW2016_EXT.bak` | 17.063s | 7.673s | 34.935s | 52.682s |
| `AdventureWorksDW2017.bak` | 0.407s | 3.344s | 1.038s | 4.468s |
| `AdventureWorksDW2019.bak` | 0.551s | 3.363s | 1.483s | 4.26s |
| `AdventureWorksDW2022.bak` | 0.434s | 3.24s | 1.005s | 4.41s |
| `AdventureWorksDW2025.bak` | 0.406s | 3.212s | 0.886s | 4.246s |
| `AdventureWorksLT2012.bak` | 0.064s | 0.121s | 0.048s | 0.137s |
| `AdventureWorksLT2014.bak` | 0.062s | 0.13s | 0.051s | 0.148s |
| `AdventureWorksLT2016.bak` | 0.065s | 0.117s | 0.056s | 0.14s |
| `AdventureWorksLT2017.bak` | 0.066s | 0.124s | 0.053s | 0.146s |
| `AdventureWorksLT2019.bak` | 0.064s | 0.126s | 0.056s | 0.141s |
| `AdventureWorksLT2022.bak` | 0.065s | 0.129s | 0.055s | 0.144s |
| `AdventureWorksLT2025.bak` | 0.064s | 0.125s | 0.053s | 0.138s |
| `BaseballData.bak` | 0.532s | 1.941s | 1.858s | 2.561s |
| `Chinook-id-pk.bak` | 0.038s | 0.12s | 0.024s | 0.079s |
| `Chinook.bak` | 0.043s | 0.121s | 0.049s | 0.087s |
| `ContosoRetailDW.bak` | 15.608s | 178.187s | 24.387s | 194.56s |
| `CreditBackup100.bak` | 0.759s | 10.317s | 3.298s | 10.986s |
| `data.gov.bak` | 0.072s | 0.516s | 0.251s | 1.195s |
| `dba.stackexchange.com.bak` | 3.509s | 16.721s | 9.818s | 101.437s |
| `EmployeeCaseStudySampleDB2012.bak` | 0.122s | 0.646s | 0.776s | 1.286s |
| `GeneralHospital.bak` | 1.166s | 9.15s | 7.081s | 20.828s |
| `IndexInternals2008.bak` | 0.065s | 0.312s | 0.471s | 0.646s |
| `Northwinds.bak` | 0.044s | 0.115s | 0.04s | 0.11s |
| `NYCTaxi_Sample.bak` | 1.014s | 23.225s | 7.582s | 30.795s |
| `Pubs.bak` | 0.037s | 0.083s | 0.045s | 0.072s |
| `SalesDB2014.bak` | 1.354s | 5.189s | 1.209s | 5.89s |
| `SalesDBOriginal.bak` | 1.295s | 5.028s | 1.192s | 5.566s |
| `StackOverflowMini.bak` | 5.824s | 37.045s | 13.168s | 134.096s |
| `tpcxbb_1gb.bak` | 3.756s | 40.595s | 11.375s | 49.11s |
| `TutorialDB.bak` | 0.003s | 0.012s | 0.02s | 0.011s |
| `WideWorldImporters-Full.bak` | 1.505s | 18.978s | 5.495s | 20.304s |
| `WideWorldImporters-Full_old.bak` | 1.583s | 17.868s | 5.476s | 19.402s |
| `WideWorldImporters-Standard.bak` | 1.645s | 17.833s | 5.844s | 19.089s |
| `WideWorldImporters-Standard_old.bak` | 1.724s | 18.257s | 5.719s | 19.633s |
| `WideWorldImportersDW-Full.bak` | 0.402s | 4.27s | 1.229s | 5.077s |
| `WideWorldImportersDW-Standard.bak` | 0.378s | 4.355s | 1.021s | 5.261s |

_Write and read times are wall-clock estimates (coarse, not exact per-sink isolation)._

## Sink read breakdown

| Backup | arrow verify | delta read | delta stats | delta verify | pg_dir read | pg_dir stats | pg_dir verify |
|--------| -------: | -------: | -------: | -------: | -------: | -------: | -------:|
| `AdventureWorks2008R2.bak` | 3.577s | 0.221s | 0.034s | 3.488s | 1.096s | 0.037s | 3.563s |
| `AdventureWorks2012.bak` | 3.606s | 0.221s | 0.034s | 3.567s | 1.016s | 0.034s | 3.485s |
| `AdventureWorks2014.bak` | 3.652s | 0.248s | 0.036s | 3.645s | 1.032s | 0.035s | 3.567s |
| `AdventureWorks2016.bak` | 3.658s | 0.234s | 0.034s | 3.495s | 0.986s | 0.034s | 3.576s |
| `AdventureWorks2016_EXT.bak` | 5.163s | 0.294s | 0.067s | 5.039s | 2.992s | 0.068s | 5.042s |
| `AdventureWorks2017.bak` | 3.616s | 0.223s | 0.033s | 3.495s | 1.01s | 0.034s | 3.478s |
| `AdventureWorks2019.bak` | 3.572s | 0.217s | 0.034s | 3.467s | 1.046s | 0.036s | 3.559s |
| `AdventureWorks2022.bak` | 3.613s | 0.222s | 0.035s | 3.518s | 0.996s | 0.034s | 3.571s |
| `AdventureWorks2025.bak` | 3.526s | 0.219s | 0.033s | 3.52s | 0.942s | 0.034s | 3.564s |
| `AdventureWorksDW2008R2.bak` | 0.997s | 0.11s | 0.03s | 0.926s | 0.679s | 0.029s | 0.907s |
| `AdventureWorksDW2012.bak` | 3.086s | 0.113s | 0.037s | 2.966s | 1.184s | 0.038s | 2.994s |
| `AdventureWorksDW2014.bak` | 3.039s | 0.134s | 0.039s | 2.94s | 1.157s | 0.04s | 2.853s |
| `AdventureWorksDW2016.bak` | 3.004s | 0.111s | 0.038s | 2.912s | 1.135s | 0.039s | 2.9s |
| `AdventureWorksDW2016_EXT.bak` | 2.97s | 1.124s | 3.062s | 3.088s | 45.481s | 3.706s | 3.016s |
| `AdventureWorksDW2017.bak` | 3.007s | 0.125s | 0.039s | 2.978s | 1.181s | 0.042s | 3.036s |
| `AdventureWorksDW2019.bak` | 3.057s | 0.126s | 0.039s | 3.022s | 1.17s | 0.04s | 2.859s |
| `AdventureWorksDW2022.bak` | 2.991s | 0.115s | 0.039s | 2.914s | 1.179s | 0.042s | 2.982s |
| `AdventureWorksDW2025.bak` | 2.986s | 0.114s | 0.038s | 2.875s | 1.158s | 0.042s | 2.842s |
| `AdventureWorksLT2012.bak` | 0.074s | 0.044s | 0.002s | 0.023s | 0.062s | 0.002s | 0.023s |
| `AdventureWorksLT2014.bak` | 0.075s | 0.047s | 0.002s | 0.024s | 0.064s | 0.002s | 0.023s |
| `AdventureWorksLT2016.bak` | 0.08s | 0.043s | 0.002s | 0.024s | 0.062s | 0.002s | 0.023s |
| `AdventureWorksLT2017.bak` | 0.107s | 0.045s | 0.002s | 0.024s | 0.061s | 0.002s | 0.024s |
| `AdventureWorksLT2019.bak` | 0.081s | 0.049s | 0.002s | 0.024s | 0.063s | 0.002s | 0.023s |
| `AdventureWorksLT2022.bak` | 0.073s | 0.048s | 0.002s | 0.023s | 0.062s | 0.002s | 0.023s |
| `AdventureWorksLT2025.bak` | 0.081s | 0.046s | 0.002s | 0.023s | 0.062s | 0.002s | 0.023s |
| `BaseballData.bak` | 1.582s | 0.126s | 0.055s | 1.588s | 0.828s | 0.049s | 1.52s |
| `Chinook-id-pk.bak` | 0.069s | 0.046s | 0.002s | 0.017s | 0.012s | 0.001s | 0.017s |
| `Chinook.bak` | 0.122s | 0.045s | 0.002s | 0.018s | 0.013s | 0.001s | 0.019s |
| `ContosoRetailDW.bak` | 170.141s | 1.005s | 1.812s | 174.809s | 21.74s | 2.879s | 169.526s |
| `CreditBackup100.bak` | 10.354s | 0.082s | 0.057s | 10.115s | 1.03s | 0.072s | 9.813s |
| `data.gov.bak` | 0.467s | 0.036s | 0.027s | 0.445s | 0.699s | 0.031s | 0.454s |
| `dba.stackexchange.com.bak` | 16.408s | 0.351s | 0.144s | 16.031s | 84.539s | 0.159s | 16.562s |
| `EmployeeCaseStudySampleDB2012.bak` | 0.641s | 0.043s | 0.025s | 0.563s | 0.668s | 0.024s | 0.579s |
| `GeneralHospital.bak` | 8.597s | 0.122s | 0.533s | 8.392s | 11.859s | 0.559s | 8.3s |
| `IndexInternals2008.bak` | 0.258s | 0.038s | 0.013s | 0.246s | 0.378s | 0.013s | 0.24s |
| `Northwinds.bak` | 0.084s | 0.041s | 0.002s | 0.022s | 0.029s | 0.002s | 0.022s |
| `NYCTaxi_Sample.bak` | 22.96s | 0.081s | 0.29s | 22.835s | 7.504s | 0.309s | 22.969s |
| `Pubs.bak` | 0.086s | 0.022s | 0.001s | 0.009s | 0.013s | 0.001s | 0.009s |
| `SalesDB2014.bak` | 5.22s | 0.078s | 0.01s | 5.07s | 0.526s | 0.012s | 5.312s |
| `SalesDBOriginal.bak` | 5.123s | 0.082s | 0.009s | 4.902s | 0.491s | 0.012s | 5.022s |
| `StackOverflowMini.bak` | 37.921s | 0.63s | 0.261s | 35.886s | 97.624s | 0.27s | 35.932s |
| `tpcxbb_1gb.bak` | 41.216s | 0.326s | 0.45s | 39.514s | 7.846s | 0.563s | 40.334s |
| `TutorialDB.bak` | 0.037s | 0.003s | 0.0s | 0.004s | 0.002s | 0.0s | 0.004s |
| `WideWorldImporters-Full.bak` | 17.906s | 0.223s | 0.106s | 18.286s | 1.688s | 0.107s | 18.152s |
| `WideWorldImporters-Full_old.bak` | 17.5s | 0.222s | 0.101s | 17.231s | 1.633s | 0.108s | 17.321s |
| `WideWorldImporters-Standard.bak` | 17.065s | 0.223s | 0.099s | 17.184s | 1.65s | 0.104s | 16.963s |
| `WideWorldImporters-Standard_old.bak` | 17.324s | 0.26s | 0.113s | 17.518s | 1.806s | 0.112s | 17.326s |
| `WideWorldImportersDW-Full.bak` | 4.07s | 0.1s | 0.061s | 3.997s | 1.044s | 0.061s | 3.854s |
| `WideWorldImportersDW-Standard.bak` | 4.094s | 0.1s | 0.063s | 4.092s | 1.059s | 0.063s | 4.032s |

_arrow verify = cell verification folded into extract_s. Sink read = pure I/O + decode. Stats = min/max/null compute. Sink verify = cell verification on the round-tripped data. Remainder of readback_s is GC / other._

---

_Generated 2026-07-21 · 49 fixtures · 49 pass · 0 xfail · 0 fail_
