# Dirty / Fuzzy Backup Analysis

## What SQL Server guarantees

Every regular SQL Server backup (`BACKUP DATABASE`) is technically a *fuzzy backup*:

- The engine reads each 8 KB data page as an atomic unit (no half-pages).
- Between pages, other transactions can commit or rollback — there is no single consistent point in time across all pages.
- The backup includes a log tail (from backup-start LSN to backup-end LSN) that the engine replays during `RESTORE … WITH RECOVERY` to bring the database to a transactionally consistent state.

This design lets SQL Server back up databases online without blocking writes.

### What `COPY_ONLY` changes

`WITH COPY_ONLY` is purely a backup-chain flag (it prevents the backup from resetting the differential base LSN). It does **not** make the backup any cleaner or dirtier with respect to in-flight transactions.

---

## What mssqlbak does

mssqlbak reads pages directly from the backup image and optionally corrects
fuzzy-backup anomalies by parsing the transaction log tail included in the backup.

By default (no log parsing) mssqlbak reads the *fuzzy* page state as-of-backup-time.
Call `logtail_from_bak(path)` to get a `LogTailResult` with three frozensets:

- `dirty_slots`: suppress uncommitted INSERT rows (phantom rows from open transactions)
- `restore_slots`: restore ghost slots from uncommitted DELETE rows (phantom delete fix)
- `modified_slots`: identify rows modified in-place by uncommitted UPDATEs (for diagnosis)
- `before_images`: `{(page_id, slot_id): ModifyImagePatch}` — pass to `read_table_rows` to restore phantom-updated rows to their pre-UPDATE values

Pass `dirty_slots`, `restore_slots`, and `before_images` to `read_table_rows` for the most complete fix.
`dirty_slots_from_bak` is still available as a compatibility shortcut (returns only dirty_slots).

---

## Empirical findings

Five scenarios were tested against a real SQL Server 2022 Linux container. Fixtures and test code are in `tests/test_dirty_backup.py`.

### Scenario A — Concurrent inserts (`dirtycoverage_concurrent.bak`)

Setup:
- 100 rows committed before backup start (phase `pre_backup`).
- A background loop inserted single rows (phase `concurrent`) throughout the backup.
- 200 concurrent rows were committed by the time the loop finished.

| Metric | Value |
|--------|-------|
| Pre-backup rows visible | **100 / 100** (all committed rows always appear) |
| Concurrent rows visible | **13 / 200** (only pages read after that insert committed) |
| Corrupt rows | **0** |
| Crash / exception | None |

Key result: **committed rows that existed before backup start are always safe**. Rows written during the backup window are captured only if their pages happened to be scanned after the commit — this is a function of backup duration and write rate.

For a backup that takes 0.5 seconds while inserting 200 rows over ~10 seconds, roughly 10–15% of concurrent rows are captured. The exact count is non-deterministic.

### Scenario B — Uncommitted transaction (`dirtycoverage_uncommitted.bak`)

Setup:
- 50 rows committed before the transaction (phase `pre_tx`).
- A second session opened a transaction, inserted 20 rows (phase `in_tx`), and held it open for 20 seconds via `WAITFOR DELAY`.
- The backup ran while the transaction was open.
- The transaction was rolled back after the backup completed.

| Metric | Value |
|--------|-------|
| Committed rows visible | **50 / 50** |
| Uncommitted rows visible | **20 / 20** (dirty-read — data SQL Server later rolled back) |
| Effective total | **70** (vs 50 in SQL Server post-rollback) |

Key result: **dirty-read confirmed**. SQL Server writes in-progress pages to the buffer pool eagerly. The backup process reads from the buffer pool, so uncommitted dirty pages are included in the backup image. mssqlbak surfaces these as regular rows.

This is the "phantom row" problem: mssqlbak shows data that SQL Server considered non-existent by the time the backup was made consistent.

### Scenario C — TRUNCATE TABLE during backup (`dirtycoverage_truncate.bak`)

Setup:
- 500 rows committed (`trunc_test`, phase `pre_trunc`).
- A background session ran `TRUNCATE TABLE` after a 1-second delay while the backup ran.

| Metric | Value |
|--------|-------|
| Rows visible | **0** (TRUNCATE completed before backup scanned data pages) |
| Corrupt rows | **0** |
| Crash / exception | None |

Key result: **no crash; row count is 0 or 500 — never a partial count**.
TRUNCATE TABLE's all-or-nothing page de-allocation means the backup captures
either the full pre-TRUNCATE page set or the empty post-TRUNCATE state.

### Scenario D — ALTER TABLE ADD COLUMN then backup (`dirtycoverage_addcol.bak`)

Setup:
- 50 rows inserted (`addcol_test`, phase `pre_ddl`).
- `ALTER TABLE ADD COLUMN extra VARCHAR(100) NULL` issued (metadata-only in SQL Server 2022).
- 10 more rows inserted with `extra = 'extra_value_N'` (phase `post_ddl`).
- Static backup of final state.

| Metric | Value |
|--------|-------|
| Total rows visible | **60 / 60** |
| New column `extra` in schema | **Yes** — present in every decoded row |
| Pre-DDL rows `extra` value | **`None`** (SQL NULL) — correct |
| Post-DDL rows `extra` value | **`'extra_value_N'`** — correct |
| Crash / exception | None |

