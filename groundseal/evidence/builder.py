"""Evidence assembly for execution results."""

from __future__ import annotations

from groundseal.contracts.models import ExecutionEvidence, ExecutionProposal

CHECK_NAMES = [
    "schema_valid",
    "policy_denied",
    "strategy_mismatch",
    "network_policy_consistency",
]


def build_simulated_evidence(proposal: ExecutionProposal) -> ExecutionEvidence:
    return ExecutionEvidence(
        strategy_rationale=proposal.strategy_rationale,
        preflight_summary="all blocking checks passed",
        simulated_command=proposal.request.command,
        checks_performed=list(CHECK_NAMES),
    )

