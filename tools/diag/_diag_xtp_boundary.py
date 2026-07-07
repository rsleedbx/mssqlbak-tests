#!/usr/bin/env -S /Users/robert.lee/github/mssqlbak/.venv/bin/python
"""Prototype boundary-aware checkpoint-chunk collector for XTP log records.

Model (empirical, DemoSalesOrderHeaderSeed):
  * 64 KB checkpoint chunks (byte0==0x01, byte1 not a page mtype) each begin with
    a self-describing preamble, then zero-fill, then a run of contiguous
    header-first records (stride = 20 + size) with occasional 8-byte container
    gaps that DO NOT lose records (seq stays contiguous).
  * The chunk's first data record has its 20-byte header clobbered by the
    preamble/zero-fill; only its payload survives, at [F-32, F) where F is the
    first valid header.  Its seq = seq(F) - 1, LB/marker = LB/marker(F).
  * A record whose header is near the chunk end and whose payload spills past the
    chunk boundary is straddle-garbage (its payload lands in the NEXT chunk's
    preamble); the real row is recovered by the next chunk's first-record salvage.
  * Log-tail (non-page, non-checkpoint) chunks are concatenated and walked as
    today (records may straddle these).

Validates DemoSalesOrderHeaderSeed to exactly {1..31465} byte-exact vs .cells.
"""
from __future__ import annotations

import datetime
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pyarrow.parquet as pq

from mssqlbak.catalog import recover_schema
from mssqlbak.compressed import (
    _HEADER_VERSION,
    _OFF_HEADER_VERSION,
    iter_decompressed_chunks,
)
from mssqlbak.pages import PageStore
from mssqlbak.xtp import _LOG_HEADER_SIZE, _decode_payload, _read_log_header

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak"
)
CELLS_DIR = (
    Path(__file__).parent.parent.parent
    / "tests" / "fixtures_realworld" / "AdventureWorks2016_EXT.bak.cells"
)
_U32 = struct.Struct("<I")
_VALID_MTYPE_MAX = 22
CKPT_CHUNK_LEN = 65536


def _is_page(ch: bytes) -> bool:
    return (len(ch) >= 96
            and ch[_OFF_HEADER_VERSION] == _HEADER_VERSION
            and 1 <= ch[1] <= _VALID_MTYPE_MAX)


def _is_checkpoint(ch: bytes) -> bool:
    # 64 KB data chunk whose first byte is 0x01 but is not a page.
    return len(ch) == CKPT_CHUNK_LEN and ch[0] == 0x01 and not _is_page(ch)


def _walk_run(seg: bytes, start: int, end: int):
    """Yield (lb, seq, marker, payload) for the contiguous record run beginning at
    *start*, resyncing across small container gaps, stopping at *end*.  A record
    whose payload would exceed *end* is skipped (straddle) and terminates the run."""
    walk = start
    while walk + _LOG_HEADER_SIZE <= end:
        hv = _read_log_header(seg, walk, end)
        if hv is None:
            # resync across an 8-byte container gap: probe next few 2-byte steps
            nxt = None
            for k in range(walk + 2, min(walk + 64, end), 2):
                if _read_log_header(seg, k, end) is not None:
                    nxt = k
                    break
            if nxt is None:
                return
            walk = nxt
            continue
        size, lb = hv
        marker = _U32.unpack_from(seg, walk + 12)[0]
        seq = _U32.unpack_from(seg, walk + 8)[0]
        payload = seg[walk + _LOG_HEADER_SIZE: walk + _LOG_HEADER_SIZE + size]
        yield lb, seq, marker, payload
        walk += _LOG_HEADER_SIZE + size


_PREAMBLE_MAGIC = b"\x01\x64\x01\x00"


