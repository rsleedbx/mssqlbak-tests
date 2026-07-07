# forgedb MCP fixes needed for large XTP fixture generation

**Date:** 2026-07-04
**Requested by:** mssqlbak XTP work (building a large, compressed, checkpoint-flushed
memory-optimized `.bak` fixture to reverse-engineer the XTP checkpoint DATA-file
format).

## Why this is needed

We want a Sonnet-medium agent to generate a **large** memory-optimized fixture
(tens of thousands of variable-length rows, `CHECKPOINT`, `BACKUP … WITH
COMPRESSION`) on **one** SQL Server version. Building big memory-optimized tables
+ checkpoint files is RAM-hungry, and SQL Server will be OOM-killed if the
container's memory cap is too low.

To make this reliable the agent must be able to:

1. **Free RAM** by stopping the SQL Server versions it is *not* using (keep only,
   say, 2022), instead of killing everything.
2. **Raise the RAM cap** on the one instance it keeps, up to the Lima VM ceiling
   (~24 GB), and retry with more RAM on OOM.
3. **Restore** the environment afterwards (restart the versions it stopped).

The current MCP tool surface cannot do (1) or (2) cleanly. The fixes below are
what's blocking.

## Re-check #2 — ALL FIXES LANDED (2026-07-04, latest)

Re-inspected after a second MCP update. **Every blocking fix is now present and
verified live.** The workflow is unblocked.

| Fix | Status | Evidence |
|---|---|---|
| 1 — `version`/`target` on `stop`/`start` | ✅ done | `stop_sqlserver_podman(profile, epoch_pin, version, target)` and `start_sqlserver_podman(profile, epoch_pin, version, target, ram_gb)`. `version` acts on only that instance; `target` overrides the Lima backend. |
| 2 — unambiguous `ram_gb` | ✅ done | `start_sqlserver_podman` docstring: "Pass ram_gb>0 to update **this version's** container memory cap before starting." Now scoped by `version`. |
| 3 — RAM headroom read | ✅ done | New `host_resources` tool. Live: `vm.total_gb`, `vm.available_gb`, `vm.used_gb`, and per-container `memory_cap_gb`. |
| 4 — OOM signal | ❓ still unverified | not observable from descriptors; not force-tested (would require an intentional OOM). Non-blocking. |
| 5 — "keep only" helper | ✅ done | `stop_all_engines(profile, keep=…)` accepts a space/comma list of `engine` or `engine:version`; engine-level granularity, with per-version stop via `stop_sqlserver_podman(version=…)`. |

**Live `host_resources` output (this check):**
- VM `forgedb-lima-rosetta2-podman`: **total 15.6 GB**, available 4.0 GB, used 11.6 GB.
- 4 SQL Server containers (2017/2019/2022/2025), each capped at **8.0 GB**.
- `host_resources` returns **4** containers (deduped) — the two-target
  duplication seen in `list_running_containers` does not appear here, confirming
  it was a listing artifact, not 8 real containers.

**Correction to an earlier assumption:** the Lima VM is **~15.6 GB total, not
24 GB.** The realistic ceiling for one kept instance is therefore roughly
`available (4) + that container's current cap (8) + whatever is freed by
stopping the other three` — plan `ram_gb` accordingly rather than assuming 24.

**Recommended sequence for the large XTP fixture (now fully supported):**

```
host_resources()                                   # read total/available/caps
stop_sqlserver_podman(version="2017")              # free RAM
stop_sqlserver_podman(version="2019")
stop_sqlserver_podman(version="2025")
host_resources()                                   # confirm freed headroom
start_sqlserver_podman(version="2022", ram_gb=14)  # keep 2022, raise its cap
# … generate fixture, CHECKPOINT, BACKUP … WITH COMPRESSION …
start_sqlserver_podman(version="2017")             # restore afterwards
start_sqlserver_podman(version="2019")
start_sqlserver_podman(version="2025")
```

Only Fix 4 (distinct OOM error signal) remains unverified; it is a
nice-to-have for the retry loop, not a blocker. Everything below this line is
the original request, kept for history.

