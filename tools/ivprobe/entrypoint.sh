#!/bin/bash
# entrypoint.sh — wrapper for the SQL Server probe container.
#
# 1. Installs gcc + libssl-dev (if absent).
# 2. Compiles hook_aes.c from /probe_src to /tmp/hook_aes.so.
# 3. Sets LD_PRELOAD and execs the real sqlservr binary so that
#    the hook is active from process start, capturing all AES init calls.
#
# The SQL Server image must be started with:
#   -v <repo>/mssqlbak-tests/tools/ivprobe:/probe_src:ro
#   -e IVPROBE_LOG=/tmp/ivprobe.log
#   --entrypoint /probe_src/entrypoint.sh

set -e

SRC=/probe_src/hook_aes.c
SO=/tmp/hook_aes.so

echo "[entrypoint] Installing build tools..."
apt-get update -qq 2>&1 | tail -1
apt-get install -y -qq gcc libssl-dev 2>&1 | tail -1

echo "[entrypoint] Compiling hook_aes.so..."
gcc -shared -fPIC -O2 -rdynamic \
    -o "$SO" "$SRC" \
    -ldl -lssl -lcrypto -I/usr/include/openssl
echo "[entrypoint] Built: $(ls -lh $SO)"

export LD_PRELOAD="$SO"
export IVPROBE_LOG="${IVPROBE_LOG:-/tmp/ivprobe.log}"
echo "[entrypoint] LD_PRELOAD=$LD_PRELOAD  IVPROBE_LOG=$IVPROBE_LOG"
echo "[entrypoint] Exec'ing sqlservr..."
exec /opt/mssql/bin/sqlservr "$@"
