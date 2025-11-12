#!/usr/bin/env bash

# Restart the Sheltr dev server on the given port (defaults to 5001).
# 1. Stops any process already bound to the port.
# 2. Activates the local virtual environment.
# 3. Starts `flask run` on that port.

set -euo pipefail

PORT="${1:-5001}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv/bin/activate"

if [[ ! -f "$VENV_PATH" ]]; then
  echo "Virtualenv not found at $VENV_PATH" >&2
  exit 1
fi

echo "Looking for processes on port $PORT..."
if PIDS=$(lsof -ti tcp:"$PORT" 2>/dev/null) && [[ -n "$PIDS" ]]; then
  echo "Stopping processes: $PIDS"
  while read -r PID; do
    kill "$PID" 2>/dev/null || true
  done <<< "$PIDS"
  sleep 1
else
  echo "Port $PORT is free."
fi

echo "Starting Sheltr on port $PORT..."
source "$VENV_PATH"
export FLASK_APP=sheltr
exec flask run --port "$PORT"
