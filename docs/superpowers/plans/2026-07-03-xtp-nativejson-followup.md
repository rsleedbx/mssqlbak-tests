# XTP + native-JSON follow-up (2026-07-03)

**Audience:** an implementing agent (Sonnet-medium). Follow-up to
`2026-07-03-test-failure-remediation.md`, whose "PRE-EXISTING / UNRELATED"
bucket deferred two failures. This plan resolves them.

Both features are **already implemented in the parser**. Neither failure is a
missing decoder. The work is (Track A) two precise test-harness corrections,
and (Track B) one genuine — but exploratory — XTP data-format coverage gap.

Investigation sources (read for full detail):
[XTP investigation](ce1ce6f4-e3cf-4b07-89c0-dfbba67f4183) ·
[native-JSON investigation](0618d14e-ce1a-4c2c-aa6e-6fd777580f83).

---

## 0. Findings — what exists vs what is missing

### Native JSON (type_id 244) — FULLY IMPLEMENTED
`mssqlbak/types.py`: `NATIVE_JSON = 244` (`:96`), in `SUPPORTED_TYPE_IDS`
(`:146`), full MSJSONB decoder `decode_native_json` (`:823`), dispatch
`_DECODERS[244] = _dv_native_json` (`:1031`), Arrow mapping `pa.string()`
(`:1137`). Dedicated coverage `tests/test_native_json_coverage.py` (uses the
SS2025 fixture, skips cleanly when absent).

**The failure is a test bug.** `tests/test_extract_e2e.py::test_extract_writes_all_tables`
loops over **all** `TYPE_CASES` and demands a `dbo/t_<name>` Delta dir for each,
but `fixture_bak` is the **SS2022** `typecoverage_full.bak` (`tests/conftest.py:47,42`).
The `native_json` case is intentionally SS2025-only — `TypeCase(name="native_json",
rows=[], auto=True, fallback_xtype=244)` (`tools/typematrix.py:478-499`) — so no
`t_native_json` table exists in that fixture and `DeltaTable(...)` raises
`TableNotFoundError`.

### XTP / In-Memory OLTP — IMPLEMENTED, with a real data-coverage gap
`mssqlbak/xtp.py` decodes compact CFP blocks (`_COMPACT_MAGICS`, `:73`;
`scan_compact_blocks`, `:138`; `decode_compact_block`, `:292`) and WAL blocks
(`_WAL_MAGIC`, `:82`; `scan_wal_blocks`, `:199`), entry point
`read_xtp_rows` (`:336`). Detection: `Table.is_memory_optimized`
(`mssqlbak/catalog.py:441`, logic `:2109-2141`); classified supported
(`mssqlbak/inspect.py:182-187`); routed in `mssqlbak/extract.py:329-342, 431-434`
via `_extract_xtp_table` (`:1002`). Synthetic fixtures (`xtp_*`) decode
correctly.

**Two separate reasons the test fails:**
1. **Data gap (real, parser-side):** `read_xtp_rows` finds **no** recognizable
   compact/WAL blocks in `AdventureWorks2016_EXT.bak`, so it returns empty row
   lists → `_extract_xtp_table` never calls `sink.write_batch` → no Delta dir →
   "absent from decode". The real backup's on-disk CFP layout differs from what
   the block scanners currently match. Documented at `tools/known_gaps.py:137-148`.
2. **Test-harness gap:** `tests/test_value_correctness.py::test_fixture_cells_match_ground_truth`
   only honors **whole-fixture** `KNOWN_GAPS` via `gap_reason` (`:512, 545`). It
   does **not** consult the **table-level** `KNOWN_SKIPPED_TABLES`, which already
   lists all 7 tables for `AdventureWorks2016_EXT` (`tools/known_gaps.py:140-148`).
   `test_stats.py:553` already honors that list; this test does not.

---

## Track A — Test-harness corrections (do this first; low-risk, well-defined)

### A1. `test_extract_e2e.py` — skip SS2025-only matrix cases

