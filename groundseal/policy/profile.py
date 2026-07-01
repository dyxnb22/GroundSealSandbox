"""Policy profile loading and denylist evaluation."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from groundseal.contracts.models import PolicyProfile

# Built-in mandatory patterns (v0 equivalent); cannot be removed by operators.
_BUILTIN_MANDATORY_PATTERNS: tuple[str, ...] = (
    r"rm\s+-rf\s+/",
    r":\(\)\s*\{",
)

_DEFAULT_POLICY_DIR = Path(__file__).resolve().parents[2] / "config" / "policies"


def _compile_patterns(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(pattern) for pattern in patterns]


def builtin_mandatory_patterns() -> list[str]:
    return list(_BUILTIN_MANDATORY_PATTERNS)


def default_policy_profile() -> PolicyProfile:
    """Return the built-in default profile matching v0 denylist behavior."""
    return PolicyProfile(
        schema_version="1",
        name="default",
        mandatory_denies=builtin_mandatory_patterns(),
        operator_denies=[],
    )


def merged_deny_patterns(profile: PolicyProfile) -> list[str]:
    """Mandatory patterns always win; operator patterns are additive."""
    seen: set[str] = set()
    merged: list[str] = []
    for pattern in [*profile.mandatory_denies, *profile.operator_denies]:
        if pattern not in seen:
            seen.add(pattern)
            merged.append(pattern)
    return merged


def command_matches_denylist(command: str, profile: PolicyProfile) -> bool:
    patterns = _compile_patterns(merged_deny_patterns(profile))
    return any(pattern.search(command) for pattern in patterns)


def load_policy_profile(path: Path | str) -> PolicyProfile:
    """Load a policy profile from YAML or JSON."""
    file_path = Path(path)
    raw_text = file_path.read_text()
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(raw_text)
    else:
        data = json.loads(raw_text)
    profile = PolicyProfile.model_validate(data)
    # Ensure built-in mandatory patterns are always present.
    mandatory = set(builtin_mandatory_patterns())
    mandatory.update(profile.mandatory_denies)
    return profile.model_copy(update={"mandatory_denies": sorted(mandatory)})


def load_default_policy_profile() -> PolicyProfile:
    default_path = _DEFAULT_POLICY_DIR / "default.yaml"
    if default_path.exists():
        return load_policy_profile(default_path)
    return default_policy_profile()
