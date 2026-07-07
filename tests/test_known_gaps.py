from __future__ import annotations

from tools.known_gaps import gap_reason


def test_dirty_cci_update_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_cci_update", version) is None


def test_dirty_concurrent_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_concurrent", version) is None


def test_dirty_large_dirty_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_large_dirty", version) is None


def test_dirty_snapshot_update_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_snapshot_update", version) is None


def test_dirty_temporal_update_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_temporal_update", version) is None


def test_realworld_credit_backup_is_no_longer_stats_known_gap() -> None:
    assert gap_reason("CreditBackup100", None) is None


def test_realworld_adventureworks_ext_is_no_longer_stats_known_gap() -> None:
    assert gap_reason("AdventureWorks2016_EXT", None) is None


def test_dirty_committed_update_v2_is_no_longer_a_known_gap() -> None:
    for version in (2017, 2019, 2022, 2025):
        assert gap_reason("dirtycoverage_committed_update_v2", version) is None
