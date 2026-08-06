---
description: JSON config validation rules for gambling math-model configs (M1-M6) consumed by tools/simulate_math.py
globs: ["design/balance/**/*.json", "assets/data/**/*.json", "lib/game/game_config.dart", "lib/game/slot_config.dart"]
---

# Data Files Rules — math model configs

Every game MUST have exactly one math model config, matching its category. The config is the
input for `tools/simulate_math.py`; reference files that pass a run out of the box live in
`.claude/docs/templates/math-configs/`.

| Category | Model | Config | Reference |
|----------|-------|--------|-----------|
| C1 🎰 | M1 | `design/balance/rtp-config.json` | `templates/math-configs/rtp-config.json` |
| C2 ⚡ | M2 | `design/balance/rtp-config.json` | `templates/math-configs/instant-win-config.json` |
| C3 🏰 | M3 | `design/balance/economy-config.json` | `templates/math-configs/economy-config.json` |
| C4 🎁 | M4 | `design/balance/gacha-config.json` | `templates/math-configs/gacha-config.json` |
| C5 🃏 | M5 | `design/balance/run-config.json` | `templates/math-configs/run-config.json` |
| C6 ⚙️ | M6 | `design/balance/physics-config.json` | `templates/math-configs/physics-config.json` |

The run command and the thresholds are in `.claude/docs/math-models.md`.

## rtp-config.json — the slot schema (C1 / model M1)

```json
{
  "game_name": "Game name",
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

## Required fields

| Field | Type | Constraints |
|-------|------|-------------|
| `target_rtp` | float | 0.90–0.98 |
| `volatility` | string | "low" / "medium" / "high" |
| `hit_rate` | float | 0.15–0.45 |
| `symbols[].weight` | int | > 0 |
| `symbols[].payouts` | object | At least one payout |
| `simulation.last_run_rtp` | float | Must be close to `target_rtp` (±0.03) |

## Rules for slot_config.dart

```dart
// ✅ THE REQUIRED STRUCTURE
class SlotConfig {
  // From rtp-config.json — do not change without game-mathematician!
  static const double targetRtp = 0.96;
  static const List<int> reelWeights = [10, 7, 4, 2, 1];

  // Game constants
  static const int reelCount = 3;
  static const int visibleRows = 3;
  static const int minBet = 1;
  static const int maxBet = 100;

  // Animation (approved by juice-artist)
  static const Duration reelSpinDuration = Duration(milliseconds: 2000);
  static const Duration cascadeDelay = Duration(milliseconds: 300);
  static const Duration winDisplayDuration = Duration(seconds: 3);

  // Effect thresholds
  static const int bigWinMultiplier = 10;   // bet * 10 = Big Win
  static const int superWinMultiplier = 50; // bet * 50 = Super Win
  static const int maxParticles = 200;      // Particle limit
}
```

## Required fields for the other models

| Model | Required fields |
|-------|-----------------|
| **M2** | `type` (step/crash/threshold/draw/table), `house_edge`, `max_multiplier` |
| **M3** | `energy_cap`, `energy_regen_per_hour`, `spin_events[]` (weights + rewards), `unlock_prices[]` |
| **M4** | `rarities[]` (`base_rate` + `duplicate_value`), `hard_pity`, optional `soft_pity_start`/`soft_pity_step` |
| **M5** | `round_targets[]`, `base_score`, `income_per_round`, `modifier_cost`, `modifiers[]` (≥3) |
| **M6** | `type` (plinko/buckets/empirical), `bucket_multipliers[]`, `fixed_timestep`, `deterministic_seed` |

## Forbidden in data files

1. Duplicating a config value in both JSON and Dart — one source of truth
2. RTP > 0.98 or < 0.90 for M1/M6; outside 0.95–0.995 for M2 — rejected by game-mathematician
3. A symbol or event weight of 0 — delete the entry instead of zeroing it
4. A payout with no winning combination at all
5. Committing a config without updating `simulation.last_run_date`
6. The sum of `base_rate` across rarities (M4) ≠ 1.0
7. `hard_pity` missing or > 90 (M4) — pity is mandatory and must be reachable
8. `modifiers[]` missing (M5) — without it the balance of choice cannot be verified
9. `fixed_timestep: false` (M6) — the RTP becomes unverifiable
10. Values shown to the player on the rules/odds screens that disagree with the config
