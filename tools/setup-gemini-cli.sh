#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEMINI_HOME="${GEMINI_HOME:-$HOME/.gemini/antigravity}"
PLUGIN_NAME="flutter-gambling-studio"
PLUGIN_DIR="$GEMINI_HOME/plugins/$PLUGIN_NAME"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DST="$PLUGIN_DIR/skills"
MODE="${1:-link}" # link | copy

echo "Setting up Gemini CLI support..."

mkdir -p "$SKILLS_DST"

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
  install_skills
  cat <<EOF

Gemini CLI bootstrap completed.
Repo: $REPO_ROOT
Plugin Path: $PLUGIN_DIR
Skills: $SKILLS_DST

The framework, skills, and agents are now runnable in the Gemini CLI!
Restart the Gemini CLI instance if needed to detect the newly linked skills.
EOF
}

main
