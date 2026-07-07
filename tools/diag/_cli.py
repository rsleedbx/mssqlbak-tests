#!/usr/bin/env python3
"""Unified CLI for mssqlbak diagnostics.

Run any subcommand with --help for full options.

Examples::

    # show first 20 rows from a table
    python tools/diag/_cli.py rows archive_part_roundtrip --limit 20

    # list all column segments for a table
    python tools/diag/_cli.py segments archive_part_roundtrip

    # walk ARCHIVE XPRESS sub-blocks for col_id=3
    python tools/diag/_cli.py subblocks archive_part_roundtrip --col-id 3

    # hex-dump raw bytes for a specific blob
    python tools/diag/_cli.py blob-hex 2106 --limit 128

    # dump a .bak's transaction-log tail (ground truth via sys.fn_dump_dblog)
    python tools/diag/_cli.py dblog dirtycoverage_rich_update.bak \\
        --version 2022 --op LOP_MODIFY_ROW --images

    # row/cell-level diff of mssqlbak extraction vs SQL Server RESTORE (.cells)
    python tools/diag/_cli.py cells-diff dirtycoverage_rich_update.bak --all-versions

    # use a different fixture version / file
    python tools/diag/_cli.py rows cs_100 \\
        --version 2022 --fixture columnstore_minimal.bak
"""

from __future__ import annotations

import mmap as _mmap
import struct
import sys
from pathlib import Path
from typing import Annotated, Any

import typer

# Ensure tools/diag/ is on sys.path so _lib resolves from any working directory.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _lib import (  # noqa: E402
    NULL_SENTINEL,
    U16,
    compute_idx_start,
    decode_pool_entry,
    fixture,
    hexdump,
    iter_subblocks,
    open_store,
    segments_for_table,
    find_table,
)

app = typer.Typer(
    help="mssqlbak diagnostic CLI — inspect .bak fixture data.",
    no_args_is_help=True,
)

# ── Shared option types ───────────────────────────────────────────────────────
_VersionOpt = Annotated[
    str, typer.Option("--version", "-v", help="Fixture version: 2017|2019|2022|2025")
]
_FixtureOpt = Annotated[
    str, typer.Option("--fixture", "-f", help="Fixture filename inside fixtures_<version>/")
]
_ColIdOpt = Annotated[int, typer.Option("--col-id", "-c", help="Column ID (0 = all)")]
_LimitOpt = Annotated[int, typer.Option("--limit", "-n", help="Max rows/entries to show")]

_DEFAULT_BAK = "archive_columnstore_partition_full.bak"


def _resolve(version: str, name: str) -> Path:
    p = fixture(version, name)
    if not p.exists():
        typer.echo(f"Fixture not found: {p}", err=True)
        raise typer.Exit(1)
    return p


# ── rows ──────────────────────────────────────────────────────────────────────
@app.command()
def rows(
    table: Annotated[str, typer.Argument(help="Table name")],
    version: _VersionOpt = "2022",
    fixture_name: _FixtureOpt = _DEFAULT_BAK,
    limit: _LimitOpt = 15,
    col: Annotated[str, typer.Option("--col", help="Column to display (default: all)")] = "",
) -> None:
    """Show decoded rows from a table."""
    from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]

    p = _resolve(version, fixture_name)
    store, schema, _boot, _blobs = open_store(p)
    tbl = find_table(schema, table)
    if tbl is None:
        names = [t.name for t in schema.tables]  # type: ignore[union-attr]
        typer.echo(f"Table '{table}' not found.\nAvailable: {names}", err=True)
        raise typer.Exit(1)

    all_rows = list(read_table_rows(store, tbl, schema.obj_to_name))  # type: ignore[union-attr]
    typer.echo(f"Total rows: {len(all_rows)}")
    typer.echo(f"\nFirst {limit} rows:")
    for i, r in enumerate(all_rows[:limit]):
        if col:
            v = r.get(col)
            display = repr(v.rstrip()) if isinstance(v, str) else repr(v)
            typer.echo(f"  [{i}]: {col}={display}")
        else:
            typer.echo(f"  [{i}]: {r}")


