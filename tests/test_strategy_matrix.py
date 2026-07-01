"""Strategy matrix tests."""

from groundseal.contracts.models import ExecutionContext, ExecutionRequest, SandboxStrategy
from groundseal.policy.strategy_matrix import STRATEGY_MATRIX, select_strategy, strategy_requires_network


def test_dry_run_does_not_require_network():
    assert strategy_requires_network(SandboxStrategy.DRY_RUN) is False


def test_strategy_matrix_covers_all_enum_values():
    for strategy in SandboxStrategy:
        assert strategy in STRATEGY_MATRIX


def test_select_strategy_defaults_to_dry_run():
    request = ExecutionRequest(
        command="echo hi",
        context=ExecutionContext(workspace_root="/tmp/ws"),
    )
    proposal = select_strategy(request, normalize_root="/tmp/ws")
    assert proposal.selected_strategy == SandboxStrategy.DRY_RUN
    assert "dry_run" in proposal.strategy_rationale


def test_select_strategy_downgrades_local_restricted():
    request = ExecutionRequest(
        command="echo hi",
        context=ExecutionContext(
            workspace_root="/tmp/ws",
            requested_strategy=SandboxStrategy.LOCAL_RESTRICTED,
        ),
    )
    proposal = select_strategy(request, normalize_root="/tmp/ws")
    assert proposal.selected_strategy == SandboxStrategy.DRY_RUN
    assert "downgraded" in proposal.strategy_rationale.lower()
