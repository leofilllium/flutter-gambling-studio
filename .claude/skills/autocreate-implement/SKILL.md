---
name: autocreate-implement
description: "Session 2 of the /autocreate pipeline (Phases 4 → 10): implementation. Five agents in sequence write the code plus the meta systems, wire up content, integrate, build to 0 errors, run a feel pass, tests, a UI audit (compliance), curve-based balancing and crash prevention. The heavy phases are DELEGATED to fresh sub-agents without a full-history fork, so the orchestrator does not exhaust its context or TPM. At the end it spawns Session 3 (autocreate-finalize). Started automatically by Session 1 through the Agent tool, or manually in a new conversation."
argument-hint: "[--resume]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Implement — Session 2 (implementation)

**Purpose**: turn Session 1's pre-production (concept + assets + audio + data) into fully
working, clean, tested game code — and hand it to Session 3 for runtime verification. This is
the **middle** of `/autocreate`'s three context sessions.

```
Session 1 (autocreate)  →[handoff-1]→  Session 2 (THIS skill)  →[autocreate-handoff.md]→  Session 3
   concept/data                Phases 4–10: code/tests/audit/balance        finalize/release-ready
```

---

## 🚨 MANDATORY CONTRACT

1. ✅ Reads `production/session-state/autocreate-handoff-1.md` **as its first action**
2. ✅ Validates Session 1's artifacts (pubspec, structure, `assets/data/*.json`, `assets/audio/*`)
3. ✅ Reads `design/asset-format.md` to determine the asset format (PNG vs SVG) and passes it to
   the agents (Agent B: `Image.asset()` for PNG, `SvgPicture` for SVG; Agent A: file extensions)
4. ✅ Reads `.claude/docs/mobile-phone-contract.md` and
   `.claude/docs/gameplay-screen-contract.md`, then passes the portrait-only product target,
   full-viewport composition, stable keys, control sizing, and phone viewport matrix to Agent B,
   QA, integration, and UI audit
5. ✅ Runs **Phases 4 → 10** as described in `.claude/skills/autocreate/SKILL.md`
   (those phases are the canonical specification; this skill drives their execution)
6. ✅ **Delegates the heavy phases to sub-agents** (see the map below) — the orchestrator does
   NOT read all of `lib/` itself, it works from command output (`dart analyze`/`flutter test`)
   and the agents' summaries
7. ✅ At the end (Phase 10.7) writes `autocreate-handoff.md` and **spawns Session 3** through
   the Agent tool

**Forbidden:**
- ❌ Rewriting Session 1's concept/assets/audio/data (you may only extend `GameConfig` with
  values from `assets/data/*.json`)
- ❌ Changing balance or content data other than through game-mathematician in Phase 9
- ❌ Calling `flutter build apk/appbundle/web`, `adb` or `emulator` — that is Session 3 / release-eng
- ❌ Reporting "done" while `dart analyze` has errors or `flutter test` is red
- ❌ Finishing without spawning Session 3 (Phase 10.7)

---

## The context protection strategy (why this is a separate session)

A complete game means a lot of code (5 agents × dozens of files + tests + the audit). If the
orchestrator read all of that itself, the context would run out before the end. So **the
Session 2 orchestrator mostly coordinates and runs commands, while the sub-agents do the file work**:

