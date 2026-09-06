#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m compileall -q "$repo_root/instruments"

(
  cd "$repo_root/instruments/b1-runner-up-trace"
  python3 -m unittest -v test_b1.py
)
(
  cd "$repo_root/instruments/b2-audit-isolation"
  python3 -m unittest -v test_b2.py
)
(
  cd "$repo_root/instruments/b3-split-authorship"
  python3 -m unittest -v test_b3.py
)
(
  cd "$repo_root/instruments/b4-dilemma-reconstruction"
  python3 -m unittest -v test_b4.py
)

echo "All framework-instrument tests passed."
