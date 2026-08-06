---
name: asset-review
description: "A vision review of the generated assets for professional consistency: one style/light/level of detail across the set, adherence to the Design DNA, readability at in-game size, clean alpha and no AI artefacts. Fixes locally first, then spends a limited GPT Images 2.0 recovery budget; the fallback is used only on a technical failure. Called automatically from /autocreate (Phase 3.6) or run manually on any project."
argument-hint: "[--sprites-only | --report-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Asset Review — visual integrity of the asset set

A game only looks professional when ALL its assets look like the work of one artist.
Generating one prompt per asset inevitably produces a mismatch — this skill catches and fixes it.

**Role**: `art-director` (`.claude/agents/art-director.md`) — read it as your FIRST action.
In environments without the Agent tool (Codex), adopt the art director's persona and run the
protocol yourself.

---

## Phase 1 — context and inventory [~1 min]

1. Read `design/gdd/game-concept.md` → the **Design DNA** section (visual world, colour
   palette, shape language, depth & effects strategy). That is the benchmark for the review.
2. Read `design/asset-format.md` → `format: png|svg`.
3. For PNG, read `design/asset-manifest.md`: the class, the SHA-256 of the prompt, the number of
   attempts and the remaining recovery budget. A matching valid cache entry does not count as a
   new asset and must not be regenerated.
4. Inventory:

```bash
ls -la assets/images/sprites/ assets/images/ui/ assets/images/backgrounds/ 2>/dev/null
```

If there are no assets, stop: "nothing to review, run /generate-asset first".

If this is an existing project with no `design/asset-manifest.md`, reconstruct it from
`design/asset-prompts.md` and the file inventory before starting the review. A missing manifest
is never a reason to regenerate an asset that already exists.

## Phase 2 — contact sheets [~1 min]

```bash
mkdir -p production/asset-review
EXT=$(grep '^format:' design/asset-format.md 2>/dev/null | awk '{print $2}'); EXT=${EXT:-png}

if command -v montage >/dev/null 2>&1 && [ "$EXT" = "png" ]; then
  montage assets/images/sprites/*.png -tile 4x -geometry 256x256+8+8 -background '#202020' \
    production/asset-review/contact-sprites.png 2>/dev/null
  # The key sheet: how the player will REALLY see the sprites (64px)
  montage assets/images/sprites/*.png -tile 8x -geometry 64x64+4+4 -background '#202020' \
    production/asset-review/contact-sprites-64px.png 2>/dev/null
  montage assets/images/ui/*.png -tile 4x -geometry 256x256+8+8 -background '#202020' \
    production/asset-review/contact-ui.png 2>/dev/null
  echo "✅ Contact sheets → production/asset-review/"
else
  echo "ℹ️ montage unavailable or SVG mode — reviewing one file at a time"
fi
```

SVG mode: render to PNG for viewing if a converter exists (`rsvg-convert`/`inkscape`; if a
Flutter render is unavailable, read the SVG source and assess the structure: one palette, the
gradient style, the stroke width).

## Phase 3 — the vision assessment (10 criteria AR1–AR10) [~3 min]

Look through Read (vision) at: the contact sheets (or each file), EVERY background at full size,
and — **mandatory** — the 64px sheet. Readability at in-game size matters more than beauty at 1024px.

The criteria (details in `art-director.md`):

| # | Criterion | # | Criterion |
|---|-----------|---|-----------|
| AR1 | One polished cartoon 2.5D style; no photoreal/product-shot/flat clipart | AR6 | Clean alpha (no halos) |
| AR2 | One light source | AR7 | Icons — one style/weight |
| AR3 | One level of detail | AR8 | The background yields focus to the field |
| AR4 | The Design DNA's palette | AR9 | The subject is identifiable |
| AR5 | Readable at 64 px | AR10 | No AI artefacts |

The technical alpha check for AR6 (PNG, complementing the visual one) — `tools/cutout.py --check`
measures exactly the defects the eye misses on a 1024 px preview:

```bash
python3 tools/cutout.py --dir assets/images/sprites --check
python3 tools/cutout.py --dir assets/images/ui --check
```

| Code | What it means | Action |
|------|---------------|--------|
| `NO_ALPHA` | the background was never cut out | Apply `cutout.py` first; a new call only if the source is technically unusable |
| `HARD_EDGE` | binary alpha: a ragged, stair-stepped silhouette | Re-cut from the source first; a new call only if there is no source or it is unusable |
| `WHITE_FRINGE` | a light halo from the background remains along the edge | Re-cut from the source first; a new call only if the source is unusable |

Also look at `bbox_fill` (`--json`): if it jumps around the set (0.3 for one sprite against 0.9
for another), the sprites will appear at different sizes in the game — run the set through
`python3 tools/cutout.py --dir assets/images/sprites` to normalise the framing.

## Phase 4 — report and verdict [~1 min]

Write `design/asset-review.md`: a table of asset → verdict (PASS/FAIL) → criterion →
action (see the template in `art-director.md`). The overall verdict: **PASS** or **REGENERATE (N)**.

`--report-only`: stop here and return the report.

## Phase 5 — economical correction of the rejects [~3 min]

Only the FAIL assets (NOT the whole set):

- **A locally fixable PNG** — first `cutout.py`, framing normalisation, fixing the anchor/scale
  in code, or reclassifying it as `derive`/`code`; none of that spends budget.
- **PNG (Codex), a defect in the original generation** — only for the `generate` class and only
  when a recovery slot is free: one retry through GPT Images 2.0 with the original prompt, the
  set's style anchor and the specific reason for the rejection. Update the SHA-256 and the
  counter in `design/asset-manifest.md`, then cut the background out with
  `python3 tools/cutout.py <file> --type sprite`.
- **The fallback** — GPT Images/default is only permitted on a technical failure of the GPT
  Images 2.0 call (an error, no file, an invalid PNG), never because of the vision assessment.
- **SVG** — edit the asset's source: bring the palette/gradients/stroke into line with the set.

Repeat Phase 3 only for the corrected assets. After one recovery per `logical_id`, further spend
is forbidden: you may accept the previous asset only if it passes the critical AR5/AR6/AR9/AR10,
otherwise mark it `BUDGET_BLOCKED` in the report and do not hide the reason.

## Exit criteria

- `design/asset-review.md` with a verdict and a row for every asset
- Contact sheets in `production/asset-review/` (if montage is available)
- 0 assets with a FAIL verdict that had neither a local correction nor the one permitted
  recovery; `BUDGET_BLOCKED` always states the reason, the spend and the decision needed
- `python3 tools/cutout.py --dir assets/images/sprites --check` — no FAIL and no
  `HARD_EDGE`/`WHITE_FRINGE` (or explicitly accepted residual risks in the report)
