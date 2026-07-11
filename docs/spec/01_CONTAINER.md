## 1. Backup Container Layer

### 1.1 Uncompressed backup — Microsoft Tape Format (MTF) `[CONFIRMED]`

An uncompressed `.bak` file is a flat sequence of fixed-size **physical
blocks**.  Block size defaults to 65 536 bytes (64 KB) but any power-of-two
multiple of 512 is legal via `BACKUP … WITH BLOCKSIZE = N`.

```
offset 0             : TAPE block  (media descriptor)
offset block_size    : SSET block  (start of backup set)
offset 2*block_size  : VOLB block  (volume)
...                  : DIRB / FILE / data blocks
...                  : ESET block  (end of set)
...                  : EOTM block  (end of tape)
```

**Block-size detection** `[CONFIRMED]`: probe offsets
`{512, 1024, 2048, 4096, 8192, 16384, 32768, 65536}`.  The correct size is the
first candidate where offset `block_size` starts with a known MTF type code
(`TAPE`, `SSET`, `VOLB`, `DIRB`, `FILE`, `CFIL`, `ESPB`, `ESET`, `EOTM`,
`SFMB`) or all-zero padding.

The MTF TAPE block field `format_logical_block_size` (uint16 LE at offset 84)
is the internal MTF *logical-block* size (1024 bytes in practice) — it is **not**
the physical MTF block size used for container framing.  The two differ because
MTF distinguishes logical blocks (minimum data-transfer unit) from physical
blocks (the actual TAPE/SSET/… fixed-size chunk).  The physical block size is
therefore not available as a stored field; the empirical probe is the confirmed
correct and only reliable detection method.  Sidecar: `tests/fixtures_2022/probe/G10.json`.

#### 1.1.1 MTF Common Block Header (`MTF_DB_HDR`) — 52 bytes `[CONFIRMED]`

Source: Microsoft Tape Format Specification v1.00a, `struct MTF_DB_HDR`.

| Offset | Size | Type | Field | Notes |
|--------|------|------|-------|-------|
| 0 | 4 | ASCII | `block_type` | `TAPE`, `SSET`, etc. |
| 4 | 4 | uint32 LE | `block_attributes` | bit flags |
| 8 | 2 | uint16 LE | `offset_to_first_event` | |
| 10 | 1 | uint8 | `os_id` | `0x0E` = Windows NT |
| 11 | 1 | uint8 | `os_version` | |
| 12 | 8 | uint64 LE | `displayable_size` | |
| 20 | 8 | uint64 LE | `format_logical_address` | |
| 28 | 2 | uint16 LE | `reserved_for_mbc` | |
| 30 | 6 | — | reserved | |
| 36 | 4 | uint32 LE | `control_block_id` | |
| 40 | 4 | — | reserved | |
| 44 | 4 | — | `os_specific_data` | `MTF_TAPE_ADDRESS {uint16 size, uint16 offset}` |
| 48 | 1 | uint8 | `string_type` | `0x00`=none, `0x01`=ANSI, `0x02`=UTF-16LE |
| 49 | 1 | — | reserved | |
| 50 | 2 | uint16 LE | `header_checksum` | |

Variable-length fields are **not** inline.  They are referenced by
`MTF_TAPE_ADDRESS {uint16 size, uint16 offset}` pointers where `offset` is
from the start of the block.

#### 1.1.2 TAPE block (`MTF_TAPE_BLK`) `[CONFIRMED]`

Immediately after the 52-byte common header:

| Offset | Size | Field |
|--------|------|-------|
| 52 | 4 | `media_family_id` |
| 56 | 4 | `tape_attributes` |
| 60 | 2 | `media_seq_num` |
| 62 | 2 | `pw_encrypt_alg` |
| 64 | 2 | `soft_filemark_block_size` |
| 66 | 2 | `media_catalogue_type` |
| 68 | 4 | `media_name` (`MTF_TAPE_ADDRESS`) |
| 72 | 4 | `media_description` (`MTF_TAPE_ADDRESS`) |
| 76 | 4 | `media_password` (`MTF_TAPE_ADDRESS`) |
| 80 | 4 | `software_name` (`MTF_TAPE_ADDRESS`, e.g. `"Microsoft SQL Server"`) |
| 84 | 2 | `format_logical_block_size` |
| 86 | 2 | `software_vendor_id` |
| 88 | 5 | `media_date` (packed MTF date, §1.1.4) |
| 93 | 1 | `mtf_major_version` |

