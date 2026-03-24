#!/usr/bin/env bash
# Pre-Compact Hook — Flutter Gambling Studio
# Saves session progress notes before context compaction

STATE_FILE="production/session-state/active.md"
LOG_DIR="production/session-logs"
DATETIME=$(date '+%Y-%m-%d %H:%M')

mkdir -p "$LOG_DIR" "production/session-state"

# Update checkpoint timestamp
if [ -f "$STATE_FILE" ]; then
  # Update last-compact timestamp
  if grep -q "Последнее сжатие:" "$STATE_FILE" 2>/dev/null; then
    sed -i.bak "s/Последнее сжатие:.*/Последнее сжатие: $DATETIME/" "$STATE_FILE" 2>/dev/null && rm -f "${STATE_FILE}.bak"
  else
    echo "" >> "$STATE_FILE"
    echo "Последнее сжатие: $DATETIME" >> "$STATE_FILE"
  fi
fi

echo "💾 Прогресс сохранён перед сжатием контекста: $DATETIME"
echo "   Файл состояния: $STATE_FILE"
echo "   После сжатия: прочитайте $STATE_FILE для восстановления контекста"
