# Broader Risk Fixture Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand correctness coverage so hard-coded decoder, canonicalizer, and verifier assumptions are exercised by at least two independent fixture shapes.

**Architecture:** Start with a static risk inventory that discovers hard-coded constants, maps, regexes, and branch thresholds. For each accepted risk class, add one sentinel test that proves unknown/neighbor values are handled generically, then add or extend `.bak` fixtures so the same path is hit through a second storage or data shape.

**Tech Stack:** Python, pytest, pyright, ruff, existing `tools.fixture_run` fixture generators, `.stats.json` and `.cells/` sidecars, SQL Server documentation in `/Users/robert.lee/github/sql-docs`.

---

## Scope

This plan targets risks that would have caught the recent real-world failures or a direct neighbor of those failures:

- Alias/user-defined types over system types.
- XML serialization and typed XML atomic values.
- Spatial WKT text and shape coverage.
- Float/real text canonicalization.
- `sql_variant` canonicalization.
- `.cells` verifier modes: full, sample, digest-only, capped digest-only.

This plan does not regenerate production data or overwrite existing `.bak` fixtures. New fixture variants use new names; existing fixture generators may be extended only when the fixture's purpose already includes that behavior.

## Coverage Standard

A risk class is accepted only when it satisfies both conditions:

- It would have caught at least one recent real-world failure.
- It has a neighboring condition that could fail from the same hard-coded assumption.

Every accepted risk class gets at least two hits:

- One constant-discovery or differential sentinel test that uses unknown or neighbor values.
- One `.bak` fixture path that exercises the same code through SQL Server storage and `.cells` verification.

## Source References

Use these SQL docs as fixture-design references:

- `docs/t-sql/data-types/bit-transact-sql.md`
- `docs/t-sql/statements/create-type-transact-sql.md`
- `docs/relational-databases/databases/create-a-user-defined-data-type-alias.md`
- `docs/t-sql/data-types/float-and-real-transact-sql.md`
- `docs/t-sql/functions/cast-and-convert-transact-sql.md`
- `docs/t-sql/spatial-geometry/stastext-geometry-data-type.md`
- `docs/t-sql/spatial-geometry/astextzm-geometry-data-type.md`
- `docs/t-sql/spatial-geography/stastext-geography-data-type.md`
- `docs/t-sql/spatial-geography/astextzm-geography-data-type.md`
- `docs/relational-databases/xml/for-xml-support-for-string-data-types.md`
- `docs/relational-databases/xml/invalid-characters-and-escape-rules.md`
- `docs/relational-databases/xml/for-xml-support-for-the-xml-data-type.md`
- `docs/relational-databases/xml/create-instances-of-xml-data.md`
- `docs/relational-databases/xml/values-for-xsd-simpletype-declarations.md`

## Files

- Create: `tools/risk_inventory.py` — static inventory of hard-coded values and their coverage owners.
- Create: `docs/risk_fixture_coverage.md` — generated/current-state ledger of risk classes and fixture hits.
- Modify: `tests/test_value_correctness.py` — verifier-mode and canonicalization sentinel tests.
- Modify: `tools/cell_canon.py` only if sentinel tests expose non-generic behavior.
- Modify: `tools/value_verify.py` only if sentinel tests expose verifier-mode gaps.
- Modify: `tools/make_alias_types_fixture.py` — unknown alias names and non-bit alias base types.
- Modify: `tests/test_alias_types_coverage.py` — assertions for unknown aliases and base-type canonicalization.
- Modify: `tools/make_typed_xml_fixture.py` — empty elements, CR/entity forms, typed numeric values.
- Modify: `tests/test_typed_xml_coverage.py` — value and digest assertions for expanded typed XML rows.
- Modify: `tools/make_spatial_edge_fixture.py` — high-precision coordinates, Z/M, collections, curves or holes.
- Modify: `tests/test_spatial_edge_coverage.py` — expected WKT assertions for expanded spatial rows.
- Create: `tools/make_float_extreme_fixture.py` — rowstore float/real text boundary fixture.
- Create: `tests/test_float_extreme_coverage.py` — float/real canonicalization and cell-value checks.
- Modify: `tools/fixture_run.py` — wire new standalone fixtures.
- Modify: `tests/conftest.py` — fixtures for new standalone `.bak` files.

## Task 1: Add Static Risk Inventory

**Files:**
- Create: `tools/risk_inventory.py`
- Create: `docs/risk_fixture_coverage.md`
- Test: `tests/test_risk_inventory.py`