#### 1.1.3 SSET block (`MTF_SSET_BLK`) `[CONFIRMED + HEURISTIC]`

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 52 | 4 | `block_attributes` | backup kind (see flags below) — `[CONFIRMED]` |
| 56 | 2 | `pw_encrypt_alg` | |
| 58 | 2 | `software_compression` | |
| 60 | 2 | `software_vendor_id` | |
| 62 | 2 | `dataset_number` | |
| 64 | 4 | `dataset_name` (`MTF_TAPE_ADDRESS`) | usually empty for DB backups |
| 68 | 4 | `dataset_description` (`MTF_TAPE_ADDRESS`) | |
| 72 | 4 | `dataset_password` (`MTF_TAPE_ADDRESS`) | |
| 76 | 4 | `user_name` (`MTF_TAPE_ADDRESS`) | |
| 80 | 8 | `physical_block_address` | |
| 88 | 5 | `media_write_date` (packed MTF date) | |
| 93 | 1 | `software_major_version` | |
| 94+ | — | SQL Server config stream | `[HEURISTIC]` — see §1.1.5 |

**Backup-kind flags** in `block_attributes` `[CONFIRMED]`:

| Bit mask | Meaning |
|----------|---------|
| `0x00000002` | COPY (`COPY_ONLY`; combined with NORMAL for copy-only full) |
| `0x00000004` | NORMAL (full backup) |
| `0x00000008` | DIFFERENTIAL |
| `0x00000010` | INCREMENTAL |
| `0x00000020` | DAILY |

#### 1.1.4 MTF packed date (`MTF_DATE_TIME`) — 5 bytes `[CONFIRMED]`

40 bits packed **big-endian**, most-significant field first:

| Field | Bits |
|-------|------|
| year | 14 |
| month | 4 |
| day | 5 |
| hour | 5 |
| minute | 6 |
| second | 6 |

All-zero → "unknown" → `None`.

Decode:
```python
yr  = (b[0] << 6) | (b[1] >> 2)
mon = ((b[1] & 0x03) << 2) | ((b[2] & 0xC0) >> 6)
day = (b[2] & 0x3E) >> 1
hr  = ((b[2] & 0x01) << 4) | ((b[3] & 0xF0) >> 4)
mn  = ((b[3] & 0x0F) << 2) | ((b[4] & 0xC0) >> 6)
sec = b[4] & 0x3F
```

#### 1.1.5 SQL Server proprietary config stream (after SSET) `[HEURISTIC]`

SQL Server appends a proprietary configuration stream immediately after the
standard SSET descriptor bytes.  Sub-block tags observed: `MQCI`, `SFGI`.
The parser decodes the fields below.

**MQCI sub-block — backup-set LSNs `[EMPIRICAL]`**

The `MQCI` tag (`reader.py: _MQCI_TAG = b"MQCI"`) marks a sub-block that
carries the four backup-set LSN triplets.  These are located by scanning the
raw SSET block bytes for the tag, then reading at fixed offsets from the tag
start (`reader.py: _parse_lsns_from_sset_block`, `reader.py:562-601`):

| Offset from tag | Size | Field |
|-----------------|------|-------|
| +54 | 10 | `first_lsn` |
| +64 | 10 | `last_lsn` |
| +74 | `checkpoint_lsn` | 10 |
| +84 | 10 | `database_backup_lsn` |

Each LSN is a 10-byte little-endian triplet:
`struct("<IIH")` = `(vlf_seq u32, blk_offset u32, rec_pos u16)`.
An all-zero triplet means "absent".  The decimal LSN string is
`"%d:%d:%d" % (vlf_seq, blk_offset, rec_pos)`.

