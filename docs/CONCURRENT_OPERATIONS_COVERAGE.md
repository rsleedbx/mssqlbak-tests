# Concurrent Operations Coverage: What mssqlbak Handles During an Online Backup

Updated: Jun 2026

SQL Server allows almost all DDL, DQL, DCL, and TCL operations to run
concurrently with an online backup without triggering Error 3023.  The
explicit exceptions are `ALTER DATABASE … ADD/REMOVE FILE`, `DBCC SHRINKFILE`,
and overlapping backup sessions.

This document maps every operation from the reference to its mssqlbak coverage
status: whether it has been tested with a real fixture, what mssqlbak returns,
and whether the result is correct.

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Tested — fixture exists, mssqlbak produces the correct result |
| 🟡 | Tested — fixture exists, mssqlbak produces a known-incorrect result (gap documented) |
| ❌ | Not tested — no fixture; behaviour is unknown or assumed |
| N/A | Not applicable — the operation does not change data page content that mssqlbak reads |

---

## 1. DDL — ALTER TABLE

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| ADD COLUMN nullable, no default | All rows returned; pre-DDL rows return `NULL` for the new column | ✅ | Metadata-only column add; `records.py` detects null-bitmap size mismatch (`null_index >= ncol`) and returns `None` (SQL NULL). Fixed — Scenario D |
| ADD COLUMN NOT NULL with DEFAULT | Pre-DDL rows return the DEFAULT value; post-DDL rows return the explicit value | ✅ | SQL Server 2012+ online-default path: pre-DDL rows lack the physical column slot. `catalog.py` reads `sysobjvalues.imageval` (ASCII, `valclass=1`) for the definition text (e.g. `((42))`), `_parse_default_literal` converts it to raw column bytes, and `decode_record` returns those bytes when the column is absent. Fixed — Scenario G |
| ADD COLUMN NOT NULL, no default | N/A | N/A | SQL Server rejects this statement; not possible |
| DROP COLUMN | Dropped column absent from output; all remaining rows decode correctly | ✅ | SQL Server removes the column from syscolpars; mssqlbak never sees it. Both pre-drop rows (ghost bytes skipped) and post-drop rows (clean format) decode correctly. Tested — Scenario F |
| ALTER COLUMN (type change, no rewrite) | All rows returned with correct values | ✅ | Metadata-only for compatible types (e.g. VARCHAR(50) → VARCHAR(200)); catalog max_length changes but physical bytes are unchanged. Tested — Scenario H |
| ALTER COLUMN (type change, rewrite) | All rows returned with correct values | ✅ | SQL Server holds a SCH-M lock for the full table rewrite; any backup that starts after the DDL commits sees all rows in the new type. Tested with NVARCHAR(200)→VARCHAR(200): all 60 rows decoded correctly (50 pre-rewrite, 10 post-rewrite). Tested — Scenario N |
| ADD / DROP CONSTRAINT (CHECK, FK, DEFAULT) | N/A | N/A | System table metadata only; does not change data page content |
| ADD / DROP PRIMARY KEY or UNIQUE INDEX | N/A | N/A | Creates or removes index pages; data pages and clustered index leaf chain are unaffected |
| ADD / DROP TRIGGER | N/A | N/A | System table metadata only |

---

## 2. DDL — ALTER INDEX

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| REBUILD (online, non-clustered) | All data rows returned correctly; no crash | ✅ | Rebuild operates on index pages only; data pages are unaffected. Tested — Scenario J |
| REBUILD (offline) | N/A | N/A | Blocks writes; any backup taken during offline rebuild would block anyway |
| REORGANIZE | N/A | N/A | In-place defragmentation of leaf pages; each 8 KB page is captured atomically and data page content is unchanged |
| DISABLE | N/A | N/A | Metadata-only flag; does not change data page format |

---

## 3. DDL — CREATE / DROP INDEX

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| CREATE INDEX (non-clustered, online) | All data rows returned correctly; no crash | ✅ | Adds new index pages only; data pages are unaffected. Tested — Scenario K (create sub-fixture) |
| CREATE INDEX (offline) | N/A | N/A | Blocks writes during build; backup taken during offline build would block |
| DROP INDEX (non-clustered) | All data rows returned correctly; no crash | ✅ | Deallocates index pages only; data pages and clustered index leaf chain are unaffected. Tested — Scenario K (drop sub-fixture) |

---

