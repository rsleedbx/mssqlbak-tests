# SQL Server `.bak` → Delta Parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Parse a SQL Server full `.bak` file directly (no engine) into typed rows + schema and write them to Delta tables.

**Architecture:** A streaming pipeline — `mtf` (demux MTF → MDF page stream) → `pages` (MDF page/allocation layer) → `catalog` (bootstrap system base tables → schema) → `records` (decode rows) → `types` (SQL→Arrow) → `sink` (deltalake). Correctness is proven against a reference fixture: a small `.bak` built from a known per-type value matrix via an ephemeral SQL Server container.

**Tech Stack:** Python 3.11+ (stdlib `struct`/`dataclasses`), `pyarrow` + `deltalake` for output, `pytest`/`ruff`/`pyright` for dev, Podman + `mcr.microsoft.com/mssql/server` for the reference fixture, `mssql_python` for the engine-diff check.

Reference for MDF internals (engineers must consult; do **not** invent byte offsets — confirm every layout against the fixture test): OrcaMDF source (github.com/improvedk/OrcaMDF) and Paul Randal's "anatomy of a page/record" articles. The page header is 96 bytes; data pages are 8192 bytes.

---

## Conventions

- All work on branch `feat/bak-to-delta`. Commit after every green step.
- Run tooling via the project venv: `./.venv/bin/pytest`, `./.venv/bin/ruff check .`, `./.venv/bin/pyright`.
- New package modules live under `mssqlbak/`. Tests mirror under `tests/`.
- Fixture-dependent tests are marked `@pytest.mark.fixture` and skipped when the fixture `.bak` is absent, so unit tests stay fast and hermetic.

---

## Task 0: Branch, dependencies, and module skeleton

**Files:**
- Modify: `pyproject.toml`
- Create: `mssqlbak/mtf.py`, `mssqlbak/pages.py`, `mssqlbak/catalog.py`, `mssqlbak/records.py`, `mssqlbak/types.py`, `mssqlbak/rows.py`, `mssqlbak/sink.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create branch**

Run:
```bash
git checkout -b feat/bak-to-delta
```

- [ ] **Step 2: Add runtime + dev dependencies**

Edit `pyproject.toml` `[project]` and extras:
```toml
dependencies = ["pyarrow>=16", "deltalake>=0.18"]

[project.optional-dependencies]
restore = ["mssql_python"]
engine  = ["mssql_python"]
dev     = ["pytest", "ruff", "pyright", "pyarrow>=16", "deltalake>=0.18"]
```

- [ ] **Step 3: Install**

Run (needs the Databricks pip proxy / network):
```bash
./.venv/bin/python -m pip install -e ".[dev]"
```
Expected: `Successfully installed ... deltalake ... pyarrow ...`

- [ ] **Step 4: Create empty module files with docstrings**

Each new module starts with a one-line module docstring and `from __future__ import annotations`. Example `mssqlbak/pages.py`:
```python
"""MDF page layer: boot page, page-by-id fetch, allocation maps."""
from __future__ import annotations
```
Repeat for `mtf.py`, `catalog.py`, `records.py`, `types.py`, `rows.py`, `sink.py`.

- [ ] **Step 5: Add the fixture marker + skip logic**

Create `tests/conftest.py`:
```python
"""Shared test fixtures and markers."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_BAK = Path(__file__).parent / "fixtures" / "typecoverage_full.bak"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "fixture: requires the generated reference .bak fixture")


@pytest.fixture
def fixture_bak() -> Path:
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK} (run tools/make_fixture.py)")
    return FIXTURE_BAK
```

- [ ] **Step 6: Verify nothing broke**

Run: `./.venv/bin/pytest -q && ./.venv/bin/ruff check . && ./.venv/bin/pyright`
Expected: existing 18 tests pass, ruff clean, pyright 0 errors.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml mssqlbak tests
git commit -m "Add module skeleton and Delta deps for bak-to-delta parser"
```

---

## Task 1: Reference fixture generator (type-coverage matrix + ephemeral SQL Server)

This is built first: it is the source of truth for every later task.

**Files:**
- Create: `tools/typematrix.py` (the value matrix + DDL/DML, shared by generator and tests)
- Create: `tools/make_fixture.py` (spin up container, load matrix, BACKUP, copy out)
- Test: `tests/test_typematrix.py`

- [ ] **Step 1: Write the failing test for the matrix definition**

Create `tests/test_typematrix.py`:
```python
from __future__ import annotations

from tools.typematrix import TYPE_CASES, expected_rows


def test_every_case_has_low_high_mid() -> None:
    for case in TYPE_CASES:
        labels = {r.label for r in case.rows}
        assert {"low", "high", "mid"} <= labels, case.sql_type


def test_nullable_cases_include_null() -> None:
    for case in TYPE_CASES:
        if case.nullable:
            assert any(r.value is None for r in case.rows), case.sql_type


def test_blob_values_capped_at_1mb() -> None:
    rows = expected_rows("varbinary_max")
    assert max(len(r.value) for r in rows if r.value is not None) <= 1_048_576
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/pytest tests/test_typematrix.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.typematrix'`.

- [ ] **Step 3: Implement the matrix**

Create `tools/__init__.py` (empty) and `tools/typematrix.py`:
```python
"""Per-type value matrix: low / high / mid / null per SQL Server data type.

