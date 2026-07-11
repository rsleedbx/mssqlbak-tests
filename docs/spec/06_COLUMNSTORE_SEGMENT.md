# Columnstore Segment — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `COLUMNSTORE_SEGMENT` (spec abstraction, not a code symbol)
**Set by:** `read_table_rows` (`mssqlbak/rows.py:1132`) when `table.compression == 3` (cmprlevel=3, CCI regular) and enc in (1,2,3,4).
Routing is driven by `table.compression` (`rows.py:1194`) and `table.is_memory_optimized` (`extract.py:494`).
**Catalog signal:** `sysrowsets.cmprlevel == 3`, `syscscolsegments` present
**Decode entry point:** `columnstore/assembly/reader.py: read_columnstore_rows()`

---

## 2. Initialization

Each column is stored independently as a segment blob. Segment metadata loaded from `syscscolsegments`. Dictionary metadata from `syscsdictionaries`. enc=1/2/4 use bitpacking/FOR/RLE. enc=3 uses dictionary lookup (global + local dict concatenated).

---

## 3. Record structure

### 7.1 Segment metadata (`syscscolsegments`, obj 62) `[CORROBORATED]`

Offsets read directly by `columnstore/storage/segment_meta.py` (constants `_SEG_*`):

| Offset | Field | Type read | Source constant |
|--------|-------|-----------|-----------------|
| 4 | `hobt_id` | u64 | `_SEG_HOBT_ID` |
| 12 | `col_id` | u32 | `_SEG_COL_ID` |
| 16 | `seg_id` | u32 | `_SEG_SEG_ID` (row-group index) |
| 24 | `enc_type` | u32 | `_SEG_ENC_TYPE` (1=value, 2=RLE, 3=dict, 4=uncompressed 64-bit, 5=raw/off-row) |
| 28 | `n_rows` | u32 | `_SEG_N_ROWS` |
| 32 | `has_null` | u32 | `_SEG_HAS_NULL` |
| 44 | `magnitude` | f64 | `_SEG_MAGNITUDE` (step between stored values) |
| 52 | dict id A | i32 | `_SEG_PRIM_DICT` |
| 56 | dict id B | i32 | `_SEG_SEC_DICT` |
| 60 | `min_data_id` | i64 | `_SEG_MIN_DATA` (`actual = mn + stored*mag`) |
| 76 | `null_val` | i64 | `_SEG_NULL_VAL` |
| 94 | `blob_id` | **u16** | `_SEG_BLOB_ID` (LOB blob holding the bit-packed segment) |

Dict-id fields at offsets **52** (`_SEG_PRIM_DICT`) and **56** (`_SEG_SEC_DICT`):
enc=3 lookup reads offset 56.  Constant names and comments in `columnstore/storage/segment_meta.py`
are swapped relative to SQL Server DMV naming — unresolved.

**G40 `[CONFIRMED]`**: Verified against `sys.column_store_segments` on SS2022 (`boundarycoverage_full.bak`).  Offset 52 = `primary_dictionary_id`; offset 56 = `secondary_dictionary_id`.  For enc=3 string columns, `secondary_dictionary_id` is always set (value 1) and `primary_dictionary_id` is -1.  The parser's `sec_dict` (offset 56) correctly selects the enc=3 string dictionary.  `spec_probe columnstore-dict-order` emits `verdict: match` against verifier output `G40.json`.

### 7.2 Dictionary metadata (`syscsdictionaries`, obj 63) `[CORROBORATED]`

Constants `_DICT_*` in `columnstore/storage/segment_meta.py`:

| Offset | Field | Type read |
|--------|-------|-----------|
| 4 | `hobt_id` | u64 |
| 12 | `col_id` | u32 |
| 16 | `dict_id` | u32 |
| 58 | `blob_id` | **u16** (LOB blob with the dictionary content) |

### 7.3 Segment blob layout `[CORROBORATED]`

