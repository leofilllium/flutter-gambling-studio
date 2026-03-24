---
description: Flutter HUD and UI rules for gambling games — screens, overlays, state separation
globs: ["lib/screens/**/*.dart", "lib/ui/**/*.dart"]
---

# UI Code Rules (Flutter Screens & HUD)

## Разделение состояния UI и игры

- **НИКОГДА** не хранить игровое состояние (баланс, ставка, текущий спин) в Flutter виджетах
- Flutter UI только **читает** состояние через `ValueNotifier` или `Stream`
- Игровая логика живёт в Flame компонентах, UI — только отображает

```dart
// ✅ ПРАВИЛЬНО — HUD читает через ValueNotifier
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> balance;
  final ValueNotifier<int> bet;
  final ValueNotifier<bool> isSpinning;

  const HudWidget({
    required this.balance,
    required this.bet,
    required this.isSpinning,
    super.key,
  });
}

// ❌ ЗАПРЕЩЕНО — HUD сам управляет балансом
class HudWidget extends StatefulWidget {
  int _balance = 1000; // Нельзя!
  void _onWin(int amount) => setState(() => _balance += amount); // Нельзя!
}
```

## Кнопка Spin

- Кнопка Spin ОБЯЗАНА быть заблокирована во время спина (`isSpinning`)
- Двойной клик ДОЛЖЕН быть защищён — игнорировать вторые нажатия
- Дебаунс минимум 300мс после последнего нажатия

```dart
// ✅ ПРАВИЛЬНО — защита от двойного клика
class SpinButton extends StatelessWidget {
  final VoidCallback? onSpin;
  final bool isSpinning;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isSpinning ? null : onSpin, // Блокировка во время спина
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        // ...
      ),
    );
  }
}
```

## Ставка (Bet) — обязательные правила

- Ставку нельзя менять во время спина — кнопки Bet+/Bet- блокируются
- Минимальная ставка: 1 (или из SlotConfig)
- Максимальная ставка не должна превышать `balance` — проверка перед спином
- Если `balance < minBet` — показать оверлей "Недостаточно средств"

## Оверлеи выигрышей

- Win overlay появляется ПОСЛЕ завершения анимации барабанов
- Длительность показа: минимум 2 секунды, максимум 5 секунд
- Auto-dismiss через 3 секунды (или тап)
- Для wins > 10x ставка — специальный "Big Win" оверлей
- Для wins > 50x ставка — "Super Win" оверлей с дополнительными партиклями

## Экраны

| Экран | Файл | Ответственность |
|-------|------|-----------------|
| Главное меню | `screens/main_menu.dart` | Только навигация, баланс read-only |
| Игровой экран | `screens/game_screen.dart` | GameWidget обёртка + HUD |
| HUD | `screens/hud_widget.dart` | ValueNotifier<int> balance, bet, isSpinning |

## Требования доступности

- Кнопка Spin должна иметь `Semantics(label: 'Вращать барабаны')`
- Баланс и ставка — `Semantics(value: '$balance монет')`
- Текст не менее 14sp на мобильных устройствах
- Контраст текста к фону минимум 4.5:1

## Запрещённые паттерны

1. **`setState()`** для обновления игрового состояния — только `ValueNotifier`
2. **`BuildContext` в Flame компонентах** — передай колбэк при инициализации
3. **Анимации UI длиннее 500мс** — замедляют восприятие результата
4. **Фиксированные размеры без `MediaQuery`** — используй `LayoutBuilder` или `FractionallySizedBox`
