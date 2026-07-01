# Known Limitations (v0.1)

Documented constraints after Phases 6–8.

## Execution

- **`local_restricted` is opt-in.** Set `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED=1` or
  `set_local_restricted_enabled(True)` in tests.
- **Subprocess uses `shell=True`** with `cwd` set to `workspace_root` only.
- **`dry_run` remains the default** when real execution is not enabled.

## Policy

- Denylist is a minimal static pattern set in `groundseal/policy/normalize.py`.
- `context.metadata` is ignored for policy decisions.

## Network and filesystem

- No OS-level network isolation or mount namespaces.
- Filesystem constraints are logical; kernel-level enforcement is future work.

## Lifecycle

- `RunStore` JSON persistence is single-file, no migration.
- Replay may detect drift if opt-in config changes between runs.

## Evaluation

- Six fixture categories plus integration-boundary variant in manifest.
- Strategy comparison experiment is offline only (`scripts/compare_strategies.py`).
