# Corroboration Sources

**Date:** 2026-06-16
**Scope:** Source index for `[CORROBORATED]` confidence tags in
[`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md).

## Related Source Docs

- [`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md) — confidence tags + section status.
- [`260616-2-fixture-dbcc-page-verifier.md`](260616-2-fixture-dbcc-page-verifier.md) — author graph, literature map, and full-read references.
- [`260616-3-random-order-fixtures-plan.md`](260616-3-random-order-fixtures-plan.md) — execution plan and tier policy derived from corroboration state.
- [`260616-status.md`](260616-status.md) — operational status and open-item triage linked to verifier findings.

This document is the SSOT for external corroboration. A `BAK_FORMAT_SPEC` section
may use `[CORROBORATED]` only when it appears in the table below with at least one
named external source. `[CORROBORATED]` means the claim works in mssqlbak fixtures
and is supported by third-party evidence, but is not confirmed by a normative
producer specification or live byte-level SQL Server verifier.

`[CONFIRMED]` sources belong in the verifier sidecar / probe record for the item
(`DBCC PAGE`, `DBCC CSINDEX`, DMV output, MS-XCA, MTF, etc.). This document tracks
the middle tier: external support that is useful but not ground truth.

## Current Counts

Section-heading counts in `BAK_FORMAT_SPEC.md`:

| `[CONFIRMED]` | `[CORROBORATED]` | `[EMPIRICAL]` | `[HEURISTIC]` | `[UNKNOWN]` | `[INVALIDATED]` | Total |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 13 | 31 | 8 | 1 | 2 | 1 | 56 |

Recompute with:

```bash
rg -c '^#{2,4} .*\[CORROBORATED\]' docs/BAK_FORMAT_SPEC.md
rg -c '^#{2,4} .*\[EMPIRICAL\]' docs/BAK_FORMAT_SPEC.md
```

## Source Index

