# Columnstore Archive — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `COLUMNSTORE_ARCHIVE` (spec abstraction, not a code symbol)
**Set by:** `read_table_rows` (`mssqlbak/rows.py:1132`) when `table.compression == 4` (cmprlevel=4, ARCHIVE) or `enc == 5` with XPRESS.
Routing is driven by `table.compression` (`rows.py:1194`).
**Catalog signal:** `sysrowsets.cmprlevel == 4`
**Decode entry point:** `columnstore/assembly/reader.py: read_columnstore_rows()` → `columnstore/decode/enc5_raw.py`

---

## 2. Initialization

XPRESS-compressed enc=5 segments. Pool+index structure. Boundary not stored explicitly — inferred by heuristic scan. See `01_XPRESS.md` for the codec.

---

## 3. Record structure

### 7.4 Columnstore archival (cmprlevel=4) `[CORROBORATED]`

Every column segment blob and dictionary blob for a `COLUMNSTORE_ARCHIVE`
table is wrapped in a 12-byte frame before the payload:

```
[+0:+4]   uint32 LE  flags (observed: 0)
[+4:+8]   uint32 LE  uncompressed_size (bytes of the unwrapped payload)
[+8:+12]  uint32 LE  compressed_size   (= len(blob) - 12)
[+12 ..]  payload
```

When `uncompressed_size == compressed_size` the payload is stored verbatim
(no compression).  When they differ the payload is XPRESS-LZ77 compressed
(using the same `xpress.decompress` path as the MTF container).

**cmprlevel=4 row-group sorting.** `ALTER INDEX … REBUILD WITH
(DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)` re-sorts rows: nullable-column
null values are pushed to the front of the row group; non-null values follow
in the order determined by the archive rebuild.  All column segments within a
row group share this same physical row order.

**enc=1/2 compact null mode (archive CCI).** For a nullable column in an
archive row group the bitpack may contain fewer entries than `n_rows`.  When
`nw × vpw < n_rows` (`vpw = 64 // bpv`), the bitpack stores only the
`n_non_null = nw × vpw` non-null values; the leading `n_null = n_rows −
n_non_null` row positions are implied NULL (the null rows sorted to the
front).  The sentinel at `bp_off − 16` confirms the non-null count.

**Catalog disambiguation (cmprlevel=4 vs 3).** SQL Server stores two
`sysrowsets` entries with `idminor=1` for the same table object after a
`COLUMNSTORE_ARCHIVE` rebuild: one at `cmprlevel=3` (the pre-rebuild CCI row
group that is still referenced) and one at `cmprlevel=4` (the archive row
group).  The parser selects the rowset with the highest `cmprlevel` to
correctly report compression level 4 and derive column metadata from the
archive row group's `sysrscols` entries.

#### Format C — XPRESS-compressed, per-row index `[EMPIRICAL]`

`h92 = 0`; `h38 = u16@38 == n_rows`.

An XPRESS block is located by scanning for a `u16 == 0xFFFF` marker where
`u16@(marker-6)` is a plausible item size (set `{1,2,4,5,8,9,10,16,17,20}`).
The marker whose recorded size matches `_enc5_item_size(col)` is preferred
(`_find_enc5_xpress_marker`); the XPRESS stream starts at `marker_off + 8`.

Decompressed layout:
```
[0 .. n_non_null × item_size)   non-null values in reverse-insertion order
[n_non_null × item_size ..]     n_rows × u16 index entries:
                                  0xFFFE = null sentinel
                                  other  = byte offset into values section
```

`n_non_null` is found by scanning: the smallest `p` where all `n_rows` u16
index entries at `d[p × item_size :]` are either `0xFFFE` or valid byte
offsets `< p × item_size` aligned to `item_size`.

The index lists rows **back-to-front** (first index entry points at the
last-stored value), so the decoded list is reversed to restore ascending
physical row order matching the other column segments. `[EMPIRICAL]`

##### Format C — variable-width string/binary pool `[EMPIRICAL]`

`VARCHAR`, `VARBINARY` (and `BINARY` with mixed widths) store distinct values at
their **natural byte length with no padding**, so pool offsets are *not*
multiples of `item_size` and the fixed-width scan above fails.  The pool is a concatenation
of the distinct values in **insertion order** (first inserted value at offset 0)
and the index holds **absolute byte offsets** into it:

