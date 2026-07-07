## 9. Fuzzy / Dirty Backup Structures

### 9.1 Log tail region `[CORROBORATED]`

A "fuzzy" (online) backup appends a transaction log tail after the last data
page.  SQL Server's crash-recovery would replay and undo dirty writes using this
tail.  `logtail.py` extracts it instead to suppress uncommitted rows and restore
ghost-deleted rows without a live SQL Server.

All offsets in this section are confirmed against SQL Server 2022 using
`sys.fn_dump_dblog` on `dirtycoverage_uncommitted.bak`, `dirtycoverage_delete.bak`,
`dirtycoverage_update.bak`, and `dirtycoverage_wide.bak`.

#### 9.1.1 Region discovery

```
rfind("MSLS")              → msls_pos
rfind("APAD", 0, msls_pos) → apad_pos
log_start = (apad_pos + 4096) & ~4095   # first 4096-aligned block after APAD
log_end   = msls_pos
```

`APAD` and `MSLS` are 4-byte ASCII markers embedded in the MTF stream.
`MSLS` is followed by `MQCI` and `SCIN` markers within the same block.
The log tail is absent for clean (offline) backups; `find("MSLS") == -1` in that case.

#### 9.1.2 Block structure

The log tail is divided into 4 096-byte blocks:

```
byte[0]        block status:
               0x50 = opening block (record area starts at byte 0x48)
               0x40 = continuation block (no header; records continue from previous block)
byte[0x0C–0x0F]  VLF sequence number  (uint32 LE)   — opening blocks only
byte[0x10–0x13]  block offset in 512-byte sectors (uint32 LE) — opening blocks only
byte[0x48–…]   record area (opening blocks)
byte[1–…]      record continuation (continuation blocks; byte[0] is the status byte, not payload)
```

At each 512-byte sub-sector boundary within a block (positions 512, 1024, …,
3584 inside the 4 096-byte block), the original data byte is overwritten by
the sector-status value `0x40`.  For NVARCHAR/UTF-16-LE data this position
corresponds to a padding zero and is safely substituted with `0x00`.  For
VARCHAR/binary data the original byte is unrecoverable; `0x00` is used as a
best-effort approximation (one byte per 512-byte window).

Records are **8-byte aligned** within a block.  The scanner advances in
8-byte steps from position `0x48` in opening blocks and from position `0` in
continuation blocks.

#### 9.1.3 Log record common header

All tracked log records have `byte[0x0E] == 0x02` (LCX context = XACT):

```
byte[0x00–0x07]  record length fields (not used for extraction)
byte[0x08–0x0B]  prev_blk_off  uint32 LE  block_offset of previous record for this xact
                                           (0 if no prior record in the capture window)
byte[0x0C–0x0D]  (unused by parser)
byte[0x0E]       LCX   = 0x02  (context: all tracked records)
byte[0x0F]       SUBTYPE:
                   0x04 = DML (INSERT or DELETE)
                   0x00 = TX-control or in-place UPDATE
byte[0x10–0x15]  xact_id  6 bytes LE  transaction ID
byte[0x16]       discriminant  (meaning depends on SUBTYPE — see §9.1.4)
byte[0x18–0x1B]  page_id   uint32 LE  (DML + MODIFY records)
byte[0x1C–0x1D]  file_id   uint16 LE  (DML + MODIFY records)
byte[0x1E–0x1F]  slot_id   uint16 LE  (DML + MODIFY records)
```

LSN for a record at position `pos` in an opening block with `vlf_seq` / `blk_offset`:
```
lsn = (vlf_seq, blk_offset, pos − 0x48)
```

#### 9.1.4 Operation codes

| SUBTYPE | byte[0x16] | Operation | Abbrev |
|---------|-----------|-----------|--------|
| 0x04 | 0x02 | LOP_INSERT_ROWS — INSERT (committed or uncommitted) | INSERT |
| 0x04 | 0x03 | LOP_DELETE_ROWS — DELETE / ghost (committed or uncommitted) | DELETE |
| 0x04 | 0x04 | LOP_MODIFY_ROW (LOB blob slot, TEXT_MIX page) | MODIFY_LOB |
| 0x00 | 0x80 | LOP_BEGIN_XACT — transaction begin | BEGIN |
| 0x00 | 0x81 | LOP_COMMIT_XACT — transaction commit | COMMIT |
| 0x00 | 0x82 | LOP_ABORT_XACT — transaction abort/rollback | ABORT |
| 0x00 | 0x04 | LOP_MODIFY_ROW (regular data-page slot) | MODIFY |

`MODIFY_LOB` and `MODIFY` have identical payload layouts; both are accepted.

Empirically measured record sizes (SQL Server 2022, 60-byte FixedVar row):
- BEGIN: 120 bytes
- COMMIT: 84 bytes
- INSERT: 160 bytes
- DELETE: 156 bytes
- MODIFY: 184 bytes

#### 9.1.5 INSERT record payload

```
byte[0x40–0x41]  row_len   uint16 LE  number of row bytes
byte[0x48–…]     row_bytes  SQL row (FixedVar / CD / LOB node format)
```

Row bytes may overflow into continuation blocks; `_read_log_payload` handles this
by skipping the status byte (`byte[0]`) of each successive block.

#### 9.1.6 DELETE record payload (before-image)

```
byte[0x40–0x41]  row_len   uint16 LE  length of before-image row bytes
byte[0x42–0x43]  (purpose unconfirmed; ignored)
byte[0x44–…]     row_bytes  before-image SQL row (same FixedVar / CD format as INSERT)
```

