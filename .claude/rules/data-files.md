---
description: JSON config validation rules for gambling math-model configs (M1-M6) consumed by tools/simulate_math.py
globs: ["design/balance/**/*.json", "assets/data/**/*.json", "lib/game/game_config.dart", "lib/game/slot_config.dart"]
---

# Data Files Rules — конфиги математических моделей

Каждая игра ОБЯЗАНА иметь ровно один конфиг математической модели, соответствующий её
категории. Конфиг — вход для `tools/simulate_math.py`; готовые эталоны, проходящие прогон
«из коробки», лежат в `.claude/docs/templates/math-configs/`.

| Категория | Модель | Конфиг | Эталон |
|-----------|--------|--------|--------|
| C1 🎰 | M1 | `design/balance/rtp-config.json` | `templates/math-configs/rtp-config.json` |
| C2 ⚡ | M2 | `design/balance/rtp-config.json` | `templates/math-configs/instant-win-config.json` |
| C3 🏰 | M3 | `design/balance/economy-config.json` | `templates/math-configs/economy-config.json` |
| C4 🎁 | M4 | `design/balance/gacha-config.json` | `templates/math-configs/gacha-config.json` |
| C5 🃏 | M5 | `design/balance/run-config.json` | `templates/math-configs/run-config.json` |
| C6 ⚙️ | M6 | `design/balance/physics-config.json` | `templates/math-configs/physics-config.json` |

Прогон и пороги — в `.claude/docs/math-models.md`.

## rtp-config.json — схема для слотов (C1 / модель M1)

```json
{
  "game_name": "Название игры",
  "version": "1.0.0",
  "target_rtp": 0.96,
  "volatility": "medium",
  "hit_rate": 0.28,
  "reels": {
    "count": 3,
    "visible_rows": 3
  },
  "symbols": [
    {
      "id": 0,
      "name": "cherry",
      "weight": 10,
      "payouts": { "3": 5, "2": 1 }
    },
    {
      "id": 1,
      "name": "bar",
      "weight": 7,
      "payouts": { "3": 10, "2": 2 }
    },
    {
      "id": 2,
      "name": "seven",
      "weight": 4,
      "payouts": { "3": 25, "2": 5 }
    },
    {
      "id": 3,
      "name": "diamond",
      "weight": 2,
      "payouts": { "3": 75 }
    },
    {
      "id": 4,
      "name": "wild",
      "weight": 1,
      "is_wild": true,
      "payouts": { "3": 100 }
    }
  ],
  "paylines": [
    [1, 1, 1],
    [0, 0, 0],
    [2, 2, 2],
    [0, 1, 2],
    [2, 1, 0]
  ],
  "bonus": {
    "free_spins_trigger_count": 3,
    "free_spins_count": 10,
    "free_spins_multiplier": 3
  },
  "simulation": {
    "last_run_spins": 1000000,
    "last_run_rtp": 0.9587,
    "last_run_date": "2026-01-01"
  }
}
```

## Обязательные поля

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `target_rtp` | float | 0.90–0.98 |
| `volatility` | string | "low" / "medium" / "high" |
| `hit_rate` | float | 0.15–0.45 |
| `symbols[].weight` | int | > 0 |
| `symbols[].payouts` | object | Хотя бы один payout |
| `simulation.last_run_rtp` | float | Должен быть близок к `target_rtp` (±0.03) |

## Правила для slot_config.dart

```dart
// ✅ ОБЯЗАТЕЛЬНАЯ СТРУКТУРА
class SlotConfig {
  // Из rtp-config.json — не менять без game-mathematician!
  static const double targetRtp = 0.96;
  static const List<int> reelWeights = [10, 7, 4, 2, 1];

  // Игровые константы
  static const int reelCount = 3;
  static const int visibleRows = 3;
  static const int minBet = 1;
  static const int maxBet = 100;

  // Анимация (утверждено juice-artist)
  static const Duration reelSpinDuration = Duration(milliseconds: 2000);
  static const Duration cascadeDelay = Duration(milliseconds: 300);
  static const Duration winDisplayDuration = Duration(seconds: 3);

  // Пороги для эффектов
  static const int bigWinMultiplier = 10;   // bet * 10 = Big Win
  static const int superWinMultiplier = 50; // bet * 50 = Super Win
  static const int maxParticles = 200;      // Лимит партиклей
}
```

## Обязательные поля прочих моделей

| Модель | Обязательные поля |
|--------|-------------------|
| **M2** | `type` (step/crash/threshold/draw/table), `house_edge`, `max_multiplier` |
| **M3** | `energy_cap`, `energy_regen_per_hour`, `spin_events[]` (веса+награды), `unlock_prices[]` |
| **M4** | `rarities[]` (`base_rate` + `duplicate_value`), `hard_pity`, опц. `soft_pity_start`/`soft_pity_step` |
| **M5** | `round_targets[]`, `base_score`, `income_per_round`, `modifier_cost`, `modifiers[]` (≥3) |
| **M6** | `type` (plinko/buckets/empirical), `bucket_multipliers[]`, `fixed_timestep`, `deterministic_seed` |

## Запрещено в data файлах

1. Дублирование значений конфига в JSON и в Dart — один источник правды
2. RTP > 0.98 или < 0.90 для M1/M6; вне 0.95–0.995 для M2 — отклоняется game-mathematician
3. Вес символа / события = 0 — удали запись вместо нуля
4. Payout без хотя бы одной выигрышной комбинации
5. Коммит конфига без обновления `simulation.last_run_date`
6. Сумма `base_rate` по редкостям (M4) ≠ 1.0
7. `hard_pity` отсутствует или > 90 (M4) — pity обязателен и обязан быть достижим
8. Отсутствие `modifiers[]` (M5) — тогда баланс выбора не верифицируется
9. `fixed_timestep: false` (M6) — RTP становится непроверяемым
10. Значения, объявленные игроку на экранах правил/шансов, расходящиеся с конфигом
