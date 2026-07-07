# mssqlbak Use Case

**mssqlbak** migrates SQL Server databases into Databricks — without touching the source database, without CDC, and without custom ETL.

It reads `.bak` and `.bacpac` files — backups every SQL Server user already creates — and loads them directly into Databricks Lakehouse (external UC, managed UC) or Lakebase.

`.bak` extraction reaches up to **101 MB/s** and **2.35M rows/s** on simple schemas; `.bacpac` extraction reaches up to **251 MB/s** and **2.77M rows/s**. Both figures are uncompressed data throughput measured on Apple M-series hardware.

**How to migrate:**
1. Upload your `.bak` or `.bacpac` file to object storage.
2. Run mssqlbak — it extracts the full backup into Databricks.
3. Apply differential backups to keep the target up to date.
4. Re-run at any time to refresh from a fresh full backup.

**Why this matters:** Migrating via CDC and custom ETL pipelines requires elevated source database permissions, adds load to production OLTP systems, and takes days to physically move large tables — turning what should be a simple migration into a multi-week project. mssqlbak eliminates all three: no permission negotiations, no source database load, no slow bulk transfer.
