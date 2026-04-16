#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CONFIG_FILE="$CODEX_HOME/config.toml"
SKILLS_DIR="$CODEX_HOME/skills"

ok() { printf "[OK] %s\n" "$1"; }
warn() { printf "[WARN] %s\n" "$1"; }
fail() { printf "[FAIL] %s\n" "$1"; }

echo "Codex Doctor"
echo "repo:   $REPO_ROOT"
echo "home:   $CODEX_HOME"
echo "config: $CONFIG_FILE"
echo ""

if [ -f "$REPO_ROOT/AGENTS.md" ]; then
  ok "AGENTS.md exists"
else
  fail "AGENTS.md missing"
fi

if [ -f "$CONFIG_FILE" ]; then
  ok "config.toml exists"
else
  fail "config.toml missing"
fi

if [ -f "$CONFIG_FILE" ] && rg -F --quiet "[projects.\"$REPO_ROOT\"]" "$CONFIG_FILE"; then
  ok "project registered in Codex config"
else
  fail "project is not registered in Codex config"
fi

if [ -f "$CONFIG_FILE" ] && rg -F --quiet "sandbox_mode = \"workspace-write\"" "$CONFIG_FILE"; then
  ok "sandbox_mode is workspace-write"
else
  warn "sandbox_mode not set to workspace-write"
fi

if [ -f "$CONFIG_FILE" ] && rg -F --quiet "approval_policy = \"on-request\"" "$CONFIG_FILE"; then
  ok "approval_policy is on-request"
else
  warn "approval_policy is not on-request"
fi

if [ -d "$SKILLS_DIR" ]; then
  SKILL_COUNT="$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 \( -type d -o -type l \) ! -name '.system' | wc -l | tr -d ' ')"
  if [ "${SKILL_COUNT:-0}" -gt 0 ]; then
    ok "custom skills discovered in $SKILLS_DIR: $SKILL_COUNT"
  else
    fail "no custom skills found in $SKILLS_DIR"
  fi
else
  fail "skills directory missing: $SKILLS_DIR"
fi

if command -v rg >/dev/null 2>&1; then
  ok "bash commands available (rg found)"
else
  warn "ripgrep (rg) not found; install rg for fast code search"
fi

echo ""
echo "If you changed config/skills, restart Codex CLI."