Single source of truth shared by the fixture generator and the parser tests.
``value`` holds the canonical Python value the parser must reproduce.
"""
from __future__ import annotations

import datetime as dt
import random
import uuid
from dataclasses import dataclass, field

SEED = 20260602
_rng = random.Random(SEED)


@dataclass(frozen=True)
class Row:
    label: str          # "low" | "high" | "mid" | "null"
    value: object       # canonical Python value, or None


@dataclass(frozen=True)
class TypeCase:
    name: str           # stable id, e.g. "int", "varbinary_max"
    sql_type: str       # SQL Server column type, e.g. "int", "varbinary(max)"
    nullable: bool
    rows: list[Row]


def _row(label: str, value: object) -> Row:
    return Row(label=label, value=value)


def _build() -> list[TypeCase]:
    cases: list[TypeCase] = []

    def add(name: str, sql_type: str, low: object, high: object, mid: object,
            nullable: bool = True) -> None:
        rows = [_row("low", low), _row("high", high), _row("mid", mid)]
        if nullable:
            rows.append(_row("null", None))
        cases.append(TypeCase(name=name, sql_type=sql_type, nullable=nullable, rows=rows))

    add("tinyint", "tinyint", 0, 255, _rng.randint(1, 254))
    add("smallint", "smallint", -32768, 32767, _rng.randint(-32767, 32766))
    add("int", "int", -2147483648, 2147483647, _rng.randint(-2_000_000, 2_000_000))
    add("bigint", "bigint", -9223372036854775808, 9223372036854775807,
        _rng.randint(-10**15, 10**15))
    add("bit", "bit", False, True, bool(_rng.getrandbits(1)))
    add("decimal_38_10", "decimal(38,10)",
        -9999999999999999999999999999.9999999999,
        9999999999999999999999999999.9999999999, 12345.6789)
    add("money", "money", -922337203685477.5808, 922337203685477.5807, 1234.5678)
    add("real", "real", -3.4e38, 3.4e38, 1.5)
    add("float", "float", -1.79e308, 1.79e308, 3.141592653589793)
    add("date", "date", dt.date(1, 1, 1), dt.date(9999, 12, 31), dt.date(2020, 6, 15))
    add("datetime2_7", "datetime2(7)",
        dt.datetime(1, 1, 1, 0, 0, 0),
        dt.datetime(9999, 12, 31, 23, 59, 59, 999999),  # µs floor of .9999999
        dt.datetime(2020, 6, 15, 12, 34, 56, 789012))
    add("char10", "char(10)", "", "ZZZZZZZZZZ", "hello")
    add("varchar_max", "varchar(max)", "", "x", "lorem ipsum dolor")
    add("nvarchar50", "nvarchar(50)", "", "Z" * 50, "café \U0001F600")  # emoji surrogate
    add("varbinary_max", "varbinary(max)", b"", b"\x00",
        bytes(_rng.getrandbits(8) for _ in range(1_048_576)))  # 1 MB cap
    add("uniqueidentifier", "uniqueidentifier",
        uuid.UUID(int=0), uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
        uuid.UUID(int=_rng.getrandbits(128)))
    return cases


TYPE_CASES: list[TypeCase] = _build()


def expected_rows(case_name: str) -> list[Row]:
    for c in TYPE_CASES:
        if c.name == case_name:
            return c.rows
    raise KeyError(case_name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/pytest tests/test_typematrix.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Implement the fixture generator script**

Create `tools/make_fixture.py`. It writes one table per case (`t_<name>` with a single column `v` plus an `int identity` PK and a `label` column), inserts the matrix rows, backs up, and copies the `.bak` out of the container.
```python
"""Build the reference .bak fixture using an ephemeral SQL Server container.

Usage: ./.venv/bin/python tools/make_fixture.py
Produces tests/fixtures/typecoverage_full.bak
Requires: podman, and the mssql image pullable.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

from tools.typematrix import TYPE_CASES, Row

CONTAINER = "mssqlbak-fixture"
SA_PW = "Fixture!Pass1"
IMAGE = "mcr.microsoft.com/mssql/server:2022-latest"
DB = "TypeCoverage"
OUT = Path(__file__).parent.parent / "tests" / "fixtures" / "typecoverage_full.bak"


def _sqlcmd(sql: str) -> None:
    subprocess.run(
        ["podman", "exec", CONTAINER, "/opt/mssql-tools18/bin/sqlcmd",
         "-S", "localhost", "-U", "sa", "-P", SA_PW, "-C", "-b", "-Q", sql],
        check=True,
    )