```
[0 .. P)                packed distinct values, natural length, no padding
[P .. P + n_rows × 2)   n_rows × u16-LE index entries:
                          0xFFFE = null sentinel
                          other  = byte offset into the pool
```

A value's length is the gap to the **next-larger distinct offset** (or `P` for
the largest), which recovers each variable width without a separate length
field.  The pool length `P` (= index start) is located by self-consistency:
the first index entry `e0 = u16@P` is the largest offset (back-to-front order),
and because the two leading values share the filler width,
`P == 2·e0 − e1`.  The candidate is accepted only when every index entry is
`0xFFFE` or `< P`, offset `0` is present, and `e0` is the maximum offset.
Decoded values are reversed to physical row order (see above).

Decoded by `_enc5_formatc_varlen`.  For `VARCHAR` and `VARBINARY`, `_decode_enc5`
calls `_decode_enc5_compressed(..., variable_width=True)`, which runs this
variable-length reader on the decompressed buffer **before** the fixed-width
scan.  This is required because the fixed-width scan can *false-positive*: with a
guessed/declared width (e.g. `item_size=8` from `blob[82]`, or the declared
`max_length=20`) it may read two adjacent short entries as one wide value and
miss every `0xFFFE` null sentinel — observed as `cmp_columnstore.name`
(varchar(20)) decoding every row to the constant `'val1val2'` with 0 nulls
instead of `'val0'..'val9'` with 28 nulls, and the matching `vbn` (varbinary(20))
4-byte values coalesced.

Evidence: `cci_varbinary` (cci_types_large, 8-byte fillers),
`cci_varbinary_narrowmax` (VARBINARY(4), 4-byte), `cci_varbinary_maxwidth`
(mixed 16/4-byte), `cci_binary_varbinary_compare` (BINARY(8)≡VARBINARY(8)),
`compressioncoverage_full` (`cmp_columnstore.name` varchar(20),
`cmp_columnstore.vbn` varbinary(20); 28/200 scattered NULLs) —
SS2017/2019/2022/2025.

The fixed-width Format C path still covers `UNIQUEIDENTIFIER` (16-byte) and
`BINARY` (uniform width); it is given priority over the ARCHIVE type-2 heuristic
for those types so a `0xFFFF` byte in the XPRESS stream plus a coincidental
`u32 == n_rows` and width-divisible pool cannot misfire (Bug K3C). Evidence:
`cci_uuid` (cci_types_large, 1,200-entry dictionary) — SS2017/2019/2022/2025.

###### ARCHIVE-inline variable-width pool `[EMPIRICAL]`

For a `COLUMNSTORE_ARCHIVE` (cmprlevel=4) CCI, each enc=5 segment blob is wrapped
in the 12-byte ARCHIVE frame and XPRESS-compressed; `_unwrap_archive_blob`
decompresses it up front, so by the time `_decode_enc5` runs the value pool is
**already inline and uncompressed** as `[enc5 header][…][0xFFFF u16][n_block u32]
[pool][index]` (the same `[0xFFFF][n_block]` marker as the ARCHIVE type-2 layout,
with the value pool starting at `marker + 6`).  Because the pool is no longer
XPRESS-compressed, `_decode_enc5_compressed` cannot re-locate/decompress a chunk
and returns `None`.  For `VARCHAR`/`VARBINARY`, `_decode_enc5` then falls back to
`_decode_enc5_archive`, whose byte-offset pool-map decoder handles the
variable-width inline pool directly (the divisibility guard in the ARCHIVE type-2
detection still rejects these for the *regular*, still-compressed CCI, so the
fallback only fires for the unwrapped archive form).

`datetimeoffset` (and any fixed-size non-string type) decoded via the ARCHIVE
pool-map must be converted with `_enc5_item_to_python` (helper
`_enc5_archive_to_python`), **not** returned as raw bytes: emitting raw 9-byte
`datetimeoffset` values makes the downstream Arrow `timestamp` conversion fail
and collapses the whole column to NULL (observed as
`cmp_columnstore_archive.dto` → 200/200 NULL instead of 28).

Evidence: `compressioncoverage_full` `cmp_columnstore_archive` —
`name` (varchar(20)), `vbn` (varbinary(20)), `dto` (datetimeoffset(3)), each
28/200 scattered NULLs — SS2017/2019/2022/2025. `[EMPIRICAL]`

