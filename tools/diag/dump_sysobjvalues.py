#!/usr/bin/env python3
"""Dump all sysobjvalues rows from a .bak fixture.

Shows valclass, objid, subobjid, valnum, value (hex), and imageval (hex + text
attempt) for every row — including non-valclass-1 rows that the reader currently
ignores.  Used to reverse-engineer the extended-property row layout.

Usage:
    .venv/bin/python tools/diag/dump_sysobjvalues.py
    .venv/bin/python tools/diag/dump_sysobjvalues.py --fixture tests/fixtures_2022/extended_properties_full.bak
    .venv/bin/python tools/diag/dump_sysobjvalues.py --valclass 6   # filter to one class
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import fixture, open_store, hexdump, REPO_ROOT  # noqa: E402

sys.path.insert(0, str(REPO_ROOT))

from mssqlbak.catalog.columns import _SYSOBJVALUES_COLS, _OBJID_SYSOBJVALUES  # noqa: E402
from mssqlbak.catalog.bootstrap import _bootstrap, _decode_table             # noqa: E402
from mssqlbak.catalog.lob import _follow_lob                                  # noqa: E402


_DEFAULT_FIXTURE = str(fixture("2022", "extended_properties_full.bak"))


def _u(v: object) -> int:
    if isinstance(v, (bytes, bytearray)):
        return int.from_bytes(v, "little")
    return int(v) if v is not None else 0


def _s(v: object) -> int:
    if isinstance(v, (bytes, bytearray)):
        return int.from_bytes(v, "little", signed=True)
    return int(v) if v is not None else 0


def _try_decode(data: bytes | None) -> str:
    if not data:
        return ""
    # Try UTF-16-LE (nvarchar)
    try:
        return repr(data.decode("utf-16-le"))
    except Exception:  # noqa: BLE001
        pass
    # Try Latin-1 (varchar/SQL text)
    try:
        t = data.decode("latin-1")
        if all(32 <= ord(c) < 127 or c in "\r\n\t" for c in t[:80]):
            return repr(t[:80])
    except Exception:  # noqa: BLE001
        pass
    return ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", default=_DEFAULT_FIXTURE,
                    help="path to .bak fixture (default: extended_properties_full.bak)")
    ap.add_argument("--valclass", type=int, default=None,
                    help="filter to a specific valclass (default: all)")
    ap.add_argument("--hex-limit", type=int, default=64,
                    help="max bytes to hex-dump per column (default: 64)")
    args = ap.parse_args()

    p = Path(args.fixture)
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.exists():
        sys.exit(f"fixture not found: {p}")

    store, _schema, _boot, _blobs = open_store(p)
    boot = _bootstrap(store)

    try:
        pg = boot.object_table_first_page(_OBJID_SYSOBJVALUES)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"cannot find sysobjvalues page: {exc}")

    try:
        rows = _decode_table(store, pg, _SYSOBJVALUES_COLS)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"cannot decode sysobjvalues table: {exc}")

    total = 0
    shown = 0
    for r in rows:
        total += 1
        vc = _u(r.get("valclass"))
        if args.valclass is not None and vc != args.valclass:
            continue
        shown += 1

        objid    = _s(r.get("objid"))
        subobjid = _s(r.get("subobjid"))
        valnum   = _s(r.get("valnum"))
        value    = r.get("value")
        imageval = r.get("imageval")

        # Attempt to follow LOB chains
        value_bytes: bytes = b""
        if value:
            try:
                value_bytes = _follow_lob(store, value)
            except Exception:  # noqa: BLE001
                value_bytes = bytes(value) if isinstance(value, (bytes, bytearray)) else b""

        imageval_bytes: bytes = b""
        if imageval:
            try:
                imageval_bytes = _follow_lob(store, imageval)
            except Exception:  # noqa: BLE001
                imageval_bytes = bytes(imageval) if isinstance(imageval, (bytes, bytearray)) else b""

        print(f"\n{'='*72}")
        print(f"  valclass={vc}  objid={objid}  subobjid={subobjid}  valnum={valnum}")
        print(f"  value ({len(value_bytes)} bytes): {value_bytes[:args.hex_limit].hex(' ')}  {_try_decode(value_bytes[:args.hex_limit])}")
        print(f"  imageval ({len(imageval_bytes)} bytes): {imageval_bytes[:args.hex_limit].hex(' ')}  {_try_decode(imageval_bytes[:args.hex_limit])}")

    print(f"\n{'='*72}")
    print(f"Total rows in sysobjvalues: {total}  Shown (valclass={args.valclass!r}): {shown}")


if __name__ == "__main__":
    main()
