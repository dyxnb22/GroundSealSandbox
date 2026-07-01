#!/usr/bin/env bash
# Manual network isolation spike — not run in CI (may require privileges).
set -euo pipefail

echo "=== GroundSealSandbox network isolation spike ==="
echo "Purpose: verify unshare --net blocks outbound curl"

if ! command -v unshare >/dev/null 2>&1; then
  echo "SKIP: unshare not available"
  exit 0
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "SKIP: curl not available"
  exit 0
fi

echo "--- Baseline: curl without isolation (expect success or DNS failure) ---"
if curl -s --max-time 3 https://example.com >/dev/null 2>&1; then
  echo "Baseline: network reachable"
else
  echo "Baseline: network unreachable or blocked (note for experiment)"
fi

echo "--- Isolated: unshare --net curl (expect failure) ---"
if unshare --net bash -c 'curl -s --max-time 3 https://example.com' >/dev/null 2>&1; then
  echo "FAIL: curl succeeded inside network namespace (isolation ineffective)"
  exit 1
else
  echo "PASS: curl failed inside network namespace as expected"
fi

echo "Conclusion: unshare --net provides basic egress isolation on this host"
