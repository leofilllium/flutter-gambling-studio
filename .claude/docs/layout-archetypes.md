# Layout Grammar — compositional variety without whole-game templates

> The old L1-L6 catalog selected one complete layout for an entire game. That produced a small
> number of recurring shells: top HUD plus bottom controls, command deck, floating corners, rail,
> split panel, or sheets. Changing the theme did not change the interaction architecture.
>
> The replacement is a grammar. Choose independent ingredients for each important screen and
> gameplay state, then connect them with one Design Signature. The result is coherent without
> forcing every screen, or every game, through one composition.

```
Game UI = mechanic and state needs
        × per-screen composition recipe
        × Design Signature
        × mobile/expanded reflow
```

## Invariants

Every recipe still follows the product contracts:

- phone-first, touch-first, full-viewport layout;
- tap targets at least 48x48 logical pixels;
- safe-area protection for essential controls and text;
- the live field is the first read, meets `gameplay-screen-contract.md`, and does not require
  page scrolling with its core controls;
- no phone mockup, nested mini-game window, unrelated information card, or fixed-width phone strip;
- a visible primary action or direct-manipulation affordance in thumb reach;
- a reliable back path and supported-input focus order;
- intentional medium/expanded reflow instead of blind scaling.

These invariants define usability, not aesthetics. They do not prescribe a top bar, centered
button, dark background, card surface, or any particular field alignment.

## Recipe axes

Choose one primary option per axis for each key screen. Add a secondary option only when the
state change genuinely needs it. The codes make plans concise; they are not prefab widgets.

### F — field or subject framing

| Code | Direction | Good fit | Watch for |
|---|---|---|---|
| F1 | Full-bleed stage | physics, crash, scenic originals | HUD contrast over moving art |
| F2 | Bounded game object | reels, boards, tables, scratch cards | object must dominate, not become a card in a card |
| F3 | Tabletop / angled plane | cards, dice, coin objects | perspective must preserve readable targets |
| F4 | Split relationship | spin plus progress/world, risk plus reward | neither side may become a thumbnail |
| F5 | Layered diorama | collection/progression with spatial depth | keep critical interaction on a stable plane |
| F6 | Instrument / cabinet | mechanical or diegetic controls | avoid ornamental chrome stealing field space |

### C — control topology

| Code | Direction | Description |
|---|---|---|
| C1 | Attached | Controls are physically or visually attached to the field/object they affect. |
| C2 | Thumb dock | A compact lower control cluster; it need not span the screen or look like a panel. |
| C3 | Edge rail | Controls occupy one safe edge and may move to a side on wider viewports. |
| C4 | Distributed | Small controls sit near their consequences, with one clear recurring action. |
| C5 | Direct manipulation | Drag, scratch, place, aim, or choose on the field; chrome is secondary. |
| C6 | Context action | The primary action changes with state in one stable location. |
| C7 | Radial / spatial choice | Options surround an object or decision point when direction has meaning. |

### H — HUD behavior

| Code | Direction | Description |
|---|---|---|
| H1 | Edge anchors | A few stable readouts occupy protected corners/edges without a full bar. |
| H2 | Compact strip | Related persistent values share one quiet strip. |
| H3 | Embedded | Values live on the machine, table, board, character, or other world object. |
| H4 | Contextual | Information appears for setup/result/risk states and recedes afterward. |
| H5 | State panels | The same zone swaps its content as the round advances. |
| H6 | Dense tactical | More information stays visible because comparison is the mechanic. |

### M — menu and hub structure

| Code | Direction | Description |
|---|---|---|
| M1 | Poster / title composition | A focused title/action composition; can be quiet or theatrical. |
| M2 | Interactive scene | World objects or hotspots are navigation. Include clear text/focus fallbacks. |
| M3 | Machine facade | The game object itself holds Play and secondary entries. |
| M4 | Map / path | Progress locations form the menu and make goals spatial. |
| M5 | Shelf / collection | Modes or content are physical/displayed objects, not equal cards by default. |
| M6 | Editorial split | Copy/identity and playable preview or choices share an intentional split. |
| M7 | Compact conventional | A clear list/grid used when speed and scanability matter more than spectacle. |

### O — overlay and secondary-surface behavior

