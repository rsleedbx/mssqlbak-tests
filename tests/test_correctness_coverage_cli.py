from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
import time
from typing import Any

from tools import correctness_coverage


def test_select_cases_can_target_one_bak(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures_realworld"
    fixture_dir.mkdir()
    selected = fixture_dir / "FailingSample.bak"
    skipped = fixture_dir / "OtherSample.bak"
    selected.write_bytes(b"bak")
    skipped.write_bytes(b"bak")
    (fixture_dir / "FailingSample.bak.stats.json").write_text("{}")
    (fixture_dir / "OtherSample.bak.stats.json").write_text("{}")

    cases = correctness_coverage._select_cases(fixture_dir, selected)

    assert cases == [(selected, fixture_dir / "FailingSample.bak.stats.json")]


def test_select_cases_can_target_multiple_baks(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures_realworld"
    fixture_dir.mkdir()
    first = fixture_dir / "FailingSample.bak"
    second = fixture_dir / "OtherSample.bak"
    skipped = fixture_dir / "SkippedSample.bak"
    first.write_bytes(b"bak")
    second.write_bytes(b"bak")
    skipped.write_bytes(b"bak")
    (fixture_dir / "FailingSample.bak.stats.json").write_text("{}")
    (fixture_dir / "OtherSample.bak.stats.json").write_text("{}")
    (fixture_dir / "SkippedSample.bak.stats.json").write_text("{}")

    cases = correctness_coverage._select_cases(fixture_dir, [first, second])

    assert cases == [
        (first, fixture_dir / "FailingSample.bak.stats.json"),
        (second, fixture_dir / "OtherSample.bak.stats.json"),
    ]


def test_select_cases_allows_confidence_fallback_for_each_selected_bak(
    tmp_path: Path,
) -> None:
    fixture_dir = tmp_path / "fixtures_realworld"
    fixture_dir.mkdir()
    first = fixture_dir / "GoodSample.bak"
    second = fixture_dir / "MissingStats.bak"
    first.write_bytes(b"bak")
    second.write_bytes(b"bak")
    (fixture_dir / "GoodSample.bak.stats.json").write_text("{}")

    cases = correctness_coverage._select_cases(fixture_dir, [first, second])

    assert cases == [
        (first, fixture_dir / "GoodSample.bak.stats.json"),
        (second, None),
    ]


def test_select_cases_allows_confidence_fallback_for_single_bak(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures_realworld"
    fixture_dir.mkdir()
    selected = fixture_dir / "MissingStats.bak"
    selected.write_bytes(b"bak")

    assert correctness_coverage._select_cases(fixture_dir, selected) == [(selected, None)]


def test_render_shows_confidence_only_result() -> None:
    md = correctness_coverage._render(
        [
            {
                "bak": "NoVerifier.bak",
                "sql_version": "",
                "bak_size_mb": 0,
                "extract_s": 0,
                "tables": [],
                "total_src_rows": 0,
                "total_src_cols": 0,
                "confidence": {
                    "status": "warn",
                    "checks": [
                        {
                            "name": "backup_set_selection",
                            "severity": "warn",
                            "message": "multiple backup sets",
                            "table": None,
                        }
                    ],
                },
            }
        ],
        show_fixture_dir=False,
    )

    assert "confidence warn" in md
    assert "backup_set_selection: multiple backup sets" in md


def test_run_cases_preserves_input_order_with_threads(
    monkeypatch,
    tmp_path: Path,
) -> None:
    slow = tmp_path / "Slow.bak"
    fast = tmp_path / "Fast.bak"
    cases: list[tuple[Path, Path | None]] = [
        (slow, tmp_path / "Slow.bak.stats.json"),
        (fast, tmp_path / "Fast.bak.stats.json"),
    ]

    def fake_run_case(bak_path: Path, stats_path: Path | None) -> dict[str, Any]:
        if bak_path == slow:
            time.sleep(0.05)
        return {"bak": bak_path.name, "stats": stats_path.name if stats_path else None}

    monkeypatch.setattr(correctness_coverage, "ProcessPoolExecutor", ThreadPoolExecutor, raising=False)
    monkeypatch.setattr(correctness_coverage, "_run_case", fake_run_case)

    results = correctness_coverage._run_cases(cases, threads=2)

    assert [r["bak"] for r in results] == ["Slow.bak", "Fast.bak"]


def test_run_cases_uses_parallel_workers(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cases: list[tuple[Path, Path | None]] = [
        (tmp_path / "A.bak", tmp_path / "A.bak.stats.json"),
        (tmp_path / "B.bak", tmp_path / "B.bak.stats.json"),
    ]
    lock = threading.Lock()
    active = 0
    max_active = 0

    def fake_run_case(bak_path: Path, stats_path: Path | None) -> dict[str, Any]:
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.05)
        with lock:
            active -= 1
        return {"bak": bak_path.name}

    monkeypatch.setattr(correctness_coverage, "ProcessPoolExecutor", ThreadPoolExecutor, raising=False)
    monkeypatch.setattr(correctness_coverage, "_run_case", fake_run_case)

    correctness_coverage._run_cases(cases, threads=2)

    assert max_active == 2


def test_render_timing_table_uses_wall_time() -> None:
    md = correctness_coverage._render(
        [
            {
                "bak": "Sample.bak",
                "sql_version": "",
                "bak_size_mb": 0,
                "extract_s": 9.876,
                "wall_s": 1.234,
                "tables": [],
                "total_src_rows": 0,
                "total_src_cols": 0,
            }
        ],
        show_fixture_dir=False,
    )

    assert "| Backup | Wall time |" in md
    assert "| `Sample.bak` | 1.234s |" in md
    assert "9.876s" not in md


def test_render_shows_table_and_column_pass_totals() -> None:
    md = correctness_coverage._render(
        [
            {
                "bak": "Mixed.bak",
                "sql_version": "",
                "bak_size_mb": 0,
                "extract_s": 0,
                "wall_s": 0,
                "total_src_rows": 2,
                "total_src_cols": 3,
                "tables": [
                    {
                        "fqn": "dbo.good",
                        "expected_rows": 1,
                        "row_ok": True,
                        "missing": False,
                        "xtp_skip": False,
                        "null_ok": 1,
                        "null_total": 1,
                        "minmax_ok": 2,
                        "minmax_total": 2,
                        "n_gt_cols": 1,
                        "col_count_ok": True,
                        "column_ok": 1,
                        "column_total": 1,
                    },
                    {
                        "fqn": "dbo.bad",
                        "expected_rows": 1,
                        "row_ok": True,
                        "missing": False,
                        "xtp_skip": False,
                        "null_ok": 1,
                        "null_total": 2,
                        "minmax_ok": 1,
                        "minmax_total": 2,
                        "n_gt_cols": 2,
                        "col_count_ok": True,
                        "column_ok": 1,
                        "column_total": 2,
                    },
                ],
            }
        ],
        show_fixture_dir=False,
    )

    assert "**Tables:** 1/2 pass · **Columns:** 2/3 pass" in md


def test_run_one_marks_expected_skipped_tables_without_bad_columns(
    monkeypatch,
    tmp_path: Path,
) -> None:
    bak = tmp_path / "AdventureWorks2016_EXT.bak"
    stats = tmp_path / "AdventureWorks2016_EXT.bak.stats.json"
    bak.write_bytes(b"bak")
    stats.write_text(
        """
        {
          "sql_version": "test",
          "bak_size_mb": 1,
          "tables": [
            {
              "schema": "Sales",
              "name": "SalesOrderHeader_inmem",
              "row_count": 31465,
              "columns": [
                {"name": "SalesOrderID", "sql_type": "int", "null_count": 0}
              ]
            }
          ]
        }
        """
    )

    def fake_extract(_bak_input: Path, _sink: Any) -> None:
        return None

    monkeypatch.setattr(correctness_coverage, "extract_bak", fake_extract)
    # AdventureWorks2016_EXT's XTP tables now land byte-exact, so the shared
    # KNOWN_SKIPPED_TABLES registry is empty.  Monkeypatch the lookup so this
    # test exercises the xtp_skip marking mechanism itself (a genuinely
    # missing, expected-skipped table must not count as a bad column).
    monkeypatch.setattr(
        correctness_coverage,
        "expected_skipped_tables",
        lambda _stem: frozenset({"Sales.SalesOrderHeader_inmem"}),
    )

    result = correctness_coverage._run_one(bak, stats)

    table = result["tables"][0]
    assert table["xtp_skip"] is True
    assert table["column_ok"] == 1
    assert correctness_coverage._table_ok(table)


def test_run_cases_logs_backups_when_processing(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    cases: list[tuple[Path, Path | None]] = [
        (tmp_path / "A.bak", tmp_path / "A.bak.stats.json"),
        (tmp_path / "B.bak", tmp_path / "B.bak.stats.json"),
    ]

    def fake_run_case(bak_path: Path, stats_path: Path | None) -> dict[str, Any]:
        return {"bak": bak_path.name}

    monkeypatch.setattr(correctness_coverage, "ProcessPoolExecutor", ThreadPoolExecutor, raising=False)
    monkeypatch.setattr(correctness_coverage, "_run_case", fake_run_case)

    correctness_coverage._run_cases(cases, threads=2)

    err = capsys.readouterr().err
    assert "processing A.bak" in err
    assert "processing B.bak" in err


def test_run_cases_does_not_log_queued_backups_as_processing(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    cases: list[tuple[Path, Path | None]] = [
        (tmp_path / "A.bak", tmp_path / "A.bak.stats.json"),
        (tmp_path / "B.bak", tmp_path / "B.bak.stats.json"),
        (tmp_path / "C.bak", tmp_path / "C.bak.stats.json"),
    ]
    started = 0
    lock = threading.Lock()
    two_started = threading.Event()
    release = threading.Event()

    def fake_run_case(bak_path: Path, stats_path: Path | None) -> dict[str, Any]:
        nonlocal started
        with lock:
            started += 1
            if started == 2:
                two_started.set()
        release.wait(timeout=2)
        return {"bak": bak_path.name}

    monkeypatch.setattr(correctness_coverage, "ProcessPoolExecutor", ThreadPoolExecutor, raising=False)
    monkeypatch.setattr(correctness_coverage, "_run_case", fake_run_case)

    runner = threading.Thread(
        target=correctness_coverage._run_cases,
        args=(cases,),
        kwargs={"threads": 2},
    )
    runner.start()
    try:
        assert two_started.wait(timeout=2)
        time.sleep(0.05)
        err = capsys.readouterr().err
        assert "processing A.bak" in err
        assert "processing B.bak" in err
        assert "processing C.bak" not in err
    finally:
        release.set()
        runner.join(timeout=2)


def test_run_cases_uses_process_pool_for_parallel_workers(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cases: list[tuple[Path, Path | None]] = [
        (tmp_path / "A.bak", tmp_path / "A.bak.stats.json"),
        (tmp_path / "B.bak", tmp_path / "B.bak.stats.json"),
    ]
    seen: dict[str, int] = {}

    class SpyProcessPool(ThreadPoolExecutor):
        def __init__(self, max_workers: int) -> None:
            seen["max_workers"] = max_workers
            super().__init__(max_workers=max_workers)

    def fake_run_case(bak_path: Path, stats_path: Path | None) -> dict[str, Any]:
        return {"bak": bak_path.name}

    monkeypatch.setattr(correctness_coverage, "ProcessPoolExecutor", SpyProcessPool, raising=False)
    monkeypatch.setattr(correctness_coverage, "_run_case", fake_run_case)

    correctness_coverage._run_cases(cases, threads=2)

    assert seen == {"max_workers": 2}
