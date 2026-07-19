#!/usr/bin/env bash
# run_probe.sh — IV capture via custom entrypoint (no writable bind mount needed).
#
# Strategy:
#   1. Start a fresh container with the ivprobe/ dir mounted read-only as
#      /probe_src, using entrypoint.sh which compiles hook_aes.so inside the
#      container then exec's sqlservr with LD_PRELOAD set.
#   2. Setup ProbeDB + ProbeCert; generate encrypted backups to /tmp inside
#      the container.
#   3. podman cp to pull backups, PVK, and the hook log to HOST_OUT.
#   4. Run analyze_ivs.py on HOST_OUT.
#
# Usage:
#   bash run_probe.sh [--image <image>] [--sa-pass <pass>] [--keep]
#   SA_PASS=xxx bash run_probe.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_OUT="/var/tmp/probe_baks"
PROBE_CONT="mssql-ivprobe"
SA_PASS="${SA_PASS:-}"
MSSQL_IMAGE=""
KEEP_CONT=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --image)    MSSQL_IMAGE="$2"; shift 2 ;;
        --sa-pass)  SA_PASS="$2";     shift 2 ;;
        --keep)     KEEP_CONT=1;      shift ;;
        *)          echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# Auto-detect image
if [[ -z "$MSSQL_IMAGE" ]]; then
    MSSQL_IMAGE=$(podman inspect robert-lee-mssql-2022-mcr-local-1779207800 \
        --format '{{.ImageName}}' 2>/dev/null || true)
fi
[[ -n "$MSSQL_IMAGE" ]] || { echo "ERROR: pass --image"; exit 1; }

# Auto-detect SA password
if [[ -z "$SA_PASS" ]]; then
    SA_PASS=$(podman inspect robert-lee-mssql-2022-mcr-local-1779207800 \
        --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null \
        | grep -m1 MSSQL_SA_PASSWORD | cut -d= -f2- || true)
fi
[[ -n "$SA_PASS" ]] || { echo "ERROR: set SA_PASS env or pass --sa-pass"; exit 1; }

echo "Image : $MSSQL_IMAGE"
echo "SA pw : ${SA_PASS:0:4}****"
echo "Host out: $HOST_OUT"
mkdir -p "$HOST_OUT"

# =========================================================================
# Step 1 — start probe container with custom entrypoint
# =========================================================================
echo ""
echo "=== Step 1: launching probe container ==="
podman rm -f "$PROBE_CONT" 2>/dev/null || true

# The entrypoint.sh:
#   - installs gcc
#   - compiles hook_aes.so from /probe_src
#   - exec's sqlservr with LD_PRELOAD=/tmp/hook_aes.so
podman run -d \
    --name "$PROBE_CONT" \
    -e ACCEPT_EULA=Y \
    -e MSSQL_SA_PASSWORD="$SA_PASS" \
    -e IVPROBE_LOG=/tmp/ivprobe.log \
    -v "$SCRIPT_DIR":/probe_src:ro \
    --entrypoint /probe_src/entrypoint.sh \
    "$MSSQL_IMAGE"

echo "Waiting 60 s for entrypoint (apt + gcc) + SQL Server startup..."
sleep 60

# Verify SQL Server is up
ALIVE=0
for attempt in 1 2 3 4 5; do
    if podman exec "$PROBE_CONT" /opt/mssql-tools18/bin/sqlcmd \
            -S localhost -U sa -P "$SA_PASS" -C \
            -Q "SELECT 1" -l 10 >/dev/null 2>&1; then
        ALIVE=1; break
    fi
    echo "  [wait] attempt $attempt — SQL Server not ready yet, sleeping 15 s..."
    sleep 15
done

if [[ "$ALIVE" -eq 0 ]]; then
    echo "ERROR: SQL Server did not start. Container logs:" >&2
    podman logs "$PROBE_CONT" | tail -40
    exit 1
fi
echo "SQL Server is up."