# ── segments ──────────────────────────────────────────────────────────────────
@app.command()
def segments(
    table: Annotated[str, typer.Argument(help="Table name")],
    version: _VersionOpt = "2022",
    fixture_name: _FixtureOpt = _DEFAULT_BAK,
    col_id: _ColIdOpt = 0,
) -> None:
    """List column segments (enc type, n_rows, hobt, blob_id, XPRESS flag)."""
    from mssqlbak.columnstore import (  # type: ignore[attr-defined]
        _enc5_archive_has_compressed_subblocks,
        _unwrap_archive_blob,
    )

    p = _resolve(version, fixture_name)
    store, schema, boot, blobs = open_store(p)
    segs = segments_for_table(store, boot, schema, table)
    if not segs:
        typer.echo(f"No segments found for '{table}'.")
        return

    for seg in segs:
        if col_id and seg.col_id != col_id:  # type: ignore[union-attr]
            continue
        xpress_tag = ""
        if seg.enc_type == 5:  # type: ignore[union-attr]
            inner = _unwrap_archive_blob(blobs.get(seg.blob_id, b""))  # type: ignore[union-attr]
            xpress_tag = "  XPRESS" if _enc5_archive_has_compressed_subblocks(inner) else "  RAW"
        typer.echo(
            f"  col={seg.col_id:2d}  enc={seg.enc_type}  n_rows={seg.n_rows:6d}"  # type: ignore[union-attr]
            f"  hobt={seg.hobt_id}  blob={seg.blob_id}{xpress_tag}"  # type: ignore[union-attr]
        )


# ── rowgroups ───────────────────────────────────────────────────────────────
_CMPR_NAMES = {0: "NONE", 1: "ROW", 2: "PAGE", 3: "COLUMNSTORE", 4: "COLUMNSTORE_ARCHIVE"}


def _candidate_live_subsets(
    rg_rows: dict[int, int], target: int, *, max_results: int = 8
) -> list[tuple[int, ...]]:
    """Return up to *max_results* sorted seg_id subsets whose n_rows sum to *target*.

    Bounded subset-sum backtracking: identifies which row groups could be the
    live (non-tombstone) set when sum(n_rows) overshoots rcrows.  The live subset
    is ambiguous whenever more than one subset totals rcrows.
    """
    items = sorted(rg_rows.items())  # (seg_id, n_rows)
    results: list[tuple[int, ...]] = []

    def bt(i: int, remaining: int, chosen: list[int]) -> None:
        if len(results) >= max_results:
            return
        if remaining == 0 and chosen:
            results.append(tuple(chosen))
            return
        if i >= len(items) or remaining < 0:
            return
        sid, n = items[i]
        if n <= remaining:
            chosen.append(sid)
            bt(i + 1, remaining - n, chosen)
            chosen.pop()
        bt(i + 1, remaining, chosen)

    bt(0, target, [])
    return results


def _dmv_overlay(bak_path: Path, table: str) -> None:
    """Restore the .bak to the fixture container and dump the authoritative
    ``sys.column_store_row_groups`` state (COMPRESSED=3 / TOMBSTONE=4)."""
    import os

    typer.echo("\n=== live DMV overlay (sys.column_store_row_groups) ===")
    try:
        from tools.fixture_run import bootstrap_fixture_env
        from tools.register_bak import _drop_db, _restore_bak, _run_sql_query
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"--dmv: register_bak helpers unavailable: {exc}", err=True)
        return

    sql = (
        "SET NOCOUNT ON; "
        "SELECT rg.partition_number, rg.row_group_id, rg.state, "
        "CASE rg.state "
        "WHEN 0 THEN 'HIDDEN' "
        "WHEN 1 THEN 'OPEN' "
        "WHEN 2 THEN 'CLOSED' "
        "WHEN 3 THEN 'COMPRESSED' "
        "WHEN 4 THEN 'TOMBSTONE' "
        "ELSE CONCAT('STATE_', rg.state) END AS state_desc, "
        "rg.total_rows, rg.deleted_rows "
        "FROM sys.column_store_row_groups rg "
        "JOIN sys.tables t ON t.object_id = rg.object_id "
        f"WHERE t.name = '{table}' "
        "ORDER BY rg.partition_number, rg.row_group_id;"
    )
    db = f"DiagRowgroups_{bak_path.stem}"
    try:
        _server, container = bootstrap_fixture_env()
        password = os.environ["FIXTURE_DBA_PASSWORD"]
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"--dmv: cannot bootstrap fixture container: {exc}", err=True)
        typer.echo(
            "  Run manually once a container is configured:\n"
            f"    python -m tools.register_bak {bak_path} --keep --db-name Probe\n"
            "  then query sys.column_store_row_groups.",
            err=True,
        )
        return
    try:
        _restore_bak(container, password, bak_path, db)
        out = _run_sql_query(container, password, f"USE [{db}]; {sql}", sep="|")
        typer.echo(out.rstrip() or "  (no row groups returned)")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"--dmv: query failed: {exc}", err=True)
    finally:
        try:
            _drop_db(container, password, db)
        except Exception:  # noqa: BLE001
            pass


