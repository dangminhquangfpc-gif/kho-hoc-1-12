#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec /workspace/venvs/khohoc/bin/uvicorn scripts.serve_demo:app --host 0.0.0.0 --port 8080 --no-access-log
