# Mobile-First Full-Viewport Contract

Every game produced by this studio is **designed for a mobile phone first**. Phone ergonomics,
touch interaction, compact hierarchy, and the portrait phone composition are the starting point.
This is not a request to draw a phone frame or restrict the app to phone-sized windows: the game
must also fill and adapt to the available viewport on tablets, landscape devices, desktop
browsers, and other supported hosts.

## Product principle

- Start with the smallest supported phone layout. Do not begin from a desktop dashboard and
  collapse it afterward.
- Keep every essential action touch-friendly and usable without hover, a mouse, or a keyboard.
- Let the root app, backdrop, routes, dialogs, overlays, and gameplay surface use the full
  available viewport. Never wrap the product in a fixed-width phone canvas or fake device bezel.
- Progressively enhance larger viewports with more room for the mechanic, wider spacing,
  repositioned controls, or an intentional multi-zone composition. Preserve the same game,
  hierarchy, and core loop rather than creating an unrelated desktop edition.
- Web is a supported full-viewport host and the primary Chrome/CDP verification target.
- Create Flutter platforms with `--platforms web,android,ios`. Add desktop platform scaffolds only
  when a project explicitly needs native desktop packaging; Web still has to work at desktop size.

## Required viewport matrix

The phone matrix defines the canonical design baseline:

| Viewport | Purpose |
|---|---|
| 360×640 | short/compact Android phone |
| 360×800 | tall compact Android phone |
| 390×844 | canonical phone capture target |
| 430×932 | large phone portrait |

The expanded matrix proves that the same app uses the whole host responsibly:

| Viewport | Purpose |
|---|---|
| 844×390 | phone landscape / short wide viewport |
| 768×1024 | tablet portrait |
| 1024×768 | tablet or compact desktop landscape |
| 1440×900 | desktop/Web fullscreen |

All eight sizes are layout gates. Phone screenshots remain the primary design and storefront
reference, but an expanded viewport may not show a narrow centered phone strip surrounded by
unused space.

## Responsive composition

Use content-driven breakpoints rather than device labels. A practical baseline is:

- **Compact**: below 600 logical pixels wide. Use the canonical single-column, thumb-reachable
  mobile composition.
- **Medium**: 600–1023 logical pixels wide. Expand the mechanic and spacing; move secondary
  content beside the field when that improves balance and keeps the primary action obvious.
- **Expanded**: 1024 logical pixels and wider. Use the full canvas with an intentional grid,
  side rail, or multi-zone layout. Do not merely scale text and controls until they become huge.

These thresholds are defaults, not hard device detection. `LayoutBuilder`, available height,
safe-area insets, text scale, and the mechanic's aspect ratio decide the final composition.

The background should normally extend edge to edge. Long-form rules or settings content may use a
readability `maxWidth`, but the app root and live game must not use a phone-sized global cap.
Use `Expanded`, `Flexible`, `AspectRatio`, `FittedBox`, `Wrap`, and deliberate reflow to avoid
stretching, clipping, or dead margins.

## Orientation and native targets

Responsive behavior is the default. Do not add a global Flutter portrait lock, an Android
`screenOrientation="portrait"` restriction, or an iPhone-only Xcode device-family restriction as
a studio invariant. Android phones/tablets, iPhone/iPad, and Web should receive the layouts their
available viewport supports.

A specific game may constrain orientation only when its mechanic genuinely requires it and the
decision is explicitly recorded in `design/gdd/game-concept.md` and an ADR. That exception must
not be used to avoid implementing the expanded viewport matrix.

Secondary informational screens may scroll when necessary. The gameplay core may not require page
scrolling; follow `gameplay-screen-contract.md`.

## Blocking failures

Treat these as HIGH defects and release blockers:

- a global 430-pixel (or similar phone-width) cap, `phoneViewport` wrapper, phone mockup, or bezel;
- blank side regions caused by keeping product UI inside a centered mobile strip;
- overflow, clipping, unreachable actions, or distorted fields at any required viewport;
- hover-only, pointer-only, or keyboard-only essential interaction;
- an expanded layout that loses the mobile hierarchy or makes the mechanic secondary;
- forced portrait or iPhone-only native targeting without the documented mechanic exception.
