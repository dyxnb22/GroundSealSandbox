"""Lifecycle record, store, and replay tests."""

from groundseal import plan_execution, preflight
from groundseal.config import reset_config, set_local_restricted_enabled
from groundseal.contracts.models import ExecutionContext, SandboxStrategy
from groundseal.lifecycle import RunStore, replay_run, run_and_record

TENANT = "test-tenant"


def teardown_function():
    reset_config()


def test_run_and_record_dry_run(tmp_path):
    store = RunStore()
    ctx = ExecutionContext(
        workspace_root=str(tmp_path),
        tenant_id=TENANT,
        requested_strategy=SandboxStrategy.DRY_RUN,
    )
    proposal = plan_execution("echo stored", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=TENANT)

    assert record.run_id
    assert record.result.status.value == "simulated"
    assert store.get(record.run_id, TENANT) is not None


def test_replay_detects_no_drift_for_dry_run(tmp_path):
    store = RunStore()
    ctx = ExecutionContext(workspace_root=str(tmp_path), tenant_id=TENANT)
    proposal = plan_execution("echo replay", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=TENANT)

    comparison = replay_run(record.run_id, store, tenant_id=TENANT)
    assert comparison.drift_detected is False
    assert comparison.status_match is True


def test_replay_local_restricted_when_enabled(tmp_path):
    set_local_restricted_enabled(True)
    store = RunStore(path=tmp_path / "runs.json")
    ctx = ExecutionContext(
        workspace_root=str(tmp_path),
        tenant_id=TENANT,
        requested_strategy=SandboxStrategy.LOCAL_RESTRICTED,
    )
    proposal = plan_execution("echo lifecycle", ctx)
    report = preflight(proposal)
    record = run_and_record(proposal, report, store, tenant_id=TENANT)

    comparison = replay_run(record.run_id, store, tenant_id=TENANT)
    assert comparison.drift_detected is False
    assert comparison.original_status == "completed"
    assert (tmp_path / "runs.json").exists()
