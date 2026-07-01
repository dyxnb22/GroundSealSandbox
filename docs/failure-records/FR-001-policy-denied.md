# Failure Record: FR-001

## Summary

Policy denylist correctly blocks `rm -rf /` before execution.

## Triggering input

```json
{"command": "rm -rf /", "context": {"workspace_root": "/tmp/workspace"}}
```

Fixture: `tests/fixtures/policy_denied.json`

## Expected behavior

- `preflight` returns `overall_status=fail`
- `blocking_reasons` mentions denylist
- `run` returns `status=denied`, `failure_class=preflight_failed`
- No shell invocation occurs

## Observed behavior

Matches expected (verified by `tests/test_negative_paths.py::test_policy_denied_blocks_execution`).

## Root cause

N/A — intentional policy enforcement.

## Deterministic?

Yes.

## Regression guard

`tests/test_negative_paths.py::test_policy_denied_blocks_execution`

## Classification

- Failure bucket: filesystem escape (prevented)
- Evaluation category: `policy_denied`