- [ ] **Step 1: Write a failing test for constant discovery**

Create `tests/test_risk_inventory.py`:

```python
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
```

- [ ] **Step 2: Run the failing test**

```bash
.venv/bin/python -m pytest tests/test_risk_inventory.py -q
```

Expected: import failure for `tools.risk_inventory`.

- [ ] **Step 3: Implement the minimum inventory model**

Create `tools/risk_inventory.py`:

```python
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
```

- [ ] **Step 4: Run the inventory test**

```bash
.venv/bin/python -m pytest tests/test_risk_inventory.py -q
```

Expected: pass.

- [ ] **Step 5: Write the initial ledger**

Create `docs/risk_fixture_coverage.md` with one row per risk:

```markdown
# Risk Fixture Coverage

| Risk | Recent failure class | Code path | Fixture hits | Required next hit |
|---|---|---|---|---|
| Alias type name map | AdventureWorks Flag/NameStyle alias BIT text | `tools/cell_canon.py` `_ALIASES` | `alias_types_full` | unknown alias names over the same base types |
| XML serialization regex | AdventureWorks XML empty-element and CR serialization | `tools/cell_canon.py` XML canonicalization | `typed_xml_full`, `xmlcoverage_full` | typed XML rows with empty element, CR, entity, numeric lexical forms |
| WKT number regex | AdventureWorks geography WKT precision | `tools/cell_canon.py` WKT canonicalization | `spatial_edge_full` | high-precision WKT and Z/M rows |
| Float text precision | max finite float sidecar text overflow | `tools/cell_canon.py` `_canon_float` | `boundarycoverage_full`, `ncci_types_full` | rowstore float/real extreme fixture |
| Cells sample digest mode | sampled/capped cells sidecar digest authority | `tools/value_verify.py` sample/digest-only branches | `cci_bitpack_probe_bigint_full` | synthetic capped sidecar and large keyless fixture |
```

## Task 2: Add Unknown Alias Sentinel Coverage

**Files:**
- Modify: `tools/make_alias_types_fixture.py`
- Modify: `tests/test_alias_types_coverage.py`
- Modify: `tools/cell_canon.py` only if alias handling remains name-specific.

- [ ] **Step 1: Write tests for unknown alias names**

Add assertions to `tests/test_alias_types_coverage.py`:

```python
def test_unknown_alias_names_use_base_type_canonicalization(
    fixture_bak_alias_types: Path,
) -> None:
    rows_by_id = {r["id"]: r for r in _rows(fixture_bak_alias_types)}
    assert canon(rows_by_id[1]["random_flag_123"], "RandomFlag123") == "1"
    assert canon(rows_by_id[2]["random_flag_123"], "RandomFlag123") == "0"
    assert canon(rows_by_id[1]["float_alias"], "FloatAlias") == "1.5"
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_alias_types_coverage.py -q
```

Expected: missing columns or canonicalization mismatch.

- [ ] **Step 3: Extend the alias fixture generator**

In `tools/make_alias_types_fixture.py`, add:

```sql
CREATE TYPE dbo.RandomFlag123 FROM bit NULL
CREATE TYPE dbo.FloatAlias FROM float NULL
CREATE TYPE dbo.MoneyAlias FROM money NULL
```

Add columns:

```sql
random_flag_123 dbo.RandomFlag123 NULL,
float_alias     dbo.FloatAlias     NULL,
money_alias     dbo.MoneyAlias     NULL
```

Add values:

```python
1: {"random_flag_123": True, "float_alias": 1.5, "money_alias": "12.3400"}
2: {"random_flag_123": False, "float_alias": 2.25, "money_alias": "0.0100"}
3: {"random_flag_123": None, "float_alias": None, "money_alias": None}
```

- [ ] **Step 4: Remove name-specific alias dependency**

If the test still depends on `_ALIASES`, update `tools/cell_canon.py` so verifier code can use manifest base-type metadata. If manifest only stores alias names, update `tools/cells_capture.py` to include both `sql_type` and `base_sql_type`, then use `base_sql_type` in `verify_table()`.

- [ ] **Step 5: Regenerate fixture and sidecars**

```bash
.venv/bin/python -m tools.fixture_run all-versions --suite alias-types
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-bak tests/fixtures_2022/alias_types_full.bak --cells-only
```

Expected: fixture exists and `.cells/_manifest.json` includes the new columns.