def _literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, bytes):
        return "0x" + value.hex() if value else "0x"
    # str / date / datetime / uuid → quoted, doubled single-quotes
    return "N'" + str(value).replace("'", "''") + "'"


def build_sql() -> str:
    stmts: list[str] = [
        f"IF DB_ID('{DB}') IS NOT NULL BEGIN ALTER DATABASE [{DB}] SET SINGLE_USER "
        f"WITH ROLLBACK IMMEDIATE; DROP DATABASE [{DB}]; END;",
        f"CREATE DATABASE [{DB}];",
        f"USE [{DB}];",
    ]
    for case in TYPE_CASES:
        t = f"t_{case.name}"
        stmts.append(
            f"CREATE TABLE [{t}] (id int IDENTITY PRIMARY KEY, "
            f"label varchar(8) NOT NULL, v {case.sql_type} NULL);"
        )
        for r in case.rows:
            stmts.append(
                f"INSERT INTO [{t}] (label, v) VALUES ('{r.label}', {_literal(r.value)});"
            )
    return "\n".join(stmts)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["podman", "rm", "-f", CONTAINER], check=False)
    subprocess.run(
        ["podman", "run", "-d", "--name", CONTAINER,
         "-e", "ACCEPT_EULA=Y", "-e", f"MSSQL_SA_PASSWORD={SA_PW}",
         "-p", "11433:1433", IMAGE],
        check=True,
    )
    # wait for readiness
    for _ in range(60):
        rc = subprocess.run(
            ["podman", "exec", CONTAINER, "/opt/mssql-tools18/bin/sqlcmd",
             "-S", "localhost", "-U", "sa", "-P", SA_PW, "-C", "-Q", "SELECT 1"],
        ).returncode
        if rc == 0:
            break
        time.sleep(2)
    _sqlcmd(build_sql())
    _sqlcmd(
        f"BACKUP DATABASE [{DB}] TO DISK = N'/tmp/{DB}.bak' "
        f"WITH FORMAT, INIT, COPY_ONLY;"
    )
    subprocess.run(
        ["podman", "cp", f"{CONTAINER}:/tmp/{DB}.bak", str(OUT)], check=True,
    )
    subprocess.run(["podman", "rm", "-f", CONTAINER], check=False)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Generate the fixture**

Run: `./.venv/bin/python tools/make_fixture.py`
Expected: `wrote .../tests/fixtures/typecoverage_full.bak (NNN bytes)`.
Commit the `.bak` (it is a few MB) and add `tests/fixtures/` as committed test data (NOT gitignored).

- [ ] **Step 7: Sanity-check with the existing metadata reader**

Run:
```bash
./.venv/bin/python -c "from mssqlbak import read_bak_metadata, print_bak_info; print_bak_info(read_bak_metadata('tests/fixtures/typecoverage_full.bak'))"
```
Expected: prints `Database: TypeCoverage`, `Type: Full`. This confirms the fixture is a readable MTF file before we parse its pages.

- [ ] **Step 8: Commit**

```bash
git add tools tests/test_typematrix.py tests/fixtures/typecoverage_full.bak
git commit -m "Add type-coverage reference fixture generator and matrix"
```

---

## Task 2: MTF → MDF page-stream extraction

Extract the embedded MDF page bytes (the data-stream blocks between `SSET` and `ESET`) from the `.bak`, exposing them as an 8 KB-page-addressable byte source.

**Files:**
- Modify: `mssqlbak/mtf.py`
- Test: `tests/test_mtf.py`

- [ ] **Step 1: Write the failing test (page count + boot-page magic)**

A full backup's MDF stream is a multiple of 8192 bytes; page 9 (file 1) is the boot page whose first bytes encode page type 13 (`m_type` byte at offset 1 == 13 for a boot page is not guaranteed; assert structurally instead). Create `tests/test_mtf.py`:
```python
from __future__ import annotations

import pytest

from mssqlbak.mtf import extract_mdf_pages

PAGE = 8192


@pytest.mark.fixture
def test_mdf_stream_is_page_aligned(fixture_bak) -> None:
    data = extract_mdf_pages(fixture_bak)
    assert len(data) > 0
    assert len(data) % PAGE == 0


@pytest.mark.fixture
def test_boot_page_present(fixture_bak) -> None:
    data = extract_mdf_pages(fixture_bak)
    # boot page is page 9 in file 1
    boot = data[9 * PAGE:(9 + 1) * PAGE]
    assert len(boot) == PAGE
    # page header byte 0 (headerVersion) is 1 on all supported versions
    assert boot[0] == 1
```

- [ ] **Step 2: Run to verify it fails**

Run: `./.venv/bin/pytest tests/test_mtf.py -q`
Expected: FAIL — `ImportError: cannot import name 'extract_mdf_pages'`.

- [ ] **Step 3: Implement `extract_mdf_pages`**

