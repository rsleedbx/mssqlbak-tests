"""Trace whether before-image undo fires for temporal_test/snapshot rows.

Monkeypatches mssqlbak.rows._apply_before_image to log each call, and also
logs the before_images dict keys passed to read_table_rows.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import deltalake

import mssqlbak.rows.patch as _patch_mod
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.logtail import logtail_from_bak

_calls: list[str] = []
_orig = _patch_mod._apply_before_image


def _wrap(after_row, patch):  # type: ignore[no-untyped-def]
    out = _orig(after_row, patch)
    _calls.append(f"applied: in_len={len(bytes(after_row))} out_len={len(bytes(out))} "
                  f"row_start={getattr(patch,'row_start',None)} "
                  f"undo={getattr(patch,'undo_data',b'')!r}")
    return out


_patch_mod._apply_before_image = _wrap  # type: ignore


def main() -> int:
    bak = sys.argv[1]
    tail = logtail_from_bak(bak)
    print(f"modified_slots ({len(tail.modified_slots)}): {sorted(tail.modified_slots)[:12]}")
    print(f"before_images keys ({len(tail.before_images)}): {sorted(tail.before_images.keys())[:12]}")
    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(bak, tmp)
        for sd in sorted(Path(tmp).iterdir()):
            for td in (sorted(sd.iterdir()) if sd.is_dir() else []):
                if not td.is_dir():
                    continue
                t = deltalake.DeltaTable(str(td)).to_pyarrow_table()
                if "label" in t.column_names:
                    labels = t.column("label").to_pylist()
                    print(f"{sd.name}.{td.name} labels[:12]={labels[:12]}")
    print(f"\n_apply_before_image called {len(_calls)} times:")
    for c in _calls[:12]:
        print("  " + c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
