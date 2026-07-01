# Lifecycle Model (v0.2)

## Purpose

Define how GroundSealSandbox records and replays executions without hidden state.

## Run identity

Each recorded execution receives a UUID `run_id` at record time. The ID is
stored in `RunRecord` and copied into `ExecutionEvidence.run_id` when real
execution is enabled.

## RunRecord

| Field | Description |
|-------|-------------|
| `schema_version` | Record schema version (default `"1"`) |
| `run_id` | Unique identifier |
| `created_at` | ISO-8601 UTC timestamp |
| `tenant_id` | Tenant scope for store isolation (required for persistence) |
| `proposal` | Snapshot at execution time |
| `preflight` | Preflight report that gated execution |
| `result` | Final execution outcome |

## Storage

`RunStore` supports:
- In-memory storage (default for tests)
- Optional JSON file persistence (`RunStore(path=...)`)
- Tenant-scoped keys `(tenant_id, run_id)` — all store operations require `tenant_id`

Records are written atomically per `save()` call. Legacy files without
`schema_version` are migrated on load via `groundseal.lifecycle.migrations`.

Use `scripts/migrate_runstore.py` for offline file migration.

## Replay semantics

`replay_run(run_id, store, tenant_id=...)`:
1. Loads the stored `RunRecord` for the given tenant
2. Re-plans from the original command and context
3. Re-runs preflight and execution
4. Returns `ReplayComparison` with drift detection

**Drift** is reported when `status` or `exit_code` differs between original
and replay, or when tenant scope does not match.

## Invariants

- Replay does not mutate the original record
- Replay uses current subsystem config (e.g. `local_restricted` opt-in); config
  drift may surface as `drift_detected=True` with notes
- Missing `run_id` for tenant returns `drift_detected=True` with explanatory notes
- Cross-tenant access returns `None` from `get` (fail closed)

## API

```python
from groundseal.lifecycle import RunStore, run_and_record, replay_run

store = RunStore()
record = run_and_record(proposal, preflight_report, store, tenant_id="tenant-a")
comparison = replay_run(record.run_id, store, tenant_id="tenant-a")
```

## Deferred

- Distributed or database-backed storage
- Partial replay (preflight-only)
