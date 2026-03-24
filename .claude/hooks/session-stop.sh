#!/usr/bin/env bash
# Session Stop Hook — Flutter Gambling Studio
# Logs session achievements when Claude stops

LOG_DIR="production/session-logs"
DATE=$(date '+%Y-%m-%d')
DATETIME=$(date '+%Y-%m-%d %H:%M')
LOG_FILE="$LOG_DIR/session-$DATE.md"

mkdir -p "$LOG_DIR"

# Count files modified in this session (approximate via git)
MODIFIED=$(git status --short 2>/dev/null | grep -c '.' || echo "0")

# Append to daily log
cat >> "$LOG_FILE" << EOF

## Сессия завершена: $DATETIME

- Изменено файлов: $MODIFIED
- Активные файлы:
$(git status --short 2>/dev/null | head -10 | sed 's/^/  /')

EOF

echo "📝 Сессия записана в $LOG_FILE"
