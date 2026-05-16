#!/usr/bin/env bash
# Software MRI — start the Vite dev server.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"
exec npm run dev
