"""Offline refresh of float column digests in .cells/_manifest.json files.

Manifests become stale when the canonical form of float values changes.  Two
known causes:

  _FLOAT_SIG change  (e.g. 13 → 15 in commit 6c46393)
    The number of significant digits used in canon() changes, so digests
    captured at the old sig no longer match the extractor.

  _canon_float implementation change  (e.g. float `.15g` → Decimal repr `.15g`)
    Python's built-in float `g` format uses scientific notation for |v| < 1e-4,
    while the Decimal path avoids it for |v| >= 1e-6 (Decimal's threshold is
    1e-6, not 1e-4).  Manifests captured before the Decimal routing was
    introduced (commit 6c46393) use scientific notation for these tiny values;
    the current verifier uses decimal notation, causing digest mismatches for
    columns that contain tiny float values (e.g. GeneralHospital Surgical
    Resource Cost).

This script recomputes only the float-typed column digests from existing
data — no live SQL Server required — and rewrites the affected manifests.

Three cases are handled:

  ncci_types_full.bak   (mode=full, GT parquet present)
    The parquet already contains the SQL Server authoritative text strings.
    Passing those strings through canon(v, "float") at the current _FLOAT_SIG
    produces the same digest as running the extractor at the current sig.

  tabletype_cci_large_full.bak  (mode=digest-only, no parquet)
    No parquet exists.  The 3 non-null float values are extracted directly from
    the .bak via PageStore + read_table_rows and canonicalized at current sig.

  GeneralHospital.bak  (mode=digest-only, realworld fixture)
    211,233-row heap table extracted via extract_bak.  Only the manifest digest
    is refreshed here; re-run tools/cells_capture.py against a live SQL Server
    restore to also refresh the diagnostic parquet.

Usage:
    .venv/bin/python tools/refresh_float_digests.py
    .venv/bin/python tools/refresh_float_digests.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import pyarrow.parquet as pq

ROOT = pathlib.Path(__file__).parent.parent
FIXTURE_DIRS = [ROOT / f"tests/fixtures_{yr}" for yr in ("2017", "2019", "2022", "2025")]
REALWORLD_DIR = ROOT / "tests/fixtures_realworld"

# (bak_stem, table_fqn, column_name, source)
#   source="parquet"  → read GT parquet and re-canon the strings
#   source="bak"      → extract live from the .bak file
_TARGETS: list[tuple[str, str, str, str]] = [
    ("ncci_types_full.bak", "dbo.ncci_float", "val", "parquet"),
    ("tabletype_cci_large_full.bak", "dbo.tt_column", "c_float", "bak"),
]

# Realworld fixtures with float columns whose manifests may need refreshing.
# These are extracted via extract_bak (not read_table_rows) because the tables
# may be large or use advanced storage (columnstore, page compression, etc.).
# source is always "bak" for realworld fixtures.
_REALWORLD_TARGETS: list[tuple[str, str, str]] = [
    # GeneralHospital.bak: Surgical Resource Cost is a float column with tiny
    # values (|v| < 1e-4) whose canonical form changed when _canon_float was
    # updated to route through Decimal instead of format(float, '.15g').
    ("GeneralHospital.bak", "dbo.SurgicalCosts", "Surgical Resource Cost"),
]


def _recompute_from_parquet(
    cells_dir: pathlib.Path, fqn: str, col_name: str
) -> str:
    from tools.cell_canon import canon, column_digest

    parq_path = cells_dir / f"{fqn}.parquet"
    tbl = pq.read_table(parq_path)
    raw_vals = tbl.column(col_name).to_pylist()
    # float('nan') in parquet represents SQL NULL — treat as None for canon().
    norm_vals = [None if (isinstance(v, float) and math.isnan(v)) else v for v in raw_vals]
    canon_vals = [canon(v, "float") for v in norm_vals]
    return column_digest(canon_vals)


def _recompute_from_bak(
    bak_path: pathlib.Path, table_name: str, col_name: str
) -> str:
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows
    from tools.cell_canon import canon, column_digest

    store = PageStore.from_bak(str(bak_path))
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == table_name)
    rows = list(read_table_rows(store, table))
    vals = [r.get(col_name) for r in rows]
    canon_vals = [canon(v, "float") for v in vals]
    return column_digest(canon_vals)


def _recompute_from_bak_extract(
    bak_path: pathlib.Path, fqn: str, col_name: str
) -> str:
    """Recompute digest via full extract_bak (for large tables or complex storage)."""
    from mssqlbak.extract import extract_bak
    from mssqlbak.sink import InMemorySink
    from tools.cell_canon import canon, column_digest

    sink = InMemorySink()
    extract_bak(bak_path, sink)
    tbl = sink.to_arrow_table(fqn)
    vals = tbl.column(col_name).to_pylist()
    canon_vals = [canon(v, "float") for v in vals]
    return column_digest(canon_vals)


def _update_manifest(
    manifest_path: pathlib.Path,
    fqn: str,
    col_name: str,
    new_digest: str,
    *,
    dry_run: bool,
) -> tuple[str | None, str]:
    """Return (old_digest, new_digest).  old_digest is None if column not found."""
    data = json.loads(manifest_path.read_text())
    old_digest: str | None = None
    changed = False

    for table in data.get("tables", []):
        if table.get("fqn") != fqn:
            continue
        for col in table.get("columns", []):
            if col.get("name") != col_name:
                continue
            old_digest = col.get("digest")
            if old_digest != new_digest:
                col["digest"] = new_digest
                changed = True

    if changed and not dry_run:
        manifest_path.write_text(json.dumps(data, indent=2))

    return old_digest, new_digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing any files.",
    )
    args = parser.parse_args(argv)

    any_error = False

    for fixture_dir in FIXTURE_DIRS:
        if not fixture_dir.exists():
            continue
        yr = fixture_dir.name.replace("fixtures_", "")

        for bak_stem, fqn, col_name, source in _TARGETS:
            bak_path = fixture_dir / bak_stem
            cells_dir = fixture_dir / (bak_stem + ".cells")
            manifest_path = cells_dir / "_manifest.json"

            if not manifest_path.exists():
                print(f"[{yr}] SKIP  {bak_stem}: no manifest", file=sys.stderr)
                continue

            try:
                if source == "parquet":
                    new_digest = _recompute_from_parquet(cells_dir, fqn, col_name)
                else:
                    if not bak_path.exists():
                        print(
                            f"[{yr}] SKIP  {bak_stem}: .bak missing", file=sys.stderr
                        )
                        continue
                    table_name = fqn.split(".")[-1]
                    new_digest = _recompute_from_bak(bak_path, table_name, col_name)
            except Exception as exc:
                print(f"[{yr}] ERROR {bak_stem}.{fqn}.{col_name}: {exc}", file=sys.stderr)
                any_error = True
                continue

            old_digest, _ = _update_manifest(
                manifest_path, fqn, col_name, new_digest, dry_run=args.dry_run
            )

            if old_digest is None:
                print(f"[{yr}] WARN  {bak_stem}: column {fqn}.{col_name} not in manifest")
                continue

            if old_digest == new_digest:
                print(f"[{yr}] OK    {bak_stem} / {fqn}.{col_name}  (already correct)")
            else:
                tag = "DRY-RUN" if args.dry_run else "UPDATED"
                print(
                    f"[{yr}] {tag} {bak_stem} / {fqn}.{col_name}\n"
                    f"        old: {old_digest}\n"
                    f"        new: {new_digest}"
                )

    # Realworld fixtures — only one copy per bak, no version-tree loop.
    if REALWORLD_DIR.exists():
        for bak_stem, fqn, col_name in _REALWORLD_TARGETS:
            bak_path = REALWORLD_DIR / bak_stem
            cells_dir = REALWORLD_DIR / (bak_stem + ".cells")
            manifest_path = cells_dir / "_manifest.json"

            if not manifest_path.exists():
                print(f"[realworld] SKIP  {bak_stem}: no manifest", file=sys.stderr)
                continue

            try:
                if not bak_path.exists():
                    print(
                        f"[realworld] SKIP  {bak_stem}: .bak missing", file=sys.stderr
                    )
                    continue
                new_digest = _recompute_from_bak_extract(bak_path, fqn, col_name)
            except Exception as exc:
                print(
                    f"[realworld] ERROR {bak_stem}.{fqn}.{col_name}: {exc}",
                    file=sys.stderr,
                )
                any_error = True
                continue

            old_digest, _ = _update_manifest(
                manifest_path, fqn, col_name, new_digest, dry_run=args.dry_run
            )

            if old_digest is None:
                print(
                    f"[realworld] WARN  {bak_stem}: column {fqn}.{col_name} not in manifest"
                )
                continue

            if old_digest == new_digest:
                print(
                    f"[realworld] OK    {bak_stem} / {fqn}.{col_name}  (already correct)"
                )
            else:
                tag = "DRY-RUN" if args.dry_run else "UPDATED"
                print(
                    f"[realworld] {tag} {bak_stem} / {fqn}.{col_name}\n"
                    f"        old: {old_digest}\n"
                    f"        new: {new_digest}"
                )

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
