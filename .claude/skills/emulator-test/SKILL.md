---
name: emulator-test
description: "Runtime-верификация готовой мини-игры на реальном устройстве через ADB (Android) или Simulator (iOS). Запускает приложение, навигирует по всем экранам, делает скриншоты, визуально анализирует их на наличие проблем (пустой игровой экран, RenderFlex overflow, Flutter red screen, отсутствующие ассеты, белые/чёрные экраны), парсит logcat на exceptions, и автоматически исправляет найденные баги через цикл с агентами. Интегрируется в /autocreate после dart analyze."
argument-hint: "[--device deviceId | --platform android|ios | --no-fix | --quick]  (default: android/adb)"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Emulator Test — Runtime-верификация на реальном устройстве

**Проблема**: `dart analyze` + `flutter test` **не видят** runtime-проблем, которые проявляются
только при запуске: пустой игровой экран (чёрный прямоугольник вместо барабанов), RenderFlex
overflow (жёлто-чёрные полосы), Flutter "red screen of death" (необработанный exception),
кривой layout на конкретном разрешении, `setState() called after dispose`, missing asset, и т.д.

**Это навык-страховка**: запускает игру в эмуляторе, навигирует по всем экранам, делает
скриншоты, **визуально анализирует их через vision** и **парсит logcat** на предмет
исключений. Найденное — автоматически чинит через цикл с профильными агентами.

**Режимы:**
- По умолчанию: полный цикл (найти → визуально проанализировать → исправить → перезапустить)
- `--no-fix`: только отчёт без изменений
- `--quick`: только главные экраны (splash/menu/game), без daily-bonus/leaderboard/profile
- `--device <id>`: использовать конкретное устройство (иначе первое доступное Android-устройство)
- `--platform android|ios`: принудительно выбрать платформу. **По умолчанию: `android` (через ADB).**
  iOS-ветка активируется только при явном `--platform ios`.

---

## Фаза 0 — Environment Preflight [~15 сек]

**Дефолтная платформа — Android через ADB.** iOS включается только явным `--platform ios`.
Перед запуском ОБЯЗАТЕЛЬНО проверить окружение. Если что-то отсутствует — сообщить пользователю
и завершить работу с понятным сообщением (НЕ пытаться чинить окружение автоматически).

```bash
# Проверка Flutter
flutter --version || { echo "❌ Flutter не найден в PATH"; exit 1; }

# Проверка устройств
flutter devices

# Проверка ADB (для Android)
adb version 2>/dev/null || echo "⚠️ adb не найден — только iOS simulator будет доступен"

# Список подключённых Android устройств
adb devices -l 2>/dev/null

# Список iOS симуляторов (только macOS)
xcrun simctl list devices booted 2>/dev/null
```

### Если нет ни одного устройства

Предложить пользователю запустить эмулятор:

**Android:**
```bash
# Показать список доступных AVD
emulator -list-avds

# Запустить первый AVD в фоне
emulator -avd <AVD_NAME> -no-snapshot-save &

# Подождать загрузки (до 90 сек)
adb wait-for-device
adb shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done'
```

**iOS (macOS only):**
```bash
xcrun simctl boot "iPhone 15"
open -a Simulator
```

**Критерий выхода Фазы 0**: есть хотя бы одно загруженное устройство в `flutter devices`.

---

## Фаза 1 — Build & Install [~2 мин]

