"""Dry-run execution (no real shell invocation)."""

from __future__ import annotations

from groundseal.contracts.models import (
    ExecutionProposal,
    ExecutionResult,
    ExecutionStatus,
    FailureClass,
    PreflightStatus,
)
from groundseal.evidence.builder import build_simulated_evidence
from groundseal.preflight.checks import run_preflight


def run_dry(proposal: ExecutionProposal) -> ExecutionResult:
    report = run_preflight(proposal)
    if report.overall_status == PreflightStatus.FAIL:
        return ExecutionResult(
            status=ExecutionStatus.DENIED,
            evidence=build_simulated_evidence(proposal),
            failure_class=FailureClass.PREFLIGHT_FAILED,
        )

    if proposal.selected_strategy.value != "dry_run":
        return ExecutionResult(
            status=ExecutionStatus.DENIED,
            evidence=build_simulated_evidence(proposal),
            failure_class=FailureClass.STRATEGY_MISMATCH,
        )

    return ExecutionResult(
        status=ExecutionStatus.SIMULATED,
        evidence=build_simulated_evidence(proposal),
    )
