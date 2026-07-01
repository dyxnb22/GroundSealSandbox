# Known Limitations (v0)

Documented constraints of the Phase 2 dry-run slice.

## Execution

- **No real subprocess invocation.** `run()` with `dry_run` returns
  `status=simulated` only.
- **`local_restricted` is declared but not executable.** Requests downgrade to
  `dry_run` with explicit rationale.

## Policy

- Denylist is a minimal static pattern set in `groundseal/policy/normalize.py`.
- `context.metadata` is ignored for policy decisions.

## Network and filesystem

- No OS-level network isolation or mount namespaces.
- Filesystem constraints are validated logically; paths are not enforced at the
  kernel level.

## Capability matrix

- Only `dry_run` is in `AVAILABLE_STRATEGIES_V0`.
- Strategy matrix row for `local_restricted` exists for forward compatibility.

## Evaluation

- Six fixture categories plus one integration-boundary variant in `tests/fixtures/manifest.json`.
- Run `python3 scripts/evaluate.py --check-baseline` for ratcheted evaluation.
- CI runs pytest and evaluation baseline on push/PR.
