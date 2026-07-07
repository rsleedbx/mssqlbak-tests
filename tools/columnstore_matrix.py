#!/usr/bin/env python3
"""Columnstore coverage matrix scoreboard.

Grades columnstore coverage on the 5 axes {data type x technique x organization x
distribution x version} and emits ``docs/columnstore_coverage_matrix.md``.

Placement (the SQLite-``permutations.test`` lesson — one declarative spec, not a
script per cell):

- **Declared targets** live in :data:`MATRIX_CELLS` (what SQL Server *can* produce,
  graded against the A1-A9 algorithm map), so an unbuilt feature shows as ``absent``,
  never silently missing. Legacy / Hekaton cells are ``out-of-scope``.
- **Observed fixtures** are discovered from ``tests/fixtures_<ver>/*.bak.segments.json``
  (ground truth) and, for ``cs__…`` convention names, reconciled against
  :func:`tools.fixture_name.parse_fixture_name` (declared intent). A filename-intent
  vs sidecar mismatch is itself a ``fail``.
- **Value grade**: when a ``<bak>.cells/`` sidecar exists, the decoder output is
  verified cell-by-cell via :mod:`tools.value_verify`. A fail-loud decode *raise* is
  caught per fixture and recorded as ``fail`` — it never aborts the whole run.

Results are persisted to a per-cell sqlite store (``--db``) so the Phase 4
matrix-cell loop can ``--status`` and ``--retest`` (re-run only failing cells),
mirroring SQLite's ``testrunner.db``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_name import parse_fixture_name

if TYPE_CHECKING:
    import pyarrow as pa

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSIONS = ("2017", "2019", "2022", "2025")
DEFAULT_DOC = REPO_ROOT / "docs" / "columnstore_coverage_matrix.md"
DEFAULT_DB = REPO_ROOT / "tests" / "fixtures" / "columnstore_matrix.db"

# Cell states (SSOT). Order = severity for the scoreboard headline.
ABSENT = "absent"
EXERCISED = "exercised"
PASS = "pass"
FAIL = "fail"
OUT_OF_SCOPE = "out-of-scope"

_ENC_DESC = {
    1: "enc1for",   # value / frame-of-reference
    2: "enc2bp",    # bit-packed
    3: "enc3dict",  # dictionary
    4: "enc4raw",   # raw 64-bit
    5: "enc5xpr",   # XPRESS / ARCHIVE
}


@dataclass(frozen=True)
class MatrixCell:
    """A declared target cell — what SQL Server can produce for this axis point.

    The five primary axes (org, enc, type, dist, versions) name the logical space.
    Qualifiers are sub-dimensions within a cell that describe *physically-distinct*
    cases where bugs actually live.  They are confirmed from ``segments.json``
    sidecars (``rowgroup_state``, ``bpv_target``, ``dict_scope``) and from the
    fixture name / backup envelope (``collation``, ``version_feature``,
    ``backup_envelope``).

    Qualifiers
    ----------
    rowgroup_state
        Expected ``sys.column_store_row_groups.state_desc`` enum seen in the sidecar.
        Comma-separated when multiple states are expected (e.g. ``"COMPRESSED"`` for
        a clean CCI, ``"COMPRESSED,TOMBSTONE"`` after a delete+rebuild, ``"OPEN"``
        for a delta store, ``""`` = don't-care).
    row_count_class
        Size class the fixture is designed to hit: ``"tiny"`` (<1 024 rows),
        ``"single_rg"`` (one full 1 048 576-row rowgroup), ``"multi_rg"`` (>1 RG),
        ``"boundary_32k"`` / ``"boundary_65k"`` (near the 32 768 / 65 537 bitpack
        sub-unit boundaries), ``""`` = don't-care.
    bpv_target
        Expected bit-packing width as a string like ``"12"`` (derived from distinct
        count *K* via ``ceil(log2 K)``), or ``""`` = don't-care.
    dict_scope
        For enc=3 cells: ``"primary"``, ``"secondary"``, ``"global"`` (shared across
        segments), ``"sorted-pool"``, ``"sort-key-only"``, or ``""`` = don't-care.
    collation
        For string/char types: ``"utf16"``, ``"varchar"``, ``"utf8"``, ``"mixed"``,
        ``"char_trailing_space"``, ``"non_bmp"``, ``"ci_ai"`` / ``"cs_as"``, or
        ``""`` = don't-care.
    version_feature
        Feature gating tag, e.g. ``"ordered_cci_2022"`` (ordered CCI requires
        SS2022+), ``"native_json_2025"``, ``"ncci_2016"``, ``"online_rebuild_2025"``,
        ``""`` = no version restriction beyond ``versions``.
    backup_envelope
        Backup-level qualifier applied to representative cells: ``"uncompressed"``,
        ``"compressed"``, ``"tde"``, ``"striped"``, ``"non_default_blocksize"``,
        ``""`` = default uncompressed.
    expected_dmv_signature
        A JSON-serialisable dict of expected fields from ``segments.json`` that the
        **generator acceptance gate** checks.  Empty dict means no gate (the cell is
        accepted as long as the fixture exists and parses).  Example::

            {"encodings": [2], "archive": False, "max_entry_count": {"lte": 4096}}

        Supported gate keys (all optional):

        * ``"encodings"``: list[int] — observed enc set must be a superset.
        * ``"archive"``: bool — ``ObservedFixture.archive`` must match.
        * ``"rowgroup_states"``: list[str] — observed states must be a superset.
        * ``"has_tombstones"``: bool.
        * ``"has_delete_bitmap"``: bool.
        * ``"max_entry_count"``: ``{"lte": N}`` — at least one dict entry_count ≤ N.
        * ``"bpv_observed"``: ``{"eq": N}`` — a segment with that bpv must appear.
    """

    org: str
    enc: str
    type: str  # noqa: A003
    dist: str
    versions: tuple[str, ...] = VERSIONS
    scope: str = "in"  # "in" or "out" (legacy / Hekaton → out-of-scope)
    note: str = ""
    # --- qualifiers (sub-dimensions) ---
    rowgroup_state: str = ""
    row_count_class: str = ""
    bpv_target: str = ""
    dict_scope: str = ""
    collation: str = ""
    version_feature: str = ""
    backup_envelope: str = ""
    expected_dmv_signature: dict[str, Any] = field(default_factory=dict)


# Declared target set (living; extend by data edit, never a new script). Seeded
# from the A1-A9 anchors + the naming-convention examples + version features. This
# is intentionally not exhaustive yet — generators (step 6) fill empty cells.
MATRIX_CELLS: list[MatrixCell] = [
    MatrixCell("cci", "enc1for", "multi", "mmbnd",
               note="A1 FOR base/magnitude at boundary",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"encodings": [1]}),
    MatrixCell("cci", "enc2int", "int32", "cycle",
               note="A2 bitpack width via distinct count",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"encodings": [2], "archive": False}),
    MatrixCell("cci", "enc3v4", "nvarchar", "cycle",
               note="A4 dict v4 string",
               rowgroup_state="COMPRESSED",
               dict_scope="primary",
               collation="utf16",
               expected_dmv_signature={"encodings": [3], "archive": False}),
    MatrixCell("cci", "enc5fa", "varbinarymax", "rand",
               note="A5 enc=5 XPRESS Format A",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"encodings": [5], "archive": False}),
    MatrixCell("cci", "arch", "multi", "rand",
               note="A5 ARCHIVE single XPRESS",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"archive": True}),
    MatrixCell("cciord", "enc1for", "bigint", "asc",
               versions=("2022", "2025"),
               note="A7 ordered CCI (SS2022+)",
               version_feature="ordered_cci_2022",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"encodings": [1]}),
    MatrixCell("delbmp", "enc1for", "multi", "runs",
               note="A8 delete bitmap",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"has_delete_bitmap": True}),
    MatrixCell("delta", "enc1for", "multi", "asc",
               note="A8 open delta store",
               rowgroup_state="OPEN",
               expected_dmv_signature={"rowgroup_states": ["OPEN"]}),
    MatrixCell("nccihp", "enc1for", "multi", "asc",
               note="A9 NCCI on heap",
               rowgroup_state="COMPRESSED",
               expected_dmv_signature={"encodings": [1]}),
    # Version-feature / legacy markers.
    MatrixCell("cci", "enc3v4", "native_json", "cycle",
               versions=("2025",),
               note="SS2025 native JSON type (244)",
               version_feature="native_json_2025",
               dict_scope="primary",
               expected_dmv_signature={"encodings": [3]}),
    MatrixCell("cci", "enc1for", "multi", "asc",
               versions=("2012", "2014", "2016"),
               scope="out",
               note="legacy read-only/updateable CCI — out of scope"),
]


@dataclass
class CellResult:
    """One graded (version, org, enc, type, dist) cell."""

    version: str
    org: str
    enc: str
    type: str  # noqa: A003
    dist: str
    state: str
    fixture: str = ""
    detail: str = ""
    # Qualifiers (from the matching MatrixCell, empty when no declared cell matches)
    rowgroup_state: str = ""
    row_count_class: str = ""
    bpv_target: str = ""
    dict_scope: str = ""
    collation: str = ""
    version_feature: str = ""
    backup_envelope: str = ""


@dataclass
class ObservedFixture:
    version: str
    bak_name: str
    stem: str
    intent: dict[str, Any] | None
    archive: bool
    encodings: set[int] = field(default_factory=set)
    dict_scopes: set[str] = field(default_factory=set)
    rowgroup_states: set[str] = field(default_factory=set)
    has_tombstones: bool = False
    has_delete_bitmap: bool = False
    dist_hint: str = "?"
    _sidecar: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


# ---------------------------------------------------------------------------
# Discovery + placement
# ---------------------------------------------------------------------------

def _dist_hint_from_segments(sidecar: dict[str, Any]) -> str:
    """Infer the data-distribution token from observed segment stats.

    low entry_count -> const/cycle; full-domain min/max spread -> mmbnd;
    has_nulls -> a null pattern was present. Best-effort, used only to colour the
    'which distribution was exercised' column when no cs__ intent is declared.
    """
    entry_counts: list[int] = []
    spreads: list[int] = []
    any_nulls = False
    for parts in sidecar.get("segments", {}).values():
        for segs in parts.values():
            for cols in segs.values():
                for col in cols:
                    if col.get("has_nulls"):
                        any_nulls = True
                    mn, mx = col.get("min_data_id"), col.get("max_data_id")
                    if isinstance(mn, int) and isinstance(mx, int):
                        spreads.append(mx - mn)
    for entries in sidecar.get("dictionaries", {}).values():
        for d in entries:
            if isinstance(d.get("entry_count"), int):
                entry_counts.append(d["entry_count"])
    hints = []
    if entry_counts and min(entry_counts) <= 1:
        hints.append("const")
    elif entry_counts and min(entry_counts) <= 4096:
        hints.append("cycle")
    if spreads and max(spreads) > 1_000_000:
        hints.append("mmbnd")
    if any_nulls:
        hints.append("+null")
    return "/".join(hints) if hints else "?"


def discover_fixtures(fixture_root: Path) -> list[ObservedFixture]:
    """Find every columnstore fixture with a .segments.json sidecar."""
    observed: list[ObservedFixture] = []
    for version in VERSIONS:
        vdir = fixture_root / f"fixtures_{version}"
        if not vdir.is_dir():
            continue
        for sidecar_path in sorted(vdir.glob("*.bak.segments.json")):
            sidecar = json.loads(sidecar_path.read_text())
            stem = sidecar_path.name.removesuffix(".bak.segments.json")
            parsed = parse_fixture_name(sidecar_path.name)
            intent = parsed if parsed.get("is_matrix") else None

            encodings: set[int] = set()
            archive = False
            for parts in sidecar.get("segments", {}).values():
                for segs in parts.values():
                    for cols in segs.values():
                        for col in cols:
                            if isinstance(col.get("encoding_type"), int):
                                encodings.add(col["encoding_type"])
                            if col.get("segment_version") not in (None, 1):
                                archive = True

            dict_scopes = {
                d.get("dict_scope", "?")
                for entries in sidecar.get("dictionaries", {}).values()
                for d in entries
            }
            states: set[str] = set()
            has_tomb = has_delbmp = False
            for t in sidecar.get("reconciliation", {}).values():
                states.update(t.get("state_counts", {}).keys())
                has_tomb = has_tomb or t.get("has_tombstones", False)
                has_delbmp = has_delbmp or t.get("has_delete_bitmap", False)

            observed.append(
                ObservedFixture(
                    version=version,
                    bak_name=stem + ".bak",
                    stem=stem,
                    intent=intent,
                    archive=archive,
                    encodings=encodings,
                    dict_scopes=dict_scopes,
                    rowgroup_states=states,
                    has_tombstones=has_tomb,
                    has_delete_bitmap=has_delbmp,
                    dist_hint=_dist_hint_from_segments(sidecar),
                    _sidecar=sidecar,
                )
            )
    return observed


# ---------------------------------------------------------------------------
# Value grading (offline cell verification of fixtures that have a .cells/ sidecar)
# ---------------------------------------------------------------------------

def grade_value(fixture_root: Path, version: str, stem: str) -> tuple[str, str] | None:
    """Return (state, detail) by verifying the decoder vs ground-truth cells.

    ``None`` when the fixture has no ``.cells/`` sidecar (so the cell is at best
    ``exercised``). A fail-loud decode raise is caught here and reported as a
    ``fail`` — the matrix run never aborts.
    """
    bak = fixture_root / f"fixtures_{version}" / f"{stem}.bak"
    cells_dir = bak.parent / (bak.name + ".cells")
    if not cells_dir.is_dir():
        return None

    import tempfile

    import deltalake

    from mssqlbak.extract import extract_bak_to_delta
    from tools.value_verify import load_manifest, verify_table

    try:
        manifest = load_manifest(cells_dir)
        with tempfile.TemporaryDirectory() as tmp:
            extract_bak_to_delta(str(bak), tmp)
            extracted: dict[str, pa.Table] = {}
            for sdir in Path(tmp).iterdir():
                if not sdir.is_dir():
                    continue
                for tdir in sdir.iterdir():
                    if tdir.is_dir():
                        extracted[f"{sdir.name}.{tdir.name}"] = deltalake.DeltaTable(
                            str(tdir)
                        ).to_pyarrow_table()
            bad: list[str] = []
            for entry in manifest.get("tables", []):
                ext = extracted.get(entry["fqn"])
                if ext is None:
                    bad.append(f"{entry['fqn']}: absent from decode")
                    continue
                res = verify_table(ext, cells_dir, entry)
                if not res.ok:
                    bad.append(f"{entry['fqn']}: {res.col_mismatches or res.digest_mismatches or res.error}")
    except Exception as exc:  # fail-loud decode raise → per-cell fail, never abort
        return FAIL, f"decode raised: {type(exc).__name__}: {exc}"

    if bad:
        return FAIL, "; ".join(bad)
    return PASS, "all cells match ground truth"


# Cell state precedence when several fixtures land in the same axis cell: a
# verified failure dominates, then a verified pass, then merely-exercised.
_STATE_RANK = {FAIL: 3, PASS: 2, EXERCISED: 1}


def build_results(fixture_root: Path, *, verify: bool) -> list[CellResult]:
    """Place declared + observed cells and grade them, one CellResult per axis cell.

    The matrix unit is the cell ``(version, org, enc, type, dist)``, not the
    fixture: multiple fixtures in one cell are merged (worst state wins, all
    contributing fixtures listed) so the scoreboard and the sqlite store agree.
    """
    observed = discover_fixtures(fixture_root)
    # axis key -> {"state", "fixtures": [...], "detail"}
    cells: dict[tuple[str, ...], dict[str, Any]] = {}

    for f in observed:
        # Axis tokens: prefer declared intent (cs__ name); else derive from sidecar.
        if f.intent is not None:
            org, enc, typ, dist = (f.intent["org"], f.intent["enc"], f.intent["type"], f.intent["dist"])
        else:
            enc_token = "arch" if f.archive else "/".join(
                _ENC_DESC.get(e, f"enc{e}") for e in sorted(f.encodings)
            ) or "enc?"
            org = "delbmp" if f.has_delete_bitmap else ("tomb" if f.has_tombstones else "cci")
            enc, typ, dist = enc_token, "multi", f.dist_hint

        state, detail = EXERCISED, f"segments seen (enc={sorted(f.encodings)}, archive={f.archive})"
        if verify:
            graded = grade_value(fixture_root, f.version, f.stem)
            if graded is not None:
                state, detail = graded
        # Filename-intent vs sidecar reconciliation: declared enc not observed → fail.
        if f.intent is not None and not _intent_matches(f, f.intent):
            state = FAIL
            detail = f"intent {f.intent} not confirmed by segments (enc={sorted(f.encodings)}, archive={f.archive})"

        # Generator acceptance gate: check DMV signature for cs__ fixtures that
        # match a declared MATRIX_CELLS entry.
        if f.intent is not None and state != FAIL:
            _gate_key = (f.version, org, enc, typ, dist)
            for cell_spec in MATRIX_CELLS:
                if cell_spec.scope == "out":
                    continue
                if f.version not in cell_spec.versions:
                    continue
                if (cell_spec.org, cell_spec.enc, cell_spec.type, cell_spec.dist) == (org, enc, typ, dist):
                    if cell_spec.expected_dmv_signature:
                        gate_ok, gate_reason = check_dmv_signature(
                            f, cell_spec.expected_dmv_signature, f._sidecar
                        )
                        if not gate_ok:
                            state = FAIL
                            detail = f"DMV signature mismatch: {gate_reason}"
                    break

        # Look up qualifiers from the matching declared cell spec.
        qualifiers: dict[str, str] = {}
        for cell_spec in MATRIX_CELLS:
            if cell_spec.scope == "out":
                continue
            if f.version not in cell_spec.versions:
                continue
            if (cell_spec.org, cell_spec.enc, cell_spec.type, cell_spec.dist) == (org, enc, typ, dist):
                qualifiers = {
                    "rowgroup_state": cell_spec.rowgroup_state,
                    "row_count_class": cell_spec.row_count_class,
                    "bpv_target": cell_spec.bpv_target,
                    "dict_scope": cell_spec.dict_scope,
                    "collation": cell_spec.collation,
                    "version_feature": cell_spec.version_feature,
                    "backup_envelope": cell_spec.backup_envelope,
                }
                break

        key = (f.version, org, enc, typ, dist)
        cell = cells.setdefault(key, {"state": state, "fixtures": [], "detail": detail, **qualifiers})
        cell["fixtures"].append(f.bak_name)
        if _STATE_RANK.get(state, 0) >= _STATE_RANK.get(cell["state"], 0):
            cell["state"] = state
            cell["detail"] = detail

    results: list[CellResult] = [
        CellResult(
            version=k[0], org=k[1], enc=k[2], type=k[3], dist=k[4],
            state=v["state"], fixture=", ".join(sorted(v["fixtures"])), detail=v["detail"],
            rowgroup_state=v.get("rowgroup_state", ""),
            row_count_class=v.get("row_count_class", ""),
            bpv_target=v.get("bpv_target", ""),
            dict_scope=v.get("dict_scope", ""),
            collation=v.get("collation", ""),
            version_feature=v.get("version_feature", ""),
            backup_envelope=v.get("backup_envelope", ""),
        )
        for k, v in cells.items()
    ]

    # Declared targets with no observed fixture → absent / out-of-scope.
    for cell_spec in MATRIX_CELLS:
        for version in cell_spec.versions:
            key = (version, cell_spec.org, cell_spec.enc, cell_spec.type, cell_spec.dist)
            if key in cells:
                continue
            state = OUT_OF_SCOPE if cell_spec.scope == "out" else ABSENT
            results.append(
                CellResult(
                    version, cell_spec.org, cell_spec.enc, cell_spec.type,
                    cell_spec.dist, state, "", cell_spec.note,
                    rowgroup_state=cell_spec.rowgroup_state,
                    row_count_class=cell_spec.row_count_class,
                    bpv_target=cell_spec.bpv_target,
                    dict_scope=cell_spec.dict_scope,
                    collation=cell_spec.collation,
                    version_feature=cell_spec.version_feature,
                    backup_envelope=cell_spec.backup_envelope,
                )
            )
            cells[key] = {"state": state, "fixtures": [], "detail": cell_spec.note}

    return results


def _intent_matches(f: ObservedFixture, intent: dict[str, Any]) -> bool:
    """Loose reconciliation: the declared enc token is consistent with observed."""
    enc = intent["enc"]
    if enc.startswith("arch"):
        return f.archive
    if enc.startswith("enc1"):
        return 1 in f.encodings
    if enc.startswith("enc2"):
        return 2 in f.encodings
    if enc.startswith("enc3"):
        return 3 in f.encodings
    if enc.startswith("enc4"):
        return 4 in f.encodings
    if enc.startswith("enc5"):
        return 5 in f.encodings
    return True


def check_dmv_signature(
    f: ObservedFixture,
    sig: dict[str, Any],
    sidecar: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    """Generator acceptance gate: check ``f`` against ``expected_dmv_signature`` *sig*.

    Returns ``(ok, reason)`` where *reason* is empty when *ok* is True.

    Supported gate keys
    -------------------
    ``"encodings"``
        ``list[int]`` — ``f.encodings`` must be a superset of this set.
    ``"archive"``
        ``bool`` — ``f.archive`` must equal this value.
    ``"rowgroup_states"``
        ``list[str]`` — ``f.rowgroup_states`` must be a superset of this set.
    ``"has_tombstones"``
        ``bool`` — ``f.has_tombstones`` must equal this value.
    ``"has_delete_bitmap"``
        ``bool`` — ``f.has_delete_bitmap`` must equal this value.
    ``"max_entry_count"``
        ``{"lte": N}`` — at least one dictionary ``entry_count`` in *sidecar*
        must be ≤ N.  Requires *sidecar*.
    ``"bpv_observed"``
        ``{"eq": N}`` — at least one segment in *sidecar* must have ``bpv`` == N.
        Requires *sidecar*.
    """
    if not sig:
        return True, ""

    reasons: list[str] = []

    if "encodings" in sig:
        required = set(sig["encodings"])
        if not required.issubset(f.encodings):
            reasons.append(f"encodings: need {sorted(required)}, got {sorted(f.encodings)}")

    if "archive" in sig:
        if f.archive != sig["archive"]:
            reasons.append(f"archive: need {sig['archive']}, got {f.archive}")

    if "rowgroup_states" in sig:
        required_states = set(sig["rowgroup_states"])
        if not required_states.issubset(f.rowgroup_states):
            reasons.append(
                f"rowgroup_states: need {sorted(required_states)}, "
                f"got {sorted(f.rowgroup_states)}"
            )

    if "has_tombstones" in sig:
        if f.has_tombstones != sig["has_tombstones"]:
            reasons.append(f"has_tombstones: need {sig['has_tombstones']}, got {f.has_tombstones}")

    if "has_delete_bitmap" in sig:
        if f.has_delete_bitmap != sig["has_delete_bitmap"]:
            reasons.append(
                f"has_delete_bitmap: need {sig['has_delete_bitmap']}, "
                f"got {f.has_delete_bitmap}"
            )

    if sidecar is not None:
        if "max_entry_count" in sig:
            lte = sig["max_entry_count"].get("lte")
            if lte is not None:
                counts = [
                    d.get("entry_count", float("inf"))
                    for entries in sidecar.get("dictionaries", {}).values()
                    for d in entries
                    if isinstance(d.get("entry_count"), int)
                ]
                if not any(c <= lte for c in counts):
                    reasons.append(
                        f"max_entry_count.lte={lte}: no dict with entry_count ≤ {lte} "
                        f"(observed: {sorted(counts)[:5]})"
                    )

        if "bpv_observed" in sig:
            eq = sig["bpv_observed"].get("eq")
            if eq is not None:
                bpvs = [
                    col.get("bpv")
                    for parts in sidecar.get("segments", {}).values()
                    for segs in parts.values()
                    for cols in segs.values()
                    for col in cols
                    if isinstance(col.get("bpv"), int)
                ]
                if eq not in bpvs:
                    reasons.append(
                        f"bpv_observed.eq={eq}: not found in segments "
                        f"(observed bpvs: {sorted(set(bpvs))[:10]})"
                    )

    ok = len(reasons) == 0
    return ok, "; ".join(reasons)


# ---------------------------------------------------------------------------
# Results store (sqlite — testrunner.db model)
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS cells (
    version TEXT, org TEXT, enc TEXT, type TEXT, dist TEXT,
    state TEXT, fixture TEXT, detail TEXT, updated_at TEXT,
    rowgroup_state TEXT DEFAULT '',
    row_count_class TEXT DEFAULT '',
    bpv_target TEXT DEFAULT '',
    dict_scope TEXT DEFAULT '',
    collation TEXT DEFAULT '',
    version_feature TEXT DEFAULT '',
    backup_envelope TEXT DEFAULT '',
    PRIMARY KEY (version, org, enc, type, dist)
);
"""

# Migration: add qualifier columns if the db was created with the old schema.
_MIGRATE = """
ALTER TABLE cells ADD COLUMN rowgroup_state TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN row_count_class TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN bpv_target TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN dict_scope TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN collation TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN version_feature TEXT DEFAULT '';
ALTER TABLE cells ADD COLUMN backup_envelope TEXT DEFAULT '';
"""


def write_store(db_path: Path, results: list[CellResult]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as con:
        con.executescript(_SCHEMA)
        # Best-effort migration for existing stores (ignore errors if column exists).
        for stmt in _MIGRATE.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    con.execute(stmt)
                except sqlite3.OperationalError:
                    pass
        con.executemany(
            "INSERT OR REPLACE INTO cells "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    r.version, r.org, r.enc, r.type, r.dist,
                    r.state, r.fixture, r.detail, now,
                    r.rowgroup_state, r.row_count_class, r.bpv_target,
                    r.dict_scope, r.collation, r.version_feature,
                    r.backup_envelope,
                )
                for r in results
            ],
        )


