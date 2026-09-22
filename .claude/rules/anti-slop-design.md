# Game UI Direction — Distinctive, Usable, Non-Templated

> Anti-slop is not a visual style. It is a decision process that prevents an agent from
> reusing an unexplained UI shell. A restrained centered layout can be excellent. An asymmetric
> layout can be generic. Glass, cards, gradients, dark mode, large type, and custom shapes are
> neither quality signals nor failures by themselves.
>
> A game passes when its interface expresses its mechanic, world, audience, and moment-to-moment
> states; remains usable on every required viewport; and is materially different from nearby
> studio output for reasons stronger than a new palette.

## 1. Precedence: contracts first, creative choices second

Hard contracts are not optional:

- the user's brief and supplied reference;
- gambling classification, math truth, and responsible-play requirements;
- `.claude/docs/mobile-first-contract.md` and `.claude/docs/gameplay-screen-contract.md`;
- readable text, safe areas, touch targets, keyboard/controller focus, reduced motion, and
  non-color-only state communication;
- the studio asset rendering baseline below.

Everything else is a contextual choice. No studio preference for centered or asymmetric
composition, one or many accent hues, flat or dimensional surfaces, sparse or dense information,
rounded or angular geometry, light or dark presentation, or quiet or theatrical motion may be
promoted into a universal rule.

When rules conflict, protect gameplay truth and usability before visual novelty. Distinctiveness
never excuses a hidden action, unreadable HUD, misleading outcome, cramped phone layout, or broken
expanded layout.

## 2. Start with a Game UI Read

Before choosing tokens or arranging widgets, write a concise read in `design/art-direction.md`:

```markdown
## Game UI Read
- Player and session: [who, posture, likely session length, one-handed/two-handed]
- Core decision: [what the player decides repeatedly]
- Emotional arc: [setup -> commitment -> anticipation -> result -> recovery/progression]
- Information pressure: [what must be known instantly; what can wait]
- World and tone: [specific fiction and attitude, not a generic adjective list]
- Reference contract: [exact reference to match, or patterns borrowed from named examples]
- Constraints: [category, accessibility, viewport, input, compliance]
- Memorable interface idea: [one interaction or spatial idea the player will remember]
```

This is the game equivalent of reading the room. Do not choose an aesthetic at random and invent
a justification afterward. If an explicit reference maps to the request, match its theme, cast,
palette, board, and composition as required by `.claude/docs/game-concept-examples.md`; the
anti-repeat gate does not authorize drifting away from that reference.

## 3. Define a Design Signature, not a skin

Keep two related records. **Asset/World Design DNA** defines the fiction, subjects, silhouette
language, materials, lighting, and illustration palette used by asset production. The **Design
Signature** below defines interaction and interface behavior. They must agree, but one must not be
used as a shortcut for the other: a new mascot or palette does not create a new interface.

Record a choice and a mechanic- or world-based reason for every axis. The examples are vocabulary,
not a menu of defaults.

| Axis | Possible directions |
|---|---|
| Field framing | full-bleed stage, bounded board-object, tabletop, cabinet, split world, layered diorama |
| Control topology | attached controls, thumb dock, edge rail, distributed controls, radial choice, direct manipulation |
| HUD behavior | persistent glanceable, contextual reveal, state-bound, diegetic, embedded in the field |
| Information density | sparse and staged, steady casual, dense strategic, progressive disclosure |
| Navigation model | scene hotspots, map/path, shelves, tabs, carousel, compact list, object-led hub |
| Geometry | orthogonal, circular, pillowy, cut-corner, irregular crafted, mixed by documented role |
| Surface and material | ink/paper, enamel toy, carved material, painted wood, metal instrument, glass, flat color |
| Type voice | quiet humanist, loud display, condensed utility, storybook, technical, arcade, mixed by role |
| Color/value logic | high-key, low-key, monochrome-plus-signal, complementary, multicolor, material-led |
| Motion and feedback | immediate/minimal, weighted mechanical, elastic toy, staged theatrical, flowing, deliberately still |
| Depth model | flat graphic, shallow layers, modeled 2.5D, deep scenic, selective overlay |
| Sound/haptics | dry clicks, soft tactile, mechanical, musical, percussive, restrained |

A signature is the combination and its rationale. “Purple, rounded, playful” is not a signature.
“The wager dial is physically attached to the submarine console; pressure information emerges
around the porthole only during the climb” is.

Use semantic tokens, but do not freeze their count across games. A candy gacha may need a broad
controlled palette; a precision crash game may need one signal color. A dense roguelike may need
more type roles than a one-button original. Cohesion comes from role discipline, not arbitrary
limits such as exactly five colors, one accent, or four-to-six font sizes.

## 4. Compose around gameplay states

One layout does not govern an entire game. Design each key state around its job while keeping the
signature coherent.

