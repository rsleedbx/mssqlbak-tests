-- Run inside the probe container to create ProbeDB and ProbeCert.
-- Execute via: sqlcmd -S localhost -U sa -P "$SA_PASS" -i setup_probe_db.sql

IF DB_ID('ProbeDB') IS NULL
    CREATE DATABASE ProbeDB;
GO

USE master;
GO

IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'ProbeKey_1!';
GO

IF NOT EXISTS (SELECT 1 FROM sys.certificates WHERE name = 'ProbeCert')
    CREATE CERTIFICATE ProbeCert
        WITH SUBJECT = 'IV probe certificate',
        EXPIRY_DATE = '2035-01-01';
GO

-- Back up the certificate + private key so we can load the PVK later.
BACKUP CERTIFICATE ProbeCert
    TO FILE = N'/probe/probe_cert.cer'
    WITH PRIVATE KEY (
        FILE           = N'/probe/probe_cert.pvk',
        ENCRYPTION BY PASSWORD = 'PvkPass_1!'
    );
GO

PRINT 'ProbeDB and ProbeCert ready.';
GO
