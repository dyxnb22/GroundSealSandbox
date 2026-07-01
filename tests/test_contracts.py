"""Contract model validation tests."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionRequest,
    NetworkMode,
    NetworkPolicyProfile,
    PreflightReport,
    PreflightStatus,
    PreflightCheck,
    SandboxStrategy,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_valid_execution_request_example():
    data = json.loads((EXAMPLES / "execution_request_valid.json").read_text())
    req = ExecutionRequest(**data)
    assert req.command == "echo hello"
    assert req.context.requested_strategy == SandboxStrategy.DRY_RUN


def test_invalid_empty_command_rejected():
    data = json.loads((EXAMPLES / "execution_request_invalid.json").read_text())
    with pytest.raises(ValidationError):
        ExecutionRequest(**data)


def test_network_policy_allow_listed_requires_hosts():
    with pytest.raises(ValidationError):
        NetworkPolicyProfile(mode=NetworkMode.ALLOW_LISTED, allowed_hosts=[])


def test_preflight_report_fail_requires_blocking_reasons():
    with pytest.raises(ValidationError):
        PreflightReport(
            checks=[PreflightCheck(name="x", status=PreflightStatus.FAIL, reason="bad")],
            overall_status=PreflightStatus.FAIL,
            blocking_reasons=[],
        )


def test_preflight_report_pass_rejects_blocking_reasons():
    with pytest.raises(ValidationError):
        PreflightReport(
            checks=[PreflightCheck(name="x", status=PreflightStatus.PASS)],
            overall_status=PreflightStatus.PASS,
            blocking_reasons=["should not be here"],
        )
