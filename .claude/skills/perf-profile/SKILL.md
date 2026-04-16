---
name: perf-profile
description: "Профилирует производительность мини-игры и выдает приоритизированные рекомендации по оптимизации."
argument-hint: "[reels|particles|audio|memory|full]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /perf-profile [область]

Запуск: пользователь вызывает `/perf-profile [reels|particles|audio|memory|full]`

## Цель

Структурированное профилирование производительности гемблинг игры.
Находит bottlenecks в game loop, анализирует frame budget, выдаёт приоритизированные
рекомендации по оптимизации.

## Агенты

- `performance-analyst` — основной аналитик
- `lead-programmer` — архитектурные рекомендации

## Порядок выполнения

### Шаг 1: performance-analyst — Baseline audit

Без запуска игры — статический анализ кода:

**Проверка аллокаций в hot path:**
```bash
# Ищем аллокации в update() / render()
grep -n "Vector2(" lib/components/*.dart
grep -n "Paint()" lib/components/*.dart
grep -n "Rect.from" lib/components/*.dart
grep -n "List<" lib/systems/*.dart
```

**Проверка SpriteBatch:**
- Используется ли SpriteBatch для символов барабанов?
- Если > 9 символов на экране без SpriteBatch — это bottleneck

**Проверка партиклей:**
```bash
# Сколько партиклей может быть создано?
grep -n "count:" lib/components/*.dart
grep -n "Particle.generate" lib/components/*.dart
```

**Проверка аудио:**
- Сколько AudioPlayer instances создаётся?
- Используется ли pool или каждый раз новый?

### Шаг 2: Статический анализ — известные паттерны

| Паттерн | Находка | Рекомендация | Приоритет |
|---------|---------|-------------|---------|
| `Vector2()` в update() | Аллокация каждый кадр | Прединициализировать как поле | HIGH |
| `Paint()` в render() | Аллокация каждый кадр | Прединициализировать как поле | HIGH |
| N×SpriteComponent без SpriteBatch | N draw calls | Использовать SpriteBatch | HIGH |
| `Particle.generate(count: >200)` | Overflow бюджета | Ограничить до 200 | MEDIUM |
| `FlameAudio.play()` каждый кадр | Аудио flood | Дебаунс + AudioPool | MEDIUM |
| `setState()` каждый кадр | Flutter rebuild | Использовать ValueNotifier | MEDIUM |
| `onGameResize()` без isMounted | Потенциальный краш | Добавить проверку | LOW |

### Шаг 3: Профилирование (если игра запущена)

```bash
# Запустить в profile mode
flutter run --profile

# Команды для DevTools:
# 1. CPU Profiler → Record → 10 спинов → Stop → Найти топ методов
# 2. Memory → Take snapshot → до и после Free Spins
# 3. Performance → посмотреть worst frames
```

**Целевые метрики:**
| Метрика | Цель | Предупреждение | Критично |
|---------|------|----------------|---------|
| FPS | > 58 | 45–57 | < 45 |
| Worst frame | < 25ms | 25–50ms | > 50ms |
| Память | < 150MB | 150–250MB | > 250MB |

### Шаг 4: Рекомендации

Агент `performance-analyst` создаёт приоритизированный список:

```markdown
## Приоритет HIGH (влияет на gameplay)
1. ReelComponent: аллокация Vector2 в update() → прединициализировать
   Ожидаемый эффект: -2ms per frame
   Файл: lib/components/reel_component.dart:45

## Приоритет MEDIUM (влияет на UX)
2. WinAnimation: 300 партиклей превышают бюджет → ограничить до 200
   Файл: lib/components/win_animation.dart:78

## Приоритет LOW (косметика)
3. HudWidget: избыточные rebuild при каждом кадре
   Файл: lib/screens/hud_widget.dart:23
```

### Шаг 5: Отчёт

Создать `docs/perf-report-YYYY-MM-DD.md`:
```markdown
# Performance Report — [дата]

## Baseline (до оптимизации)
- FPS: XX
- Worst frame: XXms
- Память: XXmb

## Найденные проблемы
[таблица находок]

## Рекомендации
[приоритизированный список]

## После применения рекомендаций (прогноз)
- Ожидаемое улучшение FPS: +N
- Ожидаемое снижение worst frame: -Nms
```

## Аргументы

- `reels` — фокус на производительности барабанов
- `particles` — фокус на партиклях и VFX
- `audio` — фокус на аудио системе
- `memory` — фокус на памяти и утечках
- `full` — полный профиль (по умолчанию)
- `--quick` — только статический анализ, без рекомендаций запуска