The before-image is needed because ghost records have their `pminlen` zeroed,
making them undecodable via the normal FixedVar decoder.

#### 9.1.7 MODIFY record payload (UNDO + REDO)

```
byte[0x38–0x39]  row_start   uint16 LE  byte offset in row where modification begins
                              (fall back to byte[0x44] when (record_pos+0x38) % 512 == 0,
                               i.e. when this field lands on a sector-status boundary)
byte[0x3A–0x3B]  undo_size   uint16 LE  length of before-image bytes
byte[0x3C–0x3F]  (zeros, unused)
byte[0x40–0x41]  undo_size   uint16 LE  (duplicate; either copy is valid)
byte[0x42–0x43]  redo_size   uint16 LE  length of after-image bytes
byte[0x44–0x45]  fixed_end   uint16 LE  fallback for row_start (coincides when update
                                          starts at the first variable-length field)
byte[0x46–0x4B]  (internal, not used)
byte[0x4C : 0x4C+undo_size]               UNDO data (before-image at row[row_start:])
byte[0x4C+undo_size : 0x4C+undo_size+redo_size]  REDO data (after-image)
```

Row reconstruction:
```
# UNDO (uncommitted UPDATE — restore original):
before_row = row[:row_start] + undo_data + row[row_start+redo_size : last_var_end(row)]

# REDO (committed UPDATE — apply after-image):
after_row  = row[:row_start] + redo_data + row[row_start+undo_size : last_var_end(row)]
```

#### 9.1.8 Block-boundary record handling

Records that overflow from one block into the next are handled in two distinct ways:

**Payload overflow** (`_read_log_payload`): when a record's payload (e.g. the row bytes
of a large INSERT) overflows the current 4096-byte block, reading continues at
`byte[1]` of the next block (skipping the status byte at `byte[0]`).

**Record-header straddle**: a record starting at positions 4072 or 4080 of block N has
its identifying fields (`LCX` at `+0x0E`, `SUBTYPE` at `+0x0F`) still within block N,
but its payload fields (`xact_id` at `+0x10`, `page_id` at `+0x18`, `slot_id` at `+0x1E`)
fall at the start of block N+1.  These are detected by stitching the last 32 bytes of
block N with the first 32 bytes of block N+1.

Complete records can also **start inside continuation blocks** (when the overflow from
the previous opening block leaves room).  These are scanned with the same 8-byte-aligned
pass from `byte[0]` of the continuation block.

**Legacy (SUBTYPE=0x00) INSERT/DELETE in continuation blocks** `[EMPIRICAL]`: some
backups (SS2017, and observed on SS2019) log INSERT/DELETE with `SUBTYPE=0x00` (the same
value as TX-control records) rather than `0x04`, disambiguated by the LOP code `0x3e` at
`+0x02`.  `iter_log_records` already recognises this "legacy DML" form in opening blocks;
the continuation-block scanner (`_iter_cont_records`) must apply the **identical** rule in
both its per-block pass and the block-boundary straddle, gated on the absence of any
`SUBTYPE=0x04` DML.  Without it, the history-table `INSERT`s of an uncommitted temporal
`UPDATE` that spill past the first opening block are never marked dirty and the rolled-back
history rows leak into the output.  When a straddling legacy INSERT's `xact_id[0]` lands on
block N+1's sector-status byte (`0x40`/`0x50`), it is recovered from the last valid
`xact_id` seen in block N (the remaining 5 bytes must match).

**Temporal-UPDATE history-page recovery** `[EMPIRICAL]`: a system-versioned `UPDATE` logs,
per row, a `MODIFY` of the current-table page followed by an `INSERT` of the prior version
into the history table.  When an INSERT's `page_id` first byte falls on a 512-byte
sector-status boundary it is overwritten by the framing byte, so a history page such as
`0x148` mis-reads as `0x140` — which *coincides* with the interleaved current-table page.
Recovery therefore tracks the **last INSERT page** per transaction separately from the
generic last-page-per-transaction (which holds the `MODIFY` target), so the corrupted
history INSERT is attributed to the previous history page rather than the current-table
page.  Recovery is restricted to INSERTs; DELETE targets are unrelated to prior inserts.
Evidence: `dirtycoverage_temporal_update` (`temporal_test_history` → 0 rows after the
uncommitted UPDATE rolls back) — SS2017/2019/2022/2025.

#### 9.1.9 Transaction analysis

Two categories of uncommitted transactions are identified for dirty-row suppression:

**In-window transactions**: have a `BEGIN` record AND at least one DML record in the
capture window, with no matching `COMMIT` or `ABORT`.  False-positive BEGINs (the byte
pattern `02 00 … 80` can appear inside record payloads) are filtered out by requiring
that at least one DML record's `prev_blk_off` falls within the capture window.

**Long-running transactions**: have DML records in the capture window but **no BEGIN and
no COMMIT**.  Their `BEGIN` resides in an earlier VLF before the window; if they had
committed, their `COMMIT` would also be in the window (the log is sequential).  The
absence of both, combined with at least one in-window `prev_blk_off`, confirms the
transaction was active at backup time.

**MinLSN limitation**: if a transaction's `INSERT` record has a `prev_blk_off` that
predates the earliest block in the capture window, the record cannot be reliably
attributed.  Those rows silently escape suppression — the xfailed
`dirtycoverage_large_dirty` fixture documents this as an inherent limit of log-tail
analysis without the full prior VLF history.

---

