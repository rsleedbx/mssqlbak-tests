#!/usr/bin/env python3
"""Probe decode_cfp_log_records for xtp_checkpoint_straddle_full.bak."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from mssqlbak.xtp import (  # noqa: E402
    scan_cfp_log_records,
    _xtp_fixed_cols,
    _xtp_var_cols,
    _xtp_fixed_width,
    _decode_payload,
    _identity_column,
    _xtp_fully_decodable,
    _xtp_var_record_consistent,
)
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402

BAK = _REPO / "tests/fixtures_2022/xtp_checkpoint_straddle_full.bak"

store = PageStore.from_bak(str(BAK))
schema = recover_schema(store)
xtp_tables = [t for t in schema.tables if t.is_memory_optimized]

t = xtp_tables[0]
print(f"Table: {t.schema}.{t.name}")
fixed = _xtp_fixed_cols(t)
var_cols = _xtp_var_cols(t)
fw = sum(_xtp_fixed_width(c) for c in fixed)
print(f"Fixed cols: {[(c.name, c.type_id, _xtp_fixed_width(c)) for c in fixed]}")
print(f"fw={fw}, var cols: {[(c.name, c.type_id) for c in var_cols]}")
idcol = _identity_column(t)
print(f"idcol: {idcol.name if idcol else None}")
print(f"fully_decodable: {_xtp_fully_decodable(t)}")

bak_bytes = BAK.read_bytes()
lb_map = scan_cfp_log_records(bak_bytes)
records = lb_map[0]
print(f"\nLB=0x00: {len(records)} records, payload sizes: {sorted(set(len(p) for _, p in records))[:10]}")

print("\nFirst 5 record probes:")
for seq, p in records[:5]:
    consistent = _xtp_var_record_consistent(p, fw, len(var_cols))
    print(f"  seq={seq} len={len(p)} consistent={consistent} hex={p.hex()}")
    try:
        row = _decode_payload(p, t, xtp_log_mode=True)
        print(f"    decoded={row}")
    except Exception as e:
        print(f"    DECODE ERROR: {e}")