```bash
# Убедиться что проект собирается
flutter pub get
dart analyze lib/ | tail -5

# Запустить в debug режиме с verbose logging в фоне
# ВАЖНО: --verbose для отлова Widget errors в stdout
# ВАЖНО: если прошлый ран дал .INVALID PNG — добавить --no-enable-impeller,
#        иначе adb screencap не увидит Flutter surface.
mkdir -p .claude/runtime-logs
IMPELLER_FLAG=""
[[ "$NO_IMPELLER" == "1" ]] && IMPELLER_FLAG="--no-enable-impeller"
flutter run -d <deviceId> --verbose $IMPELLER_FLAG > .claude/runtime-logs/flutter-run.log 2>&1 &
FLUTTER_PID=$!
echo $FLUTTER_PID > .claude/runtime-logs/flutter.pid

# Ожидание пока игра реально запустится на устройстве (до 120 сек)
# Используем маркер "Syncing files to device" из лога
for i in $(seq 1 120); do
  if grep -q "Syncing files to device\|Flutter run key commands" .claude/runtime-logs/flutter-run.log 2>/dev/null; then
    echo "✅ Приложение запущено"
    break
  fi
  sleep 1
done
```

### Параллельно запустить logcat (только Android)

```bash
# Очистить старый лог и начать запись
adb logcat -c
adb logcat -v time flutter:V *:E > .claude/runtime-logs/logcat.log 2>&1 &
LOGCAT_PID=$!
echo $LOGCAT_PID > .claude/runtime-logs/logcat.pid
```

### Если build упал

Прочитать `.claude/runtime-logs/flutter-run.log`, извлечь ошибки компиляции Gradle/CocoaPods,
исправить и повторить. Максимум 3 итерации. Если не удаётся — завершить с отчётом.

---

## Фаза 2 — Screenshot Tour [~3 мин]

**Стратегия**: навигировать по игре через ADB input events, после КАЖДОГО экрана ждать
анимацию (1-2 сек) и делать скриншот. Android — дефолт. Для iOS — `xcrun simctl io booted screenshot`.

### ⚠️ Impeller caveat (корневая причина «invalid image»)

На Android Flutter по умолчанию использует Impeller. `adb exec-out screencap -p` **не видит
Impeller surface** на ряде устройств и возвращает либо чёрный кадр, либо PNG с поломанным
color space, который vision-анализ отвергает как «invalid image».

**Поэтому первичный метод снятия — `flutter screenshot`** (читает с Flutter-стороны, Impeller-safe).
`adb exec-out screencap -p` используется только как фоллбэк. После каждого снимка **валидируем
PNG-сигнатуру** (`89 50 4E 47`). Если файл не PNG — retry через альтернативный метод.

### Координаты для навигации

Поскольку мы не знаем точные координаты кнопок для каждой игры, применяем эвристику:
1. Получить разрешение устройства: `adb shell wm size` → например `1080x2400`
2. Center tap — по центру: `adb shell input tap 540 1200`
3. Bottom action tap — нижняя треть: `adb shell input tap 540 2000` (кнопка Play/Spin обычно здесь)
4. Back: `adb shell input keyevent KEYCODE_BACK`

### Последовательность скриншотов

Создать директорию `production/runtime-screenshots/<timestamp>/` и снимать в неё.

