#!/usr/bin/env bash
# Validate Commit Hook — Flutter Gambling Studio
# Runs pre-commit checks for game integrity. Every game here is a gambling game,
# so the RNG and probability checks are unconditional.

# Only run on git commit commands
INPUT_JSON="${CLAUDE_TOOL_INPUT:-}"
if echo "$INPUT_JSON" | grep -q '"git commit"' 2>/dev/null || echo "$INPUT_JSON" | grep -q 'git commit' 2>/dev/null; then
  :
else
  exit 0
fi

ERRORS=()
WARNINGS=()

echo "🔍 Checking the game requirements before committing..."

# 1. math.Random() — CRITICAL. Unconditional: outcomes must come from Random.secure().
# Sole exception: the seeded run RNG in C5 casino roguelikes (lib/systems/run_rng.dart + ADR).
if find lib -name "*.dart" 2>/dev/null | xargs grep -l "math\.Random()" 2>/dev/null | grep -v "_test\.dart" | grep -qv "run_rng\.dart"; then
  ERRORS+=("🚨 math.Random() found! Use ONLY Random.secure()")
  find lib -name "*.dart" 2>/dev/null | xargs grep -ln "math\.Random()" 2>/dev/null | grep -v "_test\.dart" | grep -v "run_rng\.dart" | while read f; do
    ERRORS+=("   → $f")
  done
fi

# 2. Hardcoded win probabilities — unconditional
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "if.*random\(\).*<.*[0-9]\.[0-9]|Random\.secure\(\)\.nextDouble\(\)\s*<\s*[0-9]" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
  ERRORS+=("🚨 Hardcoded win probabilities! Every chance must go through GameConfig/WeightedRNG")
fi

# 2b. Real-currency symbols next to a virtual balance (responsible-gaming.md §1)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE '\$\{?(balance|coins|chips)|USD|€|₽' 2>/dev/null | grep -viE "iap|purchase|store|_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  Real-currency symbols next to the game balance — use only chips/coins")
fi

# 3. Check for hardcoded math-model values (must live in design/balance/*.json)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "(rtpTarget|targetRtp|rtp)\s*=\s*0\.[0-9]" 2>/dev/null | grep -v "game_config\.dart\|slot_config\.dart\|rtp_config\|_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  RTP values outside game_config.dart — check they are not hardcoded")
fi

# 4. Check for valid JSON configs
for json_file in design/balance/*.json assets/data/*.json; do
  if [ -f "$json_file" ]; then
    if ! python3 -c "import json,sys; json.load(open('$json_file'))" 2>/dev/null; then
      ERRORS+=("❌ Invalid JSON: $json_file")
    fi
  fi
done

# 5. Check for print() statements in lib (not test)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  print() found in lib/ — use Logger from the logging package")
  find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | while read f; do
    WARNINGS+=("   → $f")
  done
fi

# 6. Check that game_config.dart exists if there are game files
if [ -d "lib/game" ] && [ ! -f "lib/game/game_config.dart" ] && [ ! -f "lib/game/slot_config.dart" ]; then
  WARNINGS+=("⚠️  game_config.dart is missing — every game value belongs in the config")
fi

# 7. Check that weighted_rng.dart uses Random.secure() (gambling only)
if [ -f "lib/systems/weighted_rng.dart" ]; then
  if ! grep -q "Random\.secure()" lib/systems/weighted_rng.dart 2>/dev/null; then
    ERRORS+=("🚨 weighted_rng.dart does not use Random.secure()!")
  fi
fi

# Report results
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo ""
  echo "╔══════════════════════════════════════════╗"
  echo "║  ❌ COMMIT BLOCKED — game rules           ║"
  echo "╚══════════════════════════════════════════╝"
  for err in "${ERRORS[@]}"; do
    echo "  $err"
  done
  echo ""
  echo "Fix the errors and commit again."
  echo ""
  # Don't actually block (hooks are advisory) — just warn loudly
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  Warnings (they do not block the commit):"
  for warn in "${WARNINGS[@]}"; do
    echo "  $warn"
  done
fi

if [ ${#ERRORS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
  echo "✅ Game rules satisfied"
fi
