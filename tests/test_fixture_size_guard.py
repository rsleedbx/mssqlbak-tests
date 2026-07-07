from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_fixture_size import (
    HARD_LIMIT_MB,
    MIB,
    candidate_files,
    check_files,
)


@pytest.mark.quick
def test_no_tracked_blob_over_hard_limit() -> None:
    """No git-tracked/staged file may be >= the GitHub 100 MiB hard limit.

    This is the enforcement point for the fixture-size policy: oversized .bak
    fixtures must be committed as *.bak.zst (conftest decompresses at test time).
    """
    violations = check_files(candidate_files())
    errors = [v for v in violations if v.level == "error"]
    assert not errors, "tracked blobs exceed the 100 MiB hard limit:\n" + "\n".join(
        f"  {v.size_mb:.2f} MiB  {v.path}  -> {v.hint}" for v in errors
    )


@pytest.mark.quick
def test_check_files_flags_oversized(tmp_path: Path) -> None:
    big = tmp_path / "huge.bak"
    big.write_bytes(b"\0" * (3 * MIB))
    small = tmp_path / "ok.txt"
    small.write_bytes(b"\0" * 16)
    # Use tiny thresholds so the 3 MiB file trips the hard limit deterministically.
    violations = check_files([big, small], hard_mb=1, warn_mb=1, repo_root=tmp_path)
    assert [v.path for v in violations] == ["huge.bak"]
    assert violations[0].level == "error"
    assert "bak.zst" in violations[0].hint


@pytest.mark.quick
def test_check_files_warn_band(tmp_path: Path) -> None:
    mid = tmp_path / "mid.parquet"
    mid.write_bytes(b"\0" * (2 * MIB))
    violations = check_files([mid], hard_mb=4, warn_mb=1, repo_root=tmp_path)
    assert violations and violations[0].level == "warn"


@pytest.mark.quick
def test_hard_limit_is_github_value() -> None:
    assert HARD_LIMIT_MB == 100
