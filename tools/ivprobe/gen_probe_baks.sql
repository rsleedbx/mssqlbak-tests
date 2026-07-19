-- Generate encrypted backup files for IV analysis.
-- Run after setup_probe_db.sql.

-- Clear previous backups
EXEC xp_cmdshell 'rm -f /probe/probe_aes128.bak /probe/probe_aes256.bak /probe/probe_3des.bak /probe/probe_aes128_comp.bak /probe/probe_plain.bak';

-- Plaintext reference (no encryption)
BACKUP DATABASE ProbeDB
    TO DISK = N'/probe/probe_plain.bak'
    WITH FORMAT, INIT, STATS = 10;
GO

-- AES-128
BACKUP DATABASE ProbeDB
    TO DISK = N'/probe/probe_aes128.bak'
    WITH FORMAT, INIT, STATS = 10,
    ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = ProbeCert);
GO

-- AES-256
BACKUP DATABASE ProbeDB
    TO DISK = N'/probe/probe_aes256.bak'
    WITH FORMAT, INIT, STATS = 10,
    ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = ProbeCert);
GO

-- TRIPLE_DES_3KEY
BACKUP DATABASE ProbeDB
    TO DISK = N'/probe/probe_3des.bak'
    WITH FORMAT, INIT, STATS = 10,
    ENCRYPTION (ALGORITHM = TRIPLE_DES_3KEY, SERVER CERTIFICATE = ProbeCert);
GO

-- AES-128 compressed
BACKUP DATABASE ProbeDB
    TO DISK = N'/probe/probe_aes128_comp.bak'
    WITH FORMAT, INIT, COMPRESSION, STATS = 10,
    ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = ProbeCert);
GO

PRINT 'All probe backups complete.';
GO
