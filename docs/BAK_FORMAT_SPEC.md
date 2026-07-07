# SQL Server .bak / .bacpac Format Specification

This file has been reorganized into per-StoragePath spec files under `docs/spec/`.

**Start here:** [docs/spec/00_MASTER.md](spec/00_MASTER.md)

## Quick navigation

| Looking for | Go to |
|---|---|
| Which spec file for a given storage path | [00_MASTER.md — routing table](spec/00_MASTER.md#storagepath-routing-table) |
| Backup container (MTF / MSSQLBAK / BACPAC) | [spec/01_CONTAINER.md](spec/01_CONTAINER.md) |
| XPRESS codec (MS-XCA §2.1/§2.2) | [spec/01_XPRESS.md](spec/01_XPRESS.md) |
| MDF page structure | [spec/01_PAGE.md](spec/01_PAGE.md) |
| System catalog tables | [spec/01_CATALOG.md](spec/01_CATALOG.md) |
| Type on-disk layouts + LOB | [spec/01_TYPES_LOB.md](spec/01_TYPES_LOB.md) |
| Rowstore heap rows | [spec/02_ROWSTORE_HEAP.md](spec/02_ROWSTORE_HEAP.md) |
| Rowstore B-tree rows | [spec/03_ROWSTORE_BTREE.md](spec/03_ROWSTORE_BTREE.md) |
| ROW/PAGE compressed rows | [spec/04_ROWSTORE_COMPRESSED.md](spec/04_ROWSTORE_COMPRESSED.md) |
| Columnstore delta store | [spec/05_COLUMNSTORE_DELTA.md](spec/05_COLUMNSTORE_DELTA.md) |
| Columnstore segments (enc=1/2/3/4) | [spec/06_COLUMNSTORE_SEGMENT.md](spec/06_COLUMNSTORE_SEGMENT.md) |
| Columnstore archive (enc=5 XPRESS) | [spec/07_COLUMNSTORE_ARCHIVE.md](spec/07_COLUMNSTORE_ARCHIVE.md) |
| In-Memory OLTP (XTP) | [spec/08_XTP_CHECKPOINT.md](spec/08_XTP_CHECKPOINT.md) |
| Log tail / redo / undo | [spec/09_REDO_UNDO.md](spec/09_REDO_UNDO.md) |
| Coverage/guess/version registers | [spec/00_MASTER.md — registers](spec/00_MASTER.md) |
