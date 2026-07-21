/*
 * hook_aes.c — LD_PRELOAD hook for SQL Server backup-encryption IV capture.
 *
 * SQL Server 2022+ resolves OpenSSL cipher functions via dlsym() at runtime
 * rather than through the ELF PLT.  This hook therefore interposes BOTH the
 * PLT-level symbols AND dlsym() itself, so that whichever resolution path is
 * used the fake functions are returned.
 *
 * Intercepted functions:
 *   EVP_EncryptInit_ex   — legacy OpenSSL 1.x / 3.x compat API
 *   EVP_DecryptInit_ex   — legacy OpenSSL 1.x / 3.x compat API
 *   EVP_CipherInit_ex    — unified init (used by some PAL layers)
 *   EVP_EncryptInit_ex2  — OpenSSL 3.x new-style init (OSSL_PARAM variant)
 *   EVP_CIPHER_CTX_get_updated_iv — imported by sqlservr (in its PLT);
 *                          called after every block to read the chaining IV.
 *
 * For every AES call (block size == 16), logs:
 *   CALL_IDX | FUNC | NID | KEY_LEN | KEY_HEX | IV_LEN | IV_HEX | BACKTRACE
 *
 * AES-CBC NIDs (OpenSSL 3.x):
 *   419 = aes-128-cbc   423 = aes-192-cbc   427 = aes-256-cbc
 * AES-CFB8 NIDs (used for TDE page encryption, logged but marked):
 *   657 = aes-128-cfb8  661 = aes-192-cfb8   689 = aes-256-cfb8
 *
 * Build inside the container:
 *   gcc -shared -fPIC -O2 -o hook_aes.so hook_aes.c \
 *       -ldl -lssl -lcrypto -rdynamic -I/usr/include/openssl
 *
 * Launch SQL Server with it:
 *   LD_PRELOAD=/probe/hook_aes.so /opt/mssql/bin/sqlservr ...
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <openssl/evp.h>

/* ---------- log file ---------------------------------------------------- */

static FILE *g_log = NULL;

static FILE *get_log(void) {
    if (__builtin_expect(g_log != NULL, 1))
        return g_log;
    const char *path = getenv("IVPROBE_LOG");
    if (!path) path = "/probe/ivprobe.log";
    g_log = fopen(path, "a");
    if (!g_log) g_log = stderr;
    return g_log;
}

/* ---------- helpers ------------------------------------------------------ */

static atomic_int g_call_idx = 0;

static void hex(char *dst, const unsigned char *src, int len) {
    static const char hx[] = "0123456789abcdef";
    for (int i = 0; i < len; i++) {
        dst[2*i]   = hx[src[i] >> 4];
        dst[2*i+1] = hx[src[i] & 0xf];
    }
    dst[2*len] = '\0';
}

#define MAX_FRAMES 20
static void log_entry(const char *func, int nid,
                       const unsigned char *key, int key_len,
                       const unsigned char *iv,  int iv_len)
{
    int idx = atomic_fetch_add(&g_call_idx, 1);
    FILE *f = get_log();

    char key_hex[2*64+1] = "(null)";
    if (key && key_len > 0 && key_len <= 64)
        hex(key_hex, key, key_len);

    char iv_hex[2*32+1] = "(null)";
    if (iv && iv_len > 0 && iv_len <= 32)
        hex(iv_hex, iv, iv_len);

    void *frames[MAX_FRAMES];
    int  nf = backtrace(frames, MAX_FRAMES);
    char **syms = backtrace_symbols(frames, nf);

    fprintf(f, "IDX=%d FUNC=%s NID=%d KEY_LEN=%d KEY=%s IV_LEN=%d IV=%s\n",
            idx, func, nid, key_len, key_hex, iv_len, iv_hex);
    if (syms) {
        for (int i = 0; i < nf; i++)
            fprintf(f, "  BT[%d] %s\n", i, syms[i]);
        free(syms);
    }
    fprintf(f, "---\n");
    fflush(f);
}

/* ---------- generic AES context inspector -------------------------------- */

