---
name: balance-check
description: "Симулятор RTP (Return to Player) для слота. Запускает скрипт симуляции 1М вращений для проверки математики выплат и волатильности."
user-invocable: true
allowed-tools: Bash, Read, Write
argument-hint: "[кол-во спинов, по умолчанию 1000000]"
---

# `balance-check` — Симулятор Баланса

Вычисляет математическое ожидание игры (RTP) с помощью скрипта.

## Порядок действий

1. Убедитесь что готов конфиг весов `design/balance/rtp-config.json`
2. Если скрипта `tools/simulate_rtp.py` нет — вызовите `rtp-mathematician` чтобы он его написал под текущий проект.
3. Запустите скрипт через `python3 tools/simulate_rtp.py [spins]`.
4. Сохраните результат в `design/balance/simulation-report.md`.
5. Посмотрите на RTP. Если он < 85% или > 99%, порекомендуйте вызвать `/design-system rtp-weights` для балансировки.
