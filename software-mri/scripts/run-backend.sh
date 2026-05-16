#!/usr/bin/env bash
# Software MRI — start the FastAPI backend.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source .venv/bin/activate

cd backend
exec uvicorn main:app --reload --host 127.0.0.1 --port 8000
