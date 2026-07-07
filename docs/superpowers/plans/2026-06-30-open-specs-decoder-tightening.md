# Open-Spec Decoder Tightening Plan

> **For agentic workers:** Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use Microsoft's open specifications (and independent reimplementations of the same borrowed components) to tighten the spec-backed decoders — closing validation gaps, replacing reverse-engineered assumptions with spec-locked reads, and wiring independent verifiers. These are additive hardening/validation changes, not new decode features.

**Premise:** A `.bak` is not a bespoke format. It is a stack of Windows/SQL components Microsoft built for something else first, then reused — most documented in the open `[MS-*]` Open Specifications (or Unicode/OGC/tape standards). Wherever a layer reuses a shared component, that component has an authoritative spec and usually an independent decoder we can use as a verifier (per `.cursor/rules/terminology.mdc`, a *verifier*, never an "oracle").

---

## Borrowed-component lineage (context)

| `.bak` layer | Module | Borrowed from → open spec | Independent verifier |
|--------------|--------|---------------------------|----------------------|
| Outer container | `mtf.py`, `reader.py` | Microsoft Tape Format — *MTF Spec v1.00a* (also NTBackup `.bkf`) | `.bkf` readers |
| Backup compression | `xpress.py` + `rust/` | MS_XPRESS (Xpress Huffman) — `[MS-XCA]` §2.2 (also WIM, NTFS CompactOS, AD repl, RDP) | wimlib, libmspack, kernel `ntfs3` |
| Per-value type bytes | `records.py`, `types.py` | SQL type system — mirrors TDS types in `[MS-TDS]` §2.2.5 | FreeTDS, OrcaMDF |
| Unicode compression | `scsu.py` | SCSU — Unicode TR6 / UTS #6 | Unicode reference expander, OrcaSql |
| Columnstore | `columnstore/decode/*` | xVelocity / VertiPaq (no `[MS-*]`) | **pbixray** (`.pbix`/`.abf`) |
| Binary XML | `xmlbin.py` | SQL Server Binary XML — `[MS-BINXML]` | engine `CAST(col AS nvarchar(max))` |
| `hierarchyid` | `hierarchyid.py` | ORDPATH (SIGMOD 2004); on-disk bits reverse-engineered | dotMorten/Microsoft.SqlServer.Types |
| `geometry`/`geography` | `spatial.py` | CLR UDT serialization; OGC WKT | dotMorten port, engine `.AsTextZM()` |

---

## Empirical findings from the audit

These corrected first-pass assumptions and must be preserved so we plan against reality:

1. **The collation table is already broad.** `types.py:339-354` maps 14 SORTIDs (cp1250–cp1258, cp874, cp932/936/949/950, cp1256), not a 5-entry stub. Item 2 is verification + fallback policy, not a large coverage gap.
2. **The BINXML atomic dispatch is already comprehensive.** `xmlbin.py:281-349` handles strings, binary, bit/boolean, decimal/numeric, all integers, real/float, uuid, money, and every date/time/offset token. Item 1 is spec-verify + validation, not wiring missing tokens.
3. **`sql_variant` is effectively complete.** `types.py:457-497` covers every base type. Item 3 is TDS confirmation + invariant asserts, not new decode paths.
4. **The collation *name* is not stored in the backup.** A UTF-16 scan of fixtures finds `.mdf`/`master`/`model` but zero `Collation`/`_CP1`/`_CI_`/`Latin`. `RESTORE HEADERONLY`'s `Collation` column is *derived by the engine* from a numeric collation id; scraping the name offline (like db/server name) is a dead end.
5. **The offline DB-default collation source is the boot page.** `catalog.py` already reads boot page 9 record 0 (for the `sysallocunits` pointer at offset 516) and already documents the DB-default collation-id format (`catalog.py:79-81`, e.g. `Latin1_General_CI_AS` DB default → `0x3400_D008`). The `DBINFO.dbi_collation` field is one more extraction from a page we already parse.
6. **`reader.py` captures no collation today** (confirmed), and per-column resolution masks the low byte as SORTID, so DB-default ids resolve via their low byte already.
7. **pbixray is a VertiPaq verifier + sample corpus.** `pbixray/vertipaq_decoder.py`, `pbixray/column_data/{dictionary,idf,hidx,idfmeta}.py`, `pbixray/abf/{parser,data_model,mapped_buffer}.py`, plus `data/*.pbix` and `DataModel_uncompressed.abf`. Caveat: VertiPaq wraps columns in XPRESS9/XPRESS8/xmhuffman (per its `requirements.txt`), which differ from `.bak` MS-XCA framing — so it is a **logic verifier + sample source for the shared encodings**, not a byte-identical oracle.

