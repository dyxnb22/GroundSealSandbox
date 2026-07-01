"""Tests for configurable PolicyProfile and denylist."""

from pathlib import Path

import pytest

from groundseal import plan_execution, preflight, set_policy_profile
from groundseal.config import reset_config
from groundseal.contracts.models import ExecutionContext, PolicyProfile
from groundseal.policy.profile import (
    builtin_mandatory_patterns,
    command_matches_denylist,
    default_policy_profile,
    load_policy_profile,
)


def teardown_function():
    reset_config()


def test_default_profile_matches_v0_denylist():
    profile = default_policy_profile()
    assert command_matches_denylist("rm -rf /", profile)
    assert command_matches_denylist(":(){ :|:& };:", profile)
    assert not command_matches_denylist("echo hello", profile)


def test_mandatory_patterns_cannot_be_removed(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(
        "schema_version: '1'\nname: test\nmandatory_denies: []\noperator_denies: []\n"
    )
    merged = load_policy_profile(path)
    assert command_matches_denylist("rm -rf /", merged)


def test_operator_deny_extends_profile(tmp_path):
    profile = PolicyProfile(
        name="custom",
        mandatory_denies=builtin_mandatory_patterns(),
        operator_denies=[r"curl\s+"],
    )
    set_policy_profile(profile)
    ctx = ExecutionContext(workspace_root=str(tmp_path))
    proposal = plan_execution("curl https://example.com", ctx)
    report = preflight(proposal)
    assert report.overall_status.value == "fail"
    assert "denylist" in report.blocking_reasons[0]


def test_strict_yaml_loads():
    path = Path(__file__).resolve().parents[1] / "config" / "policies" / "strict.yaml"
    profile = load_policy_profile(path)
    assert profile.name == "strict"
    assert command_matches_denylist("wget http://x", profile)


def test_plan_execution_uses_default_without_override(tmp_path):
    ctx = ExecutionContext(workspace_root=str(tmp_path))
    proposal = plan_execution("echo ok", ctx)
    report = preflight(proposal)
    assert report.overall_status.value == "pass"
