# Evaluation Plan

## Purpose

Define how this project will be judged as it evolves.

## Evaluation Goals

- Verify contract correctness.
- Catch regressions early.
- Expose failure patterns instead of hiding them in aggregate scores.
- Produce evidence useful to reviewers and future maintainers.

## Evaluation Layers

1. Schema and contract validation.
2. Deterministic unit tests for core logic.
3. Fixture-based scenario tests.
4. Negative and adversarial tests.
5. Integration-boundary tests.

## Metrics To Track

- Contract pass rate.
- Negative-path correctness.
- Regression count.
- Explainability coverage.
- Unresolved known-risk count.

## Reporting Expectations

Every evaluation run should leave behind:
- what changed
- what was measured
- what regressed or improved
- what is still not covered

## Ratchet Policy

Baselines should move only when the team can explain why the new result is better or when a prior baseline was shown to be wrong.

## Fixture Categories (v0)

Each category maps to a deterministic fixture under `tests/fixtures/` and aligns
with failure buckets in [failure-analysis-plan.md](failure-analysis-plan.md).

| Category | Example scenario | Expected behavior | Failure bucket |
|----------|------------------|-------------------|----------------|
| `schema_valid` | Well-formed proposal JSON | Passes contract validation | — |
| `schema_invalid` | Missing required field or wrong type | Fail-closed with `schema_invalid` | poor ergonomics |
| `policy_denied` | Command matches denylist pattern | Preflight fail; `run` not called | filesystem escape (prevented) |
| `strategy_mismatch` | Request `local_restricted` when unavailable | Fail with `strategy_mismatch` + rationale | poor ergonomics |
| `ambiguous_high_risk` | Empty command or `../` traversal in path | Fail-closed with `ambiguous_high_risk` | filesystem escape (prevented) |
| `dry_run_happy` | Normal `echo hello` in workspace | `status=simulated`, evidence includes rationale | — |

### Category coverage targets

| Phase | Required categories |
|-------|---------------------|
| Phase 2 | `schema_valid`, `dry_run_happy` |
| Phase 3 | all six categories |
| Phase 4 | all six + integration-boundary variants |

### Running evaluation

```bash
python scripts/evaluate.py --check-baseline
```

Writes `reports/generated/evaluation-latest.json`. Baseline ratchet:
`tests/baselines/evaluation_v0.json`. CI runs evaluation on every push.

### Explainability coverage

A fixture passes explainability checks when its failure or denial path includes
a non-empty `reason` on the failing `PreflightCheck` or a `failure_class` on
the `ExecutionResult`.
