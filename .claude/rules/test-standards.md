---
description: QA test standards for mini-games — RNG distribution (gambling), game logic, edge cases
globs: ["test/**/*.dart", "integration_test/**/*.dart"]
---

# Test Standards — Gambling Game QA

## Mandatory tests for every game

### 1. RNG distribution (CRITICALLY IMPORTANT)
Every WeightedRNG MUST have a distribution test:

```dart
group('WeightedRNG', () {
  test('distributes symbols according to their weights', () {
    // Arrange
    final rng = WeightedRNG();
    final weights = [10, 5, 2, 1]; // Symbols 0,1,2,3
    final counts = List.filled(4, 0);
    const spins = 100000;

    // Act
    for (var i = 0; i < spins; i++) {
      counts[rng.pickSymbol(weights)]++;
    }

    // Assert — the error must stay within 5%
    final total = weights.reduce((a, b) => a + b); // 18
    expect(counts[0] / spins, closeTo(10/total, 0.05)); // ~55.6%
    expect(counts[1] / spins, closeTo(5/total, 0.05));  // ~27.8%
    expect(counts[2] / spins, closeTo(2/total, 0.05));  // ~11.1%
    expect(counts[3] / spins, closeTo(1/total, 0.05));  // ~5.6%
  });

  test('uses Random.secure() — not math.Random()', () {
    // Verify RNG class uses secure random
    final source = File('lib/systems/weighted_rng.dart').readAsStringSync();
    expect(source, contains('Random.secure()'));
    expect(source, isNot(contains('Random()')));
  });
});
```

### 2. Payline evaluator
```dart
group('PaylineEvaluator', () {
  test('detects a horizontal winning line', () { ... });
  test('treats a Wild as a substitute for any symbol', () { ... });
  test('3 identical symbols is a win', () { ... });
  test('2 symbols is not a win (unless Wild)', () { ... });
  test('mixed symbols is a loss', () { ... });
  test('a Scatter does not depend on its position on the line', () { ... });
});
```

### 3. Edge cases
```dart
group('Edge cases', () {
  test('an insufficient balance blocks the spin', () {
    final game = SlotMachineGame();
    game.balance = 0;
    game.bet = 1;

    final result = game.canSpin();
    expect(result, isFalse);
  });

  test('a fast double tap does not start two spins', () async {
    final game = SlotMachineGame();
    game.balance = 1000;

    game.spin(); // The first spin
    final secondSpinResult = game.spin(); // Must be ignored

    expect(secondSpinResult, isNull); // Or false
    expect(game.gameState, isA<SpinningState>());
  });

  test('state recovers after a pause', () async {
    final game = SlotMachineGame();
    await game.spin();
    game.pause();
    game.resume();

    expect(game.gameState, isA<IdleState>());
    expect(game.balance, isNonNegative);
  });

  test('a bet larger than the balance is impossible', () {
    final game = SlotMachineGame();
    game.balance = 5;
    game.bet = 10;

    expect(game.canSpin(), isFalse);
  });
});
```

### 4. State leakage tests
```dart
group('State leakage — nothing leaks between spins', () {
  test('the balance is correct after 1000 spins', () async {
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

  test('GameState returns to Idle after every spin', () async {
    final game = SlotMachineGame();

    for (var i = 0; i < 10; i++) {
      await game.spin();
      expect(game.gameState, isA<IdleState>(),
             reason: 'After spin #$i the GameState should be Idle');
    }
  });
});
```

## Minimum coverage by area

| Area | Minimum |
|------|---------|
| WeightedRNG | 95% |
| PaylineEvaluator | 95% |
| SlotConfig / mathematics | 90% |
| The GameState machine | 85% |
| HUD widgets | 70% |
| Animations (components) | 60% |

## Test format (AAA)

```dart
test('a description in the third person, present tense', () {
  // Arrange — set up
  final game = ...;

  // Act — do the thing
  final result = game.method();

  // Assert — check it
  expect(result, ...);
});
```

Test names and `reason:` strings are written in English, like the rest of the codebase.

## Forbidden in tests

1. `Random()` or `Random.secure()` inside tests — use a fixed seed or a mock
2. `sleep()` or `Future.delayed()` — use `FakeAsync` or `pump()`
3. Tests without a single `expect` — empty tests are forbidden
4. Dependence on test order — every test must be independent
