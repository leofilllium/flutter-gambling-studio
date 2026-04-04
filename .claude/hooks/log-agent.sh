#!/usr/bin/env bash
# Log Agent Hook — Flutter Game Studio
# Maintains an audit trail of all agent invocations

LOG_DIR="production/session-logs"
DATE=$(date '+%Y-%m-%d')
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
AUDIT_LOG="$LOG_DIR/agent-audit.log"

mkdir -p "$LOG_DIR"

# Get agent name from environment if available
AGENT_NAME="${CLAUDE_SUBAGENT_NAME:-unknown}"
INPUT_PREVIEW=$(echo "${CLAUDE_TOOL_INPUT:-}" | head -c 100 2>/dev/null || echo "")

# Append to audit log
echo "[$DATETIME] AGENT: $AGENT_NAME" >> "$AUDIT_LOG"
if [ -n "$INPUT_PREVIEW" ]; then
  echo "  Input: $INPUT_PREVIEW..." >> "$AUDIT_LOG"
fi
