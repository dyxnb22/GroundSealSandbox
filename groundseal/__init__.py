"""GroundSealSandbox — controlled command-execution boundary."""

from groundseal.api import (
    describe_capabilities,
    get_policy_profile,
    plan_execution,
    preflight,
    run,
    set_policy_profile,
)
from groundseal.contracts.models import PolicyProfile

__all__ = [
    "describe_capabilities",
    "get_policy_profile",
    "plan_execution",
    "preflight",
    "run",
    "set_policy_profile",
    "PolicyProfile",
]

__version__ = "0.2.0"
