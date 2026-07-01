"""GroundSealSandbox — controlled command-execution boundary."""

from groundseal.api import (
    describe_capabilities,
    plan_execution,
    preflight,
    run,
)

__all__ = [
    "describe_capabilities",
    "plan_execution",
    "preflight",
    "run",
]

__version__ = "0.1.0"