| Code | Direction | Description |
|---|---|---|
| O1 | Local callout | Feedback stays near the object or control that caused it. |
| O2 | Edge sheet | Secondary detail enters from the nearest safe edge. |
| O3 | Center dialog | Short blocking decisions only; restore focus on close. |
| O4 | Object-led reveal | A chest, card, capsule, door, meter, or board element carries the reveal. |
| O5 | Full-state takeover | Major result/bonus changes the whole scene, proportionate to importance. |
| O6 | Dedicated screen | Long rules, odds, settings, collection, and history get readable space. |

### R — expanded-viewport reflow

| Code | Direction | Description |
|---|---|---|
| R1 | Grow the field | Extra space primarily enlarges or reveals more of the mechanic/world. |
| R2 | Relocate controls | A phone dock becomes a side attachment or rail while meaning stays stable. |
| R3 | Add supporting zone | History, build detail, or progression appears beside the dominant field. |
| R4 | Rebalance a split | The same two subjects change proportion/orientation at content breakpoints. |
| R5 | Reveal environment | Art/world expands while critical UI holds a readable max measure. |

## Building recipes

The plan must define recipes for at least the main menu, live setup/idle, active/anticipation,
result, and one information-heavy secondary screen. Other screens may reuse a recipe when their
jobs are genuinely similar.

```markdown
## Layout & Composition Direction

### Main menu — M3 + O2 + R5
- Why: [the machine is the brand and the menu; secondary entries remain discoverable]
- Compact: [phone composition and thumb path]
- Expanded: [what grows, moves, or becomes visible]

### Live setup — F2 + C1 + H4 + O1 + R1
- Attention order: [field -> wager control -> action]
- Persistent/contextual information: [...]
- Primary field alignment: [centered | intentionally offset because ...]

### Anticipation — F2 + C6 + H4 + O1 + R1
- What changes from setup: [...]
- What stays spatially stable: [...]

### Result — F2 + C6 + H5 + O4 + R1
- Win/loss attention shift: [...]
- Return-to-play path: [...]

### Rules/odds — M7 + O6 + R3
- Scan and disclosure strategy: [...]

### Viewport proof
- Phone: [360x640, 360x800, 390x844, 430x932]
- Expanded: [844x390, 768x1024, 1024x768, 1440x900]
```

This example is syntax, not a recommended combination. Do not copy it into every concept.

## Coherence rules

- Keep semantic color roles, typography roles, material logic, input meanings, and navigation
  behavior consistent across recipes.
- Keep one or two stable landmarks across adjacent round states so the player perceives change,
  not a new screen teleport.
- Do not make every screen spatially unique. Variation follows job differences, not novelty quotas.
- Do not make every screen structurally identical. Menu, live round, dramatic result, and dense
  information do different work and usually need different recipes.
- A vertical button list, centered field, bottom dock, or modal is allowed when it is the clearest
  answer. It becomes slop when it appears by habit and is merely reskinned.

## Selection process

1. Map gameplay states and information priority from `.claude/rules/anti-slop-design.md`.
2. Choose a field/subject frame from the mechanic's physical or conceptual structure.
3. Choose controls based on the repeated input, hand posture, and action frequency.
4. Choose HUD behavior based on when information is needed, not where a template has space.
5. Choose overlays by interruption level and content length.
6. Define compact composition first, then choose an expanded reflow strategy.
7. Compare the resulting recipes with recent/nearest games. If the same F+C+H+M combination
   recurs, either justify it from the mechanic/reference or choose a stronger alternative.
8. Record the recipes and Similarity Check in `design/art-direction.md`.

Random selection is allowed only between equally suitable choices after this reasoning. A clock-
based roll is not a design method.

## Reference-mapped games

When `.claude/docs/game-concept-examples.md` maps the request to a local preview, read the preview's
actual framing, controls, HUD, menu, overlays, and responsive implications. Record those as recipes
without forcing them into a different combination for variety. The reference contract outranks the
anti-repeat gate; exact pixels, title/logo, and paytable numbers remain excluded as documented.

## Deprecated L1-L6 behavior

Do not select one L1-L6 archetype for a new game. Existing concepts that already record L1-L6 may
be implemented for backward compatibility, but convert them into explicit per-screen recipes when
the project is next redesigned. The old names are not accepted as sufficient art direction because
they omit state changes, information behavior, and expanded reflow.
