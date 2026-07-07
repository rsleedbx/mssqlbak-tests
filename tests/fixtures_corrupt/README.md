# Corrupt Sample Databases

Corrupt SQL Server backup files from Paul S. Randal (SQLskills.com), downloaded from
https://www.sqlskills.com/sql-server-resources/sql-server-demos/.

See `SQLSKILLS_BLOG.md` for Paul's full description of each database and its corruption type.

## Files

| BAK file | SS version | Size | Corruption type | Restores on |
|----------|-----------|------|-----------------|-------------|
| `CorruptDemoDataPurity.bak` | 2005 | 192 MB | Data purity (error 2570) | 2005 – 2012 |
| `CorruptDemoFatalCorruption1.bak` | 2005 | 1.4 MB | Corrupt system table (CHECKDB completes) | 2005 only |
| `CorruptDemoFatalCorruption2.bak` | 2005 | 1.4 MB | Corrupt system table (CHECKDB terminates) | 2005 only |
| `CorruptDemoNCIndex.bak` | 2005 | 192 MB | Nonclustered index corruptions | 2005 – 2012 |
| `CorruptDemoRestoreOrRepair.bak` | 2005 | 1.5 MB | Restore-or-repair demo | 2005 – 2012 |
| `DemoCorruptMetadata2000.bak` | 2000 | 724 KB | Corrupt `syscolumns` (SQL 2000 format) | 2005 – 2008R2 |
| `Corrupt2008DemoFatalCorruption1.bak` | 2008 | 1.4 MB | Corrupt system table (CHECKDB completes) | 2008 |
| `Corrupt2008DemoFatalCorruption2.bak` | 2008 | 1.4 MB | Corrupt system table (CHECKDB terminates) | 2008 |
| `DemoCorruptMetadata2008R2.bak` | 2008R2 | 1.3 MB | Corrupt `syscolumns` (upgraded from 2000) | 2008R2 – 2012 |
| `AdventureWorks2014_Corrupt.bak` | 2014 | 340 MB | IE0 class corruption (type 1) | 2014 |
| `AdventureWorks2014_Corrupt2.bak` | 2014 | 339 MB | IE0 class corruption (type 2) | 2014 |

## Source ZIPs (retained)

| ZIP | Size | Contents |
|-----|------|----------|
| `2005corruptdatabasesbackups.zip` | 36 MB | 5 BAK files (2005 format) |
| `2008fatalcorruptionbackups.zip` | 236 KB | 2 BAK files (2008 fatal corruption) |
| `2008r2fatalcorruptionbackups.zip` | 260 KB | 2 BAK files (2008R2 fatal corruption) |
| `democorruptmetadata2008r2.zip` | 92 KB | 1 BAK file (2008R2 metadata corruption) |
| `ie0_corruptdbs.zip` | 96 MB | 2 BAK files (2014 AdventureWorks) |

## mssqlbak relevance

These databases are intentionally corrupt.  mssqlbak reads pages directly from BAK
files without going through SQL Server's repair path, so:

- **Data-page corruptions** (`CorruptDemoDataPurity`, `CorruptDemoNCIndex`,
  `AdventureWorks2014_Corrupt*`) may be readable or may cause page-decode errors
  depending on where the corruption sits.
- **System-table corruptions** (`CorruptDemoFatalCorruption*`, `DemoCorruptMetadata*`)
  affect catalog reads that mssqlbak uses to enumerate tables and columns — expected
  to fail at the `classify_table` step.
- **SQL Server 2000 / 2005 format** BAK files exercise the pre-2008 and pre-2016 page
  format paths documented in `docs/FIXTURE_GAPS.md` Gap 6 and Gap 7.
