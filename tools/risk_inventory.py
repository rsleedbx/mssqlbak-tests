from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Risk:
    name: str
    path: str
    pattern: str
    recent_failure_class: str
    fixture_hits: tuple[str, ...]


_RISKS: tuple[Risk, ...] = (
    Risk(
        name="alias_type_name_map",
        path="tools/cell_canon.py",
        pattern="_ALIASES",
        recent_failure_class="AdventureWorks Flag/NameStyle alias BIT text",
        fixture_hits=("alias_types_full",),
    ),
    Risk(
        name="xml_serialization_regex",
        path="tools/cell_canon.py",
        pattern="_XML_EMPTY_ELEMENT_RE / _XML_INTEGER_DECIMAL_RE",
        recent_failure_class="AdventureWorks XML empty-element and CR serialization",
        fixture_hits=("typed_xml_full", "xmlcoverage_full"),
    ),
    Risk(
        name="wkt_number_regex",
        path="tools/cell_canon.py",
        pattern="_WKT_NUMBER_RE",
        recent_failure_class="AdventureWorks geography WKT precision",
        fixture_hits=("spatial_edge_full",),
    ),
    Risk(
        name="float_text_precision",
        path="tools/cell_canon.py",
        pattern="_canon_float",
        recent_failure_class="max finite float sidecar text overflow",
        fixture_hits=("boundarycoverage_full", "ncci_types_full"),
    ),
    Risk(
        name="cells_sample_digest_mode",
        path="tools/value_verify.py",
        pattern="mode == sample / values_capped",
        recent_failure_class="sampled/capped cells sidecar digest authority",
        fixture_hits=("cci_bitpack_probe_bigint_full",),
    ),
)


def discover_risks(_repo_root: Path) -> list[Risk]:
    return list(_RISKS)