In `mssqlbak/mtf.py`, reuse the block iterator from `reader.py` (refactor the shared block-walking into `mtf.py` and have `reader.py` import it to keep DRY). The MDF page data lives in the stream blocks following the `SSET` descriptor; concatenate their data-stream payloads. The engineer must confirm, against the fixture, the exact stream-block layout (MTF "stream" headers wrap the raw page data). Skeleton:
```python
"""MTF demux: extract the embedded MDF page stream from a .bak file."""
from __future__ import annotations

from pathlib import Path

from mssqlbak.reader import (
    BLOCK_ESET, BLOCK_SSET, _COMMON_HDR_SIZE, _detect_block_size, _iter_blocks,
)

PAGE_SIZE = 8192


def extract_mdf_pages(path: str | Path) -> bytes:
    """Return the concatenated 8 KB MDF pages contained in a full backup.

    Walks MTF blocks; once inside a data set (after SSET, before ESET) the
    payload bytes are the MDF page stream. The result length is a multiple of
    PAGE_SIZE. Confirm the stream-block payload offset against the fixture.
    """
    p = Path(path)
    out = bytearray()
    in_set = False
    with p.open("rb") as f:
        bs = _detect_block_size(f)
        for btype, block in _iter_blocks(f, bs):
            if btype == BLOCK_SSET:
                in_set = True
                continue
            if btype == BLOCK_ESET:
                in_set = False
                continue
            if in_set:
                out += block[_COMMON_HDR_SIZE:]  # confirm payload offset vs fixture
    usable = (len(out) // PAGE_SIZE) * PAGE_SIZE
    return bytes(out[:usable])
```

- [ ] **Step 4: Run; iterate against the fixture until the boot-page assertion passes**

Run: `./.venv/bin/pytest tests/test_mtf.py -q`
Expected: PASS. If `boot[0] != 1`, adjust the payload offset / which block types contribute page data, using a hex dump of the fixture (`xxd` first KB of each block type) to locate the page-aligned MDF start. This is the spike — get it green before moving on.

- [ ] **Step 5: Commit**

```bash
git add mssqlbak/mtf.py mssqlbak/reader.py tests/test_mtf.py
git commit -m "Extract MDF page stream from MTF backup"
```

---

## Task 3: Page layer — header, slot array, page-by-id

**Files:**
- Modify: `mssqlbak/pages.py`
- Test: `tests/test_pages.py`

- [ ] **Step 1: Write the failing tests**

```python
from __future__ import annotations

import pytest

from mssqlbak.mtf import extract_mdf_pages
from mssqlbak.pages import PageReader, PageHeader


@pytest.mark.fixture
def test_page_header_fields(fixture_bak) -> None:
    pr = PageReader(extract_mdf_pages(fixture_bak))
    boot = pr.header(9)
    assert isinstance(boot, PageHeader)
    assert boot.page_id == 9
    assert boot.file_id == 1


@pytest.mark.fixture
def test_slot_array_offsets_in_bounds(fixture_bak) -> None:
    pr = PageReader(extract_mdf_pages(fixture_bak))
    # find any data page (type 1) and ensure its slot offsets are within the page
    for pid in range(pr.page_count):
        h = pr.header(pid)
        if h.page_type == 1 and h.slot_count > 0:
            for off in pr.slot_offsets(pid):
                assert 96 <= off < 8192
            break
    else:
        pytest.skip("no data page found")
```

- [ ] **Step 2: Run to verify failure**

Run: `./.venv/bin/pytest tests/test_pages.py -q`
Expected: FAIL — import error.

- [ ] **Step 3: Implement the page layer**

In `mssqlbak/pages.py`, define the 96-byte header parse and slot array (slot array is `2 * slot_count` bytes at the end of the page, little-endian record offsets). Confirm header field offsets against OrcaMDF; the documented layout is: `headerVersion`(0,1B), `type`(1,1B), `typeFlagBits`(2,1B), `level`(3,1B), `flagBits`(4,2B), `indexId`(6,2B), `prevPage` pageId(8,4B)+fileId(12,2B), `pminlen`(14,2B), `nextPage` pageId(16,4B)+fileId(20,2B), `slotCnt`(22,2B), `objId`(24,4B), `freeCnt`(26?)… — **verify each offset against the fixture before trusting it.**
```python
"""MDF page layer: page header, slot array, page-by-id access."""
from __future__ import annotations

import struct
from dataclasses import dataclass

PAGE_SIZE = 8192
HEADER_SIZE = 96


@dataclass(frozen=True)
class PageHeader:
    page_id: int
    file_id: int
    page_type: int
    slot_count: int
    object_id: int
    next_page: int
    prev_page: int
    pminlen: int
    level: int


class PageReader:
    def __init__(self, mdf: bytes) -> None:
        self._mdf = mdf
        self.page_count = len(mdf) // PAGE_SIZE

    def raw(self, page_id: int) -> bytes:
        start = page_id * PAGE_SIZE
        return self._mdf[start:start + PAGE_SIZE]

    def header(self, page_id: int) -> PageHeader:
        b = self.raw(page_id)
        page_type = b[1]
        level = b[3]
        prev_pid, prev_fid = struct.unpack_from("<IH", b, 8)
        pminlen = struct.unpack_from("<H", b, 14)[0]
        next_pid, next_fid = struct.unpack_from("<IH", b, 16)
        slot_count = struct.unpack_from("<H", b, 22)[0]
        object_id = struct.unpack_from("<I", b, 24)[0]
        return PageHeader(
            page_id=page_id, file_id=1, page_type=page_type, slot_count=slot_count,
            object_id=object_id, next_page=next_pid, prev_page=prev_pid,
            pminlen=pminlen, level=level,
        )

    def slot_offsets(self, page_id: int) -> list[int]:
        b = self.raw(page_id)
        n = self.header(page_id).slot_count
        out: list[int] = []
        for i in range(n):
            off = struct.unpack_from("<H", b, PAGE_SIZE - 2 * (i + 1))[0]
            out.append(off)
        return out
```

