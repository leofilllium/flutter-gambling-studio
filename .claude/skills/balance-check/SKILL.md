---
name: balance-check
description: "Проверка баланса игры: RTP симуляция для gambling (1М спинов) или анализ difficulty curve для puzzle/arcade жанров. Поддерживает full-curve валидацию по ВСЕМ уровням/стейджам контента (assets/data/*.json), а не только дефолтному уровню."
user-invocable: true
allowed-tools: Bash, Read, Write
argument-hint: "[кол-во испытаний, по умолчанию 1000000]"
---

# `balance-check` — Симулятор Баланса

Проверяет математический баланс игры в зависимости от жанра.

## Определение жанра

Прочитайте `design/gdd/game-concept.md` (или `design/gdd/gambling-concept.md`) чтобы определить жанр.

---

## Gambling — RTP Симуляция

1. Убедитесь что готов конфиг весов `design/balance/rtp-config.json`
2. Если скрипта `tools/simulate_rtp.py` нет — вызовите `game-mathematician` чтобы он его написал.
3. Запустите скрипт через `python3 tools/simulate_rtp.py [spins]`.
4. Сохраните результат в `design/balance/simulation-report.md`.
5. Целевой RTP: 95–97%. Если RTP вне диапазона — вызовите `game-mathematician` для балансировки.

---

## Puzzle — Difficulty Analysis

1. Прочитайте `design/balance/level-config.json`
2. Если скрипта `tools/simulate_difficulty.py` нет — вызовите `game-mathematician`.
3. Запустите: `python3 tools/simulate_difficulty.py`
4. Целевой win rate: 40–60% на нормальных уровнях, 10–30% на финальных.
5. Сохраните в `design/balance/difficulty-report.md`.

---

## Arcade — Difficulty Curve

1. Прочитайте `design/balance/difficulty-curve.json`
2. Если скрипта нет — вызовите `game-mathematician`.
3. Проверьте: spawn rate плавно нарастает, сессия 2–5 минут до Game Over у среднего игрока.
4. Сохраните в `design/balance/balance-report.md`.

---

## Full-Curve Validation (ВЕСЬ контент, не один уровень)

> Полная игра = объём контента. Проверять нужно ВСЮ кривую `assets/data/level-config.json` /
> `difficulty-curve.json` (Фаза 4.5 `/autocreate`), а не дефолтный уровень.

1. Прочитать конфиг контента (`assets/data/*.json` — зеркало в `design/balance/`).
2. Пройти по ВСЕМ N записям и проверить:
   - **Монотонность**: сложность (скорость/плотность/цель/лимит ходов) не падает между
     соседними уровнями без причины — нет «провалов» и нет «стены» (резкий скачок >×2).
   - **Проходимость**: для каждого уровня существует выигрышная стратегия (puzzle — решаемость;
     arcade — достижимость целевого счёта за отведённое время).
   - **Звёздные пороги**: 1★ достижима большинству, 3★ требует мастерства (не недостижима).
   - **Прогрессия наград/экономики**: начисление валюты растёт с уровнем, цены магазина
     соразмерны доходу (нет «гринд-стены» и нет инфляции с 1-го уровня).
   - **(gambling) bet-tiers**: разные ставки не выводят RTP за окно 95–97%.
3. Если на участке кривая ломается — `game-mathematician` правит JSON (не код).
4. Отчёт: таблица «уровень → ключевой параметр → win-rate/RTP → вердикт» в
   `design/balance/curve-report.md`.