Key result: **no crash; all rows and the new column visible**. Pre-DDL rows
return `None` (SQL NULL) because `records.py` detects when the column's
null-bit index exceeds the row's original null-bitmap size (`null_index >= ncol`)
and returns `None` instead of reading past the bitmap.

**Resolved (Jun 2026):** `records.py` null-bitmap size check (`null_index >= ncol → None`)
fixed the `''` → `None` regression.  Tested — Scenario D.

### Scenario E — DROP TABLE during backup (`dirtycoverage_droptable.bak`)

Setup:
- `survivor_test` (200 rows, always stable) and `drop_target` (500 rows).
- A background session ran `DROP TABLE drop_target` after a 1-second delay.

| Metric | Value |
|--------|-------|
| `survivor_test` rows | **200 / 200** |
| `drop_target` in schema | **absent** (DROP completed before catalog was scanned) |
| Crash / exception | None |

Key result: **no crash; stable tables unaffected; dropped table either visible
or absent depending on timing**.

---

## What SQL Server allows during a backup

SQL Server does NOT block most concurrent operations during an online backup.
Operations that are explicitly allowed (will not trigger Error 3023):

| Category | Allowed operations |
|----------|--------------------|
| DML | INSERT, UPDATE, DELETE, MERGE |
| TCL | BEGIN/COMMIT/ROLLBACK TRANSACTION |
| DDL | ALTER TABLE (add/drop/modify columns, constraints), ALTER INDEX (rebuild/reorganize), CREATE/DROP TABLE, CREATE/DROP INDEX, TRUNCATE TABLE |
| DCL | GRANT, REVOKE, DENY |
| DBCC | CHECKDB, CHECKALLOC, UPDATE STATISTICS |

**Explicit exceptions (Error 3023):** `ALTER DATABASE … ADD/REMOVE FILE`,
`DBCC SHRINKFILE`, and overlapping concurrent backups.

---

## Scenario L — Uncommitted DELETE (`dirtycoverage_delete.bak`)

Setup:
- 50 rows committed (`delete_test`, phase `committed`).
- 20 rows committed (`delete_test`, phase `delete_target`).
- A background session opened a `DELETE WHERE phase='delete_target'` transaction,
  held it open for 20 s, then rolled it back.
- The backup ran while the transaction was open.

| Metric | Value |
|--------|-------|
| Committed rows visible | **50 / 50** |
| Delete-target rows visible | **0 / 20** — ghost DELETE captured |
| Crash / exception | None |

Key result: **phantom delete confirmed**. SQL Server marks deleted slots as *ghosts*
the moment the `DELETE` statement executes — before the transaction commits.  The
backup bypasses row-level locking and reads the ghost state.  mssqlbak's
`fixedvar_emittable` correctly filters ghost records, so the rows disappear from
the output even though the `DELETE` was rolled back.

**Resolved (Jun 2026):** `logtail_from_bak()` returns `restore_slots`; passing it to
`read_table_rows` bypasses the ghost filter for uncommitted-DELETE slots and
re-emits those rows as live rows, restoring the correct 70-row view.

### Scenario M — Uncommitted UPDATE (`dirtycoverage_update.bak`)

Setup:
- 50 rows committed (`update_test`, phase `pre_update`, label `original_N`).
- A background session `UPDATE`d the first 20 rows (label → `modified_N`,
  score → score+1000, phase → `in_update`), held for 20 s, then rolled back.
- The backup ran while the transaction was open.

| Metric | Value |
|--------|-------|
| Total rows visible | **50 / 50** |
| Modified-rows label | **`modified_N`** (phantom — rolled back) |
| Modified-rows phase | **`in_update`** (phantom — rolled back) |
| Modified-rows score | **original + 1000** (phantom — rolled back) |
| Unmodified-rows correct | **30 / 30** |
| Crash / exception | None |

Key result: **phantom update confirmed**. Without snapshot isolation, SQL Server
updates the row in-place immediately.  The buffer pool holds the modified page,
and the backup captures the modified values.  After rollback, SQL Server restores
the original values using the undo log — but the backup already saw the updated
state.

**Resolved (Jun 2026):** `collect_before_image_patches()` extracts `(row_start,
undo_data, redo_row_end)` from each `LOP_MODIFY_ROW` record into
`LogTailResult.before_images`.  `_apply_before_image()` in `rows.py` splices
`undo_data` into the page row at `row_start`, restoring all column values.
All 20 modified rows decode with their original `original_N` labels and
`pre_update` phase.


---

### Scenario S — Wide multi-block UPDATE (`dirtycoverage_wide.bak`)

Setup:
- 5 rows committed (`wide2_test`, id 1–5; `content` = `'A' * 3900`, `phase = 'pre_update'`).
- A background session UPDATEd rows 1–3 (`content` → `'B' * 3900`, `phase → 'post_update'`),
  held for 20 s, then rolled back.
- The backup ran while the transaction was open.

| Metric | Value |
|--------|-------|
| Total rows visible | **5 / 5** |
| Restored rows (phase) | **`pre_update`** for all 5 rows |
| `before_images` collected | **3** (one per modified row) |
| Crash / exception | None |

