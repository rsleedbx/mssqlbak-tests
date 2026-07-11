# SQL Server BAK Format Spec — Master Index

_Reorganized from the monolithic `docs/BAK_FORMAT_SPEC.md`. Each StoragePath has its own file._

---

## StoragePath routing table

| StoragePath | Routing signal | Spec file |
|---|---|---|
| `ROWSTORE_HEAP` | `cmprlevel=0`, `index_id=0` (heap) | [02_ROWSTORE_HEAP.md](02_ROWSTORE_HEAP.md) |
| `ROWSTORE_BTREE` | `cmprlevel=0`, `index_id≥1` | [03_ROWSTORE_BTREE.md](03_ROWSTORE_BTREE.md) |
| `ROWSTORE_COMPRESSED` | `cmprlevel=1` (ROW) or `2` (PAGE) | [04_ROWSTORE_COMPRESSED.md](04_ROWSTORE_COMPRESSED.md) |
| `COLUMNSTORE_DELTA` | `__cs_delta_*` re-entry | [05_COLUMNSTORE_DELTA.md](05_COLUMNSTORE_DELTA.md) + [03](03_ROWSTORE_BTREE.md) for record format |
| `COLUMNSTORE_SEGMENT` | `cmprlevel=3`, enc=1/2/3/4 | [06_COLUMNSTORE_SEGMENT.md](06_COLUMNSTORE_SEGMENT.md) |
| `COLUMNSTORE_ARCHIVE` | `cmprlevel=4` or enc=5 XPRESS | [07_COLUMNSTORE_ARCHIVE.md](07_COLUMNSTORE_ARCHIVE.md) |
| `XTP_CHECKPOINT` | memory-optimized filegroup | [08_XTP_CHECKPOINT.md](08_XTP_CHECKPOINT.md) |
| All paths | container/transport layer | [01_CONTAINER.md](01_CONTAINER.md) |
| All paths | XPRESS codec | [01_XPRESS.md](01_XPRESS.md) |
| All paths | page anatomy | [01_PAGE.md](01_PAGE.md) |
| All paths | system catalog | [01_CATALOG.md](01_CATALOG.md) |
| All paths | type layouts + LOB | [01_TYPES_LOB.md](01_TYPES_LOB.md) |
| Log tail / dirty backup | fuzzy backup flag | [09_REDO_UNDO.md](09_REDO_UNDO.md) |

---

## SQL Server compression algorithms - overview

SQL Server does not route rowstore and columnstore data through a single generic
byte-stream compressor. Most storage paths use database-native encodings that
preserve table structure so the engine can read, compare, and reconstruct values
without inflating an entire logical table.

1. **Rowstore ROW/PAGE compression** (`ROWSTORE_COMPRESSED`,
   [04_ROWSTORE_COMPRESSED.md](04_ROWSTORE_COMPRESSED.md)). PAGE compression is
   a structure-aware rowstore pipeline. It begins with ROW compression, which
   rewrites fixed-width values (for example `int`, `datetime`, `char`) into
   compact variable-width representations. PAGE compression then adds
   page-local prefix compression, followed by a page-local dictionary that
   replaces repeated byte sequences inside the 8 KB page with short references.
   The implementation is in `rowcompress.py` (`_parse_cd`, `parse_page_ci`,
   `_CI_HAS_ANCHOR`, `_CI_HAS_DICT`).

2. **Columnstore xVelocity / VertiPaq compression** (`COLUMNSTORE_SEGMENT`,
   [06_COLUMNSTORE_SEGMENT.md](06_COLUMNSTORE_SEGMENT.md)). Columnstore stores
   values by column segment instead of by row. The segment reader handles
   dictionary/value encoding, biased integer encoding, RLE, bit-packing, and
   row-group ordering effects that improve compression for repeated values. The
   implementation lives in the `mssqlbak/columnstore/` package:
   `storage/segment_meta.py` (metadata offsets), `decode/bitpack.py`
   (bit-packing), `decode/value_for.py` (enc=1/2/4 value arithmetic),
   `decode/dict_numeric.py` / `decode/dict_string.py` /
   `decode/dict_xvelocity.py` (dictionary formats), and
   `assembly/reader.py` (row assembly).

3. **Columnstore ARCHIVE XPRESS** (`COLUMNSTORE_ARCHIVE`,
   [07_COLUMNSTORE_ARCHIVE.md](07_COLUMNSTORE_ARCHIVE.md)). ARCHIVE compression
   first applies the columnstore encodings above, then wraps segment and
   dictionary blobs in a 12-byte frame whose payload may be compressed with
   Microsoft XPRESS (MS-XCA LZ77+Huffman). This is the closest SQL Server storage
   path to a general-purpose byte-stream compressor, but it is applied after the
   columnar stream has already been normalized. The codec is documented in
   [01_XPRESS.md](01_XPRESS.md) and implemented by `xpress.py` plus
   `rust/src/xpress_lz77_*.rs`. The enc=5 raw formats (A/B/C/D) and the archive
   wrapper are in `mssqlbak/columnstore/decode/enc5_raw.py`.

4. **XTP / In-Memory OLTP checkpoint storage** (`XTP_CHECKPOINT`,
   [08_XTP_CHECKPOINT.md](08_XTP_CHECKPOINT.md)). XTP is not page compression and
   not columnstore compression. Durable memory-optimized rows are serialized into
   checkpoint DATA/DELTA files as log-style records, outside the ordinary 8 KB
   B-tree page stream. In a `WITH COMPRESSION` backup, those checkpoint file bytes
   are still carried by the MSSQLBAK container and therefore compressed by the
   outer XPRESS transport layer. The XTP scanner in `xtp.py` recovers the row
   records from the decompressed non-page stream and gates emission on dense
   identity or dense per-table `seq` completeness.

---

## Per-path file structure (all 7 StoragePath files follow this template)

1. **Routing trigger** — when is this path active, what catalog/page signal sets it
2. **Initialization** — what metadata is loaded before the first record
3. **Record structure** — page → slot → record byte layout
4. **Value decode rules** — per-type rules applied to each cell
5. **Diagnostic events** — what `record_event` calls are made and what context they carry
6. **Known heuristics** — where the path is uncertain; open empirical questions

---

## 0. How to read, verify, and maintain this spec

This is a **reverse-engineered** spec.  The implementation in `mssqlbak/` is
the primary source of truth; this file describes what that code assumes.  To
keep the spec and code aligned, every empirical claim is anchored:

1. **Traceability — cite the code.** Each table that documents an offset names
   the source constant or function (`module.py: CONSTANT`).  If you change a
   constant in the code, update the matching row here.  If a row has no source,
   it is suspect.
2. **Confidence tag.** Every section carries one of the four tags above.  A
   claim may only be promoted to `[CONFIRMED]` when (a) a committed fixture
   exercises it **and** (b) an independent verifier (below) agrees.
3. **Guess ID.** Every `[HEURISTIC]`/`[UNKNOWN]` item has a stable `Gnn` ID
   (§10).  The fixture plan and any new test reference that ID so the chain
   "guess → fixture → test → resolution" is auditable.

### Independent ground-truth verifiers

A reverse-engineered field is only *confirmed* when something outside this
codebase agrees with it.  Approved verifiers, in rough order of authority:

| Verifier | Confirms | How |
|--------|----------|-----|
| `DBCC PAGE (db, file, page, 3) WITH TABLERESULTS` | page header, slot array, record bytes, LOB pointers | trace flag 3604; compare field-by-field |
| `DBCC IND (db, table, -1)` | IAM/page-chain membership, page types | enumerate allocated pages |
| `sys.dm_db_database_page_allocations` | extent/page allocation per object | DMV; replaces `DBCC IND` on modern versions |
| `sys.column_store_segments` / `sys.column_store_dictionaries` | columnstore segment & dict metadata (enc type, min_data_id, magnitude, dict ids) | DMV row per segment |
| `sys.fn_dblog` / `sys.fn_dump_dblog` | log-tail record offsets & types | already used to derive `logtail.py` |
| `sys.dm_db_index_physical_stats`, `sys.partitions`, `sys.allocation_units` | rowset/partition/alloc-unit ids, compression level | catalog DMVs |
| OrcaMDF (`PageHeader`, system-table defs) | page header & base-table layouts | independent open-source reimplementation — **stale (~2013); supports `[CORROBORATED]`, not `[CONFIRMED]`** |

**Evidence ladder (three tiers):**
- `[CONFIRMED]` — fixture **+** a normative producer spec (MTF, MS-XCA, Microsoft
  Learn) **or** a live byte-level engine verifier (`DBCC PAGE`/`IND`/`CSINDEX`,
  system DMVs, `fn_dump_dblog`). The engine/spec is ground truth.
- `[CORROBORATED]` — fixture **+** external third-party evidence that is *not*
  normative or live-engine: practitioner blogs/papers (Paul White, Neugebauer,
  academic PDFs) or a reverse-engineered reimplementation. **OrcaMDF belongs here**
  (last updated ~2013 — useful corroboration, not authoritative ground truth).
- `[EMPIRICAL]` — fixture only; round-trips in our own parser with **no external
  corroboration**.

### Code-source map

Where each layer of this spec is implemented (and therefore where to verify
the offsets it documents):

