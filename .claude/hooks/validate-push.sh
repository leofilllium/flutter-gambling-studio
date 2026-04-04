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
  echo "⚠️  ВНИМАНИЕ: Попытка push в защищённую ветку!"
  echo "   Убедитесь, что:"
  echo "   1. /balance-check прошёл (RTP в диапазоне 95-97%)"
  echo "   2. /release-checklist выполнен"
  echo "   3. Нет state leakage между спинами"
  echo "   4. RNG использует Random.secure() везде"
  echo ""
fi
