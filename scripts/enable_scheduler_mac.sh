#!/usr/bin/env bash
set -euo pipefail

EVERY_MINUTES="${1:-2}"
LABEL="${2:-com.emailinbox.agent}"

if ! [[ "$EVERY_MINUTES" =~ ^[0-9]+$ ]] || [ "$EVERY_MINUTES" -lt 1 ]; then
  echo "Every-minutes must be a positive integer."
  echo "Usage: bash scripts/enable_scheduler_mac.sh [every_minutes] [label]"
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$REPO_DIR/.venv/bin/python"
LOG_DIR="$REPO_DIR/logs"
LOG_PATH="$LOG_DIR/agent.log"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/$LABEL.plist"
START_INTERVAL=$((EVERY_MINUTES * 60))

if [ ! -f "$PYTHON_PATH" ]; then
  echo "Virtual environment not found: $PYTHON_PATH"
  echo "Run this first:"
  echo "  bash scripts/first_run_mac.sh"
  exit 1
fi

mkdir -p "$LOG_DIR" "$PLIST_DIR"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>-lc</string>
      <string>cd "$REPO_DIR" && "$PYTHON_PATH" -m app.main >> "$LOG_PATH" 2>&1</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>$START_INTERVAL</integer>
    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>
  </dict>
</plist>
EOF

LAUNCH_TARGET="gui/$(id -u)/$LABEL"

launchctl bootout "$LAUNCH_TARGET" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "$LAUNCH_TARGET"
launchctl kickstart -k "$LAUNCH_TARGET"

echo
echo "Scheduler is enabled."
echo "Label    : $LABEL"
echo "Interval : every $EVERY_MINUTES minute(s)"
echo "Plist    : $PLIST_PATH"
echo "Log file : $LOG_PATH"
echo
echo "Check status:"
echo "  launchctl print $LAUNCH_TARGET"
echo "Disable later:"
echo "  bash scripts/disable_scheduler_mac.sh \"$LABEL\""
