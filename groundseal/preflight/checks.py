"""Preflight check implementations."""

from __future__ import annotations

from groundseal.contracts.models import (
    ExecutionProposal,
    NetworkMode,
    PreflightCheck,
    PreflightReport,
    PreflightStatus,
    SandboxStrategy,
)
from groundseal.policy.normalize import command_matches_denylist
from groundseal.policy.strategy_matrix import (
    get_available_strategies,
    strategy_requires_network,
)


def _check_schema_valid(proposal: ExecutionProposal) -> PreflightCheck:
    try:
        ExecutionProposal.model_validate(proposal.model_dump())
        return PreflightCheck(name="schema_valid", status=PreflightStatus.PASS)
    except Exception as exc:  # noqa: BLE001 — surface as preflight fail
        return PreflightCheck(
            name="schema_valid",
            status=PreflightStatus.FAIL,
            reason=str(exc),
        )


def _check_policy_denied(proposal: ExecutionProposal) -> PreflightCheck:
    if command_matches_denylist(proposal.request.command):
        return PreflightCheck(
            name="policy_denied",
            status=PreflightStatus.FAIL,
            reason="command matches denylist pattern",
        )
    return PreflightCheck(name="policy_denied", status=PreflightStatus.PASS)


def _check_strategy_mismatch(proposal: ExecutionProposal) -> PreflightCheck:
    requested = proposal.request.context.requested_strategy
    available = get_available_strategies()
    if requested == SandboxStrategy.LOCAL_RESTRICTED:
        if SandboxStrategy.LOCAL_RESTRICTED not in available:
            if proposal.selected_strategy != SandboxStrategy.DRY_RUN:
                return PreflightCheck(
                    name="strategy_mismatch",
                    status=PreflightStatus.FAIL,
                    reason="local_restricted unavailable and not downgraded to dry_run",
                )
    if proposal.selected_strategy not in available:
        return PreflightCheck(
            name="strategy_mismatch",
            status=PreflightStatus.FAIL,
            reason=f"strategy {proposal.selected_strategy.value} is not available",
        )
    return PreflightCheck(name="strategy_mismatch", status=PreflightStatus.PASS)


def _check_network_policy_consistency(proposal: ExecutionProposal) -> PreflightCheck:
    if proposal.network_policy.mode == NetworkMode.DENY_ALL:
        if strategy_requires_network(proposal.selected_strategy):
            return PreflightCheck(
                name="network_policy_consistency",
                status=PreflightStatus.FAIL,
                reason="strategy requires network but policy is deny_all",
            )
    return PreflightCheck(name="network_policy_consistency", status=PreflightStatus.PASS)


CHECK_ORDER = [
    _check_schema_valid,
    _check_policy_denied,
    _check_strategy_mismatch,
    _check_network_policy_consistency,
]


def run_preflight(proposal: ExecutionProposal) -> PreflightReport:
    checks = [fn(proposal) for fn in CHECK_ORDER]
    blocking = [
        c.reason or c.name
        for c in checks
        if c.status == PreflightStatus.FAIL
    ]
    if blocking:
        return PreflightReport(
            checks=checks,
            overall_status=PreflightStatus.FAIL,
            blocking_reasons=blocking,
        )
    warnings = [c for c in checks if c.status == PreflightStatus.WARN]
    overall = PreflightStatus.WARN if warnings else PreflightStatus.PASS
    return PreflightReport(
        checks=checks,
        overall_status=overall,
        blocking_reasons=[],
    )
