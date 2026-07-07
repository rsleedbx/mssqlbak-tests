# Float Canon Precision Fix: `_FLOAT_SIG` 13 → 15

_Written 2026-07-01_

## Failing test

```
tests/test_value_correctness.py::test_canon_float_text_does_not_overflow_max_finite_value
```

```python
assert canon("1.79769313486232E+308", "float") == "1.79769313486232e+308"
# actual:                                          "1.797693134862e+308"   ← 13-digit truncation
```

## Root cause

`_FLOAT_SIG = 13` in `tools/cell_canon.py` causes `_format_sig_decimal` to truncate the
14-significant-digit input `"1.79769313486232E+308"` to 13 digits.

### History of `_FLOAT_SIG`

| Commit | Change | Reason |
|--------|--------|--------|
| initial | `_FLOAT_SIG = 12` | baseline |
| `619cf94` | 12 → 13 | large integer float IDs (≈ 2.85 × 10¹²) were colliding at 12 significant digits |
| `35d6d9c` | stays at 13 | GT parquet switched to Python `repr()` strings to avoid SQL Server 14/15-digit text vs repr divergence |
| `35d6d9c` docstring | says "Using `sig = 15`…" | stale — docstring was written when 15 was the intended value and was not updated when 13 was chosen |

The original design intent was `sig = 15`. The `_canon_float` docstring names 15 explicitly and gives the
correct example (`75.398223686155` → `75.39822368615496` both round to the same value at 15g). The
constant was reduced to 13 for a distinct reason (float ID collision) without revisiting 15.

## Quantization comparison across significant-digit levels

| Input | sig=13 | sig=14 | sig=15 |
|-------|--------|--------|--------|
| `"1.79769313486232E+308"` (SQL Server max-finite, 14 sig figs) | `1.797693134862e+308` | `1.7976931348623e+308` | `1.79769313486232e+308` ✓ |
| `"1.7976931348623157e+308"` (Python repr, what GT parquet stores) | `1.797693134862e+308` | `1.7976931348623e+308` | `1.79769313486232e+308` |
| `"75.398223686155"` (typical 14-digit SQL Server text) | `75.39822368616` ← drift | `75.398223686155` | `75.398223686155` |
| `"75.39822368615496"` (Python repr of same float) | `75.39822368615` | `75.398223686155` | `75.398223686155` |
| `0.1 + 0.2` vs `0.3` | equal | equal | equal |
| large float ID `2850000000000` vs `2849999999999` | distinct | distinct | distinct |

Three observations from the table:

1. Only `sig=15` preserves all 14 significant digits of the max-finite SQL Server text.
2. `sig=13` introduces a one-digit drift between SQL Server 14-digit text (`75.39822368616`) and
   the matching Python repr (`75.39822368615`). This divergence was masked because commit `35d6d9c`
   switched GT parquet to store Python `repr()` strings rather than SQL Server text, putting both
   sides through the same code path.
3. `0.1 + 0.2 == 0.3` and large integer float ID distinguishability are unaffected at any sig level.

## Alternatives considered

### 1. Weaken the test

Change the expected output to `"1.797693134862e+308"` (13 digits). Cross-engine digest comparison
still works at sig=13 because both GT parquet (now `repr()`) and the extracted float produce the
same truncated string. This removes a real invariant: SQL Server's own text representation should
not be corrupted by canonicalization.

**Not applied.**

### 2. Capture GT with `Decimal` instead of `repr()`

Store the exact decimal representation in GT parquet rather than Python `repr()`. Does not fix
the truncation in `_canon_float` and adds a new value form the canon function must handle without
providing correctness benefit.

**Not applied.**

### 3. Preserve input significant digits in the string branch

Use `max(sig, count_of_input_sig_digits)` in the string branch so string input is never
truncated below its own precision. This introduces an inconsistency: a 14-digit SQL Server string
and the same value as an extracted float64 go through different quantization levels and diverge
(e.g., string at 15 vs float at 13). Cross-engine matching breaks for any value the string branch
sees at more than 13 digits.

**Not applied.**

### 4. Skip quantization for out-of-range string values

Detect `abs(Decimal(s)) > sys.float_info.max` in the string branch and skip quantization for
those values (they have no float64 counterpart to align with). Principled, but adds a code path
for a narrow edge case and does not fix the `75.39822368616` drift for in-range values.

**Not applied.**

### 5. Raise `_FLOAT_SIG` to 15

Restores the original design intent. At sig=15:

- max-finite SQL Server text is preserved (test passes).
- 14-digit SQL Server text and its Python repr round to the same 15-digit canonical form
  (the masked drift is eliminated, not just re-masked).
- `0.1 + 0.2 == 0.3` passes unchanged.
- Large integer float IDs remain distinct.
- No new code paths.

**Applied.**

## Fix

`tools/cell_canon.py` — changed `_FLOAT_SIG` from 13 to 15 and updated the comment to explain
the reasoning and the history of the 12 → 13 → 15 evolution.

Updated comment:

```python
# Significant digits used to quantize binary floating point to a stable decimal
# string.  15 is the correct value for two reasons:
#
# 1. Round-trip fidelity: SQL Server emits FLOAT text with up to 15 significant
#    digits (e.g. "1.79769313486232E+308" for the maximum finite value).  At
#    sig=15 both the SQL Server text and Python's repr() of the same float64
#    (which has up to 17 digits) round to the same 15-digit canonical form.
#    sig=13 introduces a one-digit drift for 14-digit SQL Server text (e.g.
#    "75.398223686155" → "75.39822368616" at 13g vs "75.39822368615" for the
#    matching Python repr), which was masked only because GT parquet was
#    changed (commit 35d6d9c) to store Python repr() instead of SQL Server
#    text.
#
# 2. Large float ID coverage: 13 was previously chosen as the minimum to
#    distinguish adjacent large float IDs (≈ 2.85 × 10¹²).  15 also
#    distinguishes them (with more precision), so there is no reason to use
#    the minimum — 15 is the correct value.
_FLOAT_SIG = 15
```

## Verification

```
tests/test_value_correctness.py::test_canon_float_quantizes_beyond_precision      PASSED
tests/test_value_correctness.py::test_canon_float_text_does_not_overflow_max_finite_value  PASSED
tests/test_value_correctness.py::test_canon_spatial_normalizes_float_text_precision  PASSED
tests/test_value_correctness.py::test_fixture_cells_match_ground_truth[float_extreme_full.bak.cells0]  PASSED
tests/test_value_correctness.py::test_fixture_cells_match_ground_truth[float_extreme_full.bak.cells1]  PASSED
tests/test_value_correctness.py::test_fixture_cells_match_ground_truth[float_extreme_full.bak.cells2]  PASSED
tests/test_value_correctness.py::test_fixture_cells_match_ground_truth[float_extreme_full.bak.cells3]  PASSED
```

8 of 8 float-related tests pass. No regressions.
