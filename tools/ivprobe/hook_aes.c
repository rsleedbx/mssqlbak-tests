/*
 * hook_aes.c — LD_PRELOAD hook for SQL Server backup-encryption IV capture.
 *
 * Interposes EVP_EncryptInit_ex and EVP_DecryptInit_ex from libcrypto.so.3.
 * sqlservr imports exactly these two symbols (no _ex2 variants, confirmed via nm -D).
 *
 * For every call where the cipher has a 16-byte block size (AES family) and an
 * IV is supplied, logs:
 *   CALL_IDX | FUNC | NID | KEY_LEN | KEY_HEX | IV_HEX | BACKTRACE
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

    /* key hex */
    char key_hex[2*64+1] = "(null)";
    if (key && key_len > 0 && key_len <= 64)
        hex(key_hex, key, key_len);

    /* IV hex */
    char iv_hex[2*32+1] = "(null)";
    if (iv && iv_len > 0 && iv_len <= 32)
        hex(iv_hex, iv, iv_len);

    /* backtrace */
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

/* ---------- EVP_EncryptInit_ex interposer -------------------------------- */

typedef int (*EVP_EncryptInit_ex_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                      ENGINE *, const unsigned char *,
                                      const unsigned char *);

int EVP_EncryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                        ENGINE *impl,
                        const unsigned char *key, const unsigned char *iv)
{
    static EVP_EncryptInit_ex_fn real = NULL;
    if (!real)
        real = (EVP_EncryptInit_ex_fn)dlsym(RTLD_NEXT, "EVP_EncryptInit_ex");

    int rc = real(ctx, type, impl, key, iv);

    if (type && iv) {
        int blk = EVP_CIPHER_get_block_size(type);
        if (blk == 16) {                         /* AES family */
            int nid     = EVP_CIPHER_get_nid(type);
            int key_len = EVP_CIPHER_get_key_length(type);
            int iv_len  = EVP_CIPHER_get_iv_length(type);
            log_entry("EncryptInit_ex", nid, key, key_len, iv, iv_len);
        }
    }
    return rc;
}

/* ---------- EVP_DecryptInit_ex interposer -------------------------------- */

typedef int (*EVP_DecryptInit_ex_fn)(EVP_CIPHER_CTX *, const EVP_CIPHER *,
                                      ENGINE *, const unsigned char *,
                                      const unsigned char *);

int EVP_DecryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                        ENGINE *impl,
                        const unsigned char *key, const unsigned char *iv)
{
    static EVP_DecryptInit_ex_fn real = NULL;
    if (!real)
        real = (EVP_DecryptInit_ex_fn)dlsym(RTLD_NEXT, "EVP_DecryptInit_ex");

    int rc = real(ctx, type, impl, key, iv);

    if (type && iv) {
        int blk = EVP_CIPHER_get_block_size(type);
        if (blk == 16) {
            int nid     = EVP_CIPHER_get_nid(type);
            int key_len = EVP_CIPHER_get_key_length(type);
            int iv_len  = EVP_CIPHER_get_iv_length(type);
            log_entry("DecryptInit_ex", nid, key, key_len, iv, iv_len);
        }
    }
    return rc;
}
