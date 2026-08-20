#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PNPM_VERSION=11.3.0
if command -v pnpm >/dev/null 2>&1; then
  PNPM=(pnpm)
else
  PNPM=(npx --yes "pnpm@${PNPM_VERSION}")
fi

(
  cd backend
  uv run --locked --no-sync uvicorn app.main:create_app --factory --reload --port 8000
) &
(
  cd frontend
  "${PNPM[@]}" dev
) &

trap 'kill 0' EXIT INT TERM
wait
