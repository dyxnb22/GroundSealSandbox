# Lifecycle Model (v0)

## Purpose

Define how GroundSealSandbox records and replays executions without hidden state.

## Run identity

Each recorded execution receives a UUID `run_id` at record time. The ID is
stored in `RunRecord` and copied into `ExecutionEvidence.run_id` when real
execution is enabled.

## RunRecord

| Field | Description |
|-------|-------------|
| `run_id` | Unique identifier |
| `created_at` | ISO-8601 UTC timestamp |
| `proposal` | Snapshot at execution time |
| `preflight` | Preflight report that gated execution |
| `result` | Final execution outcome |

## Storage

`RunStore` supports:
- In-memory storage (default for tests)
- Optional JSON file persistence (`RunStore(path=...)`)

Records are written atomically per `save()` call. No migration layer in v0.

## Replay semantics

`replay_run(run_id, store)`:
1. Loads the stored `RunRecord`
2. Re-plans from the original command and context
3. Re-runs preflight and execution
4. Returns `ReplayComparison` with drift detection

**Drift** is reported when `status` or `exit_code` differs between original
and replay.

## Invariants

- Replay does not mutate the original record
- Replay uses current subsystem config (e.g. `local_restricted` opt-in); config
  drift may surface as `drift_detected=True` with notes
- Missing `run_id` returns `drift_detected=True` with explanatory notes

## API

```python
from groundseal.lifecycle import RunStore, run_and_record, replay_run

store = RunStore()
record = run_and_record(proposal, preflight_report, store)
comparison = replay_run(record.run_id, store)
```

## Deferred

- Cross-version record migration
- Distributed or database-backed storage
- Partial replay (preflight-only)
