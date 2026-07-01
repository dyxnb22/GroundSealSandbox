"""Public API surface for GroundSealSandbox v0."""

from __future__ import annotations

from groundseal.contracts.models import (
    CapabilityProfile,
    ExecutionContext,
    ExecutionProposal,
    ExecutionResult,
    ExecutionStatus,
    FailureClass,
    PreflightReport,
    SandboxStrategy,
)
from groundseal.evidence.builder import build_simulated_evidence
from groundseal.execution.dry_run import run_dry
from groundseal.policy.normalize import NormalizationError, normalize_workspace_root
from groundseal.policy.strategy_matrix import AVAILABLE_STRATEGIES_V0, select_strategy
from groundseal.preflight.checks import run_preflight

SUPPORTED_CHECKS = [
    "schema_valid",
    "policy_denied",
    "strategy_mismatch",
    "network_policy_consistency",
]

LIMITS_V0 = {
    "max_command_length": 4096,
    "contract_version": "v0",
}


def describe_capabilities() -> CapabilityProfile:
    return CapabilityProfile(
        strategies=list(AVAILABLE_STRATEGIES_V0) + [SandboxStrategy.LOCAL_RESTRICTED],
        supported_checks=SUPPORTED_CHECKS,
        limits=LIMITS_V0,
    )


def plan_execution(command: str, context: ExecutionContext) -> ExecutionProposal:
    if len(command) > LIMITS_V0["max_command_length"]:
        raise NormalizationError("command exceeds max_command_length")

    normalized_root = normalize_workspace_root(context.workspace_root)
    from groundseal.contracts.models import ExecutionRequest

    request = ExecutionRequest(command=command, context=context)
    return select_strategy(request, normalize_root=normalized_root)


def preflight(proposal: ExecutionProposal) -> PreflightReport:
    return run_preflight(proposal)


def run(proposal: ExecutionProposal) -> ExecutionResult:
    if proposal.selected_strategy not in AVAILABLE_STRATEGIES_V0:
        return ExecutionResult(
            status=ExecutionStatus.DENIED,
            evidence=build_simulated_evidence(proposal),
            failure_class=FailureClass.STRATEGY_MISMATCH,
        )
    return run_dry(proposal)