## 4. DDL — CREATE / ALTER / DROP TABLE

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| CREATE TABLE (during backup) | Stable table always fully visible; new table absent or fully present (never partial) | ✅ | Timing-dependent catalog capture; mssqlbak never crashes regardless. Tested — Scenario I |
| DROP TABLE (during backup) | Dropped table absent from schema or present with 0–N rows; no crash | ✅ | Tested — Scenario E. See `DIRTY_BACKUP_ANALYSIS.md` |
| TRUNCATE TABLE (during backup) | 0 or N rows — never a partial count; no crash | ✅ | Tested — Scenario C. Page de-allocation is all-or-nothing |
| ALTER TABLE … SWITCH PARTITION | Consistent pre- or post-SWITCH state; no crash | ✅ | SWITCH PARTITION requires a SCH-M lock on both tables; the backup and SWITCH serialize. Pre-SWITCH state captured (part_test=150, staging_test=50). mssqlbak decoded both tables correctly. No split state observed. Tested — Scenario R |

---

## 5. DDL — CREATE / ALTER / DROP VIEW

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| CREATE / ALTER / DROP VIEW | N/A | N/A | View definitions are stored in system tables only; mssqlbak reads base table data pages, not view definitions |

---

## 6. DDL — Programmability Objects

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| CREATE / ALTER / DROP PROCEDURE | N/A | N/A | Stored in system pages only; mssqlbak does not decode procedure bodies |
| CREATE / ALTER / DROP FUNCTION | N/A | N/A | Same as procedures |
| CREATE / ALTER / DROP TRIGGER | N/A | N/A | Same as procedures |
| CREATE / ALTER / DROP SYNONYM | N/A | N/A | Alias metadata only |

---

## 7. DDL — CREATE / ALTER / DROP SCHEMA

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| CREATE / ALTER / DROP SCHEMA | N/A | N/A | Schema namespace metadata in system tables; does not change data page content |

---

## 8. DDL — ALTER DATABASE

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| `SET` options (compatibility level, READ_WRITE / READ_ONLY, MULTI_USER / SINGLE_USER) | All rows returned correctly; no crash | ✅ | ALTER DATABASE SET COMPATIBILITY_LEVEL = 130 fired during backup. System boot page updated; user data pages unaffected. All 300 rows decoded correctly. Tested — Scenario O |
| `ADD FILE` / `REMOVE FILE` | **Blocked by SQL Server** | N/A | Error 3023 — cannot run concurrently with a backup |
| `SET PARTNER` (mirroring) | N/A | N/A | Replication configuration metadata; does not change data pages |
| `ADD SERVICE_BROKER` / `SET ENABLE_BROKER` | N/A | N/A | Service Broker system tables only |

---

## 9. DML — Data Manipulation

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| INSERT (committed before backup) | All rows visible | ✅ | Pre-backup committed rows always fully present — Scenario A |
| INSERT (uncommitted, rolled back) | Rows suppressed with `dirty_slots_from_bak` / `logtail_from_bak` | ✅ | Log tail parser correctly identifies and suppresses uncommitted INSERT rows. `LOP_INSERT_ROWS` records (SUBTYPE=0x04, byte[0x16]=0x02) tracked via `dirty_slots`. Tested — Scenario B |
| INSERT (concurrent, committed during backup) | Partially visible (non-deterministic) | ✅ | Rows visible only if their pages were read after commit — Scenario A |
| DELETE (uncommitted, rolled back) | Ghost rows restored via `logtail_from_bak` + `restore_slots` | ✅ | SQL Server ghosts slots immediately on DELETE; `LOP_DELETE_ROWS` records (SUBTYPE=0x04, byte[0x16]=0x03) now tracked. `logtail_from_bak()` returns `restore_slots`; passing to `read_table_rows` bypasses ghost filter and restores the row. Tested — Scenario L |
| DELETE (committed before backup) | Deleted rows absent (correct) | ✅ | Ghost records filtered by `fixedvar_emittable`; no incorrect rows |
| UPDATE (uncommitted, rolled back) | Original values restored via `logtail_from_bak` + `before_images` | ✅ | `LOP_MODIFY_ROW` records (SUBTYPE=0x00, byte[0x16]=0x04) parsed; `collect_before_image_patches()` extracts `(row_start, undo_data, redo_row_end)` per `(page_id, slot_id)` into `LogTailResult.before_images`. `_apply_before_image()` in `rows.py` splices `undo_data` into the page row, restoring all column values (fixed + variable-length). Sector-status bytes at 512-byte block boundaries replaced with `0x00` during payload extraction. Tested — Scenario M |
| UPDATE (committed before backup) | Updated values visible (correct) | ✅ | Committed values on data pages — always correct |
| MERGE | N/A | N/A | Decomposes into INSERT/UPDATE/DELETE at the row level; each operation follows the rules above |

---

## 10. DQL — SELECT

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| SELECT | N/A | N/A | Read-only; does not affect backup content. mssqlbak itself is a page reader |

---

