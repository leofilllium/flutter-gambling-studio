# Learning proposal: Require gameplay-led opening panels for object-only store art

Status: proposed; human review and merge required.

## Observed problem

Object-led store guidance prohibited a character-only opening but did not require authentic gameplay in slides one and two, allowing decorative openings or invented players.

## Proposed improvement

For games with no living character, prohibit invented people or mascots in slide one and require readable three-quarter gameplay in both opening carousel crops while preserving real topology and symbols.

Base commit: `5b8b695f96356ba701e0350e422e823da32a4ee8`

## Source evidence

### store-object-lead-learning-evidence.txt

SHA-256: `240ffa8d39ae4a5cca52e6366a15bdcbf2fc3a14850048867f8bf128401c9690`

    Observation

    The current store-screenshot guidance says object-led games should not invent a mascot or use a character-only opening, but it does not require early carousel panels to show gameplay. A user reviewing a Shining Crown store composition corrected this gap: a game with no living player/character must not introduce one on slide 1, and slides 1 and 2 should show the authentic game at a three-dimensional angle.

    Affected context

    - Workflow: .claude/skills/store-screenshots/SKILL.md
    - Example family: Shining Crown / royal crown slot
    - Existing project classification: object-led C1/M1 classic 3x3 slot with no living character asset
    - Reference observation: a royal slot cabinet shown at a dynamic three-quarter angle, with readable reels and real game objects in the foreground

    Bounded improvement

    For object- or mechanic-led games whose shipped concept and asset inventory contain no living character, prohibit invented humans, hands, animals, mascots, or player silhouettes in the opening slide. Require authentic gameplay to be visibly readable in each of the first two carousel crops, either as separate angled samples or as one continuous three-quarter gameplay surface spanning both crops. Preserve actual topology, symbols, outcome, and lead kind.

    Expected validation

    The store-screenshots skill should state this rule in planning, integrated composition, identity review, and final reporting without changing character-led game defaults. The Shining Crown example guidance should agree with the rule.

## Validation

- Command: `["python3", "-B", "-m", "unittest", "tools.tests.test_store_compose", "-q"]`; exit 0; 2026-09-14T16:19:25.421892+00:00
  Output SHA-256: `fbbf6027b6c188350cad6a3cdaef7848da24f984b2aee9d3b4cba31fb3686bfe`

       seam 1→2: detail 2.68× the picture's average
       seam 2→3: detail 0.00× the picture's average
       panorama slid -48px inside its slack so the cuts miss the subjects
       panorama slid +8px inside its slack so the cuts miss the subjects
       panorama slid +8px inside its slack so the cuts miss the subjects
       sprite asset gate: 1 standalone PNG object(s) have real alpha
    ⚠️  duplicate sprite ignored in exhaustive manifest: /tmp/tmppq5z_nyw/sprites/hero.png
       sprite inventory: 2 unique asset(s), including 1 discovered through --sprite-dir — every one belongs in the layout/reference manifest and final integrated scene
    ❌ backdrop changes the actual game's visual background and is never part of /store-screenshots by default. Re-run only after an explicit user request, with --confirm-game-background-replacement.
    ❌ long-banner gate failed with 1 blocker(s); no feature graphic was written. Regenerate the source art, or use --banner-gate warn only for a diagnostic base that cannot ship
    ❌ long-banner gate failed with 4 blocker(s); no feature graphic was written. Regenerate the source art, or use --banner-gate warn only for a diagnostic base that cannot ship
    ❌ --win draws the win state onto a plate built from --symbol. A plate lifted from a frame already has whatever state that frame was in — capture the frame at the moment the round pays and lift that one.
    ❌ --win 4x1: outside the 3x3 grid
    ❌ --win 1x9: outside the 3x3 grid
    ❌ --win 0x1: outside the 3x3 grid
    ❌ --win 1x2: listed twice
    ❌ --win 'middle': expected COLxROW (1-based), e.g. 1x2,2x2,3x2
    ❌ --win named no cells
    ❌ @hero requires --lead-kind character; use @prop or @board for objects
    ❌ --gutter abc: expected auto, pixels (100) or a percentage (7.5%)
    ❌ --gutter -5: a seam allowance cannot be negative
    ❌ --gutter 400px is more than a quarter of a 1080px panel — that is not a seam allowance, that is a missing slice
    ❌ --object-frame many: expected auto, off, or an object count
    ❌ --object-frame -1: the object count cannot be negative
    ❌ --seam-snap wide: expected auto, off, pixels (60) or a percentage (5%)
    ❌ --seam-snap -5: a search radius cannot be negative
    ❌ --seam-snap 400px is more than 15% of a 1000px panel — the cuts would wander far enough to change what each panel is about
    ❌ sprite asset gate failed; no panorama draft was written. Every reference must be one fully visible object in a PNG with a real transparent alpha canvas (no white/colour/checker background):
       /tmp/tmprga_opy3/boxed.png: no alpha channel
       Regenerate or cut out the source, then verify it with `python3 tools/cutout.py FILE.png --check`.
    ❌ --sprite a.png@z=4: unusable placement key 'z=4' — use the hero/prop/board/frame/fall role flag or x/y/w/h/rot/glow/shadow/opacity/panel/bleed/contact/light/occlude/trail=N (e.g. eagle.png@hero or gem.png@x=0.3,y=0.6,w=0.34)
    ❌ --sprite a.png@x=left: x='left' is not a number
    ❌ --sprite needs a PNG path
    ❌ --sprite a.png@villain: unusable placement key 'villain' — use the hero/prop/board/frame/fall role flag or x/y/w/h/rot/glow/shadow/opacity/panel/bleed/contact/light/occlude/trail=N (e.g. eagle.png@hero or gem.png@x=0.3,y=0.6,w=0.34)
    ❌ --hero-bounds '0.1,0.2,0.3': expected normalized x,y,w,h
    ❌ --hero-bounds 'left,0.2,0.3,0.7': every value must be a number
    ❌ --hero-bounds '0.1,0.2,0,0.7': width and height must be positive
    ❌ --hero-bounds '0.8,0.2,0.3,0.7': the box must stay inside the normalized 0..1 canvas
    ❌ --hero-bounds '0.1,0.6,0.2,0.5': the box must stay inside the normalized 0..1 canvas
    ----------------------------------------------------------------------
    Ran 140 tests in 29.438s

    OK

- Command: `["python3", "-c", "from pathlib import Path; root=Path(\".\"); skill=\" \".join((root/\".claude/skills/store-screenshots/SKILL.md\").read_text().split()); visual=\" \".join((root/\".claude/docs/visual-context.md\").read_text().split()); examples=\" \".join((root/\".claude/docs/game-concept-examples.md\").read_text().split()); review=(root/\"docs/learning/store-object-lead-opening-review.md\").read_text(); assert \"first two carousel slides\" in skill; assert \"Each opening crop, reviewed separately\" in skill; assert \"Never add a human, hand, animal, mascot or player silhouette\" in skill; assert \"Character-led games keep their existing character-first defaults\" in visual; assert \"one continuous angled gameplay surface\" in visual; assert \"slides 1\u20132 show authentic reels at a three-quarter/3D angle\" in examples; assert review.count(\"| PASS |\") == 6"]`; exit 0; 2026-09-14T16:19:31.764573+00:00
  Output SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Command: `["git", "diff", "--check"]`; exit 0; 2026-09-14T16:19:34.986014+00:00
  Output SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
