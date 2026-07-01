"""Runtime capability detection for OS enforcement backends."""

from __future__ import annotations

import os
import platform
import shutil
from typing import Any

from groundseal.config import is_local_restricted_enabled
from groundseal.contracts.models import EnforcementBackend, SandboxStrategy
from groundseal.policy.strategy_matrix import STRATEGY_MATRIX, get_available_strategies


def _landlock_available() -> bool:
    if platform.system() != "Linux":
        return False
    try:
        with open("/proc/sys/kernel/osrelease") as f:
            release = f.read().strip()
        major = int(release.split(".")[0])
        return major >= 5
    except (OSError, ValueError):
        return False


def _network_ns_available() -> bool:
    return shutil.which("unshare") is not None


def detect_os_capabilities() -> dict[str, Any]:
    """Probe host capabilities relevant to enforcement backend selection."""
    available_backends: list[str] = [EnforcementBackend.NONE.value]
    if is_local_restricted_enabled():
        available_backends.append(EnforcementBackend.PROCESS_ONLY.value)
    if _landlock_available():
        available_backends.append(EnforcementBackend.LANDLOCK.value)
    if _network_ns_available():
        available_backends.append(EnforcementBackend.NETWORK_NS.value)

    return {
        "platform": platform.system(),
        "is_root": os.geteuid() == 0 if hasattr(os, "geteuid") else False,
        "landlock_available": _landlock_available(),
        "network_ns_available": _network_ns_available(),
        "available_enforcement_backends": available_backends,
        "strategy_trust_tiers": {
            strategy.value: spec.trust_tier
            for strategy, spec in STRATEGY_MATRIX.items()
        },
        "available_strategies": [s.value for s in get_available_strategies()],
    }


def resolve_enforcement_backend(strategy: SandboxStrategy) -> EnforcementBackend:
    """Select the best available enforcement backend for a strategy."""
    spec = STRATEGY_MATRIX[strategy]
    preferred = spec.enforcement_backend

    caps = detect_os_capabilities()
    available = set(caps["available_enforcement_backends"])

    if preferred.value in available:
        return preferred

    if preferred == EnforcementBackend.PROCESS_ONLY and EnforcementBackend.NONE.value in available:
        return EnforcementBackend.NONE

    return EnforcementBackend.NONE