---

## Decision log

- **Unknown collation SORTID:** decode as cp1252 (behavior unchanged) but flag **low confidence** via a report-level `confidence.py` check. `confidence.py` operates on decoded Arrow columns per-`.bak` (report level), not per-value — so this is a new `ConfidenceCheck`, not a per-cell signal.

---

## Files

- Modify: `mssqlbak/xmlbin.py` — decimal precision-byte grounding; atomic-token coverage audit + citations
- Modify: `mssqlbak/types.py` — collation helper; TDS citations + numeric invariant asserts
- Modify: `mssqlbak/records.py` — TDS-backed invariant asserts on numeric/temporal layouts
- Modify: `mssqlbak/confidence.py` — `collation_codepage` report check
- Modify: `mssqlbak/catalog.py` — boot-page `dbi_collation` extraction (`read_dbi_collation`, offset 392) + `Schema.db_collation_id` + collation_id==0 inheritance
- Modify: `mssqlbak/reader.py` — MTF header checksum + `MTF_TAPE_ADDRESS` bounds validation
- Modify: `mssqlbak/confidence.py` — `db_collation` DB-default check (surfacing point; `inspect.py` has no CLI print path)
- Create: `tests/` cross-checks — BINXML decimal, collation verifier, pbixray VertiPaq logic verifier

---

## Item 1: `[MS-BINXML]` hardening (`xmlbin.py`)

**End state:** `_decimal_str` reads and validates the precision byte per spec; the atomic-token set is verified complete against the spec table; malformed operands fail loud instead of rendering plausible-wrong values.

- [x] **Re-ground `_decimal_str`** (`xmlbin.py:171-189`): it currently reads `scale`/`sign` but ignores the precision byte (`raw[pos]`). Read precision; assert `1 ≤ precision ≤ 38`, `0 ≤ scale ≤ precision`, `sign ∈ {0,1}`. Replace the "reverse-engineered" docstring with a `[MS-BINXML]` decimal-production citation.
- [x] **Audit the atomic-value token table** against constants (`xmlbin.py:80-110`). Confirm no token SQL Server can emit to `xml` storage falls through to the `NotImplementedError` at `xmlbin.py:347`. Document which spec tokens are intentionally unreachable. (`test_every_atomic_token_is_decoded` guards this.)
- [x] **Keep FC/FD/FE (`DOCTYPE`/`ENCODING`/`XMLDECL`) as explicit fail-loud** (`xmlbin.py:75-77`, dispatch `467`); add a one-line spec citation rather than implementing (SQL never writes them).
- [x] **Test:** decimal precision/scale/sign edge tests in `tests/test_xml_coverage.py` (`test_decimal_*`, valid + bad-precision/scale/sign).

---

## Item 2: Collation code-page tightening (`types.py`, `confidence.py`, `catalog.py`)

**End state:** the DB-default collation is recovered offline from the boot page and surfaced; unknown SORTIDs still decode as cp1252 but raise a report-level low-confidence warning; the SORTID table is verified against a live engine.

