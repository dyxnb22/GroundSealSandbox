#!/usr/bin/env python3
"""Run evaluation fixtures and optionally check against baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from groundseal.evaluation.runner import check_against_baseline, run_evaluation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GroundSealSandbox evaluation fixtures")
    parser.add_argument(
        "--check-baseline",
        action="store_true",
        help="Fail if metrics regress vs tests/baselines/evaluation_v0.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "generated" / "evaluation-latest.json",
        help="Write JSON report to this path",
    )
    args = parser.parse_args()

    report = run_evaluation()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report.to_dict(), indent=2) + "\n")

    print(f"Evaluation: {report.passed_fixtures}/{report.total_fixtures} fixtures passed")
    print(f"  contract_pass_rate: {report.contract_pass_rate}")
    print(f"  negative_path_correctness: {report.negative_path_correctness}")
    print(f"Report written to {args.output}")

    if args.check_baseline:
        regressions = check_against_baseline(report)
        if regressions:
            for r in regressions:
                print(f"REGRESSION: {r}", file=sys.stderr)
            return 1

    return 0 if report.passed_fixtures == report.total_fixtures else 1


if __name__ == "__main__":
    raise SystemExit(main())