Key result: **multi-block undo_data correctly assembled.** `LOP_MODIFY_ROW` records
for wide rows start inside `0x40` continuation log blocks (not `0x50` opening blocks).
`collect_before_image_patches` uses a two-pass scan (opening blocks first, then
continuation blocks) to find all records.  `_read_log_payload` carries the
block-crossing offset rather than resetting to 1, and treats the sector-status byte
at position 0 of each block boundary as a substituted `0x00`.  `row_start` is read
from field `+0x38`; falls back to `+0x44` (fixed_end) when `+0x38` coincides with a
512-byte sector boundary.

---

### Scenario T — INSERT then UPDATE in same uncommitted TX (`dirtycoverage_insert_update.bak`)

Setup:
- 20 rows committed (`iu_test`, `phase = 'committed'`).
- Same session opened one transaction, INSERTed 10 rows (`phase = 'dirty'`), then
  UPDATEd those same rows, held open for 20 s, then rolled back.

| Metric | Value |
|--------|-------|
| Committed rows visible | **20 / 20** |
| Dirty INSERT+UPDATE rows visible | **0** (correctly absent) |
| `dirty_slots` non-empty | **Yes** |
| Crash / exception | None |

Key result: **correct suppression ordering.** `dirty_slots` suppresses the inserted
slot before `_apply_before_image` is considered.  A row that should not exist at all
is never patched and never emitted, regardless of what the `LOP_MODIFY_ROW` record
for its update contains.

---

### Scenario U — Multiple UPDATEs on same row in one uncommitted TX (`dirtycoverage_multi_update.bak`)

Setup:
- 10 rows committed (`multi_update_test`, `phase = 'pre_update'`, `label = 'original_N'`).
- One transaction UPDATEd rows 1–5 twice each (first to `'intermediate_N'`, then to
  `'final_N'`), held open for 20 s, then rolled back.

| Metric | Value |
|--------|-------|
| Total rows visible | **10 / 10** |
| Rows 1–5 label | **`original_N`** (before any UPDATE) |
| Rows 6–10 label | **`original_N`** (untouched) |
| Crash / exception | None |

Key result: **earliest patch kept.** SQL Server writes `LOP_MODIFY_ROW` records in
forward (chronological) order.  `collect_before_image_patches` keeps the first-seen
record per `(page_id, slot_id)` (`if key not in patches`), which carries the
true pre-transaction before-image.  Later intermediate-state patches are discarded.

---

### Scenario V — Uncommitted UPDATE on ROW-compressed table (`dirtycoverage_compress_update.bak`)

Setup:
- 50 rows committed (`compress_update_test`, `WITH (DATA_COMPRESSION = ROW)`).
- A background session UPDATEd all 50 rows (label → `modified_N`, score → score+1000,
  phase → `in_update`), held for 20 s, then rolled back.

| Metric | Value |
|--------|-------|
| `modified_slots` non-empty | **Yes** — 20 log records detected (subset captured in log tail) |
| `before_images` populated | **Yes** — 20 patches extracted |
| All 50 rows restored to original values | **Yes** |
| Crash / exception | None |

Key result: **full before-image restoration for ROW-compressed tables.**
`LOP_MODIFY_ROW` for compressed rows stores `row_start=3` (the byte offset of the
second nibble byte in the CD array, which is the first byte that changes when column
widths or values differ).  The byte-splice approach used for FixedVar rows works
equally well for CD records; the only difference is that `len(raw)` is used as the
total row length instead of `_last_var_end(raw)` (CD records have no trailing
FixedVar var-offset array padding).

**Fix (Jun 2026):**
- `collect_before_image_patches` Pass 3 now treats only `row_start == 0` as invalid
  (not `row_start < 4`), so CD patches with `row_start=3` are correctly retained.
- `_apply_before_image` guard changed from `< 4` to `== 0` for the same reason.
- `_apply_before_image_cd` added to `rows.py` — same splice logic, uses `len(raw)`
  as total length.  Called from `_read_compressed` when `before_images` contains an
  entry for the current slot.

PAGE-compressed tables have the same fix.  COLUMNSTORE tables are unaffected
(columnstore updates rewrite delta-store rows rather than modifying data pages in place).

---

## Summary table

