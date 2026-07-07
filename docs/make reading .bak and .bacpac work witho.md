make reading .bak and .bacpac work without crashing - implement full and differental
make writing target work with equal or better than sqlserver restore - implement rust
make source count and null count match target - implement restore and stats collection
make source hash of each column match target - implement hash


SELECT CHECKSUM_AGG(CHECKSUM(HASHBYTES('SHA2_256', CAST(s.value AS VARCHAR(10))))) AS AggregatedHash
FROM GENERATE_SERIES(1, 100) AS s;