---
name: continue-project
description: "Analyses the current state of the project and proposes the next logical development steps. Run it when you come back to work on a game."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: ""
---

# `continue-project` — entering the project

Automatically restores the development context and points you at the right stage.

## Procedure

1. Read `design/gdd/game-concept.md` (if it exists).
2. Read `pubspec.yaml` (if it exists).
3. Read `production/session-state/active.md` (if it exists).
4. Read `.claude/docs/mobile-phone-contract.md`; if code exists, check the Flutter/native portrait
   locks, iPhone-only target, phone viewport tests, and absence of non-phone layout branches.
5. Determine the project's stage:
   - **Nothing yet**: suggest `/start` or `/brainstorm`
   - **Only a GDD**: suggest `/design-system rtp-weights` or `/generate-asset symbols`
   - **A Flutter project but no slot logic**: suggest calling `mechanics-programmer`
   - **A working slot with no sound/VFX**: suggest `juice-artist` and `sound-designer`
   - **The project looks finished**: suggest `/release-checklist`

6. Print the status as a clean block with 3 recommended commands for continuing.
