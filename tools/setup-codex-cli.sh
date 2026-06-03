#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CONFIG_FILE="$CODEX_HOME/config.toml"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DST="$CODEX_HOME/skills"
MODE="${1:-link}" # link | copy

mkdir -p "$CODEX_HOME" "$SKILLS_DST"
touch "$CONFIG_FILE"

# Idempotency checks use grep -Fqx (fixed-string, whole-line, quiet) from
# coreutils, which is always available. The previous `rg`-based checks failed
# OPEN when ripgrep was absent (exit 127 read as "not found"), so every run
# re-appended its entries — duplicate TOML keys that break Codex's config.toml.
ensure_line() {
  local line="$1"
  grep -Fqx -- "$line" "$CONFIG_FILE" || printf '%s\n' "$line" >> "$CONFIG_FILE"
}

ensure_project_block() {
  local project_key="[projects.\"$REPO_ROOT\"]"
  grep -Fqx -- "$project_key" "$CONFIG_FILE" \
    || printf '\n%s\ntrust_level = "trusted"\n' "$project_key" >> "$CONFIG_FILE"
}

ensure_sandbox_defaults() {
  ensure_line 'approval_policy = "on-request"'
  ensure_line 'sandbox_mode = "workspace-write"'
  grep -Fqx -- '[sandbox_workspace_write]' "$CONFIG_FILE" \
    || printf '\n[sandbox_workspace_write]\nnetwork_access = true\n' >> "$CONFIG_FILE"
}

install_skills() {
  if [ ! -d "$SKILLS_SRC" ]; then
    echo "Skills source not found: $SKILLS_SRC"
    exit 1
  fi

  local installed=0
  local skill_dir
  while IFS= read -r -d '' skill_dir; do
    local name
    name="$(basename "$skill_dir")"
    local src="$skill_dir"
    local dst="$SKILLS_DST/$name"

    rm -rf "$dst"
    if [ "$MODE" = "copy" ]; then
      cp -R "$src" "$dst"
    else
      ln -s "$src" "$dst"
    fi
    installed=$((installed + 1))
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0)

  echo "Installed skills: $installed ($MODE mode)"
}

main() {
  ensure_project_block
  ensure_sandbox_defaults
  install_skills
  cat <<EOF
Codex CLI bootstrap completed.
Repo: $REPO_ROOT
Config: $CONFIG_FILE
Skills: $SKILLS_DST

Next step: restart Codex CLI so it reloads skills and project config.
EOF
}

main