---

## Re-check after MCP update (2026-07-04, later)

The MCP was updated and re-inspected. **The blocking capability is still not
present.** Summary against the fixes below:

| Fix | Status | Evidence |
|---|---|---|
| 1 — `version`/`target` on `stop`/`start` | ❌ not done | `stop_sqlserver_podman` args are still only `profile, epoch_pin`; `start_sqlserver_podman` still only `profile, epoch_pin, ram_gb`. |
| 2 — unambiguous `ram_gb` | ⚠️ partial | `start_sqlserver_podman` now documents `ram_gb` ("Pass ram_gb>0 to update the container memory cap before starting"), but with no `version`/`target` it still can't name which of 4 instances. |
| 3 — RAM headroom read | ❌ not done | `forgedb://platform` still reports no VM total/free RAM and no per-container caps. |
| 4 — OOM signal | ❓ unverified | not observable from the tool descriptors. |
| 5 — "keep only" helper | ❌ not done | no `ensure_only_running`; `stop_all_engines` still `profile`-only. |

**Accepted improvements (thank you):**
- `list_running_containers` now returns structured JSON with per-container
  `name/engine/ports/target/blob/status` — machine-readable, good.
- `start_sqlserver_podman` description now explains `ram_gb`.

**Still blocking — the one thing that matters:** there is no way to stop a
*single* SQL Server version. Observed live: four versions (2017/2019/2022/2025)
all share epoch `1779207800`, so `epoch_pin` cannot disambiguate them, and
`stop_sqlserver_podman` has no `version` arg. So freeing RAM by stopping the
three unused versions is impossible through the MCP today.

Please prioritise **Fix 1's stop half**: `stop_sqlserver_podman(version=...)`.
That alone unblocks the workflow (see "Minimum viable subset").

**Two-targets question is now more urgent.** `forgedb://platform` reports only
`podman_native: true` (`lima_qemu: false`, `lima_vz: false`), yet
`list_running_containers` returns each version under **both**
`lima-native-podman` and `lima-rosetta2-podman` — 8 entries for 4 containers.
That reads as a **display duplicate**, not 8 real containers. Please either
dedupe the listing or, if they really are two runtimes, make `target` a
required selector on `stop`/`start` so the right copy is addressed. If the
`ram_gb` update path picks the wrong (phantom) target, the cap change will
silently no-op.

## Current state (observed 2026-07-04)

`list_running_containers` shows **four** SQL Server versions running
concurrently, each listed under **two** Lima targets:

| name | version | port | target(s) |
|---|---|---|---|
| robert-lee-mssql-2017-…-1779207800 | 2017 | 30002 | lima-native-podman, lima-rosetta2-podman |
| robert-lee-mssql-2019-…-1779207800 | 2019 | 30003 | lima-native-podman, lima-rosetta2-podman |
| robert-lee-mssql-2022-…-1779207800 | 2022 | 30000 | lima-native-podman, lima-rosetta2-podman |
| robert-lee-mssql-2025-…-1779207800 | 2025 | 30001 | lima-native-podman, lima-rosetta2-podman |

All share the same epoch (`1779207800`); names differ only by the `-<year>-`
segment and the resolved `target`.

Relevant tool argument surfaces today:

| tool | args today | can target one version? | can set RAM? |
|---|---|---|---|
| `setup_sqlserver_podman` | profile, epoch_pin, size, cpu, **ram_gb**, storage_gb, **version**, env, sku_json, mode, mi_subnet_cidr, **target**, source | ✅ (version + target) | ✅ ram_gb |
| `start_sqlserver_podman` | profile, epoch_pin, **ram_gb** | ❌ no version, no target | ✅ ram_gb (but ambiguous which instance) |
| `stop_sqlserver_podman` | profile, epoch_pin | ❌ no version, no target | n/a |
| `stop_all_engines` | profile | ❌ all-or-nothing | n/a |
| `list_running_containers` | profile | (read only; returns name/version/target) | — |

