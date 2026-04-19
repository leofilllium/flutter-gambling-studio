---
name: autocreate
description: "Фабрика производства ПОЛНЫХ мини-игр Zero-to-Production (любой жанр). Создает концепт, генерирует ВСЕ SVG ассеты с валидацией, пишет полный код на Flutter/Flame 1.18.x со ВСЕМИ экранами (12+), реализует ВСЮ игровую логику, пишет и запускает тесты, проводит UI/UX аудит, проверяет баланс, фиксит ВСЕ ошибки. Результат — полностью рабочее приложение без крашей."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Production Complete Game Factory

Выполняет ПОЛНЫЙ цикл разработки мини-игры до production-ready состояния.
**Результат: полностью рабочее Android-приложение, которое компилируется, запускается и НЕ КРАШИТСЯ.**

**ЗАПРЕЩАЕТСЯ задавать вопросы (кроме выбора формата ассетов в Фазе 3).**

---

## 🚨 MANDATORY EXECUTION CONTRACT (читать до начала работы)

`/autocreate` — это **полный конвейер Zero-to-Android-APK**, но он разбит на
ДВЕ context-сессии во избежание истощения токенов:

- **Часть 1 (эта conversation, Фазы 1 → 10)** — концепт, ассеты, код, `dart analyze`
  чистый, `flutter test` зелёный, UI-аудит, баланс, crash-prevention. Выполняется
  в основном контексте.
- **Часть 2 (свежий subagent, Фазы 10.5 → 12)** — runtime emulator verification,
  release-package (APK + screenshots + tar.gz), финальный отчёт. Запускается
  ТОЛЬКО через Agent tool с subagent_type="general-purpose" (чистый контекст).

**Часть 1 ОБЯЗАНА передать управление Части 2 через Agent tool в конце Фазы 10.**
Она НЕ выполняет Фазы 10.5/10.6 сама. Subagent получает путь к handoff-файлу
`production/session-state/autocreate-handoff.md` и инструкцию следовать
`.claude/skills/autocreate-finalize/SKILL.md`.

**Основная целевая платформа: Android.** iOS/Web поддерживаются как дополнительные.
Финальный артефакт (создаётся Частью 2) — release APK, упакованный в `.tar.gz`
в `project_zip/`.

### Что ОБЯЗАНО произойти в Части 1 (эта сессия, Фазы 1–10):

1. ✅ **Flutter Android-проект создан с нуля** (`flutter create --platforms android`)
2. ✅ **Все ассеты сгенерированы** (SVG по умолчанию, путь в `lib/assets.dart`)
3. ✅ **Вся игровая логика написана** (4 параллельных агента)
4. ✅ **`dart analyze lib/` → 0 errors** (цикл исправлений, до 10 итераций)
5. ✅ **`flutter test` → все зелёные** (до 5 итераций)
6. ✅ **UI/UX аудит (60+ проверок) с автофиксами**
7. ✅ **Balance check (RTP/difficulty) в допустимом диапазоне**
8. ✅ **Crash-prevention аудит (20 пунктов)**
9. ✅ **Handoff-файл записан** в `production/session-state/autocreate-handoff.md`
10. ✅ **Subagent запущен через Agent tool** для Части 2

### Что ОБЯЗАН выполнить subagent Части 2 (Фазы 10.5–12):

11. ✅ **Android эмулятор: приложение запущено, скриншоты, логи разобраны**
12. ✅ **Все CRITICAL баги со скриншотов исправлены** (auto-fix loop, до 3 итераций)
13. ✅ **Финальные скриншоты ГОТОВОЙ игры** (до 16 снимков)
14. ✅ **Release APK собран** (`flutter build apk --release`)
15. ✅ **`flutter clean` выполнен** (после сборки APK, не до)
16. ✅ **Весь проект + APK + скриншоты упакованы в `project_zip/<name>-<ts>.tar.gz`**

### Запрещено в Части 1:

- ❌ Пытаться выполнить Фазу 10.5 (emulator-test) в основной conversation
- ❌ Пытаться выполнить Фазу 10.6 (release-package) в основной conversation
- ❌ Вызывать `flutter run`, `flutter build apk`, `adb shell`, `emulator`
  в основной conversation — это задачи subagent-а
- ❌ Делать stub-файлы или TODO-комментарии в production коде
- ❌ Отчитываться об успехе Части 1, если `dart analyze lib/` не 0 errors
  или `flutter test` красный
- ❌ Рапортовать "игра готова" — RUNTIME ещё не проверен (это делает Часть 2)

### Запрещено в Части 1 НЕ делать (обязательное):

- ✅ В конце Фазы 10 ОБЯЗАТЕЛЬНО вызвать Agent tool — без этого конвейер
  считается НЕЗАВЕРШЁННЫМ, independent от того, что `dart analyze` чист

### Финальный критерий успеха всего конвейера:

`ls project_zip/` показывает `<name>-<ts>.tar.gz` размером > 1 MB, И `tar -tzf` на нём
показывает ВНУТРИ архива: `source/` (с `pubspec.yaml`), `apk/app-release.apk`,
`screenshots/*.png` (≥5 если эмулятор был), `RELEASE_INFO.md`.
APK и скриншоты ДОЛЖНЫ быть ВНУТРИ tar.gz, а не рядом с ним.
Если нет — операция ПРОВАЛЕНА, независимо от прогресса ранних фаз.

---

> **ANTI-SLOP**: Каждый экран и виджет — craft-level дизайн.
> Прочитайте `.claude/rules/anti-slop-design.md` перед началом работы.

