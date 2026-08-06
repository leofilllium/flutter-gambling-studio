# Layout Archetypes — compositional variety across screens

> **The problem this solves:** even with a unique Design DNA (colours/fonts/shapes), games come
> out looking alike because the COMPOSITION of the screens is always the same: HUD on top, a big
> button bottom-centre, a menu that is a vertical stack of buttons. The 5 structure variants
> (`directory-structure.md`) change WHERE the files live — not how a screen LOOKS. This document
> adds variety to the composition itself.

A **Layout Archetype** is a system for placing elements (where the HUD goes, where the main
action goes, how the menu is assembled, how overlays enter). Art direction (palette, fonts,
shapes) comes from the concept's **Design DNA**. The two axes are independent: the same layout
archetype with a different DNA produces completely different games, and vice versa.

```
Game = Layout Archetype (HOW it is composed) × Design DNA (HOW it looks) × Archetype A–AF (WHAT the mechanic is)
```

In `/autocreate` the layout archetype is chosen pseudo-randomly (like the structure) and
recorded in `design/art-direction.md`. `ui-programmer` reads it and composes the screens
accordingly.

---

## Invariants (upheld in EVERY archetype)

The archetype changes the composition but does NOT break the baseline UX:

- The main action sits in the thumb zone (the bottom 60% of the screen on mobile).
- Tap targets ≥ 48×48 on every interactive element.
- SafeArea on every screen except the fullscreen GameScreen.
- The play field remains the main focus of the game screen (≈60% of the area).
- Visual hierarchy: the main action is the most prominent element.
- Back navigation works from every screen.

---

## L1 — Classic Stack (top HUD / bottom panel)

The familiar mobile layout. The safe default.

- **Main menu:** a hero logo top-centre → a vertical stack of buttons beneath it. PLAY is large and dominant.
- **Game screen:** a thin HUD bar pinned to the top (balance/score/settings), the play field in the centre, the control panel and main action pinned to the bottom.
- **Action button:** centred in the bottom panel, the largest element.
- **Overlays:** toasts from the bottom above the panel; modals centred with a light scrim.
- **Transitions:** a smooth fade-through or slide-up.

## L2 — Bottom Command Deck

The whole "dashboard" is gathered into a dense bottom console; the field stretches to the edges above it.

- **Main menu:** large art/scene on top (≈55%), a sliding mode panel (bottom sheet) below with the start button.
- **Game screen:** the play field edge-to-edge on top, a pronounced console deck below carrying the HUD, the bet/controls and the main action as one block.
- **Action button:** built into the deck, set apart by colour or size relative to its neighbours.
- **Overlays:** slide up out of the deck; modals are bottom sheets with a rounded top.
- **Transitions:** sheet slide-up; the deck "breathes" during transitions.

## L3 — Floating Corners (minimal chrome)

No bars. Small floating widgets in the corners, the field full-bleed.

- **Main menu:** full-bleed art/scene across the whole screen, one central CTA, small settings/info icons in the corners.
- **Game screen:** the field fills the screen; balance/score is a floating chip in one top corner, settings in the opposite one, and the main action is a large floating button (FAB style) bottom-centre or in the thumb corner.
- **Action button:** floating, with a pronounced shadow or outline so it reads over the field.
- **Overlays:** pop out from the relevant corner; modals are compact centred cards.
- **Transitions:** scale/fade from the point of origin.
- ⚠️ Contrast between the floating elements and the field is mandatory (a backing plate, an outline or a shadow) — otherwise it is unreadable.

## L4 — Side Rail

A vertical panel along one side holds the controls and HUD; the field takes the rest. Good for wide screens and web.

- **Main menu:** title and subtitle aligned to one edge, a rail of menu items on the other side.
- **Game screen:** a narrow vertical rail at one edge (HUD + main action + quick buttons), the play field takes the remaining width.
- **Action button:** at the top or centre of the rail, visually larger than the rail's other buttons.
- **Overlays:** slide out from the rail side; modals are centred over the field.
- **Transitions:** horizontal slide, with the rail staying stable.
- ⚠️ On a narrow portrait screen the rail must not eat the play field — make it compact or collapsible.

## L5 — Split Panel (two zones)

The screen is explicitly split into two zones with different surfaces.

- **Main menu:** the upper zone is art/preview, the lower zone (a different surface) is the mode menu.
- **Game screen:** the top ≈60% is the play field, the bottom ≈40% is an information panel on its own surface (rules/history/controls + the main action).
- **Action button:** in the info panel, as the accent.
- **Overlays:** expand within the lower panel, or over both zones for major events.
- **Transitions:** the zones can animate separately (cross-fade on top, slide below).

## L6 — Card / Sheet Stack

Content lives on rounded cards or sheets that replace one another.

- **Main menu:** a horizontal carousel of mode cards; swipe to choose a mode, tap to start.
- **Game screen:** the play field on the main card; a thin HUD "pill" on top; controls on a floating sheet below.
- **Action button:** on the lower sheet, or as the accent on the card itself.
- **Overlays:** new cards ride over the stack; modals are a rising sheet.
- **Transitions:** cards slide and overlap (shared axis), with depth from layered shadows.

---

## How the archetype is chosen (in /autocreate)

In Phase 2, alongside the project structure, the layout archetype is chosen:

```python
import time
layout = ["L1", "L2", "L3", "L4", "L5", "L6"][(int(time.time() // 7) % 6)]
```

It is recorded in `design/art-direction.md`. On a `--from-concept` run it is taken from the
**Layout & Composition Direction** section of the concept (see `auto-idea`).

> **Not to be confused with the DNA.** The archetype says "the HUD is in a bottom deck"; the DNA
> says "the deck is warm wood with brass buttons" or "the deck is cold matte metal with
> backlighting". Choose the composition (the archetype) first, then dress it in the DNA. Never
> apply the same art style (neon/glass) to every game — that is exactly what slop is.