- [ ] **Step 4: Run; iterate offsets until green**

Run: `./.venv/bin/pytest tests/test_pages.py -q`
Expected: PASS. Adjust struct offsets against a fixture hex dump until `page_id`, `slot_count`, and slot offsets are sane.

- [ ] **Step 5: Commit**

```bash
git add mssqlbak/pages.py tests/test_pages.py
git commit -m "Add MDF page header and slot-array reader"
```

---

## Task 4: Catalog bootstrap — recover user-table schemas

**Files:**
- Modify: `mssqlbak/catalog.py`
- Test: `tests/test_catalog.py`

- [ ] **Step 1: Write the failing test (schema recovery vs known fixture)**

The fixture created tables `t_<name>` each with columns `id int`, `label varchar(8)`, `v <type>`. Assert the catalog recovers them.
```python
from __future__ import annotations

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.mtf import extract_mdf_pages
from mssqlbak.pages import PageReader
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
def test_recovers_all_user_tables(fixture_bak) -> None:
    pr = PageReader(extract_mdf_pages(fixture_bak))
    schema = recover_schema(pr)
    names = {t.name for t in schema.tables}
    for case in TYPE_CASES:
        assert f"t_{case.name}" in names


@pytest.mark.fixture
def test_table_columns_in_order(fixture_bak) -> None:
    pr = PageReader(extract_mdf_pages(fixture_bak))
    schema = recover_schema(pr)
    t = next(t for t in schema.tables if t.name == "t_int")
    assert [c.name for c in t.columns] == ["id", "label", "v"]
```

- [ ] **Step 2: Run to verify failure**

Run: `./.venv/bin/pytest tests/test_catalog.py -q`
Expected: FAIL — import error.

- [ ] **Step 3: Implement bootstrap**

In `mssqlbak/catalog.py`: hard-code the base-table schemas (`sysallocunits`, `sysrowsets`, `sysrscols`, `sysschobjs`, `syscolpars`), read them via the page/record layer (Task 5 provides the record decoder — implement the base-table parse here using a minimal inline decoder if Task 5 is not yet done, then refactor to share). Join to produce `Table(name, object_id, columns=[Column(...)], alloc_units=[...])`. The base-table object ids and layouts come from OrcaMDF; **confirm against the fixture** (the recovered table names must equal the known `t_<name>` set). Define dataclasses:
```python
"""Bootstrap system base tables → user-table schema."""
from __future__ import annotations

from dataclasses import dataclass, field

from mssqlbak.pages import PageReader


@dataclass(frozen=True)
class Column:
    name: str
    type_id: int
    max_length: int
    precision: int
    scale: int
    nullable: bool
    leaf_offset: int
    is_variable: bool


@dataclass(frozen=True)
class AllocUnit:
    rowset_id: int
    unit_type: int      # 1=IN_ROW, 2=LOB, 3=ROW_OVERFLOW
    first_page: int
    root_page: int
    first_iam: int


@dataclass
class Table:
    name: str
    object_id: int
    columns: list[Column] = field(default_factory=list)
    alloc_units: list[AllocUnit] = field(default_factory=list)


@dataclass
class Schema:
    tables: list[Table] = field(default_factory=list)


def recover_schema(pr: PageReader) -> Schema:
    """Recover user-table schemas by bootstrapping the system base tables.

    Steps (confirm constants against the fixture):
      1. From the boot page, locate sysallocunits' first page.
      2. Decode sysallocunits, sysrowsets, sysrscols, sysschobjs, syscolpars
         using their hard-coded schemas.
      3. Join: sysschobjs (names) + syscolpars (columns) + sysrscols (column
         storage) + sysrowsets + sysallocunits (page locations).
      4. Return only user tables (object_id >= 100 / not system).
    """
    raise NotImplementedError  # implement per docstring; green against fixture
```

- [ ] **Step 4: Implement and iterate until both tests pass**

Run: `./.venv/bin/pytest tests/test_catalog.py -q`
Expected: PASS. This is the hardest task — iterate using the fixture; the known `t_<name>` names are the reference.

- [ ] **Step 5: Commit**