**What we can locate reliably:**
- Physical data/log file paths ending in `.mdf`, `.ndf`, or `.ldf` — found by
  decoding the whole block as UTF-16LE and matching path-shaped substrings.
- Database name — sometimes present as the `dataset_name` MTF field; otherwise
  derived from the primary `.mdf` file stem.
- Backup-set LSNs — via the MQCI sub-block above.

**What we can locate with best-effort heuristic:**
- Server name framing — **G11 `[HEURISTIC]`** — best-effort: the UTF-16LE run
  immediately before the `SFGI` marker, with the database-name prefix stripped,
  is treated as the server name.  Produces the correct result on all tested
  backups (SS2017–SS2025 fixtures, WideWorldImporters, AdventureWorks) but
  would fail if the database name is not a strict prefix of the concatenated
  string.
- Database name — **G12 `[HEURISTIC]`** — `dataset_name` MTF field when
  present; otherwise the primary `.mdf` file-stem.  Works on all tested backups;
  failure scenario (e.g. dataset_name set to something unexpected) not observed.

---

### 1.2 Compressed backup — MSSQLBAK container `[EMPIRICAL + HEURISTIC]`

`BACKUP DATABASE … WITH COMPRESSION` does **not** produce an MTF file.
Instead SQL Server wraps the entire backup in a proprietary container whose
first 8 bytes are the ASCII magic `MSSQLBAK`.

External corroboration (partial): Stuart Moore independently observed compressed
backup files starting with `MSSQLBAK…` and notes the compressed format is
proprietary; Microsoft `RESTORE HEADERONLY` / backup-compression docs expose
compression state and algorithm (`MS_XPRESS`) but do not document the container
record headers. Therefore §1.2.1–§1.2.4 remain `[EMPIRICAL]`.

#### 1.2.1 Container magic and version `[EMPIRICAL]`

```
[0:8]  ASCII  "MSSQLBAK"
[8:12] uint32 LE  version word 1  →  selects record-header layout (≤1 = v1, ≥2 = v2)
[12:16] uint32 LE  version word 2  →  [UNKNOWN]
```

> **Unknown:** what `version word 2` encodes.  Observed values: 0, 1, 2.

#### 1.2.2 Record-header layout `[EMPIRICAL]`

The container is a sequence of **records**.  Each record has a
version-dependent header followed by one XPRESS-compressed chunk.

**Version 1 (SQL Server ≤ 2012) — 8-byte header:**

```
[+0]  uint32 LE  tag        bits 16..31 = compressed chunk size (incl. Huffman table)
                             bits 0..15  = [UNKNOWN]
[+4]  uint32 LE  crc32      CRC of the compressed chunk
[+8]  bytes      XPRESS chunk  (256-byte Huffman table + bitstream)
```

Next record: `H + 8 + (tag >> 16)`

**Version 2 (SQL Server 2014+) — 32-byte header:**

```
[+0]  uint32 LE  prev_uncompressed_size   [HEURISTIC] — housekeeping; not used for decode
[+4]  uint32 LE  tag                      bits 16..31 = compressed chunk size
[+8]  16 bytes   [UNKNOWN]               observed: 0xFF×16, or what appears to be a hash
[+24] uint32 LE  zero                     always 0x00000000; used as structural marker
[+28] uint32 LE  crc32
[+32] bytes      XPRESS chunk
```

Next record: `H + 28 + (tag >> 16)`

