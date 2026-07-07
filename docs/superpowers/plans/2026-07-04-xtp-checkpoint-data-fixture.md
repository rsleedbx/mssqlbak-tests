# XTP Checkpoint DATA-file Fixture + Decoder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Also read before starting** (paths are absolute skill files, read with the Read tool):
> - `/Users/robert.lee/github/mssqlbak/.cursor/skills/mssqlbak-fixtures/SKILL.md` — canonical fixture-generation commands & wiring checklist
> - `/Users/robert.lee/github/mssqlbak/.cursor/skills/mssqlbak-diag/SKILL.md` — how to write diagnostic scripts
> - `/Users/robert.lee/github/mssqlbak/.cursor/skills/format-reverse-engineering/SKILL.md` — the RE cycle for Phase 2
> - `/Users/robert.lee/github/mssqlbak/.cursor/skills/decode-bug-workflow/SKILL.md` — end-to-end decoder-fix workflow
> - forgedb RAM prep: `docs/notes/2026-07-04-forgedb-mcp-fixes-for-large-xtp-fixtures.md`

**Goal:** Recover the residual XTP checkpoint *straddle* rows (row images whose
payload tails cross a 64 KB checkpoint-chunk boundary and are clobbered in the
log stream) by building a large, compressed, checkpoint-flushed memory-optimized
`.bak` fixture with known ground truth, reverse-engineering the checkpoint
DATA-file layout against it, and implementing a decoder so both the new synthetic
fixture and `AdventureWorks2016_EXT`'s `SalesOrderHeader_inmem` /
`SalesOrderDetail_inmem` land byte-exact + complete.

**Architecture:** Three phases. **Phase 1 (concrete):** generate a single-version
SS2022 fixture — a `MEMORY_OPTIMIZED … DURABILITY = SCHEMA_AND_DATA` table with
tens of thousands of variable-width rows, `CHECKPOINT`, `BACKUP … WITH
COMPRESSION` — and wire it into the `xtp_*` suite. The dense `IDENTITY(1,1)` +
`seq` completeness gates in `mssqlbak/xtp.py` will *refuse* it until every
straddle row is recovered, so the coverage test is the pass/fail signal for the
decoder. **Phase 2 (exploratory RE):** using the fixture's known `{1..N}` ids,
locate the currently-dropped page-classified checkpoint DATA regions, find the
missing straddle ids there, and reverse-engineer their container framing.
**Phase 3 (implementation):** add a checkpoint DATA-file recovery path to
`scan_cfp_log_records`, guard it so existing fixtures don't regress, and land the
tables.

**Tech Stack:** Python 3 (`.venv/bin/python`), SQL Server 2022 in a forgedb
Podman container, `tools/fixture_run` + `tools/fixture_utils`, `pytest`,
`deltalake`, `mssqlbak/xtp.py`, `mssqlbak/compressed.py`.

---

## Why a *large*, *compressed* fixture (read before Phase 1)

Three fixture properties are load-bearing — get any wrong and the fixture cannot
reproduce the bug:

1. **Compressed.** Pass 3 (`scan_cfp_log_records` → `decode_cfp_log_records`) runs
   **only for MSSQLBAK-compressed input** (see the "Landed wiring" section of
   `docs/notes/2026-07-03-adventureworks-xtp-investigation.md`). The existing
   `xtp_rich` fixture uses plain `BACKUP` (uncompressed) and therefore exercises
   the compact/WAL path, **not** the checkpoint-container path. This fixture
   **must** use `BACKUP … WITH COMPRESSION`.
2. **Large + checkpointed.** Straddle rows only exist once frozen rows are flushed
   into 64 KB XTP checkpoint DATA chunks. A small table keeps all rows in the log
   tail (no chunk boundaries, no straddle). We need enough variable-width rows
   (tens of thousands) plus an explicit `CHECKPOINT` so the data spills across
   many 64 KB chunk boundaries.
