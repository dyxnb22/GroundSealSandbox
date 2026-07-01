"""Negative-path and fail-closed behavior tests."""

import json
from pathlib import Path

import pytest

from groundseal import plan_execution, preflight, run
from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionStatus,
    FailureClass,
    PreflightStatus,
    SandboxStrategy,
)
from groundseal.policy.normalize import NormalizationError

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_policy_denied_blocks_execution():
    data = _load_fixture("policy_denied.json")
    ctx = ExecutionContext(**data["context"])
    proposal = plan_execution(data["command"], ctx)
    report = preflight(proposal)
    assert report.overall_status == PreflightStatus.FAIL
    assert any("denylist" in r for r in report.blocking_reasons)

    result = run(proposal)
    assert result.status == ExecutionStatus.DENIED
    assert result.failure_class == FailureClass.PREFLIGHT_FAILED


def test_ambiguous_high_risk_path_traversal():
    data = _load_fixture("ambiguous_high_risk.json")
    ctx = ExecutionContext(**data["context"])
    with pytest.raises(NormalizationError, match="path traversal"):
        plan_execution(data["command"], ctx)


def test_strategy_mismatch_downgrades_with_rationale():
    data = _load_fixture("strategy_mismatch.json")
    ctx = ExecutionContext(**data["context"])
    proposal = plan_execution(data["command"], ctx)
    assert proposal.selected_strategy == SandboxStrategy.DRY_RUN
    assert "downgraded" in proposal.strategy_rationale.lower()

    report = preflight(proposal)
    assert report.overall_status == PreflightStatus.PASS


def test_empty_command_rejected_at_request_build():
    with pytest.raises(Exception):
        plan_execution("   ", ExecutionContext(workspace_root="/tmp/ws"))
