# Byte map (master coverage)

Every byte of the backup, classified as **metadata**, **data**, or
**skippable** container framing. **Generated** by `python -m tools.byte_map`
from the file bytes alone; `tests/test_byte_map.py` fails if this file is
stale or if the tiling leaves any byte unclassified.

This is the master document. It anchors the field- and type-level reports:

- **Metadata** bytes → detailed in [METADATA_COVERAGE.md](METADATA_COVERAGE.md)
- **Data** bytes (MDF page image) → decoded per the types in [TYPE_COVERAGE.md](TYPE_COVERAGE.md)
- **Skippable** bytes → MTF container framing, allocation/system pages, unallocated pages, and the end-of-set trailer (not part of restored row data)

Which backup *types* (full / differential / log / …) can be restored at all is tracked separately in [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md); how keys, indexes and constraints are encoded is in [CONSTRAINT_COVERAGE.md](CONSTRAINT_COVERAGE.md); what is detected and skipped (heaps, compression, partitioning, …) is in [ROBUSTNESS_COVERAGE.md](ROBUSTNESS_COVERAGE.md).

**Fixture:** `typecoverage_full.bak` — 7,917,568 bytes, MTF block size 4096.

**Accounted: 100.00% of the file (7,917,568 / 7,917,568 bytes). UNKNOWN: 0 bytes.**

## Byte budget

| Bucket | Bytes | Share | Meaning |
|--------|------:|------:|---------|
| Metadata | 8,192 | 0.10% | Backup descriptors we parse into fields |
| Data | 3,702,784 | 46.77% | MDF data-file page image (the restored content) |
| Skippable | 4,206,592 | 53.13% | Container framing, allocation/system pages, unallocated space, trailer |
| **Unknown** | **0** | **0.00%** | **Unclassified — must be 0** |

## Top-level layout

Contiguous regions, in file order. These tile the whole file with no gaps.

| Offset | Length | Category | Region | Anchor |
|-------:|-------:|----------|--------|--------|
| 0 | 4,096 | METADATA | TAPE media descriptor | [METADATA_COVERAGE.md](METADATA_COVERAGE.md) |
| 4,096 | 4,096 | FRAMING | soft filemark (SFMB) | — |
| 8,192 | 4,096 | METADATA | SSET backup-set descriptor | [METADATA_COVERAGE.md](METADATA_COVERAGE.md) |
| 12,288 | 4,096 | FRAMING | MDF data-stream descriptors (MSDA) + padding | — |
| 16,384 | 7,667,712 | DATA | MDF data-file page image (file 1) | [TYPE_COVERAGE.md](TYPE_COVERAGE.md) |
| 7,684,096 | 233,472 | FRAMING | end-of-set trailer: log-file stream, ESET/EOTM, filemarks, padding | — |

## Inside the data-file image (per page type)

The 7,667,712-byte image is 936 pages of 8192 bytes. Each page's `m_type` determines its class:

| Class | Page type | Pages | Bytes | Share of image |
|-------|-----------|------:|------:|---------------:|
| ALLOCATION | file-header page | 1 | 8,192 | 0.11% |
| ALLOCATION | PFS (page free space) | 1 | 8,192 | 0.11% |
| ALLOCATION | GAM (global allocation map) | 1 | 8,192 | 0.11% |
| ALLOCATION | SGAM (shared global allocation map) | 1 | 8,192 | 0.11% |
| UNUSED | unallocated (zero-filled) page | 379 | 3,104,768 | 40.49% |
| ALLOCATION | differential bitmap | 1 | 8,192 | 0.11% |
| ALLOCATION | ML (bulk-logged) map | 1 | 8,192 | 0.11% |
| DATA | data page | 166 | 1,359,872 | 17.74% |
| ALLOCATION | boot page | 1 | 8,192 | 0.11% |
| ALLOCATION | IAM (index allocation map) | 98 | 802,816 | 10.47% |
| DATA | index page | 125 | 1,024,000 | 13.35% |
| DATA | LOB / text-mix page | 158 | 1,294,336 | 16.88% |
| DATA | LOB / text-tree page | 3 | 24,576 | 0.32% |

## Restore completeness

The **data** bucket is exactly the page image the extractor reads, located by
`mssqlbak.mtf`. For a SQL Server restore this is the content written back to
the `.mdf`. When a live engine is available, `tests/test_byte_map.py` confirms
this image equals `RESTORE FILELISTONLY`'s `BackupSizeInBytes` for data file 1,
so the data file is captured byte-for-byte.

The **log file** is carried in the end-of-set trailer as its own MTF stream.
For a copy-only backup of a freshly created database its backed-up payload is
0 bytes (nothing to extract). A full crash-consistent *restore* of a database
with log activity would also need that stream replayed; the data-hydration use
case this parser targets does not.

## Legend

- **METADATA** — backup descriptor fields parsed by `reader.py` (see [METADATA_COVERAGE.md](METADATA_COVERAGE.md)).
- **DATA** — MDF data / index / LOB pages; row values decoded per [TYPE_COVERAGE.md](TYPE_COVERAGE.md).
- **ALLOCATION** — GAM/SGAM/IAM/PFS/boot/file-header/diff/ML pages: structural bookkeeping, not row data.
- **UNUSED** — unallocated, zero-filled pages.
- **FRAMING** — MTF container: descriptor blocks, stream headers, filemarks, padding, end-of-set trailer.
- **UNKNOWN** — bytes the map could not classify. A non-zero total is a confidence gap and fails the guard test.

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser scope.
