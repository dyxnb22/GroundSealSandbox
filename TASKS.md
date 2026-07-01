# TASKS.md

## Now

- Landlock wiring into `local_restricted` (after network spike evaluation).
- CI badge in README once main branch runs green.
- Platform backfeed PR into parent monorepo.

## Next

- Performance benchmarks and timeout tuning for subprocess.
- Richer reviewer HTML views.
- argv-based subprocess (replace `shell=True`).

## Later

- Database-backed RunStore.
- Partial replay (preflight-only).

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.

## Completed

### v0.2 follow-up slices
- `PolicyProfile` + configurable denylist (`config/policies/`, `groundseal/policy/profile.py`)
- OS enforcement backend + trust tiers (`docs/os-enforcement-strategy.md`)
- `RunRecord.schema_version` + migrations + `scripts/migrate_runstore.py`
- Multi-tenant `tenant_id` on context, RunStore scoping, adapter `persist_run`
- Network isolation spike (`docs/experiments/network-isolation-spike.md`)

### Phase 0–5
See git history / prior TASKS sections.

### Phase 6 — Durable / multi-run
- `RunRecord`, `ReplayComparison` models
- `RunStore` with optional JSON persistence
- `run_and_record`, `replay_run` with drift detection
- `docs/lifecycle-model.md`

### Phase 7 — Reviewer experience
- `ReviewerSummary` + `format_reviewer_markdown`
- `docs/reviewer-guide.md`
- `tests/test_reviewer.py`

### Phase 8 — Comparative experiments
- `scripts/compare_strategies.py`
- `docs/experiments/dry-run-vs-local-restricted.md`
- `tests/test_strategy_comparison.py`

### Phase 9 — Case study
- `docs/case-study.md`

### local_restricted execution
- Opt-in via `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED` / `set_local_restricted_enabled`
- `groundseal/execution/local_restricted.py`
- `tests/test_local_restricted.py`