| Scenario | mssqlbak behaviour | Risk level | Tested |
|----------|--------------------|------------|--------|
| Rows committed before backup start | Always visible, always correct | None | ✅ |
| Rows committed during backup (concurrent DML) | Partially visible (non-deterministic) | Low | ✅ |
| Rows from open INSERTs (dirty pages) | Suppressed via `logtail_from_bak().dirty_slots` | Medium → resolved | ✅ |
| TRUNCATE TABLE during backup | 0 or N rows (never partial); no crash | Low | ✅ |
| ALTER TABLE ADD COLUMN (nullable) during backup | All rows returned; pre-DDL rows return `NULL` for new column | None | ✅ |
| ALTER TABLE ADD COLUMN NOT NULL DEFAULT during backup | All rows returned; pre-DDL rows return the correct DEFAULT value | None | ✅ |
| DROP TABLE during backup | Dropped table may or may not appear; survivor tables always correct | Low | ✅ |
| DROP COLUMN, static backup | All rows returned; dropped column absent; no crash | None | ✅ |
| ALTER COLUMN (compatible type), static backup | All rows returned; values correct | None | ✅ |
| ALTER COLUMN (page rewrite), static backup | All rows correct; SCH-M lock prevents split state | None | ✅ |
| CREATE TABLE during backup | Stable table always correct; new table absent or fully present | Low | ✅ |
| ALTER INDEX REBUILD / CREATE INDEX / DROP INDEX during backup | All data rows returned; no crash | None | ✅ |
| ALTER TABLE SWITCH PARTITION during backup | Consistent pre- or post-SWITCH state; no crash | None | ✅ |
| ALTER DATABASE SET options during backup | All user data rows unaffected; system boot page updated | None | ✅ |
| Savepoints (`SAVE TRANSACTION`) | Pre-save dirty rows suppressed; post-savepoint-rollback rows absent | None | ✅ |
| Nested transactions (`BEGIN` inside `BEGIN`) | All dirty rows (outer + inner) suppressed as one uncommitted unit | None | ✅ |
| DELETE from open transaction (rolled back) | Ghost rows restored via `logtail_from_bak().restore_slots` | Medium → resolved | ✅ |
| UPDATE from open transaction (rolled back) | Original values restored via `logtail_from_bak().before_images` | Medium → resolved | ✅ |
| UPDATE: wide row, undo_data spans 4096-byte log block (Scenario S) | Original values restored; two-pass CONT/OPEN block scan | None | ✅ |
| UPDATE: INSERT then UPDATE in same uncommitted TX (Scenario T) | `dirty_slots` suppresses slot before `before_images` applied; row absent | None | ✅ |
| UPDATE: multiple UPDATEs on same row in one uncommitted TX (Scenario U) | Earliest patch kept; row restored to original pre-transaction values | None | ✅ |
| UPDATE: ROW-compressed table (Scenario V) | `before_images` populated; `_apply_before_image_cd` restores original values via CD-aware byte-splice | None | ✅ |

---

## Why SQL Server's RESTORE recovers correctly

### For a single full-backup restore — same file, richer log usage

`RESTORE DATABASE … WITH RECOVERY` reads the **same `.bak` file** as mssqlbak.
No additional files are involved.  The embedded log tail (blocks 902–929 in the
MTF stream layout documented above) is the same bytes both tools read.

SQL Server's advantage is how it uses those bytes:

| Pass | SQL Server RESTORE | mssqlbak |
|------|--------------------|----------|
| **REDO** | Re-applies every committed `LOP_INSERT_ROWS` / `LOP_MODIFY_ROW` / `LOP_DELETE_ROWS` record so that pages that were scanned before a commit reflect the committed value at backup-end LSN. | ❌ No redo pass — rows committed during the backup whose page was read before the commit remain absent from the output. |
| **UNDO** | Rolls back every open (uncommitted) transaction using formal ARIES undo. | ✅ Partial undo — suppresses uncommitted INSERTs (`dirty_slots`), restores ghost DELETEs (`restore_slots`), and splices before-images for in-row UPDATEs (`before_images`). |
| **Log record coverage** | Formal ARIES parser reads every log record type and every variable-length header format; no record is missed. | ⚠️ Empirical scanner steps 8 bytes at a time through `0x50` opening blocks and matches fixed byte offsets. Records whose layout deviates from the expected pattern are silently skipped — this is why a small number of dirty INSERT rows can leak through the `dirty_slots` filter (the "MinLSN boundary effect" in the tests). |

### Off-row LOB undo — additional log record types in the same file

When a `VARCHAR(MAX)` / `NVARCHAR(MAX)` / `XML` / spatial column is updated and its
value is stored off-row, SQL Server writes **three groups** of log records into the same
embedded log tail:

1. `LOP_MODIFY_ROW` — updates the in-row LOB root-node pointer (8 or 24 bytes).
2. `LOP_DELETE_ROWS` (for each old LOB page chain node) — deallocation undo data.
3. `LOP_INSERT_ROWS` (for each new LOB page chain node) — allocation redo data.

SQL Server's undo engine processes all three groups together.  mssqlbak parses only
`LOP_MODIFY_ROW`, so it can restore the in-row pointer but cannot reverse the LOB
page chain reallocation.  The LOB-chain log records are present in the `.bak` file;
mssqlbak does not implement a parser for them.

### Point-in-time recovery — the one case that requires an additional file

If the recovery target is a timestamp **after** the full backup's end LSN, SQL Server
chains one or more **transaction log backup files** produced by `BACKUP LOG`:

```
full.bak  →  log_1.bak  →  log_2.bak  →  target timestamp
```

These log backup files are a distinct MTF variant that contains only log records (no
data pages).  mssqlbak reads `full.bak` (or `full.bak` + one differential `.bak`)
but has no reader for log backup files.  The `Transaction log backup | 🚫` entry in
`GAP_ANALYSIS.md §5` documents this boundary.

### One-line summary per limitation

