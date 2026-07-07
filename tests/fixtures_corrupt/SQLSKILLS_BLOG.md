# Corruption Demo Databases and Scripts

**Source:** https://www.sqlskills.com/blogs/paul/corruption-demo-databases-and-scripts/  
**Author:** Paul S. Randal — January 8, 2013

---

I originally blogged a series of corruption demos and associated databases back in 2008, for use with SQL Server 2005 and 2008. Since then the releases have changed which databases and corruptions work and I've had to rework some of the databases for you. This is an update that takes into account SQL Server 2008R2 and SQL Server 2012 and sets out everything clearly.

## The Database Zips

**`2005corruptdatabasesbackups.zip`** (36 MB) — "example corrupt databases" containing:

### DemoDataPurity (`CorruptDemoDataPurity.bak`)
- 192-MB SQL Server 2005 database with a single 2570 (data purity) error
- Works on 2005 and will upgrade and work on 2008, 2008R2, and 2012

### DemoFatalCorruption1 (`CorruptDemoFatalCorruption1.bak`)
- 1-MB SQL Server 2005 database with a corrupt system table (that allows CHECKDB to complete)
- **Only works on 2005**

### DemoFatalCorruption2 (`CorruptDemoFatalCorruption2.bak`)
- 1-MB SQL Server 2005 database with a corrupt system table (that terminates CHECKDB)
- **Only works on 2005**

### DemoNCIndex (`CorruptDemoNCIndex.bak`)
- 192-MB SQL Server 2005 database with a bunch of nonclustered index corruptions
- Works on 2005 and will upgrade and work on 2008, 2008R2, and 2012

### DemoCorruptMetadata (`DemoCorruptMetadata2000.bak`)
- 1-MB SQL Server **2000** database with corrupt `syscolumns` table
- Upgrades and works on 2005, 2008, and 2008R2

---

**`2008fatalcorruptionbackups.zip`** (232 KB) — "2008 fatal corruptions databases" containing:

### DemoFatalCorruption1 (`Corrupt2008DemoFatalCorruption1.bak`)
- 1-MB SQL Server 2008 database with a corrupt system table (that allows CHECKDB to complete)

### DemoFatalCorruption2 (`Corrupt2008DemoFatalCorruption2.bak`)
- 1-MB SQL Server 2008 database with a corrupt system table (that terminates CHECKDB)

---

**`2008r2fatalcorruptionbackups.zip`** (260 KB) — "2008R2 fatal corruptions databases" containing:

### DemoFatalCorruption1 (`CorruptDemoFatalCorruption1.bak`)
- 1-MB SQL Server 2008R2 database with a corrupt system table (that allows CHECKDB to complete)

### DemoFatalCorruption2 (`CorruptDemoFatalCorruption2.bak`)
- 1-MB SQL Server 2008R2 database with a corrupt system table (that terminates CHECKDB)

---

**`democorruptmetadata2008r2.zip`** (92 KB) — "2008R2 corrupt metadata database" containing:

### DemoCorruptMetadata (`DemoCorruptMetadata2008R2.bak`)
- 1-MB SQL Server 2008R2 database upgraded from a 2000 database with a corrupt `syscolumns` table
- Works on 2008R2 and upgrades and works on 2012

---

**`ie0_corruptdbs.zip`** (96 MB) — "IE0 class corrupt 2014 AdventureWorks databases" containing:

### AdventureWorks2014 Corrupt (`AdventureWorks2014_Corrupt.bak`, `AdventureWorks2014_Corrupt2.bak`)
- ~340-MB SQL Server 2014 AdventureWorks databases with various corruptions
- Used in Paul Randal's IE0 (Immersion Event: SQL Server Internals and Architecture) class

---

## Demo Script Categories (from the scripts zip)

1. **Fatal Errors** — uses DemoFatalCorruption1 and DemoFatalCorruption2
2. **NC Indexes** — uses DemoNCIndex; nonclustered index corruption walk-through
3. **Data Purity** — uses DemoDataPurity; 2570 error detection and repair
4. **Metadata** — uses DemoCorruptMetadata; corrupt `syscolumns` walk-through
5. **Restore or Repair** — set-up scripts showing page restore vs REPAIR_ALLOW_DATA_LOSS
6. **Suspect Database** — creates its own corruption; suspect-database recovery walk-through

Note: DemoFatalCorruption databases for SQL Server 2012 were never created.
