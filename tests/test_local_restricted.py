"""Tests for local_restricted subprocess execution."""

import pytest

from groundseal import plan_execution, preflight, run
from groundseal.config import reset_config, set_local_restricted_enabled
from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionStatus,
    PreflightStatus,
    SandboxStrategy,
)


@pytest.fixture(autouse=True)
def _reset_config():
    yield
    reset_config()


def test_local_restricted_disabled_by_default(tmp_path):
    ctx = ExecutionContext(
        workspace_root=str(tmp_path),
        requested_strategy=SandboxStrategy.LOCAL_RESTRICTED,
    )
    proposal = plan_execution("echo hi", ctx)
    assert proposal.selected_strategy == SandboxStrategy.DRY_RUN


def test_local_restricted_executes_when_enabled(tmp_path):
    set_local_restricted_enabled(True)
    ws = str(tmp_path)
    ctx = ExecutionContext(workspace_root=ws, requested_strategy=SandboxStrategy.LOCAL_RESTRICTED)
    proposal = plan_execution("echo groundseal_ok", ctx)
    assert proposal.selected_strategy == SandboxStrategy.LOCAL_RESTRICTED

    report = preflight(proposal)
    assert report.overall_status == PreflightStatus.PASS

    result = run(proposal)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.exit_code == 0
    assert "groundseal_ok" in (result.evidence.stdout or "")


def test_local_restricted_nonzero_exit_is_failed(tmp_path):
    set_local_restricted_enabled(True)
    ctx = ExecutionContext(
        workspace_root=str(tmp_path),
        requested_strategy=SandboxStrategy.LOCAL_RESTRICTED,
    )
    proposal = plan_execution("exit 42", ctx)
    result = run(proposal)
    assert result.status == ExecutionStatus.FAILED
    assert result.exit_code == 42
