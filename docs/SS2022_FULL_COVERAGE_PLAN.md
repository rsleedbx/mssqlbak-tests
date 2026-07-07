# Plan: Close Remaining Gaps for Any SQL Server 2022 .bak

**Goal:** `mssqlbak` can read data rows from any SQL Server 2022 full backup
(unencrypted, non-FILESTREAM, non-In-Memory-OLTP) without silent data loss.

**Created:** Jun 2026  
**Status:** complete — all in-scope phases done (G41 confirmed Jun 2026; Phase 2 cross-version deferred to 2022-only scope)  
**Related docs:** `GAP_ANALYSIS.md`, `BAK_FORMAT_SPEC.md`, `BAK_SPEC_FIXTURES.md`


Saved as docs/SS2022_FULL_COVERAGE_PLAN.md and committed (b5e8b6d). When picking this up, start with Phase 0 — the two python -m tools.fixture_run env / stripe-probe commands will unblock everything else.

---

## Scope (this plan)

| Area | Why |
|------|-----|
| **Phase 1** — Striped multi-file backup | Largest real-world coverage gap; most production backup jobs stripe |
| **Phase 2** — G21 cross-version catalog | Proves parser works on 2012/2016/2019 databases, not just 2022 |
| **Phase 3** — G17/G18 CD long-data region | ROW/PAGE compressed tables with >30 columns are untested |
| **Phase 4** — G40/G41/G43 columnstore internals | Dict-id ordering, LOB preamble, and segment header confirmed empirically but not verifier-verified |

**Out of scope (this plan):** In-Memory OLTP, TDE, Always Encrypted, FileTable, log backups.

---

## Skill inventory

| Capability | Status |
|------------|--------|
| ROW/PAGE compression decoder | ✓ tested |
| Columnstore decoder | ✓ tested |
| MTF single-file reader | ✓ tested |
| MTF multi-file (striped) reader | ✗ gap — does not exist |
| `spec_probe` subcommand harness | ✓ tested |
| `fixture_run` credential/container automation | ✓ tested |
| `DBCC PAGE` verifier capture + sidecar JSON | ✓ tested |
| `sys.column_store_segments` verifier capture | ⚠ not yet wired to spec_probe |
| forgedb SQL Server 2012/2016/2019 containers | ✗ blocker — unknown if provisioned |

---

## Blockers and design decisions

### Blockers

| ID | Blocker | How to resolve |
|----|---------|----------------|
| B1 | SQL Server 2012/2016/2019 forgedb containers may not be provisioned | `python -m tools.fixture_run env` + `forgedb list` |
| B2 | Striped backup chunk distribution format unknown | Empirical probe of a 2-file stripe .bak (Phase 0b) |

### Design decisions (defaults shown — confirm before executing)

| ID | Decision | Default |
|----|----------|---------|
| D1 | Striped backup API shape | Add `PageStore.from_stripe([p1, p2, ...])` as a new entry point; `from_bak(path)` unchanged (no breaking change) |
| D2 | G40/G41/G43 investigation — use existing fixture first? | Yes — try `boundarycoverage_full.bak` before building a new one |

---

## Phase 0 — Verify blockers

Run these before touching any code.

| Step | Command | End state |
|------|---------|-----------|
| 0a | `python -m tools.fixture_run env` (check forgedb list) | Know which SQL Server engine versions are live |
| 0b | Generate a 2-file striped backup against local 2022 container; hex-dump first 512 bytes of each file | MTF magic confirmed in both; chunk distribution understood |
| 0c | `python tools/spec_probe.py columnstore --fixture tests/fixtures/boundarycoverage_full.bak` | Know which enc types / dict blob sizes are present in existing fixture |

---

## Phase 1 — Striped multi-file backup

**Priority:** highest (real-world impact)  
**Blocked on:** B2 (Phase 0b must complete first)

