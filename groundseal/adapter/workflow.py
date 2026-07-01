"""Orchestrates plan_execution -> preflight -> run for parent callers."""

from __future__ import annotations

from pydantic import ValidationError

from groundseal import describe_capabilities, plan_execution, preflight, run
from groundseal.adapter.models import IntegrationRequest, IntegrationResponse
from groundseal.contracts.models import (
    ExecutionContext,
    ExecutionStatus,
    FailureClass,
    PreflightStatus,
)
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
    return summary


def execute_workflow(raw: dict) -> IntegrationResponse:
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
    resp.evidence_summary = _evidence_summary(resp)
    return resp