| Phase | What the orchestrator does | Who it delegates to (Agent tool, clean context + handoff) |
|-------|----------------------------|----------------------------------------------------------|
| 4. Implementation | builds the `lib/contracts.md` contract, runs the 5 agents strictly one at a time | **A** mechanics → **E** meta-systems → **D** sound → **B** ui → **C** juice |
| 4.5. Content wiring | — | gluing data↔code: **B** (level/mode select) + **E** (progression/economy) |
| 5. Integration | — | **lead-programmer**: reads every file, fixes cross-agent mismatches, places the service/audio/VFX calls |
| 6. Build & Fix | runs `dart analyze`, collects the error list | if there are many errors, **mechanics-programmer**/**ui-programmer** fix their own; the orchestrator only re-runs analyze |
| 6.5. Feel Pass | — | **juice-artist** (living gameplay, filling in the hooks) |
| 7. Tests | runs `flutter test`, collects the failures | **qa-tester** writes/fixes the tests |
| 8. UI Audit | — | `/ui-audit` (the skill already uses agents) OR **ui-programmer** across the 10 categories |
| 9. Balance | runs the sim script | **game-mathematician** when it falls outside the window (edits the JSON) |
| 10. Crash Prevention | a final `dart analyze` + `flutter test` | targeted fixes go to the relevant agent |

> **The orchestrator's rule:** do not open `lib/` files en masse for reading. Read only the
> output of `dart analyze`/`flutter test`, `design/structure.md`, `lib/contracts.md`, and the
> BRIEF summaries the sub-agents return. A targeted Read of 1–2 files is acceptable for
> diagnosis. That keeps Session 2's context within budget even for a large game.

> **🤖 CODEX / an environment without the Agent tool:** the delegation in the table above is
> carried out as SEQUENTIAL persona passes (see `AGENTS.md` → "Execution Model"):
> before each pass read `.claude/agents/<role>.md` + `lib/contracts.md`, do that role's zone of
> responsibility, write a 3–5 line summary of the pass into
> `production/session-state/active.md`, and do NOT keep other roles' files in context.
> The Phase 4 order is: **A → E → D → B → C** (logic and services before UI, so B sees the real
> signatures). The "do not read lib/ en masse" rule matters even more under Codex — there is one
> context for everything.

> **The TPM gate:** at most one sub-agent is active at a time. Each receives only
> `lib/contracts.md`, the design/data files it needs, its role and a short handoff. Never pass
> it the parent session's full transcript.

---

## Phase 0 — preflight & handoff read [~30 s]

```bash
test -f production/session-state/autocreate-handoff-1.md || {
  echo "❌ No handoff-1. Did Session 1 /autocreate not finish?"; exit 1; }
test -f pubspec.yaml || { echo "❌ No pubspec.yaml — the project is not initialised"; exit 1; }
test -f design/structure.md || { echo "❌ No design/structure.md"; exit 1; }
ls assets/data/*.json   >/dev/null 2>&1 || echo "⚠️ no assets/data/*.json — the content data is missing"
ls assets/audio/sfx/*.wav >/dev/null 2>&1 || echo "⚠️ no audio — re-run tools/synth_sfx.py"

# Determining the asset format (PNG vs SVG). You may not silently fall back to SVG:
# Session 1 must write design/asset-format.md, and on a failure the format is inferred
# from the assets that actually exist.
ASSET_FORMAT=""
if [ -f design/asset-format.md ]; then
  ASSET_FORMAT=$(grep '^format:' design/asset-format.md | awk '{print $2}' | tr -d '[:space:]')
elif ls assets/images/sprites/*.png >/dev/null 2>&1 || ls assets/images/backgrounds/*.png >/dev/null 2>&1; then
  ASSET_FORMAT="png"
  echo "⚠️ design/asset-format.md is missing; inferred format=png from existing assets"
elif ls assets/images/sprites/*.svg >/dev/null 2>&1 || ls assets/images/backgrounds/*.svg >/dev/null 2>&1; then
  ASSET_FORMAT="svg"
  echo "⚠️ design/asset-format.md is missing; inferred format=svg from existing assets"
else
  echo "❌ No design/asset-format.md and no PNG/SVG assets found — Session 1 is incomplete"
  exit 1
fi
echo "🎨 Asset format: ${ASSET_FORMAT}"

# Validating the assets against the format
if [ "$ASSET_FORMAT" = "png" ]; then
  ls assets/images/sprites/*.png >/dev/null 2>&1 || echo "⚠️ no PNG sprites — they were expected in Codex mode"
  ls assets/images/backgrounds/*.png >/dev/null 2>&1 || echo "⚠️ no PNG backgrounds"
  if find assets/images -name "*.svg" -print -quit | grep -q .; then
    echo "⚠️ PNG mode, but SVGs were found. Do not use them in the code; check they are not the result of a mistaken generation."
  fi
else
  ls assets/images/sprites/*.svg >/dev/null 2>&1 || echo "⚠️ no SVG sprites"
  ls assets/images/backgrounds/*.svg >/dev/null 2>&1 || echo "⚠️ no SVG backgrounds"
fi
echo "✅ Preflight OK — Session 1's artifacts are in place"
```

Read `autocreate-handoff-1.md`, `design/structure.md`, `design/art-direction.md`,
`design/asset-format.md` (the asset format: PNG or SVG — it affects Agent B's code),
`design/gdd/game-concept.md` (especially the Production Plan, Screen Map, Design DNA and the
ValueNotifier contracts). Do not read `lib/` en masse.

> **CRITICAL for the asset format:** if `design/asset-format.md` says `format: png`:
> - Agent B uses `Image.asset('assets/images/sprites/name.png')`, NOT `SvgPicture`
> - `flame_svg` is NOT used in the code (it may stay in pubspec as a fallback)
> - The constants in `assets_constants` carry the `.png` extension
> - If `format: svg`, everything is as before: `SvgPicture.asset()` + `flame_svg`

### `--resume` (after a Session 2 failure)
Work out which phase to continue from, using the artifacts:
- no `lib/main.dart` / few files in `lib/` → start at Phase 4
- the code exists but `dart analyze` has errors → Phase 6
- analyze is clean, there are no tests or they are red → Phase 7
- the tests are green, the audit has not run → Phase 8
Do not redo what is already done.

---

## Phases 4 → 10 — execution against the canon

Run **Phases 4, 4.5, 5, 6, 6.5, 7, 8, 9, 10** exactly as described in
`.claude/skills/autocreate/SKILL.md` (the "Phases 4–10 run in Session 2" section), applying the
delegation map above. Each phase's exit criteria come from autocreate's Quality Gates table:

| Phase | Exit criterion | Iterations |
|-------|----------------|------------|
| 4. Implementation | the 5 agents have finished (A/B/C/D/E) | 1 (Phase 6 fixes) |
| 4.5. Content wiring | Game accepts (mode,levelId); Level/Mode Select ↔ data | 2 |
| 5. Integration | 18 connections (including the meta services) | 3 |
| 6. Build | `dart analyze lib/` 0 errors | 10 |
| 6.5. Feel Pass | the field is alive (F1–F5), analyze + test clean | 2 |
| 7. Tests | `flutter test` all green (including test/services/) | 5 |
| 8. UI Audit | 100+ checks, including the blocking phone-only full-viewport gameplay gate at 360×640, 360×800, 390×844 and 430×932 | 3 |
| 9. Balance | RTP/difficulty in range across the WHOLE curve | 3 |
| 10. Crash Prevention | 20/20 + (gambling) age gate/disclaimer; analyze + test clean | 3 |

**THE ABSOLUTE MINIMUM before Phase 10.7:** `dart analyze lib/` 0 errors, `flutter test` green,
15+ screens, working navigation, the core mechanic + content (N levels/modes) + the meta systems
in place, (gambling) the compliance flags wired up, and every player-facing string in English
(unless the user explicitly asked for another language). The live field, essential HUD, stake/risk
controls and primary action must be visible together without page scrolling; a thumbnail field or
nested game window blocks the handoff even when analyzer and tests are green. `main.dart` and the
native projects must enforce portrait, with no tablet/iPad/desktop layout branch.

---

## Phase 10.7 — handoff & spawn Session 3 [~1 min]

Run **Phase 10.7 from `.claude/skills/autocreate/SKILL.md`**: write
`production/session-state/autocreate-handoff.md` (the full context for finalisation) and
**spawn Session 3** through the Agent tool (the prompt is as in autocreate's Phase 10.7.2; it
tells the sub-agent to run `.claude/skills/autocreate-finalize/SKILL.md`: runtime + soak,
session state, release-eng PREP without building the AAB/APK, and the final report).

Once the Session 3 sub-agent returns, pass its final report upward (to Session 1 / the user).
If Session 3 failed, report the reason and the manual restart command: `/autocreate-finalize`.

---

## Recovery after a failure

- **Session 2 crashed** → the user runs `/autocreate-implement --resume` in a new conversation;
  the skill works out the phase from the artifacts and continues.
- **Session 1 never wrote handoff-1** → preflight fails with a clear message; run `/autocreate`
  again (or write `assets/data/*.json` and handoff-1 by hand).
