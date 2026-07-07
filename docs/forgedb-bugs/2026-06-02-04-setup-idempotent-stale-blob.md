# forgedb bug: `setup` short-circuits on existing instance, returns stale blob, skips persistence

**Status:** Open / needs documentation

## Trigger
Calling `setup_sqlserver_podman` repeatedly while a same-named instance exists.

## Observed
Every re-run returned the same `ready_at` timestamp
(`2026-06-02T21:49:43.108631+00:00`) from the very first provision, even after a
forgedb fix that should have changed persistence behavior. So re-running `setup`
did not re-run the create/persist code path — it returned a cached result.

## Expected
Either: (a) `setup` documents that it is idempotent and returns the existing
instance without rebuilding, and points to `recreate` to force a rebuild; or
(b) `setup` re-runs configuration/persistence so fixes take effect.

## Impact
When the persisted blob was missing (bug 03), re-running `setup` could not repair
it, and `reconfigure` couldn't either (it reads the missing blob). The only way to
exercise fixed code was teardown + setup or `recreate`.

## Suggested fix
Document idempotency explicitly in the `setup_*` description; cross-reference
`recreate`; consider having `setup` re-run the persistence step when the secret is
absent for an existing instance.