For every key screen/state, record:

```markdown
### [State or screen]
- Job: [the one thing this state must help the player do]
- Attention order: [first -> second -> third]
- Mechanic/subject: [what owns the most meaningful space]
- Primary input: [tap, drag, hold, choose, set value, inspect]
- Persistent information: [only what is needed throughout]
- Contextual information: [what appears for this state, then leaves]
- Composition recipe: [field frame + controls + HUD + overlay + expanded reflow]
- Transition reason: [feedback, hierarchy, continuity, or anticipation]
```

Map at least setup/wager, commitment, anticipation, resolution, celebration/loss, and recovery.
The focal order may change between states. A win may temporarily replace the action as the first
read; a risk choice may deliberately share attention between probability and reward. “One focal
point” is useful diagnosis, not a rule that erases meaningful tension.

Use progressive disclosure. The live round shows what is needed now; rules, history, probability
detail, collections, and configuration remain reachable without competing with the mechanic.
HUD elements should be event-driven and may be persistent, contextual, or embedded according to
the game. Do not poll state each frame merely to keep the HUD current.

### Category prompts

- **C1 social casino:** establish the reel/table/board as the spectacle. Controls may be embedded
  in a machine, attached to a table edge, distributed like chips, or gathered in a dock. Do not
  assume “top HUD + bottom panel.”
- **C2 casino originals:** make the recurring risk decision the protagonist. Put probability,
  trajectory, or selectable risk next to the action it affects; hide secondary history until asked.
- **C3 spin-to-progress:** show the relationship between the current spin and the world/progression
  it changes. Avoid presenting the spin as a generic widget above an unrelated progress card.
- **C4 gacha:** separate summon theatre, collection management, banner/rate inspection, and result
  handling. They need related art direction but not the same card grid.
- **C5 casino roguelike:** support fast comparison of risk, build state, and consequence. Dense is
  valid when hierarchy and touch navigation remain excellent.
- **C6 coin pusher/plinko:** preserve a readable physics field and place wager/drop controls where
  they do not obscure trajectories or buckets. The board, not a decorative dashboard, leads.

## 5. Use a compositional grammar, not a complete template

Build a per-screen recipe from independent choices documented in
`.claude/docs/layout-archetypes.md`: field framing, control topology, HUD behavior, menu structure,
overlay behavior, and expanded-viewport reflow. A game may use different compatible recipes for
its menu, live round, result, collection, and settings screens.

Variation must not harm orientation. Reuse navigation placement, input meanings, semantic tokens,
and feedback rules when consistency helps the player. Vary the spatial solution when the screen's
job changes. Settings may be conventionally structured because scanability matters; the main menu
may be a poster, scene, map, machine facade, shelf, or quiet typographic composition. Neither needs
to be forced into a card grid.

## 6. Anti-repeat gate

Before approval, compare the proposed signature with up to three recent or closest studio games
available in project concepts, art-direction files, session artifacts, or `examples-games/`.
Record the comparison in `design/art-direction.md`.

```markdown
## Similarity Check
Compared with: [games/references]
Repeated intentionally: [patterns required by mechanic, platform, or explicit reference]
Material differences: [at least four signature axes, with concrete descriptions]
Nearest-neighbor risk: [what could still make the games feel alike]
Correction: [what changed, or why no change is appropriate]
```

For an original, non-reference-mapped concept, palette and asset swaps do not count as material
differences. Sharing field framing, control topology, HUD behavior, menu structure, and motion
cadence is a likely duplicate even if the theme is different. Change at least four signature axes
from the closest game unless the mechanic or platform makes a repeated choice demonstrably better.
Randomness may break a tie between equally appropriate directions; it may not replace judgment.

## 7. Craft floor without a house style

### Hierarchy and grouping

- Use size, position, value, spacing, motion, and sound to create an intentional attention order.
- Group by task and timing, not because every item fits inside a card.
- Cards, borders, shadows, glow, blur, and ornaments exist only when they clarify grouping, depth,
  interaction, or state.
- Alignment may be symmetric or asymmetric, but shared edges and optical balance must look chosen.

### Typography and numbers

- Define semantic roles such as display, balance, action, body, caption, and legal. Roles may share
  a family when that is the strongest choice.
- Prioritize readability, glyph coverage, numeric clarity, and text scaling over novelty.
- Animate a changing number only when the change itself matters. Update stable utility values
  directly; do not make every counter roll because it can.
- Let containers size to content. Player-facing strings must survive 1.3x text scale and likely
  localization expansion without clipping.

### Color, value, and dynamic backgrounds

- Assign colors to roles. Do not set a universal accent count or saturation ceiling.
- Encode critical states with shape, icon, pattern, position, or text as well as color.
- Test HUD text and controls over the brightest, darkest, and busiest gameplay frames. Use a
  local backing plate, outline, shadow, or scrim when the world beneath is unpredictable.
