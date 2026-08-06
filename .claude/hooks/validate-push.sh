#!/usr/bin/env bash
# Validate Push Hook — Flutter Game Studio
# Warns when pushing to protected branches

INPUT_JSON="${CLAUDE_TOOL_INPUT:-}"

# Only run on git push commands
if ! echo "$INPUT_JSON" | grep -q 'git push' 2>/dev/null; then
  exit 0
fi

# Check if pushing to main/master
if echo "$INPUT_JSON" | grep -qE '"git push.*main|git push.*master|git push --force' 2>/dev/null; then
  echo ""
  echo "⚠️  WARNING: attempting to push to a protected branch!"
  echo "   Make sure that:"
  echo "   1. /balance-check passed (RTP within 95-97%)"
  echo "   2. /release-checklist has been run"
  echo "   3. There is no state leakage between spins"
  echo "   4. The RNG uses Random.secure() everywhere"
  echo ""
fi