def load_failing(db_path: Path) -> list[tuple[str, str]]:
    """Return (version, fixture) pairs currently marked fail (for --retest)."""
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as con:
        con.executescript(_SCHEMA)
        rows = con.execute(
            "SELECT DISTINCT version, fixture FROM cells WHERE state = ? AND fixture != ''",
            (FAIL,),
        ).fetchall()
    return [(r[0], r[1]) for r in rows]


def store_status(db_path: Path) -> dict[str, int]:
    if not db_path.exists():
        return {}
    with sqlite3.connect(db_path) as con:
        con.executescript(_SCHEMA)
        rows = con.execute("SELECT state, COUNT(*) FROM cells GROUP BY state").fetchall()
    return {state: n for state, n in rows}


# ---------------------------------------------------------------------------
# Scoreboard rendering
# ---------------------------------------------------------------------------

_STATE_GLYPH = {PASS: "✓", FAIL: "✗", EXERCISED: "·", ABSENT: "—", OUT_OF_SCOPE: "○"}


def render_markdown(results: list[CellResult]) -> str:
    reachable = [r for r in results if r.state != OUT_OF_SCOPE]
    passing = [r for r in reachable if r.state == PASS]
    score = (len(passing) / len(reachable) * 100) if reachable else 0.0

    counts: dict[str, int] = {}
    for r in results:
        counts[r.state] = counts.get(r.state, 0) + 1

    lines: list[str] = [
        "# Columnstore coverage matrix",
        "",
        "Auto-generated by `tools/columnstore_matrix.py`. Do not edit by hand.",
        "",
        f"**Score: {len(passing)}/{len(reachable)} reachable cells passing "
        f"({score:.1f}%)** — `out-of-scope` excluded.",
        "",
        "Legend: ✓ pass · ✗ fail · `·` exercised (segments seen, no cell truth) · "
        "`—` absent · ○ out-of-scope.",
        "",
        "| state | count |",
        "|-------|------:|",
    ]
    for state in (PASS, FAIL, EXERCISED, ABSENT, OUT_OF_SCOPE):
        if state in counts:
            lines.append(f"| {_STATE_GLYPH[state]} {state} | {counts[state]} |")
    lines.append("")

    # Group by type, then nested bullets per (org x enc x dist x version).
    by_type: dict[str, list[CellResult]] = {}
    for r in results:
        by_type.setdefault(r.type, []).append(r)

    for typ in sorted(by_type):
        lines.append(f"## type = `{typ}`")
        lines.append("")
        for r in sorted(by_type[typ], key=lambda r: (r.org, r.enc, r.dist, r.version)):
            glyph = _STATE_GLYPH.get(r.state, "?")
            fixture = f" — `{r.fixture}`" if r.fixture else ""
            detail = f" — {r.detail}" if r.detail and r.state in (FAIL, OUT_OF_SCOPE) else ""
            # Qualifier annotations (only non-empty ones).
            q_parts = []
            if r.rowgroup_state:
                q_parts.append(f"rg={r.rowgroup_state}")
            if r.bpv_target:
                q_parts.append(f"bpv={r.bpv_target}")
            if r.dict_scope:
                q_parts.append(f"dict={r.dict_scope}")
            if r.collation:
                q_parts.append(f"coll={r.collation}")
            if r.version_feature:
                q_parts.append(f"feat={r.version_feature}")
            if r.backup_envelope:
                q_parts.append(f"env={r.backup_envelope}")
            qualifiers = f" `({', '.join(q_parts)})`" if q_parts else ""
            lines.append(
                f"- {glyph} `{r.org}` x `{r.enc}` x `{r.dist}` x SS{r.version} "
                f"[{r.state}]{qualifiers}{fixture}{detail}"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the columnstore coverage matrix scoreboard.")
    parser.add_argument("--fixture-root", type=Path, default=REPO_ROOT / "tests")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument(
        "--verify", action="store_true",
        help="run offline cell verification for fixtures with a .cells/ sidecar",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="print the per-state count from the results store and exit",
    )
    parser.add_argument(
        "--retest", action="store_true",
        help="list fixtures currently marked fail (for the Phase 4 re-run loop)",
    )
    args = parser.parse_args(argv)

    if args.status:
        status = store_status(args.db)
        if not status:
            print("no results store yet", file=sys.stderr)
            return 0
        for state, n in sorted(status.items()):
            print(f"{state:14s} {n}")
        return 0

    if args.retest:
        failing = load_failing(args.db)
        for version, fixture in failing:
            print(f"SS{version}\t{fixture}")
        print(f"==> {len(failing)} failing fixture(s)", file=sys.stderr)
        return 0

    results = build_results(args.fixture_root, verify=args.verify)
    write_store(args.db, results)
    md = render_markdown(results)
    args.doc.write_text(md)

    reachable = [r for r in results if r.state != OUT_OF_SCOPE]
    passing = [r for r in reachable if r.state == PASS]
    print(
        f"==> wrote {args.doc} | {len(results)} cells, "
        f"{len(passing)}/{len(reachable)} reachable passing",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
