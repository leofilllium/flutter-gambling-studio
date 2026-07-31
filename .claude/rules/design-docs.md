---
description: Required sections and structure for gambling game GDD documents (categories C1-C6)
globs: ["design/**/*.md", "docs/**/*.md"]
---

# Design Document Standards — Mini-Game GDD

## Обязательные 8 секций для каждого GDD

Каждый документ в `design/gdd/` ОБЯЗАН содержать эти разделы:

### 1. Обзор (Overview)
Один абзац: что это за механика, для кого, зачем.

### 2. Фантазия игрока (Player Fantasy)
Как должен чувствовать себя игрок? Что он "переживает"?
Пример: "Игрок чувствует нарастание напряжения при остановке барабанов — каждый удар в пол создаёт ощущение близкой победы."

### 3. Детальные правила (Rules)
Однозначное описание механики. Без двусмысленности.

### 4. Формулы (Formulas)
ВСЯ математика с переменными:
```
Выигрыш = Ставка × Множитель_символа × Количество_линий_выигрыша
RTP = Σ(вероятность_комбинации × выплата) / ставка
```

### 5. Граничные случаи (Edge Cases)
- Что если баланс = 0?
- Что если выигрыш > текущего джекпота?
- Что если Free Spins прерваны паузой?
- Что при одновременном Scatter + Wild на одной линии?

### 6. Зависимости (Dependencies)
Другие системы, от которых зависит эта механика:
- `WeightedRNG` — источник случайности
- `PaylineEvaluator` — подсчёт выигрышей
- `AudioService` — звуковая обратная связь

### 7. Настроечные параметры (Tuning Knobs)
Все значения, которые game-mathematician может менять:
| Параметр | Текущее | Диапазон | Эффект |
|----------|---------|---------|--------|
| Вес Wild | 1 | 0–3 | ↑ вес = ↑ RTP |
| Free Spins множитель | 3 | 1–5 | ↑ множитель = ↑ волатильность |

### 8. Критерии приёмки (Acceptance Criteria)
Тестируемые условия успеха:
- [ ] AC-1: RTP в диапазоне 95–97% при 1М симуляций
- [ ] AC-2: Hit rate 25–35%
- [ ] AC-3: Wild заменяет любой символ кроме Scatter
- [ ] AC-4: 3 Scatter на любых позициях = Free Spins

## Жизненный цикл документа

```
Draft → [OPEN вопросы] → Review → Approved (Status: ✅ Approved YYYY-MM-DD)
→ Implemented (ссылка на PR) → Deprecated (если механика удалена)
```

## Шаблон имени файла

Общее для всех категорий:

```
design/gdd/
├── game-concept.md            # Концепт игры: категория C1–C6, архетип, матмодель, compliance
├── math-model.md              # Модель M1–M6: формулы, пороги, ссылка на JSON-конфиг
├── round-flow.md              # Полный цикл раунда: ставка → исход → раскрытие → выплата
└── compliance-screens.md      # Age-gate, дисклеймер, responsible-play, odds disclosure
```

Плюс документы по механикам конкретной категории:

| Категория | Типичные GDD |
|-----------|--------------|
| C1 🎰 | `reel-mechanics.md`, `payline-system.md`, `wild-scatter.md`, `free-spins.md` |
| C2 ⚡ | `multiplier-curve.md`, `cashout-rules.md`, `seed-fairness.md` |
| C3 🏰 | `spin-event-table.md`, `energy-economy.md`, `raid-shield.md`, `collection.md` |
| C4 🎁 | `banner-rates.md`, `pity-system.md`, `duplicate-conversion.md` |
| C5 🃏 | `run-structure.md`, `modifier-registry.md`, `shop-economy.md` |
| C6 ⚙️ | `physics-setup.md`, `bucket-payouts.md`, `determinism.md` |

## Ссылки в коде

Код ДОЛЖЕН ссылаться на GDD:
```dart
/// Implements [design/gdd/payline-system.md].
/// AC-3: Wild заменяет любой символ кроме Scatter.
class PaylineEvaluator { ... }
```

## Таблицы выплат — обязательный формат

```markdown
| Символ | 2 подряд | 3 подряд | Вес | Вероятность (3 реела) |
|--------|----------|----------|-----|----------------------|
| Вишня  | 1×       | 5×       | 10  | 18.6%               |
| Бар    | 2×       | 10×      | 7   | 9.1%                |
| Семёрка| —        | 25×      | 4   | 3.0%                |
| Алмаз  | —        | 75×      | 2   | 0.7%                |
| Wild   | —        | 100×     | 1   | 0.2%                |
```