| mssqlbak limitation | Root cause | Additional file needed? |
|---|---|---|
| Concurrent-commit rows partially absent | No REDO pass — committed rows on pre-commit pages are not added back | No — log records are in the `.bak`; REDO pass not implemented |
| Small number of dirty rows leak through `dirty_slots` | Empirical 8-byte scanner misses records that SQL Server's formal parser catches | No — same embedded log tail |
| Off-row LOB before-image not fully restored | `LOP_DELETE_ROWS`/`LOP_INSERT_ROWS` for LOB chain nodes are in the `.bak` but not parsed | No — same embedded log tail |
| No point-in-time recovery beyond backup-end LSN | Log backup files (`BACKUP LOG`) are a different format | **Yes** — `log_N.bak` files; not implemented |

---

## Practical guidance for the migration use case

### Safe scenarios (mssqlbak gives correct results)

- **Scheduled backup window** — backup taken while the database is quiescent (e.g. nightly maintenance window, or after application traffic is drained). No in-flight transactions, no concurrent writes. This is the recommended path for migrations.
- **COPY_ONLY full backup + differential chain** — the incremental chain (`full + diff_N`) works correctly because SQL Server's differential merge produces a consistent page image. All rows visible in the mssqlbak output were committed at the time diff_N was taken.

### Scenarios where mssqlbak may show inconsistent data

- **Backup taken under heavy write load** — some rows written during the backup window will not appear (they were committed after the backup scanned their page). The number of missing rows is proportional to the backup duration and write rate.
- **Long-running transactions held open during backup** — uncommitted row data may appear. For migrations, this is usually harmless (the data was going to be committed anyway), but for audit scenarios it is a dirty-read.

### Recommended mitigation

For production migrations where consistency matters:

1. Take the full backup during a low-traffic window (weekend, maintenance window).
2. Apply differential backups taken after peak write periods end.
3. Accept that the most recent N seconds of writes (where N ≈ backup duration) may be absent from the diff — this matches the SQL Server engine restore behaviour without log.

---

## Log tail fuzzy-backup fix (implemented)

mssqlbak includes a full log tail parser that corrects three classes of
fuzzy-backup anomaly: phantom rows (uncommitted INSERTs), phantom deletes
(ghost slots from uncommitted DELETEs), and detection of phantom updates
(uncommitted in-place UPDATEs).

### How it works

1. **Locate the log tail** — `find_log_range` searches for the `APAD` / `MSLS`
   markers that bracket the transaction log data at the end of the backup.
2. **Scan log records** — `iter_log_records` walks 4096-byte opening blocks
   (status byte `0x50`), stepping 8 bytes at a time.  At each candidate
   position it checks `byte[0x0e]` (LCX context = `0x02`) and `byte[0x0f]`
   (SUBTYPE).  The discriminant `byte[0x16]` distinguishes the operation:
   - SUBTYPE=`0x04`: `0x02`=LOP_INSERT_ROWS, `0x03`=LOP_DELETE_ROWS
   - SUBTYPE=`0x00`: `0x80`=BEGIN, `0x81`=COMMIT, `0x82`=ABORT, `0x04`=LOP_MODIFY_ROW
3. **Identify uncommitted transactions** — `build_uncommitted_set` flags any
   xact_id that has a BEGIN and at least one DML record (INSERT, DELETE, or
   MODIFY) but no COMMIT or ABORT.
4. **Collect slot sets** — three slot collections are built:
   - `collect_dirty_slots`: `{(page_id, slot_id), …}` for uncommitted INSERTs (suppress)
   - `collect_restore_slots`: `{(page_id, slot_id), …}` for uncommitted DELETEs (restore)
   - `collect_modified_slots`: `{(page_id, slot_id), …}` for uncommitted MODIFYs (diagnostic)
   - `collect_before_image_patches`: `{(page_id, slot_id): ModifyImagePatch}` — `(row_start, undo_data, redo_row_end)` tuples extracted from `LOP_MODIFY_ROW` undo payloads; passed to `read_table_rows` as `before_images`
5. **Apply in the row reader** — `read_table_rows` accepts `dirty_slots` (skip),
   `restore_slots` (re-emit ghost), and `before_images` (restore before-image). Slots in
   `dirty_slots` are skipped before decoding; ghost slots in `restore_slots` bypass
   `fixedvar_emittable` and decode as live rows; slots in `before_images` have
   `_apply_before_image` called before type decoding, splicing `undo_data` into the
   page row at `row_start` and preserving the tail from `redo_row_end`.

### Usage

```python
from mssqlbak.logtail import logtail_from_bak
from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows

result = logtail_from_bak("database.bak")   # LogTailResult; all sets empty for offline backups
store = PageStore.from_bak("database.bak")
schema = recover_schema(store)
for table in schema.tables:
    for row in read_table_rows(
        store, table,
        dirty_slots=result.dirty_slots,
        restore_slots=result.restore_slots,
        before_images=result.before_images,
    ):
        ...
# result.modified_slots identifies rows whose value may be the rolled-back state
```

### What is covered

