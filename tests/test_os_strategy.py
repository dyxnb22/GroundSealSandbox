"""Tests for OS enforcement backend selection and capabilities."""

from groundseal import describe_capabilities
from groundseal.config import reset_config, set_local_restricted_enabled
from groundseal.contracts.models import EnforcementBackend, SandboxStrategy
from groundseal.policy.capabilities import detect_os_capabilities, resolve_enforcement_backend
from groundseal.policy.strategy_matrix import STRATEGY_MATRIX, get_strategy_spec


def teardown_function():
    reset_config()


def test_strategy_spec_includes_trust_tier():
    dry = get_strategy_spec(SandboxStrategy.DRY_RUN)
    local = get_strategy_spec(SandboxStrategy.LOCAL_RESTRICTED)
    assert dry.trust_tier == 0
    assert local.trust_tier == 1
    assert dry.enforcement_backend == EnforcementBackend.NONE
    assert local.enforcement_backend == EnforcementBackend.PROCESS_ONLY


def test_resolve_enforcement_backend_dry_run():
    backend = resolve_enforcement_backend(SandboxStrategy.DRY_RUN)
    assert backend == EnforcementBackend.NONE


def test_resolve_enforcement_backend_local_restricted_when_enabled():
    set_local_restricted_enabled(True)
    backend = resolve_enforcement_backend(SandboxStrategy.LOCAL_RESTRICTED)
    assert backend == EnforcementBackend.PROCESS_ONLY


def test_describe_capabilities_includes_os_limits():
    caps = describe_capabilities()
    assert "available_enforcement_backends" in caps.limits
    assert "strategy_trust_tiers" in caps.limits
    assert caps.limits["strategy_trust_tiers"]["dry_run"] == 0


def test_detect_os_capabilities_structure():
    caps = detect_os_capabilities()
    assert "platform" in caps
    assert "landlock_available" in caps
    assert EnforcementBackend.NONE.value in caps["available_enforcement_backends"]


def test_strategy_matrix_covers_all_strategies():
    for strategy in SandboxStrategy:
        assert strategy in STRATEGY_MATRIX
