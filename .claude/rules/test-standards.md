---
description: QA test standards for gambling mechanics — RNG distribution, paylines, edge cases
globs: ["test/**/*.dart", "integration_test/**/*.dart"]
---

# Test Standards — Gambling Game QA

## Обязательные тесты для каждой игры

### 1. RNG Дистрибуция (КРИТИЧЕСКИ ВАЖНО)
Каждый WeightedRNG ОБЯЗАН иметь дистрибуционный тест:

```dart
group('WeightedRNG', () {
  test('распределяет символы согласно весам', () {
    // Arrange
    final rng = WeightedRNG();
    final weights = [10, 5, 2, 1]; // Символы 0,1,2,3
    final counts = List.filled(4, 0);
    const spins = 100000;

    // Act
    for (var i = 0; i < spins; i++) {
      counts[rng.pickSymbol(weights)]++;
    }

    // Assert — погрешность не более 5%
    final total = weights.reduce((a, b) => a + b); // 18
    expect(counts[0] / spins, closeTo(10/total, 0.05)); // ~55.6%
    expect(counts[1] / spins, closeTo(5/total, 0.05));  // ~27.8%
    expect(counts[2] / spins, closeTo(2/total, 0.05));  // ~11.1%
    expect(counts[3] / spins, closeTo(1/total, 0.05));  // ~5.6%
  });

  test('использует Random.secure() — не Math.Random()', () {
    // Verify RNG class uses secure random
    final source = File('lib/systems/weighted_rng.dart').readAsStringSync();
    expect(source, contains('Random.secure()'));
    expect(source, isNot(contains('Random()')));
  });
});
```

### 2. Payline Evaluator
```dart
group('PaylineEvaluator', () {
  test('определяет горизонтальную выигрышную линию', () { ... });
  test('определяет Wild как замену любого символа', () { ... });
  test('3 одинаковых символа = выигрыш', () { ... });
  test('2 символа = не выигрыш (если не Wild)', () { ... });
  test('смешанные символы = проигрыш', () { ... });
  test('Scatter не зависит от позиции на линии', () { ... });
});
```

### 3. Граничные состояния (Edge Cases)
```dart
group('Граничные ситуации', () {
  test('недостаточный баланс блокирует спин', () {
    final game = SlotMachineGame();
    game.balance = 0;
    game.bet = 1;

    final result = game.canSpin();
    expect(result, isFalse);
  });

  test('быстрый двойной клик не запускает два спина', () async {
    final game = SlotMachineGame();
    game.balance = 1000;

    game.spin(); // Первый спин
    final secondSpinResult = game.spin(); // Должен быть проигнорирован

    expect(secondSpinResult, isNull); // Или false
    expect(game.gameState, isA<SpinningState>());
  });

  test('восстановление состояния после паузы', () async {
    final game = SlotMachineGame();
    await game.spin();
    game.pause();
    game.resume();

    expect(game.gameState, isA<IdleState>());
    expect(game.balance, isNonNegative);
  });

  test('ставка > баланса невозможна', () {
    final game = SlotMachineGame();
    game.balance = 5;
    game.bet = 10;

    expect(game.canSpin(), isFalse);
  });
});
```

### 4. State Leakage Tests
```dart
group('State Leakage — нет утечки между спинами', () {
  test('баланс корректен после 1000 спинов', () async {
    final game = SlotMachineGame();
    final initialBalance = game.balance;
    var totalBet = 0;
    var totalWin = 0;

    for (var i = 0; i < 1000; i++) {
      totalBet += game.bet;
      final win = await game.spin();
      totalWin += win;
    }

    expect(game.balance, equals(initialBalance - totalBet + totalWin));
  });

  test('GameState возвращается в Idle после каждого спина', () async {
    final game = SlotMachineGame();

    for (var i = 0; i < 10; i++) {
      await game.spin();
      expect(game.gameState, isA<IdleState>(),
             reason: 'После спина #$i GameState должен быть Idle');
    }
  });
});
```

## Минимальное покрытие по категориям

| Категория | Минимум |
|-----------|---------|
| WeightedRNG | 95% |
| PaylineEvaluator | 95% |
| SlotConfig / математика | 90% |
| GameState машина | 85% |
| HUD виджеты | 70% |
| Анимации (компоненты) | 60% |

## Формат тестов (AAA)

```dart
test('описание в третьем лице настоящего времени', () {
  // Arrange — подготовка
  final game = ...;

  // Act — действие
  final result = game.method();

  // Assert — проверка
  expect(result, ...);
});
```

## Запрещено в тестах

1. `Random()` или `Random.secure()` в тестах — используй фиксированные seed или моки
2. `sleep()` или `Future.delayed()` — используй `FakeAsync` или `pump()`
3. Тесты без единого `expect` — пустые тесты запрещены
4. Зависимость порядка тестов — каждый тест должен быть независимым
