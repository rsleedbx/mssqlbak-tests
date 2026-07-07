# Rowstore Compressed — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `ROWSTORE_COMPRESSED`
**Set by:** `read_table_rows` (`mssqlbak/rows.py:860`) when `cmprlevel == 1` (ROW) or `cmprlevel == 2` (PAGE)
**Catalog signal:** `sysrowsets.cmprlevel in (1, 2)`
**Decode entry point:** `rows.py:860` → `decode_record()` → CD record path → `rowcompress.decode_compressed_value()`

---

## 2. Initialization

Page Compression Info (CI) structure precedes rows on PAGE-compressed pages. ROW compression omits it. SCSU/UTF-16LE discriminator applies to nchar/nvarchar columns.

---

## 3. Record structure

### 3.4 CD record (ROW/PAGE compression, `cmprlevel = 1 or 2`) `[CORROBORATED]`

Verified against `compressioncoverage_full.bak` and cross-checked with
OrcaMDF.

```
[+0]  uint8  header
              bit 0x01 → CD record (must be set)
              bit 0x02 → versioning info present (14-byte trailer; ignored)
              bits 0x1C → record type (not decoded)
              bit 0x20 → long-data region follows short-data region
[+1]  column count: 1 byte; if high bit set (0x80), uint16 LE at [+1:+3]
[+ptr .. ptr + ceil(ncol/2))  CD nibble array
              4 bits per column: even column = low nibble, odd = high nibble
              Nibble meanings:
                0x0  NULL
                0x1  0 bytes (zero / empty)
                0x2..0x9  1..8 in-line bytes in short-data region
                0xA  long-data region entry
                0xB  bit TRUE (no bytes; literal true for bit columns)
                0xC  PAGE-dictionary symbol (1-byte index in short-data region)
```

**Short-data region** (immediately after CD array):
- Columns are grouped into clusters of 30 (`_CLUSTER`).
- Each cluster except the last is preceded by a 1-byte length.
- Each column's bytes (length given by its nibble) are contiguous within
  its cluster.

**Long-data region** (if `header & 0x20`):
```
[+0]  uint8   flag byte  [UNKNOWN — reserved/future use]
[+1]  uint16 LE  count   number of long entries
[+3]  uint16 LE[count]   cumulative end offsets
                          top bit 0x8000 = complex/off-row LOB
[+3+2*count]  (count-1)//30 + 1 cluster-count bytes  [HEURISTIC — semantics unclear]
[+above]  long entry payloads, contiguous
```

**G17/G18 `[EMPIRICAL]`**: 40-column wide tables (`cmp_row_wide`, `cmp_page_wide`) with ROW and PAGE compression decode all 50 rows and all 40 data columns correctly via `compressioncoverage_full.bak` (SS2022).  The parser navigates the long-data region transparently.  Flag byte and cluster-count semantics remain unconfirmed by DBCC PAGE verifier; marked empirical (no observed counter-example).

**Integer encoding under ROW compression** `[EMPIRICAL]`:
Fixed-width integers (`smallint`, `int`, `bigint`, `money`, `smallmoney`) are
stored *excess-encoded big-endian*, minimal-width:
```
value = int.from_bytes(data, "big") - 2^(8*len(data) - 1)
```
Empty bytes (`_CD_ZERO`) → 0.

**Temporal encoding under ROW compression** `[EMPIRICAL]`:
The 2008+ temporal types (`date`, `time`, `datetime2`, `datetimeoffset`) store
their ordinary little-endian on-disk bytes with trailing zero (high-order)
bytes trimmed.  Decompressed by right-padding to the fixed width.

**Float / `smalldatetime` encoding** `[EMPIRICAL]`:
Stored as their ordinary LE on-disk bytes with **leading** zero (LSB-side)
bytes stripped.  Decompressed by prepending zeros.

> **G19 resolved:** `smalldatetime` is decoded as `uint16 days + uint16 minutes`
> (the same two-field integer layout as the uncompressed path, not a float-path
> shortcut).  Confirmed by `spec_probe rowcompress` against
> `compressioncoverage_full.bak` — `cmp_page.sdt` column round-trips correctly.

**`nchar`/`nvarchar`/`sysname` encoding under ROW/PAGE compression** `[EMPIRICAL]`:

These types are **NOT** stored as UTF-16LE.  SQL Server applies
**SCSU** (Unicode Technical Standard #6, "Standard Compression Scheme for
Unicode") on a per-value basis within the CD record's short- or long-data
region.

Core SCSU mechanisms observed in SQL Server output:

| Mechanism | Byte(s) | Effect |
|---|---|---|
| Single-byte window 0 (ASCII) | `0x00–0x7F` | passthrough; code point = byte |
| `SD0–SD7` (define+select dynamic window) | `0x18–0x1F` + 1-byte offset | sets one of 8 dynamic windows; subsequent high-bit bytes decode against it |
| `SDX` (define extended window, single-byte mode) | `0x0B` + 2-byte value | sets window base to `((value & 0x1FFF)<<7) + 0x10000`; accesses Plane 1–16 (astral) |
| `SQ0–SQ7` (quote one char from window pair) | `0x01–0x08` + 1 byte | emits one code point from the static/dynamic pair for the given window index |
| `SQU` (quote Unicode char, single-byte mode) | `0x0E` + 2 bytes (BE) | emits one UTF-16 code unit; stays in single-byte mode |
| `SC0–SC7` (select dynamic window) | `0x10–0x17` | switches active window; no character emitted |
| `SCU` (enter Unicode mode) | `0x0F` | subsequent bytes are big-endian UTF-16 pairs until a UC0–UC7 or end of stream |
| `UC0–UC7` (exit Unicode mode) | `0xE0–0xE7` | returns to single-byte mode, selects dynamic window |
| `UD0–UD7` (define window in Unicode mode) | `0xE8–0xEF` + 1-byte offset | defines a dynamic window without exiting Unicode mode |
| `UQU` (quote Unicode char, Unicode mode) | `0xF0` + 2 bytes (BE) | emits one UTF-16 code unit; stays in Unicode mode |
| `UDX` (define extended window, Unicode mode) | `0xF1` + 2-byte value | defines an extended window (Plane 1–16); returns to single-byte mode |
| `URS` (reserved) | `0xF2` | **reserved**; raises `ScsuError` — must never appear in SQL Server output |

**Reserved window-offset bytes** `[SPEC]`: In single-byte mode, `SDn` operand bytes in the range `0xA8–0xF8` are reserved by TR6 and raise `ScsuError`.  The operand `0x00` is also reserved (explicit zero is not a valid window).  Offset bytes `0x01–0xA7` map to BMP windows; bytes `0xF9–0xFF` map to seven fixed windows (Latin-1 supplement, extended Latin, Greek, Cyrillic, Hiragana, Katakana, half-width Katakana).

**Astral code points** `[EMPIRICAL]`: Extended-window instructions (`SDX` in single-byte mode; `UDX` in Unicode mode) set a dynamic-window base at or above `U+10000`.  When a high-byte character byte `0x80–0xFF` is subsequently decoded against such a window, the resulting code point exceeds U+FFFF and is split into a UTF-16LE surrogate pair.  Confirmed functional via unit test: SDX with value `0x0000` → base `0x10000`; byte `0x80` → U+10000 (𐀀 Linear B Syllable B008 A).  Surrogate pairs emitted by SQL Server's SCSU encoder in Unicode mode (e.g. 😀 = `D8 3D DE 00`) decode correctly via the UTF-16LE combiner.

**SQL Server trailer byte** `[EMPIRICAL]`: SQL Server's SCSU encoder appends a
trailing byte to the end of many encoded values — including values whose stream
ends in **Unicode mode** (e.g. CJK, Arabic, Hebrew).  The most common trailer
is `0x10` (SC0, no-op); `0x02` (SQ1) is also confirmed in `StackOverflowMini.bak`
Users table (stream `43 00 0f 1d 80 02 8f 02`).  Any single byte value can appear.

**Terminal-byte edge cases** `[EMPIRICAL]`:

| Trailing byte in Unicode mode | Interpretation | Action |
|---|---|---|
| `UC0–UC7` (`0xE0–0xE7`) | switch active single-byte window; exit Unicode mode | apply window change (no char emitted) |
| `URS` (`0xF2`) | reserved — invalid in any position | raise `ScsuError` |
| Any other byte (e.g. `0x10` SC0, `0x02` SQ1, `0xF0` UQU, `0xF1` UDX) | lone byte — cannot form a complete UTF-16 pair | ignore (no char emitted) |

`UDX` and `UQU` each require 2 additional operand bytes; when only 1 operand byte remains in the stream (UDX/UQU + 1 orphan), both bytes are skipped to prevent the orphan from being reprocessed in single-byte mode.

**Confirmed scripts**: ASCII (window 0 passthrough), Cyrillic (`SD+offset`
then high-bit bytes for each character) — both confirmed against
`compressioncoverage_full.bak`.  CJK and Arabic (Unicode mode via `SCU`)
confirmed against `compressioncoverage_full.bak` after fixture extension
(see BAK_SPEC_FIXTURES.md §SCSU).

### 3.6 Page Compression Info (CI) structure `[CORROBORATED]`

PAGE compression (`cmprlevel = 2`) may add a per-page **compression info**
(CI) structure between byte 96 (first post-header byte) and the first record
offset (`min_slot`).  The CI is present when that gap exists, byte 96 has bit 0
clear (so it is not a CD data record), and the `CI_HAS_ANCHOR_RECORD` flag
(bit 1, `0x02`) is set.

Byte 96 is a **flags** byte, not a fixed magic value:

| Flag | Bit mask | Meaning |
|------|----------|---------|
| `CI_HAS_ANCHOR_RECORD` | `0x02` | an anchor record follows the header |
| `CI_HAS_DICTIONARY`    | `0x04` | a dictionary section follows the anchor |
| *(bit 0)*              | `0x01` | **must be clear** — set means it's a CD data record, not a CI |
| *(bits 3–7)*           | `0xF8` | unobserved; reserved/ignored by the parser |

The two observed values are therefore `0x06` (anchor **and** dictionary) and
`0x02` (anchor only).  The `dict_offset` field is present **only** when the
dictionary flag is set, so the header is 7 bytes with a dictionary and 5 bytes
without (the anchor record shifts accordingly):

```
[+0]   uint8   CI header flags (0x06 = anchor+dict, 0x02 = anchor only)
[+1]   uint16 LE  PageModCount
[+3]   uint16 LE  dict_offset       (present ONLY when CI_HAS_DICTIONARY)
[+N]   uint16 LE  total_ci_size     (N = 5 with a dictionary, 3 without)
[+M .. anchor_end)  anchor record: a CD record (§3.4) giving each column's
                    prefix value.  M = 7 with a dictionary, 5 without.
                    anchor_end = dict_offset (with dict) or total_ci_size (without)
[dict_offset ..]  dictionary section (only when CI_HAS_DICTIONARY):
                      uint16 LE  count
                      uint16 LE[count]  cumulative end offsets from dict_start
                      entries: each is [uint8 prefix_len][suffix_bytes]
                               (prefix_len bytes from anchor, then suffix)
```

#### 3.6.1 Complete flag-byte space

The four structurally distinct cases — determined solely by bits 1 and 2 — are:

| Bits 2:1 | Canonical byte | Anchor | Dict | Observed | Parser disposition |
|----------|---------------|--------|------|----------|--------------------|
| `00` | `0x00` / `0x08` / … | — | — | No | Plain page (returns `None`) |
| `01` | `0x04` / `0x0c` / … | — | ✓ | No | `None` — no anchor flag; dict-only is incoherent (no prefix base for `_CD_ZERO`) |
| `10` | **`0x02`** | ✓ | — | **Yes** | Anchor-only CI; 5-byte header |
| `11` | **`0x06`** | ✓ | ✓ | **Yes** | Anchor + dictionary CI; 7-byte header |

Any byte with bits 3–7 set but bits 1–2 matching one of the above cases (e.g.
`0x0e`, `0x22`, `0xa6`) is parsed identically to the canonical byte for that
case; the upper bits are masked off and ignored.

**Exhaustive survey** — 32 fixtures across SS2017/2019/2022/2025 (engineered)
and seven real-world databases (WWI, Contoso, AdventureWorks, etc.) — found only
`0x02` and `0x06`.  No value with bits 3–7 set, and no `0x04` (dict-only), was
ever emitted by any SQL Server version.  SQL Server's PAGE compression engine
always writes an anchor record, so `0x04` (no anchor) is structurally incoherent
and effectively unreachable.

**G1A `[CORROBORATED]`**: The `0x06` (anchor+dictionary) shape was confirmed
against `compressioncoverage_full.bak` (SS2022).  The `0x02` (anchor-only) shape
was reverse-engineered from `pagecomp_anchor_full.bak` and **cross-checked byte
for byte against `DBCC PAGE(..., 3)`**, which reports
`CI Header Flags = CI_HAS_ANCHOR_RECORD`, `CompressionInfo size = 80`, and an
`AnchorRecord ... (COMPRESSED) PRIMARY_RECORD` of size 75 starting at CI offset 5
— i.e. no `dict_offset` field.  The anchor-only shape is the common case for
temporal history tables (e.g. WideWorldImporters `*_Archive`); failing to
recognise it caused anchored columns (`_CD_ZERO`) to decode as `0` /
`0001-01-01` / NULL.  ROW-compressed pages (`cmprlevel = 1`) have no CI structure
and byte 96 is part of the first data record.

---

