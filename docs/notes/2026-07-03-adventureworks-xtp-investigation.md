# AdventureWorks2016_EXT XTP Block Investigation (2026-07-03 → 07-04)

## Update (2026-07-05 — SOH fully landed; XPRESS v2 overlap fixed)

`Sales.SalesOrderHeader_inmem` now lands byte-exact and complete:
31,465/31,465 rows, `tools/diag/_diag_xtp_soh_diff.py` reports
`mismatch counts: {}`, and `tests/test_value_correctness.py -k
AdventureWorks2016_EXT` passes.

The residual SOH failure was not an XTP row-layout bug and was not data loss in
the checkpoint DATA stream. It was a MSSQLBAK v2 container slicing bug in the
XPRESS demux:

- v2 record chaining uses `next_h = H + 28 + comp_size`.
- the XPRESS Huffman stream starts at `H + 32`.
- therefore the stream's final dword overlaps the next record's leading size
  dword; slicing only through `next_h + 2` truncated the final coding unit by two
  bytes.

That truncation corrupted the final ~33 decompressed bytes of a 64 KB extent.
For SOH, the affected bytes are the first fixed fields of boundary-straddling
records (`OrderDate`, `DueDate`, `ShipDate`, etc.). The fixed demux slices the
full `comp_size` bytes from the Huffman-table start, and the regression vector in
`tests/vectors/xpress_soh_final_unit_seq9839.bin` locks this boundary down.

Fixture takeaway: our synthetic `xtp_checkpoint_straddle_full.bak` stresses XTP
checkpoint preamble/straddle recovery, but its simple `REPLICATE(N'x', width)`
payload did not reproduce AdventureWorks' XPRESS final-unit shape. The
AdventureWorks SOH rows are more heterogeneous and include repeated fixed
date/value patterns that the compressor encoded into a boundary-sensitive final
unit. For this bug, the raw XPRESS vector is the reliable regression; more SQL
Server XTP fixtures can add corroboration, but they should not replace the
codec-level vector because reproducing a specific compressor bitstream from T-SQL
data shape alone is low-yield.

## Update (2026-07-04 late — variable-column layout + null-bitmap size + SOH residual)

Two XTP-layout decode bugs were fixed, landing three more tables byte-exact, and
the sole remaining table (`Sales.SalesOrderHeader_inmem`) was root-caused to a
decompressor bug (not an XTP-layout bug).

1. **Variable-offset array has an explicit start (not an implicit one).** The
   post-fixed variable-offset array is `[2B start][nvar × 2B end]`, where the
   first `u16` is the explicit start of the variable-data region (the array may be
   followed by reserved padding before the data begins). The old code assumed
   `nvar` end offsets with an *implicit* start at `fw + 2 + 2·nvar`, which shifted
   every variable column by one slot (SpecialOffer/Product decoded
   `Description`/`Type`/`Category` off-by-one; SOD's `CarrierTrackingNumber` was
   garbled). Fixed in `_decode_payload` and `_xtp_var_record_consistent`.

2. **Null bitmap is `ceil(n_nullable/8)` bytes, and the offset array is 2-byte
   aligned.** The bitmap has one bit per *nullable* column — **not** `ceil(ncol/8)`.
   For `SalesOrderHeader_inmem` (23 cols, 8 nullable, odd `fw=95`) the bitmap is 1
   byte and the offset array starts at the next even offset (96), with a one-byte
   pad. The old hard-coded 2-byte skip mis-located the array for any table whose
   `fw + bitmap` was odd, so SOH failed the consistency check entirely and was
   *absent* from decode. Fixed via `_xtp_null_bitmap_bytes` + `_xtp_var_array_offset`.

   After (1)+(2): `SpecialOffer_inmem`, `Production.Product_inmem`, and
   `Sales.SalesOrderDetail_inmem` (121,317/121,317) are byte-exact.

