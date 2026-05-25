#!/usr/bin/env bash
# Smoke tests — minimal curl checks against a running API.
# Usage: TESTBENCH_API_URL=http://localhost:5000 ./tests/smoke/smoke.sh

set -euo pipefail

BASE="${TESTBENCH_API_URL:-http://localhost:5000}"
PASS=0
FAIL=0

check() {
  local desc="$1"; shift
  if "$@" &>/dev/null; then
    echo "  PASS  $desc"
    ((PASS++))
  else
    echo "  FAIL  $desc"
    ((FAIL++))
  fi
}

echo "Smoke tests → $BASE"
echo "-----------------------------------"

check "GET /health returns 200" \
  curl -sf "$BASE/health"

check "GET /health body contains ok" \
  bash -c "curl -sf '$BASE/health' | grep -q '\"ok\"'"

check "GET /runs/ returns 200" \
  curl -sf "$BASE/runs/"

check "GET /runs/ returns JSON array" \
  bash -c "curl -sf '$BASE/runs/' | grep -q '^\['"

check "POST /runs/ returns 201" \
  curl -sf -o /dev/null -w "%{http_code}" \
    -X POST "$BASE/runs/" \
    -H "Content-Type: application/json" \
    -d '{"run_name":"smoke","scenario_name":"hello-world","model_name":"test","provider":"test"}' \
  | grep -q "201"

echo "-----------------------------------"
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