Full layout of the inner segment blob (after `_unwrap_archive_blob` for cmprlevel=4,
or the raw blob for cmprlevel=3):

```
[+0 ..+3 ]  uint32 LE  version_lo    (observed: 1)
[+4 ..+7 ]  uint32 LE  version_hi    (observed: 1)
[+8 ..+11]  uint32 LE  (observed: 0)
[+12..+15]  uint32 LE  (observed: 0 or 10 depending on fixture)
[+16..+19]  uint32 LE  (observed: 3)
[+20..+23]  uint32 LE  n_frags       FOR frame count = ceil(n_rows / block_size)
[+24..+27]  uint32 LE  block_size    values per FOR frame (observed: always 512)
[+28..+31]  uint32 LE  (observed: 2)
[+32..+33]  uint16 LE  (observed: 8)
[+34..+35]  uint16 LE  bpv           bits per stored value
[+36..+39]  uint32 LE  nw            number of 64-bit words in the bitpack
[+40..+43]  uint32 LE  (observed: 3)
[+44..+47]  uint32 LE  (observed: 0)

[+48 .. +48+n_frags*8)   Fragment table  (n_frags × 8 bytes each):
    [+0..+3]  uint32 LE  block_type    Block-type indicator:
                                        0 = null-zone block (all rows in this block are NULL)
                                        2 = compact-null-prefix data block
                          NOT a Frame-of-Reference base.  `_bitpack_values` ignores
                          this field entirely; biased values are stored directly in
                          the bitpack without per-block FOR correction.
    [+4..+7]  uint32 LE  n_rows     Global row count (constant across all entries).
                                    NOTE: entry[0][+4] is at blob offset 52 = _BP_N_ROWS.

[rle_start = 48 + n_frags*8 ..]   RLE table (u32 stored_u, u32 run) pairs:
    stored_u >= 0x80000000:  bitpack reference — bit_offset = ~stored_u & 0xFFFF_FFFF;
                             read `run` bpv-bit values starting at that bit offset.
    stored_u == 0 and run == 0:  terminator.
    For non-nullable columns with nw×vpw == n_rows, the RLE table typically has one
    bitpack-reference entry covering all rows, followed by the terminator (16 bytes).

[bp_start = len(blob) - nw*8 ..]  bitpack words  (nw × 8 bytes)
    Values packed LSB-first within each 64-bit word, bpv bits per value.
```

For enc=4 (uncompressed 64-bit), `bpv = 64` and each word is one value.

For enc=1/2/4, each `bpv`-bit value `stored` maps to:
```
actual = min_data_id + (stored - (1 if has_null else 0)) * magnitude
```
with `stored = 0` being NULL when `has_null = 1`.  For non-nullable columns
(has_null=0) the formula simplifies to `actual = min_data_id + stored * magnitude`.

For archive CCI, nullable enc=1/2 columns may use **compact null mode** where
the bitpack holds only non-null rows — see §7.4.

For enc=3 (dictionary), `stored = 0` or `1` are NULL/empty sentinels;
`stored >= 2` is a 0-based dictionary index `stored - 2`.

**G43 `[EMPIRICAL — CORRECTED]`**: Segment blob layout confirmed against `boundarycoverage_full.bak`
(SS2022) and further decoded via `tools/diag_enc1_pfor.py` against ARCHIVE fixtures
(2026-06-16).  Fragment table: n_frags entries at offset 48; u32[0] per entry is a
**block-type indicator** (0=null-zone, 2=compact-null-prefix), NOT a FOR correction base;
n_rows repeated at u32[1] = blob offset 52 (`_BP_N_ROWS`).  `_bitpack_values` does NOT
add a FOR correction to stored values — the bitpack stores full biased values directly.
`_bp_for_base()` is used only by enc=2 numeric dictionary index code paths.
See `columnstore/decode/bitpack.py: _bitpack_values` docstring for the authoritative
correction of the earlier "FOR frame table" interpretation.

