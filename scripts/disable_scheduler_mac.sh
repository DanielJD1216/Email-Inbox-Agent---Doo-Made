#!/usr/bin/env bash
set -euo pipefail

LABEL="${1:-com.emailinbox.agent}"
PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
LAUNCH_TARGET="gui/$(id -u)/$LABEL"

launchctl bootout "$LAUNCH_TARGET" >/dev/null 2>&1 || true
rm -f "$PLIST_PATH"

echo
echo "Scheduler disabled for label: $LABEL"