@app.command()
def rowgroups(
    table: Annotated[str, typer.Argument(help="Table name")],
    version: _VersionOpt = "2022",
    fixture_name: _FixtureOpt = _DEFAULT_BAK,
    dmv: Annotated[
        bool,
        typer.Option(
            "--dmv",
            help="Overlay live sys.column_store_row_groups state (restores the .bak"
            " to the configured fixture container).",
        ),
    ] = False,
) -> None:
    """Per-(hobt, seg_id) row-group metadata + tombstone reconciliation.

    For each row group: segment-record row count (n_rows), blob-derived row
    count, per-column encodings, and blob_ids.  Per partition (hobt) compares
    sum(n_rows) against the rowset rcrows to flag likely TOMBSTONE row groups
    (sum > rcrows) and lists candidate live subsets.  The live subset is
    ambiguous when several subsets total rcrows; use --dmv for ground truth.
    """
    from mssqlbak.columnstore import _n_rows_from_blob  # type: ignore[attr-defined]

    p = _resolve(version, fixture_name)
    store, schema, boot, blobs = open_store(p)
    if find_table(schema, table) is None:
        names = [t.name for t in schema.tables]  # type: ignore[union-attr]
        typer.echo(f"Table '{table}' not found.\nAvailable: {names}", err=True)
        raise typer.Exit(1)

    segs = segments_for_table(store, boot, schema, table)
    if not segs:
        typer.echo(f"No column-store segments found for '{table}'.")
        return

    by_hobt: dict[int, dict[int, list]] = {}
    for s in segs:
        by_hobt.setdefault(s.hobt_id, {}).setdefault(s.seg_id, []).append(s)

    for hobt in sorted(by_hobt):
        rgs = by_hobt[hobt]
        rcrows = boot.rowset_rcrows.get(hobt)
        cmpr = boot.rowset_compression.get(hobt)
        cmpr_name = _CMPR_NAMES.get(cmpr, str(cmpr))
        rc_str = f"{rcrows:,}" if rcrows is not None else "?"
        typer.echo(f"\npartition hobt={hobt}  cmprlevel={cmpr} ({cmpr_name})  rcrows={rc_str}")
        typer.echo(
            f"  {'seg_id':>6}  {'n_rows':>11}  {'blob_n_rows':>11}  "
            f"{'encs':<14}  {'cols':>4}  blob_ids"
        )

        rg_rows: dict[int, int] = {}
        for seg_id in sorted(rgs):
            cols = rgs[seg_id]
            nrows_vals = {c.n_rows for c in cols}
            nrows = max(nrows_vals)
            rg_rows[seg_id] = nrows
            blob_nrows = 0
            for c in cols:
                bn = _n_rows_from_blob(blobs.get(c.blob_id, b""))
                if bn:
                    blob_nrows = bn
                    break
            enc_counts: dict[int, int] = {}
            for c in cols:
                enc_counts[c.enc_type] = enc_counts.get(c.enc_type, 0) + 1
            enc_str = "{" + ",".join(f"{e}:{n}" for e, n in sorted(enc_counts.items())) + "}"
            blob_ids = [c.blob_id for c in cols]
            bid_str = ", ".join(str(b) for b in blob_ids[:6])
            if len(blob_ids) > 6:
                bid_str += f" …(+{len(blob_ids) - 6})"
            warn = "  ⚠ inconsistent n_rows across cols" if len(nrows_vals) > 1 else ""
            typer.echo(
                f"  {seg_id:>6}  {nrows:>11,}  {blob_nrows:>11,}  "
                f"{enc_str:<14}  {len(cols):>4}  [{bid_str}]{warn}"
            )

        total = sum(rg_rows.values())
        if rcrows is None:
            typer.echo(f"  sum(n_rows)={total:,}  (rcrows unavailable)")
            continue
        if total > rcrows:
            extra = total - rcrows
            typer.echo(
                f"  sum(n_rows)={total:,} > rcrows={rcrows:,}  →  {extra:,} extra rows"
                " (TOMBSTONE row groups likely present)"
            )
            cands = _candidate_live_subsets(rg_rows, rcrows)
            if cands:
                typer.echo(f"  candidate live subsets (sum == rcrows={rcrows:,}):")
                for subset in cands:
                    typer.echo(f"    seg_ids {{{','.join(str(s) for s in subset)}}}")
                if len(cands) >= 2:
                    typer.echo("    (ambiguous: multiple subsets total rcrows)")
            else:
                typer.echo(
                    "    (no exact subset totals rcrows — partial tombstone / delete-bitmap case?)"
                )
        elif total < rcrows:
            typer.echo(
                f"  sum(n_rows)={total:,} < rcrows={rcrows:,}  →  {rcrows - total:,}"
                " rows unaccounted (delta store / unread row groups?)"
            )
        else:
            typer.echo(f"  sum(n_rows)={total:,} == rcrows  (no tombstones)")

    if dmv:
        _dmv_overlay(p, table)