### 7.5 Columnstore LOB blob preamble `[CORROBORATED]`

LOB blobs for columnstore dictionaries and segments have an observed structure
(`columnstore/storage/lob.py: _COLUMN_LOB_PREAMBLE = 12`, `_COLUMN_LOB_CHUNK = 65536`,
`_deinterleave`):
```
[+0:+12]   12-byte preamble  [EMPIRICAL — first 4 bytes observed: 01 00 00 00;
                              bytes 4–11 appear to be sizing metadata; not parsed]
[+12 ..]   payload in 65 536-byte chunks; each chunk except the last is followed
           by an 8-byte separator before the next chunk's payload begins
```

Separator content (8 bytes): consistently all-zeros in observed fixtures.
Preamble content (12 bytes): first u32 LE = 1 (version?); remaining 8 bytes
appear to encode total uncompressed length in two 4-byte fields.

**G41 `[EMPIRICAL]`**: Confirmed against `cs_lob_preamble2.bak` (SS2022, 1200
rows of 80-character `varchar` strings).  The dictionary LOB blob exceeded 65 536
bytes and triggered the preamble path.  `_deinterleave_column_lob` strips the
12-byte preamble and the 8-byte separators and delivers the concatenated payload
to the dictionary decoder.  Round-trip validation (all 1200 distinct strings
recovered correctly) confirms the deinterleave boundary arithmetic.  Preamble
field semantics are not confirmed against a DBCC PAGE or Microsoft documentation.

### 7.6 Columnstore dictionary payload formats

#### Global vs local (primary / secondary) dictionary model `[CORROBORATED]`

SQL Server CCI maintains **two dictionaries per column** across all row groups:

- **Global (primary) dictionary**: shared across all row groups in the column.
  Contains high-cardinality values that appear in multiple row groups.  Built once;
  shared by all segment rows.
- **Local (secondary) dictionary**: per-row-group.  Contains values unique to that
  row group.

**Stored-index addressing**: encoded values in an enc=3 segment use a flat index
into the *concatenated* combined dictionary `[global entries] + [local entries]`.
Index `i < len(global)` → global dictionary; index `i ≥ len(global)` → local
dictionary at offset `i − len(global)`.  See `_load_one_string_dict` docstring in
`mssqlbak/columnstore/assembly/reader.py`.

**Field-name / semantic inversion WARNING** (`segment_meta.py`, `_SEG_*` constants):
The two dictionary-id fields in the segment metadata row are named with swapped
semantics in the code (a historical artifact of the reverse-engineering order):

| Code field | Offset | DMV column | Actual role |
|---|---|---|---|
| `prim_dict` | 52 | `primary_dictionary_id` | **Secondary** (per-RG) dict id |
| `sec_dict` | 56 | `secondary_dictionary_id` | **Primary** (global) dict id |

The reader concatenates `_load_one_string_dict(primary_blob) + _load_one_string_dict(secondary_blob)` (global first, local second) as confirmed by G40.  The field-name inversion is kept as-is in the code to avoid a larger rename; this note is the canonical reference.

**Fallback to v7 sorted pool**: when the combined dictionary is empty (both blob ids
< 0), the reader scans all available blobs for a version=7 sorted pool header
(`_find_v7_sorted_pool`) and uses it as a cross-segment shared dictionary.  This
path is exercised only when a legacy large-dict segment has no regular enc=3 dict
blob registered in `syscsdictionaries`.

#### Small / UTF-16 dictionary (enc=3, blob ≤ 65536 bytes) `[CORROBORATED]`

```
[+0]   uint8   version = 1
[+1:+5]  uint32 LE  entry_count
[+5 ..]  uint32 LE  byte_length  followed immediately by `byte_length` bytes of
                    UTF-16 LE content, repeated `entry_count` times
```

Decoded by `_parse_dict_strings` in `columnstore/decode/dict_string.py`.

