#!/usr/bin/env python3
"""Inspect logtail result for 2017 vs 2019 dirtycoverage_temporal_update.bak."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture

from mssqlbak.logtail import logtail_from_bak  # type: ignore[attr-defined]


def show(version: str) -> None:
    path = fixture(version, "dirtycoverage_temporal_update.bak")
    r = logtail_from_bak(path)

    print(f"\n=== {version} ===")
    print(f"  dirty_slots:             {len(r.dirty_slots)}")
    print(f"  restore_slots:           {len(r.restore_slots)}")
    print(f"  modified_slots:          {len(r.modified_slots)}")
    print(f"  before_images:           {len(r.before_images)}")
    print(f"  redo_rows:               {len(r.redo_rows)}")
    print(f"  committed_delete_slots:  {len(r.committed_delete_slots)}")
    print(f"  redo_patches:            {len(r.redo_patches)}")
    print(f"  restore_rows:            {len(r.restore_rows)}")
    print(f"  dirty_row_bytes:         {len(r.dirty_row_bytes)}")
    if r.dirty_slots:
        print(f"  dirty_slots detail: {list(r.dirty_slots)[:10]}")
    if r.restore_slots:
        print(f"  restore_slots detail: {list(r.restore_slots)[:10]}")
    if r.before_images:
        print(f"  before_images keys: {list(r.before_images.keys())[:10]}")
    if r.restore_rows:
        print(f"  restore_rows detail: {list(r.restore_rows)[:5]}")


def main() -> None:
    show("2017")
    show("2019")


if __name__ == "__main__":
    main()
