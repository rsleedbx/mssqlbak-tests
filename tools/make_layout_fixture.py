#!/usr/bin/env python3
"""Build layout-coverage reference ``.bak`` from :mod:`tools.layoutmatrix`.

Creates the ``LayoutCoverage`` database with PK-position and column-count
boundary tables, backs up, and copies to ``tests/fixtures/layoutcoverage_full.bak``.

Requires a running SQL Server container (forgedb) and ``FIXTURE_DBA_PASSWORD``.

Usage::

    python -m tools.make_layout_fixture
    python -m tools.make_layout_fixture --compressed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.layoutmatrix import (  # noqa: E402
    DB_NAME,
    OUT_COMPRESSED_PATH,
    OUT_PATH,
    build_sql,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate layout coverage .bak")
    parser.add_argument(
        "--compressed",
        action="store_true",
        help="Apply PAGE compression to layout_pk_int_first (layoutcoverage_compressed.bak)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: layoutcoverage_full.bak or _compressed.bak)",
    )
    args = parser.parse_args()
    out = args.out or (OUT_COMPRESSED_PATH if args.compressed else OUT_PATH)
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(page_compression=args.compressed), out)


if __name__ == "__main__":
    sys.exit(main())
