"""In-memory and file-backed run record storage."""

from __future__ import annotations

import json
from pathlib import Path

from groundseal.contracts.models import RunRecord
from groundseal.lifecycle.migrations import migrate_store_payload


class RunStoreError(ValueError):
    """Raised when store operations violate tenant or schema constraints."""


class RunStore:
    """Simple run record store with optional JSON persistence and tenant scoping."""

    def __init__(self, path: Path | None = None) -> None:
        self._records: dict[tuple[str, str], RunRecord] = {}
        self._path = path
        if path and path.exists():
            self._load(path)

    def save(self, record: RunRecord, tenant_id: str) -> None:
        if not tenant_id:
            raise RunStoreError("tenant_id required for RunStore.save")
        if record.tenant_id and record.tenant_id != tenant_id:
            raise RunStoreError("record tenant_id does not match save tenant_id")
        stored = record if record.tenant_id else record.model_copy(update={"tenant_id": tenant_id})
        self._records[(tenant_id, record.run_id)] = stored
        if self._path:
            self._persist()

    def get(self, run_id: str, tenant_id: str) -> RunRecord | None:
        if not tenant_id:
            raise RunStoreError("tenant_id required for RunStore.get")
        return self._records.get((tenant_id, run_id))

    def list_ids(self, tenant_id: str) -> list[str]:
        if not tenant_id:
            raise RunStoreError("tenant_id required for RunStore.list_ids")
        return sorted(
            run_id for (tid, run_id) in self._records if tid == tenant_id
        )

    def _persist(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, dict] = {}
        for (_tenant_id, run_id), rec in self._records.items():
            payload[run_id] = rec.model_dump(mode="json")
        self._path.write_text(json.dumps(payload, indent=2) + "\n")

    def _load(self, path: Path) -> None:
        raw = json.loads(path.read_text())
        if not isinstance(raw, dict):
            raise RunStoreError("invalid store file: expected object at top level")
        migrated = migrate_store_payload(raw)
        for run_id, data in migrated.items():
            record = RunRecord.model_validate(data)
            tenant_id = record.tenant_id or "default"
            self._records[(tenant_id, run_id)] = record
