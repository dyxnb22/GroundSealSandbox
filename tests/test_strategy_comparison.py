"""Phase 8 controlled strategy comparison."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_compare_strategies_script_produces_expected_conclusion():
    output = ROOT / "reports" / "generated" / "test-strategy-comparison.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "compare_strategies.py"), "--output", str(output)],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(proc.stdout)
    assert len(report["observations"]) == 2
    strategies = {o["strategy"] for o in report["observations"]}
    assert strategies == {"dry_run", "local_restricted"}
    dry = next(o for o in report["observations"] if o["strategy"] == "dry_run")
    local = next(o for o in report["observations"] if o["strategy"] == "local_restricted")
    assert dry["status"] == "simulated"
    assert local["status"] == "completed"
    assert local["has_stdout"] is True
    assert "dry_run is faster" in report["conclusion"]