# ── subblocks ─────────────────────────────────────────────────────────────────
@app.command()
def subblocks(
    table: Annotated[str, typer.Argument(help="Table name")],
    version: _VersionOpt = "2022",
    fixture_name: _FixtureOpt = _DEFAULT_BAK,
    col_id: _ColIdOpt = 3,
    hobt: Annotated[
        int, typer.Option("--hobt", help="Restrict to this hobt_id (0 = first match)")
    ] = 0,
    col_width: Annotated[
        int, typer.Option("--col-width", help="Column byte width for pool decode")
    ] = 10,
    entries: Annotated[
        int, typer.Option("--entries", "-e", help="Index entries to print per block")
    ] = 5,
) -> None:
    """Walk XPRESS-compressed ARCHIVE sub-blocks: null counts + first index entries."""
    from mssqlbak.columnstore import (  # type: ignore[attr-defined]
        _enc5_archive_has_compressed_subblocks,
        _unwrap_archive_blob,
    )

    p = _resolve(version, fixture_name)
    store, schema, boot, blobs = open_store(p)
    segs = segments_for_table(store, boot, schema, table)

    shown = 0
    for seg in segs:
        if seg.col_id != col_id or seg.enc_type != 5:  # type: ignore[union-attr]
            continue
        if hobt and seg.hobt_id != hobt:  # type: ignore[union-attr]
            continue
        raw = blobs.get(seg.blob_id, b"")  # type: ignore[union-attr]
        inner = _unwrap_archive_blob(raw)
        if not _enc5_archive_has_compressed_subblocks(inner):
            continue

        typer.echo(f"\nhobt={seg.hobt_id}  n_rows={seg.n_rows}  blob={len(raw)}")  # type: ignore[union-attr]
        for bi, n_block, mk, pool_idx_b in iter_subblocks(inner):
            idx = compute_idx_start(pool_idx_b, n_block, col_width)
            index_region = pool_idx_b[idx : idx + n_block * 2]
            nulls = sum(
                1
                for i in range(0, len(index_region) - 1, 2)
                if U16.unpack_from(index_region, i)[0] == NULL_SENTINEL
            )
            typer.echo(
                f"  [{bi:2d}]  mk=0x{mk:04X}  n_block={n_block:5d}"
                f"  decomp={len(pool_idx_b):6d}  idx_start={idx:6d}  nulls={nulls}"
            )
            for j in range(min(entries, n_block)):
                off = idx + j * 2
                if off + 2 > len(pool_idx_b):
                    break
                v = U16.unpack_from(pool_idx_b, off)[0]
                decoded = decode_pool_entry(pool_idx_b, v, col_width, idx)
                typer.echo(f"         [{j:4d}]  pool_off=0x{v:04x}  →  {decoded!r}")

        shown += 1
        if not hobt:
            break  # default: first matching segment only

    if shown == 0:
        typer.echo(f"No XPRESS enc=5 segments found for '{table}' col_id={col_id}.")


# ── blob-hex ──────────────────────────────────────────────────────────────────
@app.command(name="blob-hex")
def blob_hex(
    blob_id: Annotated[int, typer.Argument(help="Blob ID to hex-dump")],
    version: _VersionOpt = "2022",
    fixture_name: _FixtureOpt = _DEFAULT_BAK,
    base: Annotated[int, typer.Option("--base", "-b", help="Start byte offset")] = 0,
    limit: _LimitOpt = 256,
) -> None:
    """Hex-dump raw bytes for a blob from the blob store."""
    p = _resolve(version, fixture_name)
    _store, _schema, _boot, blobs = open_store(p)
    raw = blobs.get(blob_id)
    if raw is None:
        typer.echo(f"Blob {blob_id} not found in {p.name}.", err=True)
        raise typer.Exit(1)
    typer.echo(f"Blob {blob_id}: {len(raw)} bytes total")
    hexdump(raw[base:], base=base, limit=limit)


