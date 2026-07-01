# Integration Contract

## Role In A Larger System

GroundSealSandbox should plug into a parent platform as a specialized subsystem rather than a hidden helper module.

## Integration Expectations

- Callers provide typed input, not arbitrary prompts.
- Callers receive typed output plus enough evidence to understand the result.
- Subsystem invariants remain enforced even when the parent platform wants convenience.
- Failure states are explicit and machine-readable.

## Desired Boundary Shape

- thin adapter layer
- explicit request and response schemas
- deterministic local mode for testing
- minimal assumptions about the rest of the platform

## Subsystem-Local vs Parent-Provided

| Concern | Owner | Notes |
|---------|-------|-------|
| Sandbox strategy selection | **Subsystem** | `plan_execution` chooses from capability matrix |
| Filesystem constraint enforcement | **Subsystem** | Paths normalized and validated locally |
| Network policy enforcement | **Subsystem** | Policy attached to proposal; enforced at execution |
| Preflight checks | **Subsystem** | `preflight` is authoritative; parent cannot skip |
| Result and evidence schema | **Subsystem** | `ExecutionResult` + `ExecutionEvidence` are stable contracts |
| Caller identity (`caller_id`) | **Parent** | Passed in; logged in evidence only in v0 |
| Workflow orchestration | **Parent** | Parent calls `plan_execution` → `preflight` → `run` |
| UI and human review presentation | **Parent** | Subsystem provides structured evidence; parent renders |
| Tenancy / multi-tenant isolation | **Shared (Phase 5)** | Enforcement location TBD; subsystem must not weaken invariants |

### Integration handshake (v0)

```
Parent                          GroundSealSandbox
  |                                      |
  |-- plan_execution(cmd, ctx) ------->|
  |<--------- ExecutionProposal ---------|
  |                                      |
  |-- preflight(proposal) ------------->|
  |<--------- PreflightReport ----------|
  |                                      |
  |-- run(proposal) [if pass] --------->|
  |<--------- ExecutionResult -----------|
  |                                      |
  |-- describe_capabilities() -------->|
  |<--------- CapabilityProfile --------|
```

Parent responsibilities:
- Do not call `run` when `PreflightReport.overall_status` is `fail`.
- Pass typed `ExecutionContext`; do not embed policy overrides in `metadata`.
- Surface `failure_class` and `blocking_reasons` to operators.

## Questions To Resolve Later

- which types must stay platform-neutral
- where tenancy and identity should be enforced
- what belongs in shared contracts versus subsystem-local models
- how much evidence should flow back to the caller by default
