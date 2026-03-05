#!/usr/bin/env bash
set -euo pipefail

echo
echo "=== Email Agent First-Run Setup (macOS/Linux) ==="
echo

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python is not installed."
  echo "Install Python 3.11+ from: https://www.python.org/downloads/macos/"
  exit 1
fi

if [ ! -f ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  "$PYTHON_CMD" -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo
echo "Starting interactive setup wizard..."
.venv/bin/python -m app.setup_wizard

echo
read -r -p "Setup complete. Run agent now? (y/n) " RUN_NOW
if [[ "$RUN_NOW" =~ ^([yY]|yes|YES)$ ]]; then
  .venv/bin/python -m app.main
fi

echo
read -r -p "Enable near-live scheduler every 2 minutes? (y/n) " ENABLE_SCHED
if [[ "$ENABLE_SCHED" =~ ^([yY]|yes|YES)$ ]]; then
  bash scripts/enable_scheduler_mac.sh 2
fi
