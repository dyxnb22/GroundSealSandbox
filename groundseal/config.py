"""Runtime configuration for GroundSealSandbox."""

from __future__ import annotations

import os

_ENABLE_LOCAL_RESTRICTED = False


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


def reset_config() -> None:
    """Reset in-process overrides."""
    set_local_restricted_enabled(False)
