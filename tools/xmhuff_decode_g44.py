"""Decode G44 blob 2001 using xmhuffman.decode_page.

Requires: xmhuffman installed (Python 3.10 wheel, e.g. in .venv_3_10)
Run:  .venv_3_10/bin/python tools/xmhuff_decode_g44.py
"""
from __future__ import annotations

import re
import struct
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ── Bypass mssqlbak/__init__.py (which pulls in deltalake/pyarrow) ────────────
# Inject a minimal stub so `from mssqlbak.X import Y` works without running
# the package-level __init__ imports.
_pkg = types.ModuleType("mssqlbak")
_pkg.__path__ = [str(REPO / "mssqlbak")]
_pkg.__package__ = "mssqlbak"
sys.modules["mssqlbak"] = _pkg
sys.path.insert(0, str(REPO))

from mssqlbak.columnstore import _collect_blobs, _deinterleave_column_lob  # noqa: E402
from mssqlbak.mtf import extract_mdf_pages  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
import xmhuffman  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
BAK_PATH  = REPO / "tests/fixtures_2022/cs_lob_preamble2.bak"
CSINDEX   = REPO / "tests/fixtures_2022/G44_csindex_output.txt"

N_HANDLES = 1200
RH_OFF    = 68          # byte offset of first record handle in deint buffer
RH_SZ     = 8           # bytes per record handle
CBUF_OFF  = 9832        # byte offset where bitstream starts in deint buffer
EA_OFF    = 9700        # byte offset of encode_array_128 in deint buffer
STB_OFF   = 9688        # byte offset of store_total_bits (u32) in deint buffer


def load_blob2001(bak: Path) -> bytes:
    img   = extract_mdf_pages(str(bak))
    store = PageStore(img)
    blobs = _collect_blobs(store)
    raw   = blobs.get(2001)
    if raw is None:
        raise RuntimeError("blob 2001 not found")
    return _deinterleave_column_lob(raw)


def load_csindex(path: Path) -> dict[int, str]:
    entries: dict[int, str] = {}
    for line in path.read_text().splitlines():
        m = re.match(r'^\s+(\d+)\s+([A-Za-z0-9]{78,82})\s*$', line)
        if m:
            entries[int(m.group(1))] = m.group(2)
    return entries


def run() -> None:
    print(f"Loading {BAK_PATH.name} …")
    deint = load_blob2001(BAK_PATH)
    print(f"  deinterleaved blob 2001: {len(deint):,} bytes")

    bit_offsets  = [struct.unpack_from("<I", deint, RH_OFF + k * RH_SZ)[0]
                    for k in range(N_HANDLES)]
    encode_array = deint[EA_OFF : EA_OFF + 128]
    bitstream    = deint[CBUF_OFF:]
    stb          = struct.unpack_from("<I", deint, STB_OFF)[0]

    print(f"  STB={stb}, bitstream={len(bitstream):,} B, ea128={encode_array[:4].hex()}…")

    print("Calling xmhuffman.decode_page …")
    results: list[bytes | None] = xmhuffman.decode_page(
        bitstream        = bitstream,
        encode_array_128 = encode_array,
        offsets          = bit_offsets,
        store_total_bits = stb,
        swap             = True,
    )
    print(f"  Returned {len(results)} items")

    # Show first 5
    for k in range(min(5, len(results))):
        r = results[k]
        print(f"  k={k}: {r!r}")

    # Validate against CSINDEX ground truth (k == data_id assumption)
    if not CSINDEX.exists():
        print("CSINDEX file not found — skipping validation")
        return

    csindex = load_csindex(CSINDEX)
    print(f"\nValidating against {len(csindex)} CSINDEX entries …")
    ok = miss = fail = 0
    bad: list[tuple[int, bytes | str | None, str | None]] = []
    for k, s in enumerate(results):
        exp = csindex.get(k)
        if s is None:
            fail += 1
            if len(bad) < 5:
                bad.append((k, None, exp))
        elif s == exp:
            ok += 1
        else:
            miss += 1
            if len(bad) < 5:
                bad.append((k, s, exp))

    print(f"  ok={ok}  miss={miss}  fail(None)={fail}  total={len(results)}")
    if bad:
        print("  First discrepancies:")
        for k, got, exp in bad:
            print(f"    k={k}: got={repr(got[:30] if got else got)!r}  "
                  f"exp={repr(exp[:30] if exp else exp)!r}")
    else:
        print("  All decoded strings match CSINDEX!")


if __name__ == "__main__":
    run()
