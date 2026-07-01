"""Tests for multi-tenant identity boundaries on RunStore and replay."""

import pytest

from groundseal import plan_execution, preflight
from groundseal.config import reset_config, set_local_restricted_enabled
from groundseal.contracts.models import ExecutionContext, SandboxStrategy
from groundseal.lifecycle import RunStore, replay_run, run_and_record
from groundseal.lifecycle.store import RunStoreError


def teardown_function():
    reset_config()


def test_same_tenant_replay_succeeds(tmp_path):
    store = RunStore()
    tenant = "tenant-a"
    ctx = ExecutionContext(
        workspace_root=str(tmp_path),
        tenant_id=tenant,
        requested_strategy=SandboxStrategy.DRY_RUN,
    )
    proposal = plan_execution("echo stored", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=tenant)

    comparison = replay_run(record.run_id, store, tenant_id=tenant)
    assert comparison.drift_detected is False


def test_cross_tenant_get_returns_none(tmp_path):
    store = RunStore()
    tenant_a = "tenant-a"
    ctx = ExecutionContext(workspace_root=str(tmp_path), tenant_id=tenant_a)
    proposal = plan_execution("echo isolated", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=tenant_a)

    assert store.get(record.run_id, "tenant-b") is None


def test_cross_tenant_replay_reports_missing(tmp_path):
    store = RunStore()
    tenant_a = "tenant-a"
    ctx = ExecutionContext(workspace_root=str(tmp_path), tenant_id=tenant_a)
    proposal = plan_execution("echo isolated", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=tenant_a)

    comparison = replay_run(record.run_id, store, tenant_id="tenant-b")
    assert comparison.drift_detected is True
    assert "not found" in comparison.notes


def test_save_without_tenant_id_fails(tmp_path):
    store = RunStore()
    tenant = "tenant-a"
    ctx = ExecutionContext(workspace_root=str(tmp_path), tenant_id=tenant)
    proposal = plan_execution("echo x", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=tenant)

    with pytest.raises(RunStoreError):
        store.save(record, "")


def test_adapter_persist_run_requires_tenant(tmp_path):
    from groundseal.adapter import execute_workflow

    store = RunStore()
    resp = execute_workflow(
        {
            "command": "echo persist",
            "context": {"workspace_root": str(tmp_path)},
            "persist_run": True,
        },
        store=store,
    )
    assert resp.ok is False
    assert resp.failure_class.value == "policy_denied"


def test_adapter_persist_run_with_tenant(tmp_path):
    from groundseal.adapter import execute_workflow

    store = RunStore()
    tenant = "tenant-a"
    resp = execute_workflow(
        {
            "command": "echo persist",
            "context": {"workspace_root": str(tmp_path), "tenant_id": tenant},
            "persist_run": True,
        },
        store=store,
    )
    assert resp.ok is True
    assert store.list_ids(tenant)
    assert resp.result is not None
    assert resp.result.evidence.run_id is not None