> **КЛЮЧЕВОЕ ОТЛИЧИЕ ОТ MVP**: Это НЕ прототип. Это полная игра:
> - ВСЯ игровая логика работает (спины крутятся, очки считаются, уровни переключаются)
> - ВСЕ экраны связаны навигацией и данными
> - ВСЕ ассеты подключены и отображаются
> - ВСЕ кнопки реагируют на нажатия с правильными состояниями
> - ВСЕ анимации проигрываются
> - Приложение НЕ крашится ни при каком сценарии использования
> - Тесты написаны и проходят

---

## Фаза 1 — Идея (Auto-Concept) [~2 мин]

Вызов логики `/auto-idea` для генерации концепции (пропустить если `--from-concept`).
Сохранение в `design/gdd/game-concept.md`.

**ВАЖНО**: Концепт ОБЯЗАН включать:
- **Screen Map** — минимум 12 экранов с ПОЛНЫМ описанием каждого
- **Data Flow** — как данные перетекают между экранами (ValueNotifiers, callbacks)
- **Complete Game Loop** — полный цикл игры от старта до конца
- **All Edge Cases** — что происходит при нулевом балансе, макс выигрыше, паузе, и т.д.

---

## Фаза 2 — Flutter Project Bootstrap [~1 мин]

**Целевая платформа — Android (primary).** iOS и Web — опциональные.

```bash
# ОБЯЗАТЕЛЬНО: Android должен быть первым в списке платформ
flutter create . --project-name game_app --platforms android,ios,web --org com.gamestudio

# Проверка что Android-директория создана
if [[ ! -d android/app ]]; then
  echo "❌ Android-проект не создан — критическая ошибка, прекращаем"
  exit 1
fi

# Проверка минимального SDK для современного Flame 1.18.x
# android/app/build.gradle должен иметь minSdkVersion >= 21
```

Обновление `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  flame: ^1.18.0
  flame_audio: ^2.1.0
  flame_svg: ^1.10.0
  google_fonts: ^6.1.0
  shared_preferences: ^2.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0

flutter:
  assets:
    - assets/images/sprites/
    - assets/images/ui/
    - assets/images/backgrounds/
    - assets/audio/sfx/
  fonts:
    - family: Orbitron
      fonts:
        - asset: assets/fonts/Orbitron-Regular.ttf
        - asset: assets/fonts/Orbitron-Bold.ttf
          weight: 700
    - family: Rajdhani
      fonts:
        - asset: assets/fonts/Rajdhani-Regular.ttf
        - asset: assets/fonts/Rajdhani-Bold.ttf
          weight: 700
```

Скачать Google Fonts в `assets/fonts/` через curl.
Создать ВСЕ необходимые директории:
```bash
mkdir -p assets/images/sprites assets/images/ui assets/images/backgrounds assets/audio/sfx assets/fonts design/gdd design/balance
```

**ОБЯЗАТЕЛЬНО**: после `flutter pub get` убедиться что нет ошибок зависимостей.

---

## Фаза 3 — Asset Generation & Validation [~5 мин]

### Выбор формата ассетов (ЕДИНСТВЕННЫЙ вопрос пользователю)

> "Выберите формат игровых ассетов:
>
> **1. SVG** (по умолчанию) — векторный, мгновенно
> **2. PNG** — через Google AI Studio (Imagen API), нужен ключ
>
> Введите 1 или 2 (Enter = SVG):"

### SVG Генерация (режим по умолчанию)

**КРИТИЧЕСКИ**: Каждый SVG ОБЯЗАН быть валидным и отрисовываемым.

#### Спрайты (`assets/images/sprites/`)
- Минимум 5-8 игровых элементов (символы для слота, тайлы для match-3, и т.д.)
- Каждый: 96x96 SVG с `viewBox="0 0 96 96"`
- Обязательны градиенты (`<linearGradient>` / `<radialGradient>`) для объёма
- НЕ плоские иконки — тени, блики, детали
- Единый стиль освещения (45 градусов сверху-слева)

#### UI Elements (`assets/images/ui/`)
- `ui_spin_button.svg` — кастомная форма (трапеция / скос)
- `ui_frame.svg` — рамка игрового поля
- `ui_bet_panel.svg` — панель ставок
- `ui_separator.svg` — декоративный разделитель
- `ui_icon_sound.svg` — иконка звука
- `ui_icon_settings.svg` — иконка настроек
- `ui_icon_info.svg` — иконка помощи

#### Фоны (`assets/images/backgrounds/`)
- `background_menu.svg` — фон меню (с паттерном / градиентом)
- `background_game.svg` — фон игрового экрана (текстурированный)

### Post-Generation Validation

**ОБЯЗАТЕЛЬНО** после генерации всех SVG:
1. Проверить что каждый файл начинается с `<svg` и содержит `</svg>`
2. Проверить что `viewBox` определён в каждом файле
3. Проверить что все файлы, указанные в коде (`lib/assets.dart`), физически существуют
4. Запустить `flutter pub get` для валидации путей ассетов

### PNG Генерация (если выбран)

Следовать логике `/generate-png-asset --from-concept`.

---

## Фаза 4 — Complete Game Implementation (FOUR parallel agents) [~15 мин]

> **КЛЮЧЕВОЕ ПРАВИЛО**: Каждый агент получает ПОЛНЫЙ концепт из `design/gdd/game-concept.md`
> и ПОЛНЫЙ список ассетов. Агенты ОБЯЗАНЫ использовать ОДИНАКОВЫЕ имена классов, типы и интерфейсы.

### Контракт между агентами (определить ДО запуска)

Перед запуском агентов, создать файл контракта `lib/contracts.md` (временный, удалить в конце):

