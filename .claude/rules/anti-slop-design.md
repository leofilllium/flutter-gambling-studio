# Contextual Design — Human-Crafted UI for Games

> The problem with AI-generated UI isn't just "purple gradients and rounded cards."
> The problem is **lack of intent**. Every visual decision in a human-made game exists
> for a reason tied to the game's identity. AI slop has no reasons — it picks defaults.
>
> But replacing one set of defaults ("always rounded") with another ("always skewed + neon")
> is just **anti-slop slop**. A cozy puzzle game with aggressive neon trapezoid buttons
> is just as soulless as a casino game with Material Design cards.
>
> The goal: every game looks like **that specific game**, not like "a game made with our studio."

## The Core Principle: Design Follows Context

Every visual decision must answer: **"Why this, for THIS game?"**

A neon cyberpunk slot should feel electric and dangerous.
A forest-themed match-3 should feel warm and organic.
A minimalist dice game should feel clean and precise.
A pirate scratch card should feel weathered and adventurous.

If you can swap the UI between two different games and nobody notices — the design failed.

---

## How AI Slop Actually Looks (and why it fails)

AI slop isn't about specific colors or shapes. It's about **decisions made without context**:

| Slop Signal | Why It's Slop | What Human Designers Do Instead |
|------------|---------------|-------------------------------|
| Same visual treatment on every element | No hierarchy — brain can't parse what's important | The primary action is visually dominant. Secondary elements recede. Different functions look different. |
| Color palette unrelated to theme | Colors were picked for "looking nice" not for meaning | Colors carry emotional weight. A gold-themed game uses warm ambers. A space game uses cold blues. An earthy puzzle uses greens and browns. |
| Default Material/Cupertino widgets | No design effort — took what the framework gave | Every widget is touched. Not necessarily replaced — but intentionally chosen and customized for the context. |
| Uniform spacing and sizing | Grid-based thinking, no visual rhythm | Important things are bigger. Related things are closer. Rhythm creates scannable hierarchy. |
| Generic transitions (fade, slide) | No thought about the transition's role | Transitions reinforce the game's metaphor. Cards flip. Doors open. Puzzles dissolve. Or: a deliberate fast cut for snappy games. |
| Overuse of blur/glow/particles everywhere | "More effects = more quality" | Effects serve a purpose. Glow highlights wins. Blur focuses attention. Particles celebrate. Not everything glows. |
| Same font for everything | No typographic hierarchy | Display text (numbers, titles) has character. Body text (descriptions, rules) prioritizes readability. The fonts relate to the game's era/mood. |
| Placeholder empty states | Developer didn't think about this state | Empty states tell the player what to do next, in the game's voice |

---

## Design DNA — Derived from the Game, Not a Template

Every game defines its own **Design DNA** during concept phase. The DNA is a set of
visual principles that emerge from the game's theme, mood, and core mechanic.

### How to Build a Design DNA

Ask these questions about the specific game:

**1. What emotion does the core mechanic create?**
- Slot spin → anticipation, tension, release → fast animations, dramatic pauses, explosive wins
- Match-3 cascade → satisfaction, flow, "one more turn" → smooth movements, chain reactions that feel earned
- Idle clicker → growth, accumulation → numbers that feel satisfying to watch increase
- Memory card flip → curiosity, "aha!" moment → reveal animations that reward the discovery
- Breakout → speed, precision, chaos → tight responsive controls, impactful collisions

**2. What world does this game exist in?**
- Neon casino → electric, artificial, nightlife → bright on dark, hard edges, glow
- Enchanted forest → organic, magical, peaceful → soft curves, earthy colors, particle leaves
- Space station → cold, vast, technological → monospace fonts, thin lines, blue-white palette
- Pirate adventure → weathered, bold, treasure → torn edges, gold accents, serif fonts
- Candy land → sweet, playful, bouncy → round shapes, pastel colors, springy animations
- Minimalist zen → calm, precise, elegant → lots of whitespace, one accent color, subtle animations