# Verify LD_PRELOAD is set
LD_CHECK=$(podman exec "$PROBE_CONT" printenv LD_PRELOAD 2>/dev/null || echo "NOT SET")
echo "LD_PRELOAD in container: $LD_CHECK"

# Enable xp_cmdshell for cleanup
podman exec "$PROBE_CONT" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$SA_PASS" -C \
    -Q "EXEC sp_configure 'show advanced options',1; RECONFIGURE;
        EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;" 2>/dev/null || true

# =========================================================================
# Step 2 — setup ProbeDB + ProbeCert (writes PVK to /tmp inside container)
# =========================================================================
echo ""
echo "=== Step 2: ProbeDB + ProbeCert ==="
# Patch setup SQL to write to /tmp
sed 's|/probe/|/tmp/|g' "$SCRIPT_DIR/setup_probe_db.sql" > /tmp/_setup_probe_db.sql
podman cp /tmp/_setup_probe_db.sql "$PROBE_CONT:/tmp/setup_probe_db.sql"
podman exec "$PROBE_CONT" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$SA_PASS" -C \
    -i /tmp/setup_probe_db.sql

# =========================================================================
# Step 3 — generate encrypted + plain backups
# =========================================================================
echo ""
echo "=== Step 3: generating probe backups ==="
sed 's|/probe/|/tmp/|g' "$SCRIPT_DIR/gen_probe_baks.sql" > /tmp/_gen_probe_baks.sql
podman cp /tmp/_gen_probe_baks.sql "$PROBE_CONT:/tmp/gen_probe_baks.sql"
podman exec "$PROBE_CONT" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$SA_PASS" -C \
    -i /tmp/gen_probe_baks.sql

# =========================================================================
# Step 4 — copy outputs to host
# =========================================================================
echo ""
echo "=== Step 4: copying outputs ==="
for f in ivprobe.log probe_cert.cer probe_cert.pvk \
          probe_plain.bak probe_aes128.bak probe_aes256.bak \
          probe_3des.bak probe_aes128_comp.bak; do
    if podman exec "$PROBE_CONT" test -f "/tmp/$f" 2>/dev/null; then
        podman cp "$PROBE_CONT:/tmp/$f" "$HOST_OUT/$f"
        echo "  copied: $f ($(du -sh "$HOST_OUT/$f" | cut -f1))"
    else
        echo "  MISSING: /tmp/$f"
    fi
done

LOG_LINES=$(wc -l < "$HOST_OUT/ivprobe.log" 2>/dev/null || echo 0)
echo ""
echo "Hook log: $LOG_LINES lines"
if [[ "$LOG_LINES" -eq 0 ]]; then
    echo "WARNING: hook log is empty — LD_PRELOAD may not have taken effect."
    echo "Container env:"
    podman exec "$PROBE_CONT" printenv | grep -E "LD_|IVPROBE"
    echo "Container logs (last 30 lines):"
    podman logs "$PROBE_CONT" 2>&1 | tail -30
fi

# =========================================================================
# Step 5 — analyze
# =========================================================================
if [[ -s "$HOST_OUT/ivprobe.log" && -f "$HOST_OUT/probe_cert.pvk" ]]; then
    echo ""
    echo "=== Step 5: analyzing IVs ==="
    python3 "$SCRIPT_DIR/analyze_ivs.py" \
        --probe-dir "$HOST_OUT" \
        --pvk       "$HOST_OUT/probe_cert.pvk" \
        --pvk-pass  "PvkPass_1!" \
        --log        "$HOST_OUT/ivprobe.log"
else
    echo "Skipping analysis (missing log or PVK)."
fi

# =========================================================================
# Cleanup
# =========================================================================
if [[ "$KEEP_CONT" -eq 0 ]]; then
    echo ""
    echo "=== Removing probe container ==="
    podman rm -f "$PROBE_CONT"
fi

echo ""
echo "Done. Outputs in $HOST_OUT/"
