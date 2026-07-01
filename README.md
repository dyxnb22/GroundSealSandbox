# GroundSealSandbox

A controlled command-execution boundary for agent-driven development workflows

## Overview

GroundSealSandbox is a long-horizon learning and engineering project focused on sandbox strategy selection, filesystem and network constraints, preflight checks, execution logging, and deterministic failure handling.
It is intentionally scoped as a standalone subsystem so it can later plug back
into a governed enterprise-agent platform without inheriting that platform's
full codebase or accidental complexity on day one.

## Why This Exists

Command execution is one of the highest-risk parts of coding agents. This project isolates the execution boundary so policies, capabilities, and failure modes can be understood independently.

## What This Project Is

- A subsystem-first engineering project with explicit contracts.
- A documentation-led project intended for sustained Cursor Cloud Agent work.
- A place to learn one difficult slice of enterprise agent systems deeply.
- A project that should produce reusable contracts, tests, and design notes.

## What This Project Is Not

- becoming a general container platform
- supporting unrestricted shell access by default
- treating sandboxing as a best-effort hint
- not a generic chatbot wrapper
- not a fast demo optimized for screenshots instead of understanding

## Core Capability Scope

- capability model
- sandbox strategy matrix
- preflight checklist
- execution result schema
- network policy profile

## Planned Interfaces

- `plan_execution(command, context) -> proposal`
- `run(proposal) -> result`
- `preflight(proposal) -> checks`
- `describe_capabilities() -> profile`

## Documentation Map

- `PROJECT_BRIEF.md` — project framing, goals, non-goals, and learning value.
- `AGENTS.md` — default execution rules for future agents.
- `TASKS.md` — prioritized task breakdown for now, next, and later.
- `docs/architecture.md` — subsystem map and trust boundaries.
- `docs/design-principles.md` — design rules and tradeoff posture.
- `docs/coding-guidelines.md` — implementation discipline once code starts.
- `docs/roadmap.md` — phased long-term execution plan.
- `docs/evaluation-plan.md` — how quality and regressions will be measured.
- `docs/failure-analysis-plan.md` — how failures are classified and reviewed.
- `docs/execution-rhythm.md` — how to keep long-running agent work disciplined.
- `docs/integration-contract.md` — how this project will plug back into larger systems.
- `docs/open-questions.md` — unresolved research and implementation questions.
- `docs/glossary.md` — canonical terminology.
- `docs/contracts.md` — v0 type and API contract definitions.
- `docs/lifecycle-model.md` — run_id, replay, and storage.
- `docs/reviewer-guide.md` — operator/reviewer inspection flow.
- `docs/case-study.md` — v0 summary and platform backfeed recommendations.

## Current Stage

**Phases 0–9 baseline complete for v0.1 slice.**

Dry-run is the default; `local_restricted` subprocess execution is available with
explicit opt-in. Lifecycle recording/replay, reviewer summaries, and strategy
comparison experiment are documented and tested. See `docs/case-study.md` and
`docs/known-limitations.md`.

## Development

```bash
pip install -e ".[dev]"
python3 -m pytest -v
python3 scripts/evaluate.py --check-baseline
python3 scripts/compare_strategies.py
```

### Integration adapter (parent workflow)

```python
from groundseal.adapter import execute_workflow
from groundseal.review import build_reviewer_summary, format_reviewer_markdown

response = execute_workflow({
    "command": "echo hello",
    "context": {"workspace_root": "/tmp/workspace"},
})
print(format_reviewer_markdown(build_reviewer_summary(response)))
```

### Real execution (opt-in)

```bash
export GROUNDSEAL_ENABLE_LOCAL_RESTRICTED=1
```

```python
from groundseal import plan_execution, preflight, run
from groundseal.contracts.models import ExecutionContext, SandboxStrategy

proposal = plan_execution(
    "echo hello",
    ExecutionContext(workspace_root="/tmp/ws", requested_strategy=SandboxStrategy.LOCAL_RESTRICTED),
)
run(proposal)  # after preflight pass
```

### Lifecycle recording

```python
from groundseal.lifecycle import RunStore, run_and_record, replay_run

store = RunStore()
record = run_and_record(proposal, preflight_report, store, tenant_id="tenant-a")
comparison = replay_run(record.run_id, store, tenant_id="tenant-a")
```

## Relationship To The Parent Platform

This project is intentionally narrower than the original platform. It should
become better than the parent implementation at its own specialty, then feed
stable contracts and lessons back into the broader system.