| Spec section | External corroboration | What it corroborates | Confidence boundary |
|--------------|------------------------|----------------------|---------------------|
| §1.1 MTF layer | MS Learn [`RESTORE HEADERONLY`](https://learn.microsoft.com/en-us/sql/t-sql/statements/restore-statements-headeronly-transact-sql?view=sql-server-ver17): *"`SoftwareVendorId` — For SQL Server, this number is 4608 (or hexadecimal `0x1200`)"*; MS Learn [`backupmediaset`](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/backupmediaset-transact-sql?view=sql-server-ver16): *"The value for Microsoft SQL Server is hexadecimal 0x1200"* + `MTF_major_version` column; [CVE-2008-0107 / Insomnia ISVA-080709.1](https://seclists.org/fulldisclosure/2008/Jul/101) (Brett Moore, Insomnia Security, 2008): outer chunk dispatcher `struct backupChunk { unsigned long nametag; unsigned long size; }`, nametags include SCIN, SFGI, MQCI; [iDefense Advisory 07.08.08](https://seclists.org/bugtraq/2008/Jul/61): *"A 32-bit integer value, representing the size of a record, is taken from the file"*; [Aaron Bertrand / sqlperformance.com T-SQL Tuesday #67](https://sqlperformance.com/2015/06/extended-events/t-sql-tuesday-67-backup-restore): SQL Server 2016 `backup_restore_progress_trace` Extended Events names `MSDA` (data file area) and `MSTL` (transaction log) as SQL Server's own stream identifiers; [Bob Dorr, Microsoft PSS SQL Blog, 2008](https://learn.microsoft.com/en-us/archive/blogs/psssql/how-it-works-what-is-restorebackup-doing): trace flag 3004 restore-phase breakdown by a SQL Server Senior Escalation Engineer | SQL Server writes vendor ID `0x1200` in the MTF_TAPE `Software Vendor ID` field (MTF_TAPE offset 86); outer chunk layout = `nametag` (4 B) + `size` (4 B total-inclusive); SQL Server's names for the two main payload streams are `MSDA` (data-file extents) and `MSTL` (transaction log VLFs) | MSDA compression container (§1.2) internals remain `[EMPIRICAL]`; SQL Server-specific nametags beyond the MTF v1.00a standard set (TAPE/SSET/VOLB/SFMB/ESPB/ESET) are not fully enumerated in any open source |
| §1.3 BACPAC container | [DacServices/BacPackage API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac.dacservices?view=sql-dacfx-162); [Export a BACPAC file (Learn)](https://learn.microsoft.com/en-us/sql/tools/sql-database-projects/concepts/data-tier-applications/export-bacpac-file); [RoboKiwi BACPAC layout](https://www.robokiwi.com/wiki/data/sql/mssql/bacpac/); [`gsiems/bac-tract`](https://github.com/gsiems/bac-tract) | BACPAC is a package/ZIP containing schema metadata and table data files | Exact mssqlbak parser behavior remains fixture-tested |
| §1.3.2 `model.xml` schema | [DacFx 3.0 file formats (Bob Beauchemin)](https://www.sqlskills.com/blogs/bobb/dacfx-3-0-the-new-file-formats/); [Dac namespace](https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac?view=sql-dacfx-162) | `model.xml` carries schema model objects and properties | Field interpretation stays fixture-tested |
| §1.3.3 BCP native row format | [Use native format to import/export data](https://learn.microsoft.com/en-us/sql/relational-databases/import-export/use-native-format-to-import-or-export-data-sql-server); [`bcp` utility docs](https://learn.microsoft.com/en-us/sql/tools/bcp-utility?view=sql-server-ver17) | Table data files use native-type binary encodings | mssqlbak's per-type edge cases remain fixture-tested |
| §1.3.4 RAM vs streaming for cloud-backed BACPAC | [Python `zipfile` docs](https://docs.python.org/3/library/zipfile.html); [Azure SQL export docs (temp disk)](https://learn.microsoft.com/en-us/azure/azure-sql/database/database-export) | ZIP central-directory seekability and disk/memory pressure for BACPAC processing | The exact 1 GiB threshold is an mssqlbak implementation choice |
| §2.6 boot page | [Paul Randal: Anatomy of a page](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | Boot page and system-table pointer concepts | Exact offset still needs `DBCC PAGE` for `[CONFIRMED]` |
| §3.2 ghost record | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/) | Record status bits include ghost-record states | Full bit semantics remain fixture-tested |
| §3.3 forwarded heap record | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/) | Heap forwarding records and RID pointer concept | Exact 9-byte layout remains fixture-tested |
| §3.4 CD record (ROW/PAGE compression) | [Row compression implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/row-compression-implementation); [Page compression implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/page-compression-implementation) | ROW/PAGE compression exists and uses row transformations, prefix, and dictionary compression | Internal CD record byte layout remains fixture-tested |
| §3.5 Always Encrypted ciphertext | [Always Encrypted](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine) | AE values are opaque ciphertext with authenticated-encryption framing | Exact observed column bytes remain fixture-tested |
| §3.6 Page Compression Info (CI) | [Page compression implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/page-compression-implementation) | Page compression uses page-level prefix/dictionary metadata | CI byte fields remain fixture-tested |
| §4.1 catalog bootstrap order | [Paul Randal: Anatomy of a page](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/); [Paul Randal: allocation unit IDs](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | System allocation/catalog objects can bootstrap page traversal | Exact object walk remains fixture-tested |
| §4.2 object IDs | [Paul Randal: allocation unit IDs](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | Stable relationships among object IDs, allocation units, and system tables | Cross-version stability remains fixture-tested |
| §4.3 base-table column layouts | [OrcaMDF](https://github.com/improvedk/OrcaMDF) | System base-table definitions align with SQL Server metadata decoding | OrcaMDF is stale; use as corroboration only |
| §5.1 `sql_variant` layout | [OrcaMDF](https://github.com/improvedk/OrcaMDF) | `sql_variant` has typed payload structure | Exact type cases remain fixture-tested |
| §5.2 binary XML | [MS-BINXML open spec](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-binxml/) | Binary XML has a documented tokenized format | SQL Server storage wrapping remains fixture-tested |
| §6.1 in-row inline LOB root | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | Records can contain LOB root/pointer structures | Exact link table fields remain fixture-tested |
| §6.2 on-page LOB record | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/); [OrcaMDF](https://github.com/improvedk/OrcaMDF); [Kazamiya forensicist — LOB data structure](https://www.kazamiya.net/en/mssql_4n6-04); [Korotkevitch — LOB storage](https://aboutsqlserver.com/2013/11/05/sql-server-storage-engine-lob-storage/) | All three btyp values (3=DATA, 2=INTERNAL/LARGE_ROOT, 5=LARGE_ROOT_YUKON/ROOT) documented with field layouts; sub-header fields MaxLinks/CurLinks/Level confirmed via DBCC PAGE output | Exact byte offsets remain fixture-tested; btyp=3 DATA needs independent verifier sidecar (VC02) |
| §6.3 legacy text pointer | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | Legacy text/ntext/image pointers reference off-row storage | Exact pointer bytes remain fixture-tested |
| §7.1 segment metadata | [`sys.column_store_segments`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17); [Rusanu 2012 columnstore internals](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/) | Columnstore segment metadata exists and exposes encoding/dictionary/min-max fields | Raw syscscolsegments bytes remain fixture-tested |
| §7.2 dictionary metadata | [`sys.column_store_segments`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17); [Rusanu 2012 columnstore internals](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/); [Neugebauer part 21 `DBCC CSINDEX`](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/) | Columnstore dictionaries are separate metadata/blobs referenced by segments | Raw syscsdictionaries bytes remain fixture-tested |
| §7.3 segment blob layout | [Larson 2011 DOI](https://doi.org/10.1145/1989323.1989448); [Larson 2015 PDF](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf); [Neugebauer part 21](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/); [Paul White grouped aggregate pushdown](https://www.sql.kiwi/2019/04/grouped-aggregate-pushdown/) | Segment decode pipeline uses value/dictionary encoding, RLE, and bit-packing | Exact blob offsets remain fixture-tested |
| §7.4 columnstore archival | [Data compression docs](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/data-compression?view=sql-server-ver17); [Larson 2015 PDF](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf); [Neugebauer part 40](https://www.nikoport.com/2014/09/09/clustered-columnstore-indexes-part-40-compression-algorithms/) | ARCHIVE adds an extra compression layer over columnstore data | Exact archive wrapper bytes remain fixture-tested |
| §7.5 columnstore LOB blob preamble | [Rusanu 2012 columnstore internals](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/); [Neugebauer part 21](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/) | Columnstore data is stored in LOB blobs with segment/dictionary payloads | Preamble/separator bytes remain fixture-tested |
| §7.6 small UTF-16 dictionary | [Larson 2011 DOI](https://doi.org/10.1145/1989323.1989448); [Larson 2015 PDF](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf); [Rusanu 2012](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/); [Neugebauer part 40](https://www.nikoport.com/2014/09/09/clustered-columnstore-indexes-part-40-compression-algorithms/) | String dictionary encoding is part of columnstore compression | Exact small-dictionary payload remains fixture-tested |
| §7.6 large dictionary (G44, xVelocity v4) | [MS-XLDM §2.3.2 Column Data Dictionary](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xldm/8c62e8ce-f605-488d-81e9-4ecdb7686a52); [`sys.column_store_dictionaries` (`type` enum)](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-dictionaries-transact-sql?view=sql-server-ver17); [PBIXray — VertiPaq dictionaries & hash indexes](https://www.pbixray.com/posts/vertipaq-dictionaries-and-hash-indexes/); [Hugoberry/pbix-dictionary-compression](https://github.com/Hugoberry/pbix-dictionary-compression); [Hugoberry/xmhuffman](https://github.com/Hugoberry/xmhuffman-cython); [d0nk3yhm VertiPaq spec](https://github.com/d0nk3yhm/pbix-mcp/blob/main/docs/vertipaq-spec.md); [xmhuffman PyPI v0.3.0](https://pypi.org/project/xmhuffman/) | The large columnstore string dictionary is the xVelocity/VertiPaq dictionary family; `XMHUFFMAN` `decode_page(bitstream, encode_array_128, offsets, total_bits, swap=True)` API confirmed: `offsets` = per-string start bit offsets from `vector_of_record_handle_structures`; `total_bits` = `store_total_bits` end sentinel; `end = offsets[s+1]` for non-last strings and `total_bits` for last string — blob 2001 fix: pass all 1200 handles (including k=1199) and `total_bits=555022` with the raw CBUF `raw[9844:]` | Columnstore blob is a **sibling** of MS-XLDM `.dictionary`, not byte-identical (no PBIX page sentinels `0xDDCCBBAA`/`0xCDABCDAB`); `entry_count=1199` vs `total_distinct_count=1200` explained by one string in blob 23844 bookmark |
| §7.7 enc=5 raw/off-row | [`sys.column_store_segments` (`encoding_type=5`)](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17); [Neugebauer part 21](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/); [Paul White grouped aggregate pushdown](https://www.sql.kiwi/2019/04/grouped-aggregate-pushdown/) | Encoding type 5 is string/binary store-by-value without dictionary | Exact Format A-D byte layouts remain `[EMPIRICAL]` |
| §8.2 Kraft sync marker | [MS-XCA Huffman construction](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/35a83e96-981d-48ed-a4eb-0b9cc6b51440); [MS-XCA processing](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/26db8e62-bbd8-472c-a09e-623f6de10f0b); [Kraft-McMillan PDF](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/67d8e68cd8fda55366e3f9f0a9465c17_MIT6_441S16_chapter_6.pdf) | XPRESS begins with Huffman code lengths; Kraft completeness is a valid prefix-code invariant | MSSQLBAK record-header semantics remain `[EMPIRICAL]` |
| §9.1 log tail | [Paul Randal storage/log internals](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/); [Rusanu: What is an LSN](https://rusanu.com/2012/01/17/what-is-an-lsn-log-sequence-number/) | Log records describe transaction changes and can be inspected through SQL Server tools | Exact backup-tail framing remains fixture-tested |
| §12.2 V04 Hekaton/XTP | [Hekaton SIGMOD 2013 DOI](https://doi.org/10.1145/2463676.2463710); [`FREED14` CMU mirror](https://15721.courses.cs.cmu.edu/spring2016/papers/freedman-ieee2014.pdf); [XTP checkpoint files DMV](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-xtp-checkpoint-files-transact-sql); [XTP durability docs](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/durability-for-memory-optimized-tables); `MS-BAK-MOT`; `MSBLOG-STORAGE`; `MSBLOG-STATE`; `NEDOTTER-BAK`; `SQLSHACK-CKPT`; `SQLPASSION-XTP`; `SQLPASSION-PERF`; `SLIDESHARE-IMOLTP` | Memory-optimized table data is stored outside normal B-tree pages in XTP structures; `FREED14` confirms: Hekaton uses latch-free hash/range indexes (no buffer pool), durability via log + checkpoint, tables rebuilt entirely from checkpoint+logs at recovery — corroborates why XTP blobs appear in `.bak`; `MS-BAK-MOT` documents the CFP-state backup table: ACTIVE/WAITING_FOR_LOG_TRUNCATION = full file bytes backed up, PRECREATED/UNDER_CONSTRUCTION/MERGE_TARGET = metadata only; `MSBLOG-STORAGE` confirms 128 MB data / 8 MB delta default CFP sizes and the ≤50%-active-rows merge trigger; `SLIDESHARE-IMOLTP` (Microsoft CSS) reveals binary checkpoint file format: fixed `"CKPT"` magic in file header block (4 KB), subsequent blocks each carry a Block Header followed by Data Rows, ROOT and DELTA files use 4 KB blocks, MVCC timestamps present in each row for visibility; `SQLSHACK-CKPT` confirms `.HKCKP` files live in `$HKv2` subfolder — matching the `/$HKv2` signature observed in `.bak` stream; `NEDOTTER-BAK` documents per-block CHECKSUM verified during backup (backup fails on mismatch) and FILESTREAM type `"S"` for the memory-optimized filegroup | XTP row payload layout (fixed + variable-length column descriptors, commit-timestamp field offsets) remains `[EMPIRICAL]` from mssqlbak probe fixtures; object-ID-to-CFP mapping is not documented in any public source found |
| §12.2 V06 enc=2 numeric dictionary | [Larson 2011 DOI](https://doi.org/10.1145/1989323.1989448); [Larson 2015 PDF](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf); [Rusanu 2012](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/); [Neugebauer part 21](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/) | Columnstore can use dictionaries plus encoded segment IDs | Integer numeric-dictionary cases remain fixture-tested |
| §12.2 V12 bit column packing | [Paul Randal: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/); [OrcaMDF](https://github.com/improvedk/OrcaMDF) | Multiple `bit` columns are bit-packed in records | Exact `bit_shift` mapping remains fixture-tested |
| §12.2 V13 temporal period columns | [System-versioned temporal tables](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables); [sys.columns (`is_hidden`, `generated_always_type`)](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql); [Create a System-Versioned Temporal Table](https://learn.microsoft.com/en-us/sql/relational-databases/tables/creating-a-system-versioned-temporal-table) — *"Referencing existing columns in PERIOD definition implicitly changes `generated_always_type` to `AS_ROW_START` and `AS_ROW_END` for those columns"* (current table only); [Temporal table considerations and limitations](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-considerations-and-limitations) — history schema alignment is count/names/types only, NOT `generated_always_type`; [sys.periods](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-periods-transact-sql); [MSSQLTips: Querying temporal metadata](https://www.mssqltips.com/sqlservertip/5145/querying-sql-server-temporal-table-metadata/) — shows type 1/2 in practice; [DBA.SE: conditionally switch versioning off](https://dba.stackexchange.com/questions/319881/conditionally-switch-history-on-temporal-tables-off) — uses `generated_always_type > 0` only on current table | `syscolpars.status` bits 28–29 (`0x10000000`/`0x20000000`) encode AS_ROW_START/AS_ROW_END on current table only; history table period columns have bits clear (plain datetime2 — schema-alignment doc confirms only count/name/type must match, not `generated_always_type`); `is_hidden` bit 13 (`0x00002000`) confirmed from `temporal_hidden_full.bak` PageStore XOR analysis: `0x10002001 XOR 0x10000001 = 0x00002000` | `V13_probe_results.txt`; `test_temporal_current_generated_always_type`; `test_temporal_history_generated_always_type_zero` |

## Canonical Link Map (Names / PDFs / URLs)

Use this map for every shorthand token used in this document and related docs
(`BAK_FORMAT_SPEC.md`, `260616-2-fixture-dbcc-page-verifier.md`,
`260616-3-random-order-fixtures-plan.md`, `260616-status.md`).

### SQL Server engine blogs and articles

| Token / name | URL |
|--------------|-----|
| `R-PAGE` — Paul Randal, Anatomy of a page | [https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/) |
| `R-IAM` — Paul Randal, IAM pages, chains, allocation units | [https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-iam-pages-iam-chains-and-allocation-units/](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-iam-pages-iam-chains-and-allocation-units/) |
| `R-ALLOC` — Paul Randal, GAM/SGAM/PFS | [https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-gam-sgam-pfs-and-other-allocation-maps/](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-gam-sgam-pfs-and-other-allocation-maps/) |
| `R-ALLOCID` — Paul Randal, allocation unit IDs | [https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/) |
| `R-REC` — Paul Randal, Anatomy of a record | [https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/) |
| `R-CSI2012` — Remus Rusanu, SQL Server 2012 columnstore internals | [https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/) |
| Paul White — Grouped Aggregate Pushdown / `DBCC CSINDEX` usage | [https://www.sql.kiwi/2019/04/grouped-aggregate-pushdown/](https://www.sql.kiwi/2019/04/grouped-aggregate-pushdown/) |
| Niko Neugebauer — `DBCC CSINDEX` syntax (part 21) | [https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/](https://www.nikoport.com/2013/11/07/clustered-columnstore-indexes-part-21-dbcc-csindex/) |
| `KAZ-LOB` — Kazamiya forensicist blog, MSSQL forensics (4) — LOB data structure | [https://www.kazamiya.net/en/mssql_4n6-04](https://www.kazamiya.net/en/mssql_4n6-04) |
| `KOR-LOB` — Dmitri Korotkevitch, SQL Server Storage Engine: LOB Storage | [https://aboutsqlserver.com/2013/11/05/sql-server-storage-engine-lob-storage/](https://aboutsqlserver.com/2013/11/05/sql-server-storage-engine-lob-storage/) |
| Stuart Moore — compressed backup header probing | [https://stuart-moore.com/reading-sql-server-backup-file-headers-directly-using-powershell/](https://stuart-moore.com/reading-sql-server-backup-file-headers-directly-using-powershell/) |
| `INSOMNIA-2008` — Brett Moore (Insomnia Security), ISVA-080709.1: SQL Server Corrupt Backup File Heap Overflow | [https://seclists.org/fulldisclosure/2008/Jul/101](https://seclists.org/fulldisclosure/2008/Jul/101); [local copy](papers/cve-2008-0107-insomnia-isva-080709-1.txt) |
| `IDEFENSE-2008` — iDefense Security Advisory 07.08.08: SQL Server Restore Integer Underflow Vulnerability | [https://seclists.org/bugtraq/2008/Jul/61](https://seclists.org/bugtraq/2008/Jul/61); [local copy](papers/cve-2008-0107-idefense-advisory.txt) |
| `BERTRAND-XE` — Aaron Bertrand, T-SQL Tuesday #67: New Backup/Restore Extended Events (SQL Server 2016, MSDA/MSTL stream names) | [https://sqlperformance.com/2015/06/extended-events/t-sql-tuesday-67-backup-restore](https://sqlperformance.com/2015/06/extended-events/t-sql-tuesday-67-backup-restore); [local copy](papers/sqlperformance-bertrand-xe-backup-restore-progress-trace-2015.txt) |
| `DORR-2008` — Bob Dorr (Microsoft PSS SQL Senior Escalation Engineer), "How It Works: What is Restore/Backup Doing?" | [https://learn.microsoft.com/en-us/archive/blogs/psssql/how-it-works-what-is-restorebackup-doing](https://learn.microsoft.com/en-us/archive/blogs/psssql/how-it-works-what-is-restorebackup-doing); [local copy](papers/pss-sql-blog-how-it-works-restore-backup-dorr-2008.txt) |
| `SQLBEK-INSIDE` — Andy Yun, "A Peek Inside a SQL Server Backup File" (byte-for-byte MDF copy, hex compare via Beyond Compare) | [https://sqlbek.wordpress.com/2022/05/11/inside-a-sql-server-backup-file/](https://sqlbek.wordpress.com/2022/05/11/inside-a-sql-server-backup-file/); [local copy](papers/sqlbek-inside-a-sql-server-backup-file-2022.txt) |
| `SQLBEK-SERIES` — Andy Yun, "SQL Server Backup Internals" series (Parts 1–5, trace flags 3004/3014/3213) | [https://sqlbek.wordpress.com/2023/07/18/sql-server-backup-internals-part-1/](https://sqlbek.wordpress.com/2023/07/18/sql-server-backup-internals-part-1/) |
| MSSQLTips — Querying SQL Server Temporal Table MetaData | [https://www.mssqltips.com/sqlservertip/5145/querying-sql-server-temporal-table-metadata/](https://www.mssqltips.com/sqlservertip/5145/querying-sql-server-temporal-table-metadata/) |
| sqlperformance.com — SQL Server 2016 Temporal Table Query Plan Behaviour (Hugo Kornelis) | [https://sqlperformance.com/2016/06/sql-server-2016/temporal-table-query-plan-behaviour](https://sqlperformance.com/2016/06/sql-server-2016/temporal-table-query-plan-behaviour) |
| DBA.SE — syscolpars CPM bitmask flags | [https://dba.stackexchange.com/questions/158336/what-is-the-system-view-for-sys-syscolpars](https://dba.stackexchange.com/questions/158336/what-is-the-system-view-for-sys-syscolpars) |
| DBA.SE — conditionally switch temporal history off | [https://dba.stackexchange.com/questions/319881/conditionally-switch-history-on-temporal-tables-off](https://dba.stackexchange.com/questions/319881/conditionally-switch-history-on-temporal-tables-off) |
| Randolph West — how SQL Server stores `uniqueidentifier` (storage internals series) | [https://bornsql.ca/blog/how-sql-server-stores-data-types-guid/](https://bornsql.ca/blog/how-sql-server-stores-data-types-guid/) |
| Dmitri Korotkevitch — clustered columnstore delta store & delete bitmap | [https://aboutsqlserver.com/2014/05/06/clustered-columnstore-indexes-exploring-delta-store-and-delete-bitmap/](https://aboutsqlserver.com/2014/05/06/clustered-columnstore-indexes-exploring-delta-store-and-delete-bitmap/) |
| `SQLPASSION-XTP` — Klaus Aschenbrenner (SQLpassion.at), "Extreme Transaction Processing (XTP, Hekaton) – the solution to everything?" (2013-08-12): XTP tables live in FILESTREAM filegroup; MVCC/no-locking; indexes (hash + range) rebuilt from scratch at startup; data recovery pipeline: load data files → apply deltas → replay log tail | [https://www.sqlpassion.at/archive/2013/08/12/extreme-transaction-processing-xtp-hekaton-the-solution-to-everything/](https://www.sqlpassion.at/archive/2013/08/12/extreme-transaction-processing-xtp-hekaton-the-solution-to-everything/) |
| `SQLPASSION-PERF` — Klaus Aschenbrenner (SQLpassion.at), "Configuring the In-Memory OLTP File Group for High Performance" (2014-06-16): Offline Checkpoint Worker pulls committed transactions from log → data/delta files; only redo log records written (no undo); rollback uses the prior version already in memory | [https://www.sqlpassion.at/archive/2014/06/16/configuring-the-in-memory-oltp-file-group-for-high-performance/](https://www.sqlpassion.at/archive/2014/06/16/configuring-the-in-memory-oltp-file-group-for-high-performance/) |
| `SQLPASSION-TXNLOG` — Klaus Aschenbrenner (SQLpassion.at), "Transaction Logging in In-Memory OLTP (Hekaton)" (2015-03-09): `LOP_HK` log record bundles multiple XTP changes; inspect via `sys.fn_dblog_xtp`; logical changes only — index-level changes not logged | [https://www.sqlpassion.at/archive/2015/03/09/transaction-logging-memory-oltp-hekaton/](https://www.sqlpassion.at/archive/2015/03/09/transaction-logging-memory-oltp-hekaton/) |
| `SQLSHACK-INTRO` — Luan Moreno M. Maciel (SQLShack), "In-Memory OLTP Series – Introduction" (2015): Data File = insert-only rows, Delta File = deleted-row references; files stored in MEMORY_OPTIMIZED_DATA filegroup; sequential I/O model; SCHEMA vs SCHEMA_AND_DATA durability options | [https://www.sqlshack.com/memory-oltp-series-introduction/](https://www.sqlshack.com/memory-oltp-series-introduction/) |
| `SQLSHACK-MON` — Prashanth Jayaram (SQLShack), "How to monitor internal data structures of SQL Server In-Memory database objects" (2019): DMV-based monitoring of CFP containers via `sys.dm_db_xtp_checkpoint_files`; reiterates Data file = inserted records, Delta file = removed-record references, merged over time by GC. Monitoring/DMV focus — no byte-level layout. | [https://www.sqlshack.com/how-to-monitor-internal-data-structures-of-sql-server-in-memory-database-objects/](https://www.sqlshack.com/how-to-monitor-internal-data-structures-of-sql-server-in-memory-database-objects/) |
| `RG-MOT` — Murilo Miranda (Red-Gate Simple Talk), "In-Memory OLTP – Understanding Memory-Optimized Tables" (2016): MVCC **row header** = Begin Timestamp (8 B) + End Timestamp (8 B) + StatementID + IndexLink Count, then index pointers, then the user-column payload; UPDATE = INSERT + DELETE (immutable rows); durable MOT operations are logged and checkpointed. Corroborates the framing header as MVCC begin/end timestamps and the insert-only nature of bulk-loaded `_inmem` copies. Conceptual, not byte-level. | [https://www.red-gate.com/simple-talk/databases/sql-server/database-administration-sql-server/in-memory-oltp-understanding-memory-optimized-tables/](https://www.red-gate.com/simple-talk/databases/sql-server/database-administration-sql-server/in-memory-oltp-understanding-memory-optimized-tables/) |
| `SQLSHACK-CKPT` — SQLShack, "SQL Server 2016 Memory-Optimized Tables – The Checkpoint operation": `.HKCKP` files reside in `$HKv2` subfolder (matches `/$HKv2` signature seen in `.bak` stream); ROOT files = system metadata; sequential writes to CFPs; recovery loads data/delta files in parallel threads, then replays log tail | [https://www.sqlshack.com/sql-server-2016-memory-optimized-tables-checkpoint-operation/](https://www.sqlshack.com/sql-server-2016-memory-optimized-tables-checkpoint-operation/) |
| `NEDOTTER-BAK` — Ned Otter, "Backup and Recovery for SQL Server databases that contain durable memory-optimized data" (2016): per-block CHECKSUM computed at write and re-verified during backup (backup fails on mismatch); FILESTREAM type `'S'` for memory-optimized filegroup (same type code as FileTable/Filestream — no per-type differentiation inside `.bak`); restore must stream all CFP data into RAM before recovery completes | [http://nedotter.com/archive/2016/02/backup-and-recovery-for-sql-server-databases-that-contain-durable-memory-optimized-data/](http://nedotter.com/archive/2016/02/backup-and-recovery-for-sql-server-databases-that-contain-durable-memory-optimized-data/) |
| `SLIDESHARE-IMOLTP` — "Inside SQL Server In-Memory OLTP" (Microsoft CSS internal presentation, SlideShare): **critical binary format**: checkpoint data file begins with a 4 KB file-header block containing fixed `"CKPT"` magic + TYPE field; subsequent blocks each carry a Block Header followed by Data Rows; ROOT and DELTA files use 4 KB fixed-size blocks; data-row blocks are 256 KB; MVCC timestamps embedded in each row for visibility (UPDATE = DELETE + INSERT, immutable row model) | [https://www.slideshare.net/slideshow/inside-sql-server-inmemory-oltp-72339103/72339103](https://www.slideshare.net/slideshow/inside-sql-server-inmemory-oltp-72339103/72339103) |
| Niko Neugebauer — invisible row groups (part 22) | [https://www.nikoport.com/2013/12/10/clustered-columnstore-indexes-part-22-invisible-row-groups/](https://www.nikoport.com/2013/12/10/clustered-columnstore-indexes-part-22-invisible-row-groups/) |
| `PBIXRAY-DICT` — PBIXray, VertiPaq dictionaries & hash indexes | [https://www.pbixray.com/posts/vertipaq-dictionaries-and-hash-indexes/](https://www.pbixray.com/posts/vertipaq-dictionaries-and-hash-indexes/) |

### Microsoft docs / specifications

| Token / name | URL |
|--------------|-----|
| `MS-BACKUPMEDIASET` — `backupmediaset` system table (`software_vendor_id = 0x1200`, `MTF_major_version`) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/backupmediaset-transact-sql?view=sql-server-ver16](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/backupmediaset-transact-sql?view=sql-server-ver16) |
| `MS-RESTORE-HEADERONLY` — `RESTORE HEADERONLY` result set (`SoftwareVendorId = 4608 / 0x1200`) | [https://learn.microsoft.com/en-us/sql/t-sql/statements/restore-statements-headeronly-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/t-sql/statements/restore-statements-headeronly-transact-sql?view=sql-server-ver17) |
| `MS-SEG` — `sys.column_store_segments` (incl. `min_deep_data`/`max_deep_data`) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17) |
| `MS-RG` — `sys.column_store_row_groups` (state enum) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-row-groups-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-row-groups-transact-sql?view=sql-server-ver17) |
| `MS-RGSTATS` — `sys.dm_db_column_store_row_group_physical_stats` | [https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-column-store-row-group-physical-stats-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-column-store-row-group-physical-stats-transact-sql?view=sql-server-ver17) |
| `MS-ROW` — row compression implementation | [https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/row-compression-implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/row-compression-implementation) |
| `MS-PAGE` — page compression implementation | [https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/page-compression-implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/page-compression-implementation) |
| Backup compression (SQL Server) | [https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-compression-sql-server](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-compression-sql-server) |
| `RESTORE HEADERONLY` | [https://learn.microsoft.com/en-us/sql/t-sql/statements/restore-statements-headeronly-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/t-sql/statements/restore-statements-headeronly-transact-sql?view=sql-server-ver17) |
| `MTF` — Microsoft Tape Format Specification v1.00a | original PDF: [papers/mtf-v100a-spec.pdf](papers/mtf-v100a-spec.pdf); Chinese translation (all sections): [https://chenjianlong.gitbooks.io/microsoft-tape-format-specification/content/](https://chenjianlong.gitbooks.io/microsoft-tape-format-specification/content/) |
| `MTF-H` — KyleBruene/mtf C header — MTF struct definitions and bitmasks | [https://github.com/KyleBruene/mtf/blob/master/mtf.h](https://github.com/KyleBruene/mtf/blob/master/mtf.h) |
| MS-XCA (Xpress Compression Algorithm) overview | [https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/) |
| MS-XCA Huffman code construction | [https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/35a83e96-981d-48ed-a4eb-0b9cc6b51440](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/35a83e96-981d-48ed-a4eb-0b9cc6b51440) |
| MS-XCA processing phase | [https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/26db8e62-bbd8-472c-a09e-623f6de10f0b](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/26db8e62-bbd8-472c-a09e-623f6de10f0b) |
| MS-BINXML open spec (landing) | [https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-binxml/](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-binxml/) |
| `MS-XLDM` — Spreadsheet Data Model File Format (§2.3.2 Column Data Dictionary; xVelocity/VertiPaq dict) | [https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xldm/8c62e8ce-f605-488d-81e9-4ecdb7686a52](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xldm/8c62e8ce-f605-488d-81e9-4ecdb7686a52) |
| `MS-DICT` — `sys.column_store_dictionaries` (`type` enum 1/3/4 = hash int/string/float) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-dictionaries-transact-sql?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-dictionaries-transact-sql?view=sql-server-ver17) |
| DacServices (DacFx API) | [https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac.dacservices?view=sql-dacfx-162](https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac.dacservices?view=sql-dacfx-162) |
| Dac namespace (`BacPackage` / `DacPackage`) | [https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac?view=sql-dacfx-162](https://learn.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.dac?view=sql-dacfx-162) |
| Export BACPAC guidance | [https://learn.microsoft.com/en-us/sql/tools/sql-database-projects/concepts/data-tier-applications/export-bacpac-file](https://learn.microsoft.com/en-us/sql/tools/sql-database-projects/concepts/data-tier-applications/export-bacpac-file) |
| Always Encrypted (database engine) | [https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine) |
| System-versioned temporal tables | [https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables) |
| Create a System-Versioned Temporal Table | [https://learn.microsoft.com/en-us/sql/relational-databases/tables/creating-a-system-versioned-temporal-table](https://learn.microsoft.com/en-us/sql/relational-databases/tables/creating-a-system-versioned-temporal-table) |
| Temporal table considerations and limitations | [https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-considerations-and-limitations](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-considerations-and-limitations) |
| `sys.periods` (temporal period column IDs) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-periods-transact-sql](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-periods-transact-sql) |
| `sys.columns` (`is_hidden`, `generated_always_type`) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql) |
| Temporal table metadata views and functions | [https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-metadata-views-and-functions](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-metadata-views-and-functions) |
| `MS-XTP-CFP` — `sys.dm_db_xtp_checkpoint_files` DMV (state enum, type DATA/DELTA/ROOT/LARGE_DATA, file_size, inserted_row_count) | [https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-xtp-checkpoint-files-transact-sql](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-xtp-checkpoint-files-transact-sql) |
| `MS-DUR-MOT` — Durability for memory-optimized tables (CFP structure, transaction-range tagging, merge policy) | [https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/durability-for-memory-optimized-tables](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/durability-for-memory-optimized-tables) |
| `MS-BAK-MOT` — Database backup with memory-optimized tables (CFP state → what gets backed up table; ACTIVE/WAITING_FOR_LOG_TRUNCATION = full bytes; PRECREATED/UNDER_CONSTRUCTION/MERGE_TARGET = metadata only; differential: data files only if closed after last full, delta files always) | [https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/backing-up-a-database-with-memory-optimized-tables](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/backing-up-a-database-with-memory-optimized-tables) |
| `MSBLOG-STORAGE` — Microsoft SQL Server Blog, "Storage Allocation and Management for Memory-Optimized Tables" (Jan 2014): 128 MB data / 8 MB delta default CFP sizes; up to 8192 CFPs per database; ACTIVE CFPs ≈ 2× in-memory size; merge triggered when active rows < 50% across adjacent CFPs | [https://www.microsoft.com/en-us/sql-server/blog/2014/01/16/storage-allocation-and-management-for-memory-optimized-tables/](https://www.microsoft.com/en-us/sql-server/blog/2014/01/16/storage-allocation-and-management-for-memory-optimized-tables/) |
| `MSBLOG-STATE` — Microsoft SQL Server Blog, "State Transition of Checkpoint Files…" (Jan 2014): UNDER CONSTRUCTION → ACTIVE on checkpoint; RTM uses 16 MB data / 1 MB delta on machines with ≤16 GB RAM | [https://www.microsoft.com/en-us/sql-server/blog/2014/01/23/state-transition-of-checkpoint-files-in-databases-with-memory-optimized-tables/](https://www.microsoft.com/en-us/sql-server/blog/2014/01/23/state-transition-of-checkpoint-files-in-databases-with-memory-optimized-tables/) |

### Papers / PDFs

| Token / name | URL |
|--------------|-----|
| `L15` — Larson et al., VLDB 2015 (PDF) | [https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf) |
| `L11` — Larson et al., SIGMOD 2011 (DOI + free CMU mirror) | [https://doi.org/10.1145/1989323.1989448](https://doi.org/10.1145/1989323.1989448); [https://15721.courses.cs.cmu.edu/spring2016/papers/p1177-larson.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/p1177-larson.pdf) — confirmed downloadable 2026-06-17 — **§2.2.1 gives the canonical value-encoding formula for C1b**: decimal exponent is positive (scale up by 10^exp, then subtract base); integer exponent is negative (scale down by 10^|exp|, then subtract base); reconstruct via `actual = (stored + base_id) / 10^exponent` where `exponent` = `magnitude` in `sys.column_store_segments` |
| `L13` — Larson et al., SIGMOD 2013 (DOI + CMU mirror) | [https://doi.org/10.1145/2463676.2463708](https://doi.org/10.1145/2463676.2463708); [https://15721.courses.cs.cmu.edu/spring2016/papers/larson-sigmod2013.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/larson-sigmod2013.pdf) — covers clustered CCI (SQL Server 2014): archival compression, delta store, delete bitmap, trickle bulk load, ARCHIVE layer over xVelocity segments |
| `H13` — Hekaton SIGMOD 2013 (DOI) | [https://doi.org/10.1145/2463676.2463710](https://doi.org/10.1145/2463676.2463710) |
| `FREED14` — Freedman, Ismert, Larson, "Compilation in the Microsoft SQL Server Hekaton Engine", IEEE Data Engineering Bulletin 2014 (CMU mirror) | [https://15721.courses.cs.cmu.edu/spring2016/papers/freedman-ieee2014.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/freedman-ieee2014.pdf) — co-authored by Per-Åke Larson (same as L11/L13/L15); describes Hekaton native compilation, latch-free index architecture (hash + range, no buffer pool), and durability model: *"During recovery Hekaton tables and their indexes are rebuilt entirely from the latest checkpoint and logs"* — directly corroborates why XTP checkpoint blobs appear in `.bak` files (§12.2 V04) |
| `HKCC12` — Larson, Blanas, Diaconu, Freedman, Patel, Zwilling, "High-Performance Concurrency Control Mechanisms for Main-Memory Databases", VLDB 2012 (CMU mirror) | [https://15721.courses.cs.cmu.edu/spring2016/papers/p298-larson.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/p298-larson.pdf) — Hekaton MVCC prototype; explains version timestamp model (begin/end timestamp fields per row version), latch-free hash indexes, optimistic vs pessimistic MVCC — background for Hekaton in-memory row format, does not document backup byte layout |
| `Z09` — Zukowski PhD thesis (PDF) | [https://ir.cwi.nl/pub/14075/14075B.pdf](https://ir.cwi.nl/pub/14075/14075B.pdf) — §6.2 defines classical FOR: `bitpack_stored = c[i] − block_min`, i.e. stored values are block-relative offsets. SQL Server CCI does **not** use this scheme in the bitpack: stored biased values are absolute. The CCI fragment table's `field1` (0 or 2) is a **block-type indicator** for null-zone detection, not a FOR compression base; useful for understanding why the fragment table superficially resembles a FOR table but is not one. Predicate-pushdown skip-scan is the intended use of the per-block range info. |
| `LB15` — Lemire & Boytsov (arXiv) | [https://arxiv.org/abs/1209.2137](https://arxiv.org/abs/1209.2137) |
| `D19` — Damme, Habich, Hildebrandt, Lehner, lightweight integer compression survey + cost model (ACM TODS 2019) | [https://dl.acm.org/doi/10.1145/3323991](https://dl.acm.org/doi/10.1145/3323991) |
| `BTR23` — BtrBlocks: efficient columnar compression (TUM, SIGMOD 2023) | [https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf) |
| Lemire — FastPFor / FrameOfReference reference C++ implementations (GitHub) | [https://github.com/fast-pack/FastPFOR](https://github.com/fast-pack/FastPFOR) · [https://github.com/lemire/FrameOfReference](https://github.com/lemire/FrameOfReference) |
| Abadi, Boncz, Harizopoulos et al. — column-oriented database systems survey (2013) | [https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf) |
| Kraft-McMillan theorem reference (MIT OCW PDF) | [https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/67d8e68cd8fda55366e3f9f0a9465c17_MIT6_441S16_chapter_6.pdf](https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/67d8e68cd8fda55366e3f9f0a9465c17_MIT6_441S16_chapter_6.pdf) |

### Open-source corroborators and related repos

| Name | URL |
|------|-----|
| OrcaMDF | [https://github.com/improvedk/OrcaMDF](https://github.com/improvedk/OrcaMDF) |
| OrcaSql | [https://github.com/ycherkes/OrcaSql](https://github.com/ycherkes/OrcaSql) |
| `gsiems/bac-tract` | [https://github.com/gsiems/bac-tract](https://github.com/gsiems/bac-tract) |
| RoboKiwi BACPAC layout note | [https://www.robokiwi.com/wiki/data/sql/mssql/bacpac/](https://www.robokiwi.com/wiki/data/sql/mssql/bacpac/) |
| Bob Beauchemin DACFx 3.0 formats | [https://www.sqlskills.com/blogs/bobb/dacfx-3-0-the-new-file-formats/](https://www.sqlskills.com/blogs/bobb/dacfx-3-0-the-new-file-formats/) |
| Andy Mallon on BACPAC `.BCP` files | [https://am2.co/2021/08/what-are-the-bcp-files-inside-a-bacpak-file/](https://am2.co/2021/08/what-are-the-bcp-files-inside-a-bacpak-file/) |
| `HUGO-DICT` — Hugoberry/pbix-dictionary-compression (C++ MS-XLDM §2.3.2 decoder) | [https://github.com/Hugoberry/pbix-dictionary-compression](https://github.com/Hugoberry/pbix-dictionary-compression) |
| `XMHUFFMAN` — Hugoberry/xmhuffman-cython (canonical-Huffman xVelocity string-page decoder) | [https://github.com/Hugoberry/xmhuffman-cython](https://github.com/Hugoberry/xmhuffman-cython) |
| `D0NK-VPAQ` — d0nk3yhm/pbix-mcp VertiPaq binary format spec | [https://github.com/d0nk3yhm/pbix-mcp/blob/main/docs/vertipaq-spec.md](https://github.com/d0nk3yhm/pbix-mcp/blob/main/docs/vertipaq-spec.md) |
| `SQLSRVFORENSICS` — aarsakian/SQLServerForensics: Go forensics tool parsing BAK files as TAPE archives + raw page structure (no restore required) | [https://github.com/aarsakian/SQLServerForensics](https://github.com/aarsakian/SQLServerForensics) |
| `MTF-RS` — rroohhh/mtf-rs: low-level Rust MTF parser; `MTFPageProvider` feeds raw pages directly to `mdf-rs` without unpacking the `.bak` | [https://github.com/rroohhh/mtf-rs](https://github.com/rroohhh/mtf-rs) |
| `MDF-RS` — rroohhh/mdf-rs: Rust MDF/BAK page parser (works via `MTFPageProvider` from `mtf-rs`) | [https://github.com/rroohhh/mdf-rs](https://github.com/rroohhh/mdf-rs) |
| `UNRAVEL-BAK` — klandermans/unraveling_sql_server_bak: open-source BAK-to-SQLite converter | [https://github.com/klandermans/unraveling_sql_server_bak](https://github.com/klandermans/unraveling_sql_server_bak) |

## Remaining Internal-Only Sections

These remain `[EMPIRICAL]` because no external source currently corroborates the
specific byte layout:

| Spec section | What is missing |
|--------------|-----------------|
| §1.2.1–§1.2.4 MSSQLBAK compressed container | Public sources corroborate the `MSSQLBAK` magic and proprietary-compression boundary, but not record-header semantics |
| §7.7 Format A-D | Public sources corroborate `encoding_type=5` at a high level, but not the four exact byte subformats |

## Latest Search Results

### BACPAC

Useful sources found:

- Microsoft DacFx API docs (`BacPackage`, `DacServices.ExportBacpac`)
- MicrosoftDocs export-bacpac docs
- Bob Beauchemin, "DACFx 3.0: The new file formats"
- RoboKiwi BACPAC layout notes
- `gsiems/bac-tract`
- Andy Mallon on `.BCP` files inside BACPAC

Outcome: §1.3 and §1.3.4 moved to `[CORROBORATED]`.

### MSSQLBAK Compressed Container

Useful sources found:

- Stuart Moore, "Reading SQL Server Backup file headers directly using PowerShell"
- Microsoft `RESTORE HEADERONLY` docs
- Microsoft backup-compression docs / SQL Server 2022 QAT overview

Outcome: partial note added to §1.2. These sources support the magic/proprietary
boundary and `MS_XPRESS` algorithm metadata, but not the record headers.

### enc=5 Format A-D

Useful sources found:

- Microsoft `sys.column_store_segments` docs (`encoding_type=5`)
- Niko Neugebauer `DBCC CSINDEX`
- Paul White grouped aggregate pushdown / `DBCC CSINDEX`

Outcome: no retag of Format A-D. Next step is `DBCC CSINDEX(object_type=1)` capture
for fixtures that trigger each subformat.

### Kraft Sync Marker

Useful sources found:

- MS-XCA Huffman code construction and processing docs
- wimlib XPRESS decompressor comments
- Kraft-McMillan theorem references

Outcome: §8.2 moved to `[CORROBORATED]`.

### Degrees-of-separation round 2 — open-item leads (2026-06-16)

Walked the citation/author graph one more hop from Randal → Rusanu → White →
Neugebauer toward the **open** `260616-status.md` G-items (these are corroboration
leads for closing issues, not retags of existing `[CORROBORATED]` sections):

| Open item | New corroboration source | What it gives |
|-----------|--------------------------|---------------|
| **G6** UUID value decode | [Randolph West — how SQL Server stores `uniqueidentifier`](https://bornsql.ca/blog/how-sql-server-stores-data-types-guid/); [GUID binary encoding (Wikipedia)](https://en.wikipedia.org/wiki/Universally_unique_identifier#Encoding); [dba.stackexchange GUID layout](https://dba.stackexchange.com/questions/121869/sql-server-uniqueidentifier-guid-internal-representation) | Exact mixed-endian byte layout (`Data1` LE u32, `Data2`/`Data3` LE u16, `Data4` 8 bytes as-is). Closes the formatting half of G6's UUID test. |
| **G6** enc=5 ≥32,768-row boundary | [Paul White — grouped aggregate pushdown](https://www.sql.kiwi/2019/04/grouped-aggregate-pushdown/) | 64-bit bitpack unit = 7 × 9-bit subunits → 4,608 units = 32,256 rows; boundary is a bitpack-unit/chunk artifact. |
| **G1** row + null counts | [Dmitri Korotkevitch — delta store & delete bitmap](https://aboutsqlserver.com/2014/05/06/clustered-columnstore-indexes-exploring-delta-store-and-delete-bitmap/); [`sys.column_store_row_groups`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-row-groups-transact-sql?view=sql-server-ver17); [`sys.dm_db_column_store_row_group_physical_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-column-store-row-group-physical-stats-transact-sql?view=sql-server-ver17); Neugebauer [part 22 invisible row groups](https://www.nikoport.com/2013/12/10/clustered-columnstore-indexes-part-22-invisible-row-groups/) | State enum `0=INVISIBLE,1=OPEN,2=CLOSED,3=COMPRESSED,4=TOMBSTONE`; live rows = Σ(delta) + Σ(compressed − deleted), excluding INVISIBLE/TOMBSTONE. |
| **G3** string/UUID min/max | [`sys.column_store_segments` `min_deep_data`/`max_deep_data`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17) | SS2022+ exposes decoded string/binary/UUID segment min/max directly (`TRY_CAST(... AS uniqueidentifier)`), a cross-check for FOR-decoded values. |

Outcome: no `BAK_FORMAT_SPEC` retags (all four are open `[EMPIRICAL]`/open-TODO
items). Hints folded into `260616-status.md`; sources added to the link map below.

### Value Coverage Register sweep (2026-06-17)

Searched open publications for each open VC item. Findings by item:

| VC item | External sources found | What they confirm |
|---------|------------------------|-------------------|
| **VC01** SSET backup-kind flags | `MTF` spec (gitbooks translation), `MTF-H` (KyleBruene/mtf C header) | Flag bitmasks confirmed: `SSET_COPY_BIT=0x02`, `SSET_NORMAL_BIT=0x04`, `SSET_DIFFERENTIAL_BIT=0x08`, `SSET_INCREMENTAL_BIT=0x10`, `SSET_DAILY_BIT=0x20` — exactly match the spec; bits are mutually exclusive per data set |
| **VC02** LOB `btyp` values | `KAZ-LOB`, `KOR-LOB`, Microsoft SQL Server 2012 Internals (Kalen Delaney), sqlity.net TEXT MIX page article | btyp=3 (`DATA`), btyp=2 (`INTERNAL`), btyp=5 (`LARGE_ROOT_YUKON`) all documented with byte-level structures; all three corroborated independently |
| **VC03** btyp=2 `max_links` field | `KAZ-LOB` (struct layout), `KOR-LOB` (DBCC PAGE output showing `MaxLinks: 5`) | Field at btyp=2 offset +14 is `MaxLinks` (node link-slot capacity), **not** a format version. Values 0x0002 and 0x0004 are 2-slot and 4-slot INTERNAL node capacities. CurLinks (+16) and Level (+18) sub-header fields also corroborated — spec updated accordingly. |
| **VC04** MSSQLBAK version word 2 | (none found) | No open publication documents the MSSQLBAK proprietary container version-word fields. Remains `[EMPIRICAL]`. |
| **VC05** columnstore `block_size` = 512 | Neugebauer part 40, Rusanu 2012, Larson 2015 | xVelocity internal blob format described as "super-secret"; block_size parameter is not mentioned in any open source. Assumption remains unconfirmed. |
| **VC07** MTF `string_type` | `MTF` spec §5 common block header | `0x00`=none, `0x01`=ANSI, `0x02`=UTF-16LE confirmed by MTF v1.00a normative spec. |

Outcome: spec §6.2 updated to fix btyp=2 sub-header naming (flags→max_links/cur_links/level) and add SQL Server canonical type names. VC02 and VC03 rows updated in §13. `KAZ-LOB` and `KOR-LOB` tokens added to the link map. MTF spec tokens (`MTF`, `MTF-H`) added.

### V13 temporal period column internals sweep (2026-06-17)

Searched for external corroboration of two empirical probe findings:
1. `syscolpars.status` bits 28–29 encode `generated_always_type` (AS_ROW_START/AS_ROW_END).
2. History table period columns have these bits **clear** — they are plain datetime2 columns with `generated_always_type=0`.

| Source | What it gives |
|--------|---------------|
| MS Learn — [Create a System-Versioned Temporal Table](https://learn.microsoft.com/en-us/sql/relational-databases/tables/creating-a-system-versioned-temporal-table) | Normative: *"Referencing existing columns in PERIOD definition implicitly changes `generated_always_type` to `AS_ROW_START` and `AS_ROW_END` for those columns."* **"Those columns"** = current table only — history table counterparts are not changed. Also says adding PERIOD performs data consistency checks on **current** table only. |
| MS Learn — [Temporal table considerations and limitations](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-table-considerations-and-limitations) | History schema alignment requirement is: *"number of columns, column names, ordering, and data types"* — `generated_always_type` is explicitly **not** in the list. Confirms history period columns are plain datetime2 with `generated_always_type=0`. |
| MS Learn — [`sys.periods`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-periods-transact-sql) | Canonical catalog view for temporal periods; exposes `start_column_id`/`end_column_id` as object references. Does not duplicate `generated_always_type`. |
| MSSQLTips — [Querying SQL Server Temporal Table MetaData](https://www.mssqltips.com/sqlservertip/5145/querying-sql-server-temporal-table-metadata/) | Shows `sys.columns.generated_always_type = 1/2` for StartDate/EndDate on a **current** temporal table; no corresponding values shown for history table — corroborates our probe result. |
| DBA.SE — [conditionally switch history on temporal tables off](https://dba.stackexchange.com/questions/319881/conditionally-switch-history-on-temporal-tables-off) | Community answer uses `c.generated_always_type > 0` to detect **current** temporal tables — would not work if history tables also had type > 0. Implicitly confirms history table period columns return 0. |
| MS Learn — [`sys.columns` (`is_hidden`, `generated_always_type`)](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql) | Confirms `is_hidden` exists as a `bit` column in the view (SS2016+), but the internal `syscolpars.status` bit position for `is_hidden` is not documented in any public source found. |

**Key finding confirmed by these sources:** The MS docs and community practice converge on the same result as our empirical probe — `generated_always_type` is a property of the **current** table's period columns only. History table period columns are schema-identical but metadata-distinct: they are plain datetime2, `generated_always_type=0`, not `GENERATED ALWAYS AS ROW START/END`.

**All bits now confirmed.** `is_hidden` = bit 13 (`0x00002000`), found by XOR-ing matching period column status values from `temporal_hidden_full.bak` (hidden) vs `temporal_visible` (non-hidden).  No open publication documents this bitmask; the bit was identified empirically from a purpose-built fixture.

Outcome: V13 entry in Source Index expanded with 6 additional external sources. No retag needed — V13 was already `[CONFIRMED]` from empirical probe. `is_hidden` bit (bit 13, `0x00002000`) subsequently confirmed from `temporal_hidden_full.bak` PageStore XOR analysis; `Column.is_hidden` added to `catalog.py`; two new regression tests added.

### G44 large columnstore dictionary sweep (2026-06-17)

Searched for the format of the columnstore "version-4" large string dictionary
(§7.6, formerly `[UNKNOWN]`). The blob is the **xVelocity / VertiPaq dictionary
format**, shared by SQL Server columnstore, SSAS Tabular, Excel Power Pivot, and
Power BI.

| Source | What it gives |
|--------|---------------|
| `MS-XLDM` §2.3.2 Column Data Dictionary (normative) | The xVelocity dictionary structure (dict_type, hash-bin header, paged string store) for the sibling `.dictionary` file |
| `MS-DICT` (`sys.column_store_dictionaries.type`) | `type` enum `1 = hash int, 3 = hash string, 4 = hash float` — confirms "hash dictionary" naming and that on-disk `version = 4` ≠ catalog `type` |
| `PBIXRAY-DICT`, `D0NK-VPAQ`, `HUGO-DICT`, `XMHUFFMAN` | Clean-room byte layouts of the PBIX `.dictionary` (page sentinels `0xDDCCBBAA`/`0xCDABCDAB`, 128-byte canonical-Huffman `encode_array`, record handles) |

Verification against `cs_lob_preamble2.bak` (scan of the actual blobs):

- The dictionary is two blobs: a **hash index** (blob 2001, `version=4`,
  `entry_count=1199`, `hash_slots=8192`, binary pool — no plaintext ASCII) and a
  **sorted pool** (blob 23844, `version=7`, `entry_count=1200`).
- The sorted pool is **not** a flat array of plain strings.  It has a 1945-byte
  header, a 194-entry bookmark block (each entry: u16 size + 80-char ASCII string
  + 21-byte metadata), and a 6072-byte pool section.  The float32 at entry
  offset +90 encodes `step − 1` (data-ids between consecutive bookmarks),
  allowing rank-0..1199 reconstruction without the full string list.  Only 37
  full strings appear verbatim in the pool section; the rest use a compact
  format not yet decoded.
- The PBIX page sentinels `0xDDCCBBAA`/`0xCDABCDAB` are **absent** — the
  columnstore blob is a sibling of the MS-XLDM `.dictionary`, not byte-identical.

Outcome: §7.6 large-dictionary entry promoted `[UNKNOWN]` → `[CORROBORATED]` →
`[CONFIRMED]`.  Decoder (`_parse_v7_sorted_pool`, `_find_v7_sorted_pool`) decodes
194/1200 strings (bookmark positions).  Verifier sidecar `G44.json` (1200 entries,
from `SELECT id, long_str ORDER BY long_str`) ships in `tests/fixtures_2022/`.
3-test suite `test_g44_large_dict_*` in `test_columnstore.py` passes.  Binary pool
encoding of the v4 hash-dict (blob 2001, 46 412-byte post-hash region) is not yet
decoded; decoding it would extend coverage to all 1200 data-ids.

### 4-degree sweep from SQLEspresso — CCI and G44 open items (2026-06-17)

Starting from Monica Morehouse (Rathbun)'s SQLEspresso CCI blog series, traced 4 hops
through the SQL Server community to find new corroboration for the open items in
`260617-1-cci-correctness-and-dirty-path.md` and `260617-2-g44.md`.

**Degree 1 — SQLEspresso direct:**

| Source | What it gives |
|--------|---------------|
| `SQLESPRESSO-P3` | Confirms `varchar(max)`/`nvarchar(max)` not ideal for CCI; data types and workload must match; not directly useful for bug streams but closes "is LOB in CCI well-documented" question |

**Degree 2 — Directly cited / adjacent to SQLEspresso:**

| Source | What it gives |
|--------|---------------|
| `STAIR4` (Hugo Kornelis / SQLServerCentral) | **Best public explanation of `base_id`/`magnitude` for C1b**: *"when all values are between 12345 and 13579, base_id is set to 12345 (the actual value might be slightly less or more) and that number is subtracted"*; also: `null_value` = *"magic value SQL Server chosen to represent NULL in this segment"* (C1a) |
| `RG-CCI1` / `RG-CCI2` (Red-Gate Simple Talk) | Architecture overview with `has_nulls` / deleted-row metadata; confirms deleted rows stay in segment until rebuild |

**Degree 3 — SQL Server community connected to SQLServerCentral / Neugebauer:**

| Source | What it gives |
|--------|---------------|
| `N32` (Neugebauer part 32 "Size Does Matter") | Small rowgroups (100 rows) produce more segments → more dict/bitmap overhead; *"Deleted Bitmaps … no way to consult its size or content directly"* — confirms C1a small-segment null bitmap behavior is not publicly documented |
| `DARLING-RGE` (Erik Darling) | *"Information about NULLs is stored internally and can be used for rowgroup elimination"* — confirms `null_value`/`has_nulls` metadata is the segment-level NULL signal for C1a |
| `XMHUFFMAN-PYPI` (PyPI v0.3.0 API docs) | **G44 fix (✅ implemented b8993f1)**: `decode_page(bitstream, encode_array_128, offsets, total_bits, swap=True)` — `offsets` = per-string start bit offsets from `vector_of_record_handle_structures`; internal formula is `end = offsets[s+1]` for non-last strings and `total_bits` for last string; passing all **1200 handles** (k=0..1199) and `total_bits=555022` with raw CBUF `raw[9844:]` decodes all 1200 strings; confirmed 1200/1200 match G44.json |

**Degree 4 — Sources from Degree 3 authors' communities:**

| Source | What it gives |
|--------|---------------|
| `MS-PAGE-EXT` (Microsoft Page/Extent Architecture Guide) | **C2 LOB min/max**: confirms off-row LOB data is stored in `LOB_DATA` allocation unit and not compressed under PAGE/ROW compression; the min/max miss for `varchar(max)` columns is expected when values are stored off-row — mssqlbak reads the 16-byte LOB pointer instead of the actual value |
| Paul White `sql.kiwi` "Grouped Aggregate Pushdown" | Shows `DBCC CSINDEX` `Segment Attributes` including `BaseId`, `Magnitude`, `MinDataId`, `MaxDataId` — confirms these are the exact fields needed to compute `actual_val = base_id + stored_val × magnitude` for C1b |

**Open items with new source status:**

| Stream | Before sweep | After sweep |
|--------|-------------|-------------|
| **C1b** FOR min/max | `[EMPIRICAL]` | `STAIR4` + Paul White confirm formula `actual = base_id + stored × magnitude`; path to fix is clear |
| **C1a** small-segment null | no sources | `STAIR4` confirms `null_value` sentinel; `DARLING-RGE` confirms rowgroup-elimination NULL flag; `N32` confirms small rowgroups have same metadata structure |
| **C2** LOB min/max | no sources | `MS-PAGE-EXT` confirms off-row LOB → 16-byte pointer, no compression; C2 failure is expected behavior reading the pointer not the value |
| **D1** ghost record min/max | ghost anatomy only | No new source found mapping ghost-record bit to min/max aggregation specifically; remains empirical |
| **D2** temporal UPDATE | period column docs | No new source found; path still: identify which 1/8 check fails, then verify DATETIME2 decode |
| **B** enc=5 ARCHIVE null | Paul White 32,768 boundary | No change — 32,768-row null-bitmap sub-block structure has no open publication |
| ~~**G44** XMHUFFMAN page~~ | ~~page header unknown~~ | ✅ **Resolved (b8993f1)**: `_decode_v4_huff_dict` calls `xmhuffman.decode_page` with raw CBUF; 1200/1200 strings confirmed |

Outcome: 10 new source tokens added to the link map. C1b, C1a, C2, and G44 XMHUFFMAN paths all upgraded with new external corroboration. G44 subsequently implemented (b8993f1). D1, D2, and B remain empirical.

### CMU SQL Server papers sweep — new papers + 4-degree search (2026-06-17)

**Starting point:** `https://15721.courses.cs.cmu.edu/spring2016/papers/p1177-larson.pdf` (L11)
became directly downloadable (previously inaccessible). Swept the CMU 15-721 spring 2016
papers directory and other CMU course years for additional SQL Server papers not yet in this
document, then traced 4 hops of the citation/author graph from those papers.

#### New CMU SQL Server papers found (not previously in source map)

| Token | Paper | CMU URL | Relevance to mssqlbak |
|-------|-------|---------|----------------------|
| `FREED14` | Freedman, Ismert, Larson — "Compilation in the Microsoft SQL Server Hekaton Engine", IEEE Data Eng. Bull. 2014 | [freedman-ieee2014.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/freedman-ieee2014.pdf) | §12.2 V04: confirms Hekaton latch-free hash+range indexes, no buffer pool, log+checkpoint durability, full table rebuild from checkpoint at recovery |
| `HKCC12` | Larson, Blanas, Diaconu, Freedman, Patel, Zwilling — "High-Performance Concurrency Control for Main-Memory Databases", VLDB 2012 | [p298-larson.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/p298-larson.pdf) | §12.2 V04 background: version timestamp (begin/end fields per row version), latch-free hash index chain structure — does not document backup byte layout |
| `L13-CMU` | Larson et al. SIGMOD 2013 clustered CCI paper | [larson-sigmod2013.pdf](https://15721.courses.cs.cmu.edu/spring2016/papers/larson-sigmod2013.pdf) | §7.4 archival compression: confirms ARCHIVE layer wraps xVelocity segments; delta store trickle load and tuple mover described; delete bitmap described as "B-tree of (row_group_id, row_number)" pairs |

Also confirmed: L13 already in DOI source map; `L13-CMU` adds a free-access mirror.

#### 4-degree search from CMU SQL Server papers

**Degree 0 (CMU starting papers):** L11, L13, FREED14, HKCC12

**Degree 1 — directly cited by or co-authored with Degree 0:**

| Source | New to map? | What it gives for mssqlbak |
|--------|-------------|----------------------------|
| `ABADI08` — Abadi, Madden, Hachem, "Column-Stores vs. Row-Stores: How Different Are They Really?", SIGMOD 2008 ([p967-abadi.pdf at CMU](https://15721.courses.cs.cmu.edu/spring2016/papers/p967-abadi.pdf)) | Yes (distinct from 2013 survey already in map) | Late vs. early materialization in column stores; confirms column-store values are decoded individually per column scan — background for enc=5 Format A-D isolation, but no SQL Server-specific byte layout |
| `ABADI06` — Abadi, Madden, Ferreira, "Integrating Compression and Execution in Column-Oriented Database Systems", SIGMOD 2006 ([abadi-sigmod2006.pdf at CMU](https://15721.courses.cs.cmu.edu/spring2016/papers/abadi-sigmod2006.pdf)) | Already referenced in course; not in source map | Describes RLE, bit-packing, null-suppression, and lightweight compression operating directly on compressed data — matches exactly what L11 §2.2.3 describes for SQL Server CCI |
| `BWTREE13` — Levandoski, Lomet, Sengupta, "The Bw-Tree: A B-tree for New Hardware", ICDE 2013 ([levandoski-icde2013.pdf at CMU](https://15721.courses.cs.cmu.edu/spring2016/papers/levandoski-icde2013.pdf)) | Yes | Lock-free B-tree used by Hekaton range indexes (cited in FREED14); page-level delta chaining and flash storage — background for Hekaton index structure, does not document XTP backup format |
| `CSTORE05` — Stonebraker et al., "C-Store: A Column-oriented DBMS", VLDB 2005 | Yes (cited by L11 §6) | Foundational column-store paper establishing per-column segment storage model; L11 credits it as the revival of column-store interest; no SQL Server-specific content |
| H13 (already in map) | — | Already in source map |

**Degree 2 — cited by Degree 1 papers:**

| Source | New to map? | What it gives for mssqlbak |
|--------|-------------|----------------------------|
| `BONCZ05` — Boncz, Zukowski, Nes, "MonetDB/X100: Hyper-Pipelining Query Execution", CIDR 2005 (cited by L13-CMU and ABADI06) | Yes (Zukowski thesis Z09 already in map captures the key material) | Vector-at-a-time execution model; Vectorwise/MonetDB bit-packing primitive used by SQL Server batch mode; Z09 thesis (already in sources) is a superset for mssqlbak purposes |
| `HEMAN10` — Héman, Zukowski, Nes, Sidirourgos, Boncz, "Positional Update Handling in Column Stores", SIGMOD 2010 (cited by L13-CMU) | Yes | Positional Delta Trees (PDT) for column-store updates; SQL Server's delta store is the analogous structure — confirms SQL Server's choice to use a separate delta B-tree rather than in-place column mutation |
| `ABADI07` — Abadi, Myers, DeWitt, Madden, "Materialization Strategies in a Column-Oriented DBMS", ICDE 2007 (cited by L11 §6) | Yes | Late vs. early materialization tradeoffs; not SQL Server-specific, less directly useful than ABADI08 |

**Degree 3 — cited by Degree 2 papers:**

| Source | New to map? | What it gives for mssqlbak |
|--------|-------------|----------------------------|
| `MONET-CWI` — Boncz et al., early MonetDB papers (cited by BONCZ05) | No new value | MonetDB architectural papers; Z09 already covers the relevant compression material |
| `JOHNSON09` — Johnson, Pandis, Hardavellas, Ailamaki, Falsafi, "Shore-MT: A Scalable Storage Manager for the Multicore Era", EDBT 2009 (cited by FREED14 context) | Yes | Lock manager bottleneck paper that motivated Hekaton's latch-free design; explains why Hekaton dropped traditional lock tables — confirms §12.2 V04 narrative |
| `PADMANABHAN01` — Padmanabhan, Malkemus, Agarwal, Jhingran, "Block Oriented Processing of Relational Database Operations", ICDE 2001 (cited by L11 §3) | Yes | Earliest antecedent of SQL Server batch mode operators; block-at-a-time tuple processing on IBM DB2 — establishes the lineage but no SQL Server CCI-specific byte content |

**Degree 4 — cited by Degree 3 papers:**

| Source | New to map? | What it gives for mssqlbak |
|--------|-------------|----------------------------|
| `WILLHALM09` — Willhalm, Popovici, Bosché, Brobst, Ben-Yitzhak, Ritt, "SIMD-Scan: Ultra Fast In-Memory Table Scan Using On-Chip Vector Processing Units", VLDB 2009 (cited by BONCZ05 community) | Yes | SIMD-accelerated scan of bit-packed column data; confirms bit-packing is the standard primitive across systems, not SQL Server-specific; relevant background for enc=5 Format A-D integer packing |
| `ZUKOWSKI07` — Zukowski, Heman, Nes, Boncz, "Super-Scalar RAM-CPU Cache Compression", ICDE 2006 (cited by Z09 which is in sources) | No new value | Z09 thesis already in sources covers this paper's content |
| `FASTLANES23` — Afroozeh, Boncz, "The FastLanes Compression Layout: Decoding >100 Billion Integers/Second with Scalar Code", VLDB 2023 (CMU 2024 schedule) | Yes | Extends the bit-packing primitive (related to LB15 already in map) with unified 1024-value SIMD lane layout; not SQL Server-specific, but confirms the 64-bit bitpack-unit model is a community standard |

#### Outcome of CMU sweep

| Item | Before | After |
|------|--------|-------|
| `FREED14` Hekaton compilation | Not in map | Added — corroborates §12.2 V04 with Larson-authored paper on Hekaton durability model |
| `HKCC12` Hekaton MVCC | Not in map | Added — background corroboration for Hekaton row version structure |
| `L13` CMU mirror | DOI only | CMU PDF mirror added; confirmed accessible; clustered CCI ARCHIVE and delete bitmap detail noted |
| L11 CMU mirror | Listed but inaccessible | Confirmed accessible 2026-06-17 |
| enc=5 Format A-D | No change | D4 sources (`WILLHALM09`, `FASTLANES23`) confirm bit-packing is the community primitive but add no SQL Server-specific byte layout; remains `[EMPIRICAL]` |
| §12.2 V04 Hekaton/XTP | H13 + DMV docs | `FREED14` added as additional corroborator; no retag needed (already `[CORROBORATED]`) |
| D1 ghost min/max | No source | No new source found through 4 hops from CMU papers |
| D2 temporal UPDATE | No source | No new source found through 4 hops from CMU papers |

No new `BAK_FORMAT_SPEC.md` retags. 7 new source tokens added to the link map
(`FREED14`, `HKCC12`, `ABADI08`, `BWTREE13`, `CSTORE05`, `HEMAN10`, `WILLHALM09`).

### 4-degree sweep from backup chunk structure and stream-name sources (2026-06-18)

**Goal:** Find corroboration for §1.1 MTF layer and §1.2 MSSQLBAK container sections
by searching for SQL Server backup format publications without referencing any
specific patent document. Search traced 4 degrees of separation.

**Degree 0 — direct search terms (no patent):**
- "Microsoft On-disk Data Structures" (MODS) — no public copy found; internal Microsoft document only
- SFIN / MQDA / SFMB SQL Server backup structure — found via hex dumps

**Degree 1 — direct finds:**

| Source | What it gives |
|--------|---------------|
| `INSOMNIA-2008` (CVE-2008-0107) — Brett Moore, Insomnia Security | **Chunk dispatcher documented**: `struct backupChunk { unsigned long nametag; unsigned long size; }` — 4-byte nametag + 4-byte total-inclusive size; nametags SCIN, SFGI, MQCI named explicitly; size subtraction of 8 bytes confirmed in disassembly of `sqlservr.exe`. Published to `bugtraq`, `full-disclosure`, and `seclists.org` — multi-archive corroboration. |
| `IDEFENSE-2008` | Independent confirmation: "A 32-bit integer value, representing the size of a record, is taken from the file" — same chunk structure from a separate security firm. |
| `BERTRAND-XE` (Aaron Bertrand, sqlperformance.com, 2015) | SQL Server 2016 Extended Events API (`backup_restore_progress_trace`) exposes `MSDA` and `MSTL` as **official, queryable stream identifiers**. "BackupStream(0): Writing MSDA of size 10048 extents"; "BackupStream(0): Processing MSTL (FID=2, VLFID=101, size=65536 bytes)" — these are SQL Server's own public diagnostic names for the data and log streams. |
| `DORR-2008` (Bob Dorr, Microsoft PSS SQL Blog, 2008) | Trace flag 3004 restore-phase breakdown by a Microsoft Senior Escalation Engineer. Confirms restore phases: PreparingContainers → Transferring data → LogZero → Redo/Undo. |

**Degree 2 — one hop from degree-1 finds:**

| Source | What it gives |
|--------|---------------|
| `MS-BACKUPMEDIASET` (MS Learn) | **Normative source**: `backupmediaset.software_vendor_id` column documented as *"The value for Microsoft SQL Server is hexadecimal 0x1200"*; `MTF_major_version` column confirms per-backup MTF version tracking. |
| `MS-RESTORE-HEADERONLY` (MS Learn) | **Normative source**: `SoftwareVendorId` result column: *"For SQL Server, this number is 4608 (or hexadecimal `0x1200`)"* — the `Software Vendor ID` field (MTF_TAPE offset 86) is a queryable value in the public T-SQL API. |
| `SQLBEK-INSIDE` (Andy Yun, sqlbek.wordpress.com, 2022) | **Data equivalence demonstrated**: hex comparison (Beyond Compare) of MDF vs BAK shows the MSDA section is a byte-for-byte copy of data file pages (uncompressed, unencrypted). Attributed to Anthony Nocentino (Pure Storage) as the originator of the insight. Code and test database published at [github.com/SQLBek/PureStorage/tree/main/backup_test](https://github.com/SQLBek/PureStorage/tree/main/backup_test). |
| `SQLBEK-SERIES` (Andy Yun, sqlbek.wordpress.com, 2023) | Backup internals 5-part series covering reader/writer thread model, backup buffers, CPU threads, and compression. Part 4 links to `SQLBEK-INSIDE` for the byte-equivalence proof. |
| MSSQLTREK TF3014 (Sreekanth Bandarla, 2011) | `MSDA` stream name confirmed in SQL Server 2008 R2 error log: "BackupStream(0): Starting MSDA of size 384 extents". |

**Degree 3 — one hop from degree-2 finds:**

| Source | What it gives |
|--------|---------------|
| `SQLSRVFORENSICS` (aarsakian, GitHub) | Open-source Go forensics tool that parses BAK files as TAPE archives using a separate MTF library; extracts pages using raw page structure without relying on backup block format. Requires a custom [MTF_Reader](https://github.com/aarsakian/MTF_Reader) library written by the same author. |
| `MTF-RS` + `MDF-RS` (rroohhh, GitHub) | Rust MTF parser + MDF parser pair. `mtf-rs` provides `MTFPageProvider` that reads SQL Server backup pages directly from a BAK file and feeds them to `mdf-rs` for parsing — a working open-source implementation of BAK page extraction. |
| Mark S. Rasmussen "Reverse Engineering SQL Server Page Headers" (improve.dk) | Already in sources as `OrcaMDF`. The specific article provides a full byte-offset map of the 96-byte page header: `{HeaderVersion, Type, TypeFlagBits, Level, FlagBits, IndexID, PreviousPageID, …, PageID, FileID, …, Lsn1/Lsn2/Lsn3, …, GhostRecCnt, reserved[60-95]}`. Cross-checks pages found in MSDA stream. |

**Degree 4 — one hop from degree-3 finds:**

| Source | What it gives |
|--------|---------------|
| `UNRAVEL-BAK` (klandermans, GitHub) | Open-source BAK-to-SQLite converter. References `KyleBruene/mtf` (already in `MTF-H`) as its MTF implementation source. Documents that BAK files "are widely speculated to adhere to the Microsoft Tape Format (MTF)". |
| OSR/NTFSD "File Virtualization Methods" thread | Developer trying to build virtual restore: *"Once you understand the headers, the data-pages are dumps directly to the .bak file. Only used pages are dumped."*; *"there is some documentation about the binary layout of Data-Pages, but the binary encoding of the Transaction-Log is completely undocumented, and may (and has) changed between SQL-Server Versions"* — confirms the MSTL payload (log records) is a distinct problem from the MSDA payload (data pages). |

**Outcome:**

| Item | Before | After |
|------|--------|-------|
| §1.1 MTF layer | No Source Index row | **New row added** with 6 external sources; vendor ID `0x1200` is a normative Microsoft-documented value; chunk `{nametag,size}` layout is security-researcher-corroborated; `MSDA`/`MSTL` names are public Extended Events identifiers |
| §1.2 MSSQLBAK container | `[EMPIRICAL]` note only | No retag — inner compressed-record headers are not documented in any of these sources; remains `[EMPIRICAL]` for §1.2.1–§1.2.4 |
| "Microsoft On-disk Data Structures" (MODS) | Unknown | Confirmed not publicly available; remains an internal Microsoft document |

New tokens added to link maps: `INSOMNIA-2008`, `IDEFENSE-2008`, `BERTRAND-XE`, `DORR-2008`,
`SQLBEK-INSIDE`, `SQLBEK-SERIES`, `MS-BACKUPMEDIASET`, `MS-RESTORE-HEADERONLY`,
`SQLSRVFORENSICS`, `MTF-RS`, `MDF-RS`, `UNRAVEL-BAK`.

### XTP/Hekaton CFP backup mechanics and binary format sweep (2026-06-28)

**Starting points:** Two URLs provided by the user:
- `SQLPASSION-XTP` — Klaus Aschenbrenner, "Extreme Transaction Processing (XTP, Hekaton) – the solution to everything?" (2013)
- `SQLSHACK-INTRO` — Luan Moreno M. Maciel, "In-Memory OLTP Series – Introduction" (2015)

**Goal:** Find corroboration for §12.2 V04 XTP backup behavior, CFP binary layout,
and `/$HKv2` signature observed in empirical `.bak` analysis.

#### Direct findings from user-provided sources

| Source | What it gives |
|--------|---------------|
| `SQLPASSION-XTP` | XTP data lives entirely in a FILESTREAM filegroup; MVCC row model (immutable rows, UPDATE = DELETE + INSERT); hash and range indexes rebuilt from scratch at startup; recovery pipeline = load data/delta files → replay log tail. Directly corroborates why XTP blobs (not traditional MDF pages) appear in `.bak`. |
| `SQLSHACK-INTRO` | Data File = insert-version rows only; Delta File = deleted-row references; stored in MEMORY_OPTIMIZED_DATA filegroup; sequential I/O (append-only). Confirms the two-file CFP model and the separation of insert vs. delete tracking. |

#### Additional sources found (one hop)

| Source | What it gives |
|--------|---------------|
| `MS-BAK-MOT` (MS Learn) | Normative: CFP state → backup content table. **ACTIVE** and **WAITING_FOR_LOG_TRUNCATION**: full file metadata + all used data bytes backed up. **PRECREATED**, **UNDER_CONSTRUCTION**, **MERGE_TARGET**: file metadata only (no payload). Full backup = disk-based data + active log + CFPs. Differential: data files only if closed after last full; delta files always. |
| `MSBLOG-STORAGE` (Microsoft SQL Server Blog, 2014-01-16) | 128 MB default data file / 8 MB default delta file; up to 8192 CFPs per database; ACTIVE CFPs ≈ 2× in-memory footprint; merge fires when active rows fall below ~50% across two or more adjacent closed CFPs. |
| `MSBLOG-STATE` (Microsoft SQL Server Blog, 2014-01-23) | State transition walkthrough with live examples. UNDER_CONSTRUCTION → ACTIVE on a committed checkpoint; RTM allocation on ≤16 GB RAM machines is 16 MB data / 1 MB delta per CFP. |
| `SQLSHACK-CKPT` (SQLShack) | `.HKCKP` files physically reside in a `$HKv2` subfolder of the MEMORY_OPTIMIZED_DATA container. **Directly confirms** the `/$HKv2` UTF-16LE signature seen in the `.bak` stream. ROOT files contain system metadata. Recovery runs parallel per CFP thread; log tail replayed after data load. |
| `NEDOTTER-BAK` (Ned Otter, 2016) | Per-block CHECKSUM written at flush time and re-validated during backup — backup fails immediately on mismatch. FILESTREAM type `'S'` identifies the memory-optimized filegroup in the `.bak` (same code as Filestream/FileTable; no further differentiation). Restore streams CFP bytes into RAM; insufficient memory causes restore to fail after all disk files are created. |
| `SLIDESHARE-IMOLTP` (Microsoft CSS presentation) | **Critical binary format detail** (not found in any normative MS publication): checkpoint data files begin with a 4 KB file-header block containing the fixed string `"CKPT"` and a TYPE field. Subsequent blocks each carry a Block Header followed by Data Rows. ROOT and DELTA files use 4 KB fixed-size blocks. Data-row blocks are 256 KB. MVCC begin/end timestamps are embedded in each row for visibility. UPDATE is implemented as DELETE (old version) + INSERT (new version) — the row payload is immutable once written. |
| `SQLPASSION-PERF` | Offline Checkpoint Worker drains committed transactions from the XTP log stream into data/delta files. Only redo log records are written for XTP (no undo); rollback re-exposes the prior version already held in memory. |
| `SQLPASSION-TXNLOG` | `LOP_HK` is the log record type that bundles XTP row changes. Inspect with `sys.fn_dblog_xtp`. Only one log record per logical INSERT/UPDATE/DELETE regardless of index count (indexes are not logged). |

#### What this sweep confirmed vs. what remains unknown

| Claim | Status after sweep |
|-------|--------------------|
| `.bak` contains raw CFP bytes (not MDF pages) for XTP | `[CORROBORATED]` — MS docs + multiple blog sources |
| `/$HKv2` path signature in `.bak` stream | `[CORROBORATED]` — `SQLSHACK-CKPT` confirms `$HKv2` folder name |
| ACTIVE CFPs fully streamed; PRECREATED/MERGE_TARGET skipped | `[CONFIRMED]` — `MS-BAK-MOT` normative source |
| Per-block CHECKSUM validation during backup | `[CORROBORATED]` — `NEDOTTER-BAK` |
| `"CKPT"` magic in CFP file header, 4 KB header block | `[CORROBORATED]` — `SLIDESHARE-IMOLTP` (Microsoft CSS, not normative spec) |
| 4 KB block granularity for ROOT/DELTA files | `[CORROBORATED]` — `SLIDESHARE-IMOLTP` |
| 256 KB block size for data-row blocks | `[CORROBORATED]` — `SLIDESHARE-IMOLTP` |
| MVCC timestamps in each row | `[CORROBORATED]` — `SLIDESHARE-IMOLTP`; `HKCC12` (already in map) |
| Compact block format (`0d 00 01 00` header) | `[EMPIRICAL]` — no public source found |
| WAL-style block format (`50 00 03 00` header) | `[EMPIRICAL]` — no public source found |
| Row payload layout (fixed columns + 8-byte variable-length descriptors) | `[EMPIRICAL]` — no public source found |
| Object-ID-to-CFP mapping (which table owns which rows) | `[UNKNOWN]` — not documented in any public source found |

**Outcome:** §12.2 V04 Source Index row expanded with 8 additional sources.
No retag needed — §12.2 V04 was already `[CORROBORATED]`.
The four internal row-format items remain `[EMPIRICAL]` or `[UNKNOWN]`.

### XTP completeness signal + inline-vs-LARGE_DATA corroboration (2026-07-04)

**Context:** After landing a fourth AdventureWorks2016_EXT XTP table
(`SpecialOfferProduct_inmem`) via a new **seq-contiguity completeness gate** and
reverse-engineering the `Product_inmem` fixed/variable payload layout (see
`docs/notes/2026-07-03-adventureworks-xtp-investigation.md`, "Resolution 2"), the
user provided three sources to check the RE. Assessment:

| Source | Helpful? | What it corroborates (and what it does not) |
|--------|----------|---------------------------------------------|
| `MS-XTP-CFP` (`sys.dm_db_xtp_checkpoint_files`, already in map) | **Yes — most** | `logical_row_count` = *"For Data, number of rows inserted"*: an engine-tracked exact per-data-file insert count — independent support that the DATA-file content is a well-defined complete insert set, so for an insert-only table (empty DELTA) a full data-file scan is complete. Corroborates the **concept** behind our seq signal (`seq_max` == row count). Does **not** confirm the per-table dense `seq` 1..N encoding itself (still `[EMPIRICAL]`). `file_type_desc` = LARGE DATA is *"(n)varchar(max)/varbinary(max) + columnstore segments"* — corroborates why **bounded** `nchar`/`nvarchar` decode **inline** in the DATA-file row (our variable-section finding for `Product_inmem`); only `(max)` types leave the row for LARGE DATA files. |
| `RG-MOT` (Red-Gate, Miranda; **new**) | Partly | MVCC row header = Begin/End timestamps + StatementID + IndexLink Count then payload; UPDATE = INSERT + DELETE. Corroborates the framing header as MVCC timestamps (`seq`/`marker` ≈ begin/end) and insert-only `_inmem` copies. Conceptual, not byte-level; no fixed-column ordering / alignment / numeric-mantissa detail. |
| `SQLSHACK-MON` (SQLShack, Jayaram; **new**) | Marginal | Reiterates Data=inserts / Delta=deletes (already have `SQLSHACK-INTRO`); DMV/disk-monitoring focus, no layout detail. |

**Outcome:** No `BAK_FORMAT_SPEC.md` retag. Two new tokens added to the link map
(`RG-MOT`, `SQLSHACK-MON`). The seq-contiguity completeness signal and the XTP
fixed/variable payload layout (alignment-ordered fixed section; numeric stored as
an 8-aligned scaled-integer mantissa; fixed `char`/`nchar` stored in the variable
section) remain `[EMPIRICAL]` — corroborated in concept by `MS-XTP-CFP` and
`RG-MOT`, but no public source gives the byte layout.
