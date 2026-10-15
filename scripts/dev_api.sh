#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f /workspace/state/khohoc.env ]]; then
  set -a
  source /workspace/state/khohoc.env
  set +a
fi
export KHOHOC_MANAGER_CREDENTIALS_FILE="${KHOHOC_MANAGER_CREDENTIALS_FILE:-/workspace/state/TAI-KHOAN-QUAN-LY.txt}"
export PYTHONPATH="$PWD/services/api"
exec /workspace/venvs/khohoc/bin/uvicorn khohoc.main:app --host 127.0.0.1 --port 8000