3. **SOH residual — an XPRESS decompressor bug, not XTP.** SOH decodes byte-exact
   except ~5 rows whose *fixed section* straddles a 64 KB XPRESS **extent**
   boundary. For those extents the decompressor mis-expands the **final coding
   unit** (the last ~33 bytes): the two native decode entry points
   (`decompress` vs `decompress_until_input`) agree for the first 65,503 bytes and
   both produce a *wrong* tail. The correct tail bytes are LZ77 back-references to
   the (constant across all SOH rows) `OrderDate`/`DueDate`/`ShipDate` values, so
   the mis-expanded final matches corrupt exactly those columns (and, for 2 rows,
   `AccountNumber`). This is a bug in the `xpress_lz77` Rust extension, reproduced
   by `tools/diag/_diag_xtp_extent_size.py`.

   Guard: `_seq_complete_rows` now refuses a table if any record decodes a NOT NULL
   column to `None` (`_row_honors_not_null`). 3 of the ~5 corrupt SOH rows decode
   `OrderDate` (NOT NULL) to `None`, so the whole table is safely refused — never
   shipped with a wrong row — until the decompressor is fixed. SOH therefore stays
   in `known_gaps` (the only remaining AdventureWorks XTP skip).

## Finding (current — supersedes all earlier phases)

The row data for all seven memory-optimized (XTP) tables **is present** in the
decompressed stream as **XTP transaction-log insert records** (the log tail plus
the 64 KB XTP checkpoint data chunks), not as compact 4 KB checkpoint blocks and
not as JSON. **Five** of the seven tables are now **fully decoded and landed**
(byte-exact + complete vs ground truth): `Sales.SpecialOffer_inmem` (16),
`Demo.DemoSalesOrderDetailSeed` (538), `Demo.DemoSalesOrderHeaderSeed`
(31,465, recovered from the checkpoint chunk container — Blocker 2 RESOLVED),
`Sales.SpecialOfferProduct_inmem` (538 — landed 2026-07-04 via the **seq
completeness signal** below, despite having no `IDENTITY` surrogate), and
`Production.Product_inmem` (504 — landed 2026-07-04 via the seq gate after
modelling the **XTP-native variable-column layout**: see "Resolution 2"; its
cells match the on-disk twin `Product_ondisk` 11,592/11,592).

The earlier claim that the remaining tables lack a completeness signal is
**superseded**: the record header's `seq` **is** a per-table dense insert
sequence (see "seq completeness signal"), so `seq_max` == the row count and a
gap-free `seq` run proves completeness for any key shape. The two still-skipped
tables each have a *specific, diagnosed* blocker (unrecovered seq-gap records for
`SalesOrderHeader/Detail_inmem`), not the absence of a signal. See "Resolution 2"
at the end.

## Record format (corrected)

After decompressing every non-page chunk and grouping consecutive non-page
chunks into a *segment*, the XTP row images sit back-to-back as fixed-framed
records — **header first, payload after**:

```
[ u32 size ][ u32 flags=0x8000_00LB ][ u32 seq ][ u32 marker ][ u32 pad=0 ][ payload (size bytes) ]
```

- **Stride = `size + 20`.** The 20-byte header comes first; the `size`-byte
  payload immediately follows it.
- ⚠️ **Correction:** earlier notes described this as
  `[payload][size][flags][seq][marker][pad]` (payload *before* the header). That
  is the same physical byte stream drawn with the record boundary one record
  off, and decoding it literally attributes each header's `size` to the
  *previous* record's bytes. For a constant-size run (DemoDetailSeed, all
  `size=20`) that off-by-one only drops the boundary record (the old "537/538");
  for a variable-size run (SpecialOffer, `size` 122–180) it garbles most rows.
  The header-first framing above decodes both byte-exact.
- `flags = 0x8000_00LB`, where the **low byte `LB` discriminates the table**.
  `seq` is a global monotone row sequence; `marker`/`pad` are effectively
  constant per run (`pad == 0` always).
- Records are contiguous within a segment, so one valid header lets us walk the
  whole run by stride (`xtp.scan_cfp_log_records`). Payload sizes may be ≡ 2
  (mod 4), so record starts are only 2-byte aligned.

### Payload layout

`[ fixed columns (colid order) ][ 2-byte null bitmap ][ variable offset array ][ variable data ]`

- Fixed date/time columns use a **non-standard encoding**: `uint64` LE of
  100-nanosecond ticks since **1900-01-01** (not the page `[time_len][3-byte
  date]` layout). `xtp._decode_xtp_date_col` handles it.
- The **2-byte null bitmap** immediately follows the fixed section: one bit per
  *nullable* column in colid order, set = NULL (verified: `SpecialOffer_inmem`'s
  only nullable column `MaxQty` → bit 0 → `0x0001` for every NULL row, 16/16).
- Variable columns follow the descriptor/offset array; NULL when
  `start_offset == end_offset`. Integer / money / varchar / nvarchar all decode
  via `xtp._decode_payload` with `xtp_log_mode=True`.

## Per-table decode status

