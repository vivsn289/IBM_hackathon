#!/usr/bin/env bash
# Software MRI — one-shot setup.
# Creates a Python venv, installs backend deps, installs frontend deps.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Software MRI setup starting in $ROOT"

# 1. Python venv
if [ ! -d ".venv" ]; then
  echo "==> Creating .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing backend Python dependencies"
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2. Frontend
echo "==> Installing frontend Node dependencies"
cd frontend
if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is required. Install Node.js 18+ first."
  exit 1
fi
npm install
cd ..

# 3. .env
if [ ! -f ".env" ]; then
  echo "==> Copying .env.example to .env (edit it before running)"
  cp .env.example .env
fi

echo
echo "==> Setup complete."
echo
echo "Next steps:"
echo "  1. Edit .env and set BOB_ENDPOINT (or BOB_CLI_PATH)"
echo "  2. Terminal 1:  bash scripts/run-backend.sh"
echo "  3. Terminal 2:  bash scripts/run-frontend.sh"
echo "  4. Open:        http://localhost:5173"
