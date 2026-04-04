#!/usr/bin/env bash
# Detect Gaps Hook — Flutter Game Studio
# Warns when critical game files are missing

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

  if [ ! -d "lib/game" ]; then
    WARNINGS+=("⚠️  lib/game/ не создан — запустите /autocreate или /brainstorm")
  fi

  # Check for RNG safety (only relevant for gambling genre)
  if find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | grep -q .; then
    # Only warn if this looks like a gambling project
    if find lib -name "*.dart" 2>/dev/null | xargs grep -l "WeightedRng\|PaylineEvaluator\|reelWeights" 2>/dev/null | grep -q .; then
      GAPS+=("🚨 КРИТИЧНО: найден math.Random() в gambling коде — используйте Random.secure()!")
      find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | while read f; do
        GAPS+=("   → $f")
      done
    fi
  fi

  # Check for hardcoded probabilities (gambling only)
  if find lib -name "*.dart" 2>/dev/null | xargs grep -lE "(0\.[0-9]+\s*[<>]=?\s*(win|lose|jackpot|bonus))|if.*random.*<.*0\." 2>/dev/null | grep -q .; then
    if find lib -name "*.dart" 2>/dev/null | xargs grep -l "WeightedRng\|reelWeights" 2>/dev/null | grep -q .; then
      GAPS+=("🚨 КРИТИЧНО: возможно захардкоженные вероятности — используйте GameConfig!")
    fi
  fi

  # Check for GDD
  if [ ! -d "design/gdd" ] || [ -z "$(ls design/gdd/*.md 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  GDD документы отсутствуют — запустите /brainstorm или /design-system")
  fi

  # Check for balance config
  if [ ! -d "design/balance" ] || [ -z "$(ls design/balance/*.json 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  design/balance/ пуст — /balance-check не будет работать")
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
