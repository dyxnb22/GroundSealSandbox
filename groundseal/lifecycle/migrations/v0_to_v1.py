"""Migrate legacy RunRecord payloads without schema_version to v1."""

from __future__ import annotations

from typing import Any


def migrate_v0_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    """Add schema_version and preserve all existing fields."""
    if "schema_version" in data:
        return data
    migrated = dict(data)
    migrated["schema_version"] = "1"
    return migrated
