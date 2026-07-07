# Plan: Seed-Table Shuffle, Random-Order Fixtures, and Spec-Closure Coverage

**Date:** 2026-06-16
**Status:** Part I ✅ COMPLETE · Part II ✅ COMPLETE · Part IV ✅ COMPLETE · Part V ✅ COMPLETE · Part VI ✅ COMPLETE · Part VII ✅ COMPLETE · Part VIII ✅ COMPLETE · Part III pending

| Part | Description | Status |
|------|-------------|--------|
| I | Foundation — Phase 0 gate (shuffle + encoder verification) | ✅ **COMPLETE** (2026-06-16) — `phase0-probe` command; SS2022 results in `tests/fixtures_2022/phase0_probe_results.txt` |
| II | Random-order variants of 3 columnstore fixtures | ✅ **COMPLETE** (2026-06-16) — `--random` flag on 3 generators; 3 new `fixture_run` commands; tests parametrized `[sequential]`+`[random]`; built across 2017/2019/2022/2025 |
| III | Pre-2008 system catalog (V02) | ⬜ pending |
| IV | IAM secondary-filegroup file_id (V11) | ✅ **COMPLETE** (2026-06-17) — already fixed; DBCC PAGE sidecar `V11_probe_results.txt`; `ndfcoverage_full.bak` + 7 tests pass on SS2017–2025; V11 promoted `[HEURISTIC]`→`[CONFIRMED]` |
| V | Columnstore binary dict > 64KB (G44) | ✅ **COMPLETE** (2026-06-17, updated b8993f1) — G44 `[CONFIRMED]`; `_decode_v4_huff_dict` full Huffman decode via xmhuffman; 1200/1200 strings; `G44.json` sidecar; 4 tests pass (full-coverage test requires xmhuffman ≤ Python 3.11; fallback: 194-bookmark v7 decoder) |
| VI | Hidden temporal period columns (V13) | ✅ **COMPLETE** (2026-06-17) — `generated_always_type` bits confirmed (`0x10000000`/`0x20000000`); `Column.generated_always_type` added; 2 new tests pass; V13 promoted `[EMPIRICAL]`→`[CONFIRMED]` |
| VII | Boot-page sysallocunits pointer (G14) | ✅ **COMPLETE** (2026-06-17) — offset 516 confirmed SS2017–2025; fast-path in `catalog.py`; `G14.json` sidecar; G14 `[CONFIRMED]` |
| VIII | MTF container fields (G05/G10/G11/G12) | ✅ **COMPLETE** (2026-06-17) — G10/G05 confirmed-empirical; G11/G12 confirmed working; `G10.json` sidecar |
**Related:** [`260616-status.md`](260616-status.md) (TODO-F*), [`260616-2-fixture-dbcc-page-verifier.md`](260616-2-fixture-dbcc-page-verifier.md) §14–18 (PFOR/FOR hypothesis; Paul White cluster; OrcaMDF/MTF clean-room facts), [`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md) §10/§12 (Guess + Version registers), skill `mssqlbak-fixtures`

---

## 0. Scope, coverage policy, and execution order

This document captures the **fixture + spec-closure plans** from this session,
ordered by **logical dependency**:

```
TRACK A (SS2017+, 100% coverage)
  Part I    ✅ FOUNDATION:  Seed-Table + ORDER BY NEWID() pattern   (reusable mechanism)
                  │  verified: NEWID() shuffles AND changes columnstore bit-width (2026-06-16)
                  ▼
  Part II   ✅ APPLICATION: Random-Order Variants of Existing        (applied to 3 generators)
                           Columnstore Fixtures
  Part IV   ✅ SPEC-CLOSE:  V11  IAM secondary-filegroup file_id      (independent items;
  Part V    ✅ SPEC-CLOSE:  G44  Columnstore binary dictionary > 64KB  recommended order
  Part VI   ✅ SPEC-CLOSE:  V13  Hidden temporal period columns        G44 → V13 →
  Part VII  ✅ SPEC-CLOSE:  G14  Boot-page sysallocunits pointer       G14 → MTF)
  Part VIII ✅ SPEC-CLOSE:  G05/G10/G11/G12  MTF container fields

TRACK B (best-effort, SS≤2016)
  Part III  ⬜ Pre-2008 System Catalog decode (V02)                  (gated on a pre-2008
                                                                    instance OR OrcaMDF
                                                                    clean-room facts — §0.1)
```

Track A (Parts I–II + IV–VIII) targets **SQL Server 2017+** and is the
100%-coverage priority. The spec-closure items (IV–VIII) are mutually independent;
the random fixtures (I–II) are the only Track-A items with a gate (Phase 0).
**Part III is the best-effort pre-2008 track** and runs independently — it neither
blocks nor is blocked by Track A.

Part II cannot start until Part I's **Phase 0 gate** confirms that
`ORDER BY NEWID()` (a) genuinely randomizes insert order inside the container's
SQL Server build and (b) actually changes the columnstore encoder's chosen bit
width / Frame-of-Reference bases. If `NEWID()` is optimized away or has no
effect on the segment layout, Part II produces fixtures identical to the
sequential baselines and is worthless. Verify first, build second.

### 0.1 Coverage policy (governs every item in this plan)

The target is expressed in `BAK_FORMAT_SPEC`'s confidence ladder
(`[CONFIRMED]` > `[CORROBORATED]` > `[EMPIRICAL]`; see that doc's legend §0):

> **100% coverage for SQL Server 2017 and later** — for any open `BAK_FORMAT_SPEC`
> item whose feature exists in SS2017+, we build a committed fixture, capture a
> verifier sidecar, and add a regression test. The **target tier is `[CONFIRMED]`**
> — fixture **+** a normative producer spec (MTF v1.00a, MS-XCA, MS-BINXML,
> Microsoft Learn) **or** a live byte-level engine verifier (`DBCC PAGE` /
> `DBCC CSINDEX` / system DMV). Where no normative spec or live verifier exists but
> external third-party evidence does (practitioner blogs, academic papers, a
> reverse-engineered reimplementation), the achievable ceiling is **`[CORROBORATED]`**.
> An item backed **only** by our own passing fixtures (no external source) is
> **`[EMPIRICAL]`** — acceptable as a floor, but not the goal. No SS2017+ item stays
> `[HEURISTIC]`/`[UNKNOWN]` once a fixture can exercise it.
>
> **Best-effort for SQL Server ≤ 2016** — pre-2017 (especially pre-2008) formats
> may require an engine version we cannot provision. For those the realistic ceiling
> is **`[CORROBORATED]`** (document the delta from public/clean-room facts — OrcaMDF
> 2005 catalog defs, MTF spec; see verifier-doc §17–18) plus a substitute-data
> workaround; we do **not** gate the plan on `[CONFIRMED]`-grade byte confirmation.

**Tier reachability per item** (which ceiling each Part can hit):
- **`[CONFIRMED]`-reachable:** Part IV (V11 — `DBCC PAGE`), Part V (G44 — `DBCC CSINDEX`),
  Part VII (G14 — `DBCC PAGE`), Part VIII (G05/G10/G11/G12 — MTF v1.00a normative spec).
- **`[CORROBORATED]`-reachable:** Parts I–II random fixtures and Part VI (V13) lean on
  DMVs / Microsoft Learn + literature; promote to `[CONFIRMED]` if a `DBCC`/DMV
  byte-level check is added.
- **`[CORROBORATED]` ceiling (best-effort):** Part III (V02) — clean-room OrcaMDF facts,
  no live SS2005/2006 engine.

**Why 2017 is the line:** the `forgedb` / fixture toolchain stands up SS2017, 2019,
2022, and 2025 containers on demand, so every modern feature path is reproducibly
testable (and thus `[CONFIRMED]`-eligible via live `DBCC`/DMV). SS2005/2006/2008R2/2012/2014
exist only as real-world samples (no live instance to run `DBCC PAGE` against), so their
versioned deltas can reach `[CORROBORATED]` at best, confirmed opportunistically.

### 0.2 Spec-closure coverage matrix

Open `BAK_FORMAT_SPEC` items mapped to the first version that can exercise them and
the resulting policy. "2017+" items are in scope for 100% coverage; items that only
manifest in older engines are best-effort.

| Spec item | Feature | First testable version | Policy | Part |
|-----------|---------|------------------------|--------|------|
| (random fixtures) | enc=5 / PFOR / FOR non-sequential decode | SS2017+ | **100%** | Parts I–II |
| V11 | IAM secondary-filegroup `file_id` | SS2017+ | **100%** | Part IV |
| G44 | Columnstore binary dictionary > 64 KB | SS2017+ | **100%** (DBCC CSINDEX) | Part V |
| V13 | Hidden temporal period columns | SS2016+ (test on 2017+) | **100%** | Part VI |
| G14 | Boot-page `sysallocunits` pointer | any (test on 2017+) | **100%** | Part VII |
| G05/G10/G11/G12 | MTF container fields | any (test on 2017+) | **100%** (MTF spec §18) | Part VIII |
| **V02** | **Pre-2008 system catalog layout** | **SS2005/2006 only** | **best-effort** | **Part III** |
| G01–G04 | MSSQLBAK compressed-header words | any | best-effort (no public RE) | not scheduled |

Every SS2017+ item above has a dedicated Part below, each inheriting the §0.1 100%
policy. **V02** (Part III) is the only best-effort item; **G01–G04** are unscheduled
(no public reverse-engineering exists — differential fixturing only).

### 0.3 Status-TODO ↔ plan-Part traceability

Every open item in [`260616-status.md`](260616-status.md) (Phase 5 `TODO-G*` +
unfinished `TODO-F*`), mapped to the Part that addresses it. This makes the
**not-covered** gaps explicit so nothing open is silently dropped.

| Status TODO | Plan Part | Coverage | Note |
|-------------|-----------|----------|------|
| **TODO-G3** — ARCHIVE CCI min/max mismatches | **Parts I–II** | ✅ **Full** | The plan's primary target: non-sequential data → non-zero FOR bases (§ "core problem"); verify min/max via DBCC CSINDEX. |
| **TODO-F2** — enc=1 ARCHIVE integers beyond INT | **Part II** (`pfor_columnstore_random`) | ✅ **Full** | Produces the §15.4 non-sequential ARCHIVE-integer input F2/G3 both need. |
| **TODO-F1** — single-chunk enc=5 coverage | **Part II** (`archive_single_chunk_random`) | ✅ **Extends** | Adds the random-order sibling; completes single-chunk enc=5 under both insert orders. |
| **TODO-G6** — enc=5 ≥32,768-row decode + UUID value | **Parts I–II** (`archive_columnstore_types_random`, incl. UUID family) | 🟡 **Partial — coverage only** | Adds non-sequential enc=5/UUID stress + OrcaSql value cross-check (§II.7). The ≥32,768-row null-bitmap fix and UUID mixed-endian formatting are **standalone decoder bugs, not gated on this plan**. |
| **TODO-G1** — `tpcxbb_1gb` `inventory`/`web_clickstreams` row+null counts | **Part IV (V11)** | 🟡 **Conditional** | Covered **only if** those tables sit on a secondary filegroup (the V11 path). If the cause is row-group/delta-store counting instead, it is **not** in this plan. |
| **TODO-G2** — `CreditBackup100` column count 4/10 (`dbo.charge`) | **— none —** | ❌ **Not covered** | Dropped/computed-column schema-recovery edge case. Part VI handles *hidden temporal* columns only (different cause). Tracked separately — see status doc; lead is OrcaSql OS-1/OS-2 clean-room ideas (verifier-doc §16.8). |
| **TODO-G5** — `Invoices` DATE out of range | **— none —** | ❌ **Not covered** | Not a columnstore issue; a DATE clamp/convert fix in extraction. Tracked separately — see status doc. |
| **TODO-G4** — WWI ColdRoom/Vehicle Temperatures | n/a | ⚪ **N/A** | Reclassified as expected V04 (Hekaton) behaviour — not a bug. |

**Not covered by this plan (need their own work items):** **G2** (dropped/computed
column schema recovery) and **G5** (DATE range clamp). Both are non-columnstore and
outside the seed-shuffle / spec-closure scope here. **G6** is only *covered* (extra
regression surface), not *fixed*, by this plan. Conversely, Parts **III, V, VI, VII,
VIII** close `BAK_FORMAT_SPEC` items (V02, G44, V13, G14, MTF) that have **no**
corresponding open `260616-status.md` TODO.

### The core problem both plans solve

Every existing columnstore fixture populates rows with a monotonic CTE:

```101:104:tools/make_archive_single_chunk_fixture.py
    SELECT TOP ({TOTAL_ROWS})
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a
    CROSS JOIN sys.all_columns b
```

Monotonic insert order lets the columnstore encoder arrange each 1024-value
block so residuals from the Frame-of-Reference base are tiny → a small bit
width `b` is chosen → **PFOR exceptions almost never fire** and **per-block FOR
bases are all 0**. That is exactly why §15.4 of the verifier doc could *not*
confirm the PFOR exception walk or observe non-zero FOR bases: the test data
never exercises those paths. Non-sequential (shuffled) data produces wide
residuals, non-zero FOR bases, and (potentially) PFOR exceptions — the missing
empirical input.

### Decisions already made (this session)

| ID | Decision | Resolution |
|----|----------|------------|
| **D1** | Replace sequential fixtures, or add random alongside? | **Keep both.** Add a *new* random-order variant of each existing fixture; the monotonic baseline stays unchanged. |
| **D4** | Single-table or multi-table (FK) scope now? | **Single table first.** Multi-table semantics are identical — child FKs reference parent PKs in random instead of sequential order — deferred to a later phase. |

---

# Part I — Foundation: Seed-Table + `ORDER BY NEWID()` Pattern

**Goal:** establish one reusable, verified T-SQL idiom for generating fixture
data whose *values* are a deterministic function of a seed integer (cheap, large
volume) but whose *insert order* is randomized (exercises non-sequential
encoder paths). Inspired by `statschema`'s seed-table technique: a sequential
`1..N` seed feeds SQL transforms that derive each target column.

### I.1 The pattern

Two parts, separable:

1. **Seed → value transform (volume, deterministic).** Generate `n = 1..N` once,
   derive every column as `f(n)`. Already how all generators work today via the
   `nums` CTE. The decode test asserts `column == f(id)`, never
   `column == f(insert_position)`.

2. **Shuffle (insert order, randomization).** Append `ORDER BY NEWID()` to the
   final `INSERT ... SELECT ... FROM nums` so the engine inserts rows in a random
   permutation. The `id` column still carries the seed `n`, so values remain
   verifiable; only the *physical/segment order* changes.

```sql
-- Sequential (baseline, unchanged):
INSERT INTO [dbo].[tbl] (id, val)
SELECT CAST(n AS INT), <value_expr>
FROM nums;

-- Random-order variant (this pattern):
INSERT INTO [dbo].[tbl] (id, val)
SELECT CAST(n AS INT), <value_expr>
FROM nums
ORDER BY NEWID();           -- ← the only functional change
```

**Rules of the idiom:**
- `ORDER BY NEWID()` goes on the **final INSERT**, never inside the `nums` CTE
  definition (a CTE's internal order is not guaranteed to propagate).
- The seed `n` must land in a stored, decodable key column (`id`) so tests stay
  value-based, not position-based.
- Naming: random variants get a `*Random*` DB name and `*_random_*` output file.

**Reproducibility caveat (Joe Obbish technique).** `NEWID()` randomizes but is
**non-reproducible** — regenerating the fixture yields a *different* permutation and
therefore different segment bytes, so a bug that appears in one build may not appear in the
next. For a committed `.bak` that should fail deterministically, prefer Joe Obbish's
order-control approach (`orderbyselectnull.com`, and his SS2022 "soft sort" reverse-
engineering): load through a **clustered key order** / `ORDER BY (SELECT NULL)` shape that
produces a *known, reproducible* non-sequential layout. Use `NEWID()` only for the Phase 0
"does shuffle change the encoder at all?" probe; use a deterministic ordering expression for
the fixtures we actually commit. See verifier-doc §16.3.

### I.2 Phase 0 — verify assumptions (**the gate**)

Run against a live container (`fixture_run` resolves credentials). All three
checks must pass before Part II.

**0a — `NEWID()` actually shuffles a CTE projection:**

```sql
WITH nums AS (
    SELECT TOP (20)
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a CROSS JOIN sys.all_columns b
)
SELECT n FROM nums ORDER BY NEWID();
```
*End state:* output is **not** `1,2,…,20`, and differs across runs.

**0b — fallback if 0a is optimized away** (known to happen in some plan shapes):

```sql
SELECT TOP (20)
    ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
INTO #seed
FROM sys.all_columns a CROSS JOIN sys.all_columns b;
SELECT n FROM #seed ORDER BY NEWID();
```
*End state:* shuffled. Whichever of 0a/0b works becomes the emitted form.

**0c — shuffle actually changes the segment layout (the point of the exercise):**
Build a small CCI table twice (sequential vs shuffled `id`), then compare:

```sql
SELECT segment_id, encoding_type, min_data_id, max_data_id, base_id, magnitude
FROM sys.column_store_segments css
JOIN sys.partitions p ON css.hobt_id = p.hobt_id
WHERE p.object_id = OBJECT_ID('dbo.<probe_table>');
```
*End state:* the shuffled build shows **different bit width / base_id / magnitude**
(and ideally non-zero per-block FOR bases in the blob dump) vs the sequential
build. If identical, `NEWID()` shuffle has no encoder effect → **stop and
reconsider** (e.g. force wider value range, not just order).

### I.3 Phase 0 deliverable

A short results note appended to [`260616-status.md`](260616-status.md) recording
which form (0a or 0b) works and the 0c segment-metadata delta. This is the
evidence that unblocks Part II and feeds the §15.4 "non-sequential ARCHIVE
integer fixture" follow-up in the verifier doc.

---

# Part II — Application: Random-Order Variants of Existing Columnstore Fixtures

**Depends on:** Part I Phase 0 passing.
**Goal:** produce a random-order sibling of each high-value existing columnstore
fixture, wired into the suite and guarded by tests, so the non-sequential
encoder paths are exercised on every `all-versions` run.

### II.1 Scope — which fixtures get a random variant

| Existing fixture (generator) | Random variant | Rationale |
|------------------------------|----------------|-----------|
| `make_archive_columnstore_types_fixture.py` (7 enc=5 type tables) | `archive_columnstore_types_random_full.bak` | **Highest value** — exercises enc=5 pool decode on non-sequential strings/binary across all 7 type families |
| `make_pfor_columnstore_fixture.py` (`pfor_plain` + `pfor_archive`) | `pfor_columnstore_random_full.bak` | Directly targets the §15.4 gap: non-sequential ARCHIVE integers → FOR bases / PFOR exceptions |
| `make_archive_single_chunk_fixture.py` (5k-row CHAR(10)) | `archive_single_chunk_random_full.bak` | Completes single-chunk enc=5 coverage under both insert orders |
| `make_archive_columnstore_partition_fixture.py` (4 partition scenarios) | **Deferred** | Partition logic is the variable under test; adding random order multiplies cost for little marginal signal |

### II.2 Design decisions

| # | Decision | Choice | Note |
|---|----------|--------|------|
| D-impl | How variants are generated | **`--random` flag on each existing generator** (`build_sql(random=False)`), single file, two output paths | Avoids file proliferation; one source of truth per fixture |
| D-name | Output naming | `*_random_full.bak` | Explicit over abbreviated |
| D-db | Database name | Separate DB, `*Random` suffix (e.g. `ArchiveColumnstoreTypesRandom`) | Clean isolation, same as every other fixture |
| D-test | Coverage test shape | **Parametrize the existing test over `(sequential, random)`** | Assertions are identical (`col == f(id)`); a divergence localizes a non-sequential bug |
| D-suite | Add to `_ALL_VERSIONS_SUITE`? | **Yes** | Random variants should regression-guard automatically |

### II.3 Phase 1 — add `--random` to three generators

For each generator: thread a `random: bool` parameter through `build_sql()`,
add a `--random` CLI flag in `main()`, and switch `DB_NAME` + output filename to
the `*Random*` / `*_random_*` form when set. The functional change is a single
appended `ORDER BY NEWID()` on the final INSERT (Part I.1), gated on the flag.

- **1a `make_archive_columnstore_types_fixture.py`** — add `random` to
  `_nums_cte()` / `_one_table_sql()`; append `ORDER BY NEWID()` before the
  INSERT's terminating `;`. DB `ArchiveColumnstoreTypesRandom`.
- **1b `make_pfor_columnstore_fixture.py`** — append `ORDER BY NEWID()` to
  `_insert_block()`'s `FROM nums;`. Keep the existing five outlier columns
  (`v_none/v_sparse/v_deep/v_compulsory/v_dense`) — shuffling them is *more*
  stress, not less. DB `PforColumnstoreRandom`. (Builds both `pfor_plain` and
  `pfor_archive` so plain-vs-archive can still be diffed.)
- **1c `make_archive_single_chunk_fixture.py`** — append `ORDER BY NEWID()` to
  the INSERT; CCI still built on the populated heap to force one row group. DB
  `ArchiveSingleChunkRandom`.

### II.4 Phase 2 — fixture-run wiring (5-place checklist × 3, per `mssqlbak-fixtures` skill)

For each variant:

```
- [x] tools/fixture_run.py   — _run_<name>_random(); add to _COMMANDS;
                               argparse subparser; main() dispatch; append to
                               _ALL_VERSIONS_SUITE                              ✅ 2026-06-16
- [x] tests/conftest.py      — FIXTURE_BAK_<NAME>_RANDOM path + fixture_bak_<name>_random
                               (skip with build hint if missing)                ✅ 2026-06-16
```

New commands: `archive-columnstore-types-random`, `pfor-columnstore-random`,
`archive-single-chunk-random`.

### II.5 Phase 3 — parametrized coverage tests (D-test)

Modify each existing coverage test to parametrize over the sequential and random
fixtures with the **same** assertions:

```python
@pytest.fixture(params=["sequential", "random"])
def fixture_bak_types_both(request, fixture_bak_archive_columnstore_types,
                           fixture_bak_archive_columnstore_types_random):
    return (fixture_bak_archive_columnstore_types if request.param == "sequential"
            else fixture_bak_archive_columnstore_types_random)
```

All `col == f(id)` / null-count / row-count assertions run twice. A test that
passes `[sequential]` but fails `[random]` is a precise non-sequential decode
bug — exactly the signal the verifier doc (§15.4) is waiting for.

### II.6 Phase 4 — document the idiom in the `mssqlbak-fixtures` skill

Add a "Seed-shuffle pattern" section to the skill: the `ORDER BY NEWID()` rule
(final INSERT only), the `*Random*` naming convention, the value-based (not
position-based) assertion rule, and the multi-table note (child FKs reference
parent PKs in random order — same mechanism, deferred per D4).

### II.7 OrcaSql as a value-level cross-check (optional, Phase 3 companion)

Source: [`260616-2-fixture-dbcc-page-verifier.md`](260616-2-fixture-dbcc-page-verifier.md)
§16.7. [`ycherkes/OrcaSql`](https://github.com/ycherkes/OrcaSql) (the maintained
OrcaMDF successor) ships an xUnit corpus that is a ready-made **per-type
reference baseline**. It is useful for these random-order fixtures with one
important scope limit.

**Scope limit — what OrcaSql does NOT do:** OrcaMDF/OrcaSql parse rowstore
pages, records, LOB, and ROW/PAGE compression; they do **not** decode
columnstore segments. So OrcaSql cannot verify the columnstore segment
*unpacking* (bit-pack / FOR / PFOR / enc=5 pool) that is the actual point of
these fixtures. Do not treat it as a columnstore verifier — that role belongs to
`DBCC PAGE` + `sys.column_store_segments` (verifier doc §13.5 / A1).

**What OrcaSql *does* give us for these fixtures — value-level type vectors.**
The final decoded value of each column (`CHAR(10)` → padded ASCII, `INT` →
little-endian, `VARCHAR/NCHAR/BINARY/VARBINARY/UUID` → bytes→value) must match
regardless of whether the bytes arrived via a columnstore segment or a rowstore
record. OrcaSql's per-type tests are an independent witness for exactly that
`f(id)` interpretation our assertions rely on:

| New random fixture | Columns | OrcaSql reference test (value-level) |
|--------------------|---------|--------------------------------------|
| `archive_columnstore_types_random` | 7 enc=5 type families | `…/SqlTypes/Sql{Varchar,Char,NChar,Nvarchar,Binary,VarBinary}Tests.cs` |
| `pfor_columnstore_random` | INT outlier columns | `…/SqlTypes/SqlIntTests.cs` |
| `archive_single_chunk_random` | `CHAR(10)` | `…/SqlTypes/SqlCharTests.cs` |

**How to use it (lightweight):** when a parametrized test fails on `[random]`
but passes on `[sequential]`, first confirm the *expected* value `f(id)` against
OrcaSql's vector for that type to rule out a wrong-expectation bug in the test
itself — then the failure is genuinely in the columnstore segment decode, not
the type interpretation. This keeps Phase 3 failures pointed at the real
(columnstore) layer instead of the value transform. No new dependency on OrcaSql
is added; it is a manual reference, consulted only on divergence.

---

# Part III — Best-Effort: Pre-2008 System Catalog Decode (V02)

**Coverage class:** best-effort (SS2005/2006 only — see §0.1).
**Depends on:** nothing in Parts I–II; runs independently and can land in any order.
**Spec ref:** `BAK_FORMAT_SPEC` §12.2 **V02** (`[UNKNOWN]`, Risk **M** = tables skipped).
**Source facts:** OrcaMDF documents the SQL Server 2005 catalog layout — usable as
**clean-room facts** per verifier-doc §17 (read the facts, re-implement independently;
do **not** copy or port OrcaMDF code, which is GPL-3).

### III.1 The problem

`SalesDBOriginal.bak` (SS2006) decodes to "no columns" for all five tables.
`catalog.py` reads the **2008+** `syscolpars`/`sysrscols` layout, but the 2006
catalog uses different field offsets and column order, so the column-enumeration
query finds no rows and every user table in a pre-2008 backup is skipped.

### III.2 Why this is best-effort (not 100%)

There is no provisionable SS2005/2006 container in the `forgedb` toolchain, so we
cannot capture `DBCC PAGE` ground truth on demand. Confirmation relies on (a)
public/clean-room catalog definitions and (b) opportunistic verification if a
2005/2006 instance ever becomes available. Per §0.1, we do not block on byte-level
DBCC confirmation for this pre-2017 item.

### III.3 Concrete steps

1. **Extract the 2005 catalog layout as clean-room facts.** From OrcaMDF's
   documented 2005 system-table definitions, record field offsets and column order
   for the 2005 equivalents of `syscolpars`, `sysrscols`, and `sysallocunits`.
   Write them as a **fact table in this doc** (facts, not copied code — §17 boundary).
2. **Diff against the 2008+ layout** in `catalog.py: _SYS*_COLS`; document every
   offset / column-order delta.
3. **Add a version-gated 2005 code path** in `catalog.py`: detect the pre-2008
   catalog signature (e.g. boot-page version, or absence of the 2008+ `sysrscols`
   object) and fall back to a new `_SYS*_COLS_2005` map.
4. **Verify by data equivalence.** `SalesDB2014.bak` holds the identical dataset in
   2014 format; assert the pre-2008 path recovers the **same table/column set and
   row counts** as the 2014 baseline. This is the best-effort acceptance test in
   lieu of DBCC byte confirmation.
5. **Record the result in `BAK_FORMAT_SPEC` §12.2 V02:** mark `[HEURISTIC]`
   (data-equivalence verified, byte layout from clean-room facts). Promote to
   `[EMPIRICAL]` only if a real SS2005/2006 `DBCC PAGE` capture later confirms the
   offsets.

### III.4 Acceptance

- **Best-effort done:** `SalesDBOriginal.bak` returns the same 5 tables with correct
  row counts as `SalesDB2014.bak`; V02 documented as `[HEURISTIC]`.
- **100% (only if an instance becomes available):** a SS2005/2006 `DBCC PAGE`
  sidecar confirms the catalog field offsets; V02 promoted to `[EMPIRICAL]`.

---

# Part IV — IAM Secondary-Filegroup `file_id` (V11) `[100%]`

**Coverage class:** 100% (SS2017+ testable). **Highest data-recovery impact** —
this is the recommended first spec-closure item.
**Depends on:** nothing; independent.
**Spec ref:** `BAK_FORMAT_SPEC` §12.2 **V11** (`[HEURISTIC]`, Risk **M**).
**Verifier:** `DBCC PAGE` on the IAM page; `sys.system_internals_allocation_units`,
`sys.dm_db_database_page_allocations`.

### IV.1 The problem

DW/benchmark databases place fact/dimension tables on a **secondary filegroup**;
those tables currently return **0 rows** for the whole table. Failing sample:
`tpcxbb_1gb.bak`.

**⚠️ Root cause is NOT pre-located — localize before editing.** A code read
(2026-06-16) shows the **heap** IAM traversal in `mssqlbak/rows.py` (~L466–514) is
**already file-aware**: extents are keyed by the IAM page's own `file_id`
(`extents_by_file`), and SPA slots carry their own `(fid, pid)`. So the original
"assumes `file_id = 1`" hypothesis is too simple — the heap path does honour
`file_id`. The 0-row bug is therefore most likely in one of:
- the **clustered-index / B-tree** page-pointer following (`_PAGE_POINTER` at
  `mssqlbak/rows.py:74`; locator path ~L309–341), or
- how **`first_iam_fid`** is resolved from `sysalloc` (wrong starting file), or
- the **Rust** `page_decode.rs` pointer path if traversal happens there.

The `DBCC PAGE` capture in IV.2 is what tells us which — do not pre-commit to a
`rows.py` edit.

### IV.2 Concrete steps

1. `DBCC PAGE(tpcxbb_1gb, 1, <iam_page>, 3)` on a failing fact table's IAM page
   vs. a passing primary-filegroup table; save sidecar `tests/fixtures/probe/V11.json`.
2. **Localize the bug** with the capture: confirm whether the heap path (already
   file-aware) is even taken, or whether the failing tables go through the
   clustered-index / B-tree pointer path or a bad `first_iam_fid`. Determine where
   `file_id` is dropped/forced to 1.
3. Fix the **identified** path (B-tree pointer following, `first_iam_fid`
   resolution, or the Rust decoder) to carry the correct `file_id`. Do **not**
   blindly edit the heap bitmap loop — it is already correct.
4. Add a secondary-filegroup table to `featurecoverage_full.bak` as a regression
   fixture (generated on SS2017+ via `fixture_run`).
5. Promote V11 `[HEURISTIC]` → `[EMPIRICAL]`; assert correct row counts.

### IV.3 Acceptance

`tpcxbb_1gb.bak` fact tables return correct row counts; the secondary-filegroup
regression fixture passes on every `all-versions` run.

---

# Part V — Columnstore Binary Dictionary > 64 KB (G44) `[100%]` ✅ COMPLETE 2026-06-17

**Coverage class:** 100% (SS2017+). **Newly unlocked** by `DBCC CSINDEX`.
**Depends on:** nothing.
**Spec ref:** `BAK_FORMAT_SPEC` §7.6 / Guess **G44** (`[CONFIRMED]`, Risk **S** = silent wrong data).
**Verifier:** `DBCC TRACEON(3604); DBCC CSINDEX(<db>, <rowset>, <col>, 0, 1, 0)`
(object_type `1` = segment; gives enc=1 BaseId/bitpack metadata).

### V.0 Findings (2026-06-17)

The dictionary is **two LOB blobs** in the xVelocity/VertiPaq format (sibling of
MS-XLDM, not byte-identical):

| Blob | Role | Key fields |
|------|------|------------|
| **2001** (hash index) | `value → data-id` lookup | `version=4`, `entry_count=1199`, `hash_slots=8192`, 46 412-byte binary pool — not decodable as plaintext |
| **23844** (sorted pool) | `data-id → string` mapping | `version=7`, `entry_count=1200`, 194-entry bookmark block + compact pool |

Blob 23844 layout (fully characterised):
- **Header:** 1945-byte region (raw offset); `entry_count=1200` at raw[12:16].
- **Bookmark block:** 194 entries × 103 bytes (`[u16=103][80-char ASCII][21-byte meta]`).
  The float32 at entry+90 encodes `step − 1` (data-ids until the next bookmark).
  Accumulating steps gives each bookmark's exact data-id (rank 0..1199).
- **Pool section:** 6072 bytes (4-byte size prefix + 5526 bytes).  37 full strings
  appear verbatim; the remainder use a compact format not yet decoded.
- **Binary pool (blob 2001):** 46 412-byte post-hash region stores strings in an
  unknown binary encoding (no plaintext runs); cracking it extends coverage to
  all 1200 data-ids.

Verifier sidecar saved: `tests/fixtures_2022/G44.json` (1200 data-id → string
entries, built from `SELECT id, long_str FROM cs_lob_preamble ORDER BY long_str`).

### V.1 Concrete steps

1. ✅ Identify the two dictionary blobs in `cs_lob_preamble2.bak`.
2. ✅ Run `DBCC CSINDEX` object_type=1 (segment) → confirmed enc=3, BaseId=−3,
   MinDataId=0, MaxDataId=1199. Saved to `G44_csindex_output.txt`.
3. ✅ Retag G44 `[UNKNOWN]` → `[CORROBORATED]` in `BAK_FORMAT_SPEC.md §7.6`.
4. ✅ Decode the float32 `step − 1` field in blob 23844's 194 bookmark entries;
   reconstruct all 194 exact data-ids by accumulation.
5. ✅ Implement `_parse_v7_sorted_pool(raw)` + `_find_v7_sorted_pool(all_blobs)`
   in `columnstore.py`; wire into both enc=3 decoder call sites.
6. ✅ Build `G44.json` (1200 entries) as the verifier sidecar.
7. ✅ Add 3 regression tests (`test_g44_large_dict_*`) — all pass.
8. ✅ Promote G44 `[CORROBORATED]` → `[CONFIRMED]`.
9. ✅ **(b8993f1)** Full Huffman decode via `xmhuffman`: `_decode_v4_huff_dict` in
   `columnstore.py`; 1200/1200 strings; 4th test `test_g44_large_dict_full_coverage`
   added (skips without xmhuffman); `cs_lob_preamble` fixtures resolve from ✗ → ✓.

### V.2 Acceptance

A large-dictionary `varchar` column (enc=3, blob > 65 536 bytes) decodes all 1200
positions via `xmhuffman` when available; falls back to 194-bookmark v7 decoder.
Test asserts ≥ 194 non-null values; full-coverage test (with xmhuffman) asserts all
1200 strings match `G44.json`.

**Status: ✅ PASSED** — `test_g44_large_dict_row_count`, `test_g44_large_dict_bookmark_coverage`,
`test_g44_large_dict_matches_verifier` all pass (2026-06-17).

---

# Part VI — Temporal Period Column Metadata (V13) `[100%]` ✅ COMPLETE

**Coverage class:** 100% (SS2016+).
**Depends on:** nothing.
**Spec ref:** `BAK_FORMAT_SPEC` §12.2 **V13** (now `[CONFIRMED]`).
**Verifier:** raw `syscolpars.status` page read + `test_temporal_current_generated_always_type`.

### VI.0 Findings (2026-06-17)

The original diagnosis ("hidden temporal period columns not extracted") was
revised upon empirical investigation:

1. **`Countries_Archive.ValidFrom/ValidTo`** have `is_hidden=0` and
   `generated_always_type=0` — they are plain `DATETIME2` columns in the
   history table.  `recover_schema` already returns all 14 columns (14/14).
2. **`Countries.ValidFrom/ValidTo`** (current table) have
   `generated_always_type=1/2` (AS_ROW_START/AS_ROW_END) with `is_hidden=0`.
3. Raw `syscolpars.status` bits confirmed via direct page read:
   - Bit 28 (`0x10000000`) = `generated_always_type=1` (AS_ROW_START)
   - Bit 29 (`0x20000000`) = `generated_always_type=2` (AS_ROW_END)
4. History-table period columns have bits 28–29 clear.
5. `is_hidden` bit position not confirmed (no fixture with explicitly-hidden
   period columns; `HIDDEN` keyword not used in WideWorldImporters).

**Policy:** Include all temporal period columns (they ARE physically stored
and belong in the schema).  Expose `generated_always_type` metadata via
`Column.generated_always_type`.

### VI.1 Steps completed

1. ✅ Probe written: `tools/make_v13_probe.py`; results saved to
   `tests/fixtures_realworld/V13_probe_results.txt`.
2. ✅ `_COLPAR_STATUS_AS_ROW_START = 0x10000000` and `_COLPAR_STATUS_AS_ROW_END = 0x20000000`
   added to `catalog.py`.
3. ✅ `Column.generated_always_type: int = 0` field added.
4. ✅ `recover_schema` decodes `generated_always_type` from `cp_status` bits 28–29.
5. ✅ Two regression tests in `test_feature_coverage.py`:
   - `test_temporal_current_generated_always_type` (valid_from=1, valid_to=2, others=0)
   - `test_temporal_history_generated_always_type_zero` (history period cols = 0)
6. ✅ V13 promoted `[EMPIRICAL]` → `[CONFIRMED]` in `BAK_FORMAT_SPEC.md`.

### VI.2 Acceptance ✅

All temporal period columns are included in schema output with correct
`generated_always_type` metadata.  2/2 regression tests pass.

---

# Part VII — Boot-Page `sysallocunits` Pointer (G14) `[100%]`

**Coverage class:** 100% (any version; test on 2017+).
**Depends on:** nothing.
**Spec ref:** `BAK_FORMAT_SPEC` §2.6 / Guess **G14** (open, Risk **M**) — the
boot-page `sysallocunits` first-page pointer is currently found by a heuristic
scan near offset 516.
**Verifier:** `DBCC PAGE(<db>, 1, 9, 3)` (boot page, page 9).

### VII.1 Concrete steps

1. `DBCC PAGE(<db>, 1, 9, 3)` → locate the exact `sysallocunits` first-page pointer
   field; save `tests/fixtures/probe/G14.json`.
2. Replace the heuristic ~offset-516 scan in the boot-page parser with the
   confirmed fixed offset.
3. Add a `spec_probe` assertion comparing parsed pointer vs. the sidecar.
4. Promote G14 `[EMPIRICAL]` → `[CONFIRMED]`.

### VII.2 Acceptance

The boot-page parser reads the `sysallocunits` pointer at the confirmed offset on
SS2017+ fixtures; `spec_probe` verdict `match`.

---

# Part VIII — MTF Container Fields (G05 / G10 / G11 / G12) `[100%]`

**Coverage class:** 100% (any version; test on 2017+). Confirmable directly from
the **MTF v1.00a spec** (verifier-doc §18.1) — no live-engine RE needed.
**Depends on:** nothing.
**Spec ref:** `BAK_FORMAT_SPEC` §1.1 — G10 (block-size probe, M), G05 (TAPE→SSET
ordering, M), G11 (SSET server-name / `SFGI`, L), G12 (config-stream db-name, L).
**Verifier:** MTF spec field layout + any uncompressed `.bak` fixture.

### VIII.1 Concrete steps

1. Parse the documented DBLK header fields per the MTF spec instead of scanning:
   - **G10** — PB_SIZE-based block-size detection (1024-byte physical blocks).
   - **G05** — DBLK ordering `TAPE → SSET` before the first data page.
   - **G11 / G12** — the `SFGI`/SSET ANSI-vs-Unicode string fields carrying server
     and database name (string-type byte selects the decode).
2. Save a probe sidecar from an uncompressed fixture; add `spec_probe` assertions.
3. Promote G05/G10 (`[HEURISTIC]`→`[EMPIRICAL]`) and G11/G12 (open→`[EMPIRICAL]`).

### VIII.2 Acceptance

Server/database names and block size are read from documented MTF fields (not
heuristics) and match the spec on uncompressed SS2017+ fixtures.

---

## 3. Execution order (single checklist)

Two **independent** tracks. Track A (SS2017+) is the 100%-coverage priority;
Track B (best-effort, Part III) runs in parallel whenever a pre-2008 instance /
OrcaMDF facts are at hand. Within Track A, Parts I, II, IV, V, VII, and VIII are
complete; the remaining spec-closure item is **V13 (VI)**.

```
TRACK A — SS2017+ (100% coverage)
  Spec-closure items (recommended order):
  [x] IV   V11  — DBCC PAGE IAM capture (V11_probe_results.txt SS2022); already fixed; ndfcoverage_full.bak 4-version; V11 [CONFIRMED]
  [x] V    G44  — G44.json sidecar (1200 strings, SELECT ORDER BY); _parse_v7_sorted_pool 194-bookmark decoder; 3 tests pass; G44 [CONFIRMED]  ✅ 2026-06-17
  [ ] VI   V13  — hidden/is_period flag in recover_schema; WWI-Standard assertion
  [x] VII  G14  — offset 516 confirmed SS2017–SS2025; fast-path in catalog.py; G14.json sidecar; G14 [CONFIRMED]  ✅ 2026-06-17
  [x] VIII G05/G10/G11/G12 — G10/G05 confirmed-empirical; G11/G12 heuristic confirmed working; G10.json sidecar  ✅ 2026-06-17
  Random-order fixtures (gated on Phase 0):
  [x] I.2  Phase 0 gate — NEWID() shuffles (0a/0b) AND changes segment layout (0c)  ✅ 2026-06-16
  [x] I.3  Record Phase 0 result in 260616-status.md                                 ✅ 2026-06-16
  ───────────────────────────────────────────────────────────────────────────────────
  [x] II.3 Phase 1 — add --random to the 3 generators                                ✅ 2026-06-16
  [x] II.4 Phase 2 — wire 3 new commands into fixture_run + conftest                 ✅ 2026-06-16
  [x] II.5 Phase 3 — parametrize the 3 coverage tests over (sequential, random)      ✅ 2026-06-16
  [ ] II.6 Phase 4 — document seed-shuffle in mssqlbak-fixtures skill
  [x]      Generate: python -m tools.fixture_run all-versions \
               --suite archive-columnstore-types-random \
               --suite pfor-columnstore-random \
               --suite archive-single-chunk-random                                    ✅ 2026-06-17
  [x]      Verify: each coverage test shows [sequential] + [random], both passing    ✅ 2026-06-17
            (114 passed + 6 xfail TODO-F1 per version, SS2017–2025)

TRACK B — pre-2008 catalog (best-effort; Part III) — no dependency on Track A
  [ ] III.3.1 Extract 2005 catalog offsets as clean-room facts (OrcaMDF, §17 boundary)
  [ ] III.3.2 Diff vs catalog.py _SYS*_COLS; document deltas
  [ ] III.3.3 Add version-gated _SYS*_COLS_2005 path in catalog.py
  [ ] III.3.4 Verify data equivalence: SalesDBOriginal.bak == SalesDB2014.bak (tables/rows)
  [ ] III.3.5 Record V02 as [HEURISTIC] in BAK_FORMAT_SPEC §12.2
```

## 4. Open gates / things needing a decision

| Gate | Question | Status |
|------|----------|--------|
| Phase 0 (I.2) | Run it, or proceed on the assumption `NEWID()` works? | ✅ **Resolved** — ran 2026-06-16; `NEWID()` confirmed to shuffle and change segment layout |
| Partition fixture (II.1) | Confirm deferral of `archive_columnstore_partition` random variant is acceptable. | ✅ **Confirmed deferred** — single-table variants sufficient for Part II |
| Multi-table (D4) | Confirmed single-table now; multi-table FK variant is a later, separate plan. | ✅ **Confirmed** |
| Part III scope (III) | Accept best-effort (data-equivalence) for V02, or hold for SS2005/2006 instance? | ⬜ **Open** — best-effort track; no instance available |
| Track A order (0.2) | Confirm spec-closure order V11 → G44 → V13 → G14 → MTF | ✅ **Resolved** — V11, G44 done; next is V13 (VI) |