**nchar/nvarchar sort-key encoding `[EMPIRICAL]`:** For `nchar`/`nvarchar`
columns, SQL Server may store sort keys rather than literal UTF-16LE strings in
the dictionary blob.  The sort-key bytes do not decode as readable text.
`_parse_dict_strings` returns whatever bytes are present; `_decode_enc3` treats
a dictionary index that falls outside the parsed entry list as a non-null
value (returning `empty_val`) rather than NULL, so the null count remains
correct even when the dictionary cannot be fully decoded.

#### Large dictionary (enc=3, blob > 65536 bytes) — xVelocity v4 hash dictionary `[CONFIRMED]`

**G44 `[CONFIRMED]`**: High-cardinality columnstore string columns store their
dictionary in the **xVelocity / VertiPaq dictionary format** — the storage engine
shared by SQL Server columnstore, SSAS Tabular, Excel Power Pivot, and Power BI.
The format family is documented by the normative `[MS-XLDM]` Open Specification
(§2.3.2 Column Data Dictionary) and by independent reverse-engineering projects
(PBIXray, Hugoberry, d0nk3yhm); see `CORROBORATION_SOURCES.md §7.6`.  The
columnstore on-disk blob is a **sibling** of the `[MS-XLDM]` `.dictionary` file —
the same conceptual model, but **not byte-identical**.

In `cs_lob_preamble2.bak` (1200 distinct 80-char `varchar(80)` strings) the
dictionary is split across two LOB blobs — a hash index and a sorted pool:

```
Hash dictionary (deinterleaved blob, observed id 2001) — the value → data-id index:
  [+0]   uint32 LE  version     = 4    ("version-4" marker; NOT the catalog `type`,
                                        which is 3 = "hash dict containing strings")
  [+4]   uint32 LE  entry_count = 1199  (last data-id; = distinct − 1)
  [+8]   uint32 LE  hash_slots  = 8192  (power-of-two hash-table size)
  [+12]  uint32 LE  ? = 2
  [+24 ..]  hash_slots × uint32 LE slots (6962/8192 non-zero), then a binary pool.
            The pool holds no plaintext: it is a hash index for value→id lookups,
            not for enumerating values by data-id.

Sorted pool (raw blob, observed id 23844) — the data-id → string mapping:
  [+0]   uint32 LE  version      = 7
  [+12]  uint32 LE  entry_count  = 1200  (total distinct strings)
  [+1945] Bookmark entry block — 194 entries × 103 bytes each:
    [entry+0]  uint16 LE  entry_size   = 103
    [entry+2]  char[80]   string       (80-char ASCII dictionary entry)
    [entry+82] byte[21]   metadata     (includes float32 step_minus_1 at entry+90)
      float32 at entry+90: step_minus_1 encodes the count of data-ids until the next
      bookmark (exclusive).  Accumulating: rank[k+1] = rank[k] + int(step_minus_1) + 1.
      The first bookmark is always rank 0 (alphabetically first); the last is rank 1199.
  [+21927] Pool section — compact sorted string store (6072 bytes including 4-byte size
           prefix).  Stores the full strings for a subset of entries in compressed or
           prefix-shared form; 37 full strings appear verbatim, the remainder require
           decoding the pool format (not yet implemented).
```

**Bookmark-based partial decoder (fallback).** `_parse_v7_sorted_pool()` in
`columnstore/decode/dict_xvelocity.py` reads the 194 bookmark entries, reconstructs each bookmark's
data-id via the step-minus-1 accumulation, and returns a partial dictionary list of
1200 slots where 194 known positions hold the correct string and the remaining 1006
return `None`.  Used as a fallback when `xmhuffman` is unavailable.

