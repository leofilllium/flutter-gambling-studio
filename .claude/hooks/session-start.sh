#!/usr/bin/env bash
# Session Start Hook — Flutter Game Studio
# Loads sprint context and shows project state at the start of every session

STATE_FILE="production/session-state/active.md"
LOG_DIR="production/session-logs"
DATE=$(date '+%Y-%m-%d %H:%M')

mkdir -p "$LOG_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 Flutter Game Studio — Сессия начата: $DATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for active game project
GAME_DIR=""
if [ -f "lib/game/slot_machine_game.dart" ]; then
  GAME_DIR="lib/game/slot_machine_game.dart"
  GAME_NAME=$(basename $(pwd))
  echo "🎮 Проект: $GAME_NAME"
fi

# Check pubspec
if [ -f "pubspec.yaml" ]; then
  GAME_NAME=$(grep -m1 '^name:' pubspec.yaml 2>/dev/null | sed 's/name: //')
  FLAME_VER=$(grep 'flame:' pubspec.yaml 2>/dev/null | head -1 | sed 's/.*flame: //' | tr -d ' ')
  if [ -n "$GAME_NAME" ]; then
    echo "📦 Пакет: $GAME_NAME"
  fi
  if [ -n "$FLAME_VER" ]; then
    echo "🔥 Flame: $FLAME_VER"
  fi
fi

# Show last 3 git commits
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo ""
  echo "📝 Последние коммиты:"
  git log --oneline -3 2>/dev/null | while read line; do
    echo "   $line"
  done
fi

# Show session state if exists
if [ -f "$STATE_FILE" ]; then
  echo ""
  echo "📋 Состояние сессии:"
  head -20 "$STATE_FILE" | grep -v '^$' | while read line; do
    echo "   $line"
  done
  echo ""
  echo "💡 Файл состояния: $STATE_FILE"
fi

# Check for GDD files
GDD_COUNT=$(find design/gdd -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$GDD_COUNT" -gt "0" ]; then
  echo ""
  echo "📐 Документов GDD: $GDD_COUNT"
  find design/gdd -name "*.md" 2>/dev/null | while read f; do
    echo "   - $f"
  done
fi

# Check RTP config
if [ -f "design/balance/rtp-config.json" ]; then
  RTP=$(grep -o '"target_rtp":[^,}]*' design/balance/rtp-config.json 2>/dev/null | head -1)
  if [ -n "$RTP" ]; then
    echo ""
    echo "💰 RTP конфиг: $RTP"
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Команды: /start | /continue-project | /autocreate | /brainstorm"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