## 11. TCL — Transaction Control

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| BEGIN + COMMIT (before backup ends) | Committed rows partially visible — only if their pages were read after commit | ✅ | Tested — Scenario A. All pre-backup committed rows always visible |
| BEGIN + ROLLBACK INSERT (during backup) | Uncommitted rows suppressed via `dirty_slots_from_bak` / `logtail_from_bak` | ✅ | Tested — Scenario B. Log tail parser implemented. LOP_INSERT_ROWS correctly distinguished from LOP_DELETE_ROWS via byte[0x16] discriminant |
| BEGIN + ROLLBACK DELETE (during backup) | Ghost-deleted rows restored via `logtail_from_bak` + `restore_slots` | ✅ | Tested — Scenario L. LOP_DELETE_ROWS tracked; `restore_slots` restores ghost slots from uncommitted DELETE transactions |
| BEGIN + ROLLBACK UPDATE (during backup) | Original values restored via `logtail_from_bak` + `before_images` | ✅ | Tested — Scenario M. `collect_before_image_patches()` parses `LOP_MODIFY_ROW` undo payload; `_apply_before_image()` reconstructs the pre-UPDATE row bytes from `(row_start, undo_data, redo_row_end)`. All 20 uncommitted-UPDATE rows decoded with original id/score/label/phase values. |
| Long-running transaction (open at backup start, commits after) | Same as concurrent-commit scenario above | ✅ | Covered by Scenario A |
| Savepoints (`SAVE TRANSACTION`) | Pre-save dirty rows suppressed via `dirty_slots_from_bak`; post-save rollback rows absent | ✅ | Tested — Scenario P. ROLLBACK TO SAVEPOINT before backup correctly ghosts the post-save rows. Pre-save rows in the open TX are suppressed by `dirty_slots_from_bak`. Confirmed with dedicated test |
| Nested transactions (`BEGIN` inside `BEGIN`) | All dirty rows (outer + inner) suppressed via `dirty_slots_from_bak` | ✅ | Tested — Scenario Q. SQL Server assigns a single xact_id to the whole nested group. Log tail parser suppresses all 20 rows as one uncommitted unit. Confirmed with dedicated test |

---

## 12. DCL — Permissions

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| GRANT | N/A | N/A | Permission metadata in system tables only |
| REVOKE | N/A | N/A | Same |
| DENY | N/A | N/A | Same |

---

## 13. DBCC and Statistics

| Operation | mssqlbak result | Status | Notes |
|-----------|----------------|--------|-------|
| DBCC CHECKDB / CHECKALLOC / CHECKCATALOG | N/A | N/A | Read-only integrity checks; do not write data pages |
| UPDATE STATISTICS / CREATE STATISTICS | N/A | N/A | Statistics data is stored in a statistics blob, not in user data pages |
| DBCC SHRINKFILE | **Blocked by SQL Server** | N/A | Error 3023 — cannot run concurrently with a backup |

---

## Summary

| Category | Total operations | ✅ Tested, correct | 🟡 Tested, gap | ❌ Not tested | N/A |
|----------|-----------------|-------------------|----------------|----------------|-----|
| ALTER TABLE | 9 | 6 (ADD NULL col, DROP col, ALTER col compatible, ADD NOT NULL with default, ALTER col rewrite) | 0 | 0 | 3 |
| ALTER INDEX | 4 | 1 (REBUILD non-clustered) | 0 | 0 | 3 |
| CREATE / DROP INDEX | 3 | 2 (CREATE, DROP non-clustered) | 0 | 0 | 1 |
| CREATE / ALTER / DROP TABLE | 4 | 4 (CREATE, DROP, TRUNCATE, SWITCH PARTITION) | 0 | 0 | 0 |
| Views, Programmability, Schema | 10 | 0 | 0 | 0 | 10 |
| ALTER DATABASE | 4 | 1 (SET options) | 0 | 0 | 3 |
| DML | 8 | 7 (pre-backup INSERT, concurrent INSERT, uncommitted INSERT, uncommitted DELETE, committed DELETE, committed UPDATE, uncommitted UPDATE) | 0 | 0 | 1 (MERGE) |
| DQL / SELECT | 1 | 0 | 0 | 0 | 1 |
| TCL | 7 | 7 (concurrent commit, long-running, rollback INSERT, rollback DELETE, savepoints, nested TX, rollback UPDATE) | 0 | 0 | 0 |
| DCL | 3 | 0 | 0 | 0 | 3 |
| DBCC / Statistics | 4 | 0 | 0 | 0 | 4 |
| **Total** | **57** | **27** | **0** | **0** | **29** |

### Remaining gaps

No gaps remain. All 57 operations are either ✅ Tested correct or N/A.

### Resolved gaps (Jun 2026)

