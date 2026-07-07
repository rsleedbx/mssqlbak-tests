# Test gap audit — 2026-07-05

Comprehensive inventory of every skip, xfail, bypass, and known gap in the
test suite as of this date.

---

## 1. Active xfails (fire when specific conditions are met)

### `test_stats.py`

`pytest.xfail(gap_reason)` fires for any fixture registered in
`tools/known_gaps.py::KNOWN_GAPS`.  One entry today:

| Fixture | Reason |
|---|---|
| `tde_full` | TDE-encrypted backup — extraction raises `EncryptedBackupError` by design |

### `test_dirty_backup.py`

Three `pytest.xfail(reason)` calls (lines 3046, 3216, 3252) gated on
`gap_reason()`.  With only `tde_full` registered they only fire for that
fixture.

### `test_value_correctness.py`

`pytest.xfail` fires when a known-gap extraction raises an exception.
Currently only the TDE fixture triggers this path.

### `test_samples.py`

Samples not in `VERIFIED` are marked `xfail(non-strict)` if the file is
present on disk; skipped if absent.  Unverified samples today:

| Filename | Status if present |
|---|---|
| `AdventureWorks2008R2.bak` | xfail |
| `telcoedw2.bak` | xfail |
| `velibDB.bak` | xfail |
| `WideWorldImporters-Full.bacpac` | xfail |
| `WideWorldImporters-Full_old.bacpac` | xfail |
| `WideWorldImporters-Standard.bacpac` | xfail |
| `WideWorldImporters-Standard_old.bacpac` | xfail |
| `WideWorldImportersDW-Full.bacpac` | xfail |
| `WideWorldImportersDW-Standard.bacpac` | xfail |

### Dynamic xfail registries — all empty

The following registries gate `request.applymarker(xfail)` calls.  All are
empty; no tests are xfailed through them.

| Registry | Location | Current value |
|---|---|---|
| `COLUMNSTORE_XFAIL` | `tools/tabletypematrix.py` | `frozenset()` |
| `COLUMNSTORE_LARGE_XFAIL` | `tools/tabletypematrix.py` | `frozenset()` |
| `_STRUCTURAL_XFAIL` | `tests/test_cci_extended_coverage.py` | `{}` |
| `_SENTINEL_XFAIL` | `tests/test_cci_extended_coverage.py` | `{}` |
| `_NULL_COUNT_XFAIL` | `tests/test_cci_extended_coverage.py` | `{}` |
| `_XFAIL_TABLES` | `tests/test_cci_types_large_coverage.py` | `frozenset()` |

---

## 2. Active skips (currently fire)

### `native_json` table type (11 tests)

`test_tabletype_coverage.py` and `test_tabletype_cci_large_coverage.py` skip
`native_json` with reason "covered by version-specific fixture".  Intentional
test organization — the type is exercised by a dedicated fixture.

### `test_stats.py::test_extraction_matches_sql_server_stats`

Skipped entirely with "got empty parameter set" because no `stats.json`
ground-truth files exist in the local environment.  The test is unreachable
until stats are generated with `tools/make_stats_fixture.py`.

### Engine tests (`@pytest.mark.engine`)

Skip without a live SQL Server connection:

- `test_byte_map.py::test_byte_map_matches_engine`
- `test_dbi_collation.py::test_dbi_collation_engine`
- `test_engine_diff.py` (entire file via `importorskip("mssql_python")`)

### Optional-dependency tests

| Test file | Skips when |
|---|---|
| `test_pbixray_verifier.py` | `pbixray` package or `.pbix` file absent |
| `test_columnstore.py`, `test_decode_synthetic.py` | `xmhuffman` package absent |

### Sample tests (`@pytest.mark.samples` / `--samples` flag)

Skipped in normal runs; only execute with `pytest --samples`:

- All of `test_samples.py`
- `test_sink_perf.py::test_sample_*`
- `test_mtf_gap_bridging.py::test_baseball_data_*`
- `test_bacpac.py::test_bacpac_*_sample`

### Catalog / fixture-version skips

`test_catalog_version.py` skips the four version-specific catalog fixtures
(`2012`, `2016`, `2019`, `2022`) when they have not been generated locally
(`python -m tools.make_catalog_fixture --engine <year>`).

### Fixture-absent skips

All fixture-tagged tests (`@pytest.mark.fixture`) skip when the corresponding
`.bak` file does not exist on disk.  These are expected on a clean checkout
until `tools/fixture_run.py` has been run.

---

## 3. Known format gaps — not asserted, silently bypassed

### Column-level min/max skips (`_KNOWN_MINMAX_COL_GAPS` in `test_stats.py`)

**Resolved 2026-07-05 — the dict is now empty.** An audit of all six former
entries against ground truth on every version (2017/2019/2022/2025) found each
was either a decoder gap that had since been fixed or a redundant duplicate of
the type-level `_MINMAX_SKIP_TYPES` skip.

