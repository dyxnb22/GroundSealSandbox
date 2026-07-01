# TASKS.md

## Now

- Implement `local_restricted` real subprocess execution behind explicit opt-in.
- Add failure record for schema_invalid boundary case (FR-002).
- Phase 6 spike: run_id and replay model draft.

## Next

- Reviewer-facing evidence summary view (Phase 7).
- Comparative dry_run vs local_restricted experiment (Phase 8).
- CI badge in README once main branch runs green.

## Later

- OS-level network policy enforcement.
- Multi-tenant identity at integration boundary.
- Case study and platform backfeed (Phase 9).

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.

## Completed

### Phase 0
- Glossary and minimal contract set (`docs/glossary.md`, `docs/contracts.md`).
- Evaluation fixture categories (`docs/evaluation-plan.md`).
- Parent-platform assumption separation (`docs/integration-contract.md`).
- Python project scaffold (`pyproject.toml`, `groundseal/` package layout).

### Phase 1
- Pydantic models (`groundseal/contracts/models.py`).
- Invariants (`docs/invariants.md`).
- Strategy matrix (`groundseal/policy/strategy_matrix.py`).
- Contract and strategy unit tests.

### Phase 2
- Public API: `describe_capabilities`, `plan_execution`, `preflight`, `run`.
- Dry-run execution path.
- E2E fixture `tests/fixtures/happy_path.json`.
- Known limitations doc.

### Phase 3
- `FailureClass` enum and negative-path tests.
- Failure record `docs/failure-records/FR-001-policy-denied.md`.

### Phase 4
- GitHub Actions CI (`.github/workflows/ci.yml`).
- All six fixture categories + `integration_boundary_metadata` variant.
- Evaluation runner (`scripts/evaluate.py`, `groundseal/evaluation/runner.py`).
- Baseline ratchet (`tests/baselines/evaluation_v0.json`).
- Report template (`reports/evaluation-report-template.md`).

### Phase 5
- Integration adapter (`groundseal/adapter/`).
- `execute_workflow` orchestrates full handshake; preflight cannot be skipped.
- Boundary tests (`tests/test_integration_adapter.py`).
- Integration example (`examples/integration_request_valid.json`).