# ── dblog ─────────────────────────────────────────────────────────────────────
@app.command()
def dblog(
    fixture_name: Annotated[str, typer.Argument(help="Fixture .bak filename")],
    version: _VersionOpt = "2022",
    op: Annotated[str, typer.Option("--op", help="Filter by Operation, e.g. LOP_MODIFY_ROW")] = "",
    page: Annotated[str, typer.Option("--page", help="Filter by Page ID, e.g. 0001:00000158")] = "",
    slot: Annotated[int, typer.Option("--slot", help="Filter by Slot ID (>=0)")] = -1,
    images: Annotated[
        bool, typer.Option("--images", help="Include before/after row images")
    ] = False,
    record: Annotated[
        bool, typer.Option("--record", help="Include full [Log Record] bytes")
    ] = False,
    census: Annotated[
        bool, typer.Option("--census", help="Show LOP census instead of records")
    ] = False,
    limit: _LimitOpt = 30,
) -> None:
    """Dump a .bak's transaction-log tail via sys.fn_dump_dblog (ground-truth log).

    Requires a running version-matched SQL Server container (forgedb). The .bak
    is copied in, read with fn_dump_dblog, then removed.
    """
    from _dblog import dump_dblog, inventory

    p = _resolve(version, fixture_name)
    if census:
        for o, c, n in inventory(p, version):
            typer.echo(f"  {n:>8}  {o:24} {c}")
        return
    recs = dump_dblog(
        p,
        version,
        op=op or None,
        page=page or None,
        slot=slot if slot >= 0 else None,
        images=images,
        record=record,
        limit=limit,
    )
    typer.echo(f"{len(recs)} records")
    for r in recs:
        typer.echo(f"  {r.lsn} {r.op:20} {r.ctx:18} len={r.length:>4} page={r.page} slot={r.slot}")
        if record and r.record is not None:
            typer.echo(f"      record={r.record.hex()}")
        if images and r.before is not None:
            typer.echo(f"      before={r.before.hex()}")
        if images and r.after is not None:
            typer.echo(f"      after ={r.after.hex()}")


# ── log-blocks / log-record-diff ──────────────────────────────────────────────
def _parse_page_id(page: str) -> int:
    """Parse a SQL Server page id like ``0001:00000158`` and return page number."""
    try:
        return int(page.split(":", 1)[1], 16)
    except (IndexError, ValueError) as exc:
        raise typer.BadParameter("page must look like 0001:00000158") from exc


def _log_block_size(data: bytes | _mmap.mmap, block_start: int) -> int:
    size = struct.unpack_from("<H", data, block_start + 6)[0]
    return size if size and size % 512 == 0 else 0


@app.command(name="log-blocks")
def log_blocks(
    fixture_name: Annotated[str, typer.Argument(help="Fixture .bak filename")],
    version: _VersionOpt = "2022",
    limit: _LimitOpt = 40,
) -> None:
    """List SQL Server log blocks, declared sizes, trailer ranges, and sector flags."""
    from mssqlbak import logtail as lt

    p = _resolve(version, fixture_name)
    with p.open("rb") as fh, _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ) as data:
        log_start, log_end = lt.find_log_range(data)
        typer.echo(f"log range: 0x{log_start:x}..0x{log_end:x} ({log_end - log_start:,} bytes)")
        shown = 0
        for block_start in range(log_start, log_end, lt._BLOCK_SIZE):
            if data[block_start] not in lt._OPEN_BLOCK_TYPES:
                continue
            size = _log_block_size(data, block_start)
            if size == 0:
                continue
            n_sectors = size // 512
            trailer_start = block_start + size - n_sectors
            flags = [f"{data[block_start + i * 512]:02x}" for i in range(n_sectors)]
            vlf = struct.unpack_from("<I", data, block_start + 0x0C)[0]
            blk_off = struct.unpack_from("<I", data, block_start + 0x10)[0]
            typer.echo(
                f"open_rel=0x{block_start - log_start:06x} type=0x{data[block_start]:02x} "
                f"size=0x{size:x} sectors={n_sectors:3d} vlf={vlf} blk_off={blk_off} "
                f"trailer_rel=0x{trailer_start - log_start:06x} flags={' '.join(flags[:16])}"
                + (" ..." if len(flags) > 16 else "")
            )
            shown += 1
            if shown >= limit:
                return