**3. What does the primary action feel like?**
- Heavy and impactful → slow press animation, screen shake, deep sound
- Quick and snappy → fast response, minimal animation, sharp sound
- Magical and ethereal → floating elements, particle trails, shimmering
- Mechanical and satisfying → click feedback, gear-like movements, ratchet sounds

### Design DNA Document Structure

```markdown
## Design DNA: [Game Name]

### Emotional Core
[1-2 sentences: what the player should FEEL]

### Visual World
[Description of the visual universe this game lives in]

### Shape Language
- Primary action: [shape and why — e.g., "bold rounded rectangle because the game is friendly"]
- Secondary controls: [shape — e.g., "circular icons because they feel approachable"]
- Information panels: [shape — e.g., "sharp rectangles because data should feel precise"]
- Why these shapes: [tied to the game's world]

### Color Palette (5 colors with REASONS)
- Background: #XXXXXX — [why this specific color for THIS game]
- Surface: #XXXXXX — [why]
- Primary: #XXXXXX — [why — tied to the game's world or emotion]
- Success/Win: #XXXXXX — [why]
- Danger/Loss: #XXXXXX — [why]

### Typography
- Display: [specific font] — [why it fits this game's personality]
- Body: [specific font] — [why it's readable and matches the mood]
- Numbers: [specific font or same as display] — [why numbers need this treatment]

### Motion Character
- Transitions: [description — tied to the game's metaphor]
- Win celebration: [description — matches the emotional peak]
- Idle state: [description — keeps the game feeling alive in a way that fits]
- Button feedback: [description — matches the "weight" of the game's world]

### Depth Strategy
- [How the game creates visual layers — not "always glassmorphism" but what makes sense]
- [E.g., "layered paper cutout effect" for a storybook game]
- [E.g., "holographic overlay" for a sci-fi game]
- [E.g., "no depth effects — flat and minimal" for a zen game]
```

---

## Universal Principles (apply to ALL games, regardless of style)

These aren't visual rules — they're UX fundamentals that human designers always follow:

### 1. Visual Hierarchy Tells You Where to Look

The most important element on screen is visually dominant.
The primary action button is the most prominent element on the game screen.
Secondary elements are visually quieter.

How to achieve this varies by game:
- Size difference (primary button 2x larger)
- Color saturation (primary is saturated, secondary is muted)
- Position (primary in thumb-reach zone on mobile)
- Animation (primary has subtle motion, secondary is static)

### 2. The 60-30-10 Layout

- 60% of the game screen → the core game area (reels, grid, play field)
- 30% → controls and information (HUD, buttons, score)
- 10% → atmosphere and decoration (background elements, ambient effects)

### 3. Every Interactive Element Has Feedback

No button should feel "dead." When you tap it, something happens visually.
But the TYPE of feedback matches the game:
- A heavy mechanical game → buttons push in with weight
- A light casual game → buttons bounce playfully
- A sleek modern game → buttons highlight with a subtle glow
- A retro game → buttons flash like old arcade machines

### 4. Numbers That Change Should Animate

Balance, score, bet, timer — when a number changes, it transitions smoothly.
The animation style matches the game:
- Casino → fast rolling counter (slot machine feel)
- Puzzle → satisfying pop-up with scale
- Idle → smooth count-up (satisfying accumulation)

### 5. States Should Be Visually Distinct

The player should always know:
- Can I interact right now? (idle vs. playing/animating)
- What just happened? (win vs. loss vs. neutral)
- Where am I? (which screen, how to go back)

### 6. Loading and Empty States Have Personality

Loading: not a generic spinner, but something that fits the game
(a spinning coin, shuffling cards, a bouncing ball — or just a themed progress bar)

Empty states: not blank, but a prompt that fits the game's voice
("Your treasure chest is empty — play to fill it!" vs "No data")

### 7. Transitions Reinforce Context

Screen transitions aren't just "fade" or "slide" — they connect to the game's world.
But they also shouldn't be 2-second elaborate animations. Speed matters.