def collect(raw: bytes):
    """Concatenated (strict-page) walk with marker-independent first-record salvage.

    Segments = runs of consecutive non-page chunks (checkpoint 64 KB chunks are
    NOT pages under the strict test, so they concatenate with their neighbours and
    records flow across contiguous chunk boundaries).  At every run start we
    salvage the 32-byte payload immediately before the first valid header as the
    clobbered first record (seq = firstseq-1), which recovers the row whose header
    was overwritten by a mid-stream preamble.  Records whose payload IS a preamble
    (a header→preamble straddle) are dropped.
    """
    recs: list[tuple[int, int, int, bytes]] = []
    segments: list[bytes] = []
    cur: list[bytes] = []
    for ch in iter_decompressed_chunks(raw):
        if _is_page(ch):
            if cur:
                segments.append(b"".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        segments.append(b"".join(cur))

    for seg in segments:
        n = len(seg)
        off = 0
        while off + _LOG_HEADER_SIZE <= n:
            if _read_log_header(seg, off, n) is None:
                off += 2
                continue
            # salvage clobbered first record before this run start, but ONLY when a
            # checkpoint preamble sits just before it (a real chunk boundary whose
            # first record's header was overwritten).  This avoids salvaging zero/
            # counter regions at unrelated resync points.
            hv0 = _read_log_header(seg, off, n)
            assert hv0 is not None
            _s0, lb0 = hv0
            mk0 = _U32.unpack_from(seg, off + 12)[0]
            seq0 = _U32.unpack_from(seg, off + 8)[0]
            if off >= 32:
                salv = seg[off - 32:off]
                near = seg[max(0, off - 1024):off]
                if salv[:4] != _PREAMBLE_MAGIC and _PREAMBLE_MAGIC in near:
                    recs.append((lb0, seq0 - 1, mk0, salv))
            chain = list(_walk_run(seg, off, n))
            if len(chain) >= 2:
                for lb, seq, mk, p in chain:
                    if p[:4] != _PREAMBLE_MAGIC:  # drop header→preamble straddle
                        recs.append((lb, seq, mk, p))
                total = sum(_LOG_HEADER_SIZE + len(p) for *_r, p in chain)
                off += total
            else:
                off += 2
    return recs


def _identity_col(table):
    for c in table.columns:
        if (c.identity_seed == 1 and c.identity_increment == 1
                and not c.is_variable and c.type_id in {48, 52, 56, 127}):
            return c
    return None


SKIPPED = [
    "Demo.DemoSalesOrderHeaderSeed",
    "Production.Product_inmem",
    "Sales.SalesOrderDetail_inmem",
    "Sales.SalesOrderHeader_inmem",
    "Sales.SpecialOfferProduct_inmem",
]


def main() -> None:
    store = PageStore.from_bak(FIXTURE)
    schema = recover_schema(store)
    raw = FIXTURE.read_bytes()
    recs = collect(raw)

    # group all records by (lb, marker)
    by_lbmk: dict[tuple[int, int], list[tuple[int, bytes]]] = {}
    for lb, seq, mk, p in recs:
        by_lbmk.setdefault((lb, mk), []).append((seq, p))
    print(f"total records: {len(recs)}; distinct (lb,marker): {len(by_lbmk)}")

    for tname in SKIPPED:
        short = tname.split(".", 1)[1]
        table = next((t for t in schema.tables if t.name == short), None)
        if table is None:
            print(f"\n{tname}: table not found")
            continue
        idc = _identity_col(table)
        if idc is None:
            print(f"\n{tname}: no IDENTITY(1,1) col")
            continue
        fw = sum(c.max_length for c in table.columns if not c.is_variable)
        # find best (lb,mk) group: the one whose decode yields the longest
        # gap-free identity prefix.
        best = None
        for (lb, mk), lst in by_lbmk.items():
            id_to_payloads: dict[int, set[bytes]] = {}
            for seq, p in lst:
                if len(p) < fw:
                    continue
                try:
                    row = _decode_payload(p, table, xtp_log_mode=True)
                except Exception:
                    continue
                v = row.get(idc.name)
                if isinstance(v, int) and v >= 1:
                    id_to_payloads.setdefault(v, set()).add(p)
            if not id_to_payloads:
                continue
            ids = set(id_to_payloads)
            N = 0
            while (N + 1) in ids:
                N += 1
            if best is None or N > best[0]:
                best = (N, lb, mk, ids, id_to_payloads)
        if best is None:
            print(f"\n{tname}: no candidate group")
            continue
        N, lb, mk, ids, id_to_payloads = best
        extras = sorted(ids - set(range(1, N + 1)))
        inconsistent = [i for i, ps in id_to_payloads.items() if len(ps) > 1]
        print(f"\n{tname}: idcol={idc.name} best lb=0x{lb:02x} mk=0x{mk:02x} "
              f"gap-free-prefix N={N} distinct-ids={len(ids)} "
              f"extras={len(extras)} (sample {extras[:3]}) "
              f"inconsistent-id-payloads={len(inconsistent)}")

    # byte-exact check for DemoSalesOrderHeaderSeed vs .cells
    table = next(t for t in schema.tables if t.name == "DemoSalesOrderHeaderSeed")
    idc = _identity_col(table)
    assert idc is not None
    fw = sum(c.max_length for c in table.columns if not c.is_variable)
    lst = by_lbmk.get((0x0d, 0x94), [])
    decoded_by_id: dict[int, dict] = {}
    for seq, p in lst:
        if len(p) < fw:
            continue
        row = _decode_payload(p, table, xtp_log_mode=True)
        v = row.get(idc.name)
        if isinstance(v, int) and 1 <= v <= 31465:
            decoded_by_id[v] = row
    gt = {int(r["LocalID"]): r for r in
          pq.read_table(CELLS_DIR / "Demo.DemoSalesOrderHeaderSeed.parquet").to_pylist()}
    mism = []
    for lid, grow in gt.items():
        drow = decoded_by_id.get(lid)
        if drow is None:
            mism.append((lid, "MISSING"))
            continue
        for col in ("CustomerID", "SalesPersonID", "BillToAddressID",
                    "ShipToAddressID", "ShipMethodID", "DueDate"):
            gv = grow[col]
            dv = drow.get(col)
            dv_s = dv.isoformat() if isinstance(dv, datetime.datetime) else str(dv)
            if gv is None:
                if dv is not None:
                    mism.append((lid, col, dv_s, "None"))
                    break
                continue
            if dv_s != str(gv):
                mism.append((lid, col, dv_s, gv))
                break
        if len(mism) > 8:
            break
    print(f"\nDemoSalesOrderHeaderSeed byte-exact vs .cells: mismatches={len(mism)} "
          f"{'BYTE-EXACT COMPLETE' if not mism else mism[:4]}")


if __name__ == "__main__":
    main()
