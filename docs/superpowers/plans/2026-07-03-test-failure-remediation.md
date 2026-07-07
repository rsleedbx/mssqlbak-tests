# Test-suite failure remediation (2026-07-03)

**Audience:** an implementing agent (Sonnet-medium is fine). Every step has an
exact command, an expected result, and a checkable end state. Do **not**
improvise beyond this plan — the pre-existing failures are deliberately left
untouched and are listed so you don't rabbit-hole into them.

---

## 0. Context

While finishing the `fix(columnstore): reserve enc=3 dict data_id slots`
commit (`a1569b2`, already on `feat/bak-to-delta`), a full `pytest` run
surfaced failures. Each has been triaged into one of three buckets:

- **STALE-TEST** — the production code is correct; the test encodes an
  outdated expectation. Fix = update the test.
- **BENIGN-BASELINE** — a decode heuristic changed branch but still produces
  correct values (cell digests pass). Fix = regenerate the recorded baseline.
- **PRE-EXISTING / UNRELATED** — fails on the branch base too, in code paths
  this branch never touched. **Leave alone.**

The branch commits (`origin/feat/bak-to-delta..HEAD`) only modified
`mssqlbak/columnstore/*` and `mssqlbak/columnstore/storage/lob.py`. Any failure
outside columnstore decode is therefore pre-existing by construction.

### Root cause of the STALE-TEST bucket

Commit `f99f370` ("fix(cells): resolve cell-level digest mismatches") changed
`_decode_char` (`mssqlbak/types.py`) so that a byte with no code-page
representation decodes to the literal `'?'` (U+003F) instead of the Unicode
replacement char `'\ufffd'` (U+FFFD). This matches live SQL Server's code-page
conversion and was validated by real fixture cell digests. Several unit tests
still assert the old `'\ufffd'` behaviour. **The code is correct; the tests are
stale.** Do not revert `_decode_char`.

---

## 1. Full failure inventory

| # | Test | Bucket | Action |
|---|------|--------|--------|
| 1 | `test_unicode_decode.py` — 10 tests (`test_undefined_cp1252_byte_yields_replacement[*]`, `test_undefined_byte_mid_string_replaces_only_bad_byte`, `test_multiple_undefined_bytes`, `test_0x8f_is_cyrillic_dzhe_in_cp1251`, `test_invalid_utf8_byte_yields_replacement`, `test_truncated_utf8_sequence_yields_replacement`) | STALE-TEST | **Already fixed** in working tree — verify & keep |
| 2 | `test_mixed_collation_coverage.py::TestDecodeCharEncodingBoundary::test_cp1252_undefined_byte_replaced` | STALE-TEST | **Already fixed** in working tree — verify & keep |
| 3 | Collection abort: `tools/diag/pr_review_sort_test.py` (`ValueError: not enough values to unpack (expected 3, got 2)`) | STALE throwaway diag | **Already deleted** in working tree — verify & keep |
| 4 | `test_decode_path_census.py::test_census_matches_baseline` | BENIGN-BASELINE | **Regenerate baseline** (Phase 2) |
| 5 | `test_record_layer.py::test_uniquifier_none_row_count`, `test_uniquifier_none_code_values`, `test_uniquifier_row_row_count` | PRE-EXISTING | Leave |
| 6 | `test_value_correctness.py::test_fixture_cells_match_ground_truth[AdventureWorks2016_EXT.bak.cells]` | PRE-EXISTING (XTP gap) | Leave |
| 7 | `test_samples.py::test_sample_bak_converts_to_delta[AdventureWorks2016_EXT.bak]`, `[WideWorldImporters-Full.bak]`, `[WideWorldImporters-Full_old.bak]`, `[WideWorldImportersDW-Full.bak]` | PRE-EXISTING | Leave |
| 8 | `test_sink_perf.py::test_delta_sink[tde_full]`, `test_pg_sink[tde_full]` | PRE-EXISTING (TDE) | Leave |
| 9 | `test_sink_perf.py::test_delta_sink[corrupt_metadata_confidence_full]`, `test_pg_sink[corrupt_metadata_confidence_full]` | PRE-EXISTING (fixture stub) | Leave |
| 10 | `test_correctness_coverage_cli.py::test_run_one_marks_expected_skipped_tables_without_bad_columns` | PRE-EXISTING (stale API ref) | Leave |
| 11 | `test_extract_e2e.py::test_extract_writes_all_tables` | PRE-EXISTING (JSON-type gap) | Leave |