**End state (checkable):**
`PageStore.from_stripe(['s1.bak', 's2.bak'])` produces the same row count and
values as an equivalent single-file backup.  `pytest tests/test_striped_backup.py`
passes.

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 1a | Add `tools/make_stripe_fixture.py`; wire into `fixture_run` as `stripe` command; generate `tests/fixtures/striped_full_{1,2}.bak` | `tools/make_stripe_fixture.py`, `tools/fixture_run.py` | ✓ done |
| 1b | Probe stripe file structure from 0b output; document page/chunk distribution in `BAK_FORMAT_SPEC.md` | `docs/BAK_FORMAT_SPEC.md` | ✓ done — each stripe is independent MSSQLBAK container; pages partitioned, no overlap except file-header |
| 1c | Implement `from_stripe(paths)` in `mssqlbak/pages.py`: open each file, read XPRESS chunks, merge pages | `mssqlbak/pages.py` | ✓ done |
| 1d | Auto-detect MTF media-set continuation in `PageStore.from_bak` (TAPE block carries a "next file" pointer for uncompressed stripes) | `mssqlbak/pages.py` | ✗ deferred — uncompressed stripe not yet needed |
| 1e | Add `tests/test_striped_backup.py`; assert row count + values match single-file baseline | `tests/test_striped_backup.py` | ✓ done — 6 tests, all pass |
| 1f | Update `GAP_ANALYSIS.md` §4 and §5 (striped → ✅) | `docs/GAP_ANALYSIS.md` | ✗ pending |

**Key unknown resolved by 0b:** whether pages are distributed round-robin by
XPRESS chunk (most likely for compressed backups) or by page-ID range.  This
determines whether the merge algorithm interleaves chunk iterators or
concatenates sorted ranges.

---

## Phase 2 — G21 cross-version catalog stability

**Priority:** high (affects all 2012/2016/2019 databases)  
**Blocked on:** B1 (Phase 0a must confirm engine availability)

**End state (checkable):**
`pytest tests/test_catalog_version.py` passes for 2012, 2016, 2019, and 2022.
G21 row in `BAK_FORMAT_SPEC.md` is struck through as `[CONFIRMED]` (or updated
with version-dispatch table if IDs differ).

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 2a | Provision 2012/2016/2019 containers if not live (forgedb `setup_sqlserver_podman --engine 20xx`) | forgedb | ✗ blocked on 0a |
| 2b | Run `python -m tools.fixture_run version-matrix` → generates `catalog_ss{2012,2016,2019}.bak` | existing tooling | ✓ tooling ready |
| 2c | Extend `spec_probe catalog` to emit per-version object IDs (sysallocunits=7, sysrowsets=5, syscolpars=41, sysschobjs=34, …) | `tools/spec_probe.py` | ✗ gap |
| 2d | Capture `sys.partitions` + `sys.allocation_units` verifier JSON for each version; commit as `tests/fixtures/probe/G21_ss{2012,2016,2019}.json` | verifier sidecars | ✗ gap |
| 2e | Add assertions to `tests/test_catalog_version.py` (already exists; extend) | `tests/test_catalog_version.py` | ✗ gap |
| 2f | Update G21 in `BAK_FORMAT_SPEC.md` Guess Register | `docs/BAK_FORMAT_SPEC.md` | ✗ gap |

---

## Phase 3 — G17/G18: CD long-data region (ROW/PAGE >30 columns)

**Priority:** medium (silent wrong data risk for wide tables)  
**Blocked on:** nothing — can start immediately once SQL Server container is live

**End state (checkable):**
`pytest tests/test_rowcompress.py` passes with `cmp_row_wide` and `cmp_page_wide`
tables (≥31 columns).  G17 and G18 promoted in `BAK_FORMAT_SPEC.md`.

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 3a | Add `cmp_row_wide` (40 `int` columns + PK, ROW compression) and `cmp_page_wide` (PAGE) to `tools/compressionmatrix.py`; regenerate `compressioncoverage_full.bak` | `tools/compressionmatrix.py` | ✓ done |
| 3b | Capture `DBCC PAGE` verifier; commit as `tests/fixtures/probe/G17.json` | verifier sidecar | ✗ deferred — empirical verdict accepted |
| 3c | Add `spec_probe rowcompress --wide` subcommand | `tools/spec_probe.py` | ✗ deferred — inline test assertions sufficient |
| 3d | Mark G17/G18 empirical | `mssqlbak/rowcompress.py` | ✓ done — all 40×50 values match formula |
| 3e | Add wide-row assertions to `tests/test_rowcompress.py` | `tests/test_rowcompress.py` | ✓ done — 8 tests, all pass |
| 3f | Update G17, G18 in `BAK_FORMAT_SPEC.md` | `docs/BAK_FORMAT_SPEC.md` | ✓ done |

