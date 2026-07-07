from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.columnstore_matrix import (
    ABSENT,
    EXERCISED,
    FAIL,
    OUT_OF_SCOPE,
    PASS,
    CellResult,
    build_results,
    discover_fixtures,
    load_failing,
    render_markdown,
    store_status,
    write_store,
)


def _write_sidecar(vdir: Path, stem: str, *, encoding: int, archive: bool, deleted: int = 0) -> None:
    vdir.mkdir(parents=True, exist_ok=True)
    seg_version = -2147483647 if archive else 1
    sidecar = {
        "segments": {
            "t": {"partition_1": {"segment_0": [
                {"column_name": "val", "column_id": 1, "segment_version": seg_version,
                 "encoding_type": encoding, "row_count": 1000, "has_nulls": 0,
                 "null_value": None, "min_data_id": 0, "max_data_id": 999,
                 "on_disk_size": 4096, "base_id": 0, "magnitude": 1},
            ]}},
        },
        "dictionaries": {},
        "reconciliation": {
            "t": {"total_rows": 1000, "deleted_rows": deleted, "live_rows": 1000 - deleted,
                  "n_row_groups": 1, "state_counts": {"COMPRESSED": 1},
                  "tombstone_row_group_ids": [], "has_tombstones": False,
                  "has_delete_bitmap": deleted > 0},
        },
        "raw_segment_count": 1,
    }
    (vdir / f"{stem}.bak.segments.json").write_text(json.dumps(sidecar))


@pytest.mark.quick
def test_discover_places_legacy_fixture_from_segments(tmp_path: Path) -> None:
    _write_sidecar(tmp_path / "fixtures_2022", "cci_legacy_probe", encoding=1, archive=False)
    observed = discover_fixtures(tmp_path)
    assert len(observed) == 1
    f = observed[0]
    assert f.version == "2022"
    assert f.intent is None  # legacy ad-hoc name, not cs__
    assert 1 in f.encodings
    assert f.archive is False


@pytest.mark.quick
def test_archive_segment_version_detected(tmp_path: Path) -> None:
    _write_sidecar(tmp_path / "fixtures_2019", "archive_x", encoding=5, archive=True)
    f = discover_fixtures(tmp_path)[0]
    assert f.archive is True
    assert 5 in f.encodings


@pytest.mark.quick
def test_cs_name_intent_mismatch_is_fail(tmp_path: Path) -> None:
    # Declared enc3v4 (dictionary, encoding 3) but the sidecar only shows enc=1 → fail.
    _write_sidecar(tmp_path / "fixtures_2022", "cs__cci__enc3v4__nvarchar__cycle", encoding=1, archive=False)
    results = build_results(tmp_path, verify=False)
    placed = [r for r in results if r.fixture == "cs__cci__enc3v4__nvarchar__cycle.bak"]
    assert placed and placed[0].state == FAIL
    assert "not confirmed" in placed[0].detail


@pytest.mark.quick
def test_cs_name_intent_match_is_exercised(tmp_path: Path) -> None:
    _write_sidecar(tmp_path / "fixtures_2022", "cs__cci__enc1for__int32__asc", encoding=1, archive=False)
    results = build_results(tmp_path, verify=False)
    placed = [r for r in results if r.fixture == "cs__cci__enc1for__int32__asc.bak"]
    assert placed and placed[0].state == EXERCISED
    assert placed[0].type == "int32"


@pytest.mark.quick
def test_declared_targets_render_absent_and_out_of_scope(tmp_path: Path) -> None:
    # No fixtures at all → every declared in-scope cell is absent, legacy is out-of-scope.
    results = build_results(tmp_path, verify=False)
    states = {r.state for r in results}
    assert ABSENT in states
    assert OUT_OF_SCOPE in states


@pytest.mark.quick
def test_render_headline_score_excludes_out_of_scope() -> None:
    results = [
        CellResult("2022", "cci", "enc1for", "int", "asc", PASS),
        CellResult("2022", "cci", "enc1for", "int", "desc", FAIL),
        CellResult("2022", "cci", "enc1for", "int", "rand", ABSENT),
        CellResult("2016", "cci", "enc1for", "int", "asc", OUT_OF_SCOPE),
    ]
    md = render_markdown(results)
    # 1 pass of 3 reachable (out-of-scope excluded) = 33.3%.
    assert "1/3 reachable cells passing (33.3%)" in md
    assert "## type = `int`" in md


@pytest.mark.quick
def test_results_store_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "m.db"
    results = [
        CellResult("2022", "cci", "enc1for", "int", "asc", PASS, "a.bak"),
        CellResult("2022", "cci", "enc1for", "int", "desc", FAIL, "b.bak", "boom"),
    ]
    write_store(db, results)
    assert store_status(db) == {PASS: 1, FAIL: 1}
    assert load_failing(db) == [("2022", "b.bak")]