```bash
TS=$(date +%Y%m%d-%H%M%S)
SHOT_DIR="production/runtime-screenshots/$TS"
mkdir -p "$SHOT_DIR"

# Платформа фиксирована: android (default). Переопределяется только --platform ios.
PLATFORM="${PLATFORM:-android}"
DEVICE_ID="${DEVICE_ID:-}"  # если пусто — flutter сам возьмёт первое устройство

# Проверка PNG: первые 8 байт должны быть 89 50 4E 47 0D 0A 1A 0A
is_valid_png() {
  local f=$1
  [[ -s "$f" ]] || return 1
  local sig
  sig=$(xxd -l 8 -p "$f" 2>/dev/null)
  [[ "$sig" == "89504e470d0a1a0a" ]]
}

# Один снимок с тройным fallback + валидацией
shoot() {
  local name=$1
  local out="$SHOT_DIR/$name.png"
  local tmp="$SHOT_DIR/.$name.tmp"

  if [[ "$PLATFORM" == "ios" ]]; then
    xcrun simctl io booted screenshot "$out" 2>/dev/null
    is_valid_png "$out" && { echo "✅ $name (ios simctl)"; return 0; }
    echo "❌ $name — simctl не дал валидный PNG"
    return 1
  fi

  # ANDROID (default)

  # Попытка 1: flutter screenshot — Impeller-safe, снимает с Flutter-стороны
  local dev_arg=""
  [[ -n "$DEVICE_ID" ]] && dev_arg="-d $DEVICE_ID"
  flutter screenshot $dev_arg --type=device -o "$out" >/dev/null 2>&1 || true
  if is_valid_png "$out"; then
    echo "✅ $name (flutter screenshot)"
    return 0
  fi

  # Попытка 2: adb exec-out screencap -p (classic)
  # ВАЖНО: именно exec-out, не `adb shell` — иначе LF→CRLF сломает PNG
  adb ${DEVICE_ID:+-s $DEVICE_ID} exec-out screencap -p > "$tmp" 2>/dev/null
  if is_valid_png "$tmp"; then
    mv "$tmp" "$out"
    echo "✅ $name (adb screencap)"
    return 0
  fi

  # Попытка 3: screencap на устройстве → pull (обходит stdout-искажения)
  adb ${DEVICE_ID:+-s $DEVICE_ID} shell screencap -p /sdcard/_shot.png 2>/dev/null
  adb ${DEVICE_ID:+-s $DEVICE_ID} pull /sdcard/_shot.png "$out" >/dev/null 2>&1
  adb ${DEVICE_ID:+-s $DEVICE_ID} shell rm /sdcard/_shot.png 2>/dev/null
  if is_valid_png "$out"; then
    echo "✅ $name (adb pull)"
    return 0
  fi

  # Полная неудача — оставляем файл для диагностики, но помечаем
  mv "$tmp" "$out.INVALID" 2>/dev/null || true
  echo "❌ $name — все 3 метода вернули невалидный PNG. Проверьте:"
  echo "   - Impeller: перезапустите с --no-enable-impeller"
  echo "   - Экран устройства разблокирован?"
  echo "   - file \"$out.INVALID\" (должно быть PNG image data, не ASCII)"
  return 1
}

# 1. Splash (сразу после запуска — даём 3 сек на первый кадр Flame)
sleep 3 && shoot 01-splash

# 2. Main menu (splash должен авто-перейти)
sleep 3 && shoot 02-menu

# 3. Game screen (тап по кнопке PLAY — нижняя треть)
adb ${DEVICE_ID:+-s $DEVICE_ID} shell input tap 540 2000
sleep 2 && shoot 03-game-idle

# 4. После основного действия (spin/play)
adb ${DEVICE_ID:+-s $DEVICE_ID} shell input tap 540 2000
sleep 3 && shoot 04-game-action
sleep 3 && shoot 05-game-after-action

# 5. Back → menu → settings
adb ${DEVICE_ID:+-s $DEVICE_ID} shell input keyevent KEYCODE_BACK
sleep 1 && shoot 06-back-menu

# 6. Дополнительные экраны (если не --quick)
#   Settings, Help, Paytable, Daily Bonus, Leaderboard, Profile
#   Навигация производится тапами по координатам кнопок меню
# ...
```

**ВАЖНО**: если `--quick`, ограничиться снимками 01–05.

После каждого скриншота сохранить соответствие: какой экран ожидался vs что снято.

### Если все три метода дают невалидный PNG

1. Убедиться что экран устройства **разблокирован** (adb screencap на lock screen иногда возвращает мусор).
2. Перезапустить Flutter с отключённым Impeller:
   ```bash
   flutter run -d "$DEVICE_ID" --no-enable-impeller > .claude/runtime-logs/flutter-run.log 2>&1 &
   ```
3. На Android 14+ бывает, что `screencap` требует разрешения `READ_FRAME_BUFFER` через
   `adb shell settings put global hidden_api_policy 1` — делать только в личном dev-окружении.
4. Диагностика: `file "$SHOT_DIR/*.INVALID"` — если там `ASCII text`, в пайп попала ошибка
   adb (unauthorized / offline / device not found).

