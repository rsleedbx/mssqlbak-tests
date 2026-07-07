# XTP Checkpoint — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `XTP_CHECKPOINT`
**Set by:** `read_table_rows` (`mssqlbak/rows.py:860`) when memory-optimized filegroup tables
**Catalog signal:** memory-optimized filegroup present in backup
**Decode entry point:** `xtp.py` (`read_xtp_rows`, `scan_cfp_log_records`)

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

---

