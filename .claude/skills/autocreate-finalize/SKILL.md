---
name: autocreate-finalize
description: "Вторая половина конвейера /autocreate (Фазы 10.5 → 11 → 12): runtime emulator verification + финальный отчёт. НЕ вызывает /release-package — упаковка APK и архива выполняется только явным запуском /release-package. Запускается автоматически через Agent tool в конце /autocreate, либо вручную в новой conversation."
argument-hint: "[--skip-emulator | --no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Finalize — Часть 2 конвейера

**Назначение**: завершить `/autocreate` после того, как Часть 1 довела проект
до `dart analyze` 0 errors + `flutter test` зелёные. В этой части:
- runtime-верификация на эмуляторе (скрины + logcat + auto-fix)
- обновление session-state + финальный отчёт

**Упаковка (APK + архив) НЕ входит в этот навык.** Для получения загружаемого
архива запустите `/release-package` отдельно после финализации.

**Когда вызывается:**
- Автоматически: `/autocreate` в конце Фазы 10 вызывает Agent tool с
  subagent_type="general-purpose" и прописанным промптом
- Вручную: пользователь запускает `/autocreate-finalize` в **новой** conversation,
  если subagent упал, или чтобы повторить runtime-проверку после правок

**Что НЕ делает:**
- НЕ переписывает игровой код, не меняет GDD, не меняет баланс
- НЕ создаёт новые экраны
- НЕ запускает Фазы 1–10 — они уже выполнены Частью 1

---

## 🚨 MANDATORY CONTRACT

1. ✅ Читает `production/session-state/autocreate-handoff.md` **первым действием**
2. ✅ Валидирует что артефакты Части 1 существуют (`pubspec.yaml`, `lib/main.dart`,
   `dart analyze` всё ещё 0 errors)
3. ✅ Выполняет Фазы 10.5 → 11 → 12 в указанном порядке
4. ✅ Возвращает финальный отчёт в родительскую сессию (или печатает пользователю)

**Запрещено:**
- ❌ Менять `lib/game/game_config.dart`, `design/balance/*.json` — баланс зафиксирован
- ❌ Переписывать целые экраны — допустимы только точечные runtime-автофиксы
  (overflow, setState after dispose, missing asset path, null ValueNotifier)
- ❌ Вызывать `/release-package` — упаковка выполняется отдельным явным запуском

---

## Фаза 0 — Preflight & Handoff Read [~30 сек]

```bash
# 1. Handoff должен существовать
test -f production/session-state/autocreate-handoff.md || {
  echo "❌ Нет handoff-файла. Часть 1 /autocreate не завершилась?"
  exit 1
}

# 2. Проект должен компилироваться
dart analyze lib/ > /tmp/finalize_preflight_analyze.log 2>&1
if grep -q " error " /tmp/finalize_preflight_analyze.log; then
  echo "❌ dart analyze lib/ показывает errors — Часть 1 не закончила работу корректно"
  exit 1
fi

# 3. Тесты должны быть зелёными
flutter test > /tmp/finalize_preflight_test.log 2>&1 || {
  echo "⚠️ flutter test красный. Продолжаем, но это стоит исправить."
}
```

Прочитать handoff-файл, извлечь:
- Имя игры → для имени архива
- Жанр → для финального отчёта
- Путь к главному классу игры → для emulator-test навигации

---

## Фаза 10.5 — Runtime Emulator Verification [~8 мин]

Вызвать skill `/emulator-test --quick` (см. `.claude/skills/emulator-test/SKILL.md`).

### 10.5.1 — Preflight с автозапуском AVD

