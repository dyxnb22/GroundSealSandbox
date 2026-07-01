# TASKS.md

## Now

- Add CI workflow for pytest on push.
- Expand fixture coverage for `schema_invalid` category with dedicated JSON fixture.
- Phase 5: thin integration adapter and boundary tests.

## Next

- Implement `local_restricted` real execution behind explicit opt-in.
- Evaluation report template under `reports/`.
- Network policy enforcement at OS level (future).

## Later

- Comparative experiments (Phase 8) and case study (Phase 9).
- Persistence and replay (Phase 6).
- Reviewer-facing output views (Phase 7).

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
