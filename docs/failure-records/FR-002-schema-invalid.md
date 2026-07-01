# Failure Record: FR-002

## Summary

Integration adapter returns `schema_invalid` for malformed parent input missing
`workspace_root`.

## Triggering input

```json
{"command": "echo hello", "context": {}}
```

Fixture: `tests/fixtures/schema_invalid.json`

## Expected behavior

- `execute_workflow` returns `ok=false`
- `failure_class=schema_invalid`
- `error` describes validation failure
- No proposal or execution result

## Observed behavior

Matches expected (verified by
`tests/test_integration_adapter.py::test_adapter_schema_invalid_missing_workspace_root`).

## Root cause

N/A — intentional contract validation at integration boundary.

## Deterministic?

Yes.

## Regression guard

- `tests/test_integration_adapter.py::test_adapter_schema_invalid_missing_workspace_root`
- Evaluation manifest entry `schema_invalid.json`

## Classification

- Failure bucket: poor ergonomics (prevented at boundary)
- Evaluation category: `schema_invalid`