**Quick transitions (200-400ms)**: for snappy, fast-paced games
**Medium transitions (400-600ms)**: for standard flow
**Elaborate transitions**: only for dramatic moments (entering bonus round, mega win)

---

## What NOT To Do (Anti-Patterns)

### Don't: Apply the Same Style to Every Game

If every game from this studio has Orbitron font, neon glow, and skewed trapezoid buttons —
that's OUR version of slop. Each game should feel like itself.

### Don't: Over-Design Simple Games

A minimalist dice game doesn't need glassmorphism, particle backgrounds, and 5 custom fonts.
Sometimes the most human choice is restraint. A simple game with clean design
and one perfect animation is better than a simple game drowning in effects.

### Don't: Add Effects Without Purpose

Every visual effect should answer: "What does this communicate to the player?"
- Glow on a button → "This is interactive / important"
- Particles on win → "Celebration! You did well!"
- Screen shake → "Big impact! Something significant happened!"
- Blur background → "Focus on this modal/overlay"

If you can't explain what the effect communicates → remove it.

### Don't: Use Default Framework Widgets Without Thought

This doesn't mean "replace everything with custom widgets."
It means: if you use a Material `Switch`, make sure it fits the game.
A neon game might want a custom glowing toggle.
A clean minimal game might want a slightly restyled standard Switch.
The point is intention, not replacement.

---

## Centralized Animation Timings

All durations and curves MUST be centralized in `lib/theme/animations.dart`.
No hardcoded `Duration(milliseconds: 300)` scattered through components.

```dart
class AnimationConfig {
  // Durations — adjust per game feel
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration medium = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration screenTransition = Duration(milliseconds: 400);

  // Curves — adjust per game weight
  static const Curve buttonPress = Curves.easeInOut;
  static const Curve numberChange = Curves.easeOutCubic;
  static const Curve screenEnter = Curves.easeOutQuart;
  static const Curve screenExit = Curves.easeInQuart;
}
```

---

## Required Screens (12+ for a complete game)

These screens are required because players EXPECT them, not because of a checklist:

1. **Splash Screen** — first impression, sets the mood (1-2 sec)
2. **Main Menu** — home base, navigation hub
3. **Game Screen + HUD** — the core experience
4. **Rules / Paytable** — players need to understand the game
5. **Settings** — sound, vibration, preferences (persisted)
6. **Help / How to Play** — onboarding for new players
7. **Win Celebration** — reward the player (scaled to win size: small/big/mega)
8. **Insufficient Funds / Game Over** — handle failure gracefully
9. **Daily Bonus** — retention mechanic
10. **Leaderboard / Stats** — progress and competition
11. **Player Profile** — identity and personalization
12. **Loading States** — never show a blank screen

The VISUAL DESIGN of each screen should come from the game's Design DNA.
A pirate game's settings screen looks different from a cyberpunk game's settings screen.

---

## Design DNA Validation (used in /ui-audit)

Instead of checking for specific widgets or effects, validate that:

- [ ] The game has a written Design DNA with justified color/shape/typography choices
- [ ] Colors have REASONS tied to the game's theme (not just "looks nice")
- [ ] Typography fits the game's mood (not defaulting to Orbitron or system font)
- [ ] The primary action button is the most visually prominent element on game screen
- [ ] Different functional elements look different (buttons vs info panels vs decorations)
- [ ] Interactive elements have feedback that matches the game's "weight"
- [ ] Numbers animate when they change
- [ ] Transitions between screens exist and relate to the game's world
- [ ] Loading states have personality (not generic spinner)
- [ ] Empty states guide the player (not blank)
- [ ] Effects serve a purpose (each glow/particle/blur communicates something)
- [ ] The design wouldn't make sense in a DIFFERENT game (it's specific to this one)
- [ ] Animation timings are centralized (not hardcoded in each widget)
- [ ] No default Material/Cupertino widgets used without intentional customization
- [ ] The overall visual identity is CONSISTENT across all screens
- [ ] 12+ screens/overlays exist with full implementation
