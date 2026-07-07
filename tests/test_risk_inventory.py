from __future__ import annotations

from pathlib import Path

from tools.risk_inventory import discover_risks


def test_risk_inventory_finds_recent_failure_classes() -> None:
    risks = discover_risks(Path.cwd())
    names = {risk.name for risk in risks}

    assert "alias_type_name_map" in names
    assert "xml_serialization_regex" in names
    assert "wkt_number_regex" in names
    assert "float_text_precision" in names
    assert "cells_sample_digest_mode" in names