---

## Фаза 3 — Visual Analysis [~2 мин]

**КРИТИЧЕСКАЯ фаза.** Здесь мы используем возможность Read смотреть на PNG как на
изображение (multimodal vision).

Для КАЖДОГО скриншота вызвать Read tool:

```
Read file_path=production/runtime-screenshots/<ts>/01-splash.png
```

И визуально проверить по чеклисту:

### Чеклист визуальных проблем (Severity Scale)

| # | Проблема | Как выглядит | Severity | Ответственный агент |
|---|----------|--------------|----------|---------------------|
| V1 | **Flutter red screen of death** | Красный фон с текстом exception и stacktrace | CRITICAL | парсинг logcat → mechanics-programmer или ui-programmer |
| V2 | **Полностью чёрный экран** | Целиком чёрный или тёмный, без контента | CRITICAL | ui-programmer (проверить onLoad, Scaffold, main.dart) |
| V3 | **Полностью белый экран** | Целиком белый, без контента | CRITICAL | ui-programmer (обычно Navigator stuck или missing route) |
| V4 | **Пустой игровой экран** | HUD есть, но область игры (барабаны/сетка/поле) пустая | CRITICAL | mechanics-programmer (компоненты не добавлены в World) |
| V5 | **RenderFlex overflow** | Жёлто-чёрные диагональные полосы на краях | HIGH | ui-programmer (Expanded/Flexible, Text overflow) |
| V6 | **Missing asset placeholder** | Серый прямоугольник с крестом или пустой SVG slot | HIGH | ui-programmer или generate-asset |
| V7 | **Overlapping UI** | Текст/кнопки перекрывают друг друга | HIGH | ui-programmer (layout constraints) |
| V8 | **Text overflow без ellipsis** | Текст обрезан по краю без "..." | MEDIUM | ui-programmer |
| V9 | **Кнопка невидимая/вне экрана** | Нет видимой кнопки действия в game_screen | HIGH | ui-programmer |
| V10 | **Низкий контраст** | Текст сливается с фоном, нечитаемо | MEDIUM | ui-programmer (Design DNA palette) |
| V11 | **Вся графика — дефолтные Material** | Синий AppBar, белые кнопки, generic look | MEDIUM | ui-programmer (нет кастомной темы) |
| V12 | **Баланс/счёт не отображается** | HUD пустой или показывает NaN/null | HIGH | mechanics-programmer (ValueNotifier не подключён) |

### Для каждого скриншота создать запись

```markdown
### 03-game-idle.png
- Expected: главный экран игры с барабанами, HUD сверху, кнопка SPIN снизу
- Observed: [что реально видно]
- Issues:
  - V4 — Область барабанов пустая (чёрный прямоугольник 800x600 в центре)
  - V8 — Текст баланса обрезан: "100..." вместо "1000"
- Severity: CRITICAL
- Suspected cause: ReelComponent не добавлен в world.onLoad() или SymbolComponent
  не загружает SVG ассеты
- File to investigate: lib/game/[name]_world.dart
```

---

## Фаза 4 — Logcat Analysis [~30 сек]

Прочитать `.claude/runtime-logs/logcat.log` и `.claude/runtime-logs/flutter-run.log`.
Извлечь все runtime-exceptions.

### Паттерны для grep

```bash
# Flutter exceptions
grep -A 20 "EXCEPTION CAUGHT" .claude/runtime-logs/flutter-run.log
grep -A 10 "Another exception was thrown" .claude/runtime-logs/flutter-run.log

# Layout errors
grep -B 2 -A 5 "A RenderFlex overflowed" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "unbounded height\|unbounded width" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "BoxConstraints forces an infinite" .claude/runtime-logs/flutter-run.log

# State lifecycle errors
grep -B 2 -A 5 "setState() called after dispose" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "called on a disposed" .claude/runtime-logs/flutter-run.log

# Asset errors
grep -B 2 -A 3 "Unable to load asset" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 3 "Could not find asset" .claude/runtime-logs/flutter-run.log

# Navigation errors
grep -B 2 -A 3 "Could not find a generator for route" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 3 "Navigator operation requested" .claude/runtime-logs/flutter-run.log

# Null/type errors
grep -B 2 -A 5 "Null check operator" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "type '.*' is not a subtype" .claude/runtime-logs/flutter-run.log

# Flame errors
grep -B 2 -A 5 "FlameGame\|PositionComponent" .claude/runtime-logs/flutter-run.log | grep -i "error\|exception"
```

