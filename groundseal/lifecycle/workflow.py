"""Record execution with durable run_id."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from groundseal import run
from groundseal.contracts.models import ExecutionProposal, PreflightReport, RunRecord
from groundseal.lifecycle.store import RunStore, RunStoreError


def run_and_record(
    proposal: ExecutionProposal,
    preflight_report: PreflightReport,
    store: RunStore,
    *,
    tenant_id: str,
) -> RunRecord:
    if not tenant_id:
        raise RunStoreError("tenant_id required for run_and_record")
    run_id = str(uuid.uuid4())
    result = run(proposal, run_id=run_id)
    record = RunRecord(
        schema_version="1",
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        tenant_id=tenant_id,
        proposal=proposal,
        preflight=preflight_report,
        result=result,
    )
    store.save(record, tenant_id)
    return record
