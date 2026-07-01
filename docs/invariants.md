# Invariants

Hard rules enforced by GroundSealSandbox. Code must not violate these; tests
should guard each invariant where practical.

## I1: Preflight gate

A proposal with `PreflightReport.overall_status == fail` **must not** be
executed. `run()` enforces this and returns `status=denied` with
`failure_class=preflight_failed` if called anyway.

## I2: Network policy vs strategy

When `network_policy.mode == deny_all`, the selected strategy **must not**
require network access. Violations fail with `strategy_mismatch`.

## I3: Fail-closed on ambiguous input

Empty commands (after strip) and path-traversal patterns in `workspace_root`
fail with `ambiguous_high_risk`. The subsystem does not guess intent.

## I4: Machine-readable failures

Every denial or failure path **must** set `FailureClass` on `ExecutionResult`
or include a `reason` on the failing `PreflightCheck`.

## I5: Evidence preservation

Outputs **must** include:
- `strategy_rationale` on proposals and execution evidence
- per-check results in `PreflightReport.checks`
- `status` and `failure_class` (when applicable) on `ExecutionResult`

## I6: No silent constraint relaxation

Filesystem and network constraints **must not** be widened without explicit
documented rationale. The only allowed v0 fallback is downgrade to `dry_run`
with rationale recorded.

## I7: Untrusted metadata

`ExecutionContext.metadata` is **ignored** for policy decisions in v0.

## I8: Strategy availability

`local_restricted` is declared in the capability profile but **not executable**
in v0. Requests for it fail with `strategy_mismatch` unless overridden to
`dry_run` with explicit rationale during planning.
