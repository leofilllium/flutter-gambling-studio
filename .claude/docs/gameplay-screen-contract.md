# Gameplay Screen Contract — Full-Viewport, Integrated, Mobile-First

This contract prevents a working mechanic from being presented as a small demo embedded inside
a generic app page. It applies to every C1–C6 `GameScreen`, regardless of Design DNA or Layout
Archetype.

The product canvas is defined by `.claude/docs/mobile-first-contract.md`: phone UI/UX is the
canonical starting point, and the same game must fill and adapt to landscape, tablet, desktop,
and Web viewports without becoming a framed phone preview.

## Required composition

1. **The gameplay screen owns the viewport.** Use an edge-to-edge game backdrop and compose the
   play field, HUD, and controls as one screen. Safe-area insets protect interactive chrome; they
   must not shrink the whole game into a second framed window.
2. **The mechanic is the dominant surface.** At the phone verification sizes, the visible
   play field should occupy at least 55% of the usable viewport and normally at least 88% of its
   width. A narrow-mechanic or portrait thumb-rail exception is allowed only when
   `design/art-direction.md` records why it improves play; the field must still be the first focal
   point and use all remaining space. At expanded sizes, grow or recompose the mechanic and its
   supporting zones so the full viewport feels intentional rather than padded around a phone UI.
3. **No nested mini-game.** Do not place the live field inside a phone-like window, browser-like
   frame, isolated card, tall decorative bezel, or large padded container floating above an
   unrelated information card. A thematic rim, cabinet, table edge, or board boundary is fine
   when it belongs to the mechanic, hugs the field, and does not create large dead margins.
4. **Integrate HUD and controls.** Attach compact controls to the field as overlays, an edge rail,
   or one deliberate command deck. Reuse the field's alignment grid, materials, shapes, and
   depth. A generic panel stacked below an unrelated game rectangle fails.
5. **The core loop never requires page scrolling.** The live field, primary action, balance or
   score, stake/risk control, and result feedback must be visible together on the first viewport.
   Rules, history, explanations, and secondary configuration may open a sheet or separate screen.
6. **Controls are proportioned and usable.** Every tap target is at least 48×48 logical pixels;
   the primary action is at least 56 logical pixels high, within thumb reach, visually dominant,
   and has idle, pressed, active, and disabled states. Labels must fit at 1.0× and 1.3× text scale.
   Secondary buttons share height, baseline, spacing, and shape logic; disabled controls remain
   legible and clearly unavailable.
7. **Use responsive constraints, not screenshot-specific pixels.** Prefer `Stack`,
   `Positioned`, `Align`, `Expanded`, `Flexible`, `AspectRatio`, and `LayoutBuilder`. Reserve
   fixed dimensions for icons, tap targets, borders, and spacing tokens.

## Required implementation hooks

Add stable keys so widget tests and runtime audits can measure the actual hierarchy:

- `Key('gameplaySurface')` on the live field/board/reels/physics surface.
- `Key('primaryAction')` on the main Spin/Play/Drop/Collect control.
- `Key('controlDeck')` on the compact group of core controls, when one exists.

Do not put `gameplaySurface` or `primaryAction` under a vertical `Scrollable`. Do not solve a
small-screen overflow by making the entire game screen scroll; recompose or collapse secondary
content instead.

## Verification matrix

Check at minimum:

| Viewport | Purpose |
|---|---|
| 360×640 | short/compact Android phone |
| 360×800 | tall compact Android phone |
| 390×844 | standard capture/runtime target |
| 430×932 | large phone portrait |
| 844×390 | phone landscape / short wide viewport |
| 768×1024 | tablet portrait |
| 1024×768 | tablet or compact desktop landscape |
| 1440×900 | desktop/Web fullscreen |

For each size, verify:

- no overflow, clipping, accidental letterboxing, or large unexplained dead zone;
- the field is visually dominant and not a thumbnail or nested app window;
- the primary action and essential counters are visible without scrolling;
- controls do not overlap the field's critical interaction zone;
- control labels fit, tap targets meet the minimum, and enabled/disabled states are clear;
- the field, HUD, and controls read as one game-specific composition.

Capture the idle and active game states at 390×844 and 1440×900, plus any breakpoint where the
composition changes materially. A visual audit is mandatory; clean analyzer output and widget
tests alone cannot approve composition.

Opening the Web build in a wide browser must use the full browser viewport. Reflow controls,
supporting information, and the field deliberately; do not center a phone-width product canvas,
draw a device frame, or blindly stretch every element.

## Blocking failures

Treat any of these as a HIGH layout defect and a release blocker:

- the field resembles a small window inside the app screen;
- the field is below the size thresholds without a documented mechanic-driven exception;
- core gameplay requires vertical scrolling;
- a large instruction/progression card competes with or is larger than the field;
- core buttons are cramped, uneven, clipped, off-screen, or visually disconnected;
- the store showcase needs cropping or concept art to hide weak gameplay composition.
- an expanded viewport shows a centered phone strip, unexplained dead margins, or oversized
  controls instead of an intentional responsive composition.

Implementation must recompose the screen before handoff. Finalization must fail and route the
screen back through `/ui-audit --fix` or `/autocreate-implement --resume`; it must not downgrade
these failures to cosmetic concerns.