3. **Variable-width rows with a dense `{1..N}` key.** Variable width is what makes
   a payload tail land across a chunk boundary. A dense `IDENTITY(1,1)` key gives
   an exact, runtime-checkable completeness signal (`{1..N}`) *and* lets Phase 2
   name the exact missing ids to hunt for in the dropped regions.

## Prerequisite: free RAM on the forgedb Lima VM

The Lima VM is **~15.6 GB total** (not 24 GB — corrected 2026-07-04 via
`host_resources`). Building a large memory-optimized table + checkpoint files is
RAM-hungry, so stop the SQL Server versions you are not using and raise the 2022
cap. All steps go through the forgedb MCP (never shell out to podman).

- [ ] **Prep step 1: read current headroom**

Call MCP tool `host_resources` (server `user-forgedb`). Note `vm.available_gb`
and each container's `memory_cap_gb`.

- [ ] **Prep step 2: stop the unused versions**

Call `stop_sqlserver_podman` (server `user-forgedb`) three times with
`{"version": "2017"}`, `{"version": "2019"}`, `{"version": "2025"}`.

- [ ] **Prep step 3: raise the 2022 cap and (re)start it**

Call `start_sqlserver_podman` with `{"version": "2022", "ram_gb": 12}`.
(Pick `ram_gb` ≤ `vm.available_gb` freed in step 2 + 2022's existing 8 GB cap;
12 is a safe start for ~100 k small rows. Re-run `host_resources` to confirm.)

- [ ] **Prep step 4: confirm exactly one SQL Server is up**

Call `list_running_containers`; expect only the `*-mssql-2022-*` entry
(ignore the duplicate `lima-rosetta2-podman` listing — it is a display artifact).
Record the container blob stem (e.g. `robert-lee-mssql-2022-mcr-local-1779207800`)
for `--server` in Phase 1.

