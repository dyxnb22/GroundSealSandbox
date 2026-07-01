"""Static sandbox strategy matrix."""

from __future__ import annotations

from dataclasses import dataclass

from groundseal.config import get_policy_profile, is_local_restricted_enabled
from groundseal.contracts.models import (
    EnforcementBackend,
    ExecutionContext,
    ExecutionProposal,
    ExecutionRequest,
    FilesystemConstraints,
    NetworkMode,
    NetworkPolicyProfile,
    PolicyProfile,
    SandboxStrategy,
)


@dataclass(frozen=True)
class StrategySpec:
    strategy: SandboxStrategy
    real_execution: bool
    requires_network: bool
    enforcement_backend: EnforcementBackend
    trust_tier: int
    description: str


STRATEGY_MATRIX: dict[SandboxStrategy, StrategySpec] = {
    SandboxStrategy.DRY_RUN: StrategySpec(
        strategy=SandboxStrategy.DRY_RUN,
        real_execution=False,
        requires_network=False,
        enforcement_backend=EnforcementBackend.NONE,
        trust_tier=0,
        description="Simulate execution without invoking a shell",
    ),
    SandboxStrategy.LOCAL_RESTRICTED: StrategySpec(
        strategy=SandboxStrategy.LOCAL_RESTRICTED,
        real_execution=True,
        requires_network=False,
        enforcement_backend=EnforcementBackend.PROCESS_ONLY,
        trust_tier=1,
        description="Execute in workspace with deny-by-default network",
    ),
}


def get_available_strategies() -> frozenset[SandboxStrategy]:
    strategies: set[SandboxStrategy] = {SandboxStrategy.DRY_RUN}
    if is_local_restricted_enabled():
        strategies.add(SandboxStrategy.LOCAL_RESTRICTED)
    return frozenset(strategies)


# Backward-compatible alias for imports
AVAILABLE_STRATEGIES_V0 = get_available_strategies()


def strategy_requires_network(strategy: SandboxStrategy) -> bool:
    return STRATEGY_MATRIX[strategy].requires_network


def get_strategy_spec(strategy: SandboxStrategy) -> StrategySpec:
    return STRATEGY_MATRIX[strategy]


def select_strategy(
    request: ExecutionRequest,
    *,
    normalize_root: str,
    policy_profile: PolicyProfile | None = None,
) -> ExecutionProposal:
    """Choose strategy and assemble a proposal from a normalized request."""
    profile = policy_profile or get_policy_profile()
    ctx: ExecutionContext = request.context
    requested = ctx.requested_strategy
    available = get_available_strategies()

    if requested == SandboxStrategy.LOCAL_RESTRICTED:
        if SandboxStrategy.LOCAL_RESTRICTED in available:
            selected = SandboxStrategy.LOCAL_RESTRICTED
            spec = STRATEGY_MATRIX[selected]
            rationale = (
                "Caller requested local_restricted and it is available; "
                f"enforcement_backend={spec.enforcement_backend.value}, "
                f"trust_tier={spec.trust_tier}"
            )
        else:
            selected = SandboxStrategy.DRY_RUN
            rationale = (
                "Requested local_restricted is not enabled; "
                "downgraded to dry_run with explicit rationale"
            )
    elif requested == SandboxStrategy.DRY_RUN:
        selected = SandboxStrategy.DRY_RUN
        rationale = "Caller requested dry_run"
    elif requested is None:
        selected = SandboxStrategy.DRY_RUN
        rationale = "No strategy requested; defaulting to dry_run"
    else:
        selected = SandboxStrategy.DRY_RUN
        rationale = "Unknown strategy preference; defaulting to dry_run"

    fs = FilesystemConstraints(workspace_root=normalize_root)
    network = NetworkPolicyProfile(mode=profile.default_network_mode)

    return ExecutionProposal(
        request=request,
        selected_strategy=selected,
        strategy_rationale=rationale,
        fs_constraints=fs,
        network_policy=network,
    )
