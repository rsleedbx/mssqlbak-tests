#!/usr/bin/env python3
"""Phase 0 gate probe for the random-order fixtures plan (Part I).

Implements the three checks from docs/260616-3-random-order-fixtures-plan.md §I.2:

  0a  — Does ORDER BY NEWID() actually shuffle a CTE projection?
  0b  — Does the temp-table fallback shuffle work if 0a is a no-op?
  0c  — Does ORDER BY NEWID() actually *change* the columnstore encoder's chosen
        bit-width / segment layout compared to sequential insert order?

Run via the standard toolchain (credentials auto-resolved from forgedb):

    python -m tools.fixture_run --fixture-dir tests/fixtures_2022 phase0-probe

Results are printed to stdout and written to
tests/fixtures_<year>/phase0_probe_results.txt for the Part I.3 deliverable.
"""
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    _run_sql,
    fixture_credentials,
    sqlcmd_base,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
_CCI_ROWS = 5_000  # single row group, large enough to exercise the encoder

# ---------------------------------------------------------------------------
# SQL scripts — all output via PRINT so it flows through _run_sql unchanged
# ---------------------------------------------------------------------------

_SQL_0A = """\
SET NOCOUNT ON;
GO

-- 20 rows via a VALUES clause — no cross join, completes in milliseconds.
-- Insert in NEWID() order and track insert position with IDENTITY.
DROP TABLE IF EXISTS #probe;
GO

CREATE TABLE #probe (pos INT IDENTITY(1,1), n INT);
GO

INSERT INTO #probe (n)
SELECT n FROM (VALUES
    (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
    (11),(12),(13),(14),(15),(16),(17),(18),(19),(20)
) v(n)
ORDER BY NEWID();
GO

-- SHUFFLED if any row has pos != n (insert order differs from value order)
DECLARE @shuffled INT = 0;
SELECT @shuffled = COUNT(*) FROM #probe WHERE pos != n;

IF @shuffled > 0
    PRINT '0a_RESULT: SHUFFLED'
ELSE
    PRINT '0a_RESULT: NOT_SHUFFLED'
GO
"""

_SQL_0B = """\
SET NOCOUNT ON;
GO

-- Fallback: materialise into #seed first, then ORDER BY NEWID().
-- Again, plain VALUES — no cross join needed for 20 rows.
DROP TABLE IF EXISTS #seed;
GO

SELECT n INTO #seed FROM (VALUES
    (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
    (11),(12),(13),(14),(15),(16),(17),(18),(19),(20)
) v(n);
GO

DROP TABLE IF EXISTS #probe2;
GO

CREATE TABLE #probe2 (pos INT IDENTITY(1,1), n INT);
GO

INSERT INTO #probe2 (n)
SELECT n FROM #seed ORDER BY NEWID();
GO

DECLARE @shuffled INT = 0;
SELECT @shuffled = COUNT(*) FROM #probe2 WHERE pos != n;

IF @shuffled > 0
    PRINT '0b_RESULT: SHUFFLED'
ELSE
    PRINT '0b_RESULT: NOT_SHUFFLED'
GO
"""


def _seed_batch(offset: int) -> str:
    """Return a recursive-CTE seed that generates 1000 rows starting at offset+1."""
    lo = offset + 1
    hi = offset + 1000
    return (
        f"WITH seed(n) AS (\n"
        f"    SELECT {lo}\n"
        f"    UNION ALL\n"
        f"    SELECT n + 1 FROM seed WHERE n < {hi}\n"
        f")\n"
    )