###### Regular CCI large string segments: XPRESS-compressed multi-sub-block pool `[EMPIRICAL]`

A **regular** (cmprlevel=3, non-ARCHIVE) CCI also stores wide enc=5 string
segments (`VARCHAR`/`VARBINARY`/`NVARCHAR`) as a sequence of XPRESS-compressed
sub-blocks — the *same* `[0xFFFF u16][n_block u32][marker u16][XPRESS pool+index]`
layout as the ARCHIVE compressed-pool variant, handled by
`_decode_enc5_archive_subblock_compressed`.  `h38_u32 == n_rows` (with
`n_rows > 32 767`) routes these to `_decode_enc5_archive`; the column type then
selects `variable_width=True`.  Three bugs prevented these from decoding
(observed on `NYCTaxi_Sample` `pickup/dropoff_longitude/latitude`,
`varchar(30)`, 200 000-row segments, all ~60–95 % spurious NULL before the fix):

1. **Full-sub-block marker range.** The 2 bytes at `marker + 6` are the first
   XPRESS word of the sub-block, not a discrete flag.  Full-size sub-blocks
   (decompress to exactly 65 536 bytes) use the *full* range `0xFFF0..0xFFFF`;
   only the final partial sub-block uses a first word `< 0xFFF0`.  The original
   ARCHIVE-only upper bound `0xFFFE` excluded `0xFFFF`, mis-routing interior full
   sub-blocks (and whole segments whose first sub-block word was `0xFFFF`) to the
   partial decoder, which then overran.  Both `_enc5_archive_has_compressed_subblocks`
   and the sub-block loop now treat `marker ≥ 0xFFF0` as a full sub-block.

2. **Variable-width pool.** For variable-length columns the pool entries are
   packed at their natural byte length, not padded to `col_width`.  Each entry
   runs from its u16 byte-offset to the next-larger referenced offset (or the
   pool end), as in the raw-pool `_decode_enc5_archive` Pass 2 — never a fixed
   `col_width` slice (which produced 30-byte windows spanning multiple values).

3. **Odd-pool index alignment.** The XPRESS decompressor pads each full
   sub-block's output to 65 536 bytes, so when the variable-length pool is an
   **odd** number of bytes the u16 index begins at an *odd* offset.  The default
   even-aligned `len − n_valid×2` is then off by one, reframing every u16 into
   out-of-range offsets and false `0xFFFE` NULLs.  The variable-width branch
   scans back a few padding bytes and picks the index start whose entries are all
   `0xFFFE` or in-pool offsets. See §6 for the current scan algorithm.

Evidence: `NYCTaxi_Sample.bak` `dbo.nyctaxi_sample` — `pickup_longitude`,
`pickup_latitude`, `dropoff_longitude`, `dropoff_latitude` (`varchar`), all
0/1 703 957 NULL after the fix — SS2022 ground truth. `[EMPIRICAL]`

#### Format D — XPRESS-compressed, dedup index `[EMPIRICAL]`

`h92 = 0`; `h38 = u16@38 < n_rows`.

`n_null = h38`; the last `n_null` output rows are NULL.
`n_non_null = n_rows − n_null`.

Same XPRESS marker scan as Format C.  Decompressed sub-chunk 0 layout:
```
[0 .. n_dedup × item_size)       n_dedup unique values
[n_dedup × item_size ..]         u16 byte-offset index entries (n_non_null total
                                  when the full index fits; n_dedup otherwise)
```

`n_dedup` is located by the self-referential property:
`d[n_dedup × item_size]` as u16 LE == `(n_dedup − 1) × item_size`.

When `n_non_null × item_size ≤ 65535`, `n_dedup == n_non_null` and all rows are
decoded.  When larger, only sub-chunk 0 is decoded; rows in subsequent sub-chunks
receive a zero-filled `bytes(item_size)` placeholder (null count stays correct).

**varchar variable-width decode:** `VARCHAR` values are decoded with the
variable-width pool reader (`variable_width=True`, see the Format C variable-width
section), not a fixed `blob[82]` stored width.  The `blob[82]` value (e.g. 8 for a
column whose true packed width is 4) is unreliable as a fixed item size and was
the source of the `cmp_columnstore.name` coalescing bug; the byte-offset index in
the pool is authoritative instead.

