"""Phase 8 strategy comparison experiment."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from groundseal import plan_execution, preflight, run  # noqa: E402
from groundseal.config import reset_config, set_local_restricted_enabled  # noqa: E402
from groundseal.contracts.models import ExecutionContext, SandboxStrategy  # noqa: E402


@dataclass
class StrategyObservation:
    strategy: str
    status: str
    exit_code: int | None
    has_stdout: bool
    elapsed_ms: float


def observe(command: str, workspace: str, strategy: SandboxStrategy) -> StrategyObservation:
    ctx = ExecutionContext(workspace_root=workspace, requested_strategy=strategy)
    start = time.perf_counter()
    proposal = plan_execution(command, ctx)
    report = preflight(proposal)
    if report.overall_status.value == "fail":
        result = run(proposal)
    else:
        result = run(proposal)
    elapsed = (time.perf_counter() - start) * 1000
    return StrategyObservation(
        strategy=proposal.selected_strategy.value,
        status=result.status.value,
        exit_code=result.exit_code,
        has_stdout=bool(result.evidence.stdout),
        elapsed_ms=round(elapsed, 2),
    )


def main() -> int:
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description="Compare dry_run vs local_restricted")
    parser.add_argument("--command", default="echo compare_ok")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "generated" / "strategy-comparison.json")
    args = parser.parse_args()

    reset_config()
    with tempfile.TemporaryDirectory() as tmp:
        dry = observe(args.command, tmp, SandboxStrategy.DRY_RUN)

        set_local_restricted_enabled(True)
        local = observe(args.command, tmp, SandboxStrategy.LOCAL_RESTRICTED)
        reset_config()

    report = {
        "command": args.command,
        "observations": [asdict(dry), asdict(local)],
        "conclusion": _conclusion(dry, local),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


def _conclusion(dry: StrategyObservation, local: StrategyObservation) -> str:
    if dry.status == "simulated" and local.status == "completed":
        return (
            "dry_run is faster and safer for planning; local_restricted provides "
            "real exit codes and stdout needed for verification."
        )
    return "unexpected outcome; review observations"


if __name__ == "__main__":
    raise SystemExit(main())