- [ ] **Step 6: Run tests**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_alias_types_coverage.py tests/test_value_correctness.py -q -k "alias_types or canon_rules"
```

Expected: pass.

## Task 3: Add XML Serialization and Typed-Atom Fixture Coverage

**Files:**
- Modify: `tools/make_typed_xml_fixture.py`
- Modify: `tests/test_typed_xml_coverage.py`
- Modify: `tools/cell_canon.py` or `mssqlbak/xmlbin.py` only for failures exposed by the fixture.

- [ ] **Step 1: Write fixture-backed XML expectations**

In `tests/test_typed_xml_coverage.py`, assert these snippets by row id:

```python
EXPECTED_NEW_SNIPPETS = {
    4: ("<empty/>",),
    5: ("line1", "line2"),
    6: ("<squareFeet>21000</squareFeet>",),
    7: ("Primary Bank &amp; Reserve",),
    8: ("<asBoolean>true</asBoolean>", "<asDecimal>3.14</asDecimal>"),
}
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_typed_xml_coverage.py -q
```

Expected: missing row ids.

- [ ] **Step 3: Extend `tools/make_typed_xml_fixture.py`**

Add schema elements:

```xml
<xsd:element name="empty" type="xsd:string" minOccurs="0" />
<xsd:element name="note" type="xsd:string" minOccurs="0" />
<xsd:element name="squareFeet" type="xsd:decimal" minOccurs="0" />
<xsd:element name="bank" type="xsd:string" minOccurs="0" />
<xsd:element name="asBoolean" type="xsd:boolean" minOccurs="0" />
<xsd:element name="asDecimal" type="xsd:decimal" minOccurs="0" />
```

Add rows:

```python
4: '<event id="4" kind="empty"><message></message><severity>40</severity><empty></empty></event>'
5: '<event id="5" kind="cr"><message>line1&#x0D;\nline2</message><severity>50</severity><note>cr</note></event>'
6: '<event id="6" kind="numeric"><message>store</message><severity>60</severity><squareFeet>21000.0</squareFeet></event>'
7: '<event id="7" kind="entity"><message>entity</message><severity>70</severity><bank>Primary Bank &amp; Reserve</bank></event>'
8: '<event id="8" kind="typed"><message>typed atoms</message><severity>80</severity><asBoolean>true</asBoolean><asDecimal>3.1400</asDecimal></event>'
```

- [ ] **Step 4: Regenerate typed XML fixture and sidecars**

```bash
.venv/bin/python -m tools.fixture_run all-versions --suite typed-xml
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-bak tests/fixtures_2022/typed_xml_full.bak --cells-only
```

- [ ] **Step 5: Run XML tests**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_typed_xml_coverage.py tests/test_xml_coverage.py tests/test_value_correctness.py -q -k "typed_xml or xml_normalizes"
```

Expected: pass.

## Task 4: Add Spatial Precision, Z/M, and Shape Coverage

**Files:**
- Modify: `tools/make_spatial_edge_fixture.py`
- Modify: `tests/test_spatial_edge_coverage.py`
- Modify: `mssqlbak/spatial.py` or `tools/cell_canon.py` only for failures exposed by the fixture.

- [ ] **Step 1: Add expected spatial rows**

Extend `EXPECTED_GEOMETRY` and `EXPECTED_GEOGRAPHY` with:

```python
5: "POINT (-122.408489591016 37.7605893030868)"
6: "POINT (1 2 3 4)"
7: "LINESTRING (0 0, 1 1, 2 1)"
8: "GEOMETRYCOLLECTION (POINT (1 2), LINESTRING (0 0, 1 1))"
9: "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1))"
```

- [ ] **Step 2: Run spatial coverage and verify failure**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_spatial_edge_coverage.py -q
```

Expected: missing row ids or WKT mismatches.

- [ ] **Step 3: Extend generator SQL**

Use `geometry::STGeomFromText(...)` and `geography::STGeomFromText(...)` for rows that SQL Server accepts. Use `geometry::Point` / `geography::Point` for high-precision point rows when that preserves the intended coordinate order.

- [ ] **Step 4: Regenerate spatial fixture and sidecars**

```bash
.venv/bin/python -m tools.fixture_run all-versions --suite spatial-edge
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-bak tests/fixtures_2022/spatial_edge_full.bak --cells-only
```

- [ ] **Step 5: Run tests**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_spatial_edge_coverage.py tests/test_value_correctness.py -q -k "spatial_edge or spatial_normalizes"
```

