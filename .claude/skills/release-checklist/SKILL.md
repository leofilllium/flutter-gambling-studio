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

1. Вызовите `release-manager`.
2. Передайте ему команду: `Пожалуйста, проверь этот проект по твоему Gambling Release Checklist и составь отчёт в production/session-logs/release-[date].md`
3. Выведите результат (GO / NO-GO) пользователю.
