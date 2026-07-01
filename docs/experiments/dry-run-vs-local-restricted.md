# Experiment: dry_run vs local_restricted

## Purpose

Compare the two v0 sandbox strategies on a controlled command to inform when
each is appropriate.

## Hypothesis

- `dry_run` is sufficient for policy and planning validation
- `local_restricted` is required when exit codes or stdout matter

## Setup

- Command: `echo compare_ok`
- Workspace: ephemeral temp directory
- `local_restricted` enabled via in-process opt-in (same as
  `GROUNDSEAL_ENABLE_LOCAL_RESTRICTED=1`)

## Procedure

```bash
python scripts/compare_strategies.py
```

## Observed tradeoffs (v0)

| Dimension | dry_run | local_restricted |
|-----------|---------|------------------|
| Shell invoked | No | Yes |
| Exit code | N/A | Real (0 on success) |
| stdout captured | No | Yes |
| Latency | Lower | Higher |
| Risk surface | Minimal | Subprocess in workspace cwd |

## Conclusion

**Chosen default:** `dry_run` for planning and preflight validation.

**Opt-in real execution:** `local_restricted` when the parent workflow needs
verifiable command output or exit codes. Requires explicit
`GROUNDSEAL_ENABLE_LOCAL_RESTRICTED` or `set_local_restricted_enabled(True)`.

## Residual uncertainty

- No OS-level network isolation in either strategy
- `shell=True` subprocess has inherent command-injection risk if preflight is weak
- Replay drift may occur if opt-in config changes between runs

## Evidence

- Script: `scripts/compare_strategies.py`
- Test: `tests/test_strategy_comparison.py`
- Output: `reports/generated/strategy-comparison.json`