Expected: pass.

## Task 5: Add Float/Real Extreme Fixture

**Files:**
- Create: `tools/make_float_extreme_fixture.py`
- Create: `tests/test_float_extreme_coverage.py`
- Modify: `tools/fixture_run.py`
- Modify: `tests/conftest.py`

- [x] **Step 1: Write tests for rowstore float/real extremes**

Create `tests/test_float_extreme_coverage.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_float_extreme_fixture import EXPECTED_ROWS, TABLE


def _rows(fixture: Path) -> dict[int, dict[str, object]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == TABLE), None)
    if table is None:
        pytest.fail(f"Table {TABLE!r} not found")
    return {int(row["id"]): row for row in read_table_rows(store, table)}


def test_float_extreme_values(fixture_bak_float_extreme: Path) -> None:
    rows = _rows(fixture_bak_float_extreme)
    assert set(rows) == set(EXPECTED_ROWS)
    for row_id, expected in EXPECTED_ROWS.items():
        assert rows[row_id]["f64"] == expected["f64"]
        assert rows[row_id]["f32"] == expected["f32"]
```

- [x] **Step 2: Run the test and verify collection fails**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_float_extreme_coverage.py -q
```

Expected: missing fixture or import.

- [x] **Step 3: Add generator**

Create `tools/make_float_extreme_fixture.py` using `tools.fixture_utils` with rows:

```python
EXPECTED_ROWS = {
    1: {"f64": 1.7976931348623157e308, "f32": 3.4028235e38},
    2: {"f64": -1.7976931348623157e308, "f32": -3.4028235e38},
    3: {"f64": 2.2250738585072014e-308, "f32": 1.17549435e-38},
    4: {"f64": 0.0, "f32": 0.0},
    5: {"f64": 0.1, "f32": 0.1},
}
```

DDL:

```sql
CREATE TABLE dbo.float_extreme (
    id  INT NOT NULL PRIMARY KEY CLUSTERED,
    f64 FLOAT NULL,
    f32 REAL NULL
)
```

- [x] **Step 4: Wire fixture**

Modify `tools/fixture_run.py`:

```python
def _run_float_extreme(*, force: bool = False) -> int:
    from tools.make_float_extreme_fixture import main
    sys.argv = ["make_float_extreme_fixture", *(["--force"] if force else [])]
    return main()
```

Add command key `float-extreme`, parser help, and dispatch branch.

Modify `tests/conftest.py`:

```python
FIXTURE_BAK_FLOAT_EXTREME = _FIXTURE_DIR / "float_extreme_full.bak"


@pytest.fixture
def fixture_bak_float_extreme() -> Path:
    if not FIXTURE_BAK_FLOAT_EXTREME.exists():
        pytest.skip("float_extreme_full.bak not present")
    return FIXTURE_BAK_FLOAT_EXTREME
```

- [x] **Step 5: Generate fixture and sidecars**

```bash
.venv/bin/python -m tools.fixture_run all-versions --suite float-extreme
.venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 register-bak tests/fixtures_2022/float_extreme_full.bak --cells-only
```

- [x] **Step 6: Run tests**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_float_extreme_coverage.py tests/test_value_correctness.py -q -k "float_extreme or float_text"
```

Expected: pass.

## Task 6: Add Verifier-Mode Sentinel Tests

**Files:**
- Modify: `tests/test_value_correctness.py`
- Modify: `tools/value_verify.py` only if tests expose mode bugs.

- [ ] **Step 1: Add capped digest-only synthetic test**

Add helper:

```python
def _write_capped_digest_cells(cells_dir: Path) -> None:
    cells_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table({"val": pa.array(["1", "2"], pa.string())}),
        cells_dir / "dbo.capped.parquet",
    )
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.capped",
                "row_count": 4,
                "key_columns": [],
                "mode": "digest-only",
                "values_sorted": True,
                "values_capped": 2,
                "columns": [
                    {
                        "name": "val",
                        "sql_type": "int",
                        "digest": column_digest(["1", "2", "3", "4"]),
                        "null_count": 0,
                    }
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))
```

Add test:

```python
def test_capped_digest_only_uses_manifest_full_column_digest(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_capped_digest_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    extracted = pa.table({"val": pa.array([1, 2, 3, 4], pa.int64())})
    res = verify_table(extracted, cells, entry)
    assert res.ok, (res.digest_mismatches, res.samples)
```