| Operation | Fix | Scenario |
|-----------|-----|---------|
| ADD COLUMN NOT NULL with DEFAULT — pre-DDL rows returned `None` | `catalog.py`: reads `sysobjvalues.imageval` (ASCII, `valclass=1`), parses literal via `_parse_default_literal`, stores bytes in `Column.default_bytes`; `records.py` returns `default_bytes` for missing fixed/variable slots | G |
| ADD COLUMN nullable, no default — returned `''` | `records.py`: `null_index >= ncol` check returns `None` (SQL NULL) | D |
| Uncommitted INSERT — phantom rows visible | `logtail_from_bak().dirty_slots`; `LOP_INSERT_ROWS` (byte[0x16]=0x02) correctly distinguished from `LOP_DELETE_ROWS` | B |
| Uncommitted DELETE — ghost rows missing | `logtail_from_bak().restore_slots`; `LOP_DELETE_ROWS` (byte[0x16]=0x03) tracked; ghost slots decoded as live rows | L |
| Savepoints (pre-save dirty rows visible) | `dirty_slots_from_bak`: outer TX xact_id covers pre-save rows; suppressed as uncommitted INSERT | P |
| Nested transactions (outer+inner dirty rows) | `dirty_slots_from_bak`: single xact_id for outer+inner; all 20 rows suppressed as one uncommitted unit | Q |
| Uncommitted UPDATE — modified values still visible | `collect_before_image_patches()` parses `LOP_MODIFY_ROW` undo payload; `_apply_before_image()` splices `undo_data` into page row bytes restoring all fixed + variable-length columns; sector-status bytes at 512-byte block boundaries replaced with `0x00`. All 20 rows restored. | M |

### All scenarios covered

As of Jun 2026, every item in the original reference has been tested with a real fixture.
All 57 operations are either ✅ Tested correct or N/A. Zero 🟡 gaps remain.

---

## 14. Deep Edge Cases — Uncommitted UPDATE Sub-scenarios

Scenario M verified the core before-image restoration path.  The four sub-scenarios
below push its boundary conditions: multi-block log records, combined INSERT+UPDATE,
multiple UPDATEs on the same row, and ROW-compressed storage.

| Sub-scenario | Description | mssqlbak result | Status | Notes |
|---|---|---|---|---|
| S — Wide multi-block MODIFY | `LOP_MODIFY_ROW` undo payload spans a 4096-byte log block boundary; record starts inside a `0x40` continuation block | Original values restored for all 3 wide rows (VARCHAR 3900) | ✅ | Two-pass scan: Pass 1 collects records from `0x50` opening blocks; Pass 2 fills gaps from `0x40` continuation blocks (never overwrites opening-block entries). `_read_log_payload` carries the block-crossing offset instead of resetting to 1; sector-status byte at position 0 of the new block is substituted with `0x00`, not skipped. `row_start` read from `+0x38`; falls back to `+0x44` (fixed_end) when `(pos+0x38) % 512 == 0`. `modified_slots` = union of `collect_modified_slots` (opening blocks) and `before_images.keys()` (continuation blocks). Fixture: `dirtycoverage_wide.bak` |
| T — INSERT then UPDATE | Same uncommitted TX inserts a new row then updates it; both the `LOP_INSERT_ROWS` and `LOP_MODIFY_ROW` records are present in the log | Inserted row fully suppressed; `before_images` patch is never reached | ✅ | `dirty_slots` is populated for the INSERT; `read_table_rows` suppresses the slot before `_apply_before_image` is considered. Correct ordering: dirty_slots check precedes before_image application. Fixture: `dirtycoverage_insert_update.bak` |
| U — Multiple UPDATEs same row | Same uncommitted TX updates the same row twice (or more); multiple `LOP_MODIFY_ROW` records for the same `(page_id, slot_id)` | Row restored to its original (pre-transaction) value, not any intermediate state | ✅ | `collect_before_image_patches` keeps the first-seen patch per `(page_id, slot_id)` (`if key not in patches`). SQL Server writes log records in forward order; the first-seen record carries the earliest before-image (closest to the true original). Subsequent intermediate patches are discarded. Fixture: `dirtycoverage_multi_update.bak` |
| V — ROW-compressed table | Uncommitted UPDATE on a table with `ROW` compression; `LOP_MODIFY_ROW` undo payload is a contiguous byte-range replacement within the CD record | Before-image correctly restored; all original values returned | ✅ | `collect_before_image_patches` treats `row_start==0` (not `<4`) as invalid, retaining valid CD patches with `row_start=3`. `_apply_before_image_cd` applies the byte-splice using `len(raw)`. `_read_compressed` accepts and applies `before_images`. Fixture: `dirtycoverage_compress_update.bak` |
