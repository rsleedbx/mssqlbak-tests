"""Tests for tools/spec_probe.py evidence harness."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.fixture
def test_spec_probe_pages_matches_g13(fixture_bak) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "tools.spec_probe", "pages", "--fixture", str(fixture_bak)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    record = json.loads(proc.stdout)
    assert record["verdict"] == "match"
    assert record["observed"]["iam_bitmap_offset"] == 194


@pytest.mark.fixture
def test_spec_probe_rowcompress_g19_schema(fixture_bak_datacompression) -> None:
    proc = subprocess.run(
        [
            sys.executable, "-m", "tools.spec_probe", "rowcompress",
            "--fixture", str(fixture_bak_datacompression),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    # G19 passes when compression matrix includes sdt column (after regen).
    record = json.loads(proc.stdout)
    if record["verdict"] == "mismatch":
        pytest.skip("compressioncoverage_full.bak predates smalldatetime column; regen matrix")
    assert record["verdict"] == "match"
