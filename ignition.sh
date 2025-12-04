#!/usr/bin/env bash

# Ignition - Launch the Sheltr dev server on the given port (defaults to 5001).
# On first run, this script will:
# 1. Create a Python virtual environment
# 2. Install all required dependencies
# 3. Initialize the database
# On every run, it will:
# 4. Stop any process already bound to the port
# 5. Activate the virtual environment
# 6. Start Flask on the specified port

set -euo pipefail

PORT="${1:-5001}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
VENV_ACTIVATE="$VENV_PATH/bin/activate"
DB_INITIALIZED_FLAG="$PROJECT_ROOT/.db_initialized"

# Step 1: Create virtual environment if it doesn't exist
if [[ ! -d "$VENV_PATH" ]]; then
  echo "Virtual environment not found. Creating one..."
  python3 -m venv "$VENV_PATH"
  echo "Virtual environment created at $VENV_PATH"
fi

# Step 2: Activate virtual environment
source "$VENV_ACTIVATE"

# Step 3: Install/upgrade dependencies
echo "Checking dependencies..."
pip install --quiet --upgrade pip
pip install --quiet flask bootstrap-flask PyJWT werkzeug

# Step 4: Initialize database if not already done
if [[ ! -f "$DB_INITIALIZED_FLAG" ]]; then
  echo "Initializing database..."
  export FLASK_APP=sheltr
  flask init-db
  touch "$DB_INITIALIZED_FLAG"
  echo "Database initialized."
fi

# Step 5: Stop any process on the target port
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

# Step 6: Start Flask server
echo "Starting Sheltr on port $PORT..."
export FLASK_APP=sheltr
exec flask run --port "$PORT" --debug
