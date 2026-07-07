"""Per-column correctness diff for a single real-world fixture.

Throwaway diagnostic: extracts one .bak and prints every column whose null
count or min/max disagrees with the committed `.bak.stats.json` ground truth.

Usage:
    .venv/bin/python -m tools.diag_realworld_diff tests/fixtures_realworld/NYCTaxi_Sample.bak
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from mssqlbak.extract import extract_bak_to_delta
from tools.correctness_coverage import _minmax_equal, _resolve_bak_input


def main(argv: list[str]) -> int:
    bak_path = Path(argv[1]).resolve()
    stats_path = bak_path.with_name(bak_path.name + ".stats.json")
    gt = json.loads(stats_path.read_text())
    bak_input = _resolve_bak_input(bak_path)

    import deltalake  # type: ignore[import]

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(bak_input, tmp)
        extracted: dict[str, dict] = {}
        for schema_dir in sorted(Path(tmp).iterdir()):
            if not schema_dir.is_dir():
                continue
            for tbl_dir in sorted(schema_dir.iterdir()):
                if not tbl_dir.is_dir():
                    continue
                try:
                    dt = deltalake.DeltaTable(str(tbl_dir))
                except Exception:
                    continue
                tbl = dt.to_pyarrow_table()
                ncs, mins, maxs = {}, {}, {}
                for cn in tbl.schema.names:
                    col = tbl.column(cn)
                    ncs[cn] = col.null_count or 0
                    try:
                        vals = col.drop_null().to_pylist()
                    except (ValueError, OverflowError):
                        vals = []
                    try:
                        mins[cn] = min(vals) if vals else None
                        maxs[cn] = max(vals) if vals else None
                    except (TypeError, ValueError):
                        mins[cn] = maxs[cn] = None
                extracted[f"{schema_dir.name}.{tbl_dir.name}"] = {
                    "rows": len(tbl), "nc": ncs, "min": mins, "max": maxs,
                }

    for ti in gt.get("tables", []):
        fqn = f"{ti['schema']}.{ti['name']}"
        exp_rows = ti["row_count"]
        act = extracted.get(fqn)
        if act is None:
            if exp_rows > 0:
                print(f"MISSING TABLE {fqn} (expected {exp_rows} rows)")
            continue
        if act["rows"] != exp_rows:
            print(f"ROW {fqn}: got {act['rows']} != exp {exp_rows}")
        for ci in ti.get("columns", []):
            cn = ci["name"]
            st = ci.get("sql_type", "")
            en = ci.get("null_count")
            if en is not None and act["nc"].get(cn) != en:
                print(f"NULL {fqn}.{cn} ({st}): got {act['nc'].get(cn)} != exp {en}")
            for which, gtv in (("min", ci.get("min_val")), ("max", ci.get("max_val"))):
                if gtv is None:
                    continue
                av = act[which][cn] if cn in act[which] else None
                if not _minmax_equal(av, gtv, st):
                    print(f"{which.upper()} {fqn}.{cn} ({st}): got {av!r} != exp {gtv!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