- [ ] **Prep step 5 (restore, run LAST — after Phase 1's fixture is copied out):**

`start_sqlserver_podman` with `{"version": "2017"}`, `{"version": "2019"}`,
`{"version": "2025"}` to bring the other versions back.

> If any `setup_*`/`start_*` fails with an OOM-like error (container exited 137),
> lower `ram_gb` or reduce `FILLER_COUNT` in Phase 1 and retry.

---

## Phase 1 — Build & wire the large compressed straddle fixture

This phase is fully concrete and independently testable: at the end the fixture
exists, ground truth is registered, and the coverage test **fails** in a
*specific, expected* way (table refused by the completeness gate because straddle
rows are still dropped). That expected failure is the entry condition for Phase 2.

### Task 1: Fixture generator

**Files:**
- Create: `tools/make_xtp_checkpoint_fixture.py`

Model exactly on `tools/make_xtp_rich_fixture.py` (same imports, same
`skip_if_exists`/`fixture_credentials`/`load_and_backup_stmts`/`_copy_out`
scaffold). Key differences: `WITH COMPRESSION`, an explicit `CHECKPOINT`, and a
large variable-width insert driven by `seed_sql`.

- [ ] **Step 1: Write the generator**

```python
#!/usr/bin/env python3
"""Generate ``xtp_checkpoint_straddle_full.bak``.

A large, COMPRESSED memory-optimized fixture whose frozen rows flush into 64 KB
XTP checkpoint DATA chunks.  Variable-width nvarchar payloads make row images
straddle chunk boundaries — the exact condition that clobbers a row's tail in
the log stream and forces checkpoint DATA-file recovery.  A dense IDENTITY(1,1)
key gives an exact {1..N} completeness signal.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
    skip_if_exists,
)

DB_NAME = "XtpCheckpointStraddle"
TABLE = "xtp_ckpt"

# Number of rows.  100k variable-width rows (avg ~200 B) → ~20 MB of checkpoint
# data → hundreds of 64 KB chunks → dozens of straddle rows.  Large enough to
# force checkpoint DATA files, small enough for a 12 GB cap.
ROW_COUNT = 100_000
# payload width cycles 1..PAYLOAD_MOD chars so row images are variable-length.
PAYLOAD_MOD = 400

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "xtp_checkpoint_straddle_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def expected_payload_len(id_: int) -> int:
    """Deterministic nvarchar length for a 1-based id.

    Mirrors the generator SQL exactly: pk is 0-based (pk = id - 1), width =
    1 + (pk % PAYLOAD_MOD).  Kept importable so the coverage test derives
    expected values from the SQL, not from memory.
    """
    pk = id_ - 1
    return 1 + (pk % PAYLOAD_MOD)


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_XTP] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'xtp_ckpt_data',
    FILENAME = N'/var/opt/mssql/data/xtp_ckpt_data'
) TO FILEGROUP [FG_XTP]""",
        f"USE [{DB_NAME}]",
    ]
    # fkr__seed(pk INT PRIMARY KEY) with pk = 0..ROW_COUNT-1 (disk table).
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id      INT            NOT NULL IDENTITY(1,1),
    width   INT            NOT NULL,
    payload NVARCHAR(400)  NOT NULL,
    CONSTRAINT pk_{TABLE} PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        # Insert in seed (pk) order so IDENTITY id == pk + 1 deterministically.
        f"""INSERT INTO dbo.{TABLE} (width, payload)
SELECT 1 + (pk % {PAYLOAD_MOD}) AS width,
       REPLICATE(N'x', 1 + (pk % {PAYLOAD_MOD})) AS payload
FROM (SELECT pk FROM fkr__seed WHERE pk < {ROW_COUNT}) AS _f
ORDER BY pk""",
        # Freeze rows into XTP checkpoint DATA files.
        "CHECKPOINT",
        "USE [master]",
        # COMPRESSION is REQUIRED — Pass 3 only runs for MSSQLBAK-compressed input.
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' "
        f"WITH FORMAT, INIT, COPY_ONLY, COMPRESSION",
    ]
    return stmts


def main(force: bool = False) -> int:
    if skip_if_exists(OUT_PATH, force=force):
        return 0
    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"creating XTP checkpoint-straddle fixture: {ROW_COUNT:,} rows")
    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
```

- [ ] **Step 2: Verify the module imports and `INSERT … SELECT … ORDER BY` is valid**

`INSERT … SELECT` into a memory-optimized table from a disk table is supported.
The `ORDER BY pk` guarantees IDENTITY assignment order so `id == pk + 1`.

Run: `.venv/bin/python -c "import tools.make_xtp_checkpoint_fixture as m; print(len(m.build_stmts()), m.expected_payload_len(1), m.expected_payload_len(401))"`
Expected: prints a statement count, `1`, `1` (id 401 → pk 400 → 400 % 400 = 0 → width 1).

- [ ] **Step 3: Commit**

```bash
git add tools/make_xtp_checkpoint_fixture.py
git commit -m "feat(fixtures): add large compressed XTP checkpoint-straddle generator"
```

### Task 2: Wire the generator into `tools/fixture_run.py`

**Files:**
- Modify: `tools/fixture_run.py` (add runner near `_run_xtp_rich` ~line 758; add to
  `_COMMANDS` dict ~line 1077; add subparser near line 1858; add dispatch near
  line 2446). **Do NOT add it to `_ALL_VERSIONS_SUITE`** — it is single-version,
  large, and RAM-heavy.

- [ ] **Step 1: Add the runner function** (place after `_run_xtp_rich`)

```python
def _run_xtp_checkpoint(*, force: bool = False) -> int:
    from tools.make_xtp_checkpoint_fixture import main

    return main(force=force)
```

- [ ] **Step 2: Register in `_COMMANDS`** (next to `"xtp-rich": _run_xtp_rich,`)

```python
    "xtp-checkpoint": _run_xtp_checkpoint,
```

- [ ] **Step 3: Add the argparse subparser** (next to the `xtp-rich` subparser)

```python
    xtp_ckpt_p = sub.add_parser(
        "xtp-checkpoint",
        help=(
            "xtp_checkpoint_straddle_full.bak — LARGE compressed memory-optimized "
            "fixture (100k variable-width rows + CHECKPOINT) that flushes XTP "
            "checkpoint DATA chunks and induces boundary-straddle rows"
        ),
    )
    xtp_ckpt_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
```

- [ ] **Step 4: Add command dispatch in `main()`** (next to the `xtp-rich` dispatch)

```python
    if args.command == "xtp-checkpoint":
        return _run_xtp_checkpoint(force=getattr(args, "force", False))
```

- [ ] **Step 5: Verify wiring without a container**

Run: `.venv/bin/python -m tools.fixture_run --help | grep xtp-checkpoint`
Expected: the `xtp-checkpoint` line appears.

- [ ] **Step 6: Commit**

```bash
git add tools/fixture_run.py
git commit -m "feat(fixtures): wire xtp-checkpoint into fixture_run (single-version)"
```

### Task 3: Register the fixture path + pytest fixture in conftest

**Files:**
- Modify: `tests/conftest.py` (path constant near line 336; `fixture_bak_*`
  provider near line 1347)

- [ ] **Step 1: Add the path constant** (after `FIXTURE_BAK_XTP_RICH`)

```python
# Large compressed XTP fixture that flushes checkpoint DATA chunks and induces
# boundary-straddle rows (drives the checkpoint DATA-file decoder).
FIXTURE_BAK_XTP_CHECKPOINT = (
    _FIXTURE_DIR / "xtp_checkpoint_straddle_full.bak"
)
```

- [ ] **Step 2: Add the pytest fixture provider** (after `fixture_bak_xtp_rich`)

```python
@pytest.fixture
def fixture_bak_xtp_checkpoint() -> Path:
    """Path to the large XTP checkpoint-straddle fixture."""
    if not FIXTURE_BAK_XTP_CHECKPOINT.exists():
        pytest.skip(
            f"xtp-checkpoint fixture missing: {FIXTURE_BAK_XTP_CHECKPOINT} "
            "(run: python -m tools.fixture_run --fixture-dir tests/fixtures_2022 xtp-checkpoint)"
        )
    return FIXTURE_BAK_XTP_CHECKPOINT
```

- [ ] **Step 3: Verify the fixture is collectable (skips cleanly when absent)**

Run: `.venv/bin/python -m pytest tests/test_xtp_rich_coverage.py --collect-only -q`
Expected: collection succeeds (proves conftest still imports).

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py
git commit -m "test(fixtures): register xtp_checkpoint_straddle conftest fixture"
```

### Task 4: Coverage test (asserts complete + byte-exact recovery)

**Files:**
- Create: `tests/test_xtp_checkpoint_coverage.py`

This test is the decoder's pass/fail signal. It will **fail** after Phase 1
(rows dropped ⇒ incomplete) and **pass** once Phase 3's decoder recovers every
straddle row. Derive expected widths from the generator, per the fixtures skill.

- [ ] **Step 1: Write the test**

```python
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake

from mssqlbak.extract import extract_bak_to_delta
from tools.make_xtp_checkpoint_fixture import ROW_COUNT, expected_payload_len


def _extract_table(bak: Path, name: str) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(bak), tmp)
        table_dir = Path(tmp) / "dbo" / name
        if not table_dir.is_dir():
            return []
        return deltalake.DeltaTable(str(table_dir)).to_pyarrow_table().to_pylist()