**Full Huffman decode via xmhuffman (implemented).** The post-hash-table region of
blob 2001 is a canonical-Huffman bitstream with a 128-byte `encode_array` at deint
offset 9700 and the compressed buffer at raw offset 9844.  `_decode_v4_huff_dict()`
in `columnstore/decode/dict_xvelocity.py` calls `xmhuffman.decode_page` with the **raw** (non-deinterleaved)
CBUF so that the 8-byte LOB separator at the 65536-byte chunk boundary is preserved
for xmhuffman's internal page-boundary handler.  Each decoded `bytes` result carries
a +2 symbol offset; stripping that offset and the leading 5-bit overhead byte recovers
the plaintext string.  Each entry's `data_id` is its **record-handle index `k`**
(its position in the per-entry record-handle array at `_V4_RH_OFF`), which is the value
enc=3 column segments store; the decoder returns the list indexed by `k`
(`[decoded_by_k[k] for k in range(n)]`).  **`data_id` is *not* the alphabetical rank** —
the dictionary is in native/insertion order.  An earlier version `sorted()` the strings,
which happened to pass `G44.json` (a set-membership / order-independent check) and the
`cci_char` case whose insertion order coincided with alphabetical order, but mis-decoded
`cci_varchar50` (low `'L'`, high `'Z'` inserted before A–Z fillers) — see Bug K3A in
`260618-2-enc3-bugs.md §7`.  Confirmed: 1200/1200 strings match the verifier sidecar.
Requires the `xmhuffman` Cython wheel (Python ≤ 3.11); falls back to the 194-bookmark v7
decoder when `xmhuffman` is absent.

**v4 record splitting — `_split_v4_record` full decision tree `[EMPIRICAL — fix ea35000, 2026-06-30]`**

`_split_v4_record(r, *, from_python_fallback, is_escape_record)` in `dict_xvelocity.py`
parses one decoded buffer `r` (bytes) into a list of strings. Two decoders produce `r`
and they behave differently; a third subtype (escape handles) adds a third case.

**Decoded `decoded0 = r[0] - _V4_CHAR_OFFSET` (signed; value < 0 means non-printable overhead byte)**

```
Case 0 — empty buffer (r == b""):
    record_tag("v4split:empty")
    return [""]
    — SQL Server uses an all-1s Huffman padding code as a handle terminator.
      Emit one empty-string slot (not []) so the dictionary slot count stays correct.
      Observed: tpcxbb has 193 such handles.

Case 1 — from_python_fallback=True AND decoded0 >= 0x80 AND is_escape_record=False
         ("long-VARCHAR non-escape via Python fallback"):
    record_tag("v4split:varchar-long-py")
    content_end = 2 + decoded0
    return [_decode_payload(r[2:content_end] if len(r) >= content_end else r[2:])]
    — r[0] encodes exact payload length; slice precisely, discard trailing garbage bytes
      produced by the Python fallback's all-1s sentinel overrun.

Case 2 — from_python_fallback=True AND (decoded0 > 0 OR is_escape_record=True)
         ("chunked-greedy via Python fallback, also all escape handles"):
    Greedy while loop: pos=0; read slen = r[pos]-off; advance pos+1; append r[pos:pos+slen]; pos+=slen.
    Break if slen<=0 or pos+slen > len(r).
    If any chunks assembled: record_tag("v4split:varchar-chunked-py"); return ["".join(chunks)]
    — Escape handles (is_escape_record=True) encode the full string as multiple
      length-prefixed chunks; r[0] is only the first chunk's length.  They always
      use this path even when decoded0 >= 0x80.

Case 3 — from_python_fallback=False AND decoded0 >= 0
         (xmhuffman native path; multi-packed record handles possible):
    Two-byte varlen prefix check: if d0=r[pos]-off >= 0x80 AND d1=r[pos+1]-off >= 0x80:
        payload = r[pos+2 : pos+2+d0]; pos += 2+d0
        (second overhead byte d1 is metadata, not part of length)
    Single-byte prefix: slen = r[pos]-off; payload = r[pos+1 : pos+1+slen]; pos += 1+slen
    Mixed-packed edge: if slen >= 0x80 and next byte also >= 0x80 after offset:
        payload = r[pos+1:]; break  (final value with two-byte varlen prefix follows short entries)
    record_tag("v4split:varchar-short") on success.
    Returns [] (empty, handled by shortfall padding) if parse fails (ok=False).
```