def _iter_raw_log_record_candidates(
    data: bytes | _mmap.mmap,
    log_start: int,
    log_end: int,
    page_id: int,
    slot_id: int,
) -> list[tuple[int, int]]:
    """Return ``(block_start, pos)`` candidates for a page/slot MODIFY record."""
    from mssqlbak import logtail as lt

    out: list[tuple[int, int]] = []
    for block_start in range(log_start, log_end, lt._BLOCK_SIZE):
        if data[block_start] not in lt._LOG_BLOCK_TYPES:
            continue
        for pos in range(0, lt._BLOCK_SIZE - lt._MIN_RECORD, lt._SCAN_STEP):
            try:
                if lt._xb_byte(data, block_start, pos, lt._OFF_LCX) != lt._LCX_XACT:
                    continue
                if lt._xb_byte(data, block_start, pos, lt._OFF_TX_TYPE) != lt._TX_MODIFY:
                    continue
                if lt._xb_uint32(data, block_start, pos, lt._OFF_PAGE_ID) != page_id:
                    continue
                if lt._xb_uint16(data, block_start, pos, lt._OFF_SLOT_ID) != slot_id:
                    continue
            except IndexError:
                continue
            out.append((block_start, pos))
    return out


@app.command(name="log-record-diff")
def log_record_diff(
    fixture_name: Annotated[str, typer.Argument(help="Fixture .bak filename")],
    version: _VersionOpt = "2022",
    page: Annotated[str, typer.Option("--page", help="Page ID, e.g. 0001:00000158")] = "",
    slot: Annotated[int, typer.Option("--slot", help="Slot ID (>=0)")] = -1,
    op: Annotated[str, typer.Option("--op", help="Operation filter")] = "LOP_MODIFY_ROW",
    limit: _LimitOpt = 4,
) -> None:
    """Diff SQL Server's reconstructed [Log Record] against raw .bak bytes."""
    from _dblog import dump_dblog
    from mssqlbak import logtail as lt

    if not page or slot < 0:
        typer.echo("log-record-diff requires --page and --slot", err=True)
        raise typer.Exit(1)

    p = _resolve(version, fixture_name)
    page_id = _parse_page_id(page)
    recs = dump_dblog(
        p, version, op=op, page=page, slot=slot, record=True, images=True, limit=limit
    )
    if not recs:
        typer.echo("No verifier records returned by fn_dump_dblog.")
        return

    with p.open("rb") as fh, _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ) as data:
        log_start, log_end = lt.find_log_range(data)
        candidates = _iter_raw_log_record_candidates(data, log_start, log_end, page_id, slot)
        typer.echo(f"raw candidates: {len(candidates)}")
        for rec in recs:
            if rec.record is None:
                continue
            typer.echo(
                f"\n{rec.lsn} {rec.op} {rec.ctx} len={len(rec.record)} page={rec.page} slot={rec.slot}"
            )
            for block_start, pos in candidates[:limit]:
                mismatches: list[tuple[int, int, int, int | None]] = []
                for i, want in enumerate(rec.record):
                    abs_pos = block_start + pos + i
                    if abs_pos >= len(data):
                        break
                    got = data[abs_pos]
                    if got == want:
                        continue
                    trailer = (
                        lt._log_block_sector_byte(data, abs_pos) if abs_pos % 512 == 0 else None
                    )
                    mismatches.append((i, got, want, trailer))
                typer.echo(
                    f"  candidate rel=0x{block_start - log_start:06x}+0x{pos:x} "
                    f"mismatches={len(mismatches)}"
                )
                for off, raw_b, sql_b, trailer in mismatches[:12]:
                    abs_pos = block_start + pos + off
                    trailer_s = f" trailer=0x{trailer:02x}" if trailer is not None else ""
                    typer.echo(
                        f"    +0x{off:04x} abs_rel=0x{abs_pos - log_start:06x} "
                        f"in_block=0x{(pos + off) % lt._BLOCK_SIZE:03x} "
                        f"mod512={(abs_pos % 512):3d} raw=0x{raw_b:02x} "
                        f"sql=0x{sql_b:02x}{trailer_s}"
                    )


# ── cells-diff ────────────────────────────────────────────────────────────────
def _patch_summary(patch: object) -> str:
    subpatches = getattr(patch, "patches", None)
    if subpatches is not None:
        return "patch-set[" + ", ".join(_patch_summary(p) for p in subpatches) + "]"
    row_start = getattr(patch, "row_start", "?")
    redo_data = getattr(patch, "redo_data", b"")
    undo_data = getattr(patch, "undo_data", b"")
    record_lsn = getattr(patch, "record_lsn", None)
    payload = redo_data if isinstance(redo_data, bytes) and redo_data else undo_data
    return f"row_start={row_start} len={len(payload) if isinstance(payload, bytes) else '?'} lsn={record_lsn}"


def _sample_key_tuple(key: Any) -> tuple[str | None, ...] | None:
    if isinstance(key, tuple):
        return tuple(None if v is None else str(v) for v in key)
    if isinstance(key, str):
        return (key,)
    return None