```bash
git add mssqlbak/catalog.py tests/test_catalog.py
git commit -m "Recover user-table schemas via system base-table bootstrap"
```

---

## Task 5: Record decoder + type system (the value reference)

**Files:**
- Modify: `mssqlbak/records.py`, `mssqlbak/types.py`
- Test: `tests/test_records.py`

- [ ] **Step 1: Write the failing test — decode every matrix value**

```python
from __future__ import annotations

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.mtf import extract_mdf_pages
from mssqlbak.pages import PageReader
from mssqlbak.rows import read_table_rows
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
@pytest.mark.parametrize("case", TYPE_CASES, ids=lambda c: c.name)
def test_decoded_values_match_matrix(fixture_bak, case) -> None:
    pr = PageReader(extract_mdf_pages(fixture_bak))
    schema = recover_schema(pr)
    table = next(t for t in schema.tables if t.name == f"t_{case.name}")
    by_label = {row["label"]: row["v"] for row in read_table_rows(pr, table)}
    for r in case.rows:
        assert by_label[r.label] == r.value, (case.name, r.label)
```

(Note: `read_table_rows` is implemented in Task 6; this test will first fail on import, then on values. Keep it here because record decoding and value correctness are the same concern.)

- [ ] **Step 2: Run to verify failure**

Run: `./.venv/bin/pytest tests/test_records.py -q`
Expected: FAIL — import error for `mssqlbak.rows`.

- [ ] **Step 3: Implement the record decoder**

`mssqlbak/records.py` decodes one record given its bytes + the ordered columns: status byte A → null bitmap → fixed columns (placed by `leaf_offset`, total fixed size = `pminlen`) → variable-column count + offset array → variable columns. Returns `dict[col_name, raw_bytes_or_none]`. `mssqlbak/types.py` converts raw bytes → Python value per `type_id` (the `_decode` functions for each supported type). Skeleton for `types.py`:
```python
"""SQL Server type decoding: raw column bytes → Python value, and Arrow type."""
from __future__ import annotations

import datetime as dt
import decimal
import struct
import uuid

import pyarrow as pa

# SQL Server system type ids (from syscolpars.xtype); confirm against fixture.
TINYINT, SMALLINT, INT, BIGINT, BIT = 48, 52, 56, 127, 104
DECIMAL, NUMERIC, MONEY = 106, 108, 60
REAL, FLOAT = 59, 62
DATE, DATETIME2 = 40, 42
CHAR, VARCHAR, VARCHAR_MAX = 175, 167, 167
NCHAR, NVARCHAR = 239, 231
BINARY, VARBINARY = 173, 165
UNIQUEIDENTIFIER = 36


def decode_int(b: bytes, signed: bool = True) -> int:
    return int.from_bytes(b, "little", signed=signed)


def decode_bit(b: bytes) -> bool:
    return b[0] != 0


def decode_uniqueidentifier(b: bytes) -> uuid.UUID:
    return uuid.UUID(bytes_le=b)


def decode_datetime2(b: bytes, scale: int) -> dt.datetime:
    # time fraction (variable bytes by scale) + 3-byte date (days since 0001-01-01)
    time_len = {0: 3, 1: 3, 2: 3, 3: 4, 4: 4, 5: 5, 6: 5, 7: 5}[scale]
    frac = int.from_bytes(b[:time_len], "little")
    days = int.from_bytes(b[time_len:time_len + 3], "little")
    base = dt.datetime(1, 1, 1)
    micro = frac // (10 ** (scale - 6)) if scale > 6 else frac * (10 ** (6 - scale))
    return base + dt.timedelta(days=days, microseconds=micro)


# ... decode_decimal, decode_float, decode_char(codepage), decode_nvarchar, etc.
```
Implement each `decode_*` so the Task 5 test passes for that type. Add the Arrow-type mapping function `arrow_type(col) -> pa.DataType` for Task 7.

- [ ] **Step 4: Iterate per type until all parametrized cases pass**

Run: `./.venv/bin/pytest tests/test_records.py -q`
Expected: each `test_decoded_values_match_matrix[<name>]` PASS. Fix one type at a time.

- [ ] **Step 5: Commit**

```bash
git add mssqlbak/records.py mssqlbak/types.py tests/test_records.py
git commit -m "Decode records and all v1 SQL Server types against the fixture"
```

---

## Task 6: Row orchestrator (heap + clustered, LOB/row-overflow)

**Files:**
- Modify: `mssqlbak/rows.py`
- Test: covered by Task 5's `test_records.py` (it imports `read_table_rows`)

- [ ] **Step 1: Implement `read_table_rows`**

