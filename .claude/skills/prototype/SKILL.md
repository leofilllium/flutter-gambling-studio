---
name: prototype
description: "Создание быстрого изолированного Flutter-кода для тестирования 'Сочности' (Juiciness) — анимаций вращения, отскока (bounce), свечения."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: "[mechanic-name] (например: spin-bounce, glow-effect)"
---

# `prototype` — Лаборатория Сочности

Гемблинг-игры живут за счет визуального фидбека. Этот навык создает изолированный прототип анимации.

## Инструкция

1. Создайте файл `prototypes/[mechanic-name]/main.dart`.
2. Напишите минимальный `runApp` с простым экраном.
3. Добавьте Flame GameWidget, если тестируем физику/Flame эффекты.
4. Добавьте Flutter Animations, если тестируем UI (свечение, popup).
5. Не используйте зависимости из `lib/` (прототипы должны собираться отдельно).
6. Выведите команду `flutter run -t prototypes/[mechanic-name]/main.dart -d chrome` для запуска.
