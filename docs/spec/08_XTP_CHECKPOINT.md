# XTP Checkpoint — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `XTP_CHECKPOINT` (spec abstraction, not a code symbol)
**Set by:** routing checks `table.is_memory_optimized` (`extract.py:494`, `catalog.py:2205`).
Detection: sysrowsets `status & 0x100` (XTP index rowsets) AND all alloc-unit page
pointers null (no B-tree pages exist).
**Catalog signal:** `sysrowsets.status & 0x100` set on at least one rowset for the table;
NOT "memory-optimized filegroup present" (detected per-table, not per-filegroup).
**Decode entry point:** `xtp.py: decode_cfp_log_records` (for MSSQLBAK-compressed backups)
or `xtp.py: scan_cfp_blocks` (for uncompressed backups with .cfp files)

---

## 2. Initialization

No ordinary 8 KB page structure. Rows are serialized in XTP checkpoint DATA files
and transaction-log-style record streams; DELTA files carry deletes. Index
definitions are persisted, but indexes are rebuilt in memory at load time.
Introduced SQL Server 2014.

---

## 3. Record structure

#### V04 — In-Memory OLTP (Hekaton/XTP) table storage `[EMPIRICAL]`

SQL Server 2014+ supports memory-optimized tables (`CREATE TABLE … WITH
(MEMORY_OPTIMIZED = ON)`).  Durable data for these tables is stored in **XTP
checkpoint file pairs**, not in the standard B-tree page stream that mssqlbak
reads.

**Status (2026-07): implemented for provably complete insert-only record sets.**
Detection uses two catalog signals: (a) the object has at least one XTP index
rowset in `sysrowsets` (status bit `0x100` set for hash/range XTP indexes), and
(b) all alloc units of the chosen data rowset have null page pointers.

For MSSQLBAK-compressed backups, `scan_cfp_log_records` scans consecutive
non-page decompressed chunks for framed XTP insert records:

```
[u32 size][u32 flags=0x8000_00LB][u32 seq][u32 marker][u32 pad=0][payload]
```

Rows are emitted only when the table is provably complete: either a dense
`IDENTITY(1,1)` key enumerates `{1..N}`, or the per-table `seq` run is gap-free
and the payloads fingerprint exactly one table schema. `AdventureWorks2016_EXT`
lands all seven memory-optimized tables under those gates.

#### V04a — Fixed-section alignment padding `[EMPIRICAL]`

The fixed (non-variable) section of a record is packed widest-slot-first, then
zero-padded up to a multiple of the **widest fixed slot width** (its natural
alignment, ≤ 8).  A fixed-only record's length therefore equals
`round_up(sum(fixed_widths), max_fixed_width)`, and any trailer bytes are zero.
Evidence: `DemoSalesOrderDetailSeed` (`smallint` + 4×`int`, widest 4) pads
fw=18 → 20; `ColdRoomTemperatures` (5×8-byte + `int`, widest 8) pads 44 → 48;
`DemoSalesOrderHeaderSeed` (`datetime` + 6×`int`, widest 8) is already 32-aligned.
Requiring the exact padded length (not merely `≥ fw`) keeps the record width a
per-table fingerprint for LB→table discrimination (`_xtp_fixed_record_consistent`).

#### V04-blocks — On-disk 4 KB checkpoint block formats `[EMPIRICAL]`

Source: `xtp.py` module docstring and `_is_compact_data_block`.

Two block types appear in XTP checkpoint data:

**Compact block** (`block_type = 0x0001000d` or `0x0001000e`):

```
[0:4]   u32 LE  block_type  (0x0001000d or 0x0001000e)
[4:8]   u32 LE  block_size  = 0x1000 (4096)
[8:12]  u32 LE  block_size  = 0x1000 (data blocks); 0 = file-header block
[12:16] u32 LE  num_records
[16:28]         metadata (checksum / sequence info)
[28:32] u32 LE  data_end_offset  (offset from byte 40 to end of all records)
[32:36] u32 LE  data_size
[36:40]         flags / unused
[40 ..]         records, each:
    [+0:4]  u32 LE  payload_size
    [+4:8]  u32 LE  flags (low byte = table discriminator index)
    [+8:12] u32 LE  = 0x00000001
    [+12:16] u32 LE seq_num
    [+16:20] u32 LE = 0
    [+20 ..] payload bytes  (payload_size bytes)
```

