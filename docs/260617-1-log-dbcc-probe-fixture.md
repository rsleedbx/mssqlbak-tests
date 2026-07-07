# Plan: LOG Backup Fixture + G31b DBCC PAGE LOB Probe

**Date:** 2026-06-17  
**Status:** Part I ⬜ pending · Part II ⬜ pending

| Part | Description | Status |
|------|-------------|--------|
| I | LOG backup fixture — closes VC01 LOG/INCREMENTAL gap | ⬜ pending |
| II | G31b DBCC PAGE probe — closes VC02 btyp=3 verifier gap; investigates VC03 max_links=4 | ⬜ pending |

**Related:** [`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md) §1.1.3 (SSET backup-kind flags), §6.2 (on-page LOB records), §13 (Value Coverage Register VC01–VC03); [`260616-3-random-order-fixtures-plan.md`](260616-3-random-order-fixtures-plan.md) (fixture wiring pattern); skill `mssqlbak-fixtures`

---

## 0. Scope and coverage policy

Both parts target **`[CONFIRMED]`** on the spec confidence ladder, achieved via a
live SQL Server byte-level verifier:

- **Part I** — SQL Server writes the MTF SSET `block_attributes` flag `0x10`
  (`SSET_INCREMENTAL_BIT`) for a transaction-log backup.  The flag is confirmed by
  the MTF v1.00a normative spec (see `CORROBORATION_SOURCES.md §MTF`).  A fixture
  + `RESTORE HEADERONLY` sidecar closes VC01's LOG/INCREMENTAL blind spot.

- **Part II** — G31 (`[EMPIRICAL]`) was captured from a Python page scan and only
  observed btyp=3 DATA records.  The sub-header fields for btyp=2 (INTERNAL /
  LARGE_ROOT) — `MaxLinks`, `CurLinks`, `Level` — were identified this session from
  external sources (`KAZ-LOB`, `KOR-LOB`) and named correctly in the spec.  G31b
  captures DBCC PAGE output from `cs_lob_preamble2.bak` to confirm those field
  names at byte level and to read `MaxLinks` off every INTERNAL node (answering VC03:
  whether any node has `MaxLinks = 4`).

### Coverage policy (same as `260616-3`)

> **`[CONFIRMED]`** = fixture committed + normative producer spec or live
> byte-level verifier (`DBCC PAGE` / `RESTORE HEADERONLY` / DMV).  
> **`[CORROBORATED]`** = fixture + independent third-party source.  
> **`[EMPIRICAL]`** = passing fixture only, no external source.

---

## Skill inventory

| Capability | Status |
|---|---|
| `BACKUP LOG ... WITH FORMAT, INIT` T-SQL pattern | ✓ tested — pattern from `make_incremental_fixture.py` |
| Fixture wiring (4-place checklist: generator + `fixture_run.py` + `conftest.py` + test) | ✓ tested — multiple prior parts |
| `DBCC IND` / `DBCC PAGE` probe via `_run_sql` + `sqlcmd_base` | ✓ tested — `make_v11_probe.py`, `make_g44_probe.py` |
| `RESTORE DATABASE ... FROM DISK` to provision probe target | ✓ tested — `make_g44_probe.py` |
| Sidecar JSON format (`tests/fixtures_2022/probe/Gnn.json`) | ✓ tested — G10/G13/G14/G31/G44 all committed |
| Reading SSET `block_attributes` from a real .bak | ⚠ not tested at integration level — unit test only (`test_reader.py` synthetic SSET) |

---

## Blockers (must be true before execution)

| Blocker | Check |
|---------|-------|
| A running SQL Server 2022 container is provisioned | `python -m tools.fixture_run env` resolves without error |
| `cs_lob_preamble2.bak` exists in `tests/fixtures_2022/` | `ls tests/fixtures_2022/cs_lob_preamble2.bak` |

---

## Design decisions

| Decision | Default if user says "go ahead" |
|----------|--------------------------------|
| Does the LOG backup fixture go in `_ALL_VERSIONS_SUITE`? | **No.** A LOG backup contains log records, not data pages; mssqlbak cannot extract rows from it. It runs via `python -m tools.fixture_run log-backup` explicitly (or per-version with `--fixture-dir`). |
| Which fixture does G31b probe use? | `cs_lob_preamble2.bak` — it already has multi-level LOB chains (ROOT → INTERNAL → DATA) confirmed by G31 and used by G44 probe. |
| Where does `G31b.json` go? | `tests/fixtures_2022/probe/G31b.json` — same directory as G31.json, G44, etc. |
| Does G31b also produce a G31c (btyp=5 ROOT sub-header)? | Yes — same DBCC PAGE run will capture all three btyp values (2, 3, 5) in one pass; output goes in a single `G31b.json` covering all three. |

---

## Part I — LOG backup fixture

### Goal

Produce two .bak files from a minimal `FULL` recovery-model database:
- `logbackupcoverage_full.bak` — full backup (base)
- `logbackupcoverage_log.bak` — transaction-log backup

The test asserts that mssqlbak reads the LOG backup and reports
`block_attributes & 0x10 != 0` (SSET INCREMENTAL bit set).

### Phase 0 — Verify environment

| Step | Command | Pass condition |
|------|---------|----------------|
| 0a | `python -m tools.fixture_run env` | Prints `FIXTURE_CONTAINER` and `FIXTURE_DBA_PASSWORD` without error |
| 0b | Check `backup_type_label` field exists | `python -c "from mssqlbak.mtf import parse_bak_header; help(parse_bak_header)"` or inspect `BackupSetInfo` — confirm the field is readable from a real .bak |

### Phase 1 — Write generator `tools/make_log_backup_fixture.py`

```
DB_NAME = "LogBackupCoverage"
```

SQL outline:
```sql
IF DB_ID('LogBackupCoverage') IS NOT NULL BEGIN
  ALTER DATABASE LogBackupCoverage SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE LogBackupCoverage;
END;
CREATE DATABASE LogBackupCoverage;
ALTER DATABASE LogBackupCoverage SET RECOVERY FULL;
GO
USE LogBackupCoverage;
GO
CREATE TABLE log_target (id INT IDENTITY PRIMARY KEY, val NVARCHAR(100));
INSERT INTO log_target(val) VALUES (N'seed row 1'), (N'seed row 2');
GO
-- Full backup (NOT COPY_ONLY — must establish differential base for log chain)
BACKUP DATABASE LogBackupCoverage
  TO DISK = N'/tmp/logbackupcoverage_full.bak'
  WITH FORMAT, INIT, STATS=10;
GO
-- Insert rows so the log has activity
INSERT INTO log_target(val) VALUES (N'after full 1'), (N'after full 2');
GO
-- Log backup
BACKUP LOG LogBackupCoverage
  TO DISK = N'/tmp/logbackupcoverage_log.bak'
  WITH FORMAT, INIT, STATS=10;
GO
```

Generator follows the `make_g44_probe.py` / `make_incremental_fixture.py` pattern:
- Uses `tools.fixture_utils.fixture_credentials()`
- Copies both .bak files from the container with `podman cp`
- Skips with `print("skip (already exists): …")` if either .bak is present
- Exports `DB_NAME`, `FULL_BAK`, `LOG_BAK` constants for the test to import

**End state:** `tests/fixtures_<year>/logbackupcoverage_full.bak` and
`tests/fixtures_<year>/logbackupcoverage_log.bak` both present.

### Phase 2 — Wire into `tools/fixture_run.py`

```python
def _run_log_backup(*, force: bool = False) -> int:
    from tools.make_log_backup_fixture import main
    sys.argv = ["make_log_backup_fixture", *(["--force"] if force else [])]
    return main()
```

Add to `_COMMANDS`:
```python
"log-backup": _run_log_backup,
```

**Not** added to `_ALL_VERSIONS_SUITE` (LOG backups are not row-decodable by mssqlbak).

Add argparse subparser entry so `--help` lists it.

**End state:** `python -m tools.fixture_run --help | grep log-backup` prints the command.

### Phase 3 — Wire `tests/conftest.py`

```python
FIXTURE_BAK_LOG_FULL = FIXTURE_DIR / "logbackupcoverage_full.bak"
FIXTURE_BAK_LOG_LOG  = FIXTURE_DIR / "logbackupcoverage_log.bak"

@pytest.fixture
def fixture_bak_log_full() -> Path:
    if not FIXTURE_BAK_LOG_FULL.exists():
        pytest.skip(f"missing {FIXTURE_BAK_LOG_FULL.name} — run: python -m tools.fixture_run log-backup")
    return FIXTURE_BAK_LOG_FULL

@pytest.fixture
def fixture_bak_log_log() -> Path:
    if not FIXTURE_BAK_LOG_LOG.exists():
        pytest.skip(f"missing {FIXTURE_BAK_LOG_LOG.name} — run: python -m tools.fixture_run log-backup")
    return FIXTURE_BAK_LOG_LOG
```

**End state:** `pytest tests/test_log_backup_coverage.py --collect-only -q` collects tests (skip if .bak absent).

### Phase 4 — Write `tests/test_log_backup_coverage.py`

Tests (all auto-skip when .bak absent):

| Test | Assertion |
|------|-----------|
| `test_log_bak_sset_incremental_bit` | `block_attributes & 0x10 != 0` for `logbackupcoverage_log.bak` |
| `test_full_bak_sset_normal_bit` | `block_attributes & 0x04 != 0` for `logbackupcoverage_full.bak` |
| `test_log_bak_type_label` | `backup_type_label` (or equivalent field) identifies the backup as a log/transaction-log backup |
| `test_log_bak_is_not_parseable_as_row_data` | Opening `logbackupcoverage_log.bak` with `PageStore.from_bak` either raises a well-typed exception or returns an empty page store (not a crash) |

Access path:

```python
from mssqlbak.reader import read_bak_metadata
meta = read_bak_metadata(path)
info = meta.first_set          # → BackupSetInfo
info.backup_type_label         # "Incremental" for BACKUP LOG (MTF SSET_INCREMENTAL = 0x10)
info.backup_attributes         # raw block_attributes int
```

`_backup_type_label` maps `SSET_INCREMENTAL (0x10)` → `"Incremental"` and `SSET_NORMAL (0x04)` → `"Full"`.  The test therefore checks `info.backup_type_label == "Incremental"` for the log .bak and `info.backup_type_label == "Full"` for the full .bak.

**End state:** `pytest tests/test_log_backup_coverage.py -v` shows 4 tests, all PASS or SKIP (not ERROR).

### Phase 5 — Spec update

Update VC01 in `BAK_FORMAT_SPEC.md §13`:
- LOG/INCREMENTAL row: change `blind-spot` from "LOG" to "—"; change status from `open` to `CLOSED`; update closing action to reference `logbackupcoverage_log.bak`

---

## Part II — G31b DBCC PAGE LOB probe

### Goal

Produce `tests/fixtures_2022/probe/G31b.json` containing DBCC PAGE output for:
- btyp=5 (ROOT / LARGE_ROOT_YUKON) — confirms MaxLinks always = 5
- btyp=2 (INTERNAL / LARGE_ROOT) — confirms MaxLinks ∈ {2, 4}; reads CurLinks and Level
- btyp=3 (DATA) — corroborates existing G31 observations with engine-native field names

This elevates G31 from `[EMPIRICAL]` to `[CONFIRMED]` and answers VC03 (whether MaxLinks=4 INTERNAL nodes exist in `cs_lob_preamble2.bak`).

### Phase 0 — Verify environment

| Step | Command | Pass condition |
|------|---------|----------------|
| 0a | `ls tests/fixtures_2022/cs_lob_preamble2.bak` | File present |
| 0b | Run DBCC IND manually on a known table to confirm output format | Restore the bak, run `DBCC IND('G31bProbe', 'LobPreamble2', -1)` via sqlcmd, observe type-3 page in output |

### Phase 1 — Write probe `tools/make_g31b_probe.py`

**SQL outline:**

```sql
-- Step 1: restore
IF DB_ID('G31bProbe') IS NOT NULL BEGIN
  ALTER DATABASE [G31bProbe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [G31bProbe];
END;
RESTORE DATABASE [G31bProbe] FROM DISK = N'/tmp/cs_lob_preamble2.bak'
WITH MOVE N'LobPreamble2' TO N'/var/opt/mssql/data/G31bProbe.mdf',
     MOVE N'LobPreamble2_log' TO N'/var/opt/mssql/data/G31bProbe_log.ldf',
     REPLACE, STATS=10;
GO

USE [G31bProbe];
GO

-- Step 2: find TEXT_MIX (type 3) pages via DBCC IND
DBCC TRACEON(3604);
GO
DBCC IND('G31bProbe', 'cs_lob_preamble', -1);
GO

-- Step 3: for each TEXT_MIX page found (type 3), run DBCC PAGE (printopt=3)
-- This emits lines like:
--   Blob row at: Page (1:<n>) Slot <s> Length: <l> Type: 5 (LARGE_ROOT_YUKON)
--   Blob Id: <id> Level: <l> MaxLinks: <m> CurLinks: <c>
--   Blob row at: Page (1:<n>) Slot <s> Length: <l> Type: 3 (DATA)
--   Blob row at: Page (1:<n>) Slot <s> Length: <l> Type: 2 (INTERNAL)
-- Capture these for all TEXT_MIX pages.
```

The Python layer:
1. Runs the restore SQL
2. Runs `DBCC IND` and parses output to collect `(PagePID, PageType)` rows where `PageType = 3` (TEXT_MIX)
3. For each TEXT_MIX page (limit to first 20 to keep output manageable), runs `DBCC PAGE(1, 1, <page>, 3)` and captures output
4. Parses DBCC PAGE output lines into structured records:
   - `Blob row at: Page (1:N) Slot S Length: L Type: T (NAME)` → `{page, slot, length, btyp, btyp_name}`
   - For btyp=5: `Blob Id: X Level: L MaxLinks: M CurLinks: C` → add to prior record
   - For btyp=2: `Child MaxLinks: M CurLinks: C Level: L` → add to prior record
5. Saves JSON output to `tests/fixtures_2022/probe/G31b.json`

Generator follows `make_g44_probe.py` exactly:
- `from tools.fixture_utils import _run_sql, fixture_credentials, sqlcmd_base`
- Checks `cs_lob_preamble2.bak` exists before starting; skips if not
- Saves probe output text to `G31b_dbcc_output.txt` alongside the JSON

**End state (Phase 1):**  
`tests/fixtures_2022/probe/G31b.json` exists and contains at least one record each for btyp=3, btyp=2, and btyp=5.

### Phase 2 — Wire into `tools/fixture_run.py`

```python
def _run_g31b_probe() -> int:
    from tools.make_g31b_probe import main
    return main()
```

Add to `_COMMANDS`:
```python
"g31b-probe": _run_g31b_probe,
```

Not in `_ALL_VERSIONS_SUITE` (probes are one-time, not all-versions).

**End state:** `python -m tools.fixture_run --help | grep g31b-probe` prints the command.

### Phase 3 — Interpret the G31b output and update the spec

After the probe runs, read `G31b.json` and:

**For VC02:** All three btyp values (3, 2, 5) appear in DBCC PAGE output with SQL Server's own field names → G31 confidence tag promoted from `[EMPIRICAL]` to `[CONFIRMED]`.

**For VC03 (two outcomes):**

| MaxLinks values seen for btyp=2 | Action |
|----------------------------------|--------|
| Only `MaxLinks = 2` | VC03 blind spot confirmed: no 4-slot node in this fixture. Update VC03 status to `open / needs larger LOB` and add a note pointing to the 4-slot LOB sizing experiment (see §3.1 below). |
| `MaxLinks = 4` seen | VC03 blind spot is closed by `cs_lob_preamble2.bak`. Update VC03 to `CLOSED`. |

**Spec updates (unconditional after probe):**
- G31 tag: `[EMPIRICAL]` → `[CONFIRMED]` (DBCC PAGE corroborates MaxLinks/CurLinks/Level field names and values)
- VC02 status: `partial` → `CLOSED` (btyp=3 now has independent DBCC PAGE verifier; all three btyp values confirmed)

### 3.1 If VC03 needs a larger LOB (conditional — only if MaxLinks=4 not seen)

A 4-slot INTERNAL node appears when the LOB value is large enough to require an INTERNAL node with more than 2 children. The strategy:

1. Extend the `make_lob_preamble_fixture.py` generator (or create a new `make_lob_multiroot_fixture.py`) with a `varbinary(max)` column loaded with a single value of ~500 KB, forcing SQL Server to build a deep LOB tree.
2. Run the G31b probe against the new fixture to check whether `MaxLinks = 4` appears.
3. If yes: commit new fixture + updated G31b.json; close VC03.

This step is gated on the Phase 2 observation; do not build it speculatively.

---

## Execution order and dependencies

```
Phase 0 (both parts) — verify env
    │
    ├─ Part I: generate LOG backup
    │       Phase 1 → make_log_backup_fixture.py
    │       Phase 2 → fixture_run.py wiring
    │       Phase 3 → conftest.py
    │       Phase 4 → test_log_backup_coverage.py
    │       Phase 5 → spec VC01 update
    │
    └─ Part II: G31b probe (independent of Part I)
            Phase 0 → verify cs_lob_preamble2.bak
            Phase 1 → make_g31b_probe.py
            Phase 2 → fixture_run.py wiring
            Phase 3 → interpret output, update spec (VC02, VC03, G31 tag)
            [Phase 3.1] → conditional MaxLinks=4 experiment
```

Parts I and II are independent; either can run first.

---

## Checkable end states

| Item | End state | How to verify |
|------|-----------|---------------|
| LOG backup fixture built | Both .bak files present | `ls tests/fixtures_2022/logbackupcoverage_{full,log}.bak` |
| LOG backup wired | Command listed in help | `python -m tools.fixture_run --help \| grep log-backup` |
| LOG backup test passes | 4 tests PASS or SKIP | `pytest tests/test_log_backup_coverage.py -v` |
| VC01 LOG closed | VC01 row status = CLOSED | Grep §13 table in `BAK_FORMAT_SPEC.md` |
| G31b probe runs | JSON sidecar present | `ls tests/fixtures_2022/probe/G31b.json` |
| G31b wired | Command listed in help | `python -m tools.fixture_run --help \| grep g31b-probe` |
| G31 promoted to CONFIRMED | Tag in §6.2 | Grep `G31.*\[CONFIRMED\]` in `BAK_FORMAT_SPEC.md` |
| VC02 closed | VC02 row status = CLOSED | Grep §13 table in `BAK_FORMAT_SPEC.md` |
| VC03 resolved | VC03 row updated (CLOSED or `open/needs-larger-LOB`) | Grep §13 table in `BAK_FORMAT_SPEC.md` |

---

## What I cannot do without your input

| Item | Why |
|------|-----|
| ~~Which mssqlbak API to use to read `block_attributes`~~ | Resolved: `read_bak_metadata(path).first_set.backup_attributes` — see Phase 4 |
| Whether to add `--force` flag to `make_log_backup_fixture.py` | Minor; default is to skip if present. Needed only if idempotent re-run is required. |
| VC03 conditional experiment priority | If G31b shows MaxLinks=2 only, building a new LOB-size fixture for MaxLinks=4 is optional; user decides whether to proceed. |
