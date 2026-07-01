"""Orchestrates plan_execution -> preflight -> run for parent callers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import ValidationError

from groundseal import describe_capabilities, plan_execution, preflight, run
from groundseal.adapter.models import IntegrationRequest, IntegrationResponse
from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionStatus,
    FailureClass,
    PreflightStatus,
    RunRecord,
)
from groundseal.lifecycle.store import RunStore
from groundseal.policy.normalize import NormalizationError


def _evidence_summary(response: IntegrationResponse) -> dict:
    summary: dict = {}
    if response.proposal:
        summary["strategy_rationale"] = response.proposal.strategy_rationale
        summary["selected_strategy"] = response.proposal.selected_strategy.value
    if response.preflight:
        summary["preflight_status"] = response.preflight.overall_status.value
        summary["blocking_reasons"] = response.preflight.blocking_reasons
    if response.result:
        summary["execution_status"] = response.result.status.value
        if response.result.failure_class:
            summary["failure_class"] = response.result.failure_class.value
        if response.result.evidence.enforcement_backend:
            summary["enforcement_backend"] = response.result.evidence.enforcement_backend.value
    return summary


def _persist_record(
    request: IntegrationRequest,
    context: ExecutionContext,
    proposal,
    report,
    result,
    store: RunStore,
) -> str | None:
    tenant_id = context.tenant_id
    if not tenant_id:
        return None
    run_id = result.evidence.run_id or str(uuid.uuid4())
    record = RunRecord(
        schema_version="1",
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        tenant_id=tenant_id,
        proposal=proposal,
        preflight=report,
        result=result,
    )
    store.save(record, tenant_id)
    return run_id


def execute_workflow(raw: dict, store: RunStore | None = None) -> IntegrationResponse:
    """Run the v0 integration handshake; parent cannot skip preflight."""
    caps = describe_capabilities()

    try:
        request = IntegrationRequest.model_validate(raw)
    except ValidationError as exc:
        return IntegrationResponse(
            ok=False,
            failure_class=FailureClass.SCHEMA_INVALID,
            error=str(exc),
            capabilities=caps,
        )

    try:
        context = ExecutionContext.model_validate(request.context)
    except ValidationError as exc:
        return IntegrationResponse(
            ok=False,
            failure_class=FailureClass.SCHEMA_INVALID,
            error=str(exc),
            capabilities=caps,
        )

    if request.persist_run:
        if not context.tenant_id:
            resp = IntegrationResponse(
                ok=False,
                failure_class=FailureClass.POLICY_DENIED,
                error="tenant_id required in context when persist_run is true",
                capabilities=caps,
            )
            resp.evidence_summary = _evidence_summary(resp)
            return resp
        if store is None:
            resp = IntegrationResponse(
                ok=False,
                failure_class=FailureClass.POLICY_DENIED,
                error="store required when persist_run is true",
                capabilities=caps,
            )
            resp.evidence_summary = _evidence_summary(resp)
            return resp

    try:
        proposal = plan_execution(request.command, context)
    except NormalizationError as exc:
        resp = IntegrationResponse(
            ok=False,
            failure_class=FailureClass.AMBIGUOUS_HIGH_RISK,
            error=str(exc),
            capabilities=caps,
        )
        resp.evidence_summary = _evidence_summary(resp)
        return resp

    report = preflight(proposal)

    if report.overall_status == PreflightStatus.FAIL:
        result = run(proposal)
        resp = IntegrationResponse(
            ok=False,
            failure_class=result.failure_class or FailureClass.PREFLIGHT_FAILED,
            proposal=proposal,
            preflight=report,
            result=result,
            capabilities=caps,
        )
        resp.evidence_summary = _evidence_summary(resp)
        return resp

    result = run(proposal)
    ok = result.status in (ExecutionStatus.SIMULATED, ExecutionStatus.COMPLETED)
    resp = IntegrationResponse(
        ok=ok,
        failure_class=result.failure_class,
        proposal=proposal,
        preflight=report,
        result=result,
        capabilities=caps,
    )
    if request.persist_run and store is not None:
        persisted_id = _persist_record(request, context, proposal, report, result, store)
        if persisted_id and resp.result:
            resp.result.evidence.run_id = persisted_id
    resp.evidence_summary = _evidence_summary(resp)
    return resp
