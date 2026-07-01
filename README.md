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

## Current Stage

**Phase 0 complete. Phases 1–3 baseline complete for dry-run slice.**

Contracts, glossary, evaluation categories, and integration boundaries are
defined. Python 3.11+ implementation uses Pydantic v2 models aligned with
`docs/contracts.md`. The v0 slice implements preflight + dry-run (no real shell
execution). See `docs/known-limitations.md` for gaps.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Relationship To The Parent Platform

This project is intentionally narrower than the original platform. It should
become better than the parent implementation at its own specialty, then feed
stable contracts and lessons back into the broader system.
