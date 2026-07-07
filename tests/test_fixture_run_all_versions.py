from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from tools import fixture_run


@pytest.mark.quick
def test_all_versions_skips_known_ss2019_xtp_generators(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        fixture_run,
        "_discover_version_instances",
        lambda: {
            "2019": "sqlserver-2019",
            "2022": "sqlserver-2022",
        },
    )

    def fake_run(argv: list[str]) -> SimpleNamespace:
        server = argv[argv.index("--server") + 1]
        cmd = argv[-1]
        calls.append((server, cmd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(fixture_run.subprocess, "run", fake_run)

    result = fixture_run._run_all_versions(
        versions=None,
        fixture_base=tmp_path,
        suite=["xtp-simple", "xtp-probe", "xtp-checkpoint", "temporal-hidden"],
    )

    assert result == 0
    assert ("sqlserver-2019", "xtp-simple") not in calls
    assert ("sqlserver-2019", "xtp-probe") not in calls
    assert ("sqlserver-2019", "xtp-checkpoint") not in calls
    assert ("sqlserver-2019", "temporal-hidden") in calls
    assert ("sqlserver-2022", "xtp-simple") in calls
    assert ("sqlserver-2022", "xtp-probe") in calls
    assert ("sqlserver-2022", "xtp-checkpoint") in calls

    stderr = capsys.readouterr().err
    assert "xfail/skip SS2019/xtp-simple" in stderr
    assert "xfail/skip SS2019/xtp-probe" in stderr
    assert "xfail/skip SS2019/xtp-checkpoint" in stderr


@pytest.mark.quick
def test_all_versions_suite_commands_are_registered_cli_subcommands() -> None:
    for cmd in fixture_run._ALL_VERSIONS_SUITE:
        assert cmd in fixture_run._COMMANDS

        result = subprocess.run(
            [sys.executable, "-m", "tools.fixture_run", cmd, "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"{cmd!r} is in _ALL_VERSIONS_SUITE but is not a usable fixture_run "
            f"subcommand:\nstdout={result.stdout}\nstderr={result.stderr}"
        )
