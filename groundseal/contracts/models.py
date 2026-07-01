"""Pydantic models aligned with docs/contracts.md."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class SandboxStrategy(str, Enum):
    DRY_RUN = "dry_run"
    LOCAL_RESTRICTED = "local_restricted"


class NetworkMode(str, Enum):
    DENY_ALL = "deny_all"
    ALLOW_LISTED = "allow_listed"


class PreflightStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class ExecutionStatus(str, Enum):
    SIMULATED = "simulated"
    COMPLETED = "completed"
    DENIED = "denied"
    FAILED = "failed"


class FailureClass(str, Enum):
    SCHEMA_INVALID = "schema_invalid"
    POLICY_DENIED = "policy_denied"
    STRATEGY_MISMATCH = "strategy_mismatch"
    AMBIGUOUS_HIGH_RISK = "ambiguous_high_risk"
    PREFLIGHT_FAILED = "preflight_failed"
    EXECUTION_ERROR = "execution_error"


class EnforcementBackend(str, Enum):
    NONE = "none"
    PROCESS_ONLY = "process_only"
    LANDLOCK = "landlock"
    NETWORK_NS = "network_ns"


class PolicyProfile(BaseModel):
    """Deployment-level policy configuration."""

    schema_version: str = "1"
    name: str = "default"
    mandatory_denies: list[str] = Field(default_factory=list)
    operator_denies: list[str] = Field(default_factory=list)
    default_network_mode: NetworkMode = NetworkMode.DENY_ALL


class ExecutionContext(BaseModel):
    workspace_root: str
    requested_strategy: SandboxStrategy | None = None
    tenant_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionRequest(BaseModel):
    command: str
    context: ExecutionContext
    caller_id: str | None = None

    @field_validator("command")
    @classmethod
    def command_not_empty_after_strip(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("command must not be empty")
        return stripped


class FilesystemConstraints(BaseModel):
    workspace_root: str
    allow_write_outside_root: bool = False


class NetworkPolicyProfile(BaseModel):
    mode: NetworkMode
    allowed_hosts: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def allow_listed_requires_hosts(self) -> NetworkPolicyProfile:
        if self.mode == NetworkMode.ALLOW_LISTED and not self.allowed_hosts:
            raise ValueError("allowed_hosts required when mode is allow_listed")
        return self


class ExecutionProposal(BaseModel):
    request: ExecutionRequest
    selected_strategy: SandboxStrategy
    strategy_rationale: str
    fs_constraints: FilesystemConstraints
    network_policy: NetworkPolicyProfile


class PreflightCheck(BaseModel):
    name: str
    status: PreflightStatus
    reason: str | None = None


class PreflightReport(BaseModel):
    checks: list[PreflightCheck]
    overall_status: PreflightStatus
    blocking_reasons: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def blocking_reasons_match_fail(self) -> PreflightReport:
        if self.overall_status == PreflightStatus.FAIL and not self.blocking_reasons:
            raise ValueError("blocking_reasons required when overall_status is fail")
        if self.overall_status != PreflightStatus.FAIL and self.blocking_reasons:
            raise ValueError("blocking_reasons must be empty unless overall_status is fail")
        return self


class ExecutionEvidence(BaseModel):
    strategy_rationale: str
    preflight_summary: str | None = None
    simulated_command: str | None = None
    checks_performed: list[str] = Field(default_factory=list)
    stdout: str | None = None
    stderr: str | None = None
    run_id: str | None = None
    enforcement_backend: EnforcementBackend | None = None


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    exit_code: int | None = None
    evidence: ExecutionEvidence
    failure_class: FailureClass | None = None

    @model_validator(mode="after")
    def failure_class_on_denied_or_failed(self) -> ExecutionResult:
        if self.status in (ExecutionStatus.DENIED, ExecutionStatus.FAILED):
            if self.failure_class is None:
                raise ValueError("failure_class required when status is denied or failed")
        return self


class CapabilityProfile(BaseModel):
    strategies: list[SandboxStrategy]
    supported_checks: list[str]
    limits: dict[str, Any] = Field(default_factory=dict)


class RunRecord(BaseModel):
    """Durable snapshot of one execution lifecycle."""

    schema_version: str = "1"
    run_id: str
    created_at: str
    tenant_id: str | None = None
    proposal: ExecutionProposal
    preflight: PreflightReport
    result: ExecutionResult


class ReplayComparison(BaseModel):
    """Outcome of replaying a stored run."""

    run_id: str
    original_status: str
    replay_status: str
    original_exit_code: int | None
    replay_exit_code: int | None
    status_match: bool
    exit_code_match: bool
    drift_detected: bool
    notes: str = ""


class ReviewerSummary(BaseModel):
    """Human-review-oriented view of an execution outcome."""

    headline: str
    decision: str
    command_preview: str
    strategy: str
    strategy_rationale: str
    preflight_status: str
    execution_status: str
    failure_class: str | None = None
    blocking_reasons: list[str] = Field(default_factory=list)
    stdout_preview: str = ""
    stderr_preview: str = ""
    run_id: str | None = None