```bash
# Дефолт: Chrome web (не требует эмулятора).
# Android AVD используется только при явном --platform android.
CHROME_AVAILABLE=0
flutter devices 2>/dev/null | grep -qiE "Chrome|web" && CHROME_AVAILABLE=1

if [[ $CHROME_AVAILABLE -eq 1 ]]; then
  echo "🌐 Chrome web доступен — используем его (default)"
  export PLATFORM=web
  unset SKIP_SCREENSHOTS
else
  # Fallback: Android эмулятор
  RUNNING_EMU=$(adb devices 2>/dev/null | grep -E "emulator-[0-9]+.*device$" | head -1 | awk '{print $1}')
  if [[ -n "$RUNNING_EMU" ]]; then
    echo "✅ Android эмулятор запущен: $RUNNING_EMU (fallback)"
    export PLATFORM=android
    adb -s "$RUNNING_EMU" shell input keyevent 82 2>/dev/null || true
  else
    AVD=$(emulator -list-avds 2>/dev/null | head -1)
    if [[ -n "$AVD" ]]; then
      echo "🚀 Запуск AVD: $AVD (fallback)"
      nohup emulator -avd "$AVD" \
            -no-snapshot-save -no-boot-anim \
            -gpu swiftshader_indirect \
            -no-audio \
            > /tmp/avd.log 2>&1 &
      EMU_PID=$!
      echo "[emulator] PID=$EMU_PID"
      adb wait-for-device
      timeout 240 bash -c \
        'until [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d "\r")" = "1" ]; do sleep 2; done'
      sleep 30
      echo "✅ AVD загружен и прогрет"
      export PLATFORM=android
    else
      echo "⚠️ Chrome недоступен и нет AVD. Фаза 10.5 — SKIPPED."
      echo "   Фаза 10.6 (release-package) всё равно выполняется без скриншотов."
      export SKIP_SCREENSHOTS=1
    fi
  fi
fi

# NDK pre-flight: ensure NDK 27 is available before flutter run attempt
if command -v sdkmanager &>/dev/null; then
  sdkmanager --list_installed 2>/dev/null | grep -q "ndk;27" || {
    echo "🔧 NDK 27 not found — installing..."
    sdkmanager "ndk;27.0.12077973" 2>/dev/null && echo "✅ NDK 27 installed" || \
      echo "⚠️ NDK install failed — build may fail if ndkVersion not resolved"
  }
fi

# Patch android/app/build.gradle if ndkVersion missing (prevents Gradle build failure)
if [[ -f android/app/build.gradle ]] && ! grep -q "ndkVersion" android/app/build.gradle; then
  python3 - <<'PY'
import re, pathlib
bg = pathlib.Path("android/app/build.gradle")
src = bg.read_text()
src = src.replace("android {", 'android {\n    ndkVersion "27.0.12077973"', 1)
src = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 21', src)
bg.write_text(src)
print("✅ Patched build.gradle: ndkVersion + minSdkVersion 21")
PY
fi
```

Критерий: если после автозапуска `adb devices` показывает `emulator-XXXX device` —
идём дальше. Если нет — SKIPPED, но Фаза 10.6 всё равно обязательна.

### 10.5.2 — Запуск emulator-test --quick

Следовать `.claude/skills/emulator-test/SKILL.md` в режиме `--quick`:
- `flutter run` с логированием в `.claude/runtime-logs/flutter-run.log`
- Параллельно `adb logcat` → `.claude/runtime-logs/logcat.log`
- Скриншоты: splash, menu, game-idle, game-action, game-after-action
- Визуальный анализ каждого скриншота по чеклисту V1–V12
- Парсинг логов на EXCEPTION CAUGHT, RenderFlex overflow, Unable to load asset

### 10.5.3 — Auto-Fix Loop (до 3 итераций)

Консолидировать проблемы, разметить severity (CRITICAL/HIGH/MEDIUM), назначить агентов:
- V2/V3/V5/V7/V8/V9/V10/V11 → **ui-programmer**
- V4/V12 → **mechanics-programmer**
- VFX не виден → **juice-artist**
- Logcat asset errors → проверить `lib/assets.dart` vs реальные файлы

**Разрешённые автофиксы:**

| Симптом | Причина | Автофикс |
|---------|---------|----------|
| Пустой чёрный прямоугольник вместо игрового поля | Компоненты не добавлены в World.onLoad() | `await world.addAll([...])` |
| HUD показывает null/NaN | ValueNotifier не проинициализирован | Проинициализировать в Game constructor |
| Splash чёрный и не переходит | Нет Timer для навигации | `Future.delayed → pushReplacementNamed` |
| Белый экран после PLAY | Route не зарегистрирован | Добавить в `routes:` map в app.dart |
| Жёлтые overflow полосы | ListView без Expanded | Обернуть в Expanded |
| Красный экран exception | Null check/type error из stacktrace | Исправить по file:line из лога |
| "Unable to load asset" | Несоответствие путей в `lib/assets.dart` | Исправить путь или создать файл |

**Запрещённые "автофиксы":**
- Менять `game_config.dart` (баланс зафиксирован)
- Менять `rtp-config.json` / `level-config.json`
- Переписывать целые экраны — только точечные правки
- Менять GDD

### 10.5.4 — Критерий выхода Фазы 10.5

- **Успех**: 0 CRITICAL визуальных проблем + 0 FATAL exceptions в logcat
- **Частичный успех**: CRITICAL устранены, остались MEDIUM — идём в 10.6
- **Неудача**: после 3 итераций CRITICAL остались — сохранить
  `production/runtime-screenshots/<ts>/REPORT.md`, отчитаться с verdict FAIL,
  **но Фаза 10.6 всё равно выполняется** (у пользователя должен быть архив
  для диагностики)

### 10.5.5 — Артефакты

- `production/runtime-screenshots/<ts>/*.png` — снимки
- `production/runtime-screenshots/<ts>/REPORT.md` — verdict PASS/CONCERNS/FAIL
- `.claude/runtime-logs/flutter-run.log`
- `.claude/runtime-logs/logcat.log`