static void log_if_aes(const char *func,
                        const EVP_CIPHER *type,
                        const unsigned char *key,
                        const unsigned char *iv)
{
    if (!type || !iv)
        return;
    int blk = EVP_CIPHER_get_block_size(type);
    if (blk != 16) /* AES family only */
        return;
    int nid     = EVP_CIPHER_get_nid(type);
    int key_len = EVP_CIPHER_get_key_length(type);
    int iv_len  = EVP_CIPHER_get_iv_length(type);
    log_entry(func, nid, key, key_len, iv, iv_len);
}

/* ---------- EVP_EncryptInit_ex interposer -------------------------------- */

typedef int (*EVP_EncryptInit_ex_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                      ENGINE *, const unsigned char *,
                                      const unsigned char *);
static EVP_EncryptInit_ex_fn real_EVP_EncryptInit_ex = NULL;

int EVP_EncryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                        ENGINE *impl,
                        const unsigned char *key, const unsigned char *iv)
{
    if (!real_EVP_EncryptInit_ex)
        real_EVP_EncryptInit_ex = (EVP_EncryptInit_ex_fn)
            dlsym(RTLD_NEXT, "EVP_EncryptInit_ex");
    int rc = real_EVP_EncryptInit_ex(ctx, type, impl, key, iv);
    log_if_aes("EncryptInit_ex", type, key, iv);
    return rc;
}

/* ---------- EVP_DecryptInit_ex interposer -------------------------------- */

typedef int (*EVP_DecryptInit_ex_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                      ENGINE *, const unsigned char *,
                                      const unsigned char *);
static EVP_DecryptInit_ex_fn real_EVP_DecryptInit_ex = NULL;

int EVP_DecryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                        ENGINE *impl,
                        const unsigned char *key, const unsigned char *iv)
{
    if (!real_EVP_DecryptInit_ex)
        real_EVP_DecryptInit_ex = (EVP_DecryptInit_ex_fn)
            dlsym(RTLD_NEXT, "EVP_DecryptInit_ex");
    int rc = real_EVP_DecryptInit_ex(ctx, type, impl, key, iv);
    log_if_aes("DecryptInit_ex", type, key, iv);
    return rc;
}

/* ---------- EVP_CipherInit_ex interposer -------------------------------- */

typedef int (*EVP_CipherInit_ex_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                     ENGINE *, const unsigned char *,
                                     const unsigned char *, int);
static EVP_CipherInit_ex_fn real_EVP_CipherInit_ex = NULL;

int EVP_CipherInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                       ENGINE *impl,
                       const unsigned char *key, const unsigned char *iv,
                       int enc)
{
    if (!real_EVP_CipherInit_ex)
        real_EVP_CipherInit_ex = (EVP_CipherInit_ex_fn)
            dlsym(RTLD_NEXT, "EVP_CipherInit_ex");
    int rc = real_EVP_CipherInit_ex(ctx, type, impl, key, iv, enc);
    const char *fn = (enc > 0) ? "CipherInit_ex(enc)" : "CipherInit_ex(dec)";
    log_if_aes(fn, type, key, iv);
    return rc;
}

/* ---------- EVP_EncryptInit_ex2 interposer (OpenSSL 3.x) --------------- */

typedef int (*EVP_EncryptInit_ex2_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                       const unsigned char *,
                                       const unsigned char *,
                                       const OSSL_PARAM[]);
static EVP_EncryptInit_ex2_fn real_EVP_EncryptInit_ex2 = NULL;

int EVP_EncryptInit_ex2(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                         const unsigned char *key, const unsigned char *iv,
                         const OSSL_PARAM params[])
{
    if (!real_EVP_EncryptInit_ex2)
        real_EVP_EncryptInit_ex2 = (EVP_EncryptInit_ex2_fn)
            dlsym(RTLD_NEXT, "EVP_EncryptInit_ex2");
    int rc = real_EVP_EncryptInit_ex2(ctx, type, key, iv, params);
    log_if_aes("EncryptInit_ex2", type, key, iv);
    return rc;
}

