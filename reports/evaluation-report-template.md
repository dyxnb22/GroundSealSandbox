# Evaluation Report

Generated: {{timestamp}}
Contract version: v0

## Summary

| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| contract_pass_rate | {{contract_pass_rate}} | {{baseline_contract_pass_rate}} | {{delta_contract}} |
| negative_path_correctness | {{negative_path_correctness}} | {{baseline_negative}} | {{delta_negative}} |
| explainability_coverage | {{explainability_coverage}} | — | — |
| fixtures passed | {{passed_fixtures}}/{{total_fixtures}} | — | — |

## What changed

{{what_changed}}

## Fixture results

| Fixture | Category | Expected OK | Actual OK | Passed | Notes |
|---------|----------|-------------|-----------|--------|-------|
{{fixture_rows}}

## Regressions

{{regressions_or_none}}

## Not yet covered

- OS-level network isolation
- Real subprocess execution (`local_restricted`)
- Multi-tenant identity enforcement
- Performance benchmarks

## Ratchet decision

{{ratchet_decision}}