| Spec section | Source module(s) | Key symbols |
|--------------|------------------|-------------|
| §1.1 MTF descriptors | `reader.py` | `_COMMON_HDR`, `_TAPE_*`, `_SSET_*`, `_parse_mtf_date`, `_MQCI_TAG`, `_MQCI_*_LSN_OFF` |
| §1.1 MTF page-image | `mtf.py` | `build_mtf_page_index`, `_scan_image_start`, `_walk_image_pages`, `_ReaderView` |
| §1.2 MSSQLBAK container | `compressed.py`, `xpress.py` | `_V1`, `_V2`, `_Layout`, `_kraft_complete`, `_decode_chunk` |
| §2 MDF page header / slots | `pages.py` | `_H_*`, `PageHeader.parse`, `Page` |
| §2.5 IAM bitmap | `rows.py` | `_IAM_BITMAP_OFFSET = 194`, `_IAM_SPA_OFFSET = 140`, `_IAM_SPA_SLOTS = 8` |
| §2.6 boot page | `catalog.py` | `_find_sysallocunits_first_page`, `_SYSALLOCUNITS_PTR_OFF = 516`, `_DBI_COLLATION_OFF = 392` |
| §3.1 FixedVar record | `records.py` | `decode_record`, `_HAS_VARCOLS`, `_COMPLEX_COL` |
| §3.4 CD record | `rowcompress.py` | `_parse_cd`, `_CD_*`, `_CLUSTER = 30`, `physical_columns`, `decode_compressed_value` |
| §3.5 Always Encrypted (AE) | `types.py`, `catalog.py` | `_decode_nchar`, `Column.is_encrypted`, `_is_ae_column`, `_AE_COLLATION_MAX = 0x4000` |
| §3.6 Page CI | `rowcompress.py` | `parse_page_ci`, `_CI_HAS_ANCHOR = 0x02`, `_CI_HAS_DICT = 0x04`, `_expand_prefix` |
| §4 system catalog | `catalog.py` | `_SYS*_COLS` (built by `_layout`), `_PARTITION_SHIFT`, `_record_columns` |
| §5 type layouts | `types.py` | `_DECODERS`, `_DT2_TIME_LEN`, `SUPPORTED_TYPE_IDS`, `SUPPORTED_UDT_TYPE_IDS` |
| §5.1 sql_variant | `types.py` | `_decode_sql_variant`, `_VARIANT_*`, `_VARIANT_BASE_TYPES` |
| §5.x json/vector | `types.py` | `decode_native_json`, `decode_vector`, `NATIVE_JSON = 244`, `NATIVE_VECTOR = 255` |
| §6 LOB / off-row | `rows.py`, `catalog.py` | `_BLOB_*`, `_RID`, `_stitch_lob`, `_read_lob_node`, `_read_lob_node_c` |
| §7 columnstore segment metadata | `columnstore/storage/segment_meta.py` | `_SEG_*`, `_DICT_*` |
| §7 columnstore LOB / preamble | `columnstore/storage/lob.py` | `_COLUMN_LOB_PREAMBLE`, `_COLUMN_LOB_CHUNK`, `_COLUMN_LOB_SEP`, `_deinterleave_column_lob`, `_unwrap_archive_blob` |
| §7 columnstore bitpack | `columnstore/decode/bitpack.py` | `_BP_BPV`, `_bitpack_values`, `_true_bp_start`, `_bp_for_base` |
| §7 columnstore value decode | `columnstore/decode/value_for.py` | `_decode_enc1`, `_apply_mag`, `_int_to_python`, `_enc4_null_sentinel` |
| §7 columnstore numeric dict | `columnstore/decode/dict_numeric.py` | `_parse_numeric_dict_int`, `_parse_numeric_dict_float`, `_decode_enc2_int_dict`, `_decode_enc2_float_dict` |
| §7 columnstore string dict | `columnstore/decode/dict_string.py` | `_parse_dict_strings`, `_parse_max_dict_entries`, `_combine_enc3_dicts`, `_decode_enc3` |
| §7 columnstore xVelocity dict | `columnstore/decode/dict_xvelocity.py` | `_V4_*`, `_V7_*`, `_decode_v4_huff_dict`, `_split_v4_record`, `_build_huff_table`, `_huff_decode_page_py` |
| §7 columnstore archive enc=5 | `columnstore/decode/enc5_raw.py` | `_ENC5_*`, `_decode_enc5`, `_multichunk_xpress_header`, `_ARCHIVE_*` |
| §7 columnstore assembly | `columnstore/assembly/reader.py` | `read_columnstore_rows`, `read_columnstore_batches`, `_load_one_string_dict`, `_active_columnstore_group_keys` |
| §7 columnstore delta | `columnstore/assembly/delta.py` | `_read_columnstore_delta_rows` |
| §8 XPRESS | `xpress.py`, `rust/src/xpress_lz77_*.rs` | `decompress`, `_BitStream`, `_build_decode_table`, `_decompress_python` |
| §9 log tail | `logtail.py` | `LOP_*`, `find_log_range`, `iter_log_records`, `collect_redo_patches`, `_log_block_sector_byte` |
| §10 XTP checkpoint | `xtp.py`, `compressed.py` | `scan_cfp_log_records`, `decode_cfp_log_records`, `_seq_complete_rows`, `_CKPT_PREAMBLE_SIG`, `_decode_chunk` |
| §11 Layout register | `catalog.py`, `rows.py` | `_record_columns`, `leaf_offset`, `null_bit` |
| §12 Version evolution | `compressed.py`, `columnstore/` package, `rows.py`, `catalog.py` | version-boundary handling per `Vnn` ID |

### Coverage model

Five orthogonal axes govern what the spec and fixtures must exercise:

1. **Byte layout** (Guess Register §10, IDs `G01`–`G52`): what do raw bytes at a
   known offset mean?  Resolved by surgical fixtures + `DBCC PAGE` / DMV verifiers.
2. **Record topology** (Layout Register §11, IDs `L01`–`L05`): where columns sit
   in a multi-column row — PK position, column count, fixed vs variable ordering.
   Drives `leaf_offset`, null-bitmap size, and var-offset array indexing in
   `catalog.py` / `rows.py`.
3. **Feature paths** ([GAP_ANALYSIS.md](GAP_ANALYSIS.md)): compression level,
   columnstore, dirty log replay, multi-file — *which decoder path* runs, not the
   per-field byte offsets.
4. **Version evolution** (Version Register §12, IDs `V01`–`V11`): where the
   on-disk format changed between SQL Server versions.  Each entry documents the
   boundary version, what the parser currently handles, and the action required
   to cover the older format.  This axis is the proactive complement to
   FIXTURE_GAPS.md: it records what we know (or suspect) about version
   differences *before* a real .bak file exposes the bug.
5. **Value coverage** (Value Coverage Register §13, IDs `VC01`–`VCnn`): for every
   field with N documented values {v₁, …, vₙ}, is each vᵢ present in at least one
   committed fixture?  A field can be fully `[CONFIRMED]` for byte layout yet still
   have a value blind spot if only one of its documented values has ever been
   exercised.  This axis catches those gaps.

Fixture tiers (see [BAK_SPEC_FIXTURES.md](BAK_SPEC_FIXTURES.md)):

| Tier | Goal | Examples |
|------|------|----------|
| 1 | Resolve `Gnn` guesses | `iam_offset_verify.bak`, `cs_enc5_*.bak` |
| 2 | Exercise `Lnn` layout | `layoutcoverage_full.bak` |
| 3 | Feature isolation | `typecoverage`, `compressioncoverage`, `dirtycoverage_*` |
| 4 | Parser hardening | property/fuzz tests on committed fixture bytes |

---

## 10. Summary: Confirmed vs Guessed

### What is fully confirmed (public spec + fixture)

- MTF common block header, TAPE block, SSET block, packed date format
- MDF page header (96 bytes, all offsets)
- Slot array layout
- FixedVar record format (status bytes, fixed/var split, null bitmap, var
  offset array, complex-column flag)
- All SQL type on-disk layouts (verified against full type-matrix fixture)
- `money` byte order (plain LE int64, not "high dword first")
- XPRESS (MS-XCA LZ77+Huffman) compression format

### What is empirically reverse-engineered (fixture only)

- MSSQLBAK container v1/v2 record-header geometry
- MTF block-size detection heuristics
- SQL Server config stream in SSET (only paths are reliable)
- Server-name extraction heuristic (SFGI marker)
- System catalog object IDs and field offsets
- Partition rowset ID seed (`object_id << 16`)
- IAM bitmap offset (194)
- Boot-page pointer scan
- CD record format (ROW/PAGE compression)
- Page CI (page compression info) structure — byte 96 flags 0x02 (anchor) / 0x06 (anchor+dict) on PAGE-compressed pages (G1A)
- BLOB inline root layout (link-count derivation)
- LOB page header — btyp=2/3/5 layouts confirmed (G31)
- Legacy text pointer structure — bytes 0–3 timestamp, 8–15 RID (G32)
- Columnstore segment/dictionary metadata offsets
- Columnstore bit-packing and value arithmetic
- Log tail framing (APAD/MSLS markers, 4096-byte block structure, sector-status bytes)
- Log record field offsets (LCX, SUBTYPE, xact_id, page_id, slot_id, prev_blk_off)
- INSERT, DELETE, and MODIFY record payload layouts (row_len, row bytes, undo/redo patches)
- Transaction analysis: in-window and long-running uncommitted detection
- Columnstore archival (XPRESS-compressed segments)
- Columnstore LOB preamble (12-byte header + 8-byte separators, G41)
- Ghost record identification (status_B bit 0, G15)
- Forwarding stub layout — 9-byte RID pointer (G16)
- Log-tail markers: `APAD` and `MSLS` confirmed present (G50)

### What is guessed — the Guess Register

Stable IDs; the fixture plan (`BAK_SPEC_FIXTURES.md`) and any new test reference
these.  "Risk" = consequence if the guess is wrong (S=silent wrong data,
M=table skipped, L=metadata only).