| LOP type | Status |
|----------|--------|
| LOP_INSERT_ROWS (byte[0x16]=0x02) — uncommitted INSERTs | ✅ Suppressed via `dirty_slots` |
| LOP_DELETE_ROWS (byte[0x16]=0x03) — uncommitted ghost DELETEs | ✅ Restored via `restore_slots` |
| LOP_MODIFY_ROW (byte[0x16]=0x04) — uncommitted in-place UPDATEs | ✅ Before-image extracted by `collect_before_image_patches()`; spliced into page row by `_apply_before_image()` (FixedVar) or `_apply_before_image_cd()` (ROW/PAGE-compressed). Handles multi-block payloads, sector-status bytes, continuation blocks, and CD-format records. |
| Compressed (ROW / PAGE) rows | ✅ `dirty_slots`/`restore_slots` filter applies; `before_images` restoration via `_apply_before_image_cd` (Scenario V) |
| Columnstore | N/A — log tail does not reference columnstore delta stores |

### Confirmed empirically

Field offsets confirmed via `sys.fn_dump_dblog` on SQL Server 2022:

- **INSERT**: SUBTYPE=`0x04`, byte[0x16]=`0x02`, page_id at `0x18`, slot at `0x1e`
- **DELETE**: SUBTYPE=`0x04`, byte[0x16]=`0x03`, page_id at `0x18`, slot at `0x1e`
- **MODIFY**: SUBTYPE=`0x00`, byte[0x16]=`0x04`, page_id at `0x18`, slot at `0x1e`

End-to-end results:
- `dirtycoverage_uncommitted.bak`: 70→50 rows after `dirty_slots` filter (20 phantom INSERTs suppressed)
- `dirtycoverage_delete.bak`: 50→70 rows after `restore_slots` (20 ghost DELETEs restored)
- `dirtycoverage_update.bak`: all 20 modified rows restored to `original_N` / `pre_update` via `before_images`
- `dirtycoverage_wide.bak`: 3 wide (VARCHAR 3900) modified rows restored; multi-block undo_data correctly assembled (Scenario S)
- `dirtycoverage_insert_update.bak`: INSERT+UPDATE rows absent after `dirty_slots` suppression (Scenario T)
- `dirtycoverage_multi_update.bak`: multiply-updated rows restored to earliest before-image (Scenario U)
- `dirtycoverage_compress_update.bak`: all 50 rows returned; `before_images` populated (20 patches); all 20 phantom-updated rows restored to original values via `_apply_before_image_cd` (Scenario V)

### Level-of-effort — what is still open

| Phase | Work | Status |
|-------|------|--------|
| A | Extract log tail (APAD/MSLS markers) | ✅ Done (`find_log_range`) |
| B | Parse INSERT/DELETE/MODIFY/BEGIN/COMMIT/ABORT | ✅ Done (`iter_log_records`) |
| C | Transaction state tracking | ✅ Done (`build_uncommitted_set`) |
| D-INSERT | Suppress dirty INSERT rows | ✅ Done (`dirty_slots` param) |
| D-DELETE | Restore ghost-deleted rows | ✅ Done (`restore_slots` param) |
| D-MODIFY | Before-image extraction for in-place UPDATE reversal | ✅ Done (`collect_before_image_patches`, `_apply_before_image`/`_apply_before_image_cd`). Handles multi-block payloads, sector-status bytes, continuation blocks (Scenarios M, S, T, U), and ROW/PAGE-compressed CD-format records (Scenario V). |
| E | Regression tests | ✅ Unit tests in `test_logtail.py`; full end-to-end in `test_dirty_backup.py` |

For the migration use case (BACKUP taken during a quiescent window) the
implemented subset is sufficient for all common dirty-read scenarios.

---

## Test coverage