```markdown
## Shared Types
- GameState sealed class: IdleState, PlayingState, AnimatingState, WinState, GameOverState, PausedState
- ValueNotifiers: balance (int), bet (int), isSpinning/isPlaying (bool), score (int), currentState (GameState)
- Game class name: [GameName]Game extends FlameGame
- World class name: [GameName]World extends World with HasCollisionDetection
- Config class name: GameConfig (static constants)

## File Paths (EXACT)
- Game: lib/game/[name]_game.dart, lib/game/[name]_world.dart
- Config: lib/game/game_config.dart
- State: lib/models/game_state.dart
- Assets helper: lib/assets.dart
- Theme: lib/theme/game_theme.dart
- Animations: lib/theme/animations.dart
```

### Agent A — mechanics-programmer (Core Game Logic):

**Prompt ОБЯЗАН включать**: Полный концепт, контракт типов, список ассетов.

Создаёт ВСЮ рабочую игровую логику:

- `lib/game/[name]_game.dart` — FlameGame с ПОЛНОЙ инициализацией
  - Создаёт World, Camera, все ValueNotifiers
  - Методы: startGame(), performAction() (spin/move/tap), pause(), resume()
  - Обработка всех GameState переходов
  - Подключение к overlays для Flutter UI
- `lib/game/[name]_world.dart` — World с HasCollisionDetection
  - Все игровые компоненты добавляются здесь
  - Метод reset() для перезапуска
- `lib/game/game_config.dart` — ВСЕ константы без исключения
  - Размеры, скорости, множители, тайминги, лимиты
  - Пороги для Small/Big/Mega Win
  - Минимальная/максимальная ставка
  - Начальный баланс
- `lib/systems/` — вся логика по жанру:
  - **Gambling**: `weighted_rng.dart` (Random.secure()), `payline_evaluator.dart`
  - **Puzzle**: `match_detector.dart`, `cascade_system.dart`
  - **Arcade**: `spawn_manager.dart`, `collision_handler.dart`
  - **Physics**: `physics_world.dart`
- `lib/models/game_state.dart` — sealed class со ВСЕМИ состояниями
- `lib/models/` — все модели данных (символы, тайлы, враги, и т.д.)
- `lib/components/` — ВСЕ Flame компоненты:
  - Основной игровой компонент (ReelComponent / GridComponent / PlayerComponent)
  - Элементы (SymbolComponent / TileComponent / ObstacleComponent)
  - Управление (touch/tap handlers)
  - Все компоненты ОБЯЗАНЫ иметь onLoad(), update(dt), и правильную очистку в onRemove()

**КРИТИЧЕСКИ для Agent A**:
- Результат действия вычисляется ДО анимации (Stateless Outcomes)
- GameState transitions ОБЯЗАНЫ быть полными (нельзя застрять в состоянии)
- update() и render() — ТОЛЬКО синхронные, нет await
- Нет аллокаций в update() — прединициализация Vector2, Paint, Rect
- Gambling: ТОЛЬКО Random.secure(), никаких захардкоженных вероятностей
- Все параметры берутся из GameConfig

### Agent B — ui-programmer (Complete UI):

**Prompt ОБЯЗАН включать**: Полный концепт с Screen Map, Design DNA, контракт типов, ПОЛНЫЙ список ассетов.

Создаёт ВСЕ экраны и виджеты (ПОЛНОСТЬЮ РАБОЧИЕ, не заглушки):

**Обязательные файлы:**

**Тема и утилиты:**
- `lib/theme/game_theme.dart` — ПОЛНАЯ кастомная тема
  - Палитра из 5 цветов (из Design DNA)
  - TextTheme с 2 шрифтами (Orbitron + Rajdhani)
  - ButtonTheme с кастомными формами
  - CardTheme, DialogTheme, AppBarTheme
- `lib/theme/animations.dart` — ВСЕ тайминги централизованы
  - Durations: fast (150ms), medium (300ms), slow (600ms), screenTransition (400ms)
  - Curves: для кнопок, для экранов, для чисел, для партиклей
- `lib/assets.dart` — типизированные пути к КАЖДОМУ ассету

**Экраны (КАЖДЫЙ полностью реализован, не stub):**
- `lib/screens/splash_screen.dart` — анимированный логотип → авто-переход на меню
- `lib/screens/main_menu.dart` — фон с партиклями/анимацией, кнопка ИГРАТЬ (пульсация), Settings, Help, Daily Bonus, Leaderboard, Profile
- `lib/screens/game_screen.dart` — GameWidget обёртка + HUD overlay + Win overlays + Game Over overlay
- `lib/screens/hud_widget.dart` — ValueListenableBuilder для баланса (animated counter), ставки, кнопки действия (с блокировкой)
- `lib/screens/paytable_screen.dart` — SVG символы с описанием выплат / правилами (скролл или PageView)
- `lib/screens/settings_screen.dart` — Sound on/off, SFX on/off, Vibration toggle (SharedPreferences)
- `lib/screens/help_screen.dart` — пошаговое руководство с иллюстрациями
- `lib/screens/daily_bonus_screen.dart` — механика ежедневного бонуса (мини-рулетка или сундуки, SharedPreferences для even tracking)
- `lib/screens/leaderboard_screen.dart` — список лучших результатов (SharedPreferences)
- `lib/screens/profile_screen.dart` — аватар (выбор из 6+), никнейм (TextField), статистика
- `lib/screens/win_overlay.dart` — 3 уровня с разными эффектами:
  - Small: toast снизу + animated counter + auto-dismiss 2s
  - Big: полу-экранный + конфетти + 3s
  - Mega: fullscreen + explosion + camera shake + 4s
- `lib/screens/insufficient_funds_dialog.dart` — Glassmorphism модал (BackdropFilter)
- `lib/screens/bonus_overlay.dart` — оверлей бонусного режима (Free Spins / Special Mode)

