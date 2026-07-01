"""In-memory and file-backed run record storage."""

from __future__ import annotations

import json
from pathlib import Path

from groundseal.contracts.models import RunRecord


class RunStore:
    """Simple run record store with optional JSON persistence."""

    def __init__(self, path: Path | None = None) -> None:
        self._records: dict[str, RunRecord] = {}
        self._path = path
        if path and path.exists():
            self._load(path)

    def save(self, record: RunRecord) -> None:
        self._records[record.run_id] = record
        if self._path:
            self._persist()

    def get(self, run_id: str) -> RunRecord | None:
        return self._records.get(run_id)

    def list_ids(self) -> list[str]:
        return sorted(self._records.keys())

    def _persist(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {rid: rec.model_dump(mode="json") for rid, rec in self._records.items()}
        self._path.write_text(json.dumps(payload, indent=2) + "\n")

    def _load(self, path: Path) -> None:
        raw = json.loads(path.read_text())
        for run_id, data in raw.items():
            self._records[run_id] = RunRecord.model_validate(data)
