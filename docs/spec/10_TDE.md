## 10. Transparent Data Encryption (TDE)

### Scope

This section covers **database-level TDE** backups — a database with TDE enabled
that was backed up with a plain `BACKUP DATABASE … TO DISK` (no `WITH ENCRYPTION`).
In that case the MTF framing and SQL config stream are **plaintext**; only the
8 KB MDF pages are AES-CBC encrypted.

Two scenarios remain **out of scope** and still raise
`mssqlbak.errors.EncryptedBackupError`:

| Out-of-scope scenario | Description |
|-----------------------|-------------|
| Backup-level encryption | `BACKUP … WITH ENCRYPTION` — the entire backup stream including MTF is encrypted with an undocumented proprietary scheme |
| EKM / asymmetric-key DEK | Database Encryption Keys protected by an Extensible Key Management provider or asymmetric key |
| 3DES DEK (pre-2012) | Legacy `ALGORITHM = TRIPLE_DES_3KEY` DEK; `_RSA_CIPHERTEXT_SIZES` check will reject the wrong-size ciphertext |

Source package: `mssqlbak/tde/` — three modules (`keys.py`, `dek.py`, `page.py`).
Optional dependency: `cryptography` (`pip install cryptography`).

---

### 10.1 Key loading `[EMPIRICAL]`

Source: `tde/keys.py: load_tde_key`, `TdeKey`

```
TdeKey
  private_key:       RSAPrivateKey (cryptography.hazmat)
  cert_thumbprint:   bytes | None  (20-byte SHA-1 fingerprint)
  key_size_bits:     int           (typically 2048 for SQL Server certs)
```

Input is a PKCS#12 / PFX file exported from SQL Server:

```sql
BACKUP CERTIFICATE [cert_name]
TO FILE = N'/tmp/cert.pfx'
WITH FORMAT = 'PFX',
     PRIVATE KEY (ENCRYPTION BY PASSWORD = N'<password>');
```

`load_tde_key(pfx_path, password)` calls
`cryptography.hazmat.primitives.serialization.pkcs12.load_pkcs12`, extracts
the RSA private key, and computes the SHA-1 thumbprint with
`certificate.fingerprint(SHA1())`.  PVK (Microsoft proprietary format) is not
supported.

The `cert_thumbprint` is required for DEK discovery (§10.2).  A key-only PFX
(no certificate) leaves `cert_thumbprint = None` and causes `extract_dek` to
raise `ValueError`.

---

### 10.2 DEK extraction `[EMPIRICAL]`

Source: `tde/dek.py: extract_dek`, `_find_dek_descriptor`, `_rsa_decrypt_pkcs1v15`, `_parse_plaintextkeyblob`

SQL Server writes the RSA-encrypted DEK descriptor into the MTF backup header
region.  The scan range is **`0x2000`–`0xC000`** relative to the start of the
`.bak` file (`_DEK_SCAN_START`, `_DEK_SCAN_END`).

**DEK descriptor layout** (G58 `[EMPIRICAL]`):

```
[off -4]  uint32 LE  : thumbprint_length  (= 20 for SHA-1)
[off  0]  bytes      : certificate thumbprint  (thumbprint_length bytes)
[off +20] uint32 LE  : ciphertext_length   (128 / 256 / 384 / 512 bytes)
[off +24] bytes      : RSA ciphertext      (ciphertext_length bytes, little-endian)
```

Valid `ciphertext_length` values (`_RSA_CIPHERTEXT_SIZES = {128, 256, 384, 512}`)
correspond to RSA-1024 through RSA-4096 key sizes.

**RSA byte-order correction**: Windows CNG (`BCryptEncrypt`) stores RSA output in
**little-endian** byte order; OpenSSL / PKCS#1 expects big-endian.  The ciphertext
blob is byte-reversed before passing it to `RSAPrivateKey.decrypt(..., PKCS1v15())`.
Source: `_rsa_decrypt_pkcs1v15`.

**PLAINTEXTKEYBLOB parse** (G59 `[EMPIRICAL]`):

```
bType     (1 byte)  = 0x08  (PLAINTEXTKEYBLOB)
bVersion  (1 byte)  = 0x02
reserved  (2 bytes) = 0x00 0x00
aiKeyAlg  (4 bytes) = 0x0000660E (CALG_AES_128) or 0x00006610 (CALG_AES_256)
dwKeyLen  (4 bytes) = AES key length in bytes (16 = AES-128, 32 = AES-256)
key data  (dwKeyLen bytes) = raw AES DEK
```

Source: `_parse_plaintextkeyblob`.  The `bType == 0x08` check guards against
decryption with a mismatched key or wrong byte order.

`extract_dek(buf, tde_key) -> bytes` returns the raw AES key (16 or 32 bytes).

---

### 10.3 Data-stream start discovery `[EMPIRICAL]`

Source: `tde/dek.py: find_tde_data_start`, `_is_valid_file_header_page`