> The full-suite run was interrupted at ~97% (a slow sample/sink test hung on
> a missing resource). The last ~3% may contain a few more failures in the
> same PRE-EXISTING families (sample conversion, TDE, XTP). If any new failure
> appears there, classify it with the Phase-0 method before acting; do **not**
> assume it is in scope.

### Why the PRE-EXISTING failures are out of scope (evidence)

- **#5 uniquifier** — record-layer/heap code; `git diff --name-only
  origin/feat/bak-to-delta..HEAD` shows no record-layer file changed.
- **#6 value_correctness[AdventureWorks]** — failure text is
  `Demo.*Seed / *_inmem: absent from decode` → In-Memory OLTP (XTP) tables,
  a documented gap unrelated to columnstore decode.
- **#8 tde_full** — `mssqlbak.errors.EncryptionError`; TDE backups need a
  certificate/DEK that isn't available.
- **#9 corrupt_metadata_confidence_full** — `ValueError: ... too small to
  contain an MDF page image`; the `.bak` is a truncated stub fixture.
- **#10 correctness_coverage_cli** — `AttributeError: module
  tools.correctness_coverage has no attribute 'extract_bak_to_delta'`; the test
  references a removed/renamed helper.
- **#11 extract_e2e** — `TableNotFoundError: .../dbo/t_native_json`; a native
  JSON-typed table isn't written to Delta (type-support gap).

---

## Phase 0 — Verify state before doing anything

```bash
cd /Users/robert.lee/github/mssqlbak
git status --short
git log --oneline -1          # expect a1569b2 fix(columnstore): reserve enc=3 dict...
```

**Expected working tree (already-applied fixes from the prior session):**

```
 M tests/test_mixed_collation_coverage.py
 M tests/test_unicode_decode.py
 D tools/diag/pr_review_sort_test.py
?? docs/correctness_coverage_cs_lob_preamble.md   # stray artifact — Phase 3 deletes it
?? docs/spec/                                     # UNRELATED untracked work — DO NOT touch/commit
```

If the working tree differs (e.g. the test edits are missing), re-apply them
per Phase 1 before continuing.

**Optional pre-existing confirmation (recommended once):** confirm a
representative pre-existing failure fails identically on the branch base:

```bash
git stash --include-untracked            # if you have local edits to protect
git worktree add /tmp/mssqlbak-base origin/feat/bak-to-delta
# (or simply reason from `git diff --name-only origin/feat/bak-to-delta..HEAD`,
#  which shows no record-layer / sink / cli / extract file changed)
git worktree remove /tmp/mssqlbak-base
git stash pop
```

---

## Phase 1 — Confirm the already-applied STALE-TEST fixes (#1, #2, #3)

These edits are **already in the working tree**. Your job is to verify they are
present and correct, not to reapply from scratch.

**End state:** `tests/test_unicode_decode.py` and the one boundary test in
`tests/test_mixed_collation_coverage.py` assert `'?'` (not `'\ufffd'`) for
undefined/undecodable bytes; `tools/diag/pr_review_sort_test.py` is deleted.

1a. Verify the unicode tests pass:

```bash
python -m pytest -q tests/test_unicode_decode.py
```
Expected: `53 passed`.

1b. Verify the mixed-collation boundary test passes:

```bash
python -m pytest -q "tests/test_mixed_collation_coverage.py::TestDecodeCharEncodingBoundary::test_cp1252_undefined_byte_replaced"
```
Expected: `1 passed`.

1c. Verify the diag file is gone (it ran heavy `.bak` decoding at import time
and crashed collection after the `_build_huff_table` 3-tuple change; its sibling
`pr_review_multiset.py` was already deleted after use):

```bash
test ! -e tools/diag/pr_review_sort_test.py && echo "deleted OK"
```

If any of 1a–1c is not satisfied, apply the edits: replace every
`"\ufffd"` expectation for an *undefined/undecodable* byte with `"?"` in those
two test files (keep expectations for *defined* bytes unchanged), and
`git rm tools/diag/pr_review_sort_test.py`.

---

## Phase 2 — Regenerate the decode-path census baseline (#4)

**Why this is safe:** the census test only tracks which heuristic branch each
fixture takes. On `cs_lob_preamble.bak` the branch moved
`v4split:varchar-long` → `v4split:fallback` because of the (already committed)
Huffman fixes. The decoded **values are still correct** — correctness coverage
for that fixture is `1/1 pass` (verified: `python -m tools.correctness_coverage
tests/fixtures_2022/cs_lob_preamble.bak` → "1/1 pass"). So the recorded baseline
is simply out of date.

**End state:** `test_decode_path_census.py::test_census_matches_baseline`
passes, and `git diff tests/census_baseline.json` shows **only** the single
`cs_lob_preamble` `v4split` tag changing.

2a. Re-confirm the flip is benign (do not skip — this is the correctness gate):

```bash
python -m tools.correctness_coverage tests/fixtures_2022/cs_lob_preamble.bak
```
Expected: `... (1/1 pass)`. If it is NOT 1/1 pass, **stop** — the census flip
is a real regression, not benign; re-open the Huffman `_split_v4_record` work
instead of touching the baseline.

> Note: 2a writes `docs/correctness_coverage_cs_lob_preamble.md` as a side
> effect. Phase 3 deletes it.

2b. Regenerate the baseline (command is documented in the census test's own
docstring):

```bash
MSSQLBAK_DECODE_TRACE=1 python tools/diag/_cli.py census \
    --version 2022 --output tests/census_baseline.json
