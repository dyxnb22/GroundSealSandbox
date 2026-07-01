"""Reviewer summary tests."""

from groundseal.adapter import execute_workflow
from groundseal.config import reset_config, set_local_restricted_enabled
from groundseal.review import build_reviewer_summary, format_reviewer_markdown


def teardown_function():
    reset_config()


def test_reviewer_summary_from_happy_path_adapter():
    resp = execute_workflow(
        {
            "command": "echo hello",
            "context": {"workspace_root": "/tmp/workspace"},
        }
    )
    summary = build_reviewer_summary(resp)
    assert summary.decision == "allow"
    assert summary.strategy == "dry_run"
    assert summary.command_preview == "echo hello"
    md = format_reviewer_markdown(summary)
    assert "# Execution simulated" in md
    assert "dry_run" in md


def test_reviewer_summary_from_denied_path():
    resp = execute_workflow({"command": "rm -rf /", "context": {"workspace_root": "/tmp/ws"}})
    summary = build_reviewer_summary(resp)
    assert summary.decision == "deny"
    assert summary.failure_class == "preflight_failed"
    assert summary.blocking_reasons


def test_reviewer_summary_includes_stdout_when_enabled(tmp_path):
    set_local_restricted_enabled(True)
    resp = execute_workflow(
        {
            "command": "echo reviewer_out",
            "context": {
                "workspace_root": str(tmp_path),
                "requested_strategy": "local_restricted",
            },
        }
    )
    summary = build_reviewer_summary(resp)
    assert summary.decision == "allow"
    assert "reviewer_out" in summary.stdout_preview
