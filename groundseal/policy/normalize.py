"""Path and command normalization utilities."""

from __future__ import annotations

import os
import re

_PATH_TRAVERSAL = re.compile(r"(^|[/\\])\.\.([/\\]|$)")

# Patterns that indicate high-risk commands (v0 denylist)
_DENYLIST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"rm\s+-rf\s+/"),
    re.compile(r":\(\)\s*\{"),  # fork bomb signature
]


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


def command_matches_denylist(command: str) -> bool:
    return any(pattern.search(command) for pattern in _DENYLIST_PATTERNS)
