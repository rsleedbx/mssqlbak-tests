#!/usr/bin/env python3
"""Generate ``corrupt_metadata_confidence_full.bak`` for confidence failure coverage."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import skip_if_exists  # noqa: E402

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "corrupt_metadata_confidence_full.bak"

# Deterministic malformed content. This is intentionally not a valid backup:
# confidence analysis should fail catalog recovery and report it clearly.
_PAYLOAD = (
    b"TAPE"
    + b"\x00" * 508
    + b"MSSQLBAK_CORRUPT_METADATA_CONFIDENCE_FIXTURE"
    + bytes(range(256)) * 4
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(_PAYLOAD)
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