**Why:** the loop must not demand a table the loaded fixture cannot contain. The
`fallback_xtype` field exists precisely to flag "type registered but no table in
the standard SS2022 fixture" (`tools/typematrix.py:87-90`). `native_json` is the
only such case today; the predicate is future-proof.

**Edit** `tests/test_extract_e2e.py`, `test_extract_writes_all_tables`:

```python
@pytest.mark.fixture
def test_extract_writes_all_tables(fixture_bak: Path, tmp_path: Path) -> None:
    extract_bak_to_delta(fixture_bak, tmp_path / "delta")
    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            # SS2025-only types (e.g. native json, type_id 244) have no table in
            # the SS2022 typecoverage fixture. They are covered by their dedicated
            # coverage tests (e.g. tests/test_native_json_coverage.py).
            continue
        dt = DeltaTable(str(tmp_path / "delta" / "dbo" / f"t_{case.name}"))
        assert dt.to_pyarrow_table().num_rows == len(case.rows)
```

**End state:** `pytest -q tests/test_extract_e2e.py` passes (both tests).

**Verify:**
```bash
python -m pytest -q tests/test_extract_e2e.py
```

### A2. `test_value_correctness.py` — honor the table-level skip list

**Why:** mirror the already-established pattern in `test_stats.py:551-556`. The 7
XTP tables are a documented gap (`KNOWN_SKIPPED_TABLES["AdventureWorks2016_EXT"]`);
their absence should xfail/skip cleanly, not hard-fail.

**Edit 1** — extend the import at `tests/test_value_correctness.py:26`:

```python
from tools.known_gaps import (
    expected_skipped_tables,
    gap_reason,
    version_from_fixture_dir,
)
```

**Edit 2** — in `test_fixture_cells_match_ground_truth`, skip intentionally-absent
tables. Replace the manifest loop (currently `:536-540`):

```python
        skipped = expected_skipped_tables(bak.stem)
        failures: list[str] = []
        for entry in manifest.get("tables", []):
            ext = extracted.get(entry["fqn"])
            if ext is None:
                if entry["fqn"] in skipped:
                    # Intentionally unsupported for this backup (e.g. XTP tables
                    # whose real CFP checkpoint layout is not yet recognized —
                    # see tools/known_gaps.py KNOWN_SKIPPED_TABLES).
                    continue
                failures.append(f"{entry['fqn']}: absent from decode")
                continue
            res = verify_table(ext, cells_dir, entry)
            if not res.ok:
                failures.append(f"{entry['fqn']}: {res.col_mismatches or res.digest_mismatches or res.error}")
```

Leave the trailing `if failures and reason is not None: pytest.xfail(...)` /
`assert not failures` unchanged.

**Important scoping note:** only skip the **absent** branch (matching
`test_stats.py`). If a listed table *does* decode but mismatches, that must still
surface as a failure — do not blanket-skip verification for listed tables.

**End state:** `test_fixture_cells_match_ground_truth[AdventureWorks2016_EXT.bak.cells]`
passes (the 7 XTP tables skip; all other tables still verify).

**Verify (this is a `@pytest.mark.full` test — enable full mode):**
```bash
python -m pytest -q -m full \
  "tests/test_value_correctness.py::test_fixture_cells_match_ground_truth[AdventureWorks2016_EXT.bak.cells]"
```
Expected: `1 passed` (or `xpassed`/`xfailed` — but NOT failed). If your repo
requires a flag other than `-m full` to run full-tier tests, use that; confirm
the test is actually collected (not deselected) before trusting a green result.

### A3. Lint + commit Track A

```bash
ruff check tests/test_extract_e2e.py tests/test_value_correctness.py
pyright  tests/test_extract_e2e.py tests/test_value_correctness.py
git add tests/test_extract_e2e.py tests/test_value_correctness.py
git status --short          # confirm docs/spec/ and plan files are NOT staged
```

Suggested commit message:

```
test: stop e2e/value tests from failing on legitimately-absent tables

Native JSON (type_id 244) and XTP are already implemented; two tests failed on
tables that legitimately don't appear in the loaded fixture:

- test_extract_writes_all_tables looped over the SS2025-only native_json matrix
  case (fallback_xtype=244) against the SS2022 typecoverage fixture. Skip cases
  with fallback_xtype set; they have dedicated coverage tests.

- test_fixture_cells_match_ground_truth ignored the table-level
  KNOWN_SKIPPED_TABLES list (AdventureWorks2016_EXT's 7 memory-optimized tables,
  whose real CFP checkpoint layout is not yet recognized). Honor it, matching
  the existing pattern in test_stats.py.
```

---

## Track B — Real XTP CFP coverage for AdventureWorks2016_EXT (EXPLORATORY)

⚠ **Uncertainty: high.** This is genuine binary-format reverse engineering, not
a wiring fix. It may not be crackable in one pass, and a Sonnet-medium agent
should treat it as an investigation with a clear stop/report point rather than a
guaranteed deliverable. **Do Track A regardless of Track B's outcome.**

**Goal / definition of done:** `read_xtp_rows` returns correct rows for the 7
`AdventureWorks2016_EXT` memory-optimized tables such that their cell digests
match ground truth; then remove those tables from
`KNOWN_SKIPPED_TABLES` (`tools/known_gaps.py:140-148`) and re-run A2's test
without the skip.

**Required skills (read them first):**
`.cursor/skills/format-reverse-engineering/SKILL.md`,
`.cursor/skills/decode-bug-workflow/SKILL.md`,
`.cursor/skills/mssqlbak-diag/SKILL.md`.

**Entry points:**
- Working decoder + block scanners: `mssqlbak/xtp.py`
  (`_is_compact_data_block:114`, `scan_compact_blocks:138`, `_WAL_MAGIC:82`,
  `scan_wal_blocks:199`, payload decode `_decode_payload:232`).
- Diagnostic: `tools/diag_xtp_blocks.py` — run it against
  `tests/fixtures_realworld/AdventureWorks2016_EXT.bak` to dump what block
  magics / candidate blocks are actually present.
- Spec: `docs/spec/08_XTP_CHECKPOINT.md` (note: stale — says XTP "not yet
  implemented"; treat as background, not ground truth).

**Suggested method (empirical loop):**
1. Dump the raw backup and enumerate the 4 KB-aligned block magics actually
   present for the XTP alloc units. Compare against `_COMPACT_MAGICS` and
   `_WAL_MAGIC`. The likely finding: AdventureWorks uses a real CFP block
   magic/layout variant the scanners don't match.
2. Cross-check against a synthetic fixture that DOES decode (`xtp_rich_full.bak`
   / `xtp_simple_full.bak`) to see how the byte layout differs.
3. Form a falsifiable hypothesis about the missing magic/offset; extend the
   scanner/decoder minimally and guard it so synthetic fixtures still pass.
4. Validate: cell digests for all 7 tables match ground truth
   (`tests/fixtures_realworld/AdventureWorks2016_EXT.bak.cells`), AND
   `tests/test_xtp_coverage.py` + `tests/test_xtp_rich_coverage.py` still pass
   (no regression on the synthetic fixtures).

**If blocked after a reasonable empirical budget:** stop, write up the observed
block magics/layout and the specific mismatch in a dated `docs/` note, and leave
the `KNOWN_SKIPPED_TABLES` entry in place. That is an acceptable outcome — the
tables remain a documented gap, not a test failure (Track A already handles the
test).

---

## What I cannot decide for you

| Item | Why it needs a human |
|------|----------------------|
| Whether to invest in Track B now | It's open-ended reverse engineering with uncertain payoff. Track A makes the suite green; Track B is a real feature-coverage improvement that may take significant time. |
| Updating stale `docs/spec/08_XTP_CHECKPOINT.md` | It contradicts the shipped `mssqlbak/xtp.py` decoder (says XTP unimplemented). But `docs/spec/` is an **untracked** separate effort in this working tree — correct it only if that directory's owner wants it in scope. |
| The other pre-existing failures from the remediation plan (record_layer uniquifier, TDE, corrupt-metadata stub, `test_correctness_coverage_cli` stale API ref) | Each is its own unrelated project, out of scope for this XTP/JSON follow-up. |
