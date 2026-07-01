"""Policy and strategy selection."""

from groundseal.policy.strategy_matrix import (
    STRATEGY_MATRIX,
    select_strategy,
    strategy_requires_network,
)

__all__ = [
    "STRATEGY_MATRIX",
    "select_strategy",
    "strategy_requires_network",
]