| Table | GT rows | identity | status |
|---|---|---|---|
| `Sales.SpecialOffer_inmem` | 16 | dense | **LANDED — byte-exact + complete** (log tail; dense-identity gate) |
| `Demo.DemoSalesOrderDetailSeed` | 538 | dense | **LANDED — byte-exact + complete** (log tail; dense-identity gate) |
| `Demo.DemoSalesOrderHeaderSeed` | 31,465 | dense `LocalID` 1..N | **LANDED — byte-exact + complete** (log tail + checkpoint container; dense-identity gate) |
| `Sales.SpecialOfferProduct_inmem` | 538 | no `IDENTITY(1,1)` | **LANDED — byte-exact + complete** (seq contiguous 1..538; **seq gate**) |
| `Production.Product_inmem` | 504 | `ProductID` sparse | **LANDED — byte-exact + complete** (seq contiguous 1..504; **seq gate** + XTP-native variable-column layout) |
| `Sales.SalesOrderHeader_inmem` | 31,465 | `SalesOrderID` sparse | **LANDED — byte-exact + complete** (seq contiguous 1..31465 after XPRESS v2-overlap fix) |
| `Sales.SalesOrderDetail_inmem` | 121,317 | `SalesOrderDetailID` sparse | **LANDED — byte-exact + complete** (seq contiguous 1..121317 after checkpoint-container splice recovery + XTP variable-layout fix) |

> Note: `LB` (flags low byte) / `marker` per-table fingerprints and the earlier
> log-tail-only row estimates from intermediate phases are preserved below for
> history; the final landing verdict is the table above.

## Landing gate (how "complete" is decided without ground truth)

