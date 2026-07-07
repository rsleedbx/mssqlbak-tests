# Backup-type coverage

Which SQL Server **backup types** the `.bak` -> Delta parser can restore.
**Generated** by `python -m tools.backup_coverage`; each SUPPORTED row is
validated against the committed fixtures, and `tests/test_backup_coverage.py`
fails if this file is out of date or a SUPPORTED claim stops holding.

Companion to the byte-complete [BYTE_MAP.md](BYTE_MAP.md) (master coverage doc): [TYPE_COVERAGE.md](TYPE_COVERAGE.md) tracks column *data* and [METADATA_COVERAGE.md](METADATA_COVERAGE.md) tracks *metadata* fields, while this report tracks *which kinds of backup* can be turned into a full restore.

**Coverage:** 4/8 backup types restore the whole database to Delta (50%).

**First priority — full restore.** A *full database backup* is the only backup type that contains every data extent on its own, so it is the basic unit that enables a complete database -> Delta restore. That path is SUPPORTED (uncompressed and `WITH COMPRESSION`); everything else is ranked by how much extra machinery it needs before it can yield a full restore.

## Backup types

| Category | Backup type | T-SQL | Restore yields | Status | Notes |
|----------|-------------|-------|----------------|--------|-------|
| Database backup | Full database backup | `BACKUP DATABASE db TO DISK=…` | whole database | SUPPORTED | first-priority path: contains every data extent plus enough log to recover; the entire MDF page image is rebuilt and every user table extracted to Delta. Validated on the committed fixture. |
| Database backup | Full database backup, WITH COMPRESSION | `BACKUP DATABASE db TO DISK=… WITH COMPRESSION` | whole database | SUPPORTED | same full-restore path; the MSSQLBAK/XPRESS container is transparently decompressed (mssqlbak.compressed). Validated on the compressed fixture. |
| Database backup | Full database backup, copy-only | `BACKUP DATABASE db TO DISK=… WITH COPY_ONLY` | whole database | SUPPORTED | byte-for-byte the same page-image format as a full backup; copy-only only changes the differential base, a metadata flag the reader decodes. The committed fixture is itself a copy-only full backup, so this row is validated directly. |
| Differential backup | Differential database backup | `BACKUP DATABASE db TO DISK=… WITH DIFFERENTIAL` | changed extents merged onto full base | SUPPORTED | PageStore.from_diff_bak(diff_bak, full_bak) merges the differential's changed extents onto the full-backup page image, yielding a complete page store identical to restoring to an engine. Validated against the committed tabletypecoverage_diff.bak + tabletypecoverage_full.bak fixture pair. |
| Differential backup | Differential partial backup | `BACKUP DATABASE db FILEGROUP=… WITH DIFFERENTIAL` | changed extents of a subset | PLANNED | changed extents since a partial base; needs both the partial base and extent-merge. Not implemented. |
| Log backup | Transaction-log backup | `BACKUP LOG db TO DISK=…` | log records (no data pages) | UNSUPPORTED | contains log records, not data pages — a different on-disk format. Required later for point-in-time recovery and CDC/log-chain hydration, but yields no standalone table data. |
| File backup | File / filegroup backup | `BACKUP DATABASE db FILE=… | FILEGROUP=…` | subset of files | UNSUPPORTED | backs up only some files/filegroups; cannot reconstruct the whole database on its own. Out of scope for the full-restore goal. |
| Partial backup | Partial backup | `BACKUP DATABASE db READ_WRITE_FILEGROUPS …` | primary + read/write filegroups | UNSUPPORTED | skips read-only filegroups, so it is not a complete-database image. Out of scope for v1. |

## Container / option dimensions

Orthogonal to the backup *type* above; any full backup may carry these.

| Option | Status | Notes |
|--------|--------|-------|
| Uncompressed (MTF) | SUPPORTED | the native Microsoft Tape Format container; default for any backup type above. |
| Compressed (WITH COMPRESSION) | SUPPORTED | MSSQLBAK container, XPRESS (LZ77+Huffman); decoded by mssqlbak.compressed. |
| TDE-encrypted | UNSUPPORTED | MSSQLBAK container whose payload is encrypted; the page image cannot be reconstructed without the certificate, so extraction raises ValueError. |
| Striped / multi-file (TO DISK=…, DISK=…) | PLANNED | a single backup split across several files; only single-file backups are read in v1. |
| Mirrored media set | PLANNED | redundant copies; read one mirror only. Not yet implemented. |

## Legend

- **SUPPORTED** — restores the whole database to Delta; validated against a committed fixture. Counts toward coverage.
- **PLANNED** — restorable in principle but not yet implemented (needs base-merge, multi-file assembly, etc.). A gap.
- **UNSUPPORTED** — cannot yield a complete-database restore on its own (log records, file/partial subsets, encrypted payloads). Out of scope for v1.

## Roadmap (toward more backup types)

1. **Differential database backup** — merge changed extents onto a full base image (both already decodable individually).
2. **Striped / multi-file** — concatenate the data stream across files before page reassembly.
3. **Transaction-log backup** — decode log records for point-in-time and CDC/log-chain hydration (the original analytics/CDC goal).

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.
