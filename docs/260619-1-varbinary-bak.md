# VARBINARY enc=5 Format C — Diagnostic Fixture Specs

**Date:** 2026-06-19  
**Status:** Generated and tested — 2026-06-19  
**Scope:** Five new `.bak` fixtures targeting the three unresolved mysteries in
`cci_varbinary` (K3B) Format C decoding

**Related:**
- [`260618-2-enc3-bugs.md`](260618-2-enc3-bugs.md) — K3B bug definition
- [`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md) §7.x — enc=5 Format C spec
- [`mssqlbak-fixtures` skill](../.cursor/skills/mssqlbak-fixtures/SKILL.md) — generator wiring checklist
- Existing fixture: `tests/fixtures_2022/cci_types_large_full.bak` → table `cci_varbinary`

---

## 1. Open mysteries (K3B)

The existing 1,200-row `cci_varbinary` fixture has revealed the following about the
Format C (enc=5, XPRESS-compressed) layout for `VARBINARY(16)`:

| ID | Mystery | What is known | What is unknown |
|----|---------|---------------|-----------------|
| **M1** | Pool entry encoding | Entries are 8-byte fixed slots; 1-byte values pad differently from 2-byte values | Exact encoding rule: how slot bytes map to the VARBINARY bit pattern for arbitrary k-byte values |
| **M2** | Index encoding | `index[i]` is a 2-byte LE value; null sentinel is `0xFE00`; `v=0` → LOW row | What `v` encodes for non-null, non-LOW rows: not a plain pool byte offset |
| **M3** | Pool/index boundary | Pool appears to end near byte 9592 for a 1,199-entry pool | `CAST(1197)` straddles the boundary; unclear whether this is an off-by-one or a deliberate layout quirk |

---

## 2. Fixture specifications

### F1 — `cci_varbinary_micro` (highest priority)

**Purpose:** Resolve all three mysteries (M1, M2, M3) by making the full pool
and index manually inspectable.

**Generator:** `tools/make_cci_varbinary_micro_fixture.py`  
**Output:** `tests/fixtures_<year>/cci_varbinary_micro_full.bak`

**Schema:**

```sql
CREATE TABLE cci_varbinary_micro (
    id   INT            NOT NULL,
    val  VARBINARY(16)  NULL
);
CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_micro
    ON cci_varbinary_micro;
```

**Rows:**

| id | val | Notes |
|----|-----|-------|
| 1 | `0x01` | 1-byte value (LOW) |
| 2 | `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF` | 16-byte value (HIGH = all-0xFF) |
| 3 | NULL | null sentinel |
| 4 | `0x0102` | 2-byte value |
| 5 | `0x0201` | 2-byte value, reversed byte order from id=4 |
| 6 | `0xABCDEF` | 3-byte value, odd width |
| 7 | `0x0000000000000001` | 8-byte value = `item_size` exactly |

After insert: `ALTER INDEX ... REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`.

**What this reveals:**
- Pool has 6 non-null entries. Each entry is directly traceable to a known source
  value, making M1 immediately readable.
- Index has 7 entries. With pool ≤ 48 bytes and index ≤ 14 bytes, M3 (straddling)
  cannot occur at this size; its absence or presence at this scale disambiguates
  whether it is inherent to the encoding or an artifact of pool size.
- Comparing `v` values for id=4 and id=5 (same length, different byte content)
  resolves M2 directly.

**Variants to generate in the same run:**

- `cci_varbinary_micro_nullonly`: 1 non-null row + 20 NULLs. Isolates the null
  sentinel encoding without any pool interference.
- `cci_varbinary_micro_1byte`: 20 rows, val = `CAST(n AS VARBINARY(16))` for
  n = 1..20. All values are 1-byte (n ≤ 255). Shows a pure 1-byte pool with no
  multi-byte values.

---

### F2 — `cci_varbinary_maxwidth`

**Purpose:** Determine whether `item_size` in the XPRESS marker is driven by
observed value width or by `max_length`. Resolves M1.

**Generator:** add a table to an existing fixture or a new
`tools/make_cci_varbinary_maxwidth_fixture.py`  
**Output:** `tests/fixtures_<year>/cci_varbinary_maxwidth_full.bak`

**Schema:** `VARBINARY(16)`, 1,200 rows.

**Row values:**

```sql
-- all values are exactly 16 bytes (max_length)
filler_expr = "CAST(CAST(n AS BINARY(16)) AS VARBINARY(16))"
-- id=1 low:  0x0000000000000000000000000000001
-- id=2 high: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
-- id=3: NULL
-- id=7..1203: CAST(CAST(n AS BINARY(16)) AS VARBINARY(16))
```

**What this reveals:**  
If `item_size` in the XPRESS marker changes from 8 (observed in existing
`cci_varbinary`) to 16, the item size tracks observed value byte width, not
`max_length`. If it stays at 8, item size is type-class-fixed regardless of
value width.

---

### F3 — `cci_varbinary_narrowmax`

**Purpose:** Determine whether `item_size` follows `max_length` by changing the
column declaration to `VARBINARY(4)`. Complements F2. Resolves M1.

**Generator:** add table to an existing fixture or new
`tools/make_cci_varbinary_narrowmax_fixture.py`  
**Output:** `tests/fixtures_<year>/cci_varbinary_narrowmax_full.bak`

**Schema:** `VARBINARY(4)`, 1,200 rows.

**Row values:**

```sql
-- id=1 low:  0x01
-- id=2 high: 0xFFFFFFFF  (4 bytes = max_length)
-- id=3: NULL
-- filler_expr = "CAST(n AS VARBINARY(4))"  -- values 1..1197, each 1-2 bytes for small n
```

**What this reveals:**  
`_enc5_item_size` currently returns `col.max_length` (4 here, 16 in the existing
fixture). If the XPRESS marker `item_size` is also 4, `max_length` drives slot
width. If `item_size` is 8, the slot width is fixed at 8 for all variable-binary
columns regardless of `max_length`. Either result pins the correct implementation
of `_enc5_item_size` for VARBINARY.

---

### F4 — `cci_binary_varbinary_compare`

**Purpose:** Compare `BINARY(8)` (known-working Format C) and `VARBINARY(8)` in
the same row group with identical values. Resolves M1 and M2.

**Generator:** `tools/make_cci_binary_varbinary_compare_fixture.py`  
**Output:** `tests/fixtures_<year>/cci_binary_varbinary_compare_full.bak`

**Schema:**

```sql
CREATE TABLE cci_binary_varbinary_compare (
    id   INT           NOT NULL,
    bin8 BINARY(8)     NULL,
    vb8  VARBINARY(8)  NULL
);
```

**Row values:**

```sql
-- id=1: bin8 = 0x0000000000000001, vb8 = 0x0000000000000001
-- id=2: bin8 = 0xFFFFFFFFFFFFFFFF, vb8 = 0xFFFFFFFFFFFFFFFF
-- id=3: bin8 = NULL, vb8 = NULL
-- filler: n=1..1197
--   bin8 = CAST(n AS BINARY(8))
--   vb8  = CAST(n AS VARBINARY(8))
```

Both columns share the same row group (same segment). `BINARY(8)` uses
`item_size=8` and its Format C pool/index is known to decode correctly.

**What this reveals:**  
Side-by-side byte comparison of the two column blobs at the same `item_size`
directly shows what VARBINARY adds — different null sentinel, different pool sort
order, different index encoding, or none of the above. This is the cleanest
controlled experiment available.

---

### F5 — `cci_varbinary_small_rowgroup`

**Purpose:** Resolve M3 by producing a segment where pool and index sizes are
known by construction, making the boundary unambiguous.

**Generator:** add table to an existing fixture or new
`tools/make_cci_varbinary_small_rowgroup_fixture.py`  
**Output:** `tests/fixtures_<year>/cci_varbinary_small_rowgroup_full.bak`

**Schema:** `VARBINARY(16)`, **128 rows** (no NULLs, no structural LOW/HIGH
sentinel rows — all non-null filler).

**Row values:**

```sql
-- 128 rows, val = CAST(n AS VARBINARY(16)) for n=1..128
-- No NULL row intentionally — simplifies null sentinel analysis
```

**What this reveals:**  
With 128 non-null rows and item_size=8:
- Pool = 128 × 8 = 1,024 bytes
- Index = 128 × 2 = 256 bytes
- Total = 1,280 bytes (plus any alignment padding)

Any XPRESS-decompressed buffer near 1,280 bytes confirms these sizes. The exact
end of the pool is at byte 1,024, making straddling trivially detectable. If
`CAST(127)` or `CAST(128)` straddles the 1,024-byte boundary, M3 is confirmed as
inherent to the encoding. If not, M3 is an artifact of the specific 1,199-entry
pool in the existing fixture.

---

## 3. Generation priority and wiring

Generate in this order — each fixture resolves progressively more of M1/M2/M3:

| Order | Fixture | Mysteries resolved |
|-------|---------|--------------------|
| 1 | F1 `cci_varbinary_micro` | M1, M2, M3 |
| 2 | F4 `cci_binary_varbinary_compare` | M1, M2 (from known-good baseline) |
| 3 | F3 `cci_varbinary_narrowmax` | M1 (`item_size` vs `max_length`) |
| 4 | F2 `cci_varbinary_maxwidth` | M1 (`item_size` vs value width) |
| 5 | F5 `cci_varbinary_small_rowgroup` | M3 (boundary definitively) |

F1 alone may be sufficient to resolve all three mysteries. Generate F2–F5 only if
F1 leaves ambiguity.

### Wiring checklist per fixture (from `mssqlbak-fixtures` skill)

Each new fixture requires entries in:

```
- [ ] tools/make_<name>_fixture.py
- [ ] tools/fixture_run.py         (_run_<name>(); _COMMANDS; argparse; dispatch)
- [ ] tests/conftest.py            (FIXTURE_BAK_<NAME> + fixture_bak_<name>)
- [ ] tests/test_<name>_coverage.py
```

Import expected-value constants from the generator into the coverage test to
avoid drift.

### Generate command (once containers are running)

```bash
# All SQL Server versions
.venv/bin/python -m tools.fixture_run all-versions --suite cci-varbinary-micro

# One version only
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 cci-varbinary-micro
```

---

## 4. Generation results (2026-06-19)

All five specs were implemented across **SS2017, SS2019, SS2022, SS2025**.  The
spec's F2, F3, and F5 were combined into a single generator
(`make_cci_varbinary_probe_fixture.py` → `cci_varbinary_probe_full.bak`) to
reduce wiring overhead.

| Generator | Bak | Versions |
|-----------|-----|----------|
| `make_cci_varbinary_micro_fixture.py` | `cci_varbinary_micro_full.bak` | 2017/2019/2022/2025 |
| `make_cci_binary_varbinary_compare_fixture.py` | `cci_binary_varbinary_compare_full.bak` | 2017/2019/2022/2025 |
| `make_cci_varbinary_probe_fixture.py` | `cci_varbinary_probe_full.bak` | 2017/2019/2022/2025 |

### Test outcome

```
16 passed, 46 xfailed
```

Structural assertions (row count, id presence, NULL sentinel where expected)
all pass.  All value-decoding assertions are `xfail(strict=False)` because the
bugs under investigation (K3B, E3B) are not yet fixed.

### New finding — K3B is bidirectional

The test run exposed that K3B (null-polarity inversion) has two manifestations
depending on the column type and table schema:

| Fixture | Column | NULL row behaviour | Non-null row behaviour |
|---------|--------|--------------------|------------------------|
| `cci_varbinary_maxwidth` (VARBINARY(16), 1200 rows) | `val` | **None ✓** (correct) | all None (K3B fires) |
| `cci_varbinary_micro` (VARBINARY(16), 7 rows) | `val` | **None ✓** (correct) | all None (K3B fires) |
| `cci_varbinary_narrowmax` (VARBINARY(4), 1200 rows) | `val` | **garbage bytes ✗** | all None (K3B fires) |
| `cci_binary_varbinary_compare` (2-col, 1200 rows) | `bin8`, `vb8` | **garbage bytes ✗** | all None (K3B fires) |

The pattern suggests that for some type/width combinations the null-vector
polarity is inverted in the *opposite* direction: null rows are decoded as
non-null (returning garbage bytes from the pool) while non-null rows are decoded
as null (returning `None`).  For VARBINARY(16) the decoder happens to have the
correct polarity for the null sentinel but the wrong polarity for non-null rows.

The `cci_varbinary_small_rowgroup` table (128 rows, 0 NULLs) passes all
structural checks; value-decoding is xfail (some enc=3 VARBINARY bug other than
K3B may also be present, since there are no NULLs to trigger K3B).

### Implications for fixer agent

- K3B fix must handle **both polarity directions**.  The null-vector bit meaning
  (0 = null or 1 = null) differs by column type or segment metadata field.
- The fixer should look for a flag or header field in the Format C blob that
  controls null-vector polarity, rather than hard-coding one convention.
- `cci_varbinary_small_rowgroup` (0 NULLs) passing structural tests but failing
  value tests suggests there may be a separate decoding bug for VARBINARY that
  is independent of the null vector — worth isolating after K3B is fixed.

### Regenerate commands

```bash
.venv/bin/python -m tools.fixture_run all-versions \
  --suite cci-varbinary-micro \
  --suite cci-binary-varbinary-compare \
  --suite cci-varbinary-probe
```