**Виджеты (КАЖДЫЙ с анимациями и состояниями):**
- `lib/widgets/animated_counter.dart` — плавное изменение чисел (Tween)
- `lib/widgets/glow_button.dart` — кнопка с glow пульсацией (idle/hover/tap/disabled)
- `lib/widgets/skewed_button.dart` — кнопка с ClipPath (4 состояния)
- `lib/widgets/neon_text.dart` — текст с Shadow glow
- `lib/widgets/pulsating_widget.dart` — idle пульсация для любого child
- `lib/widgets/game_loading.dart` — тематический загрузчик (НЕ CircularProgressIndicator)
- `lib/widgets/glassmorphism_container.dart` — переиспользуемый контейнер с BackdropFilter

**Маршрутизация:**
- `lib/app.dart` — MaterialApp с именованными routes:
  ```
  /splash → /menu → /game → (overlays через Flame)
                   → /settings
                   → /help
                   → /paytable
                   → /daily-bonus
                   → /leaderboard
                   → /profile
  ```
- `lib/main.dart` — runApp(const GameApp())

**КРИТИЧЕСКИ для Agent B — CRASH PREVENTION (читай `.claude/rules/ui-code.md`):**

**Layout safety (предотвращение RenderFlex overflow):**
- КАЖДЫЙ ListView/GridView внутри Column ОБЯЗАН быть в `Expanded`
- НЕТ `Expanded` внутри `SingleChildScrollView` (не работает!)
- КАЖДЫЙ динамический Text с `overflow: TextOverflow.ellipsis, maxLines: 1` или в FittedBox
- КАЖДЫЙ Image/SvgPicture с явными width + height
- КАЖДЫЙ экран обёрнут в SafeArea (кроме GameScreen)

**Widget lifecycle (предотвращение setState after dispose):**
- КАЖДЫЙ setState в Future/Timer/callback — `if (!mounted) return;` ПЕРЕД setState
- КАЖДЫЙ AnimationController — `dispose()` в `dispose()`
- КАЖДЫЙ Timer — `cancel()` в `dispose()`
- КАЖДЫЙ ScrollController, TextEditingController — `dispose()` в `dispose()`

**Navigation (предотвращение route crashes):**
- ВСЕ pushNamed маршруты определены в routes: map в app.dart
- Splash → Menu через `pushReplacementNamed` (не push!)
- Navigator.pop — только с `if (Navigator.canPop(context))`
- PopScope на КАЖДОМ экране для Back button
- `onUnknownRoute` определён в MaterialApp как fallback

**Interaction (предотвращение UX багов):**
- Кнопка действия: debounce 300ms + isPlaying check + 3 визуальных состояния
- Ставка блокируется во время действия (IgnorePointer)
- КАЖДАЯ кнопка с visual feedback (AnimatedScale при нажатии)
- Tap target >= 48x48 на все кнопки
- Insufficient Funds проверяется перед действием

**Functional completeness (НЕТ заглушек):**
- Если экран существует — он ПОЛНОСТЬЮ реализован
- Settings: SharedPreferences load + save (try-catch)
- Daily Bonus: DateTime check через SharedPreferences
- Leaderboard: реальные данные из SharedPreferences
- Profile: nickname + avatar сохраняются
- Win overlay: 3 уровня (small/big/mega) с auto-dismiss

### Agent C — juice-artist (VFX & Animations):

Создаёт ВСЕ визуальные эффекты (рабочие, подключённые):

- `lib/components/win_animation.dart` — ParticleSystemComponent для 3 уровней выигрыша
- `lib/components/action_vfx.dart` — эффекты основного действия (spin trail, cascade glow, и т.д.)
- `lib/components/payline_overlay.dart` — визуализация выигрышных линий (gambling)
- `lib/components/ambient_particles.dart` — фоновые частицы (звёзды, искры, пыль)
- `lib/components/screen_shake.dart` — camera shake для mega win
- Анимации кнопки действия: press scale 0.92 → release scale 1.0 + glow flash
- Idle-анимации: символы медленно покачиваются, glow пульсирует

**КРИТИЧЕСКИ для Agent C:**
- Все VFX ОБЯЗАНЫ быть подключены к реальным игровым событиям
- Particle count НЕ превышает GameConfig.maxParticles (200)
- Нет аллокаций в update() — прединициализация
- lifespan частиц конечен — нет утечек

### Agent D — sound-designer (Audio Events):

Создаёт аудио-систему:

- `lib/audio/audio_service.dart` — полный сервис:
  - BGM: loop фоновой музыки (с fade in/out)
  - SFX: действие (spin start, spin stop, tap, match, collision)
  - Win: 3 уровня (small ding, big fanfare, mega explosion)
  - UI: button tap, navigation swish, error buzz
  - Проверка Settings (sound on/off) перед каждым воспроизведением
  - Максимум 3 параллельных звука
- `lib/audio/audio_assets.dart` — константы путей аудио

**Примечание**: Если реальные .ogg файлы недоступны, AudioService ОБЯЗАН gracefully handle
отсутствие файлов (try-catch, не крашить). Логирование через Logger, не print().

---

## Фаза 5 — Deep Integration & Wiring [~5 мин]

**ЭТО САМАЯ ВАЖНАЯ ФАЗА.** Большинство крашей происходит из-за плохой интеграции.

### 5.1 — Файл ассетов
Создать / обновить `lib/assets.dart`:
```dart
class GameAssets {
  // Sprites
  static const String spriteCherry = 'assets/images/sprites/sprite_cherry.svg';
  // ... ВСЕ ассеты с ТОЧНЫМИ путями к существующим файлам

  // Validate all assets exist (вызвать в debug mode)
  static List<String> get all => [spriteCherry, ...];
}
```

### 5.2 — Проверка связей
ОБЯЗАТЕЛЬНО прочитать и проверить:

