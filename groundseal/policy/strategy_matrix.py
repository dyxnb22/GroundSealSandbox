"""Static sandbox strategy matrix."""

from __future__ import annotations

from dataclasses import dataclass

from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionProposal,
    ExecutionRequest,
    FilesystemConstraints,
    NetworkMode,
    NetworkPolicyProfile,
    SandboxStrategy,
)

AVAILABLE_STRATEGIES_V0: frozenset[SandboxStrategy] = frozenset({SandboxStrategy.DRY_RUN})


@dataclass(frozen=True)
class StrategySpec:
    strategy: SandboxStrategy
    real_execution: bool
    requires_network: bool
    description: str


STRATEGY_MATRIX: dict[SandboxStrategy, StrategySpec] = {
    SandboxStrategy.DRY_RUN: StrategySpec(
        strategy=SandboxStrategy.DRY_RUN,
        real_execution=False,
        requires_network=False,
        description="Simulate execution without invoking a shell",
    ),
    SandboxStrategy.LOCAL_RESTRICTED: StrategySpec(
        strategy=SandboxStrategy.LOCAL_RESTRICTED,
        real_execution=True,
        requires_network=False,
        description="Execute in workspace with deny-by-default network (not available in v0)",
    ),
}


def strategy_requires_network(strategy: SandboxStrategy) -> bool:
    return STRATEGY_MATRIX[strategy].requires_network


def select_strategy(
    request: ExecutionRequest,
    *,
    normalize_root: str,
) -> ExecutionProposal:
    """Choose strategy and assemble a proposal from a normalized request."""
    ctx: ExecutionContext = request.context
    requested = ctx.requested_strategy

    if requested == SandboxStrategy.LOCAL_RESTRICTED:
        if SandboxStrategy.LOCAL_RESTRICTED not in AVAILABLE_STRATEGIES_V0:
            selected = SandboxStrategy.DRY_RUN
            rationale = (
                "Requested local_restricted is not available in v0; "
                "downgraded to dry_run with explicit rationale"
            )
        else:
            selected = SandboxStrategy.LOCAL_RESTRICTED
            rationale = "Caller requested local_restricted and it is available"
    elif requested == SandboxStrategy.DRY_RUN:
        selected = SandboxStrategy.DRY_RUN
        rationale = "Caller requested dry_run"
    elif requested is None:
        selected = SandboxStrategy.DRY_RUN
        rationale = "No strategy requested; defaulting to dry_run"
    else:
        selected = SandboxStrategy.DRY_RUN
        rationale = f"Unknown strategy preference; defaulting to dry_run"

    fs = FilesystemConstraints(workspace_root=normalize_root)
    network = NetworkPolicyProfile(mode=NetworkMode.DENY_ALL)

    return ExecutionProposal(
        request=request,
        selected_strategy=selected,
        strategy_rationale=rationale,
        fs_constraints=fs,
        network_policy=network,
    )