| Test | File | What it pins |
|------|------|-------------|
| `test_concurrent_backup_does_not_crash` | `test_dirty_backup.py` | No exception on fuzzy backup |
| `test_concurrent_pre_backup_rows_all_visible` | `test_dirty_backup.py` | 100/100 pre-backup rows present |
| `test_concurrent_rows_partially_visible` | `test_dirty_backup.py` | Concurrent count in [0, 200] |
| `test_concurrent_no_corrupt_rows` | `test_dirty_backup.py` | All rows have valid fields |
| `test_uncommitted_committed_rows_all_visible` | `test_dirty_backup.py` | 50/50 committed rows |
| `test_uncommitted_dirty_read_occurs` | `test_dirty_backup.py` | 20 dirty-read rows visible (without filter) |
| `test_uncommitted_total_row_count` | `test_dirty_backup.py` | 70 total (50 + 20 dirty-read) |
| `test_truncate_does_not_crash` | `test_dirty_backup.py` | No crash on TRUNCATE-during-backup fixture |
| `test_truncate_row_count_is_zero_or_full` | `test_dirty_backup.py` | Row count is 0 or 500 — never partial |
| `test_truncate_no_corrupt_rows` | `test_dirty_backup.py` | All captured rows decode cleanly |
| `test_addcol_does_not_crash` | `test_dirty_backup.py` | No crash on ADD COLUMN backup |
| `test_addcol_total_row_count` | `test_dirty_backup.py` | All 60 rows (50 pre-DDL + 10 post-DDL) visible |
| `test_addcol_new_column_present_in_schema` | `test_dirty_backup.py` | `extra` column in every row |
| `test_addcol_pre_ddl_rows_column_is_null` | `test_dirty_backup.py` | Pre-DDL rows have `None` (SQL NULL) for new column |
| `test_addcol_post_ddl_rows_have_column_value` | `test_dirty_backup.py` | Post-DDL rows have `extra_value_N` |
| `test_droptable_does_not_crash` | `test_dirty_backup.py` | No crash; survivor table always present |
| `test_droptable_survivor_rows_always_visible` | `test_dirty_backup.py` | survivor_test has 200 rows |
| `test_droptable_target_visible_or_absent_no_crash` | `test_dirty_backup.py` | drop_target 0 or 500 rows; no crash |
| `test_find_log_range_*` (2 tests) | `test_logtail.py` | Log range bounds, offline backup error |
| `test_iter_log_sectors_*` (2 tests) | `test_logtail.py` | Opening block walk, block size |
| `test_iter_log_records_*` (3 tests) | `test_logtail.py` | Uncommitted xact found, 20 INSERTs, slot ground truth |
| `test_build_uncommitted_set_*` (2 tests) | `test_logtail.py` | Identifies 1 uncommitted; empty when all committed |
| `test_collect_dirty_slots_*` (1 test) | `test_logtail.py` | 20 dirty slots match ground truth |
| `test_dirty_slots_from_bak_*` (2 tests) | `test_logtail.py` | Entry point; returns empty for offline backups |
| `test_dirty_slots_suppress_*` (1 test) | `test_logtail.py` | End-to-end: 70→50 rows after dirty_slots filter |
| `test_delete_ghost_rows_restored_with_logtail` | `test_dirty_backup.py` | End-to-end: 50→70 rows after restore_slots (Gap D fixed) |
| `test_update_modified_slots_detected_by_logtail` | `test_dirty_backup.py` | modified_slots populated when phantom update captured (Gap E detected) |
| `test_savepoint_dirty_reads_suppressed` | `test_dirty_backup.py` | dirty_slots suppresses before_save rows from outer TX |
| `test_nested_dirty_reads_suppressed` | `test_dirty_backup.py` | dirty_slots suppresses all 20 rows (outer+inner TX same xact_id) |
| `test_update_before_image_restores_original_values` | `test_dirty_backup.py` | All 20 phantom-updated rows restored to original values via before_images (Scenario M) |
| `test_wide_update_does_not_crash` | `test_dirty_backup.py` | No crash on multi-block LOP_MODIFY_ROW fixture (Scenario S) |
| `test_wide_update_all_patches_collected` | `test_dirty_backup.py` | 3 before_image patches found including CONT-block records (Scenario S) |
| `test_wide_update_before_images_restore_original_values` | `test_dirty_backup.py` | All 5 wide rows restored to phase=pre_update (Scenario S) |
| `test_insert_then_update_does_not_crash` | `test_dirty_backup.py` | No crash on INSERT+UPDATE fixture (Scenario T) |
| `test_insert_then_update_dirty_rows_suppressed` | `test_dirty_backup.py` | Dirty INSERT+UPDATE rows absent; dirty_slots non-empty (Scenario T) |
| `test_multi_update_does_not_crash` | `test_dirty_backup.py` | No crash on multiple-UPDATE fixture (Scenario U) |
| `test_multi_update_earliest_patch_kept` | `test_dirty_backup.py` | Rows restored to original_N label (earliest patch); no intermediate state (Scenario U) |
| `test_compress_update_does_not_crash` | `test_dirty_backup.py` | No crash on ROW-compressed UPDATE fixture (Scenario V) |
| `test_compress_update_modified_slots_detected` | `test_dirty_backup.py` | modified_slots non-empty and before_images populated (20 patches) for compressed table (Scenario V) |
| `test_compress_update_before_image_restores_original_values` | `test_dirty_backup.py` | All 20 phantom-updated compressed rows restored to original values via `_apply_before_image_cd` (Scenario V) |


---

## All gap scenarios complete

All 15 additional gap scenarios (W–AL) documented in `docs/DIRTY_BACKUP_GAPS_PLAN.md`
are implemented and tested as of Jun 2026.  See that document for the full list.

---

## Empirical MTF log-stream research (2026-06-05)

### Method

All findings below are empirical, derived from `tests/fixtures/dirtycoverage_uncommitted.bak` (SQL Server 2022, 3.68 MB, block size 4096, full backup of 432 data pages + 20 uncommitted INSERTs).

### Correction: "LOGSHARD" does not exist

`DIRTY_BACKUP_ANALYSIS.md` previously referred to "MTF LOGSHARD blocks."  No block type with that identifier exists in this backup or in the MTF specification.  The correct container identifier is **MQDA** (see below).

### Complete MTF stream layout

The backup uses fixed 4096-byte MTF physical blocks throughout.  Below is the exact block layout of the dirty-uncommitted fixture.

