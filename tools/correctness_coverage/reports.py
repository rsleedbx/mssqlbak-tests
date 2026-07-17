"""JSON history I/O: write edge reports, load latest run, assemble from disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _write_edge_json(
    reports_dir: Path,
    stem: str,
    run_id: str,
    edge: str,
    payload: dict[str, Any],
) -> None:
    """Write a tracked, timestamped edge JSON; never overwrites existing runs."""
    run_dir = reports_dir / stem / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / f"{stem}_{edge}.json"
    out.write_text(json.dumps(payload, default=str, indent=2))


def _load_latest_run(
    reports_dir: Path,
    stem: str,
    source_mode: str,
) -> dict[str, dict[str, Any]] | None:
    """Load all edge JSONs from the latest matching run for *stem*.

    Returns {edge_name: payload} or None if no runs exist.
    """
    stem_dir = reports_dir / stem
    if not stem_dir.is_dir():
        return None
    suffix = "_http" if source_mode == "http" else ""
    run_dirs = sorted(
        (d for d in stem_dir.iterdir() if d.is_dir() and d.name.endswith(suffix or "")),
        key=lambda d: d.name,
        reverse=True,
    )
    if not run_dirs:
        return None
    latest = run_dirs[0]
    edges: dict[str, dict[str, Any]] = {}
    for jf in latest.glob(f"{stem}_*.json"):
        edge_name = jf.stem[len(stem) + 1 :]
        try:
            edges[edge_name] = json.loads(jf.read_text())
        except Exception:
            pass
    return edges if edges else None


def _assemble_from_disk(
    reports_dir: Path,
    fixture_dir: Path,
    source_mode: str,
) -> list[dict[str, Any]]:
    """Reconstruct results from the latest on-disk JSON reports per bak stem."""
    results: list[dict[str, Any]] = []
    if not reports_dir.is_dir():
        return results
    for stem_dir in sorted(reports_dir.iterdir()):
        if not stem_dir.is_dir():
            continue
        stem = stem_dir.name
        edges = _load_latest_run(reports_dir, stem, source_mode)
        if not edges:
            continue
        # Reconstruct result from mssql_arrow edge (primary edge)
        primary = edges.get("mssql_arrow", next(iter(edges.values())))
        validations_payload = edges.pop("_validations", None)
        r: dict[str, Any] = {
            "bak": primary.get("bak", f"{stem}.bak"),
            "sql_version": primary.get("sql_version", ""),
            "bak_size_mb": primary.get("bak_size_mb", 0),
            "extract_s": primary.get("extract_s", 0),
            "total_src_rows": primary.get("total_src_rows", 0),
            "total_src_cols": primary.get("total_src_cols", 0),
            "run_id": primary.get("run_id", ""),
            "source_mode": primary.get("source_mode", source_mode),
            "tables": edges.get("mssql_arrow", {}).get("tables", []),
            "edges": {
                edge_name: {
                    "tables": payload.get("tables", []),
                    "write_s": payload.get("write_s"),
                    "readback_s": payload.get("readback_s"),
                }
                for edge_name, payload in edges.items()
            },
            "write_s": primary.get("write_s", {}),
            "readback_s": primary.get("readback_s", {}),
            "wall_s": None,
        }
        if validations_payload:
            r["validations"] = validations_payload.get("validations", {})
        results.append(r)
    return results
