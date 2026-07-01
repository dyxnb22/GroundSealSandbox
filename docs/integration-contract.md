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
| Tenancy / multi-tenant isolation | **Shared (v0.2)** | `tenant_id` on `ExecutionContext`; `RunStore` scoped by tenant |

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

## Adapter layer (v0)

Parent systems may use the thin adapter instead of calling four functions
directly:

```python
from groundseal.adapter import execute_workflow

response = execute_workflow({
    "command": "echo hello",
    "context": {"workspace_root": "/tmp/workspace"},
    "caller_id": "parent-workflow-1",
})
```

The adapter:
- Validates `IntegrationRequest` and returns `schema_invalid` on malformed input
- Always runs `plan_execution` → `preflight` → `run` (preflight cannot be skipped)
- Ignores policy override hints in `context.metadata`
- Returns `IntegrationResponse` with `evidence_summary` for parent UI
- When `persist_run=true`, requires `context.tenant_id` and a `RunStore` instance

### Tenancy (v0.2)

- Parent provides `context.tenant_id` as the isolation key.
- `RunStore.save/get/list_ids/replay_run` all require the same `tenant_id`.
- Cross-tenant reads return `None`; `persist_run` without `tenant_id` returns
  `policy_denied`.
- `caller_id` remains audit metadata only; it is not used for isolation.

Example with persistence:

```python
from groundseal.adapter import execute_workflow
from groundseal.lifecycle import RunStore

store = RunStore(path=Path("runs.json"))
response = execute_workflow({
    "command": "echo hello",
    "context": {
        "workspace_root": "/tmp/workspace",
        "tenant_id": "org-123",
    },
    "persist_run": True,
}, store=store)
```

Example payloads: `examples/integration_request_valid.json`

Boundary tests: `tests/test_integration_adapter.py`, `tests/test_tenant_boundary.py`

## Questions To Resolve Later

- which types must stay platform-neutral
- what belongs in shared contracts versus subsystem-local models
- how much evidence should flow back to the caller by default