SQL Server TDE leaves the **first 96 bytes of every page** (the SQL Server page
header) in plaintext in the backup.  The file-header page (`m_type=15`,
`page_id=0`, `file_id=1`) is therefore identifiable without decryption.

Scan parameters:

| Constant | Value | Meaning |
|----------|-------|---------|
| `_DATA_SCAN_START` | `0x2000` | Scan start offset |
| `_DATA_SCAN_END` | `0x200000` (2 MB) | Scan end offset |
| `_DATA_SCAN_STRIDE` | `512` | MTF streams are 512-byte-aligned |

At each candidate offset the scanner checks (G60 `[EMPIRICAL]`):
- `page[0] == 1` (`m_headerVersion`)
- `page[1] == 15` (`m_type = FILE_HEADER`)
- `struct.unpack_from("<IH", page, 32)` returns `(page_id=0, file_id=1)` (page
  locator at offset 32)

`find_tde_data_start(buf, dek) -> int` returns the byte offset of the first page.
The `dek` parameter is accepted for API compatibility but not used (the scan is
plaintext-only).

---

### 10.4 Per-page decryption `[EMPIRICAL]`

Source: `tde/page.py: decrypt_page`, `_make_page_iv`

Each 8 192-byte page in a TDE backup is laid out as:

```
[  0 ..  95]  96-byte SQL Server page header — PLAINTEXT (verbatim copy)
[ 96 .. 8191]  8 096-byte data portion — AES-CBC CIPHERTEXT
```

The page header is returned unchanged; only bytes `[96:8192]` are decrypted.

**IV derivation** (G61 `[EMPIRICAL]`, confirmed by known-plaintext analysis on
SQL Server 2022 backups):

```python
IV = struct.pack('<IH', page_id, file_id) + b'\x00' * 10  # 16 bytes total
```

`page_id` and `file_id` are read from the plaintext header at offset 32
(`m_pageId u32 LE`, `m_fileId u16 LE`).

Algorithm: `AES-CBC` via
`cryptography.hazmat.primitives.ciphers.algorithms.AES` +
`cryptography.hazmat.primitives.ciphers.modes.CBC`.

**m_flagBits TDE indicator**: byte 4–5 of the page header (`m_flagBits`) has
bit `0x08` set in TDE backups to mark the encrypted state.  The rest of the
header is preserved verbatim from the on-disk representation.

`decrypt_page(page_bytes, dek, page_id, file_id) -> bytes` returns a 8 192-byte
fully decryptable page ready for the standard page-header parser (`pages.py:
PageHeader.parse`, §2).

---

### 10.5 Integration — call flow

Source: `mtf.py: extract_mdf_files`, `pages/store.py: PageStore.from_bak`,
`extract/driver.py`, `cli/bak.py`

```
PageStore.from_bak(path, tde_key=load_tde_key("cert.pfx", "pass"))
    └─ mtf.py: extract_mdf_files(buf, tde_key=...)
           ├─ detect non-encrypted MSSQLBAK container vs raw page stream
           ├─ if TDE detected (plaintext header, no MSSQLBAK magic):
           │      dek = extract_dek(buf, tde_key)             # tde/dek.py
           │      data_start = find_tde_data_start(buf, dek)  # tde/dek.py
           │      ── yield 8 KB pages, each decrypted on the fly via
           │         decrypt_page(page_bytes, dek, pid, fid)  # tde/page.py
           └─ on backup-level encryption → raise EncryptedBackupError
```

The resulting `PageStore` is indistinguishable from a non-TDE store: downstream
catalog recovery (`catalog/recover.py`), metadata extraction, and data extraction
all operate on the decrypted page bytes.

---

### 10.6 Guess Register entries — TDE

| ID | Guess | Evidence | Risk |
|----|-------|----------|------|
| G58 | DEK descriptor layout in MTF header: `uint32 thumbprint_len` immediately before thumbprint bytes; `uint32 ciphertext_len` immediately after | Empirically mapped against SQL Server 2022 backup; TDE fixture decrypts correctly | S (wrong DEK → AES failure) |
| G59 | Decrypted blob is a Windows PLAINTEXTKEYBLOB: `bType=0x08`, `bVersion=0x02`, `aiKeyAlg` at +4, `dwKeyLen` at +8, key at +12 | PLAINTEXTKEYBLOB structure is publicly documented (MS-MQQB §2.2.1); validated against SQL Server 2022 AES-128 and AES-256 DEKs | S |
| G60 | File-header page signature: `m_type=15`, `page_id=0`, `file_id=1`, `m_headerVersion=1` at bytes 0–1 and 32–37 (plaintext) | Invariant with non-TDE page header; confirmed present in TDE fixture | M (data-stream not found) |
| G61 | IV = `struct.pack('<IH', page_id, file_id) + b'\x00'*10` | Known-plaintext analysis on SQL Server 2022: decrypted page header matches non-TDE counterpart at all expected fields | S (garbled pages) |