**`is_escape_record`** is set when the handle index `k` appears in `escape_ks` — a set
populated when `_huff_decode_page_py` returns `escape_idx_set` for handles whose first
decoded symbol is a Huffman escape prefix code. This flag routes all escape handles
through Case 2 regardless of `decoded0`.

**Catalog `type` vs on-disk `version`.** `sys.column_store_dictionaries.type`
documents `1 = hash int, 3 = hash string, 4 = hash float` (Microsoft Learn).  The
leading `uint32 = 4` in the hash-dictionary blob is the **format version**, not the
catalog type: a `varchar` column has catalog `type = 3` yet an on-disk `version = 4`.

**PBIX sentinel bytes absent; xmhuffman works via LOB boundary alignment.**
The PBIX paged-Huffman page sentinels (`0xDDCCBBAA` / `0xCDABCDAB`) are absent from
these blobs (zero matches confirmed).  Nevertheless `xmhuffman.decode_page` decodes
all 1200 strings correctly when given the **raw** (non-deinterleaved) CBUF: the
8-byte LOB separator at the 65536-byte chunk boundary coincides with xmhuffman's
internal per-page skip length, so boundary alignment works without the PBIX sentinel.
The `encode_array` and compressed-bitstream layout are identical to the `[MS-XLDM]`
model; only the sentinel is absent.

**Verifier sidecar.** `tests/fixtures_2022/G44.json` holds all 1200 data-id → string
mappings, built from `SELECT id, long_str FROM cs_lob_preamble ORDER BY long_str`
against `cs_lob_preamble2.bak`.  The 4-test suite in `test_columnstore.py`
(`test_g44_large_dict_*`) validates row count, minimum-coverage floor (≥ 194),
verifier membership for all decoded strings, and — when `xmhuffman` is present —
full 1200-string decode against `G44.json`.  Fixture: `cs_lob_preamble2.bak`
(1200 rows, clustered columnstore index).

### 7.7 enc=5 (raw/off-row) `[CORROBORATED]`

enc=5 stores fixed-size raw bytes per value.  The segment blob (after
`_unwrap_archive_blob` for cmprlevel=4) is dispatched to one of four formats
by `_decode_enc5` (`columnstore/decode/enc5_raw.py`).  Constants:
`_ENC5_SENTINEL = b"\xfe\xff"`, `_ENC5_HDR_ITEM_SZ = 92`,
`_ENC5_HDR_N_NONNULL = 94`, `_ENC5_DATA_OFFSET = 98`.

**Format detection order:**

1. If `h92 = u16@92 == 0` → Format C or D regardless of whether `\xfe\xff`
   appears later in the blob (the XPRESS payload can contain false-positive
   sentinel bytes; h92=0 takes precedence).
2. Else if `\xfe\xff` is absent → Format A.
3. Else → Format B (`\xfe\xff` sentinel is present and h92 ≠ 0).

#### Format A — uncompressed, header-encoded `[EMPIRICAL]`

No sentinel.  `h92 ≠ 0` and `h92 ≠ 0xFFFF`.

```
u16@92  item_size    (bytes per stored value; e.g. 9 for datetimeoffset(3))
u16@94  n_non_null
[+98 .. +98 + n_non_null × item_size)  non-null values, contiguous
[+98 + n_non_null × item_size .. ]     implicit NULLs to fill n_rows
```

#### Format B — uncompressed, sentinel-indexed `[EMPIRICAL]`

`\xfe\xff` sentinel present; `h92 = 0xFFFF` or `h92 ≠ 0` and sentinel found.

Non-null values are stored consecutively from offset 98.
A u16 start-offset index surrounds the sentinel:

```
[+98 ..]                   non-null values at byte offsets 0, item_size, 2×item_size, …
[before sentinel]          before-sentinel index: descending start-offsets for
                            n_after_null rows, ending with 0x0000
\xfe\xff                   sentinel (_ENC5_SENTINEL)
[after sentinel]           after-sentinel index: descending start-offsets for
                            n_before_null rows, ending with 0x0000
```

Derivation:
```
n_before_null   = len(after-sentinel entries) - 1   (excluding trailing 0)
item_size       = after-sentinel[-2]                 (last non-zero entry)
n_after_null    = (sentinel_off - 98 - n_before_null × item_size) / (item_size + 2)
n_null          = n_rows - n_before_null - n_after_null
```

### 7.8 CCI rowgroup lifecycle: tombstone suppression and delete bitmap `[EMPIRICAL]`

Two internal structures track the logical state of compressed rowgroups — which
rowgroups are still live and which individual rows within a live rowgroup have
been deleted.  Both are decoded by `columnstore/assembly/reader.py` before row data is yielded.

#### 7.8.1 Tombstone rowgroup filter

`ALTER INDEX … REORGANIZE` on a CCI merges small compressed rowgroups into a
single larger one.  SQL Server creates a new `syscscolsegments` entry with a
higher `seg_id` for the merged rowgroup and marks the source rowgroups as
`TOMBSTONE`, but both the tombstoned entries and the merged entry remain in
`syscscolsegments` until a background cleanup runs.  Without filtering,
mssqlbak would double-count the merged rows.

**Detection:** `sysrowsets.rcrows` for the `cmprlevel=3` rowset holds the
authoritative total row count across all live compressed rowgroups for that
`hobt_id`.  If the sum of all decoded segment `n_rows` values exceeds `rcrows`,
tombstoned rowgroups are present.

**Resolution (greedy descent):** rowgroups are sorted by `seg_id` descending
(newest first — merged rowgroups always have higher `seg_id` than their
sources).  Groups are included until the accumulated row count reaches `rcrows`;
remaining groups are dropped.

**ARCHIVE partition passthrough:** groups whose `hobt_id` is not present in the
`cmprlevel=3` `sysrowsets` set (e.g. `cmprlevel=4` COLUMNSTORE_ARCHIVE rowsets)
are not subject to tombstone merging and are kept unconditionally.  Without this
guard, an ARCHIVE partition that coexists with a regular CCI partition on the
same table would be incorrectly dropped.

Evidence: `cci_reorganize_full.bak` (post-REORGANIZE CCI, 1000 live rows + 200
tombstoned rows from the pre-merge rowgroup) — SS2017/2019/2022/2025.

#### 7.8.2 CCI delete bitmap

After a CCI rowgroup is compressed, subsequent `DELETE` statements against the
CCI table do not remove the stored row from the segment blob.  Instead, SQL
Server records each deletion in a separate `cmprlevel=2` (PAGE-compressed) B-tree
rowset owned by the same `object_id`.  Each CD record in this rowset has two
fields:

```
col[0]   excess-BE-encoded integer   seg_id of the compressed rowgroup
col[1]   excess-BE-encoded integer   0-based row position within that rowgroup
```

`_cd_excess_be_int` decodes excess-big-endian CD integers.  For each
`(seg_id, row_pos)` pair, the row at `row_pos` in the decoded segment for
`seg_id` is suppressed before being yielded.  In the Arrow path
(`read_columnstore_batches`) the suppression is applied with
`pa.RecordBatch.filter()` using a boolean mask.

**Scope:** only `cmprlevel=2` rowsets belonging to the same `object_id` as the
CCI table are scanned; rowsets with any other `cmprlevel` are skipped.

Evidence: `filtered_ncci_full.bak` (400 inserted rows, 200 deleted via direct
`DELETE`) and `cci_reorganize_full.bak` — SS2022.

---