| ID | Guess | Spec § | Risk | Status | Fixtures |
|----|-------|--------|------|--------|----------|
| G01 | MSSQLBAK `tag` bits 0..15 meaning | 1.2.2 | L | open | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| G02 | MSSQLBAK v2 16-byte field at +8 (hash? pointer?) | 1.2.2 | L | open | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| G03 | MSSQLBAK v2 `prev_uncompressed_size` at +0 | 1.2.2 | L | open | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| G04 | MSSQLBAK version word 2 (bytes 12:16) | 1.2.1 | L | open | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| ~~G05~~ | ~~Always TAPE+SSET chunks before first data page~~ | 1.2.4 | M | **CONFIRMED** — TAPE(→SFMB)→SSET in all SS2017–SS2025 fixtures; SFMB is a legal soft-filemark between the two descriptors | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| ~~G10~~ | ~~Block-size detection probe order~~ | 1.1 | M | **CONFIRMED** — TAPE `format_logical_block_size` (offset 84) is internal logical-block size, NOT physical block size; empirical probe is the only correct method. `G10.json` | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| G11 | SSET server-name extraction (SFGI marker) | 1.1.5 | L | heuristic — confirmed working on all tested backups; see §1.1.5 | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| G12 | Config-stream database-name fallback | 1.1.5 | L | heuristic — confirmed working on all tested backups; see §1.1.5 | [container](BAK_SPEC_FIXTURES.md#container-and-metadata) |
| ~~G13~~ | ~~IAM bitmap offset = 194~~ | 2.5 | M | **CONFIRMED** — DBCC PAGE verifier; `G13.json` | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G14~~ | ~~Boot-page `sysallocunits` pointer (scan, ~offset 516)~~ | 2.6 | M | **CONFIRMED** — fixed offset 516 confirmed SS2017–SS2025 across all fixture types; `G14.json` | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G15~~ | ~~`status_B` bit meanings beyond `0x01`~~ | 3.2 | S | **EMPIRICAL** — bit 0=ghost-forwarded only; bits 1–7 never non-zero in any fixture | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G16~~ | ~~Forwarded-heap 9-byte stub layout~~ | 3.3 | M | **EMPIRICAL** — `status_A(u8) + page_id(u32 LE) + file_id(u16 LE) + slot(u16 LE)`; confirmed `dirtycoverage_heap_forward.bak` (SS2022) | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G17~~ | ~~CD long-data region flag byte~~ | 3.4 | M | **EMPIRICAL** — `cmp_row_wide`/`cmp_page_wide` (40 cols, 50 rows) decode correctly; no counter-example observed | [row/page](BAK_SPEC_FIXTURES.md#rowpage-compression) |
| ~~G18~~ | ~~CD long-data per-cluster count bytes~~ | 3.4 | M | **EMPIRICAL** — same as G17; cluster-count bytes navigated successfully | [row/page](BAK_SPEC_FIXTURES.md#rowpage-compression) |
| ~~G19~~ | ~~`smalldatetime` under ROW/PAGE (float-path assumption)~~ | 3.4 | S | **EMPIRICAL** — `spec_probe rowcompress` match; `compressioncoverage_full.bak` | [row/page](BAK_SPEC_FIXTURES.md#rowpage-compression) |
| ~~G1A~~ | ~~Page CI flags byte `0x02`/`0x06`~~ | 3.6 | M | **CORROBORATED** — byte 96 is a flags byte: `0x02`=anchor only, `0x06`=anchor+dictionary; `0x06` confirmed on `compressioncoverage_full.bak`, `0x02` cross-checked against `DBCC PAGE` on `pagecomp_anchor_full.bak`; absent on ROW-compressed | [row/page](BAK_SPEC_FIXTURES.md#rowpage-compression) |
| ~~G20~~ | ~~`sysrowsets.cmprlevel` at offset 39~~ | 4.3 | M | **CONFIRMED** — DBCC PAGE `Slot 0 Column 9 Offset 0x27`; `G20.json` | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G21~~ | ~~Base-table object IDs stable across versions~~ | 4.2 | M | **EMPIRICAL** — 50 real-world samples from SQL Server 2006 through 2025 all decode correctly using the same object IDs; no version-specific variation observed | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G22~~ | ~~Partition rowset id seed `object_id << 16`~~ | 4.4 | M | **CONFIRMED** — `sys.allocation_units` verifier; `G22.json` | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G30~~ | ~~In-row inline-root `nlinks = (len-12)//12`; header [+2:+12]~~ | 6.1 | S | **EMPIRICAL** — `test_lob_links.py` passes; `lob_links_fixture.bak` | [LOB](BAK_SPEC_FIXTURES.md#lob-and-off-row-storage) |
| ~~G31~~ | ~~On-page LOB record header [+0:+12]; LARGE_ROOT links~~ | 6.2 | S | **EMPIRICAL** — btyp=2 (LARGE_ROOT) and btyp=5 (ROOT) layouts confirmed; `cs_lob_preamble2.bak` (SS2022); multi-level LOB chain traces correctly | [LOB](BAK_SPEC_FIXTURES.md#lob-and-off-row-storage) |
| ~~G32~~ | ~~Legacy text-pointer bytes 0–7~~ | 6.3 | L | **EMPIRICAL** — bytes 0–3=timestamp u32; bytes 4–7=zero padding; bytes 8–15=RID; confirmed `legacytext.bak` + DBCC PAGE (SS2022) | [LOB](BAK_SPEC_FIXTURES.md#lob-and-off-row-storage) |
| ~~G40~~ | ~~Columnstore dict-id field ordering (names swapped)~~ | 7.1 | S | **CONFIRMED** — offset 52 = `primary_dictionary_id`, offset 56 = `secondary_dictionary_id`; `spec_probe columnstore-dict-order` match vs `G40.json` verifier output | [columnstore](BAK_SPEC_FIXTURES.md#columnstore) |
| ~~G41~~ | ~~Columnstore LOB preamble (12) + separator (65 536)~~ | 7.5 | S | **EMPIRICAL** — 12-byte preamble + 8-byte separators confirmed; `cs_lob_preamble2.bak` 1200-row fixture; deinterleave round-trip validates all 1200 strings | [columnstore](BAK_SPEC_FIXTURES.md#columnstore) |
| ~~G42~~ | ~~Columnstore enc=5 header / sentinel / scale-7~~ | 7.7 | S | **EMPIRICAL** — `spec_probe columnstore` match; enc=5 tables decoded in `compressioncoverage_full.bak` | [columnstore](BAK_SPEC_FIXTURES.md#columnstore) |
| ~~G43~~ | ~~Columnstore segment blob header [+0:+33]~~ | 7.3 | M | **EMPIRICAL** — bpv at offset 34, nw at offset 36 confirmed; 24 segments validate with `spec_probe columnstore-seg-header` | [columnstore](BAK_SPEC_FIXTURES.md#columnstore) |
| ~~G44~~ | ~~Columnstore binary dictionary format (dict blob > 65536 B)~~ | 7.6 | S | **CONFIRMED** — xVelocity v4 hash dictionary + version-7 sorted pool; full 1200-string decode via `xmhuffman`; bookmark fallback covers ≥194 slots; `G44.json` verifier sidecar | [columnstore](BAK_SPEC_FIXTURES.md#columnstore) |
| ~~G50~~ | ~~Log-tail `APAD`/`MSLS` framing and 4096-byte block structure~~ | 9.1 | M | **EMPIRICAL** — APAD/MSLS discovery, opening/continuation blocks, 72-byte header layout, sector-status bytes, and record field offsets fully documented in §9.1.1–9.1.4 | [log tail](BAK_SPEC_FIXTURES.md#log-tail) |
| ~~G51~~ | ~~Log-tail block type byte and cross-block payload reading~~ | 9.1 | S | **EMPIRICAL** — `0x50`=opening / `0x40`=continuation; `_read_log_payload` sector-status handling; record-header straddle at positions 4072/4080/4088; documented §9.1.2, §9.1.8 | [log tail](BAK_SPEC_FIXTURES.md#log-tail) |
| ~~G52~~ | ~~`LOP_ABORT_XACT` presence and all LOP discriminant values~~ | 9.1 | M | **EMPIRICAL** — all six operation codes (INSERT/DELETE/MODIFY×2/BEGIN/COMMIT/ABORT) and their SUBTYPE+discriminant combos documented §9.1.4; abort confirmed `dirtycoverage_aborted_xact.bak` | [log tail](BAK_SPEC_FIXTURES.md#log-tail) |
| ~~G55~~ | ~~`syscolpars.collationid` LCID bit layout for code-page detection~~ | 3.6 | S | **EMPIRICAL** — SORTID (bits 0–7) maps directly to code page; 13 collations verified via `unicode_codepage_coverage.bak` | [unicode-codepage](BAK_SPEC_FIXTURES.md#5--g55-collation_id-lcid-bit-layout-unicode_codepage_coveragebak) |
| ~~G56~~ | ~~Inline MAX-type value `0x21` type-marker byte~~ | 3.1 | S | **EMPIRICAL** — stripped for varchar/varbinary(max); nvarchar(max) even-length guard preserves genuine U+0421/U+7121 first bytes; `nvarchar_max_u21_full.bak`; census tag `u21:*` | [types](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |
| ~~G57~~ | ~~Boot-page `DBINFO.dbi_collation` (database-default collation id) offset~~ | 2.6 | S | **CONFIRMED** — uint32 LE at byte offset 392 of boot-page 9 record 0; all four container defaults (SS2017–SS2025, `SQL_Latin1_General_CP1_CI_AS`) store `0x3400D008` matching `COLLATIONPROPERTY(...,'CollationID')`; a `COLLATE Greek_CI_AS` database stores `0x0000D007` there, so the field tracks the actual DB collation; string columns whose own `collationid` is 0 inherit it | [pages/catalog](BAK_SPEC_FIXTURES.md#pages-records-and-catalog) |

### What is still not decoded at all `[UNKNOWN]`

- MSSQLBAK v2 16-byte field (G02) and version word 2 (G04)

### What is decoded but field semantics remain partially unknown

- Columnstore segment blob preamble bytes 0–33 (G43) — offsets through `nw`@36 and the FOR table@48 are confirmed and used; a few observed u32/u16 fields lack confirmed names

### What is resolved since last update

Confirmed by DBCC PAGE verifiers, committed regression tests, and empirical
byte inspection in this session.  Most recently: complete log tail format
documented in §9.1 (G50–G52 fully resolved):

| ID | Resolution | Verifier | Test |
|----|------------|--------|------|
| G13 | IAM bitmap starts at byte 194 | `DBCC PAGE(CatalogSS2022,1,239,3)` → Extent Alloc Status at 0xC2=194 | `test_spec_probe.py` |
| G15 | `status_B` bit 0=ghost-forwarded; bits 1–7 never non-zero | Survey of all fixture records; no non-zero upper bits observed | — |
| G16 | Forwarding stub: `status_A(u8) + page_id(u32 LE) + file_id(u16 LE) + slot(u16 LE)` | Byte inspection `dirtycoverage_heap_forward.bak`; 9-byte stub layout confirmed | — |
| G17 | CD long-data region navigated correctly for 40-column tables | `cmp_row_wide`/`cmp_page_wide` round-trip match | `test_rowcompress.py::test_wide_table_*` |
| G18 | CD cluster-count bytes correctly traversed | same as G17 | same |
| G19 | `smalldatetime` decoded via uint16+uint16 (float path absent) | `spec_probe rowcompress` → match | `test_spec_probe.py` |
| G1A | Page CI: byte 96 flags `0x02` (anchor) / `0x06` (anchor+dict); absent in ROW-compressed pages | Byte inspection `compressioncoverage_full.bak` (0x06); `DBCC PAGE` cross-check on `pagecomp_anchor_full.bak` (0x02) | — |
| G20 | `sysrowsets.cmprlevel` at record offset 39 | `DBCC PAGE(TypeCoverage,1,17,3)` → Column 9 at 0x27=39 | — |
| G22 | System table rowsetid = `object_id << 16` | `sys.allocation_units` container_id matches formula for obj 3,5,7,8 | — |
| G30 | Inline-root LOB `nlinks = (blob_len-12)//12` | `typecoverage_full.bak` read + `test_lob_links.py` assertions | `test_lob_links.py` |
| G31 | btyp=2 (LARGE_ROOT): 16-byte link entries (cumul_end u64, page_id u32, file_id u16, slot u16); btyp=5 (ROOT): 12-byte fragment entries | Multi-level LOB chain trace in `cs_lob_preamble2.bak`; all fragments recovered | — |
| G32 | Legacy text pointer: bytes 0–3=timestamp u32, 4–7=zero, 8–15=RID | DBCC PAGE (style=3) on `legacytext.bak` data page; pointer bytes match LOB root RID | — |
| G40 | offset 52 = `primary_dictionary_id`; offset 56 = `secondary_dictionary_id` | `sys.column_store_segments` on BoundaryCoverage (SS2022) → `G40.json` | `spec_probe columnstore-dict-order` → match |
| G41 | Columnstore LOB preamble: 12-byte header + 8-byte separators every 65 536 bytes | `cs_lob_preamble2.bak` 1200-row fixture; deinterleave round-trip validates all 1200 strings | — |
| G42 | Columnstore enc=5 tables decoded end-to-end | `spec_probe columnstore` → 2 CCI tables in `compressioncoverage_full.bak` | `test_robustness.py` |
| G43 | bpv at offset 34 (u16), nw at offset 36 (u32); preamble bytes 0–33 opaque | `spec_probe columnstore-seg-header` → match; 24 segments validated | `spec_probe columnstore-seg-header` |
| G50 | Log-tail region: APAD/MSLS discovery algorithm; 4096-byte opening blocks with 72-byte header (VLF seq at +0x0C, block offset at +0x10); sector-status byte 0x40 at every 512-byte boundary; record field offsets (LCX=0x0E, SUBTYPE=0x0F, xact_id=0x10–0x15, page_id=0x18, file_id=0x1C, slot_id=0x1E) | Raw scan + `sys.fn_dump_dblog` on `dirtycoverage_uncommitted.bak`; `logtail.py` field constants validated | `test_dirty_backup.py`, `test_logtail.py` |
| G51 | Block types: 0x50=opening (records at +0x48), 0x40=continuation (records at +0x00); `_read_log_payload` skips status byte 0x00 sub; record-header straddle detection at positions 4072/4080/4088 using 64-byte stitched buffer | `dirtycoverage_wide.bak` MODIFY record spanning block boundary; all before-image column values restored | `test_dirty_backup.py` |
| G52 | All six LOP codes with SUBTYPE+discriminant: INSERT(0x04,0x02), DELETE(0x04,0x03), MODIFY_LOB(0x04,0x04), BEGIN(0x00,0x80), COMMIT(0x00,0x81), ABORT(0x00,0x82); INSERT/DELETE/MODIFY payload layouts fully documented | `dirtycoverage_aborted_xact.bak`; `sys.fn_dump_dblog` confirms all field offsets | `test_spec_probe.py`, `test_dirty_backup.py` |
| G21 | System catalog base-table object IDs stable across SQL Server versions | 50 real-world samples from SQL Server 2006–2025 all decode with the same object IDs; no version-specific variation observed | — |
| G53 | Always Encrypted (AE) nvarchar/nchar columns store AEAD ciphertext (version byte `0x01`, 32B auth-tag, 16B IV, N×16B ciphertext; always odd total length).  BIN2 collation (`collation_id` in `[1, 0x4000)` — `_AE_COLLATION_MAX = 0x4000`, `catalog.py:96`) detected at catalog level; odd byte-length at decode level.  Parser returns `None` for all AE column values. | `AdventureWorks2016_EXT.bak` `CustomerPII.SSN` (81B, odd, first byte `0x01`); 18 966 rows extracted with `SSN=None` | — |
| G54 | cp1252 defines only 251 of 256 byte values; bytes 0x81/0x8D/0x8F/0x90/0x9D are undefined.  Some databases store data in a non-cp1252 code page (cp1251 Cyrillic, cp932 Japanese, raw UTF-8) in a varchar column collated as cp1252.  Observed: `dba.stackexchange.com.bak` `PostHistory.Text`, byte 0x8F at position 1191.  Parser retries decode with `errors='replace'`, substituting U+FFFD for each undecodable byte; row is extracted rather than skipped. | `dba.stackexchange.com.bak` `PostHistory` — `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f` before fix; table extracted after fix | — |
| G55 | `syscolpars.collationid` SORTID bit layout.  **Closed.**  Bits 0–7 are the SQL Server Sort Order ID (SORTID); bits 8–15 are sensitivity flags (`0xD0` = CI+AS); bits 16–31 are extra flags (non-zero only on the database-default collation row, e.g. `0x3400` on Latin1_General_CI_AS).  SORTID maps directly to a Windows code page: 0x01→cp1256, 0x03→cp950, 0x07→cp1253, 0x08→cp1252, 0x0C→cp1255, 0x10→cp932, 0x11→cp949, 0x13→cp1250, 0x15→cp1251, 0x19→cp874, 0x1A→cp1254, 0x1F→cp1257, 0x20→cp1258, 0x24→cp936.  All 13 non-cp1252 code pages verified via `unicode_codepage_coverage.bak`. | `unicode_codepage_coverage.bak` probe output + `TestCodecForCollation` (53 tests pass) | `tests/test_unicode_decode.py::TestCodecForCollation` |
| G57 | Boot-page `DBINFO.dbi_collation`: the database-default collation id is a uint32 LE at byte offset 392 of boot-page 9 record 0 (same bit layout as G55).  String columns whose own `syscolpars.collationid` is 0 inherit it (`catalog.recover_schema`); `confidence.py` reports it. | Live-engine verifier: SS2017/2019/2022/2025 default `SQL_Latin1_General_CP1_CI_AS` → `0x3400D008` at offset 392, equal to `COLLATIONPROPERTY(SERVERPROPERTY('Collation'),'CollationID')`; a `COLLATE Greek_CI_AS` database → `0x0000D007` (field tracks the DB collation, not a constant) | `tests/test_dbi_collation.py` (incl. `@pytest.mark.engine` verifier) |
| Stripe | `MSSQLBAK` striped backup: each stripe is an independent compressed container; pages are partitioned (no overlap except file-header); merge = union of both page sets | hex-probe of 2-file stripe; `from_stripe` decodes all 20 rows matching single-file baseline | `test_striped_backup.py` (6 tests) |
| §7.4 (archive blob) | Archive segment/dict blobs wrapped in 12-byte frame `[flags u32][unc_size u32][cmp_size u32]`; payload XPRESS-LZ77 when sizes differ | Byte inspection of `compressioncoverage_full.bak` archive CCI blobs; `_unwrap_archive_blob` decodes correctly | `test_robustness.py::test_columnstore_archive_decodes` |
| §7.4 (compact null) | Nullable enc=1 columns in archive row groups use compact mode: `nw×vpw < n_rows` → first `n_null` rows are implied NULL | Byte inspection: nw=429, vpw=2 → 858 < 1000 for `amount` column; sentinel at `bp_off−16` confirms n_non_null | `test_robustness.py::test_columnstore_archive_decodes` |
| §7.4 (catalog) | `cmprlevel=4` wins over `cmprlevel=3` when two `idminor=1` sysrowsets entries exist for same object after `COLUMNSTORE_ARCHIVE` rebuild | `sysrowsets` raw byte dump confirms both entries present; `max(cmprlevel)` fix in `catalog.py` | `test_robustness.py::test_columnstore_archive_decodes` |
| §7.2 (varchar dict) | VARCHAR/CHAR dictionary blobs must be parsed as cp1252, not UTF-16LE; the UTF-16LE check falsely matches even-length ASCII strings | Byte comparison: `val1` = `76 61 6C 31` → falsely decodes as `慶ㅬ` in UTF-16LE | `test_robustness.py` (cmp_columnstore name column) |
| §7.6 (nchar dict) | nchar/nvarchar dictionary blobs may contain sort keys rather than literal UTF-16LE strings; out-of-range dictionary indices are non-null (`empty_val`) | `compressioncoverage_full.bak` `cs_1000.ncf`/`cs_10000.ncf`: null count matched expected after fix | `test_stats.py` |
| §7.7 (enc=5 formats A-D) | Four enc=5 formats: A (h92=item_size, values from offset 98); B (sentinel + descending index); C (h92=0, h38=n_rows, XPRESS + per-row u16 index, `0xFFFE`=null); D (h92=0, h38<n_rows, XPRESS dedup + n_non_null u16 index, self-ref scan at `d[n_dedup*sz]==(n_dedup-1)*sz`) | `compressioncoverage_full.bak` enc=5 segments all correct null counts; 64 test_stats.py cases pass | `test_stats.py` |
| §7.7 (enc=5 sentinel FP) | When h92=0, `\xfe\xff` within the XPRESS payload is a false-positive sentinel; h92=0 overrides the sentinel scan | `cmp_columnstore_archive.dto`: blob[-2:]=`\xfe\xff` inside XPRESS payload; Format B path gave 1000 nulls instead of 142 | `test_stats.py` |
| §7.7 (enc=5 varchar stored width) | For varchar/char, `blob[82]` (u16 LE) holds the actual per-row item width; may be less than `max_length` | `cs_100.name` (varchar(20)): blob[82]=4, max_length=20; wrong XPRESS marker selected when using max_length | `test_stats.py` |
| §7.7 (ARCHIVE enc=5 null fallback) | For cmprlevel=4 enc=5 segments, the inner XPRESS block may not satisfy Format D self-ref; null count recovered from h38 directly | `cmp_columnstore_archive.dto`: outer unwrap (9666 B) → inner decompress (73728 B) → no self-ref; h38=142 → correct n_null=142 | `test_stats.py` |
| G44 | xVelocity v4 hash dictionary (version=4 blob) + version-7 sorted pool; Huffman decode via `xmhuffman`; `data_id` is insertion/record-handle order, not alphabetical rank (Bug K3A) | `G44.json` verifier sidecar (1200 data-id → string mappings) | `test_columnstore.py::test_g44_large_dict_*` (4 tests) |
| §7.8 (CCI tombstone) | `sysrowsets.rcrows` for cmprlevel=3 rowset is authoritative live row count; greedy desc-`seg_id` selection drops tombstoned rowgroups; cmprlevel=4 ARCHIVE groups kept unconditionally | `cci_reorganize_full.bak` 1000 live rows (not 1200); `archive_part_single.bak` 140 000 rows | `test_cci_reorganize_coverage.py`, `test_archive_columnstore_partition_coverage.py` |
| §7.8 (CCI delete bitmap) | cmprlevel=2 PAGE-compressed rowset per `object_id`; CD records encode `(seg_id, row_pos)` as excess-BE integers; row positions are suppressed from the decoded segment | `filtered_ncci_full.bak` 400 rows (200 deleted suppressed correctly) | `test_cci_reorganize_coverage.py` |

### Out of Guess Register

These areas are **not** tracked as G01–G52 guesses.  They are documented
elsewhere or intentionally out of scope for this byte-layout register:

| Area | Where tracked | Notes |
|------|---------------|-------|
| `json` (SQL Server 2025+) | §5 | type_id 244 (`NATIVE_JSON`); stored as binary blob; returned as raw `bytes`; implemented in `types.py` and mapped to `pa.binary()` in the Arrow path |
| `vector(N)` (SQL Server 2025+) | §5 | Stored as `varbinary` (type_id 165); 8-byte header `[format_id u16-LE][dims u16-LE][flags u32-LE]` + N × float32-LE; returned as raw `bytes`; fixture `vector_full.bak` (SS2025) |
| GAM / SGAM / PFS pages (`m_type` 7/8/9) | §2.3 | Allocation-map pages; no row data; no traversal decoder |
| Decoder coverage gaps (features, not bytes) | [GAP_ANALYSIS.md](GAP_ANALYSIS.md) | Complementary to this spec: *what* paths are implemented vs *how* bytes lay out |

Fixture build steps for unresolved guesses: [BAK_SPEC_FIXTURES.md §1.7](BAK_SPEC_FIXTURES.md#fixture-recipes).

---

## 11. Layout Coverage Register

Stable IDs parallel to the Guess Register (§10).  Each row tracks a **record
topology** dimension that affects how `sysrscols` column metadata maps to
physical record bytes.  Fixtures and tests reference these IDs the same way as
`Gnn` guesses.

| ID | Layout dimension | Risk | Current coverage | Fixture |
|----|------------------|------|------------------|---------|
| L01 | PK column position (first / second / penultimate / last) | S | 13 types × 4 positions; also surfaced BIT byte-packing (§3.1) | `layoutcoverage_full.bak` |
| L02 | PK type (int, bigint, uniqueidentifier, datetime2, varchar, …) | S | Only `int` PK in matrices | `layoutcoverage_full.bak` |
| L03 | Column count boundaries (1, 30, 31, 1023, 1024) | M | Max ~3 cols per table in type matrix | `layoutcoverage_full.bak` |
| L04 | Multi-page B-tree (rows spanning pages) | M | Type tables are single-page | `layout_cols_1024` (many rows) |
| L05 | Variable columns before fixed PK (null-bitmap ordering) | S | Not exercised | PK-position tables with `varchar` fillers |

Risk codes match §10: `S` = silent wrong data, `M` = table skipped.

Resolution workflow (same as §0):

1. Committed fixture exercises the layout (`tools/layoutmatrix.py` SSOT).
2. `tools/spec_probe.py layout` emits `{layout_id, observed, verifier, verdict}`.
3. Regression test in `tests/test_layout_coverage.py` asserts row values.
4. Promote matching spec rows from `[HEURISTIC]` to `[EMPIRICAL]` or correct
   the layout assumption.

## 12. Version Evolution Register

A **fourth coverage axis** orthogonal to byte layout (§10), record topology
(§11), and feature paths (GAP_ANALYSIS.md).  Each row records a **format
layer** where the on-disk representation changed between SQL Server versions,
the boundary version where the change occurred, the current parser's handling,
and the confidence level.

**Confidence tags** are the same four as §0.  An `[UNKNOWN]` entry means the
parser either applies a single code path without knowing which version it
targets, or does not handle the older format at all.

**V-series IDs** (`V01`–`Vnn`) are stable anchors so that fixture plans,
commit messages, and test names can reference a specific version-boundary
claim.  Existing Guess Register IDs (`Gnn`) are cross-referenced where they
overlap.

**Impact** codes:
- `S` — silent wrong data (rows extracted with incorrect values)
- `M` — rows or tables missing entirely
- `E` — parse error / exception raised

---

### 12.1 Summary table

| ID | Layer | Old behaviour (version ≤) | New behaviour (version ≥) | Boundary | Parser handles | Confidence | Impact if old unhandled | Sample evidence |
|----|-------|--------------------------|--------------------------|----------|----------------|------------|------------------------|-----------------|
| V01 | MSSQLBAK container record header | 8-byte v1 header | 32-byte v2 header | 2012 → 2014 | Both (`compressed.py _V1`/`_V2`) | `[EMPIRICAL]` | E | All v1/v2 fixtures |
| V02 | System catalog page format | Pre-2008 catalog layout | 2008+ catalog layout | 2006 → 2008 | 2008+ only | `[UNKNOWN]` | M | `SalesDBOriginal.bak` |
| V03 | Heap + XML LOB inline pointer | Pre-2016 LOB ptr layout in heap records with `xml NOT NULL` | Post-2016 layout | 2014 → 2016 | All versions pass as of 2026-06 | `[INVALIDATED]` | — | Hypothesis falsified — see §12.2 V03 |
| V04 | In-Memory OLTP (Hekaton/XTP) table storage | Not applicable (feature introduced 2014) | XTP checkpoint files; not B-tree pages | — / 2014+ | XTP log/checkpoint records decoded from the decompressed non-page stream when completeness is provable | `[EMPIRICAL]` | M | `AdventureWorks2016_EXT.bak`, `xtp_checkpoint_straddle_full.bak` |
| V05 | Columnstore enc type: biased integer encoding | `enc=2` (pre-2017 biased RLE/bitpack) | `enc=1` (post-2016 biased RLE/bitpack; different null sentinel) | 2016 → 2017 | Both paths in `columnstore/assembly/reader.py` and `columnstore/decode/value_for.py` | `[EMPIRICAL]` | S | `NYCTaxi_Sample.bak` (enc=2), `boundarycoverage.bak` (enc=1) |
| V06 | Columnstore enc=2 integer numeric secondary dictionary | Integer columns may carry a numeric `sec_dict` blob | Same | ≤2016 (observed) | Handled since commit `ec7ebd2` | `[EMPIRICAL]` | S | `NYCTaxi_Sample.bak` (`passenger_count`, `trip_time_in_secs`) |
| V07 | Columnstore ARCHIVE compression wrapper (enc=5) | Not applicable (feature introduced 2014) | 12-byte frame + optional XPRESS payload per segment/dict blob | — / 2014+ | Handled (`columnstore/decode/enc5_raw.py _ENC5_*`, `columnstore/storage/lob.py _unwrap_archive_blob`) | `[EMPIRICAL]` | E | `cs_lob_preamble.bak` |
| V08 | Always Encrypted column metadata | Not applicable (feature introduced 2016) | `crypt_type` + `crypt_property` in `syscolpars`; encrypted values are opaque | — / 2016+ | Pass-through (opaque bytes returned) | `[EMPIRICAL]` | S | `AdventureWorks2016_EXT.bak` |
| V09 | Temporal types (`date`, `time`, `datetime2`, `datetimeoffset`) | Not applicable (introduced 2008) | Variable-length fixed-field encoding (§5) | — / 2008+ | Handled (`types.py _DT2_TIME_LEN`) | `[CONFIRMED]` | — | `typecoverage_full.bak` |
| V10 | Row / Page CD compression format | Not applicable (introduced 2008) | CD record format (§3.4) | — / 2008+ | Handled (`rowcompress.py`) | `[EMPIRICAL]` | E | `compressioncoverage_full.bak` |
| V11 | IAM page filegroup scope | All IAM pages assumed `file_id = 1` (primary filegroup) | IAM `start_pg` encodes `(file_id, page_id)`; extent bitmap maps extents in same file as IAM page; SPA slots carry explicit `(fid u16, pid u32)` | Always | Handled: `rows.py` uses `iam_loc[1]` for extent pages; reads SPA `fid` directly; checks `available_files` | `[CONFIRMED]` | — | `ndfcoverage_full.bak` (SS2017–2025); DBCC PAGE sidecar `tests/fixtures_2022/V11_probe_results.txt` |
| V12 | Bit column packing (`bit_shift`) | Bit 0 of the status byte always decoded (shift=0 assumed) | Multiple `bit` columns packed into one byte; each offset by `bit_shift` | Always (SQL Server packs from ≥2 bit columns) | Fixed: Rust decoder reads `(byte >> bit_shift) & 1` | `[EMPIRICAL]` | S | `AdventureWorksDW2012.bak` `DimEmployee.SalariedFlag` |
| V13 | System-versioned temporal period columns | Not applicable (temporal introduced 2016) | `ValidFrom`/`ValidTo` period columns carry `generated_always_type` 1/2 encoded in `syscolpars.status` bits 28–29 (`0x10000000`/`0x20000000`); `is_hidden` (HIDDEN keyword) encoded in bit 13 (`0x00002000`); history-table period columns have bits 28–29 clear | — / 2016+ | Extracted: included as normal columns; `Column.generated_always_type` and `Column.is_hidden` expose the metadata | `[CONFIRMED]` | — | `featurecoverage_full.bak` + `temporal_hidden_full.bak` (PageStore XOR probe) |
| V14 | SS2025 new scalar types: `json`, `vector(N)` | Types absent (feature introduced 2025) | `json`: type_id 244 (`NATIVE_JSON`), binary blob; `vector(N)`: type_id 165 (`varbinary`) with 8-byte header `[format_id u16-LE (0x01A9)][dims u16-LE][flags u32-LE (0)]` + N × float32-LE | — / 2025+ | `json`: returned as raw `bytes` (mapped to `pa.binary()`); `vector(N)`: returned as raw `bytes` | `[EMPIRICAL]` | S | `native_json_full.bak` + `vector_full.bak` (SS2025 only) |

---

### 12.2 Detail notes

#### V02 — Pre-2008 system catalog page format `[UNKNOWN]`

`SalesDBOriginal.bak` is a SQL Server 2006 backup.  `classify_table` returns
"no-columns" for all five tables: the column-enumeration query against the
system catalog page tree finds no rows.  The 2006 catalog uses a different
internal layout for `syscolpars` / `sysrscols` than the 2008+ format that
`catalog.py` reads.

**What is unknown:** the 2006 catalog layout — field offsets, column order,
and which system objects exist.

**Action (V02):** Obtain raw catalog page bytes from `SalesDBOriginal.bak`
via `DBCC PAGE` on a SQL Server 2005/2006 instance (or use OrcaMDF's
documented 2005 catalog definitions) and compare field-by-field with the 2008+
layout in `catalog.py: _SYS*_COLS`.  Document the delta here.  A synthetic
fixture is not possible (requires a pre-2008 instance).

**Workaround:** `SalesDB2014.bak` contains the identical dataset in 2014
format; use it as a substitute when only the data is needed.

---

#### V03 — Pre-2016 heap + XML LOB inline pointer `[INVALIDATED]`

**Status (2026-06):** This hypothesis was falsified by `correctness_coverage_samples.md`.
`dbo.DatabaseLog` (heap, `XmlEvent xml NOT NULL`) passes with the correct row count in
every sample version tested, including SS 2008R2 and SS 2012:

| Sample | Creator | `DatabaseLog` rows | Result |
|--------|---------|-------------------|--------|
| `AdventureWorks2008R2.bak` | SS 2008 R2 | 1,597 | ✓ |
| `AdventureWorks2012.bak` | SS 2012 | 1,596 | ✓ |
| `AdventureWorks2014.bak` | SS 2014 | 1,597 | ✓ |
| `AdventureWorksDW2008R2.bak` | SS 2008 R2 | 115 | ✓ |
| `AdventureWorksDW2012.bak` | SS 2012 | 96 | ✓ |

The earlier failures that motivated this entry were caused by a different bug
(now fixed) that affected test_stats.py comparisons before the min/max and
enc=2 fixes landed.  No pre-2016 XML LOB pointer layout difference has been
observed.

**No action needed.**  If a future sample shows `dbo.DatabaseLog` failing with
a genuine row-count drop isolated to pre-2016 backups, reopen this entry with
fresh DBCC PAGE evidence.

---

#### V04 — In-Memory OLTP (Hekaton/XTP) table storage `[EMPIRICAL]`

SQL Server 2014+ supports memory-optimized tables (`CREATE TABLE … WITH
(MEMORY_OPTIMIZED = ON)`).  Durable data for these tables is stored in **XTP
checkpoint file pairs**, not in the standard B-tree page stream that mssqlbak
reads.

**Status (2026-07): partially decoded, completeness-gated.** Detection still
uses the XTP catalog signals above, but compressed backups are no longer treated
as opaque. `xtp.py` scans consecutive non-page decompressed chunks for framed XTP
insert records:

```
[u32 size][u32 flags=0x8000_00LB][u32 seq][u32 marker][u32 pad=0][payload]
```

Rows are emitted only when a table has a provable completeness signal:

- a dense `IDENTITY(1,1)` key enumerating `{1..N}`, or
- a gap-free per-table `seq` run whose payloads fingerprint exactly one schema.

Checkpoint DATA chunks include preamble/header-block artifacts, and v2 MSSQLBAK
compression has a four-byte stream overlap with the following record header; both
are modeled in the current scanner/demux. `AdventureWorks2016_EXT.bak` now lands
all seven XTP tables byte-exact against `.cells` sidecars.

---

#### V06 — Columnstore enc=2 integer numeric secondary dictionary `[CORROBORATED]`

Prior to SQL Server 2017, integer columnstore columns used `enc=2` (biased
encoding).  Some `enc=2` integer segments additionally carry a **numeric
secondary dictionary** blob (`sec_dict ≥ 0`) that maps encoded indices to
actual integer values — the same mechanism used for `REAL`/`FLOAT` columns.
The parser previously applied the dictionary path only for float types; integer
`enc=2` columns fell through to the formula-based path and produced wrong
values.

Fixed in commit `ec7ebd2`: `_parse_numeric_dict_int` + `_decode_enc2_int_dict`
added; dispatch in `read_columnstore_rows` / `read_columnstore_batches` now
checks `enc=2 AND sec_dict ≥ 0 AND not float` and falls back to formula-based
decoding only when the dictionary blob is absent.

**Remaining unknown:** whether `enc=2` integer numeric dictionaries also appear
in SQL Server 2017+ fixtures, or are exclusive to the pre-2017 engine.  No
SS2017+ sample has been observed with this combination.

---

#### V11 — IAM page filegroup scope `[CONFIRMED]` (2026-06-17)

**Fixed and verified.**  `rows.py` correctly handles tables on secondary
filegroups; `ndfcoverage_full.bak` provides a regression fixture with a
clustered-index table on `FG_SECONDARY` (file_id=3), passing 7/7 tests on
SS2017–2025.

**DBCC PAGE confirmation** (`tests/fixtures_2022/V11_probe_results.txt`):

- Primary-filegroup IAM at `(1:353)`: `start_pg = (1:0)` — bitmap maps
  extents in file_id=1.
- Secondary-filegroup IAM at `(3:16)`: `start_pg = (3:0)` — bitmap maps
  extents in file_id=3 (the NDF file).

**Confirmed mechanism:**

1. An IAM page lives in the same file as the extents it maps.  The
   `start_pg` field in the IAM header records `(file_id, page_id)` as a
   standard page pointer; all extents in the bitmap belong to
   `start_pg.file_id`.
2. SPA (single-page allocation) slots at IAM offset +0x2E are 6-byte
   `(file_id u16, page_id u32)` pairs and may reference any file (mixed
   extents spanning files are possible).
3. `rows.py _heap_pages_for_unit`: uses `iam_loc[1]` as the file_id for
   all extent-mapped pages; reads `fid` directly from each SPA slot; guards
   both with `fid in store.available_files`.
4. `rows.py _data_pages`: uses `first_page[file_id]` from the catalog
   allocation unit (correctly populated by the `catalog.py` sysalloc reader)
   and follows `next_page` using the page header's embedded `(pid, fid)`.

**Regression fixture:** `ndfcoverage_full.bak` — `dbo.secondary_tbl` is a
clustered-index table on `FG_SECONDARY`; `tests/test_ndf_coverage.py`
assertions: row count (10), values, `available_files` includes secondary fid.

---

#### V12 — Bit column packing (`bit_shift`) `[CORROBORATED]`

SQL Server packs multiple `bit` columns into a single status byte.  When a
table has two or more `bit` columns, the Rust decoder was extracting bit 0 of
the byte for every column, ignoring the `bit_shift` offset stored in
`sysrscols`.  Affected tables (e.g. `dbo.DimEmployee.SalariedFlag`) produced
incorrect min/max distributions (always False instead of True/False).

**Status (2026-06): Fixed.** `ColSchema.bit_shift` added to the Rust
`page_decode.rs` struct; bit decoding changed from `b[0] & 1` to
`(b[0] >> bit_shift) & 1`.

---

#### V13 — System-versioned temporal period columns `[CONFIRMED]`

SQL Server 2016+ system-versioned temporal tables have `GENERATED ALWAYS AS
ROW START / ROW END` period columns (`ValidFrom` / `ValidTo`, or custom names).
These are stored as regular `DATETIME2` columns in both the current table and
the history (_Archive) table.  They are NOT excluded from `syscolpars` and DO
have `sysrscols` entries.

**`syscolpars.status` bit encoding (confirmed from `featurecoverage_full.bak`
and `temporal_hidden_full.bak` via raw PageStore read + XOR analysis):**

| Bit | Mask | Meaning |
|-----|------|---------|
| 13 | `0x00002000` | `is_hidden=1` (period column declared with `HIDDEN` keyword) |
| 28 | `0x10000000` | `generated_always_type=1` (AS_ROW_START) |
| 29 | `0x20000000` | `generated_always_type=2` (AS_ROW_END)   |

These bits are set **only on the current system-versioned table**; the history
table's period columns have bits 28–29 clear (`generated_always_type=0`) because
they are plain `DATETIME2` columns there.  Bit 13 (`is_hidden`) is set on the
current table when the `HIDDEN` keyword was used in the `CREATE TABLE` statement;
it controls whether the column appears in `SELECT *` results.  HIDDEN period
columns still have `sysrscols` entries and decode identically to non-hidden ones.

`recover_schema` exposes these as `Column.generated_always_type` (int: 0, 1, or 2)
and `Column.is_hidden` (bool).

**Bit 13 confirmation method:** `temporal_hidden_full.bak` contains two identical
temporal tables differing only in the `HIDDEN` keyword.  PageStore XOR of matching
`valid_from` status values:
`0x10002001` (hidden) XOR `0x10000001` (visible) = `0x00002000` (bit 13).

**Verifier:** `tests/fixtures_2022/V13_hidden_probe_results.txt` (PageStore XOR
from `temporal_hidden_full.bak`); `tests/fixtures_realworld/V13_probe_results.txt`
(status hex from `featurecoverage_full.bak`).  Four regression tests in
`test_feature_coverage.py`:
`test_temporal_current_generated_always_type`,
`test_temporal_history_generated_always_type_zero`,
`test_temporal_hidden_period_columns_is_hidden`, and
`test_temporal_hidden_generated_always_type_unchanged`.

---

#### V14 — SS2025 new scalar types: `json`, `vector(N)` `[EMPIRICAL]`

**`json` type (NATIVE_JSON, type_id 244).**  SQL Server 2025 introduces a
first-class `json` scalar type distinct from `nvarchar(max)` JSON strings.
The on-disk representation is a proprietary binary blob; the content is not
plain UTF-8 text.  `types.py` maps type_id 244 (`NATIVE_JSON`) to the
`_dv_bytes` decoder, which returns raw `bytes`.  In the Arrow path
`arrow_type()` maps it to `pa.binary()`.

`SUPPORTED_TYPE_IDS` includes 244, so tables with `json` columns are not
skipped.

**`vector(N)` type.**  SQL Server 2025 also introduces `VECTOR(N)`, a
fixed-dimension float32 array type.  On-disk it is stored as a `varbinary`
(type_id 165) with the following layout:

```
[+0:+2]   uint16 LE  format_id    0x01A9 for float32 vectors
[+2:+4]   uint16 LE  dims         number of dimensions (= N)
[+4:+8]   uint32 LE  flags        0 in all observed fixtures
[+8 ..]   N × float32-LE          the vector components
```

mssqlbak returns the raw `bytes` blob.  Callers decode components with:

```python
import struct
n_dims = struct.unpack_from("<H", raw, 2)[0]
floats = struct.unpack_from(f"<{n_dims}f", raw, 8)
```

**Fixtures:** `tests/fixtures_2025/native_json_full.bak` (json columns);
`tests/fixtures_2025/vector_full.bak` (VECTOR(3) column, 100 rows).
**Tests:** `test_native_json_coverage.py`, `test_vector_coverage.py`.

---

### 12.3 Coverage model (updated)

The spec now tracks five orthogonal axes:

| Axis | Register | IDs | What it covers |
|------|----------|-----|----------------|
| Byte layout | §10 Guess Register | `G01`–`G52` | Raw byte offsets and field meanings |
| Record topology | §11 Layout Register | `L01`–`L05` | Column position within multi-column rows |
| Feature paths | GAP_ANALYSIS.md | — | Which decoder path runs for a given storage feature |
| Version evolution | §12 (this section) | `V01`–`V14` | Format changes across SQL Server versions |
| **Value coverage** | **§13 Value Coverage Register** | **`VC01`–`VCnn`** | **For each field with N documented values, are all N values present in ≥1 fixture?** |

A format layer is only safe to call `[CONFIRMED]` across a version range when
a committed fixture exercising both the old and new format exists **and** a
DBCC PAGE or DMV verifier confirms the byte-level delta.

A field is only safe to call fully covered when every documented value appears
in at least one committed fixture (§13).

---

## 13. Value Coverage Register

A **fifth coverage axis** alongside byte layout (§10), record topology (§11),
version evolution (§12), and feature paths (`GAP_ANALYSIS.md`).

**The question this axis answers:** For every field whose spec documents N
possible values {v₁, …, vₙ}, does at least one committed fixture exercise each
vᵢ?

This is different from the Guess Register — a field can be fully `[CONFIRMED]`
for byte layout yet have a value blind spot if only one of its documented values
ever appears in any fixture.  The Guess Register says "we know what this byte
means"; the Value Coverage Register says "we have also tested every value it can
take."

**How a value enters this register:** the spec body says "observed values: X, Y,
Z" or "can be A or B" — any enumeration of two or more documented values where
not all are demonstrably present in the committed fixture corpus.

**Risk codes** match §10/§12: `S` = silent wrong data, `M` = table/row skipped,
`L` = metadata only.

**Status values:**

| Status | Meaning |
|--------|---------|
| `open` | ≥1 documented value absent from all committed fixtures |
| `partial` | Present in fixtures but no independent verifier sidecar for the missing sub-case |
| `not catalogued` | Multiple values documented and observed but not tracked which fixture has which value |
| `assumed-constant` | Spec says "always X"; parser does not branch on it; no counter-example observed. Low actionability; documented so the assumption is explicit. |
| `CLOSED` | All documented values present in ≥1 committed fixture |

### 13.1 Summary table

| ID | Field | Layer | Documented values | Covered in fixtures | Blind-spot values | Risk | Status | Closing action |
|----|-------|-------|-------------------|---------------------|-------------------|------|--------|----------------|
| VC01 | SSET `block_attributes` backup kind | §1.1.3 | NORMAL (`0x04`), DIFFERENTIAL (`0x08`), LOG/INCREMENTAL (`0x10`), COPY_ONLY (`0x02`) | NORMAL only (every committed fixture) | DIFFERENTIAL, LOG, COPY_ONLY | M | **open** | `BACKUP DATABASE … WITH DIFFERENTIAL`, `BACKUP LOG`, `BACKUP DATABASE … WITH COPY_ONLY` fixtures; verify with `RESTORE HEADERONLY` sidecar |
| VC02 | LOB on-page record `btyp` | §6.2 | 3 (DATA / `DATA`), 2 (LARGE_ROOT / `INTERNAL`), 5 (ROOT / `LARGE_ROOT_YUKON`) | 2 ✅ G31, 5 ✅ G31; 3 implicitly traversed in every LOB chain | btyp=3 has no independent verifier sidecar | S | **partial** | `DBCC PAGE (<db>, 1, <DATA-leaf-page>, 3)` on `cs_lob_preamble2.bak`; commit result as `G31b.json`.  All three btyp values are corroborated by Kazamiya forensicist blog + Korotkevitch aboutsqlserver.com |
| VC03 | LOB btyp=2 `max_links` at `+14` | §6.2 | `0x0002` (2-slot INTERNAL node), `0x0004` (4-slot INTERNAL node) | `0x0002` in `cs_lob_preamble2.bak` (likely); `0x0004` status unknown | `max_links=4` node — no committed fixture confirmed | S | **open** | Research: btyp=2 nodes with `max_links=4` appear when the LOB tree fan-out uses 4-child internal nodes. Probe `cs_lob_preamble2.bak` INTERNAL pages with DBCC PAGE to check `MaxLinks` value; if only 2-slot nodes seen, generate a LOB value large enough to require 4+ level-1 children.  **Note:** previous name "flags / format_version" was incorrect — external sources confirm this is `MaxLinks` (node link capacity), not a format version. |
| VC04 | MSSQLBAK `version word 2` [12:16] | §1.2.1, G04 | 0, 1, 2 (all three observed) | Not tracked per fixture | All three values — fixture association uncatalogued | L | **not catalogued** | `python -c "import sys; d=open(sys.argv[1],'rb').read(); print(int.from_bytes(d[12:16],'little'))" <fixture>.bak` on each compressed fixture; record value per SS version in G04 detail note |
| VC05 | Columnstore segment blob `block_size` at `+24` | §7.3 | "always 512" (one value ever observed) | 512 only | Non-512 (theoretical) | S | **assumed-constant** | Add assertion `assert block_size == 512` in `columnstore/storage/segment_meta.py` so any deviation surfaces as a loud error rather than silent wrong data |
| VC06 | Columnstore ARCHIVE blob `flags` at `+0` | §7.4 | "observed: 0" | 0 only | Non-zero (theoretical) | M | **assumed-constant** | Add assertion in `_unwrap_archive_blob`; document assumption in §7.4 |
| VC07 | MTF `string_type` (common block header `+48`) | §1.1.1 | `0x00` none, `0x01` ANSI, `0x02` UTF-16LE | `0x02` only | `0x00`, `0x01` | L | **not actionable for SS2017+** | `0x02` is invariant for all supported SQL Server versions; `0x01` is a pre-SQL Server 7 artifact.  Close if the SS2017+ target is confirmed as the floor. |
| ~~VC08~~ | Columnstore `enc_type` | §7.1 | 1, 2, 3, 4, 5 | 1 ✅, 2 ✅ (NYCTaxi_Sample), 3 ✅, 4 ✅, 5 ✅ | — | S | **CLOSED** | — |
| ~~VC09~~ | Columnstore `has_null` | §7.1 | 0 (no nulls), 1 (has nulls) | both ✅ (`compressioncoverage_full.bak`) | — | S | **CLOSED** | — |
| ~~VC10~~ | Columnstore FOR `for_base` | §7.3 | 0 (sequential), non-zero (random order) | both ✅ — closed by Part II random-order fixtures (2026-06-16) | — | S | **CLOSED** | — |
| ~~VC11~~ | Log tail block type byte | §9.1.2, G51 | `0x50` (opening block), `0x40` (continuation block) | both ✅ (`dirtycoverage_wide.bak` cross-block record) | — | M | **CLOSED** | — |
| ~~VC12~~ | Log INSERT/DELETE `SUBTYPE` | §9.1.4, G52 | `0x00` (SS2017), `0x04` (SS2019+) | both ✅ (SS2017 and SS2019 fixture dirs) | — | S | **CLOSED** | — |
| ~~VC13~~ | Record `status_B` bit 0 (forwarded heap stub) | §3.2, G15/G16 | 0 (normal), 1 (forwarded) | both ✅ (`dirtycoverage_heap_forward.bak`) | — | S | **CLOSED** | — |

### 13.2 Priority and closing actions

**VC01 (backup kind)** is the highest-impact open item.  DIFFERENTIAL and LOG
backups are common in production environments.  The parser reads `block_attributes`
from the MTF SSET header to classify the backup type; a misclassification here
causes the extractor to silently skip data or return incorrect metadata.  The
fixtures are straightforward to generate:

```sql
-- in the fixture creation script, after a FULL backup:
BACKUP DATABASE [Fixture] TO DISK = '/path/backupkind_differential.bak'
    WITH DIFFERENTIAL;

BACKUP LOG [Fixture] TO DISK = '/path/backupkind_log.bak';

BACKUP DATABASE [Fixture] TO DISK = '/path/backupkind_copyonly.bak'
    WITH COPY_ONLY;
```

Attach `RESTORE HEADERONLY` output as the verifier sidecar (it returns
`BackupType` 1=full, 2=log, 4=diff, 5=file, 6=filegroup diff, 7=partial).

**VC02 (btyp=3 sidecar)** is low effort.  `cs_lob_preamble2.bak` already
contains multi-level LOB chains; the btyp=3 DATA leaf pages are already
physically present.  A targeted `DBCC PAGE` probe documents the byte layout
independently.  No new fixture is required — only a new verifier sidecar.

**VC03 (LARGE_ROOT flags `0x0004`)** requires understanding when SQL Server
emits this flag variant.  First check whether any existing sample corpus file
(AdventureWorks, WideWorldImporters) contains a btyp=2 record with
`flags = 0x0004`, then decide whether a new synthetic fixture is needed.

**VC04 (version word 2)** requires only a one-line hex probe of three compressed
fixtures built from different SS versions.  Record the value in the G04 detail
note (§10).

**VC05 / VC06 (assumed-constant fields)** do not need new fixtures.  The closing
action is adding an explicit `assert` or `raise ValueError` in `columnstore/storage/segment_meta.py`
so that any future backup with a non-512 block_size or non-zero archive flags
produces a clear error rather than silent wrong data.

---

## 13. Value Coverage Register (VC)

A **fifth coverage axis** that links decoder heuristics to discriminators,
fixtures, and census branch tags.  Use this table to answer: *"which heuristic
changed, which fixture exercises it, and which census tag should appear?"*

Update this table whenever a new heuristic is added or an existing one is
replaced with a grounded discriminator.  A **discriminator** is an upstream
catalog or header field that deterministically selects the branch (e.g.
`enc_type`, `type_id`, `is_unicode`) rather than a magic-byte probe.

| ID | Decoder heuristic | Location | Discriminator (real) | Remaining uncertainty | Fixture(s) | Census tag(s) |
|----|-------------------|----------|---------------------|----------------------|------------|---------------|
| VC01 | `0x21` inline-MAX strip (all MAX types) | `mssqlbak/rows.py read_table_rows` | `col.max_length == -1` selects candidate; parity of `len(cell)` for nvarchar(max) type_id 231 | None — discriminator is fully grounded (parity uniquely identifies genuine prefix vs data byte) | `nvarchar_max_u21_full.bak` | `u21:strip-all`, `u21:keep-even` |
| VC02 | `_align_enc1_blob` preamble probe | `mssqlbak/columnstore/assembly/reader.py` | `is_archive_rg` (catalog `cmprlevel`); BPV at offset 34 (u16); n_rows at offset 52 | The BPV=0 + n_rows=0 case (legacy preamble) is not confirmed by any committed fixture | `archive_columnstore_types_full.bak`, `columnstore_minimal.bak` | `align:archive`, `align:bpv-nonzero`, `align:nrows-nonzero`, `align:deinterleave` |
| VC03 | enc=5 format A/B/C/D/ARCHIVE detection | `mssqlbak/columnstore/decode/enc5_raw.py _decode_enc5` | `u16@92` (h92), `\xfe\xff` sentinel, `u16@38`/`u32@38` vs n_rows; `is_archive_rg` for outer ARCHIVE | h38_u32 == n coincidence for non-ARCHIVE blobs (guarded by per-type override) | `columnstore_minimal.bak`, `archive_columnstore_types_full.bak` | `enc5:archive`, `enc5:formatA`, `enc5:formatB`, `enc5:formatC`, `enc5:formatD`, `enc5:multichunk` |
| VC04 | v4 Huffman record splitting in `_split_v4_record` | `mssqlbak/columnstore/decode/dict_xvelocity.py` | Per-byte sign of `decoded0 = r[0] - _V4_CHAR_OFFSET`; length prefix byte; CHAR(n) multi-pack divisibility | Mixed-packed records with short+long values in one handle | `columnstore_minimal.bak`, `cci_extended_full.bak`, `cs_lob_preamble.bak`, `cs_lob_preamble2.bak` | `v4split:varchar-short`, `v4split:varchar-long`, `v4split:char-multi`, `v4split:fallback`, `v4split:empty` |
| VC05 | Small string dict encoding order (UTF-16 vs cp1252) | `mssqlbak/columnstore/decode/dict_string.py _parse_dict_strings` | `col.type_id in (NVARCHAR, NCHAR)` → `unicode_first=True`; others → False | The heuristic try-order is now grounded by column type; false positive still possible for cp1252 ASCII bytes that form valid UTF-16LE | Small-dict CCI fixtures with nvarchar vs varchar columns | `dict:utf16-ok`, `dict:cp1252-ok`, `dict:binary`, `dict:empty` |
| VC06 | Global vs local (prim/sec) dict concatenation order | `mssqlbak/columnstore/assembly/reader.py _load_one_string_dict` | Segment metadata fields `prim_dict`/`sec_dict` (offset 52/56); confirmed by G40 verifier | `prim_dict`/`sec_dict` field-name inversion documented in §7.6 — wiring is correct; the naming is the risk | `boundarycoverage_full.bak` (G40 verifier) | No census tag (dictionary loading precedes row iteration) |

**Column definitions:**

- **Discriminator (real)**: the catalog or header field that should determine the branch.
  When this is a magic-byte probe rather than a named field, the entry is `[HEURISTIC]`.
- **Remaining uncertainty**: known edge cases where the discriminator can produce a wrong
  branch selection.  Empty = fully grounded.
- **Census tag**: the stable string emitted by `mssqlbak/decode_trace.py record_tag()` when
  this branch is taken.  Update `tests/census_baseline.json` whenever a tag is added or a
  fixture's path changes.

---

## See Also

- [docs/design/README.md](../design/README.md) — implementation design: third-party vs hand-rolled dependencies, decode pipeline architecture, and quality-attribute tradeoffs.
- [docs/COVERAGE.md](COVERAGE.md) — consolidated feature coverage: supported types, backup types, storage features, real-world corpus results, and unsupported areas.
- [docs/CORROBORATION_SOURCES.md](CORROBORATION_SOURCES.md) — SSOT for `[CORROBORATED]` source rows and remaining internal-only sections.
- [docs/BAK_SPEC_FIXTURES.md](BAK_SPEC_FIXTURES.md) — fixture and verifier plan for resolving Guess IDs.
- [docs/BAK_SPEC_FIXTURES.md §1.7](BAK_SPEC_FIXTURES.md#fixture-recipes) — executable fixture build recipes.
- [docs/GAP_ANALYSIS.md](GAP_ANALYSIS.md) — supported storage features and out-of-scope areas.
- [docs/DIRTY_BACKUP_ANALYSIS.md](DIRTY_BACKUP_ANALYSIS.md) — dirty/fuzzy backup scenarios.
- [docs/CONCURRENT_OPERATIONS_COVERAGE.md](CONCURRENT_OPERATIONS_COVERAGE.md) — concurrent-operation coverage.
- [docs/FIXTURE_GAPS.md](FIXTURE_GAPS.md) — per-gap evidence and actions for failures observed in the real-world sample corpus.