- [x] **2a — Verify existing rows** (`types.py:339-354`) against `sys.fn_helpcollations` sort-order IDs + Windows code-page assignments. Rows fixture-verified via `unicode_codepage_coverage.bak` (G55, resolved); the live-engine cross-check landed with 2d — the container default `SQL_Latin1_General_CP1_CI_AS` and a synthesized `COLLATE Greek_CI_AS` DB both resolve to the `_SORTID_TO_CODEC`-predicted code page (cp1252 / cp1253) matching `COLLATIONPROPERTY(...,'CodePage')`.
- [x] **2b — Confidence check.** Added `is_known_collation_sortid(collation_id) -> bool` in `types.py` (masks the UTF-8 flag + low byte) and a `collation_codepage` check in `confidence.py`'s `analyze_bak` per-table loop that emits `Severity.WARN` (column + SORTID in `evidence`) for unknown SORTIDs, `PASS` otherwise. `_codec_for_collation` still returns cp1252 for unknown (unchanged). Guarded by `TestCollationCodepage` in `tests/test_constraint_checks.py`.
- [x] **2c — Boot-page `dbi_collation` (G57, [CONFIRMED]).** `catalog.read_dbi_collation` reads the DB-default collation id as a uint32 LE at boot-page 9 record 0 offset **392** (`_DBI_COLLATION_OFF`). Offset located by scanning the boot record for the live-engine collation id and confirmed unique across SS2017–SS2025. Exposed on `Schema.db_collation_id`; string columns whose own `syscolpars.collationid` is 0 now inherit it (before the blind cp1252 fallback); `confidence.py` gained a `db_collation` check (PASS/WARN on known/unknown default SORTID). (Note: `inspect.py` is a support module with no CLI print path, so DB-default surfacing lives in `confidence.py` + `Schema` rather than `inspect.py`.)
- [x] **2d — Verifier.** Live-engine (`forgedb` SS2017/2019/2022/2025) cross-check instead of `RESTORE HEADERONLY` (whose `Collation` is the *derived name*, not the stored id): `COLLATIONPROPERTY(SERVERPROPERTY('Collation'),'CollationID')` = `0x3400D008` = boot-page offset 392 on all four versions; a `CREATE DATABASE … COLLATE Greek_CI_AS` backup stores `0x0000D007` there, proving the field tracks the actual DB collation. Encoded as `tests/test_dbi_collation.py::test_dbi_collation_matches_live_engine` (`@pytest.mark.engine`, skips offline; passed live against the 2022 engine).

**Caveat:** mapping collation id → full *name* offline needs a large lookup (`sys.fn_helpcollations` ≈ 5,500 rows); ship only the common subset for display and rely on the code page for decoding.

---

## Item 3: `[MS-TDS]` §2.2.5 confirmation + invariants (`types.py`, `records.py`)

**End state:** numeric/temporal byte layouts carry spec citations and domain asserts; `sql_variant`'s base-type set is asserted complete against the TDS enumeration.

- [x] **Cross-check byte layouts** against `[MS-TDS]` TYPE_INFO: `decimal`/`numeric` (sign+scale+mantissa, §2.2.5.5.1.2), `datetimeoffset` (scale + tz minutes, §2.2.5.5.1.5), `money`/`smallmoney` scaling (§2.2.5.5.1.1). Citations added to the decoder docstrings in `types.py`.
- [x] **Add domain asserts** to the numeric/temporal decoders so corruption fails loud: `_decode_decimal` (scale 0–38, sign ∈ {0,1}); `_decode_datetimeoffset` (tz ±840 min); `datetime2`/`time` scale 0–7 already fails loud via the `_DT2_TIME_LEN` KeyError (now documented).
- [x] **Assert `sql_variant` completeness** (`types.py`): added `_VARIANT_BASE_TYPES` frozenset pinning the [MS-TDS] §2.2.5 base-type surface, cited in `_decode_sql_variant`. Guarded both directions by `test_sql_variant_*` in `tests/test_tds_invariants.py`. No new decode paths.
- [x] **Add spec citations** to `_decode_sql_variant` and the numeric decoders (mirrors `xpress.py`/`scsu.py`).
- [x] **Verified** against the full fixture suite: type/columnstore coverage (561 passed each on 2017/2019/2022/2025) + `test_stats.py` (144 passed) — no valid fixture trips a new assert. New unit tests: `tests/test_tds_invariants.py` (9 passed).

