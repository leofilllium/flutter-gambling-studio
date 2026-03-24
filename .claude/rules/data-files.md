---
description: JSON config validation rules for RTP weights, paytables, and balance configs
globs: ["design/balance/**/*.json", "assets/data/**/*.json", "lib/game/slot_config.dart"]
---

# Data Files Rules — RTP конфиги и игровые данные

## rtp-config.json — Обязательная схема

Каждая игра ОБЯЗАНА иметь `design/balance/rtp-config.json`:

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
  // Из rtp-config.json — не менять без rtp-mathematician!
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

## Запрещено в data файлах

1. Дублирование значений SlotConfig в JSON и коде — один источник правды
2. `rtp` > 0.98 или < 0.90 — будет отклонено rtp-mathematician
3. Вес символа = 0 — удали символ вместо нуля
4. Payout без хотя бы одной комбинации из 3 символов
5. Коммит rtp-config.json без обновления поля `simulation.last_run_date`
