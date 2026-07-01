"""Integration boundary types (platform-neutral JSON-friendly)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from groundseal.contracts.models import (
    CapabilityProfile,
    ExecutionProposal,
    ExecutionResult,
    FailureClass,
    PreflightReport,
)


class IntegrationRequest(BaseModel):
    """Parent-to-subsystem request envelope."""

    command: str
    context: dict[str, Any]
    caller_id: str | None = None


class IntegrationResponse(BaseModel):
    """Subsystem-to-parent response envelope."""

    ok: bool
    failure_class: FailureClass | None = None
    error: str | None = None
    proposal: ExecutionProposal | None = None
    preflight: PreflightReport | None = None
    result: ExecutionResult | None = None
    capabilities: CapabilityProfile | None = None
    evidence_summary: dict[str, Any] = Field(default_factory=dict)
