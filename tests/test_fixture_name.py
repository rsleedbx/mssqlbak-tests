from __future__ import annotations

import pytest

from tools.fixture_name import (
    DIST,
    ENC,
    NULL,
    ORG,
    fixture_name,
    parse_fixture_name,
)


@pytest.mark.quick
@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        (
            dict(org="cci", enc="enc1for", type="multi", dist="mmbnd", rows=65537),
            "cs__cci__enc1for__multi__mmbnd__r65537.bak",
        ),
        (
            dict(org="cci", enc="enc3v4", type="nvarchar", dist="cycle", null="spnull"),
            "cs__cci__enc3v4__nvarchar__cycle__spnull.bak",
        ),
        (
            dict(org="cciord", enc="enc1for", type="bigint", dist="asc"),
            "cs__cciord__enc1for__bigint__asc.bak",
        ),
        (
            dict(org="delbmp", enc="enc1for", type="multi", dist="runs"),
            "cs__delbmp__enc1for__multi__runs.bak",
        ),
    ],
)
def test_fixture_name_matches_plan_examples(kwargs: dict, expected: str) -> None:
    assert fixture_name(**kwargs) == expected


@pytest.mark.quick
@pytest.mark.parametrize(
    "kwargs",
    [
        dict(org="cci", enc="enc1for", type="multi", dist="mmbnd", rows=65537),
        dict(org="cci", enc="enc3v4", type="nvarchar", dist="cycle", null="spnull"),
        dict(org="ccipart", enc="enc3v4", type="decimal_38_10", dist="rand", null="nullrun", rows=32768),
        dict(org="nccihp", enc="arch2", type="datetime2_7", dist="desc"),
    ],
)
def test_round_trip(kwargs: dict) -> None:
    parsed = parse_fixture_name(fixture_name(**kwargs))
    assert parsed["is_matrix"] is True
    for key, val in kwargs.items():
        assert parsed[key] == val
    # Defaulted optionals come back as None when omitted from kwargs.
    if "null" not in kwargs:
        assert parsed["null"] is None
    if "rows" not in kwargs:
        assert parsed["rows"] is None


@pytest.mark.quick
def test_default_optionals_are_omitted() -> None:
    name = fixture_name(org="cci", enc="enc1for", type="int", dist="asc", null="none")
    assert name == "cs__cci__enc1for__int__asc.bak"
    assert parse_fixture_name(name)["null"] is None


@pytest.mark.quick
@pytest.mark.parametrize(
    "candidate",
    [
        "cci_bitpack_probe_full.bak",  # legacy ad-hoc name
        "tabletypecoverage_full.bak",
        "ncci_heap_full",
    ],
)
def test_legacy_names_are_not_matrix(candidate: str) -> None:
    parsed = parse_fixture_name(candidate)
    assert parsed["is_matrix"] is False


@pytest.mark.quick
def test_parse_strips_sidecar_suffixes() -> None:
    stem = "cs__cci__enc1for__int__asc"
    for suffix in (".bak", ".bak.stats.json", ".bak.segments.json", ".cells", ".bak.zst"):
        parsed = parse_fixture_name(f"tests/fixtures_2022/{stem}{suffix}")
        assert parsed["is_matrix"] is True
        assert parsed["org"] == "cci"
        assert parsed["dist"] == "asc"


@pytest.mark.quick
def test_unknown_tokens_fail_loud() -> None:
    with pytest.raises(ValueError):
        fixture_name(org="nope", enc="enc1for", type="int", dist="asc")
    with pytest.raises(ValueError):
        fixture_name(org="cci", enc="badenc", type="int", dist="asc")
    with pytest.raises(ValueError):
        fixture_name(org="cci", enc="enc1for", type="int", dist="sideways")


@pytest.mark.quick
def test_malformed_matrix_name_raises_but_legacy_does_not() -> None:
    # cs__ prefix but too few fields → generator bug → loud.
    with pytest.raises(ValueError):
        parse_fixture_name("cs__cci__enc1for.bak")
    # cs__ with an unknown trailing token → loud.
    with pytest.raises(ValueError):
        parse_fixture_name("cs__cci__enc1for__int__asc__bogus.bak")


@pytest.mark.quick
def test_vocabularies_are_disjoint_where_it_matters() -> None:
    # A trailing token is classified as null vs rows vs error; these must not collide.
    assert NULL.isdisjoint(ORG)
    assert NULL.isdisjoint(ENC)
    assert NULL.isdisjoint(DIST)