---

## Item 4: MTF descriptor validation (`reader.py`)

**End state:** malformed/truncated MTF descriptors fail loud rather than mis-read.

- [x] **Validate the 52-byte common-block header**: added `_common_header_checksum_ok` (MTF Spec v1.00a — XOR of all 26 header words == 0, verified against the fixture matrix: 1059/1060 headers XOR to 0, the sole exception being the intentionally-corrupt `corrupt_metadata_confidence` fixture). `_read_metadata_blocks` skips a TAPE/SSET whose checksum fails rather than mis-reading it; with no valid descriptor, `read_bak_metadata` raises (fail-loud boundary).
- [x] **Bounds-check `MTF_TAPE_ADDRESS` pointers** in `_resolve_addr`: already present (`offset + size > len(block)` guard); added the MTF_TAPE_ADDRESS citation to the docstring.
- [x] **Leave the proprietary name heuristics unchanged**; added a comment that no open spec covers the appended SQL Server config stream (`_extract_db_files`).
- [x] **Tests:** `test_common_header_checksum_*` and `test_read_bak_skips_descriptor_with_bad_checksum` in `tests/test_reader.py`; the synthetic `.bak` builder now writes a spec-correct checksum. Verified: reader tests pass on 2017/2019/2022/2025; the 2017 `test_real_fixture_metadata` failure is a pre-existing version-specific `server_name` extraction quirk (reproduces on HEAD).

---

## Item 5: pbixray VertiPaq verifier (test infra)

**End state:** an independent implementation of the xVelocity/VertiPaq encodings cross-checks our `columnstore/decode/*` logic, with a non-SQL-Server sample corpus.