Cleanup: остановить `flutter run` и `adb logcat` по PID из `.claude/runtime-logs/*.pid`.

---

## Фаза 11 — Session State Update [~1 мин]

Обновить `production/session-state/active.md`:

```markdown
<!-- STATUS -->
Epic: [Game Name]
Feature: Complete Game
Task: Production-ready
<!-- /STATUS -->

## Статус
Игра полностью реализована и верифицирована. Для получения APK и архива запустите /release-package.

## Runtime verification
- Verdict: [PASS / CONCERNS / FAIL / SKIPPED]
- Скриншоты: production/runtime-screenshots/<ts>/
- Report: production/runtime-screenshots/<ts>/REPORT.md

## Тесты Части 1
- Unit: [N] зелёные
- Integration: [N] зелёные
- Edge cases: [N] зелёные

## Баланс
[RTP / Difficulty curve результаты из Части 1]
```

Также отметить handoff-файл завершённым: дописать в
`production/session-state/autocreate-handoff.md` финальную секцию
`## Часть 2 завершена` с ISO-timestamp и verdict.

---

## Фаза 12 — Final Report

Вывести пользователю (а если вызван как subagent — вернуть в родительскую сессию):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 AUTOCREATE COMPLETE — PRODUCTION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Экраны (12+):
   ✅ Splash, Main Menu, Game Screen + HUD
   ✅ Paytable, Settings, Help, Daily Bonus
   ✅ Leaderboard, Profile, Win Overlays (3 tiers)
   ✅ Insufficient Funds, Bonus Mode Overlay

🎮 Gameplay:
   ✅ Core game loop works end-to-end
   ✅ [Genre]: [RNG/matching/spawning/physics] fully functional
   ✅ Stateless Outcomes, GameState sealed class
   ✅ All constants in GameConfig, double-click protection

🧪 Tests (Часть 1):
   ✅ Unit: [N] passed | Integration: [N] passed | Edge: [N] passed

🌐 Runtime verification (Chrome, Фаза 10.5):
   [PASS / CONCERNS / FAIL / SKIPPED] — [N] CRITICAL, [N] HIGH issues
   Скриншоты: production/runtime-screenshots/<ts>/
   Report: production/runtime-screenshots/<ts>/REPORT.md

⚖️ Balance (Часть 1):
   [Gambling: RTP XX.X% (target 95-97%)]
   [Puzzle: Difficulty curve validated]
   [Arcade: Spawn/scoring balanced]

📦 Для получения APK и загружаемого архива:
   /release-package                 — упаковка APK + скриншоты + исходники → один .zip

🔧 Команды запуска:
   flutter run -d chrome        — запустить в Chrome
   flutter run                  — запустить на доступном устройстве
   flutter test                 — запустить тесты
   adb install project_zip/[name]-[ts]/apk/*.apk — установить APK (если есть)

📋 Рекомендованные перезапуски:
   /emulator-test               — ПОВТОРНАЯ runtime-верификация
   /release-package             — ПОВТОРНАЯ упаковка релиза
   /autocreate-finalize         — перезапустить Часть 2 целиком

📋 Опциональные следующие шаги:
   /add-feature [фича]          — добавить механику
   /code-review                 — полное ревью кода
   /balance-check               — детальная проверка баланса (1М итераций)
   /perf-profile                — профилирование производительности
   /release-checklist           — финальный GO/NO-GO чеклист перед стор-релизом
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Гарантии качества (Quality Gates)

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 0. Preflight | Handoff есть + `dart analyze` 0 errors | 1 (fail-fast) |
| 10.5. Runtime Chrome | 0 CRITICAL visual + 0 FATAL в flutter-run.log | 3 (Chrome всегда доступен) |
| 11. Session State | `active.md` обновлён | 1 |
| 12. Final Report | Отчёт напечатан / возвращён | 1 |

**АБСОЛЮТНЫЙ МИНИМУМ для завершения Части 2:**
- `production/session-state/active.md` обновлён
- Финальный отчёт напечатан с verdict runtime-верификации

---

## Восстановление после сбоев

**Если subagent упал посреди Части 2** — пользователь запускает
`/autocreate-finalize` в новой conversation. Skill:
1. Читает `autocreate-handoff.md` и `active.md`
2. Определяет, с какой фазы продолжить (по наличию артефактов):
   - Нет `production/runtime-screenshots/<ts>/` → начать с 10.5
   - Есть скрины, но `active.md` не обновлён → начать с 11
3. Продолжает с нужной фазы, не переделывая сделанное

**Если Chrome почему-то недоступен** — попробовать `flutter run -d web-server` или
установить Chrome. Chrome — первичная платформа, всегда должен быть доступен.
Если совсем нет браузера — Фаза 10.5 SKIPPED, архив создаётся без скриншотов.
В `RELEASE_INFO.md` пометка `CHROME_SKIPPED: true`.
