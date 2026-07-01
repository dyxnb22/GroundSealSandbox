# Contracts (v0)

Authoritative contract surface for GroundSealSandbox Phase 0–2. All public
behavior must map to these types and the four API functions defined in
[glossary.md](glossary.md).

## Public API Surface (v0)

```
plan_execution(command: str, context: ExecutionContext) -> ExecutionProposal
preflight(proposal: ExecutionProposal) -> PreflightReport
run(proposal: ExecutionProposal) -> ExecutionResult
describe_capabilities() -> CapabilityProfile
```

No other functions are part of the v0 public contract.

## Type Definitions

### ExecutionContext

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workspace_root` | string (path) | yes | Root directory for filesystem constraints |
| `requested_strategy` | SandboxStrategy | no | Caller preference; subsystem may override |
| `metadata` | object | no | Opaque caller hints; not trusted for policy |

### ExecutionRequest

| Field | Type | Required | Layer |
|-------|------|----------|-------|
| `command` | string | yes | Contract |
| `context` | ExecutionContext | yes | Contract |
| `caller_id` | string | no | Contract |

### ExecutionProposal

| Field | Type | Required | Layer |
|-------|------|----------|-------|
| `request` | ExecutionRequest | yes | Contract |
| `selected_strategy` | SandboxStrategy | yes | Policy |
| `strategy_rationale` | string | yes | Evidence |
| `fs_constraints` | FilesystemConstraints | yes | Policy |
| `network_policy` | NetworkPolicyProfile | yes | Policy |

### FilesystemConstraints

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workspace_root` | string (path) | yes | Absolute path; all relative paths resolve here |
| `allow_write_outside_root` | boolean | no | Default `false` |

### NetworkPolicyProfile

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | enum | yes | `deny_all`, `allow_listed` |
| `allowed_hosts` | string[] | no | Required when `mode` is `allow_listed` |

### SandboxStrategy

Enum values for v0:

| Value | Real execution | Notes |
|-------|----------------|-------|
| `dry_run` | no | Default for Phase 2 slice |
| `local_restricted` | yes (future) | Declared but not executable in v0 |

### PreflightCheck

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Check identifier (e.g. `schema_valid`) |
| `status` | enum | yes | `pass`, `fail`, `warn` |
| `reason` | string | no | Human-readable explanation |

### PreflightReport

| Field | Type | Required | Layer |
|-------|------|----------|-------|
| `checks` | PreflightCheck[] | yes | Contract |
| `overall_status` | enum | yes | `pass`, `fail`, `warn` |
| `blocking_reasons` | string[] | yes | Empty when `overall_status` is not `fail` |

### ExecutionEvidence

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `strategy_rationale` | string | yes | Why this strategy was selected |
| `preflight_summary` | string | no | Aggregated preflight outcome |
| `simulated_command` | string | no | Present for `dry_run` / `simulated` status |
| `checks_performed` | string[] | no | Names of checks that ran |

### ExecutionResult

| Field | Type | Required | Layer |
|-------|------|----------|-------|
| `status` | enum | yes | `simulated`, `completed`, `denied`, `failed` |
| `exit_code` | integer | no | Set only for real execution |
| `evidence` | ExecutionEvidence | yes | Evidence |
| `failure_class` | FailureClass | no | Set when status is `denied` or `failed` |

### FailureClass

Machine-readable failure categories (see [invariants.md](invariants.md)):

| Value | Meaning |
|-------|---------|
| `schema_invalid` | Input failed contract validation |
| `policy_denied` | Command or context violates policy |
| `strategy_mismatch` | Requested strategy unavailable |
| `ambiguous_high_risk` | Ambiguous input; fail-closed |
| `preflight_failed` | Proposal did not pass preflight |
| `execution_error` | Real execution failed (future) |

### CapabilityProfile

| Field | Type | Required | Layer |
|-------|------|----------|-------|
| `strategies` | SandboxStrategy[] | yes | Currently available strategies |
| `supported_checks` | string[] | yes | Preflight check names |
| `limits` | object | yes | Subsystem limits (e.g. max command length) |

## Input Trust Model

| Input | Trust level | Normalization |
|-------|-------------|---------------|
| `command` | Untrusted | Strip leading/trailing whitespace; reject empty |
| `context.workspace_root` | Untrusted | Resolve to absolute path; reject path traversal |
| `context.metadata` | Untrusted | Ignored for policy decisions in v0 |
| `caller_id` | Parent-provided | Logged in evidence only; not used for policy in v0 |

## Evidence Requirements

The following must always appear in outputs when applicable:

1. **Strategy selection rationale** — in `ExecutionProposal.strategy_rationale` and `ExecutionEvidence.strategy_rationale`
2. **Preflight per-check results** — in `PreflightReport.checks`
3. **Final status and failure class** — in `ExecutionResult.status` and `ExecutionResult.failure_class`

## Acceptable Fallback Paths

| Scenario | Allowed fallback | Forbidden |
|----------|------------------|-----------|
| Strategy unavailable | Downgrade to `dry_run` with explicit rationale | Silent strategy change without rationale |
| Ambiguous command | Fail with `ambiguous_high_risk` | Guess intent and execute |
| Network policy conflict | Fail with `strategy_mismatch` | Relax `deny_all` to permit execution |
| FS constraint violation | Fail with `policy_denied` | Widen `workspace_root` silently |

## State Transitions

```
ExecutionRequest
  -> plan_execution -> ExecutionProposal
  -> preflight -> PreflightReport
       (if overall_status == pass)
  -> run -> ExecutionResult
       (if overall_status == fail)
  -> run MUST NOT be called (caller responsibility; run() also enforces)
```

## Versioning

Contract version: **v0**. Breaking changes require a new version suffix and
updated fixtures.