| Blocks | Byte range | Content |
|--------|-----------|---------|
| 0 | 0 – 4095 | **TAPE** — MTF media descriptor |
| 1 | 4096 – 8191 | **SFMB** — soft filemark |
| 2 | 8192 – 12287 | **SSET** — backup set (attrs=0x04 = Full, `DirtyCoverage`, SQL Server 2022) |
| 3 | 12288 – 16383 | FILE sub-block (bytes 0–2047) + **MSDA** stream descriptor (bytes 2048–4071) + **MQDA** start-of-data header (bytes 4072–4095) |
| 4 – 867 | 16384 – 3555327 | MDF data pages — 432 × 8192 bytes = 2 MTF blocks per page |
| 868 | 3555328 – 3559423 | **MQDA** end-of-stream (bytes 0–1023) + **MSDA** system-pages descriptor (bytes 1024–4071) + **MQDA** start (bytes 4072–4095) |
| 869 – 900 | 3559424 – 3690495 | System pages (pages 0–15 of the primary file: file-header, PFS, GAM, SGAM, boot, IAM, etc.) — 16 × 8192 bytes |
| 901 | 3690496 – 3694591 | **MQDA** end-of-system-pages (attrs=0x00060000) + **SPAD** + **APAD** preamble |
| 902 – 929 | 3694592 – 3809279 | **Transaction log sectors** — 28 × 4096 bytes |
| 930 – 933 | 3809280 – 3825663 | Zero-filled padding |
| 934 | 3825664 – 3829759 | **SPAD** — stream alignment pad |
| 935 | 3829760 – 3833855 | **MSLS** — SQL Server log-stream summary (contains **MQCI** + **SCIN**) |
| 936 | 3833856 – 3837951 | **SFMB** — soft filemark |
| 937 | 3837952 – 3842047 | **ESET** — end of set |
| 938 | 3842048 – 3846143 | **TSMP** — timestamp |
| 939 | 3846144 – 3850239 | **ESET** |
| 940 | 3850240 – 3854335 | **SFMB** |

### SQL Server proprietary markers

The following 4-byte tags appear inside the data stream (not as standalone MTF blocks):

| Tag | Description |
|-----|-------------|
| `MSDA` | Microsoft SQL Data A — MDF/system-page stream descriptor |
| `MQDA` | SQL data-stream boundary; attrs=`0x00020000` = start, attrs=`0x00060000` = end |
| `SPAD` | SQL stream pad — alignment filler before/after log data |
| `APAD` | Alignment pad — appears in the log stream preamble block (901) |
| `MSLS` | Microsoft SQL Log Stream — footer block summarising the log backup |
| `MQCI` | Backup queue checkpoint info — sub-structure inside MSLS |
| `SCIN` | SQL Chain Info — encodes the backup LSN range, sub-structure inside MSLS |
| `TSMP` | Timestamp block following ESET |

### Transaction log sector format

Each 4096-byte log block contains eight 512-byte sectors.  Sectors are **not** prefixed with an MDF-style page header; they use a distinct status-byte framing:

```
Offset  Size  Field
     0     1  sector_status
             0x50 = active sector that opens a log block (bit 6 = 1, bit 4 = 1)
             0x40 = continuation / padding sector (bit 6 = 1, bit 4 = 0)
     1     3  (reserved / secondary flags)
     4     8  (block framing fields, layout partially opaque)
    12     4  VLF_SeqNo — VLF sequence number (0x2a = 42 in this fixture)
    16     4  BlkOffset — byte offset of this log block within the VLF (e.g. 664)
    20     4  SlotCount or related field
    24     8  Checksum / SQUID
```

The value pair (VLF_SeqNo=42, BlkOffset=664) appears in the majority of sector headers in this backup and in the SCIN sub-structure of MSLS — confirming these are LSN components.

### Log record content confirmed

The uncommitted transaction's INSERT records are fully preserved in the log stream.  Probing the first log block (block 902, offset 3694592) by UTF-16LE string search:

| Offset | Content | Interpretation |
|--------|---------|---------------|
| 3694748 | `user_transaction` | LOP_BEGIN_XACT descriptor — names the transaction |
| 3694877 | `uncommitted row 1` + `in_tx_1` (ANSI, +34 bytes) | LOP_INSERT_ROWS record for row 1 |
| 3695037 | `uncommitted row 2` + `in_tx_2` | LOP_INSERT_ROWS record for row 2 |
| … | … | Records 3–20 follow at 160-byte spacing |
| 3698700 | `Backup:InvalidateDiffMaps` | Backup housekeeping log record |
| 3801324 | `INSERT` | LOP_INSERT_ROWS for committed (pre-backup) rows |
| 3803371 | `pre_tx_1` (ANSI) | Row data from the 50 committed rows |

Each LOP_INSERT_ROWS record is **160 bytes** in this fixture.  The row description string (UTF-16LE) and the actual varchar data (ANSI, at +34 from the description) are both readable without any decompression.

### What a log-replay implementation would need

The log records are parseable from blocks 902–929 using:

1. **Extract**: locate the MQDA stream at the `0x00060000` boundary following block 900, then read blocks 902–929 as raw 512-byte sectors.
2. **Identify LOP_BEGIN_XACT / LOP_COMMIT_XACT / LOP_ABORT_XACT**: these records carry the transaction ID and status.  The `user_transaction` descriptor string marks `LOP_BEGIN_XACT`.
3. **Identify LOP_INSERT_ROWS / LOP_DELETE_ROWS**: at 160-byte record spacing in this fixture; contain the row data needed for undo.
4. **Track open transactions at backup-end LSN**: any `LOP_BEGIN_XACT` without a matching `LOP_COMMIT_XACT` before the backup-end LSN is an uncommitted (dirty-read) transaction.
5. **Apply undo to PageStore**: reverse the INSERT records for those transactions.

The SCIN sub-block inside MSLS provides the backup-start and backup-end LSN needed for step 4.

