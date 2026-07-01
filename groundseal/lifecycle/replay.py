"""Replay stored runs and detect drift."""

from __future__ import annotations

from groundseal import plan_execution, preflight, run
from groundseal.contracts.models import ReplayComparison, RunRecord
from groundseal.lifecycle.store import RunStore


def replay_run(run_id: str, store: RunStore, *, tenant_id: str) -> ReplayComparison:
    record = store.get(run_id, tenant_id)
    if record is None:
        return ReplayComparison(
            run_id=run_id,
            original_status="missing",
            replay_status="missing",
            original_exit_code=None,
            replay_exit_code=None,
            status_match=False,
            exit_code_match=False,
            drift_detected=True,
            notes="run_id not found in store for tenant",
        )

    ctx_tenant = record.proposal.request.context.tenant_id
    if ctx_tenant and ctx_tenant != tenant_id:
        return ReplayComparison(
            run_id=run_id,
            original_status=record.result.status.value,
            replay_status="denied",
            original_exit_code=record.result.exit_code,
            replay_exit_code=None,
            status_match=False,
            exit_code_match=False,
            drift_detected=True,
            notes="tenant mismatch on replay",
        )

    req = record.proposal.request
    proposal = plan_execution(req.command, req.context)
    report = preflight(proposal)
    if report.overall_status.value == "fail":
        replay = run(proposal)
    else:
        replay = run(proposal, run_id=f"{run_id}-replay")

    orig_status = record.result.status.value
    replay_status = replay.status.value
    status_match = orig_status == replay_status
    exit_match = record.result.exit_code == replay.exit_code
    drift = not (status_match and exit_match)

    notes = ""
    if proposal.selected_strategy != record.proposal.selected_strategy:
        notes = "strategy selection differed on replay"

    return ReplayComparison(
        run_id=run_id,
        original_status=orig_status,
        replay_status=replay_status,
        original_exit_code=record.result.exit_code,
        replay_exit_code=replay.exit_code,
        status_match=status_match,
        exit_code_match=exit_match,
        drift_detected=drift,
        notes=notes,
    )
