# Run 10 — committed_delete_v4 phantom rows: an OPEN-block scanner gap, not missing log records

Date: 2026-06-27

## Why this run happened
`dirtycoverage_committed_delete_v4` was the last `dirtycoverage_*` fixture still
carrying a known-gap xfail. The registered reason claimed the DELETE record for
the phantom row "has sub=0x00/disc=0x00 in the log and cannot be identified as
LOP_DELETE_ROWS … genuinely absent or unrecognisable." The task was to confirm
whether that record is truly absent vs a fixable classification gap.

It is **fully fixable**: the records are present and well-formed; mssqlbak's
OPEN-block scanner was skipping them.

## What the fixture is
5,000-row clustered table `dbo.dirty_v4`; ids 1..1000 committed-DELETEd mid
(fuzzy) backup. Expected surviving rows after RESTORE: 4,000. Only SS2017
(`cells0`) failed — 4,003 rows, i.e. **3 phantom deleted rows still present**.

## Establishing ground truth (`fn_dump_dblog`)
Reading the SS2017 `.bak` directly:
- `LOP_DELETE_ROWS | LCX_MARK_AS_GHOST` × **1000** — every committed DELETE is in
  the log tail.
- Distribution of (LCX@0x0e, SUBTYPE@0x0f, DISC@0x16, len): **all 1000** are
  `02 / 00 / 03` (legacy SS2017 DML: sub=0x00, disc=0x03=DELETE). **Zero**
  records have disc≠0x03. So the old gap text (`sub=0x00/disc=0x00`, "id=372")
  was simply wrong.

## Finding the real phantoms
The actual phantoms are **id=328, 656, 984**, at physical `(file=1, page=338,
slot=48)`, `(1, 342, 8)`, `(1, 345, 60)`. mssqlbak's `committed_delete_slots`
held only **997** of 1000 — exactly these 3 missing — so the 3 rows were never
suppressed.

## Root cause
Each missing DELETE record **begins at block offset `0x30`** in an OPEN log block
(`0x329000`, `0x338000`, `0x347000`) — the first record of a new log-flush
segment. Its header is intact and correct there (marker 0x3e, LCX 0x02,
sub 0x00, disc 0x03, page/slot correct). But `iter_log_records` starts its
OPEN-block scan at the hardcoded record-area offset `_BLOCK_HDR = 0x48` and steps
in 8-byte units, so it lands *inside* this first record (on its payload) and
never matches a header. The next record at `0xe8` is found normally — which is
why exactly the **first** record of each of these 3 blocks was lost.

(The records do NOT straddle a block boundary, so the existing Pass-2 straddle
logic did not apply; and the blocks are OPEN, not CONT, so Pass-1 skipped them.)

## Fix
`mssqlbak/logtail.py::_iter_cont_records` — Pass 1 now also scans the
`[0, _BLOCK_HDR)` **prefix** of OPEN blocks (in addition to scanning CONT blocks
in full). `iter_log_records` still owns `[_BLOCK_HDR, end)`, and a prefix record
spans past 0x48, so the main scan never re-yields it — no duplicates. The
existing strict guards (LCX==0x02, valid subtype, non-zero xact_id, legacy-DML
marker 0x3e, page_id≠0) keep the header region from producing false positives.

## Result
`dirtycoverage_committed_delete_v4` reads exactly **4,000** rows; `cells0`
(SS2017) now passes alongside cells1/2/3. The known_gaps entry is removed.

Regression: the 5 `test_dirty_backup.py::test_committed_*` failures and the 13
columnstore/LOB `test_value_correctness` failures observed are **identical with
and without** this change (verified by stashing `logtail.py`) — all pre-existing,
none introduced here. ruff + pyright clean.

## Files
- `mssqlbak/logtail.py` — `_iter_cont_records` scans OPEN-block `[0, 0x48)` prefix.
- `tools/known_gaps.py` — `dirtycoverage_committed_delete_v4` gap removed.
- `tools/diag/_diag_cdv4_phantom.py` — verifier (reports phantom ids + physical
  location vs `committed_delete_slots`).
