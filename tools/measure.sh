#!/usr/bin/env bash
# Measure the things the knowledge base's records rest on, so every claim in
# knowledge-base/findings/ can be re-checked at any time instead of being
# remembered.
#
# Strictly read-only. Runs no state-changing omarchy command, sends no input,
# maps no window, captures no screen, never restarts or rescans the shell.
#
#   bash tools/measure.sh            human-readable table
#   bash tools/measure.sh --json     print the JSON instead
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/baseline"

exec python3 "$ROOT/tools/measure.py" \
  --omarchy-bin "${OMARCHY_BIN:-/usr/bin}" \
  --omarchy-path "${OMARCHY_PATH:-/usr/share/omarchy}" \
  --out "$ROOT/baseline/measurements.json" \
  ${1:+--json}