**ARCHIVE null-count fallback:** For cmprlevel=4 segments, the inner XPRESS
block may decompress to a layout that does not satisfy the Format D self-ref
scan (double-compressed Vertipaq-style data).  When `_decode_enc5_compressed`
returns `None` and `h38 < n_rows`, `_decode_enc5` falls back to
`[placeholder] × n_non_null + [None] × n_null`, preserving the null count.
The placeholder value is `_enc5_item_to_python(bytes(item_size), col)`.

**Supported types:** `datetimeoffset(n)` (9 bytes, scale-7 decode),
`datetime2(n)`, `binary(n)`, `varbinary(n)`, `char(n)`, `varchar(n)`,
`nchar(n)`, `uniqueidentifier`, `decimal`/`numeric`.  Unknown type IDs fall
back to raw bytes.

**G42 resolved** — see §10.

---

## 5. Diagnostic events

| tag | decision | extra fields |
|---|---|---|
| `enc5:archive` | ARCHIVE multi-sub-block path taken | — |
| `enc5:formatC` | Format C (XPRESS per-row index) selected | — |
| `enc5:formatD` | Format D (XPRESS dedup index) selected | — |

_Note: current `record_tag` calls record only the branch name. `raw_first16`, `n_valid`,
`buf_len`, `cand_selected` require upgrading to `record_event` (see architecture plan Goal #2)._

---

## 6. Known heuristics

### Pool/index boundary scan `[EMPIRICAL — fix 595bf57, 2026-06-30]`

The XPRESS decompressor fills a fixed 65 536-byte output buffer, leaving up to ~10 padding
bytes past the true data end. SQL Server does not store the pool/index boundary explicitly.
The decoder must scan backward to find where the index begins.

**Gate:** the scan only fires when `variable_width=True` (VARCHAR/VARBINARY/NVARCHAR
columns). Fixed-width columns use the simpler `idx_start = len(pool_idx_b) - n_valid * 2`
without any backward scan.

**Current algorithm** (`enc5_raw.py`, function `_decode_enc5_archive_subblock_compressed`,
scan block at `elif variable_width:`):

```
Default:    idx_start = len(pool_idx_b) - n_valid * 2

If variable_width=True and idx_start >= 0:
  scan-back window: range(idx_start, max(-1, idx_start - 12), -1)
                    (widened from 4 to 12 bytes in fix 595bf57)

  For each candidate cand (scanning downward from idx_start):

    Criterion 1 — all-valid check:
      For every i in range(n_valid):
        v = pool_idx_b[cand + i*2 : cand + i*2 + 2]  (u16 LE)
        reject cand if v != 0xFFFE and v >= cand  (out-of-pool or >= boundary)

    Criterion 2 — row-0 anchor (only evaluated if criterion 1 passes):
      last_v = pool_idx_b[cand + (n_valid-1)*2 : ...]  (u16 LE)
      accept cand only if last_v == 0 or last_v == 0xFFFE
      — last entry = logical row 0 (inserted first into pool) → always at
        pool offset 0.  Rules out false-positive alignments.

    Criterion 3 — printable-ASCII tail check (text_values=True only):
      tail_start = pool_idx_b[cand : cand+2]  (the index's first u16 = row 0's offset)
      if 0 <= tail_start < cand:
        reject cand if any byte in pool_idx_b[tail_start:cand] is < 0x20 or > 0x7E
      — "last pool entry" = bytes from tail_start to cand.  Absorbed index bytes
        (2-byte binary u16s) fail this check; real pool text does not.

    Criterion 4 — secondary tighter-boundary check (evaluated only after cand
                  passes criteria 1+2+3):
      Try cand2 = cand - 2.  Re-run criterion 1 for cand2.
      If cand2 also passes criterion 1 AND pool_idx_b[cand2+(n_valid-1)*2] == 0 or NULL:
        prefer cand2 (absorbed one extra index entry into pool at cand → cand2 is tighter)
      In either case, accept this candidate and stop the scan.
```

**Why the heuristic exists:** XPRESS padding artefacts at the buffer tail. The boundary
is derivable as `len(buf) - n_valid × 2` exactly on disk; it only requires scanning in
the decompressor output where `len(buf)` is the fixed 65 536.

**History:** original scan window was 4 bytes (sufficient for small artefacts). Widened to
12 bytes (`595bf57`) after `GeneralHospital.bak` pools with larger artefacts and/or multiple
self-consistent alignments exposed the insufficiency.