1. **main.dart → app.dart**: `runApp(const GameApp())` вызывается
2. **app.dart → routes**: ВСЕ именованные routes определены и ведут на реальные экраны
3. **game_screen.dart → Game class**: GameWidget правильно создаёт игру, передаёт overlays
4. **Game class → ValueNotifiers → HUD**: ValueNotifiers создаются в Game, передаются в HUD
5. **Game class → VFX**: win_animation и другие VFX подключены к событиям
6. **Game class → Audio**: AudioService вызывается при правильных событиях
7. **Settings → SharedPreferences**: Настройки сохраняются И загружаются
8. **Win Overlay → Game Screen**: показывается через Flame overlays или Navigator
9. **Insufficient Funds → Game Screen**: вызывается при balance < bet
10. **Daily Bonus → SharedPreferences**: дата проверяется, бонус начисляется
11. **Leaderboard → SharedPreferences**: результаты записываются и читаются
12. **Profile → SharedPreferences**: данные сохраняются

### 5.3 — Исправление несоответствий между агентами
Типичные проблемы:
- Agent A назвал класс `SlotGame`, Agent B ожидает `SlotMachineGame` → исправить
- Agent A создал ValueNotifier<int>, Agent B ожидает ValueNotifier<double> → привести к единому типу
- Agent C создал VFX компонент, но Agent A не добавляет его в World → добавить
- Пути ассетов в коде не совпадают с реальными файлами → исправить

### 5.4 — pubspec.yaml финализация
- Все папки с ассетами перечислены в `flutter.assets`
- Все шрифты перечислены в `flutter.fonts`
- Нет дублирующихся зависимостей

---

## Фаза 6 — Build & Fix (Strict Loop) [~5 мин]

**ОБЯЗАТЕЛЬНО выполнить полный цикл `dart analyze` → исправление → повтор.**
Нельзя останавливаться на первой ошибке или считать "в целом зелёно".

```bash
flutter pub get
dart analyze lib/ --fatal-infos
```

### Цикл исправлений (до 10 итераций):

**Итерация N:**
1. `dart analyze lib/` → собрать ВСЕ ошибки
2. Исправить ВСЕ ошибки (не по одной, а ВСЕ сразу)
3. Повторить анализ

**Типичные ошибки после параллельной генерации:**
- Missing imports → добавить
- Undefined class/method → проверить контракт, исправить имя
- Type mismatch → привести к единому типу
- Missing required parameters → добавить
- Unused imports → удалить
- Override method signature mismatch → исправить сигнатуру

**Критерий выхода:** `dart analyze lib/` показывает 0 errors.
Warnings допустимы, но не info about unused variables (удалить их).

---

## Фаза 7 — Test Suite Generation & Execution [~8 мин]

**НОВАЯ ФАЗА. Тесты ОБЯЗАТЕЛЬНЫ, не опциональны.**

Запустить агент qa-tester для создания полного набора тестов:

### 7.1 — Unit Tests

**`test/systems/`** — тесты логики:

Для Gambling:
- `weighted_rng_test.dart` — дистрибуция символов (100K итераций, ±5%)
- `payline_evaluator_test.dart` — все комбинации выигрышей + edge cases
- Проверка что Random.secure() используется (чтение исходника)

Для Puzzle:
- `match_detector_test.dart` — горизонтальные, вертикальные, L-shape совпадения
- `cascade_system_test.dart` — заполнение пустот, chain cascades

Для Arcade:
- `spawn_manager_test.dart` — корректность spawn intervals
- `collision_handler_test.dart` — все типы коллизий

Для Physics:
- `physics_world_test.dart` — объекты не проваливаются, отскоки корректны

### 7.2 — Model Tests

**`test/models/`**:
- `game_state_test.dart` — все переходы между состояниями
- `game_config_test.dart` — все константы имеют разумные значения

### 7.3 — Integration Tests (Game Flow)

**`test/game/`**:
- `game_flow_test.dart`:
  - Игра инициализируется без ошибок
  - Основное действие (spin/move/tap) работает
  - Баланс / счёт обновляется корректно
  - GameState возвращается в Idle после каждого действия
  - 100 последовательных действий без ошибок (state leakage test)
  - Пауза и возобновление работают

### 7.4 — Edge Case Tests

**`test/edge_cases/`**:
- Нулевой баланс → действие блокируется
- Быстрый двойной клик → второй игнорируется
- Ставка > баланса → показывает insufficient funds
- Максимальная ставка на минимальном балансе

### 7.5 — Запуск тестов

```bash
flutter test --reporter expanded
```

**Цикл**: если тесты падают → исправить КОД (не тесты, если тесты верны) → перезапустить.
До 5 итераций исправлений.

**Критерий выхода**: ВСЕ тесты зелёные (passed).

---

## Фаза 8 — Deep UI/UX Audit & Auto-Fix [~8 мин]

**ЭТО КРИТИЧЕСКАЯ ФАЗА. Большинство багов — UI/UX ошибки.**

Прочитать ВСЕ файлы в `lib/screens/`, `lib/widgets/`, `lib/theme/`, `lib/app.dart`.
Провести полный аудит по 7 категориям (60+ проверок) из `.claude/skills/ui-audit/SKILL.md`.

### 8.1 — КРАШ-УЯЗВИМОСТИ (исправлять ПЕРВЫМИ!)

