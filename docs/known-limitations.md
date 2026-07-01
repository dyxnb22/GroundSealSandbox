# Known Limitations (v0.2)

Documented constraints after v0.2 follow-up slices.

## Execution

- **`local_restricted` is opt-in.** Set `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED=1` or
  `set_local_restricted_enabled(True)` in tests.
- **Subprocess uses `shell=True`** with `cwd` set to `workspace_root` only.
- **`dry_run` remains the default** when real execution is not enabled.
- **OS backends beyond `process_only`** are detected but not default execution paths.

## Policy

- Denylist is configurable via `PolicyProfile` and `config/policies/*.yaml`.
- Built-in mandatory patterns cannot be removed by operators.
- `context.metadata` is ignored for policy decisions.

## Network and filesystem

- No production OS-level network isolation in `local_restricted` (spike only).
- Filesystem constraints are logical; Landlock is not wired into execution.

## Lifecycle

- `RunStore` JSON persistence is single-file with per-record `schema_version`.
- Legacy v0 records migrate on load; use `scripts/migrate_runstore.py` offline.
- Replay may detect drift if opt-in config changes between runs.
- Tenant isolation requires explicit `tenant_id` on store operations.

## Evaluation

- Six fixture categories plus integration-boundary variant in manifest.
- Strategy comparison experiment is offline only (`scripts/compare_strategies.py`).
- Network isolation spike is manual (`scripts/spike_network_isolate.sh`).
