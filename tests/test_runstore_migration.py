"""Tests for RunStore schema migration."""

import json
from pathlib import Path

import pytest

from groundseal.contracts.models import RunRecord
from groundseal.lifecycle.migrations import migrate_record, migrate_store_payload
from groundseal.lifecycle.migrations.migrate import MigrationError
from groundseal.lifecycle.store import RunStore


def _sample_v0_record() -> dict:
    return {
        "run_id": "legacy-1",
        "created_at": "2026-01-01T00:00:00+00:00",
        "proposal": {
            "request": {
                "command": "echo legacy",
                "context": {"workspace_root": "/tmp/ws"},
            },
            "selected_strategy": "dry_run",
            "strategy_rationale": "test",
            "fs_constraints": {"workspace_root": "/tmp/ws"},
            "network_policy": {"mode": "deny_all", "allowed_hosts": []},
        },
        "preflight": {
            "checks": [],
            "overall_status": "pass",
            "blocking_reasons": [],
        },
        "result": {
            "status": "simulated",
            "evidence": {"strategy_rationale": "test"},
        },
    }


def test_migrate_v0_record_adds_schema_version():
    record = migrate_record(_sample_v0_record())
    assert record.schema_version == "1"
    assert record.run_id == "legacy-1"


def test_migrate_store_payload():
    payload = {"legacy-1": _sample_v0_record()}
    migrated = migrate_store_payload(payload)
    assert migrated["legacy-1"]["schema_version"] == "1"


def test_unknown_schema_version_fails_closed():
    data = _sample_v0_record()
    data["schema_version"] = "99"
    with pytest.raises(MigrationError):
        migrate_record(data)


def test_runstore_round_trip_with_schema_version(tmp_path):
    store = RunStore(path=tmp_path / "runs.json")
    record = migrate_record(_sample_v0_record())
    record = record.model_copy(update={"tenant_id": "tenant-a"})
    store.save(record, "tenant-a")
    reloaded = RunStore(path=tmp_path / "runs.json")
    loaded = reloaded.get("legacy-1", "tenant-a")
    assert loaded is not None
    assert loaded.schema_version == "1"


def test_runstore_loads_legacy_file_without_schema_version(tmp_path):
    legacy_path = tmp_path / "legacy.json"
    legacy_path.write_text(json.dumps({"legacy-1": _sample_v0_record()}, indent=2))
    store = RunStore(path=legacy_path)
    # legacy records without tenant_id map to default tenant on load
    record = store.get("legacy-1", "default")
    assert record is not None
    assert record.schema_version == "1"
