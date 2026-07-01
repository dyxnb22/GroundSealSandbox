"""Integration adapter and boundary tests."""

import json
from pathlib import Path

from groundseal.adapter import execute_workflow
from groundseal.contracts.models import FailureClass, NetworkMode, PreflightStatus

FIXTURES = Path(__file__).resolve().parent / "fixtures"
EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_adapter_happy_path_e2e():
    resp = execute_workflow(_load("happy_path.json"))
    assert resp.ok is True
    assert resp.proposal is not None
    assert resp.preflight is not None
    assert resp.preflight.overall_status == PreflightStatus.PASS
    assert resp.result is not None
    assert resp.result.status.value == "simulated"
    assert resp.evidence_summary["strategy_rationale"]


def test_adapter_schema_invalid_missing_workspace_root():
    resp = execute_workflow(_load("schema_invalid.json"))
    assert resp.ok is False
    assert resp.failure_class == FailureClass.SCHEMA_INVALID
    assert resp.error
    assert resp.proposal is None


def test_adapter_policy_denied_does_not_succeed():
    resp = execute_workflow(_load("policy_denied.json"))
    assert resp.ok is False
    assert resp.failure_class == FailureClass.PREFLIGHT_FAILED
    assert resp.preflight is not None
    assert resp.preflight.overall_status == PreflightStatus.FAIL


def test_adapter_always_runs_preflight_before_run():
    """Parent cannot skip preflight; adapter always produces preflight report."""
    resp = execute_workflow(_load("happy_path.json"))
    assert resp.preflight is not None
    check_names = {c.name for c in resp.preflight.checks}
    assert "schema_valid" in check_names
    assert "policy_denied" in check_names


def test_adapter_ignores_metadata_policy_override():
    resp = execute_workflow(_load("integration_boundary_metadata.json"))
    assert resp.ok is True
    assert resp.proposal is not None
    assert resp.proposal.network_policy.mode == NetworkMode.DENY_ALL


def test_adapter_ambiguous_high_risk_path_traversal():
    resp = execute_workflow(_load("ambiguous_high_risk.json"))
    assert resp.ok is False
    assert resp.failure_class == FailureClass.AMBIGUOUS_HIGH_RISK


def test_integration_request_valid_example_roundtrip():
    data = json.loads((EXAMPLES / "integration_request_valid.json").read_text())
    resp = execute_workflow(data)
    assert resp.ok is True
