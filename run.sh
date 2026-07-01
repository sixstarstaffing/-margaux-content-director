#!/usr/bin/env bash
# run.sh · dead-simple Margaux test runner. Just: bash run.sh
# Uses the ANTHROPIC_API_KEY already in your shell, or a .key file if present.
cd "$(cd "$(dirname "$0")" && pwd)" || exit 1

if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f .key ]; then
  export ANTHROPIC_API_KEY="$(tr -d '[:space:]' < .key)"
fi
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "No API key. Put it in a file once:  echo 'sk-ant-...' > .key   then rerun: bash run.sh"
  exit 2
fi

[ -f .venv/bin/activate ] && . .venv/bin/activate
echo "running Margaux on ./flat ..."
python deploy/sprint/test-run.py --folder flat --out routing-sheet.md 2>&1 | tee run.log
echo
echo "=== DONE. Everything above is also saved in run.log ==="
