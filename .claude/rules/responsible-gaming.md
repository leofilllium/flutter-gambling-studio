# Responsible Gaming & Store Compliance — the mandatory layer in every game

> The studio builds **simulated** gambling. No game accepts or pays out real money. That
> implies a set of requirements which are not up for discussion and are not "added later":
> without them the game gets pulled from the store, and `/gate-check qa` and
> `/release-checklist` return FAIL.
>
> Applies to all categories C1–C6. The single relaxation is for C5 (casino roguelikes with
> no purchases and no currency wagers): see "Relaxed profile".

---

## 1. Absolute prohibitions (violation = release blocked)

1. **No real money as an outcome.** The game does not pay out money, prizes, or anything
   exchangeable for money. No withdrawals, no cashing out into currency, no "swap chips for
   gift cards".
2. **Virtual currency never converts back.** You can buy chips; you cannot sell them.
   A one-way arrow, and the UI must make that obvious.
3. **No real-currency symbols next to the game balance.** `$`, `€`, `₽`, `USD` next to the
   in-game balance are forbidden. Use only the name of the virtual currency: "chips",
   "coins", "crystals". Real-currency symbols are allowed ONLY on the IAP purchase screen.
4. **No promises of winnings.** Not in the UI, not in copy, not in store metadata, not on
   screenshots: "win money", "real payouts", "casino payout", "earn cash" are forbidden.
5. **The outcome is not for sale.** Buying currency does not improve the odds. Paying for a
   spin does not change the RTP. Any "pay more, win more often" is forbidden both
   mathematically and in the copy.
6. **No dark patterns.** Forbidden: fake "almost won" moments engineered for monetisation
   (a visual near-miss is allowed ONLY when it honestly reflects the outcome), fake scarcity
   timers, hidden costs, offers that cannot be dismissed.

---

## 2. Required screens and elements

Every game in the studio MUST contain the following (this is part of the MVP screen map):

### 2.1 Age gate — on first launch

- Shown ONCE, before the main menu; the result is persisted in `SharedPreferences`.
- Asks for a date of birth or confirmation of "I am 18 or older".
- On refusal or an underage answer: a polite exit screen, with NO route into the game.
- It is not a modal over the game: it is a full screen in the routes.

```dart
/// Gate shown once before the main menu.
/// See .claude/rules/responsible-gaming.md §2.1.
class AgeGateScreen extends StatelessWidget { ... }
```

### 2.2 Disclaimer — on the splash AND in the paytable/rules

The exact wording (it may be adapted to the game's voice, but the meaning must survive):

> "This game is played with virtual chips. Real money is neither accepted nor paid out.
> This game does not offer an opportunity to win real money or prizes.
> Success in this game does not imply future success at real-money gambling."

That last sentence is not decoration — it is the key phrase stores require from social
casino games.

### 2.3 Responsible Play — a block in settings

Required items:
- A session-time reminder (toggleable, 30/60 minute intervals);
- A "Take a break" button that gently returns the player to the menu;
- Text stating the game is intended for entertainment;
- A link or text with problem-gambling help contacts (a constant in the config, not
  hardcoded in a widget).

### 2.4 Odds disclosure — the "Odds" screen

Required for **C4 (gacha)** and for **C3** when spins can be paid for. Recommended for
C1/C2 (there the paytable plays that role).

- Reachable **BEFORE** currency is spent, not after.
- Shows: the base rate for each rarity, hard pity, and the effective rate including pity.
- The numbers come from the same config the game uses — never duplicated in the widget.

### 2.5 Paytable / rules

- The full payout table, or the multiplier formula.
- For C2: the declared house edge and the maximum multiplier.
- For C6: the bucket multipliers and the stated RTP.
- Reachable from the game screen in one tap.

---

## 3. Store metadata and rating

| Item | Requirement |
|------|-------------|
| Age rating | 18+ (Google Play), 17+/18+ (App Store) for C1–C4, C6 |
| Google Play category | Casino / Card / Casual — with "simulated gambling: yes" on the questionnaire |
| Store screenshots | No real-currency symbols and no payout promises |
| Description | Contains the virtual-currency disclaimer in the first 3 lines |
| Title / keywords | No "real money", "payout", "win cash", "casino bonus" |
| Regions | The list of countries restricting social casino is recorded in `store/metadata.md` |
| IAP | Only virtual currency bundles / remove-ads / cosmetics. Never "buying a chance" |

`/release-engineering` generates `store/metadata.md` with these fields already present;
empty fields block `/release-checklist`.

---

## 4. Relaxed profile (C5 only)

A casino roguelike with no purchases and no currency wagering (Balatro-like) is a premium
game with gambling **aesthetics** but no simulated betting.

Required:
- A disclaimer stating this is a roguelike, not a gambling game (if it looks like a casino);
- No IAP tied to randomness;
- Typically a 12+ rating.

Not required: age gate, responsible-play block, odds disclosure.

**The decision to use the relaxed profile is made once, at the concept stage, and recorded in
the "Classification" block with a justification.** If currency purchases are added to the game
later, the profile automatically becomes the full one.

---

## 5. Checks across the pipeline

| Where | What is checked |
|-------|-----------------|
| `/gate-check concept` | The "Classification" block contains a compliance profile |
| `/gate-check design` | Age gate, disclaimer, responsible play and odds are in the screen map |
| `/ui-audit` | The screens are implemented; no real-currency symbols next to the game balance |
| `/balance-check` | The numbers shown to the player match the simulation config |
| `/playtest` | The age gate really does appear on a clean launch, and is remembered |
| `/release-checklist` | Store metadata, rating and copy — the final GO/NO-GO |

### Automatic grep checks (used by `/ui-audit` and `/release-checklist`)

```bash
# Real-currency symbols next to the game balance
grep -rnE '\$\{?balance|\$\{?coins|USD|€|₽' lib/ --include="*.dart"

# Forbidden promises in UI copy and metadata
grep -rniE 'real money|win money|win cash|cash ?out|payout|earn cash' \
  lib/ store/ --include="*.dart" --include="*.md"

# Presence of the required screens
grep -rl 'AgeGate' lib/ && grep -rl 'ResponsiblePlay' lib/ && grep -rl 'Disclaimer' lib/
```

The first two commands MUST find nothing (other than the IAP purchase screen and the text of
the disclaimer itself). The third MUST find all three.

---

## 6. Copy constants

All compliance copy lives in one place rather than scattered across widgets:

```dart
/// Compliance copy required by .claude/rules/responsible-gaming.md.
/// Do not inline these strings into widgets — stores audit them and they change per region.
class ComplianceCopy {
  static const String disclaimer =
      'This game is played with virtual chips. Real money is neither accepted nor paid out. '
      'Success in this game does not imply future success at real-money gambling.';

  static const String ageGatePrompt = 'Please confirm that you are 18 or older';
  static const String responsiblePlay =
      'Play for fun. Take regular breaks.';
  static const String helpContact = '...'; // from the region config
  static const int sessionReminderMinutes = 60;
}
```

> These strings are English by default, like the rest of the game's copy. If the user has
> explicitly asked for the game in another language, translate the compliance copy along with
> the rest of the player-facing text — the meaning of the disclaimer must survive the
> translation intact, because that is what the stores audit.