def test_xtp_checkpoint_recovers_every_row(fixture_bak_xtp_checkpoint: Path) -> None:
    rows = _extract_table(fixture_bak_xtp_checkpoint, "xtp_ckpt")
    ids = sorted(r["id"] for r in rows)
    # Completeness: the dense IDENTITY(1,1) key must enumerate {1..N} with no gaps.
    assert ids == list(range(1, ROW_COUNT + 1)), (
        f"expected {ROW_COUNT} contiguous ids 1..{ROW_COUNT}, "
        f"got {len(ids)} (first gap reveals dropped straddle rows)"
    )


def test_xtp_checkpoint_payloads_byte_exact(fixture_bak_xtp_checkpoint: Path) -> None:
    rows = {r["id"]: r for r in _extract_table(fixture_bak_xtp_checkpoint, "xtp_ckpt")}
    # Spot-check a spread of ids, including likely boundary-straddle rows.
    for id_ in (1, 2, 400, 401, 12_345, ROW_COUNT // 2, ROW_COUNT - 1, ROW_COUNT):
        row = rows.get(id_)
        assert row is not None, f"row id={id_} missing (dropped straddle row)"
        want_len = expected_payload_len(id_)
        assert row["width"] == want_len
        assert row["payload"] == "x" * want_len
```

- [ ] **Step 2: Verify it collects**

Run: `.venv/bin/python -m pytest tests/test_xtp_checkpoint_coverage.py --collect-only -q`
Expected: 2 tests collected.

- [ ] **Step 3: Commit**

```bash
git add tests/test_xtp_checkpoint_coverage.py
git commit -m "test(xtp): coverage test asserting complete + byte-exact checkpoint recovery"
```

### Task 5: Generate the fixture and register ground truth

**Files:** none (produces `tests/fixtures_2022/xtp_checkpoint_straddle_full.bak`
+ `.stats.json` + `.cells`).

- [ ] **Step 1: Generate the `.bak` on SS2022 only**

Use the `--server` stem recorded in Prereq step 4 (only needed if >1 server is
up; after the prereq you should have only 2022 running, so `--server` is optional
but harmless):

Run:
```bash
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 xtp-checkpoint
```
Expected: `wrote .../xtp_checkpoint_straddle_full.bak (… bytes)`. If it fails with
OOM (exit 137), lower `ROW_COUNT` (e.g. 60_000) or raise the 2022 `ram_gb`, then
re-run with `--force`.

- [ ] **Step 2: Register `.stats.json` and `.cells` ground truth**

Run (interactive terminal, NOT nohup — this goes through the forgedb socket; see
the fixtures skill):
```bash
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-bak xtp_checkpoint_straddle_full.bak
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-all --cells-only
```
Expected: `xtp_checkpoint_straddle_full.bak.stats.json` and `.cells` appear
alongside the `.bak`. Confirm the stats report `xtp_ckpt` row count == `ROW_COUNT`.

- [ ] **Step 3: Run the restore prereq cleanup (Prereq step 5) now**

Bring the other SQL Server versions back up via `start_sqlserver_podman`.

- [ ] **Step 4: Run the coverage test — expect a SPECIFIC failure**

Run: `FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_xtp_checkpoint_coverage.py -v`
Expected: **FAIL** — `test_xtp_checkpoint_recovers_every_row` reports fewer than
`ROW_COUNT` ids (a gap), and/or `test_xtp_checkpoint_payloads_byte_exact` reports
a missing boundary id. This confirms the fixture reproduces the straddle bug.

> **Decision gate G1:** If the test *passes* here, the fixture did NOT reproduce
> the bug (rows all stayed in the log tail, or checkpoint data was fully
> recovered by the existing container model). Increase `ROW_COUNT` and/or
> `PAYLOAD_MOD` variance and regenerate with `--force`, or add a second `CHECKPOINT`
> after a delete/re-insert to force more chunk turnover. Do not proceed to Phase 2
> until the fixture demonstrably drops straddle rows. Record the observed
> dropped-id set (from step 4's assertion output) — Phase 2 needs it.

- [ ] **Step 5: Commit the fixture + ground truth**

```bash
git add tests/fixtures_2022/xtp_checkpoint_straddle_full.bak \
        tests/fixtures_2022/xtp_checkpoint_straddle_full.bak.stats.json \
        tests/fixtures_2022/xtp_checkpoint_straddle_full.bak.cells
git commit -m "test(fixtures): add xtp_checkpoint_straddle SS2022 fixture + ground truth"
```

---

## Phase 2 — Reverse-engineer the checkpoint DATA-file container (EXPLORATORY)

**This phase is genuine reverse engineering; its exact byte layout is not known
in advance.** Follow `format-reverse-engineering/SKILL.md` (alternate bottom-up
probing with top-down corroboration) and write probes per `mssqlbak-diag/SKILL.md`
(scripts under `tools/diag/_diag_xtp_*.py`). The synthetic fixture is the
advantage: you know the *exact* set of missing ids (from G1) and each row's exact
payload (`"x" * expected_payload_len(id)`), so you can search the dropped regions
for known byte patterns instead of guessing.

Known starting facts (from `docs/notes/2026-07-03-adventureworks-xtp-investigation.md`):
- Straddle rows are dropped by the current scanner in `mssqlbak/xtp.py` — either
  (a) their header→preamble straddle is refused (`_CKPT_PREAMBLE_SIG not in payload`
  guard, `xtp.py:771`), or (b) their intact copy lives in a 64 KB chunk currently
  classified as a *page* and skipped by the strict page test (`xtp.py:705-713`).
- The intact straddle row is believed to exist in a page-classified checkpoint
  DATA region (~hundreds of MB dropped on the real fixture).
- Checkpoint DATA rows otherwise use the **identical** header-first framing +
  payload layout as the log tail (`[u32 size][u32 flags=0x8000_00LB][u32 seq]
  [u32 marker][u32 pad=0][payload]`, stride `20 + size`).

### Task 6: Locate the missing straddle rows in the decompressed stream

**Files:**
- Create: `tools/diag/_diag_xtp_ckpt_locate.py`

- [ ] **Step 1: Write a probe that finds the missing ids' payload bytes**

The probe must: decompress the fixture (reuse
`mssqlbak.compressed.iter_decompressed_chunks`), take the missing-id set from G1,
build each missing row's known payload bytes (the UTF-16LE of `"x"*width`, plus
the fixed `id`/`width` little-endian ints), and `bytes.find` them across **all**
decompressed chunks — *including the page-classified ones the scanner drops*.
Report, per missing id: which chunk index it lands in, the chunk's first 16 bytes
(`is_page`? preamble?), and the byte offset within the chunk.

Follow the diag-script conventions in `mssqlbak-diag/SKILL.md` (argparse over a
`--bak` path defaulting to the new fixture; print a compact table).

- [ ] **Step 2: Run it and classify where missing rows live**

Run: `.venv/bin/python -m tools.diag._diag_xtp_ckpt_locate`
Expected: each missing id is found in exactly one region. Classify: are they in
(a) page-classified dropped chunks, (b) across a chunk seam, or (c) truly absent?

> **Decision gate G2:**
> - If missing rows are found intact in **page-classified dropped chunks** →
>   Phase 3 = relax/branch the page test to also scan those chunks as a checkpoint
>   DATA region.
> - If missing rows **straddle a seam** but both halves are present in adjacent
>   chunks (log-tail + next chunk) → Phase 3 = reassemble across the seam instead
>   of dropping.
> - If a missing row is **truly absent** from the decompressed stream → the row is
>   not recoverable from this backup; STOP and document (guardrail 4: no partial
>   decode). Re-examine whether the fixture's `CHECKPOINT`/backup captured it.

### Task 7: Reverse-engineer the DATA-file record framing

**Files:**
- Create: `tools/diag/_diag_xtp_ckpt_frame.py`

- [ ] **Step 1: Dump the bytes around a known missing row**

For one missing id located in Task 6, dump ~256 bytes before and after its
payload. Identify: the record header (does the 20-byte header precede it? is it
clobbered/zeroed like B2.3a?), the enclosing chunk's preamble, and the stride to
the neighbouring records.

- [ ] **Step 2: Confirm the framing hypothesis on ≥5 missing rows**

Verify the same framing reproduces for at least 5 distinct missing ids spread
across different chunks. A format claim that holds on one row is a coincidence;
holding on 5+ across chunks is a pattern.

- [ ] **Step 3: Corroborate top-down**

Cross-check against `docs/spec/08_XTP_CHECKPOINT.md` and the corroboration
sources already cited in the investigation note (§B2.5). Record findings inline
in the note (see Task 11). Per `format-reverse-engineering/SKILL.md`, do not ship
a layout supported only by bottom-up probing without a corroboration attempt.

> **Decision gate G3:** Write down the exact recovery rule as pseudocode before
> writing production code — e.g. "for each dropped chunk beginning with
> `_CKPT_PREAMBLE_SIG`, skip `K` preamble bytes, then walk header-first records at
> stride `20 + size` until `< _LOG_MIN_CHAIN` valid headers remain." If you cannot
> state the rule precisely, you are not done with Phase 2.

---

## Phase 3 — Implement, guard, and land

### Task 8: Add checkpoint DATA-file recovery to the scanner

**Files:**
- Modify: `mssqlbak/xtp.py` — `scan_cfp_log_records` (`:667-783`); add a helper
  near it; possibly add a constant near the checkpoint block (`:267-276`).

- [ ] **Step 1: Write the recovery per the G3 rule**

Implement the exact rule from G3 as a focused helper (e.g.
`_scan_ckpt_data_chunk(chunk: bytes) -> list[tuple[int, int, bytes]]`) and call
it for the chunks the current strict page test drops. Reuse `_read_log_header`
and the existing salvage/straddle logic — do not duplicate framing code (DRY).
Dedup recovered rows into the existing `lb_seen` map by `seq` (or decoded
identity, matching the existing `.setdefault(seq, …)` policy at `:777`).

> Keep the change **local to the XTP scanner**. Do NOT modify
> `compressed.py`'s shared page logic (the note, §B2.4 step 1, warns against this).

- [ ] **Step 2: Run the new fixture's coverage test — expect PASS**

Run: `FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_xtp_checkpoint_coverage.py -v`
Expected: both tests PASS (all `ROW_COUNT` ids present; sampled payloads exact).

- [ ] **Step 3: Commit**

```bash
git add mssqlbak/xtp.py
git commit -m "feat(xtp): recover checkpoint DATA-file straddle rows"
```

### Task 9: Guard against regression on existing XTP fixtures + AdventureWorks

**Files:** none (verification); fix `mssqlbak/xtp.py` if a regression appears.

- [ ] **Step 1: Synthetic XTP fixtures still decode**

Run: `FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_xtp_coverage.py tests/test_xtp_rich_coverage.py tests/test_xtp_checkpoint_coverage.py -v`
Expected: all PASS.

- [ ] **Step 2: AdventureWorks2016_EXT value-correctness (the real payoff)**

Run: `.venv/bin/python tools/diag/_cli.py cells-diff AdventureWorks2016_EXT.bak --all-versions`
(Also run the value-correctness test if the fixture is present:
`.venv/bin/python -m pytest "tests/test_value_correctness.py::test_fixture_cells_match_ground_truth" -k AdventureWorks2016_EXT -v`.)
Expected: `SalesOrderHeader_inmem` and `SalesOrderDetail_inmem` now land
byte-exact + complete (or, if still short, Task 6's G2 classification told you why
— resolve or keep them documented as skipped; do NOT ship partial).

> **Decision gate G4:** If AdventureWorks SOH/SOD still do not complete but the
> synthetic fixture does, the real backup's straddle rows differ from the
> synthetic ones (e.g. two payload shapes for SOD, per the note §B2.3b). Either
> extend the recovery rule to cover the real shape, or update
> `tools/known_gaps.py` with the *refined* reason. Never mark them landed unless
> `.cells` matches.

- [ ] **Step 3: Update known-gaps if SOH/SOD landed**

**Files:** Modify `tools/known_gaps.py` (`KNOWN_SKIPPED_TABLES["AdventureWorks2016_EXT"]`).
If both tables now land, remove them from the skip list. If only some land, update
the entry to the precise remaining reason.

- [ ] **Step 4: Commit**

```bash
git add tools/known_gaps.py
git commit -m "fix(xtp): land AdventureWorks SOH/SOD via checkpoint recovery"
```

### Task 10: Lint & type gates

- [ ] **Step 1: Run ruff + pyright on every changed file**

Run:
```bash
ruff check tools/make_xtp_checkpoint_fixture.py tools/fixture_run.py \
  tests/conftest.py tests/test_xtp_checkpoint_coverage.py mssqlbak/xtp.py \
  tools/diag/_diag_xtp_ckpt_locate.py tools/diag/_diag_xtp_ckpt_frame.py \
  tools/known_gaps.py
pyright mssqlbak/xtp.py tools/make_xtp_checkpoint_fixture.py tools/diag/_diag_xtp_ckpt_locate.py tools/diag/_diag_xtp_ckpt_frame.py
```
Expected: `All checks passed!` and `0 errors`. Fix root causes (no `# noqa`/
`# type: ignore` suppression except the existing `# noqa: E402` sys.path pattern).

