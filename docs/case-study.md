# Case Study: GroundSealSandbox v0.2

## Problem

Agent-driven development workflows need a command-execution boundary that is
contract-first, testable, and fail-closed — without becoming a general
container platform.

## Approach

GroundSealSandbox was built as a standalone subsystem with:

1. **Explicit contracts** — typed models, four API functions, integration adapter
2. **Phased delivery** — docs → schemas → dry-run → failures → evaluation → integration → lifecycle → review
3. **Deterministic evaluation** — manifest fixtures with baseline ratchet
4. **Opt-in real execution** — `local_restricted` behind explicit enablement

## What was built

### v0.1 (Phases 0–9)

| Phase | Deliverable |
|-------|-------------|
| 0–1 | Glossary, contracts, Pydantic models, invariants |
| 2–3 | dry-run API, negative paths, failure records |
| 4–5 | CI, evaluation runner, integration adapter |
| 6 | RunRecord, RunStore, replay with drift detection |
| 7 | ReviewerSummary and markdown formatter |
| 8 | dry_run vs local_restricted experiment |
| 9 | Case study and integration backfeed notes |

### v0.2 (follow-up slices)

| Slice | Deliverable |
|-------|-------------|
| Policy | `PolicyProfile`, YAML denylist (`config/policies/`) |
| OS strategy | `EnforcementBackend`, trust tiers, capability detection |
| Lifecycle | `RunRecord.schema_version`, migrations, `migrate_runstore.py` |
| Identity | `tenant_id`, tenant-scoped `RunStore`, adapter `persist_run` |
| Spike | Network isolation experiment (manual, not production default) |

## Lessons for parent platform integration

1. **Thin adapter** — Parent calls `execute_workflow`; subsystem owns preflight
2. **No silent policy relaxation** — Metadata cannot override network/fs policy
3. **Evidence by default** — `strategy_rationale`, `failure_class`, blocking reasons
4. **Ratcheted quality** — Evaluation baseline prevents undocumented regressions
5. **Strategy default** — Prefer `dry_run`; enable real execution only when needed
6. **Tenant at store boundary** — `tenant_id` scopes persistence; fail closed without it

## Residual risks

- Subprocess execution uses `shell=True` with cwd constraint only
- Multi-tenant identity enforced at RunStore boundary; not kernel-level
- Replay sensitive to runtime config changes
- Network namespace isolation documented as spike only, not production default
- Landlock / `NETWORK_NS` backends detected but not wired into default execution

## Recommendations for backfeed

- Adopt `IntegrationRequest` / `IntegrationResponse` shape for workflow handshakes
- Require `ReviewerSummary` fields in operator dashboards
- Treat `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED` as a deployment-level gate
- Promote failure records (FR-001, FR-002) into platform regression suites
- Load deployment policy from `config/policies/`; never allow caller override of mandatory denies

## Credibility evidence

- 57 deterministic pytest cases
- 6 evaluation fixtures with baseline ratchet
- Documented experiments with controlled comparison script
- Failure taxonomy with machine-readable `FailureClass`
- CI on Python 3.11 and 3.12 (tests + evaluation + strategy comparison)

## Milestone status

Phases 0–9 and the v0.2 follow-up plan are **complete**. Next work is optional
hardening (Landlock, argv subprocess, platform backfeed) tracked in `TASKS.md`.