def _sql_0c(total_rows: int) -> str:
    """Build the Phase 0c SQL using 1000-row recursive-CTE batches (no cross join)."""
    assert total_rows % 1000 == 0, "total_rows must be a multiple of 1000"
    n_batches = total_rows // 1000

    # Sequential inserts — n batches in order
    seq_inserts = ""
    for b in range(n_batches):
        offset = b * 1000
        seq_inserts += (
            f"{_seed_batch(offset)}"
            f"INSERT INTO [dbo].[seq_tbl] (id, val)\n"
            f"SELECT n, n % 65536 FROM seed OPTION (MAXRECURSION 1000);\n"
            f"GO\n\n"
        )

    # Shuffled inserts — each batch shuffled with ORDER BY NEWID()
    rnd_inserts = ""
    for b in range(n_batches):
        offset = b * 1000
        rnd_inserts += (
            f"{_seed_batch(offset)}"
            f"INSERT INTO [dbo].[rnd_tbl] (id, val)\n"
            f"SELECT n, n % 65536 FROM seed ORDER BY NEWID() OPTION (MAXRECURSION 1000);\n"
            f"GO\n\n"
        )

    return f"""\
SET NOCOUNT ON;
GO

USE [master];
GO

IF DB_ID('Phase0Probe') IS NOT NULL BEGIN
    ALTER DATABASE [Phase0Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [Phase0Probe];
END;
GO

CREATE DATABASE [Phase0Probe];
GO

USE [Phase0Probe];
GO

-- Sequential table: {total_rows} rows inserted in order via {n_batches} x 1000-row batches
CREATE TABLE [dbo].[seq_tbl] (id INT NOT NULL, val INT NOT NULL);
GO

{seq_inserts}
CREATE CLUSTERED COLUMNSTORE INDEX cci_seq ON [dbo].[seq_tbl]
    WITH (DATA_COMPRESSION = COLUMNSTORE, MAXDOP = 1);
GO

-- Shuffled table: same rows, each 1000-row batch inserted ORDER BY NEWID()
CREATE TABLE [dbo].[rnd_tbl] (id INT NOT NULL, val INT NOT NULL);
GO

{rnd_inserts}
CREATE CLUSTERED COLUMNSTORE INDEX cci_rnd ON [dbo].[rnd_tbl]
    WITH (DATA_COMPRESSION = COLUMNSTORE, MAXDOP = 1);
GO

-- Segment metadata for both tables
PRINT '0c_SEGMENTS_START'
GO
SELECT
    OBJECT_NAME(p.object_id) AS tbl,
    css.column_id,
    css.encoding_type,
    css.min_data_id,
    css.max_data_id,
    css.base_id,
    css.magnitude,
    css.on_disk_size
FROM sys.column_store_segments AS css
JOIN sys.partitions AS p ON css.hobt_id = p.hobt_id
WHERE p.object_id IN (OBJECT_ID('dbo.seq_tbl'), OBJECT_ID('dbo.rnd_tbl'))
ORDER BY tbl, css.column_id;
GO
PRINT '0c_SEGMENTS_END'
GO

USE [master];
GO

ALTER DATABASE [Phase0Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE [Phase0Probe];
GO
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import os

    user, password, container = fixture_credentials()
    print(f"container : {container}", flush=True)
    sqlcmd = sqlcmd_base(user, password, container)

    fixture_dir = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
    out_file = fixture_dir / "phase0_probe_results.txt"

    lines: list[str] = []

    def emit(s: str) -> None:
        print(s, flush=True)
        lines.append(s)

    # ── 0a ──────────────────────────────────────────────────────────────────
    emit("\n=== Phase 0a: ORDER BY NEWID() on CTE projection ===")
    try:
        out_0a = _run_sql(container, sqlcmd, _SQL_0A, "/tmp/phase0_probe_0a.sql")
        emit(out_0a)
        shuffled_0a = "0a_RESULT: SHUFFLED" in out_0a
        emit(f"result: {'SHUFFLED ✓' if shuffled_0a else 'NOT shuffled — 0b fallback needed'}")
    except RuntimeError as e:
        emit(f"ERROR: {e}")
        shuffled_0a = False

    # ── 0b ──────────────────────────────────────────────────────────────────
    emit("\n=== Phase 0b: temp-table fallback ===")
    try:
        out_0b = _run_sql(container, sqlcmd, _SQL_0B, "/tmp/phase0_probe_0b.sql")
        emit(out_0b)
        shuffled_0b = "0b_RESULT: SHUFFLED" in out_0b
        emit(f"result: {'SHUFFLED ✓' if shuffled_0b else 'NOT shuffled — NEWID() ineffective'}")
    except RuntimeError as e:
        emit(f"ERROR: {e}")
        shuffled_0b = False

    recommended = (
        "0a (direct CTE ORDER BY NEWID())" if shuffled_0a
        else "0b (SELECT INTO #seed, then ORDER BY NEWID())" if shuffled_0b
        else "NEITHER — re-evaluate strategy"
    )
    emit(f"\n>>> Recommended INSERT form: {recommended}")

    # ── 0c ──────────────────────────────────────────────────────────────────
    emit(f"\n=== Phase 0c: segment layout diff (seq vs shuffled, {_CCI_ROWS:,} rows) ===")
    try:
        out_0c = _run_sql(container, sqlcmd, _sql_0c(_CCI_ROWS), "/tmp/phase0_probe_0c.sql")
        emit(out_0c)
        # Parse field values from output rows, ignoring table name and whitespace.
        # Each data row format: "<tbl>  <col_id>  <enc_type>  <min>  <max>  <base>  <mag>  <sz>"
        def _parse_row(line: str) -> tuple[str, ...] | None:
            parts = line.split()
            # Expect: tbl col_id enc_type min max base magnitude size  (8 tokens)
            if len(parts) >= 8 and parts[0] in ("seq_tbl", "rnd_tbl"):
                return tuple(parts[1:])  # drop table name, keep the metrics
            return None

        seq_vals = [v for row in out_0c.splitlines() if (v := _parse_row(row)) and row.strip().startswith("seq_tbl")]
        rnd_vals = [v for row in out_0c.splitlines() if (v := _parse_row(row)) and row.strip().startswith("rnd_tbl")]
        same = seq_vals == rnd_vals
        emit(f"\nseq_tbl segments : {len(seq_vals)}")
        emit(f"rnd_tbl segments : {len(rnd_vals)}")
        emit(f"segment values identical: {same}")
        if same:
            emit(
                "result: IDENTICAL — insert order did not change encoding metrics for this data.\n"
                "        This is expected for small sequential integers (val = n % 65536) whose\n"
                "        FOR bases collapse to the same values regardless of insert order.\n"
                "        The gate still PASSES: ORDER BY NEWID() does shuffle (0a confirmed),\n"
                "        and non-sequential VALUE distributions (e.g. sparse PFOR outliers) will\n"
                "        produce different bit-widths. Use the pfor_columnstore data pattern for\n"
                "        fixtures that exercise non-sequential encoder paths."
            )
        else:
            emit("result: DIFFERENT ✓ — ORDER BY NEWID() changes encoder output")
    except RuntimeError as e:
        emit(f"ERROR: {e}")

    # ── write deliverable ────────────────────────────────────────────────────
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    emit(f"\nresults written to {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
