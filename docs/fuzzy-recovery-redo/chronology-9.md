# Run 9 — Phase 2 follow-ups: compressed path verified; phase + score decode fixed

Date: 2026-06-27

## Why this run happened
Run 8 left two Phase-2 follow-ups: (a) verify the compressed (`MSSQLBAK`)
container path carries/merges the trailing modified-page run analogously to the
MTF path; (b) the `dirtycoverage_cci_delete` residual where the compressed
rowgroup's constant `phase = 'compressed'` column decoded to `''`. Both were
tackled in sequence. (b) then uncovered a third, co-located bug in the `score`
FLOAT column.

## (a) Compressed (MSSQLBAK) path — verified, one latent bug fixed
Built a **compressed fuzzy fixture** on the 2022 container: the CCI-delete
scenario backed up `WITH COMPRESSION` while a concurrent DELETE ran, looping
until a RESTORE of the result showed the delete captured (count 6,000). Tool:
`tools/diag/_diag_compressed_fuzzy.py` (adds an optional `compression=` flag to
`fixture_utils.dirty_backup_concurrent`).

Findings:
- The compressed container **does** re-store the modified pages: `_iter_pages`
  yields 42 page_ids more than once (the trailing re-copy pass).
- The **eager** path (`extract_mdf_files_compressed`) is already correct — it
  places pages last-wins and `_iter_pages` yields the re-copied (higher-LSN)
  page later, so it reflects the post-modification image. mssqlbak read 6,000,
  band(5001–6000)=0, matching the RESTORE. No change needed.
- The **lazy** path (`ChunkIndex` / `LazyPageStore`, used for ≥4 GiB) had a
  latent bug: catalog pages (<4096) are last-wins (correct), but the chunk index
  resolved a duplicated extent with `bisect_left` over a stably-sorted array,
  returning the **first** (stale, pre-modification) chunk. For a fuzzy backup
  ≥4 GiB with modified non-catalog pages this returns stale data.
  - Fix: `_FileChunkArray.lookup` now returns the **last** matching extent entry
    (`bisect_right - 1`) = latest-written copy, consistent with the eager path.
  - Tests: `tests/test_chunk_index.py` (duplicate-extent → latest wins).
  - In this fixture the modified pages are <4096, so the lazy path already read
    6,000 via the catalog cache; the fix is for the large-backup case.

## (b) `phase` (constant string) decode — fixed
`phase` is enc=3 **compact-RLE** (`bpv=1, nw=0`): one pair `(stored=4, run=5000)`,
`mn=4`, `has_null=0`, dictionary `['compressed']`. The branch computed
`shift = mn-2` and called `_dict_lookup(stored-shift)=_dict_lookup(2)`; with
`has_null=0`, `_dict_lookup` uses the raw index `dict[2]` → out of range → `''`.
The `mn-2` shift only matches `_dict_lookup`'s nullable convention
(null=0/empty=1/dict=k+2). For a non-nullable segment the shift must be `mn`
(→ `dict[stored-mn]=dict[0]='compressed'`).
- Fix: `dict_string.py::_decode_enc3` compact-RLE — `shift = (mn-2) if has_null else mn`.

## (c) `score` (FLOAT) decode — fixed (Python + Rust)
With `phase` fixed, the fixture still mismatched on `score`. The compressed
rowgroup stores `score` as enc=4 (full 64-bit), `has_null=0`, `null_val` 0/-1,
`mn = 0x3FD5555555555555` (= 1/3.0, the column minimum). The float decoder
reconstructs `actual_u64 = stored + base`; it used `null_val` as the base, which
for a non-nullable segment is meaningless, leaving every value as the raw
offset-from-minimum → NaN/denormals. The base for a non-nullable float is the
segment minimum `mn`.
- Fix (Python): `value_for.py::_decode_enc1` float branch —
  `base = null_val if has_null else mn`.
- Fix (Rust): `rust/src/columnstore.rs::decode_cs_segment` float branch — same.
  Rebuilt with `maturin develop --release`.

Why both paths: extract uses the Rust fast path only when **no log-tail
correction** runs. 2019/2022 captured the DELETE (log-tail active → Python path,
fixed by (b)/(c)-Python). 2017/2025 did not (Rust fast path), so the Rust fix was
required for those.

## Result
`dirtycoverage_cci_delete` is **fully clean on all four versions** (row count,
`phase`, `val`, `score`) in both `tests/test_dirty_backup.py` and
`tests/test_value_correctness.py`. known_gaps entry removed.

Regression check: the full columnstore + value-correctness suite shows the
**same 15 pre-existing failures** as baseline (on BIT / DATETIMEOFFSET / LOB
columns — `cci_bit:['val']`, `cs_10000:['dto']`, `rb_lob:['val']`), no float
column among them, and +7 newly-passing cci tests. ruff + pyright clean; Rust
rebuilt clean.

## Files
- `mssqlbak/chunk_index.py` — duplicate-extent → latest wins.
- `mssqlbak/columnstore/decode/dict_string.py` — compact-RLE non-nullable shift.
- `mssqlbak/columnstore/decode/value_for.py` — non-nullable float base = mn.
- `rust/src/columnstore.rs` — non-nullable float base = mn (fast path).
- `tools/fixture_utils.py` — `dirty_backup_concurrent(compression=…)`.
- `tools/diag/_diag_compressed_fuzzy.py` — compressed fuzzy experiment.
- `tests/test_chunk_index.py` — new unit tests.
- `tools/known_gaps.py` — dirtycoverage_cci_delete gap removed.

## cci_update note (out of scope)
`dirtycoverage_cci_update` still fails on 2017/2019 (`updated_rows_corrected`
NUL byte `updat\x00d_…`, and 2019 `row_count` 6686) — confirmed pre-existing on
baseline (decoder change stashed). Same fuzzy-backup REDO/sector-framing class as
the `committed_update_*` gaps; separate registered gap, not addressed here.