| # | Проверка | Как найти | Автофикс |
|---|----------|-----------|----------|
| A1 | **RenderFlex overflow** | Column/Row с ListView/GridView без Expanded | Обернуть scroll-виджет в `Expanded` |
| A2 | **ListView в Column** | `ListView` внутри `Column` без `Expanded` | Обернуть в `Expanded` |
| A3 | **setState after dispose** | `setState` в Future/Timer/callback без `if (!mounted) return;` | Добавить mounted check |
| A4 | **AnimationController без dispose** | StatefulWidget с AnimationController, нет dispose() | Добавить `controller.dispose()` в `dispose()` |
| A5 | **Timer без cancel** | `Timer.periodic` без `cancel()` в `dispose()` | Добавить cancel |
| A6 | **Navigator.pop без canPop** | `Navigator.pop(context)` без проверки | Добавить `if (Navigator.canPop(context))` |
| A7 | **Отсутствующий ассет** | Пути в коде vs реальные файлы в `assets/` | Создать файл или исправить путь |
| A8 | **Шрифт не зарегистрирован** | fontFamily в коде vs fonts в pubspec.yaml | Добавить в pubspec |
| A9 | **Expanded в SingleChildScrollView** | `Expanded` внутри `SingleChildScrollView` — не работает | Убрать Expanded, использовать фиксированный/intrinsic размер |
| A10 | **Missing Key на списках** | `ListView.builder` без `key:` на children | Добавить `ValueKey` |

### 8.2 — LAYOUT БЕЗОПАСНОСТЬ

| # | Проверка | Автофикс |
|---|----------|----------|
| B1 | SafeArea на КАЖДОМ экране (кроме GameScreen) | Обернуть в SafeArea |
| B2 | Нет фиксированных px для layout (>100px) | Заменить на MediaQuery / LayoutBuilder |
| B3 | Каждый динамический Text с overflow handling | Добавить `overflow: TextOverflow.ellipsis, maxLines:` |
| B4 | TextField внутри ScrollView (для клавиатуры) | Обернуть в SingleChildScrollView |
| B5 | Scaffold на каждом экране | Обернуть в Scaffold |
| B6 | Image/SVG с width + height | Добавить размеры |
| B7 | Нет вложенных scroll (или shrinkWrap на внутреннем) | Добавить shrinkWrap + NeverScrollableScrollPhysics |
| B8 | Контент адаптируется к маленьким экранам (< 640px height) | Добавить scroll или адаптивный layout |

### 8.3 — НАВИГАЦИЯ И СОСТОЯНИЕ

| # | Проверка | Автофикс |
|---|----------|----------|
| C1 | ВСЕ pushNamed маршруты определены в app.dart routes | Добавить недостающие routes |
| C2 | Back button обработан (PopScope) на каждом экране | Добавить PopScope |
| C3 | Splash → Menu через pushReplacementNamed (не push) | Заменить на pushReplacement |
| C4 | Splash имеет авто-переход (Timer/Future.delayed) | Добавить таймер |
| C5 | Flame overlays закрываются по таймеру + тапу | Добавить auto-dismiss |
| C6 | Settings сохраняются в SharedPreferences | Добавить persistence |
| C7 | Settings применяются (sound toggle → AudioService) | Добавить проверку |
| C8 | Daily Bonus проверяет дату | Добавить date check |
| C9 | Leaderboard обновляется при новом highscore | Добавить запись |
| C10 | Profile сохраняет nickname/avatar | Добавить persistence |
| C11 | onUnknownRoute определён в MaterialApp | Добавить fallback |

### 8.4 — КНОПКИ И ВЗАИМОДЕЙСТВИЕ

| # | Проверка | Автофикс |
|---|----------|----------|
| D1 | Кнопка действия: debounce 300ms + isPlaying check | Добавить защиту |
| D2 | Кнопка действия: 3 визуальных состояния (idle/press/disabled) | Добавить анимацию |
| D3 | Bet блокирован во время действия (IgnorePointer или disabled) | Добавить блокировку |
| D4 | КАЖДАЯ кнопка с visual feedback (scale/opacity при нажатии) | Добавить AnimatedScale |
| D5 | Tap target >= 48x48 на все кнопки | Обернуть в SizedBox(48) |
| D6 | Insufficient Funds проверяется перед действием | Добавить if (balance < bet) |
| D7 | Пустые состояния (empty list) стилизованы | Добавить EmptyStateWidget |
| D8 | Win overlay: 3 уровня (small/big/mega) | Добавить switch по multiplier |
| D9 | Win overlay: auto-dismiss + tap-to-dismiss | Добавить Timer + GestureDetector |
| D10 | Числа (баланс/счёт) анимируются через AnimatedCounter | Обернуть |

### 8.5 — DESIGN INTENT (контекстуальный дизайн)

> Не "всегда neon + trapezoid." А: каждое решение обосновано контекстом ЭТОЙ игры.
> Прочитай Design DNA из `design/gdd/game-concept.md`.

| # | Проверка | Автофикс |
|---|----------|----------|
| E1 | Нет default ThemeData.dark/light без кастомизации | → Кастомная тема из Design DNA |
| E2 | Нет generic CircularProgressIndicator | → Тематический загрузчик (контекст игры) |
| E3 | Нет generic AlertDialog | → Стилизованный диалог (стиль из DNA) |
| E4 | Нет generic MaterialPageRoute | → Тематический PageRouteBuilder |
| E5 | Нет print() | → debugPrint или удалить |
| E6 | Есть animations.dart | Создать если нет |
| E7 | Нет хардкоженных Duration в screens | → AnimationConfig |
| E8 | Цвета из game_theme.dart соответствуют Design DNA | Скорректировать палитру |
| E9 | Шрифты подходят настроению игры | Заменить если generic |
| E10 | Кнопки имеют единый стиль из DNA | Привести к единству |
| E11 | Визуальная консистентность между экранами | Проверить палитру/шрифты/стиль |
| E12 | UI НЕ transferable — уникален для этой игры | Усилить тематическую привязку |

### 8.6 — ЭКРАНЫ (все 12+ существуют и работают)

Проверить что каждый экран из списка Agent B (Фаза 4) существует,
содержит реальный код (не заглушку), подключён к навигации.

