"""Real subprocess execution with workspace cwd constraint."""

from __future__ import annotations

import subprocess

from groundseal.contracts.models import (
    ExecutionEvidence,
    ExecutionProposal,
    ExecutionResult,
    ExecutionStatus,
    FailureClass,
    PreflightStatus,
)
from groundseal.evidence.builder import CHECK_NAMES
from groundseal.preflight.checks import run_preflight

DEFAULT_TIMEOUT_SECONDS = 30


def _build_executed_evidence(
    proposal: ExecutionProposal,
    *,
    stdout: str,
    stderr: str,
    run_id: str | None = None,
) -> ExecutionEvidence:
    return ExecutionEvidence(
        strategy_rationale=proposal.strategy_rationale,
        preflight_summary="all blocking checks passed",
        simulated_command=proposal.request.command,
        checks_performed=list(CHECK_NAMES),
        stdout=stdout,
        stderr=stderr,
        run_id=run_id,
    )


def run_local_restricted(
    proposal: ExecutionProposal,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    run_id: str | None = None,
) -> ExecutionResult:
    report = run_preflight(proposal)
    if report.overall_status == PreflightStatus.FAIL:
        return ExecutionResult(
            status=ExecutionStatus.DENIED,
            evidence=_build_executed_evidence(proposal, stdout="", stderr=""),
            failure_class=FailureClass.PREFLIGHT_FAILED,
        )

    cwd = proposal.fs_constraints.workspace_root
    try:
        completed = subprocess.run(
            proposal.request.command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            evidence=_build_executed_evidence(proposal, stdout="", stderr="timeout"),
            failure_class=FailureClass.EXECUTION_ERROR,
        )
    except OSError as exc:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            evidence=_build_executed_evidence(proposal, stdout="", stderr=str(exc)),
            failure_class=FailureClass.EXECUTION_ERROR,
        )

    status = ExecutionStatus.COMPLETED if completed.returncode == 0 else ExecutionStatus.FAILED
    failure = None if completed.returncode == 0 else FailureClass.EXECUTION_ERROR

    return ExecutionResult(
        status=status,
        exit_code=completed.returncode,
        evidence=_build_executed_evidence(
            proposal,
            stdout=completed.stdout,
            stderr=completed.stderr,
            run_id=run_id,
        ),
        failure_class=failure,
    )
