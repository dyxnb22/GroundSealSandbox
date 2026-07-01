"""Record execution with durable run_id."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from groundseal import run
from groundseal.contracts.models import ExecutionProposal, PreflightReport, RunRecord
from groundseal.lifecycle.store import RunStore


def run_and_record(
    proposal: ExecutionProposal,
    preflight_report: PreflightReport,
    store: RunStore,
) -> RunRecord:
    run_id = str(uuid.uuid4())
    result = run(proposal, run_id=run_id)
    record = RunRecord(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        proposal=proposal,
        preflight=preflight_report,
        result=result,
    )
    store.save(record)
    return record