- [ ] **Step 2: Add raw full-sidecar normalization test**

Add a full sidecar that stores `True`/`False` but has a manifest digest over the raw strings. Assert decoded booleans pass because `verify_table()` accepts the raw sidecar digest and compares canonicalized cell values.

- [ ] **Step 3: Run tests**

```bash
.venv/bin/python -m pytest tests/test_value_correctness.py -q -k "capped_digest or raw_full_sidecar or sample_sidecar"
```

Expected: pass.

## Task 7: Add SQL Variant Neighbor Coverage

**Files:**
- Modify: `tools/make_sql_variant_extract_fixture.py`
- Modify: `tests/test_sql_variant_extract_coverage.py`

- [ ] **Step 1: Add test expectations for unhit branches**

Add rows for:

```sql
CAST(CONVERT(uniqueidentifier, '11111111-1111-1111-1111-111111111111') AS sql_variant)
CAST(0xDEADBEEF AS sql_variant)
CAST(CONVERT(datetimeoffset, '2020-01-02T03:04:05.1234567+05:30') AS sql_variant)
CAST(CAST(1.2300 AS decimal(10,4)) AS sql_variant)
```

- [ ] **Step 2: Run tests to verify failure or missing rows**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_sql_variant* -q
```

- [ ] **Step 3: Extend or add fixture**

Extend `tools/make_sql_variant_extract_fixture.py` using its existing fixture style and expected values from `tools.cell_canon._canon_sql_variant_text()`.

- [ ] **Step 4: Generate and verify**

```bash
.venv/bin/python -m tools.fixture_run all-versions --suite sql-variant-extract
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_sql_variant* tests/test_value_correctness.py -q -k "sql_variant"
```

## Task 8: Regenerate Coverage and Update Ledger

**Files:**
- Modify: `docs/risk_fixture_coverage.md`
- Modify: `docs/correctness_coverage_fixtures_2017.md`
- Modify: `docs/correctness_coverage_fixtures_2019.md`
- Modify: `docs/correctness_coverage_fixtures_2022.md`
- Modify: `docs/correctness_coverage_fixtures_2025.md`

- [ ] **Step 1: Update risk ledger**

For each risk, record two independent hits:

```markdown
| Alias type name map | `alias_types_full` known aliases | `alias_types_full` unknown alias rows | pass |
| XML serialization regex | `xmlcoverage_full` untyped XML | `typed_xml_full` typed empty/CR/entity/numeric rows | pass |
| WKT number regex | `spatial_edge_full` basic shapes | `spatial_edge_full` high-precision/ZM/collection rows | pass |
| Float text precision | `boundarycoverage_full` CCI | `float_extreme_full` rowstore | pass |
| Cells sample digest mode | `cci_bitpack_probe_bigint_full` large sampled sidecar | synthetic capped digest-only sidecar | pass |
```

- [ ] **Step 2: Regenerate versioned correctness docs**

```bash
.venv/bin/python -m tools.correctness_coverage --fixture-dir tests/fixtures_2017
.venv/bin/python -m tools.correctness_coverage --fixture-dir tests/fixtures_2019
.venv/bin/python -m tools.correctness_coverage --fixture-dir tests/fixtures_2022
.venv/bin/python -m tools.correctness_coverage --fixture-dir tests/fixtures_2025
```

Expected: each doc reports `0 xfail · 0 fail`.

- [ ] **Step 3: Run final verification**

```bash
.venv/bin/python -m ruff check tools tests
.venv/bin/python -m pyright tools tests
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest \
  tests/test_value_correctness.py \
  tests/test_alias_types_coverage.py \
  tests/test_typed_xml_coverage.py \
  tests/test_spatial_edge_coverage.py \
  tests/test_float_extreme_coverage.py \
  -q
```

Expected: no lint/type errors and all selected tests pass, except intentional TDE xfail where included by broader stats runs.

## Execution Order

Implement in this order:

1. Task 1: static risk inventory and ledger.
2. Task 6: verifier-mode sentinel tests.
3. Task 2: unknown alias fixture expansion.
4. Task 3: typed XML expansion.
5. Task 4: spatial expansion.
6. Task 5: float extreme fixture.
7. Task 7: sql_variant neighbor coverage.
8. Task 8: coverage regeneration and final verification.

This order catches hard-coded assumptions before adding expensive fixtures, then expands existing fixtures before adding new standalone fixtures.
