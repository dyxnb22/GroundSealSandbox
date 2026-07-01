"""Human-readable review artifacts from subsystem outputs."""

from __future__ import annotations

from groundseal.adapter.models import IntegrationResponse
from groundseal.contracts.models import RunRecord, ReviewerSummary


def build_reviewer_summary_from_response(response: IntegrationResponse) -> ReviewerSummary:
    command = ""
    strategy = "unknown"
    rationale = ""
    preflight_status = "unknown"
    execution_status = "unknown"
    failure_class = response.failure_class.value if response.failure_class else None
    blocking: list[str] = []
    stdout = None
    stderr = None
    run_id = None

    if response.proposal:
        command = response.proposal.request.command
        strategy = response.proposal.selected_strategy.value
        rationale = response.proposal.strategy_rationale
    if response.preflight:
        preflight_status = response.preflight.overall_status.value
        blocking = list(response.preflight.blocking_reasons)
    if response.result:
        execution_status = response.result.status.value
        if response.result.failure_class and not failure_class:
            failure_class = response.result.failure_class.value
        stdout = response.result.evidence.stdout
        stderr = response.result.evidence.stderr
        run_id = response.result.evidence.run_id

    headline = _headline(response.ok, execution_status, failure_class)
    decision = "allow" if response.ok else "deny"

    return ReviewerSummary(
        headline=headline,
        decision=decision,
        command_preview=_truncate(command),
        strategy=strategy,
        strategy_rationale=rationale,
        preflight_status=preflight_status,
        execution_status=execution_status,
        failure_class=failure_class,
        blocking_reasons=blocking,
        stdout_preview=_truncate(stdout or ""),
        stderr_preview=_truncate(stderr or ""),
        run_id=run_id,
    )


def build_reviewer_summary_from_record(record: RunRecord) -> ReviewerSummary:
    ok = record.result.status.value in ("simulated", "completed")
    failure = record.result.failure_class.value if record.result.failure_class else None
    return ReviewerSummary(
        headline=_headline(ok, record.result.status.value, failure),
        decision="allow" if ok else "deny",
        command_preview=_truncate(record.proposal.request.command),
        strategy=record.proposal.selected_strategy.value,
        strategy_rationale=record.proposal.strategy_rationale,
        preflight_status=record.preflight.overall_status.value,
        execution_status=record.result.status.value,
        failure_class=failure,
        blocking_reasons=list(record.preflight.blocking_reasons),
        stdout_preview=_truncate(record.result.evidence.stdout or ""),
        stderr_preview=_truncate(record.result.evidence.stderr or ""),
        run_id=record.run_id,
    )


def build_reviewer_summary(source: IntegrationResponse | RunRecord) -> ReviewerSummary:
    if isinstance(source, RunRecord):
        return build_reviewer_summary_from_record(source)
    return build_reviewer_summary_from_response(source)


def format_reviewer_markdown(summary: ReviewerSummary) -> str:
    lines = [
        f"# {summary.headline}",
        "",
        f"- **Decision:** {summary.decision}",
        f"- **Strategy:** {summary.strategy}",
        f"- **Preflight:** {summary.preflight_status}",
        f"- **Execution:** {summary.execution_status}",
    ]
    if summary.failure_class:
        lines.append(f"- **Failure class:** {summary.failure_class}")
    if summary.run_id:
        lines.append(f"- **Run ID:** {summary.run_id}")
    lines.extend(
        [
            "",
            "## Rationale",
            summary.strategy_rationale,
            "",
            "## Command",
            f"```\n{summary.command_preview}\n```",
        ]
    )
    if summary.blocking_reasons:
        lines.extend(["", "## Blocking reasons", *[f"- {r}" for r in summary.blocking_reasons]])
    if summary.stdout_preview:
        lines.extend(["", "## stdout (preview)", f"```\n{summary.stdout_preview}\n```"])
    if summary.stderr_preview:
        lines.extend(["", "## stderr (preview)", f"```\n{summary.stderr_preview}\n```"])
    return "\n".join(lines) + "\n"


def _headline(ok: bool, execution_status: str, failure_class: str | None) -> str:
    if ok:
        return f"Execution {execution_status}"
    if failure_class:
        return f"Execution denied ({failure_class})"
    return "Execution denied"


def _truncate(text: str, limit: int = 200) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
