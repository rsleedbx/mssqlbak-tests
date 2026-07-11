# mssqlbak decoder — design overview

This directory documents **how the decoder is implemented**, complementing the
format specification in [`docs/spec/`](../spec/00_MASTER.md), which documents
what the bytes mean.

## What is here

| File | Contents |
|---|---|
| [`dependencies.md`](dependencies.md) | Runtime dependencies and what was deliberately hand-rolled instead |
| [`architecture.md`](architecture.md) | Decode pipeline, module map, and Rust / Python split |
| [`quality-attributes.md`](quality-attributes.md) | Performance, simplicity, readability, scalability, availability, observability, and idempotency tradeoffs |
| [`module-boundaries.md`](module-boundaries.md) | Package split map — which flat files were split into sub-packages and why |

## Reading order

1. [`dependencies.md`](dependencies.md) — establishes which third-party
   libraries are load-bearing and which codecs had to be written from scratch.
2. [`architecture.md`](architecture.md) — shows how the modules connect end
   to end from `.bak` bytes to Arrow `RecordBatch`.
3. [`quality-attributes.md`](quality-attributes.md) — explains the tradeoffs
   behind the architectural choices.

## Scope

Coverage is limited to the **read/decode path**
(`reader.py`, `compressed.py`, `mtf.py`, `pages.py`, `catalog/`, `rows.py`,
`records.py`, `rowcompress.py`, `types/`, `columnstore/`, `xtp.py`,
`logtail/`, `extract.py`).

Write targets (`sinks/`, `writers/`, `spark_sink.py`, `bacpac.py`) and the
optional restore path (`mssql_python`) are out of scope here.

## Related

- [`docs/spec/00_MASTER.md`](../spec/00_MASTER.md) — byte-layout format spec
- [`docs/PERFORMANCE_PLAN.md`](../PERFORMANCE_PLAN.md) — performance benchmark targets and measurement methodology
- [`docs/XPRESS_IMPL_HISTORY.md`](../XPRESS_IMPL_HISTORY.md) — XPRESS implementation history
- [`docs/columnstore_algorithm_map.md`](../columnstore_algorithm_map.md) — columnstore encoding algorithm map
- [`docs/decisions/`](../decisions/) — point-in-time decision records
