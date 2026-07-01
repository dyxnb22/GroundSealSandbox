# Network Isolation Spike

## Purpose

Determine whether basic OS-level egress isolation (`unshare --net`) is viable
on typical Linux dev hosts before promoting `EnforcementBackend.NETWORK_NS`.

## Hypothesis

A subprocess started inside a new network namespace cannot reach external hosts
via `curl`, while the same command succeeds (or fails for unrelated reasons)
outside the namespace.

## Procedure

Run manually (not in CI):

```bash
bash scripts/spike_network_isolate.sh
```

The script:

1. Checks for `unshare` and `curl`
2. Attempts baseline `curl` without isolation
3. Attempts `curl` inside `unshare --net`
4. Expects failure in the isolated case

## Observations

Record host-specific results here when run:

| Environment | Baseline curl | Isolated curl | Notes |
|-------------|---------------|---------------|-------|
| CI agent | skipped | skipped | no root / no unshare in CI by design |

## Conclusion (v0.2)

- Spike is **documented and scripted** but **not wired** into
  `local_restricted` production execution.
- `EnforcementBackend.NETWORK_NS` remains a capability flag only.
- Promoting network isolation to default execution requires a follow-up slice
  with privilege model and regression fixtures.

## Evaluation intent

- Negative path: isolated `curl` must not succeed when namespace is effective.
- CI: spike script exits 0 with SKIP when tools unavailable (no false green on
  isolation claims).
