"""End-to-end dry-run path."""

import json
from pathlib import Path

from groundseal import describe_capabilities, plan_execution, preflight, run
from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionStatus,
    PreflightStatus,
    SandboxStrategy,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_describe_capabilities_lists_dry_run():
    profile = describe_capabilities()
    assert SandboxStrategy.DRY_RUN in profile.strategies
    assert "schema_valid" in profile.supported_checks


def test_e2e_dry_run_happy_path():
    data = _load_fixture("happy_path.json")
    ctx = ExecutionContext(**data["context"])
    proposal = plan_execution(data["command"], ctx)
    assert proposal.selected_strategy == SandboxStrategy.DRY_RUN

    report = preflight(proposal)
    assert report.overall_status == PreflightStatus.PASS

    result = run(proposal)
    assert result.status == ExecutionStatus.SIMULATED
    assert result.evidence.strategy_rationale
    assert result.evidence.simulated_command == "echo hello"
    assert "dry_run" in result.evidence.strategy_rationale.lower() or proposal.strategy_rationale
