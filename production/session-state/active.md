# Session State — Flutter Gambling Studio

<!-- STATUS -->
Epic: Studio Setup
Feature: Infrastructure
Task: English-only studio pass complete
<!-- /STATUS -->

## Status

The studio is configured and ready to build gambling games. The general-purpose multi-genre
configuration has been retired: puzzles, runners, shooters and clickers are no longer supported.

## Changes (2026-07-31) — the move to a gambling specialisation

- **Six categories instead of six genres**: C1 Social Casino · C2 Casino Originals ·
  C3 Spin-to-Progress · C4 Gacha & Loot-Box · C5 Casino Roguelike · C6 Coin Pusher & Plinko.
  The canonical reference is `.claude/docs/gambling-categories.md`
- **32 archetypes A–AF**, all gambling (previously 32 mixed, 20 of them non-gambling)
- **Six mathematical models M1–M6** with verifiable thresholds —
  `.claude/docs/math-models.md`
- **`tools/simulate_math.py`** — the single verifier for all six models
  (it replaced `tools/simulate_rtp.py`, which the documentation described but which never
  existed). Exact calculation wherever the outcome space is enumerable; Monte Carlo only for
  path-dependent models. Exit codes: 0 = PASS, 1 = CONCERNS, 2 = FAIL
- **Reference configs** for all six models — `.claude/docs/templates/math-configs/`,
  each passing a run out of the box (`python3 tools/simulate_math.py --selftest`)
- **`.claude/rules/responsible-gaming.md`** — the compliance layer became a release blocker:
  age gate, disclaimer, responsible play, odds disclosure, and a ban on real-currency symbols
- **The RNG / stateless-outcome rules are now unconditional** — they used to be conditional,
  "for the gambling genre only". The single exception: seeded run determinism in C5 (requires an ADR)
- **The "Classification" block** is mandatory in every concept: category, archetype, model,
  target metric, config, compliance profile. Without it `/gate-check concept` returns FAIL
- All 32 skills, 14 agents and the mirror layers (Codex / Gemini / Copilot / Cursor)
  were moved to the gambling taxonomy

## Changes (2026-08-06) — English across the whole studio

- The studio now works **in English end to end**: agent responses, design documents, reports,
  session state, tool output and hook messages
- **The generated game ships in English too** — every player-facing string, plus store
  metadata and screenshot captions. The only exception is an explicit user request for another
  language, which is recorded in the concept's "Classification" block
- The previous "respond in Russian" mandates were removed from `CLAUDE.md`, `AGENTS.md`,
  `GEMINI.md`, `.cursorrules`, `.gemini/rules.md` and `.claude/docs/coordination-rules.md`
- `ComplianceCopy` now carries the English disclaimer wording that the stores audit
- `tools/simulate_math.py`, `tools/web_verify.mjs`, `tools/synth_sfx.py` and
  `tools/store_compose.py` emit and match English; the font coverage probe now defaults to a
  Latin sample, so Latin-only display faces are no longer rejected

## Studio commands

```
/start              — Orientation: where to begin
/brainstorm         — A gambling game concept (choosing the category C1–C6)
/auto-idea          — An autonomous concept from the 32 archetypes A–AF
/autocreate         — Zero-to-playable, no questions asked
/team-dev           — Development orchestration
/balance-check      — Math model verification M1–M6
/release-checklist  — The final quality gate + compliance
```

## To get started

Run `/start` or `/brainstorm` for a new game.
Run `/continue-project` if there is an unfinished project.

Last updated: 2026-08-06
