"""Runtime configuration for GroundSealSandbox."""

from __future__ import annotations

import os

from groundseal.contracts.models import PolicyProfile

_ENABLE_LOCAL_RESTRICTED = False
_ACTIVE_POLICY_PROFILE: PolicyProfile | None = None


def is_local_restricted_enabled() -> bool:
    """Return True when real subprocess execution is explicitly opted in."""
    if _ENABLE_LOCAL_RESTRICTED:
        return True
    return os.environ.get("GROUNDSEAL_ENABLE_LOCAL_RESTRICTED", "").lower() in (
        "1",
        "true",
        "yes",
    )


def set_local_restricted_enabled(enabled: bool) -> None:
    """Set opt-in flag in-process (used by tests)."""
    global _ENABLE_LOCAL_RESTRICTED
    _ENABLE_LOCAL_RESTRICTED = enabled


def get_policy_profile() -> PolicyProfile:
    """Return the active policy profile (loads default on first access)."""
    global _ACTIVE_POLICY_PROFILE
    if _ACTIVE_POLICY_PROFILE is None:
        from groundseal.policy.profile import load_default_policy_profile

        _ACTIVE_POLICY_PROFILE = load_default_policy_profile()
    return _ACTIVE_POLICY_PROFILE


def set_policy_profile(profile: PolicyProfile) -> None:
    """Override the active policy profile in-process (used by tests/deploy)."""
    global _ACTIVE_POLICY_PROFILE
    _ACTIVE_POLICY_PROFILE = profile


def reset_config() -> None:
    """Reset in-process overrides."""
    global _ACTIVE_POLICY_PROFILE
    set_local_restricted_enabled(False)
    _ACTIVE_POLICY_PROFILE = None
