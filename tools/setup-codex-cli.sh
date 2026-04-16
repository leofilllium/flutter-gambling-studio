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

ensure_line() {
  local line="$1"
  if ! rg -F --quiet "$line" "$CONFIG_FILE"; then
    printf "%s\n" "$line" >> "$CONFIG_FILE"
  fi
}

ensure_project_block() {
  local project_key="[projects.\"$REPO_ROOT\"]"
  if ! rg -F --quiet "$project_key" "$CONFIG_FILE"; then
    printf "\n%s\ntrust_level = \"trusted\"\n" "$project_key" >> "$CONFIG_FILE"
  elif ! rg -n -U "\\[projects\\.\"$REPO_ROOT\"\\][\\s\\S]*?trust_level\\s*=\\s*\"trusted\"" "$CONFIG_FILE" >/dev/null 2>&1; then
    printf "\n# Added by flutter-game-studio bootstrap\n%s\ntrust_level = \"trusted\"\n" "$project_key" >> "$CONFIG_FILE"
  fi
}

ensure_sandbox_defaults() {
  ensure_line "approval_policy = \"on-request\""
  ensure_line "sandbox_mode = \"workspace-write\""
  if ! rg -F --quiet "[sandbox_workspace_write]" "$CONFIG_FILE"; then
    printf "\n[sandbox_workspace_write]\nnetwork_access = true\n" >> "$CONFIG_FILE"
  elif ! rg -n -U "\\[sandbox_workspace_write\\][\\s\\S]*?network_access\\s*=\\s*true" "$CONFIG_FILE" >/dev/null 2>&1; then
    printf "\n# Added by flutter-game-studio bootstrap\n[sandbox_workspace_write]\nnetwork_access = true\n" >> "$CONFIG_FILE"
  fi
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
