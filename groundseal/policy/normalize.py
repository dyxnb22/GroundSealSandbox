"""Path and command normalization utilities."""

from __future__ import annotations

import os
import re

from groundseal.contracts.models import PolicyProfile
from groundseal.policy.profile import command_matches_denylist as _command_matches_denylist

_PATH_TRAVERSAL = re.compile(r"(^|[/\\])\.\.([/\\]|$)")


class NormalizationError(ValueError):
    """Raised when untrusted input cannot be safely normalized."""


def normalize_workspace_root(raw: str) -> str:
    """Resolve workspace_root to absolute path; reject traversal."""
    if _PATH_TRAVERSAL.search(raw):
        raise NormalizationError("path traversal detected in workspace_root")
    resolved = os.path.abspath(os.path.expanduser(raw.strip()))
    if _PATH_TRAVERSAL.search(resolved):
        raise NormalizationError("path traversal detected in workspace_root")
    return resolved


def command_matches_denylist(command: str, profile: PolicyProfile) -> bool:
    return _command_matches_denylist(command, profile)
