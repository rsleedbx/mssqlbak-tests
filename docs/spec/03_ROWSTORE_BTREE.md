# Rowstore B-Tree — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `ROWSTORE_BTREE` (spec abstraction, not a code symbol)
**Set by:** `read_table_rows` (`mssqlbak/rows.py:1132`) when `table.compression == 0` and `table.index_id >= 1`.
Routing is driven by `table.compression` (`rows.py:1194`) and `table.is_memory_optimized` (`extract.py:494`).
**Catalog signal:** `sysrowsets.cmprlevel == 0`, `sys.indexes.type in (1, 2)` (clustered or nonclustered)
**Decode entry point:** `rows.py:1132` → `decode_record()` (`records.py:69`) → FixedVar path

---

## 2. Initialization

Same FixedVar record format as ROWSTORE_HEAP. Clustered key columns are part of the row. See `02_ROWSTORE_HEAP.md` §3 for the record layout — it is identical.

---

## 3. Record structure

> **Cross-reference:** For the base FixedVar record layout, see `02_ROWSTORE_HEAP.md` §3 — the format is identical.

### 3.5 Always Encrypted (AE) ciphertext in string columns `[CORROBORATED]`

**Feature introduced**: SQL Server 2016.  Fixture: `AdventureWorks2016_EXT.bak`
(`CustomerPII.SSN`, `CustomerPII.CreditCardNumber`).

When a table column is protected by **Always Encrypted**, SQL Server stores
**opaque AEAD ciphertext** on disk in the column's physical storage slot.
The column type (nvarchar, varchar, int, datetime, …) declared in the schema
is retained as-is in `syscolpars`, but the on-disk bytes are the ciphertext,
not the plaintext.  SQL Server itself cannot decrypt the data; only a client
application with the Column Encryption Key (CEK) can do so.

**Ciphertext wire format** (algorithm `AEAD_AES_256_CBC_HMAC_SHA_256`):

| Offset | Size | Field |
|--------|------|-------|
| 0 | 1 | version byte = `0x01` |
| 1 | 32 | HMAC-SHA-256 authentication tag |
| 33 | 16 | AES-CBC IV |
| 49 | N×16 | AES-CBC ciphertext (plaintext padded to 16-byte AES blocks) |

Total length = 49 + N×16 bytes, which is **always odd** (49 is odd; N×16 is even).

**Parser behaviour**: `mssqlbak` cannot decrypt AE ciphertext and returns
``None`` (SQL NULL) for all Always Encrypted column values.

**Detection at catalog level** `[EMPIRICAL]`: SQL Server assigns a binary
(**BIN2**) collation to the physical storage of AE-encrypted string columns.
BIN2 collation IDs are anomalously small compared to standard collation IDs
(which sit in the high-hundred-thousands to millions range).  Observed value
in `AdventureWorks2016_EXT.bak`: `collation_id = 2056 (0x0808)` for `SSN` and
`CreditCardNumber` versus `872468488 (0x3400D008)` for the non-encrypted
nvarchar columns in the same table.  The parser uses `0 < collation_id < 0x4000`
(`_AE_COLLATION_MAX = 0x4000`, `catalog.py:96`) for string type IDs
`{99, 167, 175, 231, 239}` as the catalog-level AE indicator
(`Column.is_encrypted = True`).

**Detection at decode level** (runtime safety net): valid UTF-16-LE data always
has **even** byte length; AE ciphertext is always **odd**.  Any nchar/nvarchar
raw blob with odd byte length is treated as AE ciphertext and decoded to
``None`` without attempting UTF-16-LE decode (see `types._decode_nchar`).

**Guess register**: G53 (see [Guess Register §10](00_MASTER.md#what-is-guessed--the-guess-register)).

---

## 4. B-tree descent to leaf `[EMPIRICAL]`

Source: `rows.py: _leftmost_leaf` / `catalog.py: _Bootstrap._leftmost_leaf_from_root`.

A clustered B-tree is descended by following the child pointer in the first
slot of each non-leaf index page until a leaf data page is reached:

```
loc = root_page_pointer        # (page_id, file_id) from sysallocunits.pgroot
while page.header.m_type == 2:  # INDEX page
    rec = page.record(0)         # first slot in the index page
    child_page_id  = struct.unpack_from("<I", rec, len(rec) - 6)[0]
    child_file_id  = struct.unpack_from("<H", rec, len(rec) - 2)[0]
    loc = (child_page_id, child_file_id)
# Now on a leaf data page; follow next_page chain
```

The child pointer is at `rec[-6:]` (last 6 bytes) for uncompressed index
records (`pminlen - 6`).  For CD (compressed) index pages the nibble array
at position 7 in the CD header marks the child-pointer column.  Once on a leaf,
follow the `next_page` chain to enumerate all leaf records.

See also `01_CATALOG.md §4.5` for the catalog bootstrap variant.

