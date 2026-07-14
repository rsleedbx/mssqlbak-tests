# Metadata coverage

Every field in the SQL Server backup container's metadata and whether
`mssqlbak.reader` extracts it. **Generated** by `python -m tools.metadata_coverage`
from the MTF specification field list and the committed fixture;
`tests/test_metadata_coverage.py` fails if this file is out of date or if an
EXPOSED field stops resolving on the fixture.

This is the **metadata** slice of the byte-complete [BYTE_MAP.md](BYTE_MAP.md) (the master coverage doc); the data slice is [TYPE_COVERAGE.md](TYPE_COVERAGE.md). Which backup *types* can be restored is tracked in [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md).

**Coverage:** 15/16 meaningful fields exposed (94%); 1 gap(s). Format-internal fields (reserved/checksum/positioning) are SKIPPED and excluded from the denominator.

The metadata path (`read_bak_metadata`, used by the CLI `info` command and
`restore`) is independent of the data-decode path (`extract_mdf_pages`, used by
`extract`); they share no block-walking logic. See [DESIGN](../DESIGN.md).

| Source | Field | Status | Exposed as | Notes |
|--------|-------|--------|------------|-------|
| common header | DBLK type | INTERNAL | — | dispatches TAPE vs SSET parsing |
| common header | block attributes | SKIPPED | — | continuation/compression flags |
| common header | offset to first event | SKIPPED | — | tape stream positioning |
| common header | OS id / OS version | SKIPPED | — | always Windows NT for SQL Server |
| common header | displayable size | SKIPPED | — | user-display hint, not authoritative |
| common header | format logical address | SKIPPED | — | tape positioning |
| common header | control block id | SKIPPED | — | recovery aid |
| common header | OS-specific data ptr | INTERNAL | — | address of OS extension |
| common header | string type | INTERNAL | — | selects ANSI vs UTF-16LE decode |
| common header | header checksum | SKIPPED | — | integrity field |
| common header | physical block size | INTERNAL | BakMetadata.block_size | detected by probing, exposed |
| TAPE | media family id | SKIPPED | — | media-set grouping |
| TAPE | tape attributes | SKIPPED | — | soft-filemark/label flags |
| TAPE | media sequence number | SKIPPED | — | multi-volume ordering |
| TAPE | password encryption | SKIPPED | — | media password algorithm |
| TAPE | media catalogue type | SKIPPED | — | MBC type |
| TAPE | media name | EXPOSED | MediaInfo.media_name | optional; shares the validated `_resolve_addr` path with software name |
| TAPE | media description/label | SKIPPED | — | pipe-delimited vendor label |
| TAPE | media password | SKIPPED | — | encrypted password digest |
| TAPE | software name | EXPOSED | MediaInfo.software_name |  |
| TAPE | software vendor id | SKIPPED | — | numeric vendor id |
| TAPE | media date | EXPOSED | MediaInfo.media_date |  |
| TAPE | MTF major version | EXPOSED | MediaInfo.mtf_version |  |
| SSET | block attributes (backup kind) | EXPOSED | BackupSetInfo.backup_attributes / backup_type_label | Full / Differential / copy-only |
| SSET | password encryption | SKIPPED | — | set password algorithm |
| SSET | software compression | SKIPPED | — | compression algorithm id |
| SSET | software vendor id | SKIPPED | — | numeric vendor id |
| SSET | data set number | EXPOSED | BackupSetInfo.dataset_number |  |
| SSET | data set name | EXPOSED | BackupSetInfo.database_name | used as database name when present |
| SSET | data set description | SKIPPED | — | free-text, usually empty |
| SSET | data set password | SKIPPED | — | encrypted password digest |
| SSET | user name | EXPOSED | BackupSetInfo.user_name |  |
| SSET | physical block address | SKIPPED | — | tape positioning |
| SSET | media write date | EXPOSED | BackupSetInfo.write_date | backup timestamp |
| SSET | software major version | EXPOSED | BackupSetInfo.software_version |  |
| SSET | software minor version | SKIPPED | — | only major version retained |
| SSET | time zone | SKIPPED | — | UTC offset of write date |
| SSET | MTF minor version | SKIPPED | — | format revision |
| SSET | media catalog version | SKIPPED | — | MBC version |
| SQL config | database name | EXPOSED | BackupSetInfo.database_name | data-set name or primary .mdf stem |
| SQL config | data/log file paths | EXPOSED | BackupSetInfo.data_files | .mdf/.ndf/.ldf paths in the SSET block |
| SQL config | server instance | EXPOSED | BackupSetInfo.server_instance | MACHINE or MACHINE\INSTANCE extracted from the MQCI sub-block (same as RESTORE HEADERONLY ServerName); empty when not parseable |
| SQL config | machine name | EXPOSED | BackupSetInfo.machine_name | machine component of server_instance (before the first backslash); empty when server_instance is absent |
| SQL config | backup LSNs (first/last/checkpoint) | GAP | — | header LSNs are not stored verbatim in the SSET descriptor; the LSN-shaped triples there are internal fork/differential markers, not RESTORE HEADERONLY's First/Last/Checkpoint. Available via the engine for future reverse-engineering |
| SQL config | compression / TDE detection | EXPOSED | reader.is_compressed_or_encrypted() | compressed/encrypted backups use an MSSQLBAK container; compressed ones are decoded by mssqlbak.compressed (XPRESS) for extraction, TDE-encrypted ones are unsupported; the MTF info reader needs the uncompressed form |

## Legend

- **EXPOSED** — parsed and surfaced via the public API; validated present on the fixture. Counts toward coverage.
- **INTERNAL** — parsed and used to drive decoding/iteration, but not surfaced as metadata.
- **SKIPPED** — present in the format but intentionally not extracted (reserved, checksum, encryption/compression ids, tape positioning). Not relevant to backup identity.
- **GAP** — meaningful metadata we do not yet extract. Counts against coverage.
- **MISSING** — an EXPOSED field that failed to resolve on the fixture (a regression).

## Gaps

To reach 100% coverage, decode these from SQL Server's proprietary config stream:

- `backup LSNs (first/last/checkpoint)` — header LSNs are not stored verbatim in the SSET descriptor; the LSN-shaped triples there are internal fork/differential markers, not RESTORE HEADERONLY's First/Last/Checkpoint. Available via the engine for future reverse-engineering

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.
