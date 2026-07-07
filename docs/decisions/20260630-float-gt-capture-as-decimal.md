# Float ground-truth capture: native float vs CAST AS DECIMAL

**Date:** 2026-06-30  
**Status:** accepted

## Question

When `tools/cells_capture.py` selects a `FLOAT` or `REAL` column from SQL Server to
build the ground-truth parquet, should the SELECT expression cast the value to
`DECIMAL(38,15)` so that the driver returns an exact `decimal.Decimal` instead of a
binary `float`? The goal was to eliminate the `_FLOAT_SIG` quantization step and make
float comparison simpler.

## Options considered

### Option A — Cast to DECIMAL in the SELECT (proposed change)

```sql
CAST([col] AS DECIMAL(38, 15)) AS [col]
```

The Python driver returns `decimal.Decimal`. The GT parquet stores the SQL Server
decimal representation.

### Option B — Select as-is; canonicalize with repr() → Decimal on both sides (current)

```python
_FLOAT_SIG = 13   # in cell_canon.py

def _canon_float(value, sig):
    _fv = float(value)
    return _format_sig_decimal(Decimal(repr(_fv)), sig)
```

The driver returns a Python `float`. Both the GT capture and the mssqlbak decoder apply
the same `repr() → Decimal → format(sig=13)` path.

## Decision

Keep Option B (current approach).

## Reasoning

**Option A does not remove `_canon_float`.**  
The mssqlbak decoder always reads a binary IEEE 754 float from the `.bak` and returns a
Python `float`. That side still needs the full `repr() → Decimal → format` path regardless
of what the GT capture does. `_canon_float` cannot be deleted.

**Option A introduces a new mismatch vector.**  
`CAST(float AS DECIMAL(38,15))` applies SQL Server's rounding rules. Python's `repr(float)`
produces the shortest decimal that round-trips through IEEE 754. The two strategies can
produce different digit sequences beyond the 13th significant digit, creating a canonical
disagreement that does not exist when both sides go through `repr()` on the same binary
value.

**Option A breaks for `inf` and `nan`.**  
`CAST(CAST('inf' AS float) AS DECIMAL(38,15))` is a SQL Server error. A `CASE` guard would
be required in `_select_expr`, adding code rather than removing it.

**The current design is already minimal.**  
GT capture returns a Python `float` from the driver. Both sides start from the same IEEE 754
binary value and apply the identical `repr() → Decimal → _format_sig_decimal(sig=13)` path,
so they agree trivially. The `_FLOAT_SIG = 13` constant and the string branch in
`_canon_float` exist only to handle legacy GT parquets captured before this design was
established (when SQL Server's 15-digit text was stored directly).
