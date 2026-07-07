"""Guard: the committed type-mapping doc must match a fresh generation.

Keeps ``docs/type_mapping_delta.md`` in sync with ``mssqlbak.types.arrow_type`` and
the curated value rules — if a mapping or note changes, this test fails until
the doc is regenerated with ``python -m tools.type_mapping``.
"""
from __future__ import annotations

from mssqlbak.types import SUPPORTED_TYPE_IDS
from tools.type_mapping import DOC_PATH, VALUE_RULES, build_report


def test_type_mapping_doc_is_current() -> None:
    expected = build_report()
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/type_mapping_delta.md is stale; regenerate it with "
        "`python -m tools.type_mapping`"
    )


def test_every_supported_type_has_a_value_rule() -> None:
    missing = sorted(SUPPORTED_TYPE_IDS - VALUE_RULES.keys())
    assert not missing, f"add a VALUE_RULES note for xtype(s) {missing} in tools/type_mapping.py"
