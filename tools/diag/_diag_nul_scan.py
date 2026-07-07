"""Scan dirty/update fixtures across all version dirs; flag cell mismatches
whose `got` value contains a NUL (the inherent 512-byte log-sector framing
overwrite).  Distinguishes the NUL-framing gap from other mismatch classes."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import deltalake

from mssqlbak.extract import extract_bak_to_delta
from tools import value_verify


def _has_nul(v: object) -> bool:
    if isinstance(v, str):
        return "\x00" in v
    if isinstance(v, (bytes, bytearray)):
        return b"\x00" in bytes(v)
    return False


def main() -> int:
    root = Path("tests")
    baks = sorted(root.glob("fixtures_*/*.bak"))
    pat = sys.argv[1] if len(sys.argv) > 1 else "update|wide|compress|lob"
    import re
    rx = re.compile(pat, re.I)
    for bak in baks:
        if not rx.search(bak.stem):
            continue
        cells_dir = value_verify.cells_dir_for(bak)
        if not cells_dir.exists():
            continue
        try:
            arrow_tables: dict[str, object] = {}
            with tempfile.TemporaryDirectory() as tmp:
                extract_bak_to_delta(str(bak), tmp)
                for sd in sorted(Path(tmp).iterdir()):
                    if not sd.is_dir():
                        continue
                    for td in sorted(sd.iterdir()):
                        if td.is_dir():
                            arrow_tables[f"{sd.name}.{td.name}"] = (
                                deltalake.DeltaTable(str(td)).to_pyarrow_table()
                            )
            results = value_verify.verify_bak(arrow_tables, cells_dir)
        except Exception as exc:  # noqa: BLE001
            print(f"{bak.parent.name}/{bak.stem}: ERROR {type(exc).__name__}: {exc}")
            continue
        nul_cols: set[str] = set()
        other_cols: set[str] = set()
        for fqn, r in results.items():
            if r.ok:
                continue
            for _key, col, got, _want in r.samples:
                if _has_nul(got):
                    nul_cols.add(f"{fqn}.{col}")
                else:
                    other_cols.add(f"{fqn}.{col}")
        if nul_cols or other_cols:
            tag = "NUL" if nul_cols and not other_cols else ("MIXED" if nul_cols else "OTHER")
            print(f"[{tag}] {bak.parent.name}/{bak.stem}")
            if nul_cols:
                print(f"    nul   : {sorted(nul_cols)}")
            if other_cols:
                print(f"    other : {sorted(other_cols)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
