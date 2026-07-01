# OS Enforcement Strategy (v0.2)

## Purpose

Describe how GroundSealSandbox maps sandbox strategies to OS-level enforcement
backends and trust tiers without silently relaxing policy.

## Trust tier matrix

| Strategy | Trust tier | Enforcement backend | Real execution |
|----------|------------|---------------------|----------------|
| `dry_run` | 0 | `none` | No |
| `local_restricted` | 1 | `process_only` | Yes (opt-in) |

Reserved for future slices:

| Backend | Trust tier | Status |
|---------|------------|--------|
| `landlock` | 2 | Detected only; not default execution path |
| `network_ns` | 3 | Spike only; see network-isolation experiment |

## Selection rules

1. Caller-requested `local_restricted` is used only when
   `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED` (or in-process test flag) is set.
2. Otherwise downgrade to `dry_run` with explicit `strategy_rationale`.
3. `resolve_enforcement_backend()` picks the best available backend for the
   selected strategy; v0.2 default remains `process_only` for
   `local_restricted`.
4. Silent relaxation of filesystem or network policy is forbidden.

## Capability detection

`detect_os_capabilities()` probes:

- platform and root status
- Landlock availability (Linux kernel >= 5)
- `unshare` presence for network namespace experiments

`describe_capabilities().limits` exposes these fields for parent operators.

## Evidence

Real execution records `enforcement_backend` on `ExecutionEvidence` so reviewers
can see which backend was active without reverse-engineering config.

## Deferred

- Wiring Landlock or network namespaces into default `local_restricted`
- Replacing `shell=True` subprocess with argv-based invocation
