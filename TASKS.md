# TASKS.md

## Now

- OS-level network policy enforcement spike.
- Multi-tenant identity at integration boundary (Phase 5 open question).
- CI badge in README once main branch runs green.

## Next

- Record migration for RunStore schema changes.
- Expand denylist with configurable policy profiles.
- Integration adapter optional `persist_run` flag.

## Later

- Performance benchmarks and timeout tuning for subprocess.
- Richer reviewer HTML views.
- Platform backfeed PR into parent monorepo.

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.

## Completed

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