- [x] **Add `pbixray` as a dev/test-only dependency** (never in the runtime decode path): added the `verify` optional-dependency group in `pyproject.toml` (`kaitaistruct`, `xpress9`, `xpress8`, `apsw`, `numpy`, `pandas`); pbixray itself is loaded from a local checkout (`PBIXRAY_PATH` env or `~/github/pbixray`). Verified the `vertipaq_decoder` import chain does **not** need the SQL/xpress path (`apsw`/`xpress9/8` are only in `meta/sqlite_source.py`), only kaitai + numpy + xmhuffman.
- [x] **Algorithm-level cross-check test:** `tests/test_pbixray_verifier.py` cross-checks mssqlbak's `bitpack.py` (`_bitpack_values`) against pbixray's independent `VertiPaqDecoder._read_bitpacked` — the shared xVelocity primitive (LSB-first, `64 // bpv` values per 64-bit word) — across bit widths 1..63 (19 passed), plus a frame-of-reference base check (our `_bp_for_base` vs pbixray's `min_data_id`).
- [x] **Sample-corpus + dictionary/RLE cross-checks** (`dict_string.py`, `dict_numeric.py`, `dict_xvelocity.py`, `data/*.pbix`, `.abf`): completed across Groups B–E.
  - *Group B* (5b): `_decode_enc3` compact-RLE, direct-bitpack, and hybrid modes against a pure-Python `_ref_idf_decode` reference (offline).
  - *Group C* (5c): Adventure Works DW 2020 integer column IDF decode end-to-end vs pbixray's `_read_rle_bit_packed_hybrid`.
  - *Group D* (5d): `_parse_numeric_dict_{int,float}` synthetic `.bak`-format blob roundtrips; format-difference note documents why `.pbix` numeric dict cross-format verification is intentionally excluded.
  - *Group E* (5e): `_huff_decode_page_py` (mssqlbak's pure-Python Huffman fallback for `dict_xvelocity.py`) verified byte-for-byte against `xmhuffman.decode_page` on all 8 compressed string pages from the Adventure Works DW 2020 `.pbix` (191 489 strings, 0 mismatches).  Character-encoding differences (UTF-16LE vs `.bak` latin-1 with chr(b−2)) are caller-side and excluded from this test.
- [x] **Document the caveat:** captured in the test-module docstring — VertiPaq's XPRESS9/XPRESS8/xmhuffman container differs from `.bak` MS-XCA framing; pbixray is a logic verifier + sample source, not a byte-identical oracle. The test compares *decoded* bit-pack output, not raw container bytes.

---

## Bugs this would have prevented (evidence from git history)

Each plan item maps to a real, already-fixed bug. This is the concrete "we could have prevented / caught X earlier" case for doing the work up front.

| Plan item | Past bug (commit) | Nature | How the plan addresses it |
|-----------|-------------------|--------|---------------------------|
| 1 — BINXML token audit | `b75f8fd` "implement all missing atomic-value token types" | Silent skip — 11 tokens raised `NotImplementedError`, whole tables with those XML values were skipped | Auditing the `[MS-BINXML]` atomic-value token table up front yields full coverage in one pass instead of reactive per-token fixes |
| 2 — collation confidence + id-format verify | `ebc01e7` "two silent corruption bugs for per-column non-UTF-8 collations (Gap G-3)" | **Silent corruption** — Greek/Hebrew/Arabic decoded as CP1252; AE threshold nulled CI-collation columns | The `collation_codepage` WARN surfaces unverified code pages instead of shipping plausible-wrong text; 2a verifies the collation-id bit layout against `sys.fn_helpcollations` |
| 3 — TDS temporal/numeric invariants | `de82feb` "round classic datetime to whole ms"; `619cf94` float precision | Wrong values — raw truncated ticks never matched any SQL Server client | Pinning `datetime` (days + 1/300s ticks, ms-rounded) and numeric layouts to `[MS-TDS]` semantics + domain asserts surfaces the rule at implementation time |
| 4 — MTF/XPRESS fail-loud validation | `8df3d63` "XPRESS infinite loop on false-positive headers"; `ca33c7b` "MTF checkpoint-block gap bridging" | Hang / mis-read — garbage chunk header passing the Kraft test spun forever | Spec-derived bounds (MS-XCA chunk semantics) + MTF header checksum / `MTF_TAPE_ADDRESS` bounds make malformed input fail loud |
| 5 — pbixray VertiPaq verifier | `d633fe6`, `2306e0d`, `ec7ebd2`, `be4335d`, `6cc5b1c`, `c032a8d` (columnstore fix cluster) | Reactive — dictionary/bit-pack/RLE bugs found one `.bak` fixture variant at a time | An independent VertiPaq decoder cross-checks the shared encoding logic on `.pbix`/`.abf` samples, catching errors before a matching fixture exists |

Cross-cutting: `57e9219` "correct value decoding across codepage/columnstore/compressed paths" touched Item 2 (codepage) **and** Item 5 (columnstore) in one commit.

**Strongest cases:**
- *Would have prevented:* Item 2 / `ebc01e7` — a silent data-corruption bug an existing confidence check would have flagged rather than emitting wrong text.
- *Would have found far earlier:* Item 1 / `b75f8fd` — reading the `[MS-BINXML]` token table once replaces a string of reactive per-token fixes.

---

## Sequencing & risk

Order: 1 → 2 → 3 → 4, with 5 alongside future columnstore work. All changes are additive validation or test-only, so regression risk is low — but each fail-loud assert (items 1, 3, 4) must be run against the full fixture suite (`tools.fixture_run` coverage) to confirm no currently-passing fixture trips a new assertion.
