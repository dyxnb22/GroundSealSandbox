"""RunRecord migration entry points."""

from __future__ import annotations

from typing import Any

from groundseal.contracts.models import RunRecord
from groundseal.lifecycle.migrations.v0_to_v1 import migrate_v0_to_v1

_SUPPORTED_VERSIONS = {"1"}
_MIGRATORS: dict[tuple[str, str], Any] = {
    ("0", "1"): migrate_v0_to_v1,
}


class MigrationError(ValueError):
    """Raised when a stored record cannot be migrated."""


def _detect_version(data: dict[str, Any]) -> str:
    return str(data.get("schema_version", "0"))


def migrate_record(data: dict[str, Any], *, target_version: str = "1") -> RunRecord:
    """Migrate a raw record dict to the target schema version."""
    version = _detect_version(data)
    if version == target_version:
        return RunRecord.model_validate(data)

    if version == "0" and target_version == "1":
        migrated = migrate_v0_to_v1(data)
        return RunRecord.model_validate(migrated)

    raise MigrationError(
        f"unsupported migration path: schema_version {version} -> {target_version}"
    )


def migrate_store_payload(raw: dict[str, Any], *, target_version: str = "1") -> dict[str, Any]:
    """Migrate an entire store file payload keyed by run_id."""
    migrated: dict[str, Any] = {}
    for run_id, record_data in raw.items():
        if not isinstance(record_data, dict):
            raise MigrationError(f"invalid record payload for run_id {run_id}")
        record = migrate_record(record_data, target_version=target_version)
        migrated[run_id] = record.model_dump(mode="json")
    return migrated
