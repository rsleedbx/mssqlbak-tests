from __future__ import annotations

from pathlib import Path

import pytest

from tools import register_bak


def test_register_all_skips_unrestoreable_fixtures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    for name in (
        "corrupt_metadata_confidence_full.bak",
        "normal_full.bak",
        "tde_full.bak",
    ):
        (tmp_path / name).write_bytes(b"bak")

    registered: list[str] = []

    def fake_main(argv: list[str]) -> int:
        registered.append(Path(argv[0]).name)
        return 0

    monkeypatch.setattr(register_bak, "main", fake_main)

    assert register_bak.register_all(tmp_path) == 0
    assert registered == ["normal_full.bak"]

    stderr = capsys.readouterr().err
    assert "skip (unrestoreable by design): corrupt_metadata_confidence_full.bak" in stderr
    assert "skip (unrestoreable by design): tde_full.bak" in stderr
