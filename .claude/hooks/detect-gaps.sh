#!/usr/bin/env bash
# Detect Gaps Hook — Flutter Game Studio
# Warns when critical game files are missing

GAPS=()
WARNINGS=()

# Check if any game has been started
if [ ! -f "pubspec.yaml" ]; then
  GAPS+=("❌ pubspec.yaml is missing — the project is not initialised")
fi

# Check for critical game files
if [ -f "pubspec.yaml" ]; then
  if [ ! -f "lib/main.dart" ]; then
    GAPS+=("❌ lib/main.dart is missing")
  fi

  # Phone-only product target — Flutter + native declarations must all be portrait, iPhone-only.
  if [ -f "lib/main.dart" ]; then
    if ! grep -q "SystemChrome.setPreferredOrientations" lib/main.dart || \
       ! grep -q "DeviceOrientation.portraitUp" lib/main.dart; then
      GAPS+=("❌ Phone contract: lib/main.dart does not lock DeviceOrientation.portraitUp")
    fi
    if ! grep -R -q "phoneViewport" lib 2>/dev/null; then
      GAPS+=("❌ Phone contract: Key('phoneViewport') is missing — wide Web may reflow as desktop/tablet")
    fi
  fi
  if [ -f "android/app/src/main/AndroidManifest.xml" ] && \
     ! grep -q 'android:screenOrientation="portrait"' android/app/src/main/AndroidManifest.xml; then
    GAPS+=("❌ Phone contract: Android launcher activity is not locked to portrait")
  fi
  if [ -f "ios/Runner/Info.plist" ]; then
    if ! grep -q "UIInterfaceOrientationPortrait" ios/Runner/Info.plist; then
      GAPS+=("❌ Phone contract: iOS portrait orientation is missing")
    fi
    if grep -qE "UIInterfaceOrientationLandscape|UISupportedInterfaceOrientations~ipad" ios/Runner/Info.plist; then
      GAPS+=("❌ Phone contract: iOS still declares landscape or iPad orientations")
    fi
  fi
  if [ -f "ios/Runner.xcodeproj/project.pbxproj" ]; then
    if ! grep -qE 'TARGETED_DEVICE_FAMILY = "?1"?;' ios/Runner.xcodeproj/project.pbxproj || \
       grep -qE 'TARGETED_DEVICE_FAMILY = .*2' ios/Runner.xcodeproj/project.pbxproj; then
      GAPS+=("❌ Phone contract: Xcode target must use TARGETED_DEVICE_FAMILY = 1 in every configuration")
    fi
  fi

  if [ ! -d "lib/game" ]; then
    WARNINGS+=("⚠️  lib/game/ has not been created — run /autocreate or /brainstorm")
  fi

  # Gameplay-screen contract — deterministic hooks for geometry tests and runtime measurement.
  GAME_SCREEN_FILES=$(find lib/screens -type f -name "*game*screen*.dart" 2>/dev/null)
  if [ -n "$GAME_SCREEN_FILES" ]; then
    if ! grep -q "gameplaySurface" $GAME_SCREEN_FILES 2>/dev/null; then
      GAPS+=("❌ GameScreen is missing Key('gameplaySurface') — full-viewport geometry cannot be verified")
    fi
    if ! grep -q "primaryAction" $GAME_SCREEN_FILES 2>/dev/null; then
      GAPS+=("❌ GameScreen is missing Key('primaryAction') — action visibility/size cannot be verified")
    fi
    if [ ! -f "test/screens/game_screen_layout_test.dart" ]; then
      GAPS+=("❌ test/screens/game_screen_layout_test.dart is missing — run the four-size gameplay layout gate")
    fi
  fi

  # RNG safety — unconditional: every game in this studio is a gambling game.
  # The only sanctioned exception is the seeded run RNG in C5 roguelikes (run_rng.dart + ADR).
  if find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | grep -qv "run_rng.dart"; then
    GAPS+=("🚨 CRITICAL: math.Random() found — use Random.secure()!")
    find lib -name "*.dart" 2>/dev/null | xargs grep -l "math.Random()" 2>/dev/null | grep -v "_test.dart" | grep -v "run_rng.dart" | while read f; do
      GAPS+=("   → $f")
    done
  fi

  # Check for hardcoded probabilities
  if find lib -name "*.dart" 2>/dev/null | xargs grep -lE "(0\.[0-9]+\s*[<>]=?\s*(win|lose|jackpot|bonus))|if.*random.*<.*0\." 2>/dev/null | grep -q .; then
    if find lib -name "*.dart" 2>/dev/null | xargs grep -l "WeightedRng\|reelWeights" 2>/dev/null | grep -q .; then
      GAPS+=("🚨 CRITICAL: probabilities may be hardcoded — use GameConfig!")
    fi
  fi

  # Check for GDD
  if [ ! -d "design/gdd" ] || [ -z "$(ls design/gdd/*.md 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  No GDD documents — run /brainstorm or /design-system")
  fi

  # Check for balance config
  if [ ! -d "design/balance" ] || [ -z "$(ls design/balance/*.json 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  design/balance/ is empty — /balance-check will not work")
  fi
fi

# Print gaps
if [ ${#GAPS[@]} -gt 0 ]; then
  echo ""
  echo "🚨 CRITICAL PROBLEMS FOUND:"
  for gap in "${GAPS[@]}"; do
    echo "   $gap"
  done
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  WARNINGS:"
  for warn in "${WARNINGS[@]}"; do
    echo "   $warn"
  done
fi

if [ ${#GAPS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ] && [ -f "pubspec.yaml" ]; then
  echo "✅ Project structure looks fine"
fi