```

2c. Verify the diff is exactly the one expected line change:

```bash
git diff tests/census_baseline.json
```
Expected: only the `cs_lob_preamble` entry changes its `v4split:*` tag from
`varchar-long` to `fallback`. **If any other fixture/table entry changes,
stop** and investigate those additional flips the same way (run correctness
coverage on each affected fixture) before committing.

2d. Confirm the test now passes:

```bash
python -m pytest -q tests/test_decode_path_census.py::test_census_matches_baseline
```
Expected: `1 passed`.

---

## Phase 3 — Clean up the stray verification artifact

`docs/correctness_coverage_cs_lob_preamble.md` was produced by the coverage
runs in Phase 2a and is not a tracked doc. Remove it so it isn't accidentally
committed:

```bash
rm -f docs/correctness_coverage_cs_lob_preamble.md
```

**Do not** touch the untracked `docs/spec/` directory — it is a separate,
unrelated body of work.

---

## Phase 4 — Verify and commit

4a. Targeted re-run of everything this plan touched:

```bash
python -m pytest -q \
  tests/test_unicode_decode.py \
  tests/test_mixed_collation_coverage.py \
  tests/test_decode_path_census.py
```
Expected: all pass (0 failed).

4b. Lint the changed files (root-cause only, no suppressions):

```bash
ruff check tests/test_unicode_decode.py tests/test_mixed_collation_coverage.py
pyright  tests/test_unicode_decode.py tests/test_mixed_collation_coverage.py
```
Expected: clean. (`census_baseline.json` is data, not linted.)

4c. Stage exactly the intended paths and commit (do **not** `git add -A` — that
would sweep in `docs/spec/`):

```bash
git add tests/test_unicode_decode.py \
        tests/test_mixed_collation_coverage.py \
        tests/census_baseline.json
git rm  tools/diag/pr_review_sort_test.py     # records the deletion if not already staged
git status --short                            # confirm docs/spec/ is NOT staged
```

Suggested commit message:

```
test: align _decode_char expectations with '?' substitution; refresh census baseline

Commit f99f370 made _decode_char emit '?' (U+003F) for bytes with no code-page
representation (matching SQL Server, validated by cell digests). Update the
stale unit tests in test_unicode_decode.py and test_mixed_collation_coverage.py
that still expected U+FFFD.

Refresh tests/census_baseline.json: the committed Huffman fixes moved
cs_lob_preamble's v4 split from 'varchar-long' to 'fallback'; correctness
coverage for that fixture is still 1/1 pass, so the branch flip is benign.

Delete tools/diag/pr_review_sort_test.py: a throwaway diagnostic (rejected
"descending sort" hypothesis) whose *_test.py name made pytest collect it and
run heavy .bak decoding at import, aborting collection after the 3-tuple
_build_huff_table change.
```

**End state:** `git status` clean except untracked `docs/spec/`; the three
touched test artifacts committed.

---

## What I cannot decide for you

| Item | Why it needs a human |
|------|----------------------|
| Whether to fix the 6 PRE-EXISTING families (#5–#11) | They are real gaps (XTP tables, TDE decryption, JSON type support, a stale CLI API ref, a stub fixture). Each is its own project and unrelated to this branch. Fixing them is a scope decision, not a lint/regression fix. |
| Whether to update `docs/spec/00_MASTER.md` (G54) and `docs/spec/01_TYPES_LOB.md` (§3.6) | Those untracked spec docs still say undefined bytes → `U+FFFD`, which is now wrong (should be `'?'`). They belong to a separate untracked effort; correct them only if the owner of `docs/spec/` wants it in this change. |
| Pushing to `origin` | Branch is ahead of `origin/feat/bak-to-delta`; do not push unless asked. |
