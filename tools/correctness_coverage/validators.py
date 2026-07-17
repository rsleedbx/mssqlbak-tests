"""Pluggable validator registry for metadata ground-truth verification.

Pattern mirrors the sink registry in :mod:`~tools.correctness_coverage.sinks`
(``SinkSpec`` / ``SINKS``).  Adding a new metadata category requires:

1. A comparator function in :mod:`~tools.correctness_coverage.metadata_verify`.
2. One :class:`ValidatorSpec` entry appended to :data:`VALIDATORS`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from tools.correctness_coverage.metadata_verify import RecoveredMetadata, ValidationResult


@dataclass(frozen=True)
class ValidatorSpec:
    """Registry entry for a metadata-category validator."""

    name: str
    label: str
    run: Callable[["dict", "RecoveredMetadata"], "ValidationResult"]


def _make_validators() -> dict[str, ValidatorSpec]:
    from tools.correctness_coverage.metadata_verify import (
        verify_constraints,
        verify_extended_properties,
        verify_indexes,
        verify_modules,
        verify_plan_guides,
        verify_query_store,
        verify_schema_objects,
        verify_security,
        verify_statistics,
    )

    return {
        "constraints": ValidatorSpec(
            name="constraints",
            label="Constraints (PK/UQ/FK/CHECK/DEFAULT)",
            run=lambda gt, rm: verify_constraints(gt, rm),
        ),
        "indexes": ValidatorSpec(
            name="indexes",
            label="Indexes",
            run=lambda gt, rm: verify_indexes(gt, rm),
        ),
        "extended_properties": ValidatorSpec(
            name="extended_properties",
            label="Extended properties (MS_Description, …)",
            run=lambda gt, rm: verify_extended_properties(gt, rm),
        ),
        "modules": ValidatorSpec(
            name="modules",
            label="Module definitions (views, procs, functions, triggers)",
            run=lambda gt, rm: verify_modules(gt, rm),
        ),
        "schema_objects": ValidatorSpec(
            name="schema_objects",
            label="Schema objects (schemas, sequences, synonyms, table types)",
            run=lambda gt, rm: verify_schema_objects(gt, rm),
        ),
        "security": ValidatorSpec(
            name="security",
            label="Security (principals + permissions)",
            run=lambda gt, rm: verify_security(gt, rm),
        ),
        "statistics": ValidatorSpec(
            name="statistics",
            label="Statistics (existence + key cols + flags)",
            run=lambda gt, rm: verify_statistics(gt, rm),
        ),
        "plan_guides": ValidatorSpec(
            name="plan_guides",
            label="Plan guides",
            run=lambda gt, rm: verify_plan_guides(gt, rm),
        ),
        "query_store": ValidatorSpec(
            name="query_store",
            label="Query Store (enabled + query-text presence)",
            run=lambda gt, rm: verify_query_store(gt, rm),
        ),
    }


# Lazily initialised on first access to avoid import cycles at module load time.
_VALIDATORS: dict[str, ValidatorSpec] | None = None


def get_validators() -> dict[str, ValidatorSpec]:
    """Return the VALIDATORS registry (initialised once, thread-safe for reads)."""
    global _VALIDATORS
    if _VALIDATORS is None:
        _VALIDATORS = _make_validators()
    return _VALIDATORS


#: Convenience alias — callers can ``from validators import VALIDATORS`` after
#: the module is fully imported, but prefer :func:`get_validators` in code that
#: may run before all imports are resolved.
VALIDATORS: dict[str, ValidatorSpec] = {}  # populated lazily via __getattr__


def __getattr__(name: str) -> object:
    if name == "VALIDATORS":
        return get_validators()
    raise AttributeError(name)
