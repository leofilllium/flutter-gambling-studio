#!/usr/bin/env bash
# Statusline for Flutter Gambling Studio
# Shows current game project context

STATE_FILE="production/session-state/active.md"

if [ -f "$STATE_FILE" ]; then
  EPIC=$(grep -m1 'Epic:' "$STATE_FILE" 2>/dev/null | sed 's/.*Epic: //' | tr -d '\r')
  FEATURE=$(grep -m1 'Feature:' "$STATE_FILE" 2>/dev/null | sed 's/.*Feature: //' | tr -d '\r')
  TASK=$(grep -m1 'Task:' "$STATE_FILE" 2>/dev/null | sed 's/.*Task: //' | tr -d '\r')

  if [ -n "$EPIC" ] && [ -n "$FEATURE" ] && [ -n "$TASK" ]; then
    echo "🎰 $EPIC › $FEATURE › $TASK"
  elif [ -n "$EPIC" ] && [ -n "$FEATURE" ]; then
    echo "🎰 $EPIC › $FEATURE"
  elif [ -n "$EPIC" ]; then
    echo "🎰 $EPIC"
  else
    echo "🎰 Gambling Studio"
  fi
else
  echo "🎰 Gambling Studio"
fi