- Preserve one lighting logic across generated art and UI materials.

### Interaction states

Every interactive control needs idle, focus/hover where applicable, pressed, disabled, and
loading/committed behavior. Touch feedback begins immediately. Dangerous or irreversible actions
need separation and confirmation appropriate to their risk. Empty, error, locked, insufficient-
funds, interrupted, and offline states must tell the player what happened and what to do next.

### Motion, haptics, and celebration

- Every motion must communicate feedback, hierarchy, continuity, anticipation, or outcome.
- Input acknowledgement is immediate; ordinary UI transitions are brief; dramatic outcome
  sequences may be longer when they are proportional to the event and do not delay repeated play.
- Keep world shake out of stable HUD/readout layers. Offer reduced motion and reduced flashing;
  collapse large travel, parallax, bounce, and shake to quiet fades or direct state changes.
- Centralize timings and curves in `lib/theme/animations.dart`, but derive their values from this
  game's motion character. Do not copy one timing preset to every game.

## 8. Mobile, expanded layouts, and input

- Design the compact phone state first with real thumb reach and 48x48 minimum touch targets.
- Protect essential UI with `SafeArea`/reported insets while allowing noncritical art to bleed.
- Use anchors, constraints, and containers rather than screenshot-specific coordinates.
- At medium and expanded widths, recompose: grow the mechanic, relocate secondary information,
  or create an intentional second zone. Never preserve a narrow phone strip inside empty space.
- The live loop stays in one viewport as required by `gameplay-screen-contract.md`.
- Pointer, keyboard, controller, and touch behavior must coexist when supported. Give every screen
  an initial focus, visible non-color-only focus state, logical traversal, modal focus trap, and
  reliable back path. Resolve displayed prompts from the active binding instead of hardcoding keys.

## 9. Studio asset rendering baseline

The visual world, subjects, materials, details, and palette come from the concept and reference.
Generated raster art uses the studio's polished cartoon 2.5D casual-game finish: bold readable
silhouettes, rounded or slightly exaggerated modeled forms, theme-aware saturated color, smooth
gradients, glossy highlights, restrained star glints, and one consistent top-left light.

This rendering baseline does not prescribe UI composition. A UI may be flat, typographic, scenic,
mechanical, papery, or sparse while its illustrated assets meet the shared production bar.
Photorealistic/product-render art, flat vector clipart, emoji/sticker styling, and mixed rendering
languages remain out of scope. Inspect relevant `examples-games/` through
`.claude/docs/visual-context.md` and `.claude/docs/game-concept-examples.md`.

## 10. Validation

An anti-slop review must answer with evidence, not taste:

- [ ] The Game UI Read and complete Design Signature exist and are used in code/assets.
- [ ] Each key gameplay state has a job, attention order, information policy, and composition recipe.
- [ ] The mechanic owns the live screen and the core loop works without page scrolling.
- [ ] Menu, live round, result, and secondary screens do not all reuse one component skeleton.
- [ ] The Similarity Check names real neighbors and identifies at least four material differences,
      unless an explicit reference or mechanic justifies repetition.
- [ ] The design remains recognizable in grayscale/wireframe; its distinction is not only color/art.
- [ ] Controls expose complete states and immediate touch feedback.
- [ ] HUD information is readable over worst-case gameplay frames and is not color-only.
- [ ] Compact and expanded viewport matrices pass without clipping, fake device framing, or dead space.
- [ ] Text scale, reduced motion, safe areas, focus traversal, back behavior, and input prompts pass.
- [ ] Motion and effects communicate something and remain proportional to event importance.
- [ ] Generated assets follow the concept/reference and studio rendering baseline.
- [ ] Compliance surfaces are reachable and legible without being visually mistaken for rewards.

The audit must not “fix” a game by adding a fashionable treatment. It should first correct broken
hierarchy, state communication, composition, responsiveness, or mismatch with the recorded
signature. A familiar pattern used for a clear reason passes. A fashionable pattern copied without
one fails.

## 11. Defaults explicitly rejected

The following are never studio-wide requirements:

- 60/30/10 screen ratios;
- one accent color, exactly five colors, or a fixed saturation range;
- one focal object for every state;
- four-to-six type sizes or mandatory two-font pairing;
- centered or asymmetric layouts as a default;
- a top HUD, bottom command deck, floating chips, side rail, or card stack for every screen;
- animated entry for every element or rolling animation for every number;
- glassmorphism, double bezels, pill buttons, rounded cards, neon, dark mode, huge typography,
  parallax, particles, or themed transitions everywhere;
- replacing all standard controls when a clear, accessible, lightly themed control serves better;
- using “different palette + different mascot” as proof of a different interface.

These techniques remain available when the Game UI Read and state map justify them. The rule bans
unexamined repetition, not design vocabulary.
