#!/usr/bin/env bash
# Validate Commit Hook — Flutter Game Studio
# Runs pre-commit checks for game integrity (gambling-specific checks are conditional)

# Only run on git commit commands
INPUT_JSON="${CLAUDE_TOOL_INPUT:-}"
if echo "$INPUT_JSON" | grep -q '"git commit"' 2>/dev/null || echo "$INPUT_JSON" | grep -q 'git commit' 2>/dev/null; then
  :
else
  exit 0
fi

ERRORS=()
WARNINGS=()

echo "🔍 Проверка игровых требований перед коммитом..."

# Detect if this is a gambling project
IS_GAMBLING=false
if find lib -name "*.dart" 2>/dev/null | xargs grep -l "WeightedRng\|PaylineEvaluator\|reelWeights" 2>/dev/null | grep -q .; then
  IS_GAMBLING=true
fi

# 1. Check for math.Random() — CRITICAL for gambling RNG integrity
if [ "$IS_GAMBLING" = true ]; then
  if find lib -name "*.dart" 2>/dev/null | xargs grep -l "math\.Random()" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
    ERRORS+=("🚨 math.Random() найден в gambling коде! Используйте ТОЛЬКО Random.secure()")
    find lib -name "*.dart" 2>/dev/null | xargs grep -ln "math\.Random()" 2>/dev/null | grep -v "_test\.dart" | while read f; do
      ERRORS+=("   → $f")
    done
  fi
fi

# 2. Check for hardcoded win probabilities (gambling only)
if [ "$IS_GAMBLING" = true ]; then
  if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "if.*random\(\).*<.*[0-9]\.[0-9]|Random\.secure\(\)\.nextDouble\(\)\s*<\s*[0-9]" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
    ERRORS+=("🚨 Захардкоженные вероятности выигрыша! Все шансы должны идти через GameConfig/WeightedRNG")
  fi
fi

# 3. Check for hardcoded game config values (all genres)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "(rtpTarget|targetRtp|rtp)\s*=\s*0\.[0-9]" 2>/dev/null | grep -v "game_config\.dart\|slot_config\.dart\|rtp_config\|_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  RTP значения вне game_config.dart — проверьте, что это не захардкожено")
fi

# 4. Check for valid JSON configs
for json_file in design/balance/*.json assets/data/*.json; do
  if [ -f "$json_file" ]; then
    if ! python3 -c "import json,sys; json.load(open('$json_file'))" 2>/dev/null; then
      ERRORS+=("❌ Невалидный JSON: $json_file")
    fi
  fi
done

# 5. Check for print() statements in lib (not test)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  print() найден в lib/ — используйте Logger из пакета logging")
  find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | while read f; do
    WARNINGS+=("   → $f")
  done
fi

# 6. Check that game_config.dart exists if there are game files
if [ -d "lib/game" ] && [ ! -f "lib/game/game_config.dart" ] && [ ! -f "lib/game/slot_config.dart" ]; then
  WARNINGS+=("⚠️  game_config.dart отсутствует — все игровые значения должны быть в конфиге")
fi

# 7. Check that weighted_rng.dart uses Random.secure() (gambling only)
if [ -f "lib/systems/weighted_rng.dart" ]; then
  if ! grep -q "Random\.secure()" lib/systems/weighted_rng.dart 2>/dev/null; then
    ERRORS+=("🚨 weighted_rng.dart не использует Random.secure()!")
  fi
fi

# Report results
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo ""
  echo "╔══════════════════════════════════════════╗"
  echo "║  ❌ КОММИТ ЗАБЛОКИРОВАН — game rules      ║"
  echo "╚══════════════════════════════════════════╝"
  for err in "${ERRORS[@]}"; do
    echo "  $err"
  done
  echo ""
  echo "Исправьте ошибки и повторите коммит."
  echo ""
  # Don't actually block (hooks are advisory) — just warn loudly
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  Предупреждения (не блокируют коммит):"
  for warn in "${WARNINGS[@]}"; do
    echo "  $warn"
  done
fi

if [ ${#ERRORS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
  echo "✅ Игровые правила соблюдены"
fi
