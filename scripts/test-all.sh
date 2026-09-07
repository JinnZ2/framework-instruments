#!/usr/bin/env bash
# Runs every suite with the standard library only. Each suite chdirs into a
# temporary directory before writing, so no runs.jsonl lands in the tree.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m compileall -q "$repo_root/instruments" "$repo_root/arena"

run_suite() {
  ( cd "$repo_root/$1" && shift && python3 -m unittest -q "$@" )
}

run_suite instruments test_runrecord test_status_paths
run_suite instruments/b1-runner-up-trace test_b1 test_b1_pipeline
run_suite instruments/b2-audit-isolation test_b2
run_suite instruments/b3-split-authorship test_b3
run_suite instruments/b4-dilemma-reconstruction test_b4 test_b4_runrecord
run_suite instruments/unfold test_unfold
run_suite arena test_arena

# Coverage as counted (script, status) pairs; the count is printed, never stored.
( cd "$(mktemp -d)" && python3 "$repo_root/instruments/coverage_pairs.py" "$repo_root/instruments" coverage.jsonl )

echo "All framework-instrument tests passed."