### Классификация ошибок

Каждую пойманную ошибку разметить:
- **file:line** — где произошло (из stacktrace)
- **category** — layout / lifecycle / asset / navigation / null / flame / other
- **fix_owner** — кто чинит (ui-programmer / mechanics-programmer / juice-artist)

---

## Фаза 5 — Auto-Fix Loop [~5 мин, до 3 итераций]

Консолидировать находки из Фазы 3 (visual) и Фазы 4 (logcat) в единый список проблем.
Сортировать по severity: CRITICAL → HIGH → MEDIUM.

### Стратегия исправления

1. **Остановить запущенное приложение** (иначе hot reload создаст шум):
   ```bash
   kill $(cat .claude/runtime-logs/flutter.pid) 2>/dev/null
   kill $(cat .claude/runtime-logs/logcat.pid) 2>/dev/null
   ```

2. **Группировать проблемы по ответственному агенту.**

3. **Запустить агентов параллельно** (каждый получает свой список):

   **ui-programmer**:
   - V2/V3 (чёрный/белый экран): проверить main.dart → runApp, app.dart → routes, SafeArea
   - V5/V7/V8/V9 (layout): добавить Expanded, overflow: ellipsis, FittedBox
   - V10/V11 (design): применить палитру из Design DNA, заменить Material defaults

   **mechanics-programmer**:
   - V4 (пустой игровой экран): проверить [name]_world.dart — onLoad добавляет компоненты,
     компоненты имеют правильные position/size, загружают ассеты
   - V12 (HUD не обновляется): проверить что ValueNotifiers созданы в FlameGame и
     прокинуты в HUD через GameWidget overlayBuilderMap

   **juice-artist** (если упоминается VFX):
   - Particle systems не видны: проверить что ParticleSystemComponent добавлен в World

   **ui-audit skill** (вспомогательно):
   - Если логкат показал много layout errors, запустить `/ui-audit --fix`

4. **После исправлений**:
   ```bash
   dart analyze lib/
   flutter test
   ```
   Если это ломает компиляцию или тесты — откатить некритичные правки, оставить только те,
   что чинят CRITICAL/HIGH.

5. **Re-run цикла** (с Фазы 1): заново запустить игру, сделать скриншоты, сравнить.
   Если количество CRITICAL проблем уменьшилось — продолжаем. Если нет прогресса 2 итерации
   подряд — остановиться и отчитаться пользователю.

### Критерии выхода Фазы 5

**Успех**: 0 CRITICAL, ≤2 HIGH, MEDIUM — допустимы.
**Частичный успех**: CRITICAL устранены, HIGH остались — отчитаться пользователю.
**Неудача**: CRITICAL остались после 3 итераций — подробный отчёт + ручная эскалация.

---

## Фаза 6 — Report & Artifacts

Создать `production/runtime-screenshots/<timestamp>/REPORT.md`:

