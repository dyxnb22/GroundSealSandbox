# Glossary

Canonical terminology for GroundSealSandbox. Use these terms consistently across
docs, contracts, and implementation.

## Core Types

### ExecutionRequest

Input to `plan_execution`. Contains an untrusted `command` string, execution
`context` (workspace paths, caller hints), and optional `caller_id` supplied by
the parent platform.

### ExecutionProposal

Output of `plan_execution`. Bundles the normalized request, a `selected_strategy`,
filesystem constraints, network policy, and strategy selection rationale. A
proposal is the unit passed to `preflight` and, if allowed, `run`.

### PreflightCheck

A single pre-execution gate result. Each check has a `name`, `status`
(`pass`, `fail`, or `warn`), and an optional human-readable `reason`.

### PreflightReport

Output of `preflight`. Aggregates all `PreflightCheck` items, an
`overall_status`, and `blocking_reasons` when execution must not proceed.

### ExecutionResult

Output of `run`. Contains `status`, optional `exit_code`, `evidence`, and
optional `failure_class` when the run did not succeed.

### CapabilityProfile

Output of `describe_capabilities`. Describes supported sandbox strategies,
available preflight checks, and subsystem limits visible to callers.

## Policy Types

### SandboxStrategy

A named row in the strategy matrix (e.g. `dry_run`, `local_restricted`).
Determines whether real execution occurs and which constraints apply.

### NetworkPolicyProfile

Network constraint configuration attached to a proposal. Examples: `deny_all`,
`allow_listed`.

### FilesystemConstraints

Path and access rules for a proposal (e.g. `workspace_root`, allowed write
paths).

## Subsystem Boundaries

| Term | Subsystem | Responsibility |
|------|-----------|----------------|
| Sandbox strategy selection | Policy layer | Choose `SandboxStrategy` from request + capabilities |
| Filesystem constraints | Policy layer | Define and enforce path boundaries |
| Network constraints | Policy layer | Define network access rules per strategy |
| Preflight checks | Contract + Policy | Validate proposal before execution |
| Execution logging | Evidence layer | Capture decisions and outcomes in `evidence` |
| Deterministic failure handling | Contract + Policy | Fail closed with `FailureClass` on ambiguous paths |

## Public API Functions

| Function | Input | Output |
|----------|-------|--------|
| `plan_execution` | `command`, `context` | `ExecutionProposal` |
| `preflight` | `ExecutionProposal` | `PreflightReport` |
| `run` | `ExecutionProposal` | `ExecutionResult` |
| `describe_capabilities` | (none) | `CapabilityProfile` |

## Status Values

### Preflight overall_status

- `pass` — all blocking checks passed; `run` may proceed
- `fail` — one or more blocking checks failed; `run` must not proceed
- `warn` — non-blocking issues present; behavior defined per check

### ExecutionResult status

- `simulated` — dry-run completed without real execution
- `completed` — real execution finished (future)
- `denied` — execution blocked (e.g. preflight bypass attempt)
- `failed` — execution attempted but did not succeed

## Related Documents

- [contracts.md](contracts.md) — field-level contract definitions
- [architecture.md](architecture.md) — layer model and trust boundaries
- [invariants.md](invariants.md) — hard rules enforced by the subsystem