The mismatch is the problem: `setup_*` can address a specific
`(version, target)`, but `start_*` / `stop_*` cannot. With four versions × two
targets running, `stop_sqlserver_podman` is ambiguous and `stop_all_engines` is
too blunt.

## Fixes requested

### Fix 1 — add `version` + `target` selectors to `stop_sqlserver_podman` and `start_sqlserver_podman` (highest priority)

Mirror the `setup_sqlserver_podman` signature so a single instance can be
addressed:

- `stop_sqlserver_podman(profile, epoch_pin, version, target)`
- `start_sqlserver_podman(profile, epoch_pin, version, target, ram_gb)`

Behaviour:
- When `version` (and/or `target`) is given, act on **only** the matching
  container(s).
- When omitted, keep today's behaviour (back-compat).
- Accept the same `version` keys as `setup`/`preview_db_name` (`lts`,
  `latest`, `2017`, `2019`, `2022`, `2025`, …).

**Acceptance:** with all four versions up,
`stop_sqlserver_podman(version="2017")` stops only the 2017 container(s) and
leaves 2019/2022/2025 running (verified via `list_running_containers`).

### Fix 2 — make `start_sqlserver_podman ram_gb` unambiguous per instance

`ram_gb` already exists on `start_sqlserver_podman`, but with no `version`/
`target` it's unclear which of the four instances the new cap applies to. Once
Fix 1 lands, `start_sqlserver_podman(version="2022", ram_gb=24)` must set the
2022 container's memory cap to 24 GB (and only that one) before starting it.

**Acceptance:** `start_sqlserver_podman(version="2022", ram_gb=24)` results in
the 2022 container running with a 24 GB cap; the other containers' caps are
unchanged.

### Fix 3 — expose RAM headroom (read-only resource or tool)

Add a way to read, without mutating anything:
- the Lima VM's **total** RAM and currently-free RAM, and
- each running container's **current** memory cap.

Could be a new `forgedb://host/resources` resource or a `host_resources` tool.

**Why:** the agent needs to know how high it can safely push `ram_gb` (the VM
tops out around 24 GB) instead of guessing and over-committing.

**Acceptance:** a single read returns VM total/free RAM and per-container caps in
a machine-readable shape.

### Fix 4 — distinct, machine-readable OOM/failure signal

When SQL Server is killed mid-generation because the cap was too low, the failing
MCP call (`setup_*` / `start_*` / any exec) should return a **distinct** error
that names OOM and suggests raising `ram_gb` — e.g.
`{"error": "oom", "hint": "container exited 137; retry with higher ram_gb", "current_cap_gb": 8}`.

**Why:** the agent's retry loop is "on failure, raise `ram_gb` and retry." That
only works if OOM is distinguishable from an ordinary SQL/schema error.

**Acceptance:** a forced OOM (tiny cap + big table) returns the OOM-tagged error,
not a generic failure string.

### Fix 5 — (nice-to-have) "keep only these engines" helper

An idempotent convenience so the agent doesn't loop N stop calls:
- `stop_all_engines(profile, keep=["sqlserver:2022"])`, **or**
- `ensure_only_running(engines=["sqlserver:2022"])`.

**Acceptance:** one call leaves only the requested engine/version running.

## Minimum viable subset

If only one thing ships, it must be **Fix 1** (per-`version`/`target` stop &
start). With Fix 1 the agent can already:

```
stop_sqlserver_podman(version="2017")
stop_sqlserver_podman(version="2019")
stop_sqlserver_podman(version="2025")
start_sqlserver_podman(version="2022", ram_gb=24)   # needs Fix 2 semantics
```

Fixes 3–5 make the retry-on-OOM loop and cleanup smoother but are not strictly
blocking.

## Note on the two Lima targets

`list_running_containers` reports each version under **both**
`lima-native-podman` and `lima-rosetta2-podman`. Please clarify whether these are
two distinct VMs (double the RAM pressure) or one instance surfaced twice. If two
VMs, Fix 1's `target` selector is required to stop the right copy; if a display
artifact, dedupe the listing.