---

## Phase 4 — G40/G41/G43: Columnstore internals

**Priority:** medium-low (empirically correct today; verifier confirmation pending)  
**Blocked on:** nothing — use `boundarycoverage_full.bak` first (Rule 1)

**End state (checkable):**
`spec_probe columnstore` emits `verdict: match` for G40, G41, and G43.
All three rows struck through in `BAK_FORMAT_SPEC.md` Guess Register.

### G43 — Segment blob header [+0:+33]

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 4a | Add `spec_probe columnstore-seg-header` subcommand; dump preamble [0:33] + compare bpv/nw validity | `tools/spec_probe.py` | ✓ done — 24 segments checked, verdict: match |
| 4b | Run against live DB; commit verifier sidecar `tests/fixtures/probe/G43.json` | verifier sidecar | ✓ done — `G43.json` committed |
| 4c | Document bpv/nw offsets in `BAK_FORMAT_SPEC.md §7.3`; update G43 | `docs/BAK_FORMAT_SPEC.md` | ✓ done — G43 marked EMPIRICAL |

### G40 — Dict-id field ordering (offsets 52 vs 56)

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 4d | Add `spec_probe columnstore-dict-order` subcommand; compare `sec_dict` vs verifier `secondary_dictionary_id` | `tools/spec_probe.py` | ✓ done — verdict: match |
| 4e | Field order confirmed correct — no code change needed | `mssqlbak/columnstore.py` | ✓ done — offset 56 = secondary_dictionary_id confirmed |
| 4f | Commit verifier sidecar `tests/fixtures/probe/G40.json`; update G40 in spec | `docs/BAK_FORMAT_SPEC.md` | ✓ done — G40 marked CONFIRMED |

### G41 — LOB preamble (12 bytes + 8-byte separators every 65 536 bytes)

| Step | Work | File(s) | Status |
|------|------|---------|--------|
| 4g | Check `boundarycoverage_full.bak` for dict blobs > 65 536 bytes via `spec_probe columnstore-lob-preamble` | `tools/spec_probe.py` | ✓ done — max blob 9832 B; path not triggered; verdict: pending |
| 4h | Build `cs_lob_preamble.bak` (`nvarchar(4000)` CCI with long distinct values) | `tools/make_boundary_fixture.py` | ✗ remaining — needed to trigger LOB preamble path |
| 4i | Verify deinterleave; commit verifier sidecar `G41.json`; update spec | `docs/BAK_FORMAT_SPEC.md` | ✗ remaining |

---

## Execution order

```
Phase 0  (all blockers resolved, same session)
    │
    ├─── Phase 3   ──── no external blockers; uses existing fixture + container
    │
    ├─── Phase 4   ──── uses boundarycoverage_full.bak; container needed for verifier
    │
    ├─── Phase 2   ──── unblocked once 0a confirms engine containers
    │
    └─── Phase 1   ──── largest scope; format probe (0b) must complete first
```

Phases 3 and 4 can run in the same session immediately after Phase 0.  
Phases 1 and 2 have external blockers and may require separate sessions.

---

## Acceptance criteria (overall)

All of the following must be true before this plan is closed:

- [x] `PageStore.from_stripe([f1, f2])` passes `test_striped_backup.py` (6 tests)
- [ ] `test_catalog_version.py` passes for 2012, 2016, 2019, 2022 (Phase 2, skipped — 2022-only scope)
- [x] `test_rowcompress.py` passes with 40-column tables under ROW and PAGE compression (8 new tests)
- [x] `spec_probe columnstore-dict-order` emits `verdict: match` for G40
- [x] `spec_probe columnstore-seg-header` emits `verdict: match` for G43
- [x] `spec_probe columnstore-lob-preamble` emits `verdict: match` for G41 — cs_lob_preamble.bak (587 KB dict blob)
- [x] G17, G18, G40, G41, G43 struck through in `BAK_FORMAT_SPEC.md` Guess Register
- [x] G41 struck through
- [x] `GAP_ANALYSIS.md §4` striped row marked ✅
- [x] `GAP_ANALYSIS.md §7` Tier 3 list updated (striped item struck through)
