# Cell Discrepancy Follow-up Plan
_Written 2026-06-30 — pick up here tomorrow_

## Background

`docs/correctness_coverage_fixtures_realworld.md` shows **11 failing fixtures**.  
All have correct row/null/min-max counts — the failures are exclusively **cell-level digest mismatches** for specific columns.  

The Python-fallback changes committed today (`ea35000`) fixed the synthetic fixture regression but left the root tpcxbb issue open.

---

## Open Issues (priority order)

### 1. `tpcxbb_1gb.bak` — `dbo.product_reviews.pr_review_content`

**Symptom:** 62,506 rows decode as `''` instead of real review text; reference has only 5 empty rows.

**Root cause (confirmed):** The V4 Huffman dictionary for this column uses an _underfull_ tree (Kraft sum ≈ 0.999939 — only 2 unused 15-bit entries: codes 32766 and 32767). `xmhuffman` rejects the tree outright. Our `_huff_decode_page_py` fallback hits code 32766 on the _first_ bit of 193 handles and stops immediately, producing `b""`.  

Those 193 handles collectively account for the 62,506 wrong-empty rows (~323 rows each on average reference those data_ids).

**Why do 193 handles start with code 32766?**  
Unknown. All `cbuf_raw` offsets are even (swap alignment is fine). For page 32 (the one page xmhuffman _can_ decode) the Python fallback gives identical results — canonical code ordering matches. So the ordering is correct. The 193 handles may genuinely begin with bits that look like 32766 _before_ any valid code, which could mean:

- The bit boundary (`bos`) is off by one or two for those handles (parse the handle array more carefully).
- SQL Server uses a "relaxed" decode — when an invalid code is encountered it falls back to the next-shorter code length.
- Those 193 handles encode a "jump" marker (e.g., `FFF...E` prefix = "this slot is present in the sorted pool but the string is NOT stored in the Huffman stream; use fallback").

**Suggested investigations (in order):**

1. **Inspect raw bits before and after `bos[k]`** for a handful of the 193 handles. Check if the 15 bits immediately _before_ bos are also `111...1` (i.e., the padding of the _previous_ handle runs right up to and past the boundary).  
2. **Try `bos[k] + 1` and `bos[k] - 1`** as the start point — maybe there's an off-by-one in how bos values are parsed from the deinterleaved array vs raw bytes.  
3. **Check handle k=5898** which has `bos=0` (handle at the very start of the page) — that should decode cleanly if bos=0 truly means "bit 0 of the compressed buffer". If it also decodes as empty, that's a strong sign the decoder itself is wrong.

---

### 2. `WideWorldImporters-Full.bak` (and Standard/old variants) — `Application.People.HashedPassword`

**Symptom:** 19,997/19,998 cells match; digest wrong for both `People` and `People_Archive`.

**Root cause (unknown):** One cell is missing. `HashedPassword` is likely `VARBINARY(32)` (SHA-256 hash). VARBINARY in CCI is stored as dictionary-encoded binary or as a direct blob.

**Suggested investigation:**

1. Find the 1 row where `HashedPassword` is null/wrong in our decode vs the reference parquet.  
2. Check whether it is the last row of a row group (common boundary bug) or a specific value (e.g., all-zero hash or a hash that starts with a control byte).

---

### 3. `StackOverflowMini.bak` — `dbo.Posts.Body` / `dba.stackexchange.com.bak` — `dbo.Comments.Text`, `dbo.PostHistory.Text`

**Symptom:** Cell counts all match; digest fails. Likely `NVARCHAR(MAX)` or `VARCHAR(MAX)` columns with large LOBs.

**Root cause (unknown):** The canonicalization or decoding of large text bodies drifts from the reference. Could be:
- Unicode normalization (NVARCHAR stored in UTF-16LE, we decode as latin-1 then re-encode).
- Trailing whitespace or NUL differences.
- LOB stitching joining pages in wrong order for some rows.

**Suggested investigation:**

1. Find 1 differing row (compare decoded value vs reference parquet byte-by-byte).
2. Check column data type — if NVARCHAR(MAX), verify the UTF-16LE decode path in `reader.py` for LOB-stitched cells.
3. Check if it's a fixed canonicalization mismatch (e.g., we strip trailing NULs but shouldn't, or vice versa).

---

### 4. `NYCTaxi_Sample.bak` — `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, `dropoff_latitude`

**Symptom:** All four are `float` columns; digest fails.

**Root cause (likely):** IEEE 754 double encoding in CCI. These columns are likely stored as `REAL` (float32) or `FLOAT` (float64). Our canonicalization of floats may differ from the reference (e.g., we emit `nan` vs `NULL`, or we round differently).

**Suggested investigation:**

1. Check column data types (`REAL` vs `FLOAT`).
2. Compare a sample of decoded float values to reference parquet values.
3. Check if any `NaN`, `Inf`, or `-0.0` values appear and how we handle them.

---

### 5. `GeneralHospital.bak` — `dbo.SurgicalCosts."Surgical Resource Cost"`

**Symptom:** Digest fails for a single oddly-named column with a space in the name.

**Suggested investigation:**

1. Check data type and a sample of values.
2. The column name has a space — confirm the catalog lookup matches correctly.
3. Look at the correctness report for any count/null anomalies.

---

## State of `_split_v4_record` / `_huff_decode_page_py` (as of today's commit)

- **Synthetic fixture regression:** Fixed. Handle k=8183 (two packed long-VARCHARs, xmhuffman) correctly produces 2 entries again.
- **Python fallback long-VARCHAR content:** Fixed. We now extract `r[2:2+d0]` instead of all of `r[2:]`, so reviews are no longer padded with garbage.
- **193 empty handles (tpcxbb):** NOT fixed. These handles still decode as `""`. The underlying issue (why their first bits map to unused code 32766) is unresolved.
- **Empty-r shortfall:** Fixed. `b""` → `[""]` so the shortfall check doesn't reject the whole dictionary.

## Quick wins to try first

Before diving into tpcxbb's underfull-tree mystery, the WideWorldImporters 1-cell miss (issue 2) and the digest-only failures (issues 3–5) are likely simpler fixes that can improve the pass rate without needing new Huffman theory.

Recommended order:
1. WideWorldImporters `HashedPassword` (1 cell missing — probably a boundary row bug)
2. NYCTaxi float columns (likely a float canonicalization issue)
3. GeneralHospital single column
4. StackOverflow / dba.stackexchange text digest (large-LOB canonicalization)
5. tpcxbb `pr_review_content` (deep underfull Huffman tree investigation)