- [ ] **Step 2: Commit any lint fixes**

```bash
git add -A && git commit -m "chore: lint/type fixes for xtp checkpoint work"
```

### Task 11: Documentation

**Files:**
- Modify: `docs/notes/2026-07-03-adventureworks-xtp-investigation.md` — add a
  dated "Resolution 3 — checkpoint DATA-file recovery" section with the G3 rule
  and Task 7's corroboration.
- Modify: `docs/correctness_coverage_AdventureWorks2016_EXT.md` and
  `docs/correctness_coverage_fixtures_realworld.md` — reflect SOH/SOD status.
- Prune superseded `tools/diag/_diag_xtp_*.py` scripts that Task 6/7 replace
  (per the investigation note's repro-script list), keeping only the ones the
  final note references.

- [ ] **Step 1: Write the resolution note + update coverage docs**

Follow `docs-writing-style/SKILL.md`. Mark empirical claims `[EMPIRICAL]` and
corroborated ones with their source, matching the existing note's convention.

- [ ] **Step 2: Commit**

```bash
git add docs/ tools/diag/
git commit -m "docs(xtp): document checkpoint DATA-file recovery; prune stale diags"
```

---

## Self-Review checklist (run before handoff)

- [ ] **Fixture reproduces the bug:** Phase 1 ends with a *failing* coverage test
  for a specific missing-id reason (gate G1), not a green one.
- [ ] **Compression is on:** the generator uses `BACKUP … WITH COMPRESSION`
  (without it, Pass 3 never runs and the fixture is inert).
- [ ] **Single-version:** `xtp-checkpoint` is NOT in `_ALL_VERSIONS_SUITE`.
- [ ] **Wiring is complete (5 places):** generator, `fixture_run` runner +
  `_COMMANDS` + subparser + dispatch, conftest path + provider, coverage test.
- [ ] **No shared-page-logic change:** `compressed.py` untouched; recovery is
  local to `scan_cfp_log_records`.
- [ ] **No partial decode:** if a table cannot be completed byte-exact, it stays
  skipped with a precise `known_gaps.py` reason (guardrail 4).
- [ ] **Names consistent across tasks:** `xtp-checkpoint` (command),
  `xtp_checkpoint_straddle_full.bak` (file), `dbo.xtp_ckpt` (table),
  `ROW_COUNT`/`expected_payload_len` (importable from the generator),
  `FIXTURE_BAK_XTP_CHECKPOINT`/`fixture_bak_xtp_checkpoint` (conftest).
- [ ] **RAM restored:** the three stopped SQL Server versions are restarted
  (Prereq step 5) before finishing.

## Notes on scope & risk

| Concern | Note |
|---|---|
| Phase 2 is open-ended RE | The exact DATA-file byte layout is proprietary and empirical-only (investigation note §B2.5). Phases 1 + 3 are concrete; Phase 2 uses the synthetic fixture's known ground truth to bound the search. Gates G2/G3 stop wasted effort if a row is truly unrecoverable. |
| Fixture may not straddle on first try | Gate G1 forces regeneration with more rows / more width variance until straddle rows are demonstrably dropped. |
| RAM | Lima VM is ~15.6 GB; keep only SS2022 up during generation and cap it ≤ ~12 GB. Lower `ROW_COUNT` on OOM (exit 137). |
| AdventureWorks may need shape-specific handling | SOD has two payload shapes (56/80 B). The synthetic fixture uses one shape; if the real backup needs more, extend the rule in Task 9 G4 or document the residual gap. |
