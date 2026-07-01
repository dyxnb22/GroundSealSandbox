"""Evaluation baseline and ratchet tests."""

import json

from groundseal.evaluation.runner import check_against_baseline, run_evaluation


def test_evaluation_all_manifest_fixtures_pass():
    report = run_evaluation()
    assert report.total_fixtures == 6
    assert report.passed_fixtures == report.total_fixtures
    assert report.contract_pass_rate == 1.0
    assert report.negative_path_correctness == 1.0


def test_evaluation_no_regression_vs_baseline():
    report = run_evaluation()
    regressions = check_against_baseline(report)
    assert regressions == [], f"regressions: {regressions}"


def test_baseline_fixture_keys_match_manifest():
    from pathlib import Path

    baseline = json.loads(
        (Path(__file__).parent / "baselines" / "evaluation_v0.json").read_text()
    )
    manifest = json.loads((Path(__file__).parent / "fixtures" / "manifest.json").read_text())
    assert set(baseline["fixture_results"].keys()) == set(manifest.keys())
