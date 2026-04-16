---
name: tech-debt
description: "Сканирует и ведет реестр технического долга, формирует план его погашения."
argument-hint: "[сканировать|добавить|показать|план]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# /tech-debt [область]

Запуск: пользователь вызывает `/tech-debt [сканировать|добавить|показать|план]`

## Цель

Отслеживает, категоризирует и приоритизирует технический долг в гемблинг игре.
Сканирует код на индикаторы долга, ведёт реестр, рекомендует порядок выплаты.

## Категории технического долга

| Категория | Символ | Примеры |
|-----------|--------|---------|
| CRITICAL (gambling) | 🚨 | math.Random(), захардкоженные RTP |
| Architecture | 🏗️ | неправильное Flame API, нарушение архитектуры |
| Performance | ⚡ | аллокации в update(), нет SpriteBatch |
| Testing | 🧪 | нет тестов для критической логики |
| Documentation | 📝 | нет GDD, нет комментариев |
| Code Quality | 🔧 | TODO без тикетов, magic numbers |

## Команды

### /tech-debt сканировать

Агент `lead-programmer` сканирует весь `lib/`:

```bash
# TODO без тикетов
grep -rn "TODO\|FIXME\|HACK\|XXX" lib/ --include="*.dart"

# Magic numbers (вне конфига)
grep -rn "[^a-zA-Z][0-9]\{2,\}[^0-9]" lib/ --include="*.dart" | grep -v "slot_config\|_test"

# print() statements
grep -rn "^\s*print(" lib/ --include="*.dart" | grep -v "_test"

# Устаревшее Flame API
grep -rn "isPaused\s*=\|HasCollisionDetection" lib/game/ --include="*.dart"

# Нет тестов для критических файлов
for f in lib/systems/*.dart lib/game/slot_config.dart; do
  test_f="test/$(basename ${f%.dart}_test.dart)"
  [ ! -f "$test_f" ] && echo "❌ Нет теста: $f"
done
```

Результат — список находок с файлами и строками.

### /tech-debt добавить

Добавить запись в реестр долга `docs/tech-debt-register.md`:
```
/tech-debt добавить "Описание долга"
```

### /tech-debt показать

Показать текущий реестр `docs/tech-debt-register.md` с группировкой по приоритету.

### /tech-debt план

Создать план выплаты долга — с какого начать и почему.

## Реестр долга

Реестр хранится в `docs/tech-debt-register.md`:

```markdown
# Tech Debt Register — [дата]

## 🚨 CRITICAL (gambling integrity)
| ID | Файл | Описание | Стоимость | Риск |
|----|------|----------|-----------|------|
| TD-001 | lib/game/old_component.dart:45 | math.Random() вместо Random.secure() | 30мин | КРИТИЧНЫЙ |

## 🏗️ Architecture
| ID | Файл | Описание | Стоимость | Риск |
|----|------|----------|-----------|------|
| TD-002 | lib/game/game.dart | HasCollisionDetection на FlameGame | 2ч | HIGH |

## ⚡ Performance
...

## 🧪 Testing
...

## Итог
- Critical: N (выплатить НЕМЕДЛЕННО)
- High: N (следующий спринт)
- Medium: N (следующие 2 спринта)
- Low: N (backlog)
```

## Правила приоритизации

1. **CRITICAL gambling** — всегда выплачивать первыми, они влияют на целостность игры
2. **Architecture** — выплачивать до добавления новых фич
3. **Performance** — выплачивать при замедлении игры ниже порогов
4. **Testing** — выплачивать перед релизом
5. **Documentation** — выплачивать при передаче задачи другому агенту
6. **Code Quality** — выплачивать в порядке "попутно"

## Аргументы

- `сканировать` — автосканирование кода (по умолчанию)
- `показать` — показать текущий реестр
- `добавить "описание"` — добавить запись вручную
- `план` — создать план выплаты
- `--critical-only` — только gambling-критические проблемы