### Post-Audit (ОБЯЗАТЕЛЬНО)

```bash
dart analyze lib/
flutter test
```

Если автофиксы сломали компиляцию или тесты → исправить (до 5 итераций).
**Критерий**: 0 errors в analyze + все тесты зелёные.

---

## Фаза 9 — Balance Check (Genre-Specific) [~3 мин]

### Для Gambling жанра:

Создать `tools/simulate_rtp.py`:
```python
# Симуляция 100K спинов для проверки RTP
# Читает веса из design/balance/rtp-config.json
# Выводит: actual RTP, hit rate, max win, volatility
```

Запустить: `python3 tools/simulate_rtp.py 100000`

**Требование**: RTP в диапазоне 93-98% (более широкий для быстрой генерации).
Если RTP вне диапазона → скорректировать веса в `game_config.dart` и `rtp-config.json`.

### Для Puzzle жанра:
- Проверить что difficulty curve растёт плавно
- Проверить что все уровни проходимы

### Для Arcade жанра:
- Проверить что spawn rate не создаёт impossible ситуации
- Проверить что scoring прогрессия мотивирует

Сохранить отчёт в `design/balance/simulation-report.md`.

---

## Фаза 10 — Final Compilation & Crash Prevention [~3 мин]

### 10.1 — Чистая компиляция
```bash
flutter clean
flutter pub get
dart analyze lib/
flutter test
```

ВСЕ команды должны пройти без ошибок.

### 10.2 — Crash Prevention Audit (20 проверок)

Прочитать ключевые файлы и проверить КАЖДЫЙ пункт:

**Dart / Null Safety:**
1. Нет голого `!` без обоснования — все nullable обработаны через `??` или pattern matching
2. Нет `await` в Flame `update()` / `render()` — ТОЛЬКО синхронные

**Widget Lifecycle (САМЫЕ ЧАСТЫЕ КРАШИ):**
3. КАЖДЫЙ `setState` в async контексте имеет `if (!mounted) return;` перед ним
4. КАЖДЫЙ `AnimationController` disposed в `dispose()`
5. КАЖДЫЙ `Timer` / `Timer.periodic` cancelled в `dispose()`
6. КАЖДЫЙ `StreamSubscription` cancelled в `dispose()`
7. КАЖДЫЙ `ScrollController`, `TextEditingController`, `FocusNode` disposed

**Layout (ВТОРОЙ ПО ЧАСТОТЕ):**
8. НЕТ `ListView` / `GridView` внутри `Column` / `Row` без `Expanded`
9. НЕТ `Expanded` / `Flexible` внутри `SingleChildScrollView`
10. КАЖДЫЙ динамический `Text` имеет `overflow:` + `maxLines:` или обёрнут в `FittedBox`/`Flexible`
11. КАЖДЫЙ `Image` / `SvgPicture` имеет `width:` + `height:`
12. SafeArea на каждом экране (кроме fullscreen GameScreen)

**Navigation:**
13. `Navigator.pop` защищён `canPop` проверкой
14. Splash → Menu через `pushReplacementNamed` (не push)
15. ВСЕ маршруты из кода присутствуют в `routes:` map
16. `onUnknownRoute` определён как fallback

**External Resources (try-catch):**
17. SharedPreferences: try-catch вокруг КАЖДОГО вызова (get/set)
18. Audio: try-catch вокруг КАЖДОГО FlameAudio вызова
19. Flame overlay lifecycle: каждый `overlays.add()` имеет соответствующий `overlays.remove()` по таймеру

**Game State:**
20. GameState sealed class не может застрять — каждое состояние имеет transition наружу

Исправить ВСЕ найденные проблемы. Каждый пункт — потенциальный краш.

### 10.3 — Финальная перекомпиляция
```bash
dart analyze lib/
flutter test
```

---

## Фаза 10.7 — Handoff & Subagent Spawn [~1 мин]

**ЭТО ПОСЛЕДНЯЯ ФАЗА ОСНОВНОЙ CONVERSATION.**
Фазы 10.5 (emulator-test), 10.6 (release-package), 11 (session state) и 12
(final report) выполняются в **subagent-е с чистым контекстом**, не здесь.

### 10.7.1 — Запись handoff-файла

Создать `production/session-state/autocreate-handoff.md` со всем контекстом,
необходимым subagent-у:

