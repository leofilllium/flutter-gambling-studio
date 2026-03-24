#!/usr/bin/env bash
# Detect Gaps Hook — Flutter Gambling Studio
# Warns when critical gambling game files are missing

GAPS=()
WARNINGS=()

# Check if any game has been started
if [ ! -f "pubspec.yaml" ]; then
  GAPS+=("❌ pubspec.yaml отсутствует — проект не инициализирован")
fi

# Check for critical game files
if [ -f "pubspec.yaml" ]; then
  if [ ! -f "lib/main.dart" ]; then
    GAPS+=("❌ lib/main.dart отсутствует")
  fi

  if [ ! -f "lib/game/slot_machine_game.dart" ] && [ ! -d "lib/game" ]; then
    WARNINGS+=("⚠️  lib/game/ не создан — запустите /autocreate или /brainstorm")
  fi

  # Check for RNG safety
  if find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | grep -q .; then
    GAPS+=("🚨 КРИТИЧНО: найден math.Random() — используйте Random.secure()!")
    find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | while read f; do
      GAPS+=("   → $f")
    done
  fi

  # Check for hardcoded probabilities
  if find lib -name "*.dart" 2>/dev/null | xargs grep -lE "(0\.[0-9]+\s*[<>]=?\s*(win|lose|jackpot|bonus))|if.*random.*<.*0\." 2>/dev/null | grep -q .; then
    GAPS+=("🚨 КРИТИЧНО: возможно захардкоженные вероятности — используйте SlotConfig!")
  fi

  # Check for GDD
  if [ ! -d "design/gdd" ] || [ -z "$(ls design/gdd/*.md 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  GDD документы отсутствуют — запустите /brainstorm или /design-system")
  fi

  # Check for RTP config
  if [ ! -f "design/balance/rtp-config.json" ]; then
    WARNINGS+=("⚠️  design/balance/rtp-config.json отсутствует — RTP не зафиксирован")
  fi

  # Check for RTP simulation tool
  if [ ! -f "tools/simulate_rtp.py" ]; then
    WARNINGS+=("⚠️  tools/simulate_rtp.py отсутствует — /balance-check не будет работать")
  fi
fi

# Print gaps
if [ ${#GAPS[@]} -gt 0 ]; then
  echo ""
  echo "🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ НАЙДЕНЫ:"
  for gap in "${GAPS[@]}"; do
    echo "   $gap"
  done
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  ПРЕДУПРЕЖДЕНИЯ:"
  for warn in "${WARNINGS[@]}"; do
    echo "   $warn"
  done
fi

if [ ${#GAPS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ] && [ -f "pubspec.yaml" ]; then
  echo "✅ Структура проекта в порядке"
fi
