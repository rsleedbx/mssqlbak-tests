#!/usr/bin/env python3
"""Generate catalog version-matrix fixtures for G01/G21.

Runs :mod:`tools.make_catalog_fixture` for each engine in the matrix.

Usage::

    FIXTURE_DBA_PASSWORD=... python -m tools.make_version_matrix
    FIXTURE_DBA_PASSWORD=... python -m tools.make_version_matrix --engine 2022
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_catalog_fixture import ENGINES, main as catalog_main  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate catalog_ss*.bak fixtures")
    parser.add_argument("--engine", choices=ENGINES, action="append", dest="engines")
    parser.add_argument("--v1-inspect", action="store_true", help="Also build mssqlbak_v1_inspect.bak on 2012")
    args = parser.parse_args()
    engines = args.engines or list(ENGINES)
    rc = 0
    for eng in engines:
        sys.argv = ["make_catalog_fixture", "--engine", eng]
        if rc := catalog_main():
            return rc
    if args.v1_inspect or "2012" in engines:
        sys.argv = ["make_catalog_fixture", "--engine", "2012", "--compressed"]
        rc = catalog_main()
    return rc


if __name__ == "__main__":
    sys.exit(main())
