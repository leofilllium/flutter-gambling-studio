#!/usr/bin/env bash
# Validate Assets Hook — Flutter Game Studio
# Validates asset naming conventions after Write/Edit operations

INPUT_JSON="${CLAUDE_TOOL_INPUT:-}"
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only run after Write or Edit on asset files
if ! echo "$INPUT_JSON" | grep -qE '"assets/images|assets/audio|assets/data"' 2>/dev/null; then
  exit 0
fi

ERRORS=()
WARNINGS=()

# Check SVG naming conventions
find assets/images -name "*.svg" 2>/dev/null | while read f; do
  filename=$(basename "$f" .svg)
  if ! echo "$filename" | grep -qE '^(sprite_|background_|ui_|icon_)[a-z0-9_]+$'; then
    echo "⚠️  Неверное имя SVG ассета: $f"
    echo "   Ожидается: sprite_X, background_X, ui_X, или icon_X (snake_case)"
  fi
done

# Check audio naming conventions
find assets/audio -name "*.ogg" -o -name "*.mp3" 2>/dev/null | while read f; do
  filename=$(basename "$f")
  if ! echo "$filename" | grep -qE '^(sfx_|bgm_|ambient_)[a-z0-9_]+\.(ogg|mp3)$'; then
    echo "⚠️  Неверное имя аудио ассета: $f"
    echo "   Ожидается: sfx_X.ogg, bgm_X.ogg, или ambient_X.ogg"
  fi
done

# Check that assets are registered in pubspec.yaml
if [ -f "pubspec.yaml" ]; then
  NEW_FILE=$(echo "$INPUT_JSON" | grep -o '"file_path":"[^"]*assets[^"]*"' 2>/dev/null | sed 's/"file_path":"//' | tr -d '"')
  if [ -n "$NEW_FILE" ] && [ -f "$NEW_FILE" ]; then
    if ! grep -q "$NEW_FILE" pubspec.yaml 2>/dev/null; then
      ASSET_DIR=$(dirname "$NEW_FILE")/
      if ! grep -q "$ASSET_DIR" pubspec.yaml 2>/dev/null; then
        echo "⚠️  Ассет не зарегистрирован в pubspec.yaml: $NEW_FILE"
        echo "   Добавьте в секцию flutter.assets:"
        echo "     - $ASSET_DIR"
      fi
    fi
  fi
fi