File-header blocks have 0 in the second block-size field (`bytes[8:12]`).
Manifest blocks contain `/$HKv2` in bytes 0–63 and are skipped.

**WAL-style block** (`block_type = 0x00030050`):

```
[0:4]    u32 LE  block_type  = 0x00030050
[4:0xFF]         block header / metadata
[0xFF]   u8      separator = 0x03
[0x100:0x104] u32 LE  flags (low byte = table discriminator index)
[0x104:0x108] u32 LE  = 0x00000001
[0x108:0x10A] u16 LE  payload_size
[0x10A ..]    payload bytes
```

#### V04-preamble — Checkpoint segment demux `[EMPIRICAL]`

Source: `xtp.py: _CKPT_PREAMBLE_SIG = b"\x01\x64\x01\x00\x01\x00\x01\x00"`.

In MSSQLBAK-compressed backups, XTP blocks are embedded in the decompressed
non-page stream.  The stream is chunked by checkpoint-segment header blocks
that begin at 512-aligned offsets with the 8-byte preamble signature.
`scan_cfp_log_records` scans for this signature (aligned-only hits) and uses
the detected segment boundaries to splice straddle records.

**CFP log-record format** (MSSQLBAK-compressed backups):

```
[+0:4]  u32 LE  size        (payload size, NOT including the 20-byte header)
[+4:8]  u32 LE  flags       0x8000_00LB where LB = table discriminator byte
[+8:12] u32 LE  seq         sequence number (unique per table)
[+12:16] u32 LE marker
[+16:20] u32 LE = 0         (padding)
[+20 ..] payload bytes      (size bytes)
stride = 20 + size
```

Header comes FIRST; payload FOLLOWS (earlier "payload before size" description
was wrong — proved byte-exact by anchor-scan verification).

#### V04b — Duplicate seq resolution (metadata twins) `[EMPIRICAL]`

A single `seq` can appear more than once in the stream with **different**
payloads: the genuine insert row plus a checkpoint metadata twin (a mostly-zero
payload whose variable-offset array is all zero, carrying a `"TM"` marker), and,
across checkpoint copies, an earlier corrupt copy plus a later good one.
`scan_cfp_log_records` keeps every distinct payload per `seq`; the completeness
gate then resolves each `seq` to the **last consistent** copy — inconsistent
twins are skipped (they fail the per-table structural check), and among
consistent copies the later checkpoint copy supersedes the earlier one.  This
single rule fixes both `AdventureWorks2016_EXT.SalesOrderHeader_inmem` (later
copy of seq 21608 is the inconsistent twin → keep the earlier good copy) and
`WideWorldImporters-Full.VehicleTemperatures` (earlier copy of a `FullSensorData`
row is corrupt → keep the later good copy).

#### V04c — Completeness gating `[EMPIRICAL]`

Source: `xtp.py: _seq_complete_rows`, `_dense_identity_rows`.

XTP rows are emitted only when the table is **provably complete** — the
scanned rows account for all expected inserts with no gaps.  Two gating
strategies are applied:

1. **Dense IDENTITY gate** (`_dense_identity_rows`): if the table has an
   `IDENTITY(1,1)` primary key column with no gaps and the scanned seqs form
   exactly `{1, 2, …, N}`, the table is complete.
2. **Seq-contiguity gate** (`_seq_complete_rows`): the per-table `seq` values
   form a contiguous run with no gaps, and the fixed-section of each payload
   passes `_xtp_fixed_record_consistent` (length equals `round_up(fixed_width, max_width)`).

Both gates fail gracefully — if neither is satisfied, the table is omitted
from output rather than returning potentially incomplete data.

**Fixed-section alignment** (`_xtp_fixed_align`): XTP fixed columns are
ordered widest-slot-first (descending `max_length`, then ascending `colid`),
then zero-padded to the next multiple of the widest column's width (≤ 8).

**Variable-column payload** in XTP rows: each variable-length column has an
8-byte VL descriptor `[2B flags][2B start_offset][2B end_offset][2B trailer]`
after the fixed section.  NULL: `start_offset == end_offset`.  Variable data
follows all descriptors.

---

