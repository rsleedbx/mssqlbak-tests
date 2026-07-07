-- Columnstore enc=2 formula synthetic test
-- Goal: understand how SQL Server encodes INT FK columns vs. DATE/DECIMAL columns
-- and whether compact-null-mode (n_stored < n_rows) changes the formula.

USE master;
GO

IF DB_ID('cs_enc_test') IS NOT NULL
BEGIN
    ALTER DATABASE cs_enc_test SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE cs_enc_test;
END
GO

CREATE DATABASE cs_enc_test;
GO

USE cs_enc_test;
GO

-- Table mimicking WideWorldImportersDW Fact.Sale structure:
--   sale_key        INT (identity, enc=1 expected)
--   city_key        INT (larger range, e.g. 2000-6000, no nulls)
--   customer_key    INT (small range, 1-663, WITH nulls to trigger compact mode)
--   stock_item_key  INT (small range, 1-227, WITH nulls)
--   invoice_date    DATE (no nulls)
--   quantity        INT (can be negative, WITH nulls)
--   unit_price      DECIMAL(18,2) (no nulls)
CREATE TABLE dbo.sale_cs (
    sale_key       INT          NOT NULL,
    city_key       INT          NOT NULL,
    customer_key   INT              NULL,   -- nullable: triggers compact-null-mode
    stock_item_key INT              NULL,   -- nullable
    invoice_date   DATE         NOT NULL,
    quantity       INT              NULL,   -- nullable, can be negative
    unit_price     DECIMAL(18,2) NOT NULL
);
GO

-- Insert 1048 rows (just over 1 row group = 1024 rows threshold).
-- Use known deterministic formulas so we can verify extraction.
-- sale_key: 1..1048
-- city_key: 2000 + (sale_key % 3200)   → range [2000, 5199]
-- customer_key: NULL for every 5th row, else (sale_key % 663) + 1  → range [1,663]
-- stock_item_key: NULL for every 7th row, else (sale_key % 227) + 1 → range [1,227]
-- invoice_date: '2012-01-01' + sale_key days
-- quantity: NULL for every 11th row, else -50 + (sale_key % 100)   → range [-50,49]
-- unit_price: CAST((sale_key % 500) AS DECIMAL(18,2)) / 100        → range [0.00,4.99]

WITH n AS (
    SELECT TOP 1048 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn
    FROM sys.columns a CROSS JOIN sys.columns b
)
INSERT INTO dbo.sale_cs
SELECT
    rn,
    2000 + (rn % 3200),
    CASE WHEN rn % 5 = 0 THEN NULL ELSE (rn % 663) + 1 END,
    CASE WHEN rn % 7 = 0 THEN NULL ELSE (rn % 227) + 1 END,
    DATEADD(day, rn, '2012-01-01'),
    CASE WHEN rn % 11 = 0 THEN NULL ELSE -50 + (rn % 100) END,
    CAST((rn % 500) AS DECIMAL(18,2)) / 100
FROM n;
GO

-- Add clustered columnstore index (forces all data into columnstore storage)
CREATE CLUSTERED COLUMNSTORE INDEX CCI_sale_cs ON dbo.sale_cs;
GO

-- Force compression: reorganize to close open delta stores
ALTER INDEX CCI_sale_cs ON dbo.sale_cs REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);
GO

-- ============================================================
-- Query 1: Check column_store_segments metadata
-- This shows what SQL Server actually stores for each column
-- ============================================================
SELECT
    c.name                          AS column_name,
    css.segment_id,
    css.row_count,
    css.encoding_type,
    css.min_data_id,
    css.max_data_id,
    css.null_value,
    css.on_disk_size
FROM sys.column_store_segments css
JOIN sys.partitions p       ON css.hobt_id = p.hobt_id
JOIN sys.indexes i          ON p.object_id = i.object_id AND p.index_id = i.index_id
JOIN sys.index_columns ic   ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                            AND ic.key_ordinal = css.column_id
JOIN sys.columns c          ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('dbo.sale_cs')
ORDER BY css.column_id, css.segment_id;
GO

-- ============================================================
-- Query 2: First 20 rows sorted by sale_key for comparison
-- (mssqlbak will extract these; we compare extraction vs ground truth)
-- ============================================================
SELECT TOP 20
    sale_key, city_key, customer_key, stock_item_key,
    invoice_date, quantity, unit_price
FROM dbo.sale_cs
ORDER BY sale_key;
GO

-- ============================================================
-- Backup to a known path so mssqlbak can read it
-- ============================================================
BACKUP DATABASE cs_enc_test
TO DISK = '/var/opt/mssql/data/cs_enc_test.bak'
WITH FORMAT, COMPRESSION;
GO

PRINT 'Backup complete: /var/opt/mssql/data/cs_enc_test.bak';
GO
