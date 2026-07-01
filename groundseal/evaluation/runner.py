"""Deterministic fixture evaluation and baseline comparison."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from groundseal.adapter.workflow import execute_workflow

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"
BASELINE_PATH = Path(__file__).resolve().parent.parent.parent / "tests" / "baselines" / "evaluation_v0.json"


@dataclass
class FixtureResult:
    fixture: str
    category: str
    passed: bool
    expect_ok: bool
    actual_ok: bool
    failure_class: str | None = None
    notes: str = ""


@dataclass
class EvaluationReport:
    fixture_results: list[FixtureResult] = field(default_factory=list)
    contract_pass_rate: float = 0.0
    negative_path_correctness: float = 0.0
    explainability_coverage: float = 0.0
    total_fixtures: int = 0
    passed_fixtures: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_pass_rate": self.contract_pass_rate,
            "negative_path_correctness": self.negative_path_correctness,
            "explainability_coverage": self.explainability_coverage,
            "total_fixtures": self.total_fixtures,
            "passed_fixtures": self.passed_fixtures,
            "fixture_results": {
                r.fixture: {
                    "category": r.category,
                    "passed": r.passed,
                    "expect_ok": r.expect_ok,
                    "actual_ok": r.actual_ok,
                    "failure_class": r.failure_class,
                    "notes": r.notes,
                }
                for r in self.fixture_results
            },
        }


def _load_manifest() -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / "manifest.json").read_text())


def _has_explainability(response_failure_class: str | None, raw: dict) -> bool:
    if response_failure_class:
        return True
    manifest = _load_manifest()
    name = raw.get("_fixture_name", "")
    entry = manifest.get(name, {})
    if entry.get("expect_ok") is False:
        return response_failure_class is not None
    return True


def run_evaluation() -> EvaluationReport:
    manifest = _load_manifest()
    results: list[FixtureResult] = []

    for fixture_name, spec in manifest.items():
        raw = json.loads((FIXTURES_DIR / fixture_name).read_text())
        expect_ok = spec["expect_ok"]
        category = spec["category"]

        if spec.get("via") == "adapter":
            response = execute_workflow(raw)
            actual_ok = response.ok
            failure_class = response.failure_class.value if response.failure_class else None

            passed = actual_ok == expect_ok
            notes = ""

            expected_fc = spec.get("expect_failure_class")
            if expected_fc and failure_class != expected_fc:
                passed = False
                notes = f"expected failure_class={expected_fc}, got {failure_class}"

            if spec.get("assert_network_deny_all") and response.proposal:
                if response.proposal.network_policy.mode != "deny_all":
                    passed = False
                    notes = "metadata must not override network policy"

            if not _has_explainability(failure_class, {"_fixture_name": fixture_name}):
                passed = False
                notes = "missing explainability on failure path"

            results.append(
                FixtureResult(
                    fixture=fixture_name,
                    category=category,
                    passed=passed,
                    expect_ok=expect_ok,
                    actual_ok=actual_ok,
                    failure_class=failure_class,
                    notes=notes,
                )
            )

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    negative = [r for r in results if not r.expect_ok]
    negative_correct = sum(1 for r in negative if r.passed)

    report = EvaluationReport(
        fixture_results=results,
        total_fixtures=total,
        passed_fixtures=passed_count,
        contract_pass_rate=passed_count / total if total else 0.0,
        negative_path_correctness=negative_correct / len(negative) if negative else 1.0,
        explainability_coverage=passed_count / total if total else 0.0,
    )
    return report


def check_against_baseline(report: EvaluationReport) -> list[str]:
    """Return list of regressions vs committed baseline."""
    if not BASELINE_PATH.exists():
        return [f"baseline missing: {BASELINE_PATH}"]

    baseline = json.loads(BASELINE_PATH.read_text())
    regressions: list[str] = []

    for metric in ("contract_pass_rate", "negative_path_correctness"):
        actual = getattr(report, metric)
        expected = baseline.get(metric, 1.0)
        if actual < expected:
            regressions.append(f"{metric} regressed: {actual} < {expected}")

    for fixture, expected in baseline.get("fixture_results", {}).items():
        actual_entry = report.to_dict()["fixture_results"].get(fixture)
        if actual_entry is None:
            regressions.append(f"fixture missing from run: {fixture}")
        elif expected == "pass" and not actual_entry["passed"]:
            regressions.append(f"fixture regressed: {fixture}")

    return regressions