Unresolved: **G01**–**G04** — see [Guess Register §10](#what-is-guessed--the-guess-register) and [work queue](BAK_SPEC_FIXTURES.md#container-and-metadata).

#### 1.2.3 Record chain and re-synchronization `[EMPIRICAL]`

Records chain forward by the rule above.  At `SFMB` (soft filemark) and
sub-block boundaries the chain is interrupted by padding; the parser
**re-synchronizes** by scanning forward for the next structurally valid header.

A structurally valid v2 header satisfies all of:
1. A zero `uint32` at `+24`.
2. The 256 bytes at `+32` form a **Kraft-complete** XPRESS Huffman table (all
   512 4-bit codeword lengths exactly fill the code space).
3. `tag >> 16 > 0` (a non-zero compressed size).

Kraft equality is an extremely strong filter; false positives are observed but
are caught by decode failure.

#### 1.2.4 XPRESS chunk payload `[EMPIRICAL]`

Each chunk decompresses to at most one **allocated extent** = 8 × 8 KB = 64 KB.
Trailing all-zero pages within the extent are omitted (the compressed output is
shorter).  The true decompressed size is recovered by decoding until the
compressed input is exhausted, then rounding up to the next 8 KB multiple.

The first two chunks of any compressed backup decompress to MTF descriptor
blocks (TAPE and SSET) rather than 8 KB pages.  These are identified by their
4-byte block type identifier at offset 0.  **G05 `[CONFIRMED]`**: in
uncompressed backups the first physical blocks are always `TAPE` (offset 0),
optionally `SFMB` (soft filemark), then `SSET` — confirmed across SS2017–SS2025;
the `SFMB` is a soft filemark boundary marker inserted by SQL Server between the
media descriptor and the backup set and must be tolerated.  In compressed
backups the same TAPE + SSET descriptor ordering is preserved as the first two
decompressed chunks.

#### 1.2.5 Version 2 chunk-stream overlap `[EMPIRICAL]`

**Critical implementation detail**: for v2 containers the XPRESS bitstream of
a chunk extends **4 bytes past the nominal end** of the record.

For a v2 record with header at `H`:
- `next_H = H + 28 + (tag >> 16)` (the next record's header start)
- The XPRESS stream for the *current* chunk starts at `H + 32` (the Huffman
  table) and **ends at `next_H + 4`**, i.e. 4 bytes into the next record.

Expressed using the layout constants (`compressed.py: _V2`):
```
stream_end = next_h + huffman_off - next_base
           = next_h + 32 - 28
           = next_h + 4
```

Omitting this 4-byte overlap (feeding only bytes `[H+32 : next_H]` to the
XPRESS decoder) produces a corrupted final page — specifically the last two
bytes of the last page in an extent are wrong.  The overlap is consumed
during the bitstream decode and must be included in the input slice.

Source: `compressed.py: _decode_chunk` (line 293), `_iter_chunks_with_pages`
(lines 618-621).

---

### 1.3 BACPAC container `[CORROBORATED]`

A `.bacpac` file is a **ZIP archive** (RFC 1950 + Deflate) with no SQL Server
proprietary framing.  mssqlbak reads it via `zipfile.ZipFile`; for cloud-backed
`BakReader` sources the ZIP central directory is located by a two-step seek (end
of file, then central directory offset).

#### 1.3.1 Archive layout

```
[Content_Types].xml  — OOXML content-type registry
_rels/.rels          — package relationships (type: DacMetadata)
DacMetadata.xml      — DACPAC metadata (schema version, build version)
Origin.xml           — export metadata (ExportSqlServer, ExportVersion, etc.)
model.xml            — DACPAC schema model (tables, columns, types)
Data/<schema>.<table>/TableData-000-00000.BCP  — one file per non-empty table
```

Only `model.xml` and the `Data/` entries are consumed by the extractor.

#### 1.3.2 model.xml schema (DACPAC XML, MS-DACPAC) `[CORROBORATED]`

```xml
<DataSchemaModel>
  <Model>
    <Element Type="SqlTable" Name="[schema].[table]">
      <Element Type="SqlSimpleColumn" Name="[schema].[table].[col]">
        <Property Name="IsNullable" Value="False"/>    <!-- absent = True -->
        <Property Name="IsComputed" Value="True"/>     <!-- absent = False -->
        <Relationship Name="TypeSpecifier">
          <Element Type="SqlTypeSpecifier">
            <Property Name="SqlDataType" Value="Int"/>
            <Property Name="Length" Value="50"/>       <!-- char/varchar/binary/varbinary -->
            <Property Name="Precision" Value="38"/>    <!-- decimal/numeric -->
            <Property Name="Scale" Value="10"/>        <!-- decimal/numeric/datetimeoffset/etc. -->
          </Element>
          <!-- OR: reference to a user-defined type -->
          <Relationship Name="References">
            <Entry>
              <References ExternalSource="BuiltIns" Name="[sys].[int]"/>
            </Entry>
          </Relationship>
        </Relationship>
      </Element>
    </Element>
  </Model>
</DataSchemaModel>
```

DACPAC type names are PascalCase SQL keyword strings (`Int`, `NVarChar`, `DateTime2`,
`UniqueIdentifier`, `HierarchyId`, etc.) stored in `SqlDataType`.

#### 1.3.3 BCP native row format (`bcp -n`) `[CORROBORATED]`

Each `.BCP` file is a sequence of rows with no row-count header.  Column encoding
within each row:

| Column class | Encoding |
|---|---|
| Fixed numeric / temporal (`int`, `bigint`, `real`, `float`, `datetime`, …) | Raw little-endian bytes, no prefix, no null indicator |
| `decimal` / `numeric` | 1-byte signed indicator (−1=null, precision=non-null) + 19-byte `SQL_NUMERIC_STRUCT` (`[precision][scale][positive][int128 LE]`) |
| `varchar(n)`, `nvarchar(n)`, `varbinary(n)`, `text`, `ntext`, `image` | `uint16 LE` length prefix; `0xFFFF` = null |
| `char(n)`, `nchar(n)`, `binary(n)` | `uint16 LE` length prefix; `0xFFFF` = null (fixed-length types still use a variable-length prefix for nullable columns in `bcp -n` output) |
| `bit` | 1 byte (`0x00` or `0x01`); preceded by 1-byte signed null indicator (−1=null, 1=non-null) |
| `date` | 3 bytes LE, days since `0001-01-01`; Arrow `date32` epoch is `1970-01-01` (offset −719,162 days applied) |
| `uniqueidentifier` | 16 bytes, mixed-endian Microsoft GUID |
| `xml`, `sql_variant` | Not exported by `bcp -n`; absent from BACPAC |

**G-BACPAC-01 `[EMPIRICAL]`**: `char(N)`, `nchar(N)`, `binary(N)` columns use a
`uint16 LE` length prefix (matching `varchar`/`nvarchar`/`varbinary`) rather than
a fixed N-byte body, even though they are nominally fixed-length.  Confirmed by
byte inspection of `typecoverage.bacpac` (generated from SQL Server 2022) — a
`char(10)` column always emits `0x0A 0x00` prefix (length=10) followed by 10 bytes,
or `0xFF 0xFF` for null.

**G-BACPAC-02 `[EMPIRICAL]`**: `date` values in BCP native output are stored as
days since `0001-01-01` (SQL Server epoch), not as days since `1970-01-01` (Unix
epoch).  PyArrow `date32` uses the Unix epoch.  Offset applied:
`arrow_days = sql_days − 719162`.  Confirmed by round-trip comparison between
`bcp -n` output and a live SQL Server `SELECT CAST(DATEDIFF(DAY,'0001-01-01',val) AS INT)`.

#### 1.3.4 RAM vs streaming for cloud-backed BACPAC `[CORROBORATED]`

`zipfile.ZipFile` requires a seekable file-like object.  When the source is a
cloud `BakReader` (not a local `Path`):

- If `reader.size ≤ 1 GiB`: the entire file is loaded into `io.BytesIO` before
  opening the ZIP.
- If `reader.size > 1 GiB`: the reader is wrapped by `_SeekableFromReader`
  (`io.RawIOBase`) and then `io.BufferedReader`.  `seek()` is implemented via
  `read_at(pos, ...)`.

The 1 GiB threshold is `_RAM_LOAD_THRESHOLD = 1 << 30` in `mssqlbak/bacpac.py`.
External corroboration covers the ZIP central-directory / seekability constraint
and DacFx/Azure export temporary-disk pressure. The exact 1 GiB cutoff is an
mssqlbak implementation choice.

---