```markdown
# Runtime Verification Report — [дата]

## Device
- Platform: Android / iOS
- Device: [model / emulator name]
- Resolution: [WxH]
- Flutter: [version]

## Screens Tested
- [x] Splash → Menu transition
- [x] Main Menu
- [x] Game Screen (idle)
- [x] Game Screen (action in progress)
- [x] Game Screen (after action)
- [ ] Settings (--quick mode: skipped)
- ...

## Issues Found

### Initial run (iteration 1)
- CRITICAL (2):
  - V4 on 03-game-idle.png — reels area is black rectangle. Root cause: ReelComponent not
    added in SlotMachineWorld.onLoad(). Fixed by mechanics-programmer: lib/game/slot_world.dart
  - V2 on 01-splash.png — all-black splash. Root cause: splash_screen.dart did not wrap
    content in Scaffold. Fixed by ui-programmer.
- HIGH (1):
  - V5 on 02-menu.png — RenderFlex overflow bottom 42px. Fixed: wrapped ListView in Expanded.

### Final run (iteration 2) — VERIFIED
- CRITICAL: 0
- HIGH: 0
- MEDIUM: 1 (V11 — menu uses default AppBar color, consider theming)

## Logcat Summary
- Exceptions: 3 (iteration 1) → 0 (iteration 2)
- Warnings: 5 (acceptable)

## Screenshots
- production/runtime-screenshots/<ts>/01-splash.png
- ...

## Verdict
✅ PASS — game runs end-to-end without crashes, all CRITICAL/HIGH issues resolved.
```

Также обновить `production/session-state/active.md`:
```markdown
## Runtime verified
- Date: [дата]
- Device: [устройство]
- Issues fixed: [N]
- Verdict: PASS / CONCERNS / FAIL
- Report: production/runtime-screenshots/<ts>/REPORT.md
```

---

## Фаза 7 — Cleanup

```bash
# Остановить приложение
kill $(cat .claude/runtime-logs/flutter.pid) 2>/dev/null || true
kill $(cat .claude/runtime-logs/logcat.pid) 2>/dev/null || true

# Логи НЕ удалять (могут понадобиться для отладки)
# Скриншоты НЕ удалять (артефакт верификации)

# Опционально: удалить старые раны (оставить последние 5)
ls -1t production/runtime-screenshots/ | tail -n +6 | xargs -I{} rm -rf "production/runtime-screenshots/{}"
```

---

## Integration in /autocreate

Этот навык автоматически запускается из `/autocreate` в **Фазе 10.5** — сразу после
`Фаза 10 Crash Prevention` и до `Фаза 11 Session State Update`.

В `/autocreate` используется режим **`--quick`** (только главные экраны) чтобы уложиться
в бюджет времени. Если есть критические проблемы — запускается полный режим.

---

## Quality Gates

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 0. Preflight | Устройство доступно | 1 (иначе abort) |
| 1. Build | `flutter run` не падает, приложение запущено | 3 |
| 2. Screenshots | Минимум 5 снимков сделано | 2 |
| 3. Visual Analysis | Все снимки проанализированы | 1 |
| 4. Logcat | Лог прочитан, ошибки классифицированы | 1 |
| 5. Auto-Fix | 0 CRITICAL | 3 |
| 6. Report | REPORT.md создан | 1 |
| 7. Cleanup | Процессы остановлены | 1 |

---

## Запрещено в этом навыке

1. Изменять `pubspec.yaml` зависимости во время auto-fix (это задача основного пайплайна)
2. Запускать эмулятор с `-wipe-data` — пользователь может потерять state других приложений
3. Использовать `adb root` или `adb shell su` — не требуется и небезопасно
4. Удалять скриншоты или логи до окончания отчёта
5. Делать git commit автоматически — только пользователь решает

---

## Аргументы

- `--device <id>` — конкретный `flutter devices` ID (по умолчанию: первое Android-устройство из `adb devices`)
- `--platform android|ios` — форсировать платформу. **Default: `android`** (через ADB + `flutter screenshot`).
- `--no-fix` — только анализ и отчёт, без исправлений
- `--quick` — сокращённый тур (splash → menu → game → action)
- `--skip-logcat` — пропустить парсинг logcat (полезно для iOS где logcat недоступен)
- `--no-impeller` — запустить `flutter run` с `--no-enable-impeller`. Используйте, если
  первый прогон дал `.INVALID` PNG: `adb screencap` часто не видит Impeller surface.
