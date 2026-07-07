# 260623-2 — Rust P6 PAGE-compression min/max fix

**Session goal:** Fix min/max mismatches in the Rust `P6` fast path for PAGE-compressed
rowstore tables.  Python path (`read_table_rows`) is already correct; only the Rust
decoder in `rust/src/page_compress.rs` / `page_decode.rs` is broken.

---

## Scorecard at session start

`docs/correctness_coverage_fixtures_realworld.md` — **39 pass / 45 total / 6 fail**

| Fixture | Fail symptom | Priority |
|---------|-------------|---------|
| `AdventureWorksDW2016_EXT.bak` | `FactResellerSalesXL_PageCompressed` 45/54 min/max | **active** |
| `ContosoRetailDW.bak` | 7 tables fail min/max (see below) | **active** |
| `WideWorldImporters-Full.bak` | 0x02 PAGE-CI + 2 col-count gaps | parked |
| `WideWorldImporters-Full_old.bak` | same | parked |
| `tpcxbb_1gb.bak` | enc=3 G44, enc=1-on-CHAR, bigint off-by-8 | pending |
| `CreditBackup100.bak` | `dbo.charge` row count + legacy null/min-max | pending |

---

## Active task — G3: PAGE-compressed rowstore min/max

### Failing tables

**AdventureWorksDW2016_EXT.bak**
- `dbo.FactResellerSalesXL_PageCompressed` — 45/54 min/max (9 column mismatches).
  All other tables in this fixture pass.

**ContosoRetailDW.bak**
- `dbo.DimProduct` — 54/58 (4 mismatches)
- `dbo.FactInventory` — 25/32 (7 mismatches)
- `dbo.FactITMachine` — 14/16 (2 mismatches)
- `dbo.FactOnlineSales` — 22/36 (14 mismatches)
- `dbo.FactSales` — 28/38 (10 mismatches)
- `dbo.FactSalesQuota` — 21/26 (5 mismatches)
- `dbo.FactStrategyPlan` — 19/22 (3 mismatches)

Observed wrong values: `MachineKey` min = **-128** (expect positive int ≥ 1);
negative `money` values for `UnitCost`, `UnitPrice`, `CostAmount`.

### Why only the Rust path?

`extract_bak_to_delta` dispatches PAGE-compressed tables with supported column types
to the Rust `P6` path (`decode_compressed_page_to_columns`).  Python `read_table_rows`
produces correct values for these same tables.

### Root cause identified

In `rust/src/page_compress.rs` — `PageCI::parse` — the CI anchor record was parsed
with `CdValue::Zero => None` (meaning "no anchor").  Python stores `b""` (empty bytes)
for the same case.

Consequence: a data row on a zero-anchor column with a `_CD_SHORT` inline byte of
`b'\x00'` was NOT treated as anchored.  The byte was returned verbatim and decoded as
a 1-byte excess-encoded int → value = `0x00 - 128 = -128`.

A secondary bug: the CI type check used a fixed equality test (`page_raw[base] == 0x06`)
that silently rejected `0x02` (anchor-only, no dictionary) pages.

### Fixes applied (in `rust/src/page_compress.rs`)

1. **CI type check** — replaced `== 0x06` with flag-based check:
   ```rust
   const CI_HAS_ANCHOR: u8 = 0x02;
   const CI_HAS_DICT:   u8 = 0x04;
   if (flags & HDR_CD_FORMAT) != 0 || (flags & CI_HAS_ANCHOR) == 0 { return None; }
   ```

2. **Anchor zero** — changed `CdValue::Zero => None` to `CdValue::Zero => Some(vec![])`.
   This makes Rust match Python: the anchor is present but zero-length, so data rows'
   inline bytes are correctly prefix-expanded (stripping the leading `plen=0` byte)
   instead of being passed through verbatim.

Rebuilt with:
```
cd rust && touch src/page_compress.rs src/page_decode.rs && maturin develop --release
```

Installed .so timestamp: `Jun 23 16:11` — matches source.

### Verification status

**NOT YET CONFIRMED.**  The diag script was never run after the rebuild.  The previous
session's verification probes timed out or used incorrect module paths.

### Next step to resume

```bash
# Run the per-column diff for each failing fixture:
.venv/bin/python -m tools.diag_realworld_diff \
    tests/fixtures_realworld/ContosoRetailDW.bak

.venv/bin/python -m tools.diag_realworld_diff \
    tests/fixtures_realworld/AdventureWorksDW2016_EXT.bak
```

If both come back clean → regenerate `docs/correctness_coverage_fixtures_realworld.md`
and move to the next task.

If failures persist → look in `rust/src/page_decode.rs` at `excess_be_int` and the
`CdValue::Short` branch in `push_compressed_value` (line ~1020–1035).  The `-128`
pattern means a 1-byte `b'\x00'` is still reaching `excess_be_int` un-expanded;
the anchor lookup for that `phys_idx` is still returning `None`.

---

## Subsequent tasks (priority order)

### G4 — tpcxbb_1gb.bak (3 independent bugs)

| id | Symptom | Affected tables |
|----|---------|----------------|
| tpcxbb-enc3 | enc=3 G44 v4 Huffman dict empty → all/partial null | unknown subset |
| tpcxbb-enc1 | enc=1-on-CHAR all-null decode | unknown subset |
| tpcxbb-minmax | bigint `wcs_click_date_sk` min/max off by 8 | `web_clickstreams` |

Approach: `tools/diag_realworld_diff.py` to identify affected columns, then targeted
probe with Python path to isolate enc=3/enc=1 vs shared logic.

### G5 — CreditBackup100.bak

- `dbo.charge`: row count wrong (extracted 0 or wrong count), legacy null/min-max
  mismatch.  Likely a B-tree traversal issue on an old-format table (backup from SQL
  Server 2000 era).

### G6 — WideWorldImporters-Full.bak (parked)

Root-caused: `0x02` PAGE-CI anchor-only format.  The Python side was fixed in a prior
session.  The Rust side may also need the same CI-type fix (already applied in fix #1
above).  Once G3 is confirmed, re-run diag to see if WWI also clears.

---

## Key files

| File | Role |
|------|------|
| `rust/src/page_compress.rs` | `PageCI::parse` — CI header + anchor parsing |
| `rust/src/page_decode.rs` | `push_compressed_value` — per-column type dispatch |
| `mssqlbak/rowcompress.py` | Python reference implementation (correct) |
| `mssqlbak/extract.py` | `_try_extract_table_rust_compressed` P6 dispatch |
| `tools/diag_realworld_diff.py` | Per-column correctness diff against stats.json |
| `tools/correctness_coverage.py` | Bulk report generator |
| `docs/correctness_coverage_fixtures_realworld.md` | Last generated: 2026-06-23 (stale — pre-Rust fix) |

---

## Hooks

A `afterShellExecution` hook is active (`.cursor/hooks.json` + `.cursor/hooks/diag-reminder.py`).
After every shell command it injects a reminder to run `tools/diag_realworld_diff.py`
before declaring any fix complete.

---

## Quick-start commands

```bash
# Rebuild Rust extension after any src/page_*.rs change:
cd rust && maturin develop --release && cd ..

# Verify a fixture:
.venv/bin/python -m tools.diag_realworld_diff tests/fixtures_realworld/ContosoRetailDW.bak

# Regenerate full coverage doc:
.venv/bin/python -m tools.correctness_coverage \
    --fixture-dir tests/fixtures_realworld \
    --out docs/correctness_coverage_fixtures_realworld.md
```
