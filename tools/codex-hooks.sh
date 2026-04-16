#!/usr/bin/env bash
set -euo pipefail

HOOK_NAME="${1:-}"
CUSTOM_INPUT="${2:-}"
HOOK_DIR=".claude/hooks"

if [ -z "$HOOK_NAME" ]; then
  echo "Использование: bash tools/codex-hooks.sh <hook-name>"
  echo "Доступные hook'и: session-start, detect-gaps, validate-assets, validate-commit, validate-push, pre-compact, session-stop, log-agent, all"
  exit 1
fi

if [ ! -d "$HOOK_DIR" ]; then
  echo "Каталог $HOOK_DIR не найден"
  exit 1
fi

run_hook() {
  local hook="$1"
  local script_path="$HOOK_DIR/$hook.sh"
  local default_input=""

  if [ ! -f "$script_path" ]; then
    echo "Hook не найден: $hook"
    return 1
  fi

  case "$hook" in
    validate-commit)
      default_input='git commit'
      ;;
    validate-push)
      default_input='git push origin main'
      ;;
    validate-assets)
      default_input='{"file_path":"assets/images/manual.svg"}'
      ;;
    log-agent)
      default_input='manual codex subagent invocation'
      ;;
    *)
      default_input='manual codex invocation'
      ;;
  esac

  echo "==> $hook"
  CLAUDE_TOOL_INPUT="${CLAUDE_TOOL_INPUT:-${CUSTOM_INPUT:-$default_input}}" \
  CLAUDE_TOOL_NAME="${CLAUDE_TOOL_NAME:-CodexManualHook}" \
  CLAUDE_SUBAGENT_NAME="${CLAUDE_SUBAGENT_NAME:-codex}" \
  bash "$script_path"
  echo ""
}

case "$HOOK_NAME" in
  all)
    run_hook session-start
    run_hook detect-gaps
    run_hook validate-assets
    run_hook validate-commit
    run_hook validate-push
    run_hook pre-compact
    run_hook session-stop
    ;;
  session-start|detect-gaps|validate-assets|validate-commit|validate-push|pre-compact|session-stop|log-agent)
    run_hook "$HOOK_NAME"
    ;;
  *)
    echo "Неизвестный hook: $HOOK_NAME"
    exit 1
    ;;
esac
