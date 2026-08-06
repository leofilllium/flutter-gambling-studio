#!/usr/bin/env bash
# Pre-Compact Hook — Flutter Game Studio
# Saves session progress notes before context compaction

STATE_FILE="production/session-state/active.md"
LOG_DIR="production/session-logs"
DATETIME=$(date '+%Y-%m-%d %H:%M')

mkdir -p "$LOG_DIR" "production/session-state"

# Update checkpoint timestamp
if [ -f "$STATE_FILE" ]; then
  # Update last-compact timestamp
  if grep -q "Last compaction:" "$STATE_FILE" 2>/dev/null; then
    sed -i.bak "s/Last compaction:.*/Last compaction: $DATETIME/" "$STATE_FILE" 2>/dev/null && rm -f "${STATE_FILE}.bak"
  else
    echo "" >> "$STATE_FILE"
    echo "Last compaction: $DATETIME" >> "$STATE_FILE"
  fi
fi

echo "💾 Progress saved before context compaction: $DATETIME"
echo "   State file: $STATE_FILE"
echo "   After compaction: read $STATE_FILE to restore context"
