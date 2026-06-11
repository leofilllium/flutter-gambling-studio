---
name: release-checklist
description: "Вызывает агента release-manager для проведения контроля качества перед релизом игры. Полностью проверяет архитектуру RNG и отсутствие State Leakage."
user-invocable: true
allowed-tools: Bash, Read, Agent
argument-hint: ""
---

# `release-checklist` — Проверка готовности

Запускает процесс релиза. Самостоятельно не работает, делегирует задачу менеджеру релизов.

## Инструкция 

1. Вызовите `release-manager` (в среде без Agent tool — примите persona из
   `.claude/agents/release-manager.md`).
2. Передайте ему команду: `Пожалуйста, проверь этот проект по твоему Gambling Release Checklist И по несгораемым инвариантам из .claude/docs/quality-bar.md (§9 + выборочно §1–§8), и составь отчёт в production/session-logs/release-[date].md`
3. Если существуют `production/playtest/*/PLAYTEST-REPORT.md` и `design/asset-review.md` —
   release-manager обязан учесть их вердикты (NOT-PLAYABLE или непройденный asset-review = NO-GO).
4. Выведите результат (GO / NO-GO) пользователю.