/* ---------- EVP_DecryptInit_ex2 interposer (OpenSSL 3.x) --------------- */

typedef int (*EVP_DecryptInit_ex2_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                       const unsigned char *,
                                       const unsigned char *,
                                       const OSSL_PARAM[]);
static EVP_DecryptInit_ex2_fn real_EVP_DecryptInit_ex2 = NULL;

int EVP_DecryptInit_ex2(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                         const unsigned char *key, const unsigned char *iv,
                         const OSSL_PARAM params[])
{
    if (!real_EVP_DecryptInit_ex2)
        real_EVP_DecryptInit_ex2 = (EVP_DecryptInit_ex2_fn)
            dlsym(RTLD_NEXT, "EVP_DecryptInit_ex2");
    int rc = real_EVP_DecryptInit_ex2(ctx, type, key, iv, params);
    log_if_aes("DecryptInit_ex2", type, key, iv);
    return rc;
}

/* ---------- EVP_CIPHER_CTX_get_updated_iv interposer -------------------- */
/* SQL Server 2022+ imports this symbol (visible in PLT).                    */
/* It is called after AES operations to retrieve the updated IV/counter.     */

typedef int (*EVP_CIPHER_CTX_get_updated_iv_fn)(EVP_CIPHER_CTX *, void *, size_t);
static EVP_CIPHER_CTX_get_updated_iv_fn real_get_updated_iv = NULL;

int EVP_CIPHER_CTX_get_updated_iv(EVP_CIPHER_CTX *ctx, void *buf, size_t len)
{
    if (!real_get_updated_iv)
        real_get_updated_iv = (EVP_CIPHER_CTX_get_updated_iv_fn)
            dlsym(RTLD_NEXT, "EVP_CIPHER_CTX_get_updated_iv");
    int rc = real_get_updated_iv(ctx, buf, len);
    if (rc == 1 && buf && len <= 32) {
        /* We got the updated IV — log it with key "(captured_after)" */
        int nid     = EVP_CIPHER_CTX_get_type(ctx);
        int blk     = EVP_CIPHER_CTX_get_block_size(ctx);
        if (blk == 16) {
            log_entry("get_updated_iv", nid,
                      (const unsigned char *)"(not_captured)", 14,
                      (const unsigned char *)buf, (int)len);
        }
    }
    return rc;
}

/* ---------- dlsym interposer -------------------------------------------- */
/* SQL Server resolves crypto functions via dlsym() at startup.  By          */
/* intercepting dlsym we redirect requests for EVP init functions to our     */
/* own wrappers, so we capture calls even when SQL Server bypasses the PLT.  */

typedef void *(*dlsym_fn)(void *, const char *);
static dlsym_fn real_dlsym = NULL;

void *dlsym(void *handle, const char *name)
{
    /* Bootstrap: get real dlsym via dlvsym with the GLIBC version. */
    if (!real_dlsym)
        real_dlsym = (dlsym_fn)dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.34");
    if (!real_dlsym)  /* fallback for older glibc */
        real_dlsym = (dlsym_fn)dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.2.5");

    /* Redirect crypto init functions to our wrappers. */
    if (name) {
        if (strcmp(name, "EVP_EncryptInit_ex") == 0)
            return (void *)EVP_EncryptInit_ex;
        if (strcmp(name, "EVP_DecryptInit_ex") == 0)
            return (void *)EVP_DecryptInit_ex;
        if (strcmp(name, "EVP_CipherInit_ex") == 0)
            return (void *)EVP_CipherInit_ex;
        if (strcmp(name, "EVP_EncryptInit_ex2") == 0)
            return (void *)EVP_EncryptInit_ex2;
        if (strcmp(name, "EVP_DecryptInit_ex2") == 0)
            return (void *)EVP_DecryptInit_ex2;
        if (strcmp(name, "EVP_CIPHER_CTX_get_updated_iv") == 0)
            return (void *)EVP_CIPHER_CTX_get_updated_iv;
    }

    return real_dlsym(handle, name);
}