`xtp.decode_cfp_log_records` emits a table **only** when the table's
`IDENTITY(1,1)` column enumerates `{1..N}` exactly (`_dense_identity_complete`):
a gap-free identity sequence starting at 1 means the table's entire insert
history is in the log tail. This is both the completeness gate and the
LB→table discriminator — restricting the dense check to the *declared* identity
column stops a wrong candidate table from claiming a group whose bytes happen to
expose `{1..N}` at an unrelated offset. The five split tables all fail it (their
identity keys have gaps or don't start at 1), so they stay absent rather than
being emitted partially (guardrail 4: never ship a partial decode).

## Remaining blocker (why five tables are still skipped) — REFINED 2026-07-04

**Blocker 2 — log-tail vs checkpoint split.** The five tables are only *partially*
present in the records the current scanner collects; the rest were checkpointed
into XTP **checkpoint data files**. New this session, the checkpoint data has been
**located and its format identified** — it is *not* a separate/opaque format:

### B2.1 — Checkpoint rows use the IDENTICAL framing + payload as log records
A no-twin canary (`DemoSalesOrderHeaderSeed` LocalID=6500, in a missing run) was
found in the decompressed stream at a checkpoint region, stored as:

```
[u32 size=32][u32 flags=0x8000000d][u32 seq=LocalID][u32 marker=0x94][u32 pad=0][32-byte payload]
```

i.e. the same header-first record and the same fixed-column payload layout as the
log tail, laid out **contiguously at stride = 20 + size**, in identity order. So
`_read_log_header` / `_decode_payload` already handle these rows — no new decoder
is needed.

### B2.2 — Root cause of the miss: `is_page` misclassifies 64 KB checkpoint chunks
`scan_cfp_log_records` builds segments from *non-page* decompressed chunks, using
`compressed.py`'s page test `len(ch) >= 96 and ch[0] == _HEADER_VERSION(=1)`. XTP
checkpoint data arrives in 65536-byte chunks; **6041 of 9028** of them begin with
byte `0x01` and are wrongly treated as pages, so they are dropped from the scan.
The chunk holding LocalID=6500 is one: it begins `01 64 01 00 …` — byte 1
(`m_type`) = `0x64`=100, far outside the valid page-type range (1..~22). The two
missing runs per table (`DemoSalesOrderHeaderSeed`: exactly two 1251-row runs
6390–7640 and 26520–27770 ≈ one 64 KB chunk each) are precisely these dropped
chunks.

### B2.3 — Prototype and the SECOND blocker it exposes
Tightening the page test to `byte0==1 AND 1 <= byte1 <= 22` recovers most of the
missing rows (`tools/diag/_diag_xtp_refit.py`):

| LB | table | current | strict-page | GT |
|---|---|---|---|---|
| 0x08 | Product_inmem | 233 | 504 | 504 |
| 0x09 | SpecialOfferProduct_inmem | 319 | 538 | 538 |
| 0x0a | SalesOrderHeader_inmem | 29,564 | 31,447 | 31,465 |
| 0x0b | SalesOrderDetail_inmem | 99,489 | **81,764 ↓** | 121,317 |
| 0x0d | DemoSalesOrderHeaderSeed | 28,963 | 31,464 | 31,465 |

`0x0b` *regresses* — but not because of dedup: the chain-walk plus zeroed-header
boundary (B2.3a) changes which run-starts the probe locks onto, and `0x0b`'s two
payload shapes (size 56 and 80) mean a wrong-offset start decodes the identity
from the wrong bytes (garbage max id `281479271769089`). Each table is emitted
with a single, clean `marker` (0x08→0x68, 0x09→0x6a, 0x0a→0x6c, 0x0b→0x6e,
0x0d→0x94), so `marker` is a reliable per-table fingerprint — but the collection
still needs per-table shape handling and **identity-value dedup** (not header
`seq`), since a row can appear in both the checkpoint and the log tail.

### B2.3a — First record per checkpoint chunk has a zeroed header prefix
Each checkpoint chunk's data region is zero-padded, then the first data record
begins with its leading **12 header bytes (size, flags, seq) zeroed** — only
`marker`+`pad` survive — e.g. for `DemoSalesOrderHeaderSeed` LocalID=6390:

```
00 00 00 00 | 00 00 00 00 | 00 00 00 00 | 94 00 00 00 | 00 00 00 00 | <32B payload, LID=6390>
size=0(!)     flags=0(!)     seq=0(!)      marker=0x94   pad=0
<next record LID=6391 has a fully valid 20-byte header>
```

So `_read_log_header` cannot lock onto the first record; the walk starts at the
*second* record and drops the first. This is why strict-page still misses exactly
the first row of each dropped chunk (`DemoSalesOrderHeaderSeed` → 31,463/31,465,
missing only 6390 and 26520).

A one-stride back-probe salvage (at a run start, if the 8 bytes at
`z=off-20-size` are `(marker, 0)`, take `seg[z+20:z+20+size]` as the first
record) recovered **6390 but not 26520** (`tools/diag/_diag_xtp_d_validate.py`).
Examining the residue shows chunk boundaries carry **three** artifacts, not one:

1. a **chunk preamble** (`01 64 01 00 01 00 01 00 00 e0 12 01 …`) at the start of
   each reincluded 64 KB chunk, followed by zero padding;
2. the **zeroed-header first record** (B2.3a above);
3. a **straddling leftover header** at the previous chunk's tail whose 32-byte
   payload runs into the next chunk's preamble — collected as a spurious record
   (e.g. decoded id `30623464`, seq=26520, payload = the preamble bytes). This
   straddle is what disrupts 26520's run-start so the salvage misses it, and it
   also injects a garbage id that breaks the `{1..N}` gate.

**Conclusion (revised scope):** byte-exact recovery is *not* just "one salvage on
top of the log-record scanner." It requires **modeling the XTP checkpoint chunk
container** — locate each chunk's preamble/data boundary, read records only within
a chunk's data region, and forbid records from straddling a chunk→preamble seam —
then apply identity dedup. That is a larger, self-contained RE task
(`docs/spec/08_XTP_CHECKPOINT.md`). Until it is done, all five tables stay
skipped (guardrail 4: no partial decode); the two log-tail-complete tables
(`SpecialOffer_inmem`, `DemoSalesOrderDetailSeed`) remain landed and unaffected.

### B2.5 — External corroboration (2026-07-04)
Sources: MS Learn "Durability for Memory-Optimized Tables"; the Hekaton SIGMOD
2013 paper (CMU 15-721 copy); Red-Gate "Understanding Memory-Optimized Tables";
`sys.dm_db_xtp_checkpoint_files` / `..._checkpoint_stats` docs.

- A **CFP = data file (inserted versions) + delta file (deleted RowIDs)**. The
  final table state is **data-file inserts MINUS delta-file deletes**. Our scan
  reads only the data/insert side; a table that had post-load deletes/updates
  needs the delta file applied for byte-exactness.
- **UPDATE = DELETE + INSERT** internally. The `_inmem` copies here are populated
  by bulk `INSERT … SELECT` (likely insert-only ⇒ delta near-empty), but this
  must be checked per table before trusting inserts alone.
- A version record is **[header: Begin/End timestamps] + [payload]** — consistent
  with our 20-byte framing header (`seq`/`marker` ≈ the MVCC begin/end stamps)
  followed by the user-column payload. Corroborates the payload decode structure.
- Data-file rows **interleave across tables in transaction (commit-timestamp)
  order**; the serialization segment is ~1 MB. Matches the LB-interleaved records
  and the `seq`/marker fingerprints.
- **No public byte-level spec and no existing parser** — the format is proprietary
  and version-specific (OrcaMDF reads 8 KB pages, not XTP CFPs). So the chunk
  preamble/boundary framing (B2.3/B2.3a) is **empirical-only RE**; there is no
  reference layout to shortcut it. This raises the "modeling the container" task's
  confidence that it is necessary, and its cost estimate.

### B2.3b — Per-table decode obstacles (beyond boundaries)
Even with all records collected, the current `_decode_payload` + dense-identity
gate does not fit every table:
- `Product_inmem` (0x08): identity `ProductID` decodes to garbage (distinct=105,
  values ±2^31) — its fixed-column layout/identity offset is wrong for the XTP
  payload; needs per-column layout RE.
- `SalesOrderHeader_inmem` (0x0a): `SalesOrderID` is **not** seed=1 (values up to
  ~75k for 31,465 rows), so the `{1..N}` dense gate does not apply — needs a
  different completeness criterion (e.g. row count vs a trusted count, or a
  contiguous-key check anchored at the real seed).
- `SalesOrderDetail_inmem` (0x0b): **two payload shapes** (size 56 and 80) in one
  LB group — disambiguate before decoding identity.
- `SpecialOfferProduct_inmem` (0x09): 16-byte payloads, **no seed-1 identity
  column** detected — dense gate inapplicable.

### B2.4 — Resumable roadmap to land the five tables
1. Strict page test in `scan_cfp_log_records`'s segment build (`byte0==1 AND
   1 <= byte1 <= 22`) so checkpoint chunks are not dropped. Keep it local to the
   XTP scanner; do **not** change `compressed.py`'s shared page logic without
   separately validating page-tier tests.
2. Salvage the first record per chunk (B2.3a): back-probe one stride at each run
   start and reconstruct the zeroed header from the run's constant fields.
3. Group by `(lb, marker)` (per-table fingerprint), handle multiple payload
   shapes per table (B2.3b, `0x0b`), and dedup by **decoded identity value**
   (keep last version; drop tombstones) instead of header `seq`.
4. Fix per-table fixed-layout decode where identity is garbage (`Product_inmem`)
   and adopt a completeness gate that also covers non-seed-1 identity tables
   (`SalesOrderHeader_inmem`) and no-identity tables (`SpecialOfferProduct_inmem`).
5. Land only tables that are byte-exact + complete vs `.cells`; verify the two
   already-landed tables (16/16, 538/538) and the synthetic `xtp_*` fixtures do
   not regress. Guardrail 4: partial ⇒ stay skipped.

**Nearest-term win:** `DemoSalesOrderHeaderSeed` is one boundary-salvage (B2.3a)
away from complete (31,463 → 31,465), needs steps 1+2+3 only, and has no B2.3b
obstacle (fixed 32-byte payload, clean marker 0x94, seed-1 identity). The other
four each additionally need step 4.

Repro scripts (this session): `tools/diag/_diag_xtp_split.py`,
`_diag_xtp_gap.py`, `_diag_xtp_ckpt_probe.py`, `_diag_xtp_canary.py`,
`_diag_xtp_chainmiss.py`, `_diag_xtp_chunkcls.py`, `_diag_xtp_refit.py`,
`_diag_xtp_pop.py`, `_diag_xtp_d_validate.py`, `_diag_xtp_preamble.py`.

*(Blocker 1 — the non-standard XTP date encoding — is RESOLVED; see the
payload-layout section.)*

## Corrections to prior notes

- The framing is **header-first** (see above), not payload-first.
- The `50 00 03 00` blocks carrying UTF-16LE JSON (`[{"CarrierTrackingNumber":
  ...}]`) are the **disk-based** `Sales.SalesOrder_json` table's `OrderItems`
  column, **not** XTP row data. The old "transaction-log JSON, out of scope"
  conclusion was a misidentification and remains retracted.

## Landed wiring

`extract.py` feeds decompressed bytes to `read_xtp_rows(..., is_compressed=True)`.
Pass 3 (`scan_cfp_log_records` + `decode_cfp_log_records`) runs only for
MSSQLBAK-compressed input; the uncompressed synthetic compact/WAL path
(`xtp_simple_full.bak`, `xtp_probe_full.bak`, `xtp_rich_full.bak`) is unchanged
and still exercises the compact-block and WAL-block decoders.

## Resolution (2026-07-04) — checkpoint chunk container modeled; Blocker 2 closed

The checkpoint chunk container is now modeled in `scan_cfp_log_records`, and
`DemoSalesOrderHeaderSeed` lands **byte-exact + complete (31,465/31,465)**. The
production changes:

1. **Strict page test** — `is_page` now also requires `1 <= byte1 <= 22`
   (`_PAGE_MTYPE_MAX`). 64 KB checkpoint chunks open with `0x01` but carry an
   out-of-range `m_type` (e.g. `0x64`), so they stay in the non-page stream and
   concatenate with their neighbours (records flow across contiguous checkpoint
   chunk boundaries as before).
2. **Preamble-gated, marker-independent first-record salvage** — a checkpoint
   chunk begins with a self-describing preamble (`_CKPT_PREAMBLE_MAGIC = 01 64 01
   00`) + zero-fill that overwrites the first data record's 20-byte header. At each
   run start we salvage the payload at `[off - size, off)` with `seq = seq(F) - 1`
   **iff** a preamble sits within `_CKPT_PREAMBLE_LOOKBACK` bytes before it. This
   fixes the B2.3a case where the whole header (incl. `marker`) is zeroed — the old
   marker-dependent salvage recovered LID 6390 (marker survived) but missed LID
   26520 (marker zeroed).
3. **Header→preamble straddle drop** — the record whose header sits just before a
   chunk boundary has its payload spill into the next chunk's preamble, so its
   "payload" *is* the preamble bytes; those are dropped (the real row is recovered
   by salvage on the next chunk). Also frees `seq = S-1` for the salvage.
4. **Dense-identity gate with stray tolerance** (`_dense_identity_rows`, replacing
   `_dense_identity_complete`) — decode all records, index by identity value
   (reject if any identity maps to divergent payloads → unresolved versioning),
   take the gap-free `{1..N}` prefix, and accept only when the strays beyond `N`
   are **isolated far-outliers** (≤ `_MAX_DENSE_STRAYS`, none consecutive, first
   `> _MIN_DENSE_STRAY_FACTOR * N`). This absorbs the handful of delta/system
   records that share a table's LB+marker but decode to identities far outside the
   key range (e.g. `117492051`), while still **refusing** sparse-key tables (a
   *consecutive* stray run ⇒ real rows beyond `N` ⇒ key is not dense-from-1 ⇒
   completeness unprovable).

### Why the other four stay skipped (fundamental, not a container gap)
> **SUPERSEDED by "Resolution 2" below.** The "no provable completeness signal"
> conclusion in this subsection was wrong: `seq` is the signal.
> `SpecialOfferProduct_inmem` is now **landed** via the seq gate, and the other
> three each have a specific diagnosed blocker. Kept here for history.

With the container recovered, all four are byte-recoverable but have **no provable
completeness signal**:
- `SalesOrderHeader_inmem` / `SalesOrderDetail_inmem` — **sparse business keys**
  (`SalesOrderID` jumps 4→316; `SalesOrderDetailID` similar): a dense `{1..N}`
  prefix cannot certify completeness.
- `Product_inmem` — no dense prefix at all (N=0 from the collected records).
- `SpecialOfferProduct_inmem` — no `IDENTITY(1,1)` surrogate key.

Landing these needs an independent completeness signal (an authoritative
checkpoint row-count) the backup stream does not expose. Emitting them now would
violate guardrail 4 (never ship a partial decode). Repro:
`tools/diag/_diag_xtp_boundary.py` (model + all-five verdicts),
`tools/diag/_diag_xtp_e2e.py` (production-path landing check).

## Resolution 2 (2026-07-04) — seq completeness signal; SpecialOfferProduct landed

The "no provable completeness signal" verdict was **wrong**. A per-LB census of
the (deduped) records the production scanner now collects shows the record
header's `seq` is a **dense per-table insert sequence** whose maximum equals the
table's row count (`tools/diag/_diag_xtp_seq.py`):

| LB | table | recs | seq span | gaps | GT |
|---|---|---|---|---|---|
| 0x07 | SpecialOffer_inmem | 16 | 1..16 | 0 | 16 |
| 0x08 | Product_inmem | 504 | 1..504 | 0 | 504 |
| 0x09 | SpecialOfferProduct_inmem | 538 | 1..538 | 0 | 538 |
| 0x0a | SalesOrderHeader_inmem | 31,447 | 1..31465 | 18 | 31,465 |
| 0x0b | SalesOrderDetail_inmem | 81,764 | 1..121317 | 39,553 | 121,317 |
| 0x0c | DemoSalesOrderDetailSeed | 538 | 31466..32003 | 0 | 538 |
| 0x0d | DemoSalesOrderHeaderSeed | 31,465 | 1..31465 | 0 | 31,465 |

So **seq contiguity** (`distinct(seq) == max-min+1`) is a runtime completeness
signal that works for **any** key shape — sparse, composite, or absent.

> **Corroboration (2026-07-04).** `sys.dm_db_xtp_checkpoint_files` exposes
> `logical_row_count` = *"For Data, number of rows inserted"* — the engine tracks
> an exact per-data-file insert count, so a DATA file holds a well-defined complete
> insert set (for an insert-only table with an empty DELTA file, a full data-file
> scan is complete). This is independent conceptual support for the seq signal
> (`seq_max` == row count); the per-table dense `seq` 1..N encoding itself remains
> `[EMPIRICAL]`. The same DMV's LARGE DATA `file_type_desc` (only `(n)varchar(max)`/
> `varbinary(max)` + columnstore leave the row) corroborates why the bounded
> `nchar`/`nvarchar` columns of `Product_inmem` decode **inline** in the variable
> section. See `docs/CORROBORATION_SOURCES.md` (2026-07-04 sweep).

This is
implemented as **Pass B** (`_seq_complete_rows`) in `decode_cfp_log_records`,
running after the dense-identity Pass A on the LB groups Pass A did not claim.
Pass B maps an LB group to a schema table via a per-table fingerprint plus
`_xtp_fully_decodable` (columns the decoder reproduces byte-exact):

- **no variable columns** — constant payload width == fixed width (e.g.
  `SpecialOfferProduct_inmem`: int, int, datetime2; all payloads exactly 16 bytes;
  seq 1..538 → **538/538**).
- **with variable columns** — every payload must be an internally consistent
  record whose variable data is *fully consumed* by exactly this table's columns
  (`_xtp_var_record_consistent`: descriptor offsets non-decreasing, in-bounds, and
  the last end offset == payload length). This full-consumption equality is the
  discriminator for a variable-width group (e.g. `Product_inmem` below).

### XTP-native record layout (empirically solved, `Product_inmem`)
Landing `Product_inmem` required modelling the native in-memory record layout,
which differs from the compact/WAL page-ish layout in three ways:

1. **Fixed section ordered by slot width descending, then colid** (not
   `max_length` desc).
2. A **numeric/decimal** column occupies an **8-aligned** fixed slot storing an
   8-byte little-endian signed **scaled-integer mantissa** (`value = mantissa /
   10**scale`; `Weight` 2.24 → `0xE0`=224 at offset 16), *not* the page format's
   sign-byte+magnitude.
3. **bit** columns are stored **one per byte** (value in bit 0), not bit-packed —
   so the page decoder's per-column `bit_shift` reads the wrong bit (this made
   `FinishedGoodsFlag` decode to 0 on all 295 finished-goods rows until fixed).
4. **Fixed char/nchar/binary** columns live in the **variable section** (via the
   offset array), *not* the fixed section; nchar values are space-padded to their
   declared width and the comparator (`canon`) trims trailing pad.

Worked example — `Product_inmem` seq=1 (ProductID 680, rich row), offsets solved
by `tools/diag/_diag_xtp_layout.py`:
`StandardCost@0, ListPrice@8, Weight(numeric)@16, SellStartDate@24,
SellEndDate@32, DiscontinuedDate@40, ModifiedDate@48, ProductID@56,
DaysToManufacture@60, ProductSubcategoryID@64, ProductModelID@68,
SafetyStockLevel@72, ReorderPoint@74, MakeFlag@76, FinishedGoodsFlag@77` (fixed
section 78 bytes); then the 2-byte null bitmap and a **variable offset array**
covering the nvarchar columns (`Name/ProductNumber/Color/Size`) **and** the nchar
columns (`SizeUnitMeasureCode/WeightUnitMeasureCode/ProductLine/Class/Style`) in
colid order. Implemented as `_xtp_fixed_cols`/`_xtp_var_cols`/`_xtp_fixed_width`/
`_decode_xtp_numeric_col` (log-mode only; the compact/WAL path is unchanged).
Result: **504/504 byte-exact + complete**, cells matching the on-disk twin
`Production.Product_ondisk` (11,592/11,592).

### Why the two others still stay skipped (specific, not "no signal")
- **`SalesOrderHeader_inmem`** — near-complete: seq 1..31465 with only **18 gaps**
  (31,447/31,465). A handful of checkpoint-container records are still lost (the
  seq gate correctly refuses on any gap).
- **`SalesOrderDetail_inmem`** — seq 1..121317 with **39,553 gaps** (81,764);
  records arrive in **two payload shapes** (56 and 80 bytes) and the missing ones
  are not yet recovered.

Repro: `tools/diag/_diag_xtp_seq.py` (seq census), `_diag_xtp_four.py`
(per-table coverage vs GT), `_diag_xtp_layout.py` (Product fixed-layout solver),
`_diag_xtp_sop.py` (SpecialOfferProduct byte-exact check),
`_diag_xtp_product_verify.py` (Product byte-exact check via `canon`),
`_diag_xtp_e2e.py` (production-path landing check).

## Resolution 3 — straddle-row recoverability investigation (2026-07-04)

**Hypothesis:** The variable-section data of records that straddle a 64 KB XTP
checkpoint-chunk boundary might survive intact elsewhere in the backup stream
(e.g., in checkpoint DATA files), allowing a second-pass decoder to recover them.

**Investigation:**

A synthetic `xtp_checkpoint_straddle_full.bak` fixture was generated with
100,000 rows (each 400-byte `nvarchar(400)` payload) to reliably induce straddle
conditions at every 64 KB boundary.  `tools/diag/_diag_xtp_ckpt_locate.py`
exhaustively searched the entire decompressed stream for the 42 resulting missing
row IDs. Findings [EMPIRICAL]:

1. **Non-page (log) stream**: The fixed section of each straddle record (id +
   width field) is present. The `nvarchar` tail beginning at the chunk boundary is
   **zero-filled** by the next chunk's preamble overwrite — not merely clobbered
   with a different magic, but replaced with contiguous `\x00` bytes.

2. **Page-classified 64 KB chunks** (`byte0=page_version`, `byte1=0x01`): These
   chunks are 64 KB XTP checkpoint blocks misidentified as SQL Server 8 KB pages
   by the `is_page` guard.  They contain **XTP B-tree index structures** (sorted
   key arrays with the missing IDs visible as index entries), not row payload data.
   No full row payload (fixed + variable sections combined) was found in these
   blocks.

3. **Exhaustive stream search** for the complete id=682 payload (fixed section +
   variable nvarchar data): **zero matches** across all decompressed chunks
   (including pages, non-pages, and the misclassified 64 KB blocks).

**Gate G2 = (c) truly absent.** The `nvarchar` variable payloads of straddle rows
are not stored anywhere in this compressed backup format after the preamble
overwrite.  There is no checkpoint DATA file within the backup that contains
intact copies.

**Consequence:** Tasks 7–8 (reverse-engineer checkpoint DATA-file framing and add
a recovery pass to `xtp.py`) are cancelled.  The two SOH/SOD tables remain in
`KNOWN_SKIPPED_TABLES` permanently under this backup format.  The 18 missing SOH
rows and ~39,553 missing SOD rows represent an inherent data loss in the backup
file itself, not a decoding limitation.

Repro: `tools/diag/_diag_xtp_ckpt_locate.py` (straddle-row location probe),
`tools/diag/_diag_xtp_ckpt_probe.py` (payload decode verification),
`tests/test_xtp_checkpoint_coverage.py` (regression guard for the straddle
fixture — expected to show 42 missing rows from the `xtp_checkpoint_straddle`
table).

---

## Status

`AdventureWorks2016_EXT` now has **no expected XTP skips** in
`KNOWN_SKIPPED_TABLES`. All seven memory-optimized tables are landed and verified
byte-exact + complete against `.cells` ground truth. The normal sidecar harness
passes for `AdventureWorks2016_EXT`, and `tools/diag/_diag_xtp_soh_diff.py`
reports 31,465 SOH rows with no mismatches.

The earlier Gate G2 conclusion is superseded. The remaining SOH blocker was the
MSSQLBAK v2 XPRESS stream-overlap bug described in the 2026-07-05 update above.
