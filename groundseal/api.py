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
from groundseal.execution.local_restricted import run_local_restricted
from groundseal.policy.normalize import NormalizationError, normalize_workspace_root
from groundseal.policy.strategy_matrix import get_available_strategies, select_strategy
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
    available = get_available_strategies()
    declared = list(available)
    if SandboxStrategy.LOCAL_RESTRICTED not in available:
        declared.append(SandboxStrategy.LOCAL_RESTRICTED)
    return CapabilityProfile(
        strategies=declared,
        supported_checks=SUPPORTED_CHECKS,
        limits={
            **LIMITS_V0,
            "local_restricted_enabled": SandboxStrategy.LOCAL_RESTRICTED in available,
        },
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


def run(proposal: ExecutionProposal, *, run_id: str | None = None) -> ExecutionResult:
    available = get_available_strategies()
    if proposal.selected_strategy not in available:
        return ExecutionResult(
            status=ExecutionStatus.DENIED,
            evidence=build_simulated_evidence(proposal),
            failure_class=FailureClass.STRATEGY_MISMATCH,
        )

    if proposal.selected_strategy == SandboxStrategy.LOCAL_RESTRICTED:
        return run_local_restricted(proposal, run_id=run_id)

    return run_dry(proposal)
