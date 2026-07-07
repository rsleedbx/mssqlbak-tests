# Offline Confidence Scoring

Offline confidence scoring checks whether a `.bak` is internally consistent with
the rows mssqlbak decodes. It is designed for backups where SQL Server verifier
sidecars are unavailable.

Confidence scoring is weaker than `.stats.json` and `.cells/` verification:

- `.cells/` compares decoded values against a SQL Server restore.
- `.stats.json` compares row, null, and min/max aggregates against a SQL Server restore.
- Confidence scoring compares decoded output against metadata inside the `.bak`.

## Run A Report

```bash
.venv/bin/python -m tools.confidence_report tests/fixtures_realworld/Chinook-id-pk.bak
```

JSON output:

```bash
.venv/bin/python -m tools.confidence_report --json tests/fixtures_realworld/Chinook-id-pk.bak
```

`tools.correctness_coverage` uses confidence scoring when a selected `.bak` has
no `.stats.json` sidecar:

```bash
.venv/bin/python -m tools.correctness_coverage path/to/database.bak --no-write
```

## Current Checks

| Check | Evidence | Meaning |
|-------|----------|---------|
| `file_identity` | SHA-256 of the `.bak` | Identifies the input file used for analysis. |
| `backup_set_selection` | MTF `SSET` descriptor count | Warns when one `.bak` contains multiple backup sets. |
| `catalog_consistency` | schema recovery | Confirms mssqlbak can recover user-table metadata. |
| `page_structure` | data-page traversal and slot reads | Confirms table data pages and slot boundaries are readable. |
| `row_count_consistency` | decoded rows vs `sysrowsets.rcrows` | Confirms decoded table row counts match catalog row counts. |
| `columnstore_metadata_consistency` | decoded rows vs catalog row count | Confirms columnstore row counts match catalog row counts. |

## Interpreting Results

`pass` means the check agreed with internal metadata.

`warn` means the backup has a condition that reduces confidence but does not
prove extraction is wrong. Multiple backup sets in a single `.bak` are a warning
because default SQL Server restore uses `FILE=1`.

`fail` means mssqlbak decoded data that conflicts with recovered metadata, or the
metadata needed for the check could not be read.

## Limits

Confidence scoring does not prove every cell value is correct. Rowstore metadata
mostly validates structure and counts. Columnstore metadata can support stronger
checks because rowgroups and segments store per-column metadata, but value-level
verification still requires `.cells/`.
