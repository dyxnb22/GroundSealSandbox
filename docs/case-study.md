# Case Study: GroundSealSandbox v0

## Problem

Agent-driven development workflows need a command-execution boundary that is
contract-first, testable, and fail-closed — without becoming a general
container platform.

## Approach

GroundSealSandbox was built as a standalone subsystem with:

1. **Explicit contracts** — five types, four API functions, integration adapter
2. **Phased delivery** — docs → schemas → dry-run → failures → evaluation → integration → lifecycle → review
3. **Deterministic evaluation** — manifest fixtures with baseline ratchet
4. **Opt-in real execution** — `local_restricted` behind explicit enablement

## What was built (v0)

| Phase | Deliverable |
|-------|-------------|
| 0–1 | Glossary, contracts, Pydantic models, invariants |
| 2–3 | dry-run API, negative paths, failure records |
| 4–5 | CI, evaluation runner, integration adapter |
| 6 | RunRecord, RunStore, replay with drift detection |
| 7 | ReviewerSummary and markdown formatter |
| 8 | dry_run vs local_restricted experiment |
| 9 | This case study |

## Lessons for parent platform integration

1. **Thin adapter** — Parent calls `execute_workflow`; subsystem owns preflight
2. **No silent policy relaxation** — Metadata cannot override network/fs policy
3. **Evidence by default** — `strategy_rationale`, `failure_class`, blocking reasons
4. **Ratcheted quality** — Evaluation baseline prevents undocumented regressions
5. **Strategy default** — Prefer `dry_run`; enable real execution only when needed

## Residual risks

- Subprocess execution uses `shell=True` with cwd constraint only
- No multi-tenant identity enforcement at boundary (Phase 5 open question)
- Replay sensitive to runtime config changes

## Recommendations for backfeed

- Adopt `IntegrationRequest` / `IntegrationResponse` shape for workflow handshakes
- Require `ReviewerSummary` fields in operator dashboards
- Treat `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED` as a deployment-level gate
- Promote failure records (FR-001, FR-002) into platform regression suites

## Credibility evidence

- 30+ deterministic pytest cases
- 6 evaluation fixtures with baseline ratchet
- Documented experiments with controlled comparison script
- Failure taxonomy with machine-readable `FailureClass`
