# Open Questions

- Which parts of GroundSealSandbox must be deterministic from day one, and which can be deferred?
- What is the smallest implementation slice that will still teach something real?
- Which failure modes deserve dedicated fixtures instead of informal notes?
- Where should integration boundaries stop to avoid subsystem creep?
- Which tradeoffs are likely to be architecture-defining rather than local?

## Questions That Should Be Answered Before Broad Implementation

### What is the authoritative contract surface?

**Answered (v0):** Five types (`ExecutionRequest`, `ExecutionProposal`,
`PreflightReport`, `ExecutionResult`, `CapabilityProfile`) plus four public
functions (`plan_execution`, `preflight`, `run`, `describe_capabilities`).
See [contracts.md](contracts.md).

### What inputs are untrusted and how are they normalized?

**Answered (v0):** `command` and `context` are untrusted. `command` is
stripped and rejected if empty. `context.workspace_root` is resolved to an
absolute path with path-traversal rejection. `context.metadata` is ignored for
policy in v0. See [contracts.md](contracts.md#input-trust-model).

### What evidence must always be preserved?

**Answered (v0):** Strategy selection rationale, preflight per-check results,
and final status/failure_class. See [contracts.md](contracts.md#evidence-requirements).

### What counts as an acceptable fallback path?

**Answered (v0):** Only explicit downgrade to `dry_run` with documented
rationale. Silent relaxation of filesystem or network constraints is forbidden.
Ambiguous high-risk inputs fail closed with `ambiguous_high_risk`. See
[contracts.md](contracts.md#acceptable-fallback-paths).

## Questions Best Deferred Until After A Baseline Exists

- performance optimization tradeoffs
- richer UX or service wrappers
- storage or framework expansion beyond the minimum viable shape
