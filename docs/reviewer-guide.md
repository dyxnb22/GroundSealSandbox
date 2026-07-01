# Reviewer Guide

## Purpose

Help operators and security reviewers inspect GroundSealSandbox outcomes without
reading internal module structure.

## Quick start

```python
from groundseal.adapter import execute_workflow
from groundseal.review import build_reviewer_summary, format_reviewer_markdown

response = execute_workflow({
    "command": "echo hello",
    "context": {"workspace_root": "/tmp/workspace"},
})
summary = build_reviewer_summary(response)
print(format_reviewer_markdown(summary))
```

## ReviewerSummary fields

| Field | Meaning |
|-------|---------|
| `headline` | One-line outcome |
| `decision` | `allow` or `deny` |
| `strategy` | Selected sandbox strategy |
| `strategy_rationale` | Why this strategy was chosen |
| `preflight_status` | `pass`, `fail`, or `warn` |
| `execution_status` | `simulated`, `completed`, `denied`, `failed` |
| `failure_class` | Machine-readable denial reason when applicable |
| `blocking_reasons` | Human-readable preflight blockers |
| `stdout_preview` / `stderr_preview` | Truncated process output (local_restricted) |
| `run_id` | Present when lifecycle recording is used |

## What to check

1. **Decision vs expectation** — Does `decision` match policy intent?
2. **Strategy rationale** — Was downgrade to `dry_run` explicit?
3. **Preflight** — Are `blocking_reasons` specific, not generic?
4. **Failure class** — Is denial machine-readable for automation?
5. **Output previews** — For real execution, does stdout/stderr match expectations?

## Denied path example

Policy-denied commands should show:
- `decision=deny`
- `preflight_status=fail`
- `failure_class=preflight_failed`
- Non-empty `blocking_reasons`

See failure record FR-001.

## Artifacts

- Markdown via `format_reviewer_markdown`
- Structured `ReviewerSummary` for parent UI rendering
- Evaluation fixtures under `tests/fixtures/` for regression examples