def _trace_cell_sample(bak: Path, fqn: str, key: Any) -> None:
    """Print physical row/patch context for a keyed cell-diff sample."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.logtail import logtail_from_bak
    from mssqlbak.pages import PageStore, page_lsn_tuple
    from mssqlbak.records import decode_record
    from mssqlbak.rows import _data_pages, _record_columns
    from mssqlbak.types import decode_value
    from tools.cell_canon import canon
    from tools import value_verify

    key_tuple = _sample_key_tuple(key)
    if key_tuple is None:
        typer.echo("      trace: sample has no row key")
        return
    cells_dir = value_verify.cells_dir_for(bak)
    manifest = value_verify.load_manifest(cells_dir)
    entry = next((e for e in manifest.get("tables", []) if e.get("fqn") == fqn), None)
    if entry is None:
        typer.echo("      trace: manifest entry not found")
        return
    key_cols: list[str] = entry.get("key_columns", []) or []
    if not key_cols:
        typer.echo("      trace: table has no key columns")
        return

    table_name = fqn.split(".", 1)[1] if "." in fqn else fqn
    store = PageStore.from_bak(bak)
    schema = recover_schema(store)
    table = find_table(schema, table_name)
    if table is None:
        typer.echo(f"      trace: table {table_name!r} not found in catalog")
        return
    sql_types = {c["name"]: c.get("sql_type", "") for c in entry.get("columns", [])}
    rec_cols = _record_columns(table)
    logtail = logtail_from_bak(bak)
    col_by_name = {c.name: c for c in table.columns}

    for pid, fid in _data_pages(store, table):
        page_obj = store.page(pid, fid)
        for slot_id in range(page_obj.header.slot_cnt):
            raw = page_obj.record(slot_id)
            try:
                decoded = decode_record(raw, rec_cols, {})
            except (ValueError, struct.error):
                continue
            typed = {
                name: decode_value(col_by_name[name], raw_cell)
                for name, raw_cell in decoded.items()
                if name in col_by_name
            }
            got_key = tuple(canon(typed.get(k), sql_types.get(k, "")) for k in key_cols)
            if got_key != key_tuple:
                continue
            phys = (fid, pid, slot_id)
            typer.echo(
                f"      trace: phys=(file={fid}, page={pid}, slot={slot_id}) "
                f"page_lsn={page_lsn_tuple(page_obj.header.lsn)}"
            )
            if phys in logtail.before_images:
                typer.echo(f"        before_image: {_patch_summary(logtail.before_images[phys])}")
            if phys in logtail.redo_patches:
                typer.echo(f"        redo_patch:   {_patch_summary(logtail.redo_patches[phys])}")
            if phys in logtail.redo_rows:
                typer.echo(f"        redo_row:     len={len(logtail.redo_rows[phys])}")
            if phys in logtail.committed_delete_slots:
                typer.echo("        committed_delete_slot: yes")
            return
    typer.echo(f"      trace: key={key_tuple!r} not found in rowstore page scan")


def _cells_diff_one(bak: Path, version: str, max_samples: int, trace: bool) -> bool:
    """Extract *bak* and print row/cell mismatches vs its .cells. Return True if any."""
    import tempfile

    import deltalake

    from mssqlbak.extract import extract_bak_to_delta
    from tools import value_verify
    from tools.known_gaps import gap_reason

    cells_dir = value_verify.cells_dir_for(bak)
    if not cells_dir.exists():
        typer.echo(f"[{version}] {bak.name}: no .cells sidecar — skipped", err=True)
        return False

    arrow_tables: dict[str, object] = {}
    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(bak), tmp)
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
                arrow_tables[f"{schema_dir.name}.{tbl_dir.name}"] = dt.to_pyarrow_table()

    results = value_verify.verify_bak(arrow_tables, cells_dir)
    try:
        year: int | None = int(version)
    except ValueError:
        year = None
    gap = gap_reason(bak.stem, year)
    any_bad = False
    for fqn, r in sorted(results.items()):
        if r.ok:
            continue
        any_bad = True
        tag = f"  [known gap: {gap}]" if gap else ""
        typer.echo(
            f"\n[{version}] {fqn}  mode={r.mode} cells_ok={r.cells_ok}/{r.cells_total} "
            f"col_mismatches={r.col_mismatches} digest={r.digest_mismatches} "
            f"missing_keys={r.missing_keys} error={r.error}{tag}"
        )
        for key, col, got, want in r.samples[:max_samples]:
            typer.echo(f"    key={key!r} col={col}\n      got ={got!r}\n      want={want!r}")
            if trace:
                _trace_cell_sample(bak, fqn, key)
    if not any_bad:
        typer.echo(f"[{version}] {bak.name}: ALL TABLES OK")
    return any_bad


@app.command(name="cells-diff")
def cells_diff(
    fixture_name: Annotated[str, typer.Argument(help="Fixture .bak filename")],
    version: _VersionOpt = "2022",
    all_versions: Annotated[
        bool, typer.Option("--all-versions", help="Check 2017/2019/2022/2025")
    ] = False,
    samples: Annotated[
        int, typer.Option("--samples", help="Max per-table sample diffs to show")
    ] = 8,
    trace: Annotated[
        bool, typer.Option("--trace", help="Trace sample keys to physical row/patch context")
    ] = False,
) -> None:
    """Row/cell-level diff of mssqlbak extraction vs SQL Server RESTORE (.cells).

    Unlike the column-digest pass/fail in value_verify, this prints the specific
    mismatching cells (got vs want) and annotates known gaps.
    """
    versions = ["2017", "2019", "2022", "2025"] if all_versions else [version]
    seen = False
    for v in versions:
        p = fixture(v, fixture_name)
        if not p.exists():
            if not all_versions:
                typer.echo(f"Fixture not found: {p}", err=True)
                raise typer.Exit(1)
            continue
        seen = True
        _cells_diff_one(p, v, samples, trace)
    if not seen:
        typer.echo(f"No fixture '{fixture_name}' found in any version.", err=True)
        raise typer.Exit(1)


@app.command()
def census(
    version: _VersionOpt = "2022",
    fixture_name: Annotated[
        str,
        typer.Option(
            "--fixture",
            "-f",
            help="Fixture .bak filename (default: all .bak in fixtures_<version>/)",
        ),
    ] = "",
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Write JSON to this path (default: print to stdout)"),
    ] = "",
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress progress lines")] = False,
) -> None:
    """Snapshot decode-path branch tags per (fixture, table) for regression detection.

    Requires MSSQLBAK_DECODE_TRACE=1 to be set in the calling environment, or
    sets it internally for child processes if not already active.  Each heuristic
    decision point in the decoders records a stable tag string; this command
    harvests those tags per table and emits a deterministic JSON that can be
    checked in as a census baseline.

    Run after any change to a decoder heuristic to confirm which (fixture, table)
    pairs changed code paths — before recomputing column digests.

    Example::

        MSSQLBAK_DECODE_TRACE=1 python tools/diag/_cli.py census --version 2022 \\
            --fixture columnstore_minimal.bak --output tests/census_baseline.json
    """
    import json
    import os
    import sys

    # Enable tracing for this process if not already active.
    os.environ.setdefault("MSSQLBAK_DECODE_TRACE", "1")

    # Import trace *after* setting the env flag so _ACTIVE is correctly set.
    # Because decode_trace._ACTIVE is computed at module import time we need to
    # reload it if it was already imported with the flag off.
    if "mssqlbak.decode_trace" in sys.modules:
        import importlib
        dt_mod = importlib.reload(sys.modules["mssqlbak.decode_trace"])
    else:
        import mssqlbak.decode_trace as dt_mod  # type: ignore[assignment]

    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    # Collect target .bak files.
    fixture_dir = _HERE.parent.parent / "tests" / f"fixtures_{version}"
    if fixture_name:
        baks = [fixture_dir / fixture_name]
    else:
        baks = sorted(fixture_dir.glob("*.bak"))

    result: dict[str, dict[str, list[str]]] = {}

    for bak in baks:
        if not bak.exists():
            typer.echo(f"[skip] {bak.name} not found", err=True)
            continue
        key = f"fixtures_{version}/{bak.name}"
        if not quiet:
            typer.echo(f"  {bak.name} ...", err=True)
        try:
            store = PageStore.from_bak(bak)
            schema = recover_schema(store)
        except Exception as exc:
            typer.echo(f"  [error] {bak.name}: {exc}", err=True)
            result[key] = {"_error": [str(exc)]}
            continue

        tbl_tags: dict[str, list[str]] = {}
        for tbl in schema.tables or []:
            dt_mod.reset()
            try:
                for _ in read_table_rows(store, tbl, schema.obj_to_name or {}):
                    pass
            except Exception as exc:
                tbl_tags[tbl.name] = [f"_error:{exc}"]
                continue
            raw = dt_mod.get_and_reset()
            # Store sorted unique set so the JSON is stable across runs.
            unique = sorted(set(raw))
            if unique:
                tbl_tags[tbl.name] = unique
        result[key] = tbl_tags

    payload = json.dumps(result, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(payload)
        if not quiet:
            typer.echo(f"Census written to {output}")
    else:
        typer.echo(payload)


if __name__ == "__main__":
    app()