| Former column key | Disposition |
|---|---|
| `dirtycoverage_delete.dbo.delete_test.id` | Fixed — ghost slot no longer emitted; min/max matches (int). Entry removed; real comparison now runs. |
| `dirtycoverage_temporal_update.dbo.temporal_test.ValidFrom` | Fixed — no ghost history row emitted; min/max matches (datetime2). Entry removed; real comparison now runs. |
| `columnstore_minimal.dbo.cs_10000.dto` | Fixed — enc=5 Format D datetimeoffset decodes correctly; min/max matches. Entry removed; real comparison now runs. |
| `compressioncoverage_full.dbo.cmp_columnstore_archive.dto` | Fixed — same decoder path; min/max matches. Entry removed; real comparison now runs. |
| `tabletypecoverage_full.dbo.tt_partition.c_varbinary_max` | Redundant — `varbinary` is in `_MINMAX_SKIP_TYPES`; the per-column entry never had any effect. Entry removed. |
| `AdventureWorks{2012…2022}` — 5 columns | Redundant — `Person.Password.*` are `varchar` and the `Production` LOBs are `varbinary`; all covered by `_MINMAX_SKIP_TYPES`. Entries removed. |

The `varchar`/`varbinary`/`image` columns above remain bypassed at the **type
level** by `_MINMAX_SKIP_TYPES` — a ground-truth-generation limitation
(`register_bak.py` uses CI_AS-collated string min/max and `MIN(CONVERT(VARBINARY(250), …))`
truncate-before-min), not a decoder bug.  Genuinely un-bypassing those types
requires regenerating every `stats.json` with BIN2-ordered / full-length
aggregates against a live engine; tracked by the TODOs in `_MINMAX_SKIP_TYPES`.

### Format sub-problems documented in `tools/known_gaps.py` comments (untested)

These are documented but no fixture exercises the path and no assertion
exists:

1. **enc=5 ARCHIVE sub-block overflow-row `pre_meta` layout** — the
   `pre_meta` format for overflow rows in COLUMNSTORE_ARCHIVE compressed
   sub-blocks is not confirmed.  Needs DBCC CSINDEX from an `arch2` fixture.

2. **enc=5 Format D multichunk / >32 767-row overflow rows** — the second-pool
   index-entry format for large segments (`u32@38 == n_rows`) is partially
   observed.  The exact stride and last-chunk "contaminated" overflow layout
   are not confirmed.  No checked-in fixture exercises a segment with
   > 32 767 rows, so this path is currently unexercised (distinct from the
   ≤ 10 000-row `cs_10000.dto` second-pool case, which now decodes correctly).

3. **v4 Huffman dict with > 128 entries** — single-page decoder only; the
   multi-page tree layout is speculative and not confirmed with DBCC CSINDEX.

---

## 4. Bugs documented in test comments but already fixed

The following tests carry `# xfail — Bug X` comments but no
`@pytest.mark.xfail` decorator.  The bugs are fixed; all tests pass.

| Comment | Bug | Status |
|---|---|---|
| `test_archive_types_coverage.py` | Bug E — NVARCHAR(20) ARCHIVE enc=3 null count | Fixed, passes |
| `test_archive_types_coverage.py` | Bug F — UNIQUEIDENTIFIER ARCHIVE enc=5 null count | Fixed, passes |
| `test_archive_types_coverage.py` | Bug G — VARBINARY(20) ARCHIVE enc=5 null count | Fixed, passes |
| `test_archive_types_coverage.py` | Bug H — VARCHAR(20) ARCHIVE enc=5 null count | Fixed, passes |
| `test_cci_binary_varbinary_compare_coverage.py` | Bug E3B — BINARY offset-table absent in enc=3 | Fixed, passes |
| `test_cci_binary_varbinary_compare_coverage.py` | Bug K3B — VARBINARY sparse-NULL polarity inversion | Fixed, passes |

---

## 5. Correctness coverage doc status

### Synthetic fixtures (per-version)

| Doc | Fixtures | Pass | xfail | Fail | Notes |
|---|---|---|---|---|---|
| `correctness_coverage_fixtures_2017.md` | 127 | 127 | 0 | 0 | |
| `correctness_coverage_fixtures_2019.md` | 126 | 126 | 0 | 0 | |
| `correctness_coverage_fixtures_2022.md` | 145 | 144 | 0 | 1 | `corrupt_metadata_confidence_full` — intentional; asserts `Severity.FAIL` |
| `correctness_coverage_fixtures_2025.md` | 132 | 132 | 0 | 0 | |

The 1 fail in 2022 (`corrupt_metadata_confidence_full.bak`) is a deliberately
malformed backup.  `test_corrupt_metadata_confidence_coverage.py` asserts
`report.status is Severity.FAIL`; the correctness tool counts it as a fail
because catalog recovery fails.

### Real-world fixtures

`correctness_coverage_fixtures_realworld.md` (generated 2026-07-05):

**59 fixtures · 57 pass · 0 xfail · 2 fail**  
Tables: 1433/1433 · Columns: 12536/12536 · Rows ✓ · Nulls ✓ · Min/max ✓ · Cells ✓

The 2 failures are intentional corruption fixtures:

| Fixture | Reason |
|---|---|
| `CorruptDemoRestoreOrRepair.bak` | Confidence fail — row count differs from catalog |
| `DemoCorruptMetadata2000.bak` | Confidence fail — catalog recovery fails on unsupported layout |

---

## 6. `KNOWN_SKIPPED_TABLES` — empty

`tools/known_gaps.py::KNOWN_SKIPPED_TABLES` is `{}`.  No tables are currently
expected to be absent from extraction for any structural reason.

---

## 7. `KNOWN_GAPS` — one entry

`tools/known_gaps.py::KNOWN_GAPS` has one entry:

| Key | Reason |
|---|---|
| `tde_full` | TDE-encrypted backup — AES page encryption; extraction raises `EncryptedBackupError` by design |