```markdown
# AutoCreate Handoff — Часть 1 завершена

**Время завершения Части 1**: [ISO timestamp]
**Следующий шаг**: subagent выполняет `.claude/skills/autocreate-finalize/SKILL.md`

## Метаданные игры
- **Название**: [Game Name]
- **Жанр**: [gambling / puzzle / arcade / physics / casual / card]
- **Архетип**: [A-X / Unique]
- **Package name**: com.gamestudio.[name]
- **Пути**:
  - Концепт: `design/gdd/game-concept.md`
  - Баланс: `design/balance/[rtp-config.json или level-config.json]`
  - Главный класс игры: `lib/game/[name]_game.dart`
  - Entry point: `lib/main.dart`

## Статус Части 1 (Фазы 1–10)
- [x] Фаза 1: Концепт сгенерирован
- [x] Фаза 2: Flutter Android проект создан
- [x] Фаза 3: [N] ассетов сгенерированы ([SVG/PNG])
- [x] Фаза 4: 4 агента завершили имплементацию
- [x] Фаза 5: Интеграция проверена
- [x] Фаза 6: `dart analyze lib/` → 0 errors
- [x] Фаза 7: `flutter test` → [N] тестов, все зелёные
- [x] Фаза 8: UI/UX аудит пройден (60+ проверок)
- [x] Фаза 9: Balance check — [RTP XX.X% / difficulty OK]
- [x] Фаза 10: Crash-prevention аудит — 20/20 чистые

## Задачи для Части 2 (subagent выполняет)
- [ ] Фаза 10.5: Runtime emulator verification (скрины + logcat + auto-fix loop)
- [ ] Фаза 10.6: Release package (до 16 скринов + APK + `flutter clean` + `.tar.gz`)
- [ ] Фаза 11: Обновить `production/session-state/active.md`
- [ ] Фаза 12: Финальный отчёт

## Контракт артефактов Части 2 (должны существовать ПОСЛЕ)
- `project_zip/<name>-<ts>.tar.gz` (валидный `tar -tzf`)
- Внутри архива: `source/pubspec.yaml`, `apk/app-release.apk`,
  `screenshots/*.png` (≥5 если был эмулятор), `RELEASE_INFO.md`

## Ссылки на документацию
- Skill Части 2: `.claude/skills/autocreate-finalize/SKILL.md`
- Runtime verification: `.claude/skills/emulator-test/SKILL.md`
- Release packaging: `.claude/skills/release-package/SKILL.md`
```

### 10.7.2 — Spawn subagent через Agent tool

**ОБЯЗАТЕЛЬНО** вызвать Agent tool ИМЕННО ТАК (после записи handoff-файла):

```
Agent(
  subagent_type="general-purpose",
  description="AutoCreate finalize: runtime + package",
  prompt="""
Ты работаешь во 2-й части конвейера /autocreate с чистым контекстом.

КОНТЕКСТ:
- Часть 1 конвейера завершена (dart analyze чист, flutter test зелёный, UI-аудит пройден)
- Handoff-файл: production/session-state/autocreate-handoff.md — прочитай его ПЕРВЫМ
- Твой skill-план: .claude/skills/autocreate-finalize/SKILL.md — прочитай его ВТОРЫМ и выполняй

ТВОИ ЗАДАЧИ (в порядке):
1. Фаза 10.5 — runtime emulator verification (см. .claude/skills/emulator-test/SKILL.md --quick)
   - auto-fix loop до 3 итераций при CRITICAL проблемах
2. Фаза 10.6 — release-package (см. .claude/skills/release-package/SKILL.md)
   - финальные скриншоты + APK + flutter clean + .tar.gz
3. Фаза 11 — обновить production/session-state/active.md
4. Фаза 12 — вернуть финальный отчёт в том формате, что указан в autocreate-finalize/SKILL.md

КРИТЕРИИ УСПЕХА:
- project_zip/<name>-<ts>.tar.gz создан и валиден (tar -tzf проходит)
- Внутри: source/pubspec.yaml, apk/app-release.apk (если build прошёл),
  screenshots/*.png (≥5 если был эмулятор), RELEASE_INFO.md
- Если APK build упал — архив всё равно создаётся с пометкой APK_FAILED

ОГРАНИЧЕНИЯ:
- НЕ переписывай игровой код — Часть 1 уже закончила имплементацию
- Допустимы ТОЛЬКО runtime-автофиксы UI-багов, которые видны на скриншотах
  или в logcat (overflow, setState after dispose, missing asset, null ValueNotifier)
- Не меняй game_config.dart, rtp-config.json — баланс уже утверждён
"""
)
```

### 10.7.3 — Вывод в основную conversation

После возврата subagent-а — в основную сессию сразу вернуть пользователю
**только** результат subagent-а (финальный отчёт Фазы 12). Не дублировать
работу. Если subagent упал — сообщить пользователю точную причину и команду
для ручного перезапуска в новой conversation: `/autocreate-finalize`.

---

## Гарантии качества (Quality Gates)

Каждая фаза имеет критерий выхода. Если критерий не выполнен — фаза повторяется.

### Часть 1 (основная conversation):

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 2. Bootstrap | `flutter pub get` — 0 errors | 3 |
| 3. Assets | Все SVG валидны, все пути существуют | 2 |
| 4. Implementation | Все 4 агента завершены | 1 (но Фаза 6 исправляет) |
| 5. Integration | Все 12 связей проверены | 3 |
| 6. Build | `dart analyze` — 0 errors | 10 |
| 7. Tests | `flutter test` — all passed | 5 |
| 8. UI Audit | 60+ checks passed | 3 |
| 9. Balance | RTP/difficulty в допустимом диапазоне | 3 |
| 10. Crash Prevention | 20/20 checks passed, `dart analyze` + `flutter test` clean | 3 |
| 10.7. Handoff & Spawn | Handoff-файл записан + Agent tool вызван | 1 |

### Часть 2 (subagent, подробности в `.claude/skills/autocreate-finalize/SKILL.md`):

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 10.5. Runtime Emulator | 0 CRITICAL visual issues + 0 FATAL exceptions | 3 (SKIPPED если нет устройств) |
| 10.6. Release Package | `project_zip/<name>-<ts>.tar.gz` + APK ИЛИ ≥5 скриншотов | 2 (non-fatal) |

**АБСОЛЮТНЫЙ МИНИМУМ для Части 1 (без него нельзя звать Часть 2)**:
- `dart analyze lib/` — 0 errors
- `flutter test` — all passed
- 12+ экранов созданы
- Навигация работает между всеми экранами
- Основная игровая механика работает
- Handoff-файл записан и Agent tool вызван

**АБСОЛЮТНЫЙ МИНИМУМ для Части 2 (subagent отчитывается в основную сессию)**:
- **Android release APK собран** (если эмулятор был): `build/app/outputs/flutter-apk/app-release.apk`
- **Финальный архив создан**: `project_zip/<name>-<ts>.tar.gz`, проходит `tar -tzf`
- **Содержимое архива проверено**: есть `source/`, `apk/` (если был build),
  `screenshots/` (если был эмулятор), `RELEASE_INFO.md`