```python
"""Per-table row orchestration: alloc units → pages → records → typed rows."""
from __future__ import annotations

from collections.abc import Iterator

from mssqlbak.catalog import Table
from mssqlbak.pages import PageReader
from mssqlbak.records import decode_record


def _data_pages(pr: PageReader, table: Table) -> Iterator[int]:
    """Yield data page ids for the table's IN_ROW alloc unit.

    Heap: follow the IAM page chain. Clustered index: descend to the leftmost
    leaf, then follow next_page. Confirm IAM/leaf traversal against the fixture.
    """
    ...


def read_table_rows(pr: PageReader, table: Table) -> Iterator[dict]:
    for pid in _data_pages(pr, table):
        for off in pr.slot_offsets(pid):
            raw = pr.raw(pid)
            yield decode_record(raw, off, table.columns, pr)
```

`decode_record` resolves LOB / row-overflow pointers by calling back into `pr` to fetch the referenced pages and stitch the value (full size in production; the fixture's 1 MB blob exercises this).

- [ ] **Step 2: Run Task 5's full suite**

Run: `./.venv/bin/pytest tests/test_records.py -q`
Expected: all type cases PASS, including `varbinary_max` (1 MB LOB) and `varchar_max`.

- [ ] **Step 3: Commit**

```bash
git add mssqlbak/rows.py
git commit -m "Add row orchestrator with heap/clustered + LOB traversal"
```

---

## Task 7: Delta sink + engine-diff test

**Files:**
- Modify: `mssqlbak/sink.py`
- Test: `tests/test_sink.py`, `tests/test_engine_diff.py`

- [ ] **Step 1: Write the failing sink test**

```python
from __future__ import annotations

import pyarrow as pa
from deltalake import DeltaTable

from mssqlbak.sink import DeltaSink


def test_sink_writes_readable_delta(tmp_path) -> None:
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([("id", pa.int32()), ("label", pa.string())])
    sink.open_table("dbo.t_int", schema)
    sink.write_batch(pa.record_batch([[1, 2], ["low", "high"]], schema=schema))
    sink.close()
    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t_int"))
    assert dt.to_pyarrow_table().num_rows == 2
```

- [ ] **Step 2: Run to verify failure**

Run: `./.venv/bin/pytest tests/test_sink.py -q`
Expected: FAIL — import error.

- [ ] **Step 3: Implement `DeltaSink`**

```python
"""Delta output sink (deltalake/delta-rs implementation of the Sink protocol)."""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
from deltalake import write_deltalake


class DeltaSink:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._path: Path | None = None
        self._schema: pa.Schema | None = None
        self._first = True

    def open_table(self, qualified_name: str, schema: pa.Schema) -> None:
        schema_name, _, table = qualified_name.partition(".")
        self._path = self._root / schema_name / table
        self._schema = schema
        self._first = True

    def write_batch(self, batch: pa.RecordBatch) -> None:
        assert self._path is not None and self._schema is not None
        write_deltalake(
            str(self._path), pa.Table.from_batches([batch], schema=self._schema),
            mode="overwrite" if self._first else "append",
        )
        self._first = False

    def close(self) -> None:
        self._path = None
        self._schema = None
```

- [ ] **Step 4: Run sink test**

Run: `./.venv/bin/pytest tests/test_sink.py -q`
Expected: PASS.

- [ ] **Step 5: Write the engine-diff test (Test B)**

`tests/test_engine_diff.py` restores the same fixture into a container and compares the engine's query results to the parser output, row-for-row, for every table. Marked `@pytest.mark.fixture` and `@pytest.mark.engine` (skipped without `mssql_python` + podman).
```python
from __future__ import annotations

import pytest

mssql_python = pytest.importorskip("mssql_python")

from mssqlbak.catalog import recover_schema
from mssqlbak.mtf import extract_mdf_pages
from mssqlbak.pages import PageReader
from mssqlbak.rows import read_table_rows
from tools.typematrix import TYPE_CASES
# Helper restore_fixture_and_connect() spins up a container, RESTORE, returns conn.
from tests.engine_support import restore_fixture_and_connect


@pytest.mark.fixture
@pytest.mark.engine
@pytest.mark.parametrize("case", TYPE_CASES, ids=lambda c: c.name)
def test_parser_matches_engine(fixture_bak, case) -> None:
    conn = restore_fixture_and_connect(fixture_bak)
    cur = conn.cursor()
    cur.execute(f"SELECT label, v FROM t_{case.name} ORDER BY id")
    engine = {row[0]: row[1] for row in cur.fetchall()}
    pr = PageReader(extract_mdf_pages(fixture_bak))
    table = next(t for t in recover_schema(pr).tables if t.name == f"t_{case.name}")
    parsed = {r["label"]: r["v"] for r in read_table_rows(pr, table)}
    assert parsed == engine
```

- [ ] **Step 6: Implement `tests/engine_support.py`** (live-engine connection helper)

A helper mirroring `tools/make_fixture.py`'s container handling: copy the `.bak` into a fresh container, `RESTORE DATABASE … WITH MOVE`, return an `mssql_python` connection. Reuse `restore_from_bak` logic where possible (DRY).

- [ ] **Step 7: Run the engine diff**

Run: `./.venv/bin/pytest tests/test_engine_diff.py -q`
Expected: all cases PASS (parser == engine). Differences here are real parser bugs — fix the decoder, not the test.

- [ ] **Step 8: Commit**

```bash
git add mssqlbak/sink.py tests/test_sink.py tests/test_engine_diff.py tests/engine_support.py
git commit -m "Add Delta sink and engine-diff test"
```

---

## Task 8: End-to-end CLI (`extract`) + wiring

**Files:**
- Modify: `mssqlbak/_cli.py`, `mssqlbak/__init__.py`
- Create: `mssqlbak/extract.py`
- Test: `tests/test_extract_e2e.py`

- [ ] **Step 1: Write the failing end-to-end test**

```python
from __future__ import annotations

import pytest
from deltalake import DeltaTable

from mssqlbak.extract import extract_bak_to_delta
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
def test_extract_writes_all_tables(fixture_bak, tmp_path) -> None:
    extract_bak_to_delta(fixture_bak, tmp_path / "delta")
    for case in TYPE_CASES:
        dt = DeltaTable(str(tmp_path / "delta" / "dbo" / f"t_{case.name}"))
        assert dt.to_pyarrow_table().num_rows == len(case.rows)
```

- [ ] **Step 2: Run to verify failure**

Run: `./.venv/bin/pytest tests/test_extract_e2e.py -q`
Expected: FAIL — import error.

- [ ] **Step 3: Implement `extract_bak_to_delta`**

```python
"""End-to-end: .bak → Delta tables."""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa

from mssqlbak.catalog import recover_schema
from mssqlbak.mtf import extract_mdf_pages
from mssqlbak.pages import PageReader
from mssqlbak.rows import read_table_rows
from mssqlbak.sink import DeltaSink
from mssqlbak.types import arrow_schema_for

BATCH = 10_000


def extract_bak_to_delta(bak: str | Path, out: str | Path) -> None:
    pr = PageReader(extract_mdf_pages(bak))
    schema = recover_schema(pr)
    sink = DeltaSink(out)
    for table in schema.tables:
        arrow_schema = arrow_schema_for(table)
        sink.open_table(f"dbo.{table.name}", arrow_schema)
        buf: list[dict] = []
        for row in read_table_rows(pr, table):
            buf.append(row)
            if len(buf) >= BATCH:
                sink.write_batch(_to_batch(buf, arrow_schema))
                buf.clear()
        if buf:
            sink.write_batch(_to_batch(buf, arrow_schema))
        sink.close()


def _to_batch(rows: list[dict], schema: pa.Schema) -> pa.RecordBatch:
    cols = {name: [r.get(name) for r in rows] for name in schema.names}
    return pa.record_batch([cols[n] for n in schema.names], schema=schema)
```

- [ ] **Step 4: Add the CLI subcommand**

In `mssqlbak/_cli.py`, add `mssqlbak extract <file.bak> --out <dir>` that calls `extract_bak_to_delta`; keep the existing metadata print as the default/`info` command. Export `extract_bak_to_delta` from `mssqlbak/__init__.py`.

- [ ] **Step 5: Run e2e + full suite + tooling**

Run: `./.venv/bin/pytest -q && ./.venv/bin/ruff check . && ./.venv/bin/pyright`
Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add mssqlbak/extract.py mssqlbak/_cli.py mssqlbak/__init__.py tests/test_extract_e2e.py
git commit -m "Add end-to-end extract CLI: .bak to Delta"
```

---

## Task 9: Docs + limitations

**Files:**
- Modify: `README.md`, `DESIGN.md`

- [ ] **Step 1: Document the `extract` workflow, supported types, and the detect-and-fail boundaries (compression/TDE, deferred types).** Note the `datetime2(7)`→µs truncation explicitly.

- [ ] **Step 2: Commit**

```bash
git add README.md DESIGN.md
git commit -m "Document bak-to-delta extract workflow and limitations"
```

---

## Self-Review (completed during authoring)

- **Spec coverage:** mtf (T2), pages (T3), catalog (T4), records+types (T5), rows incl. LOB (T6), sink+engine diff (T7), CLI/e2e (T8); type-coverage fixture incl. 1 MB blob (T1); detect-and-fail + datetime2 truncation (T5/T9). Differential and CDC are out of v1 scope per spec.
- **Placeholder scan:** byte-offset details intentionally defer to fixture-driven verification with a cited reference (OrcaMDF) — this is a research boundary, not a placeholder; every such task has an objective pass condition (known fixture values).
- **Type consistency:** `extract_mdf_pages`, `PageReader`, `recover_schema`, `Table`/`Column`/`AllocUnit`, `read_table_rows`, `decode_record`, `DeltaSink.open_table/write_batch/close`, `arrow_schema_for`/`arrow_type` are used consistently across tasks.

## Known research risk

Tasks 3–6 depend on reverse-engineered MDF layouts. The plan front-loads the fixture (T1) and treats the boot/page spike (T2–T3) as the gating de-risk step: if page-header and slot offsets cannot be made to match the fixture, stop and re-spike before T4+. The engine diff (T7) is the final backstop that proves byte-level correctness against the engine.
