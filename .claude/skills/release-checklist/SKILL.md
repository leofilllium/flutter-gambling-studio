---
name: release-checklist
description: "Calls the release-manager agent to run quality control before the game is released. Fully verifies the RNG architecture and the absence of state leakage."
user-invocable: true
allowed-tools: Bash, Read, Agent
argument-hint: ""
---

# `release-checklist` — readiness check

Starts the release process. It does no work itself; it delegates to the release manager.

## Instructions

1. Call `release-manager` (in an environment without the Agent tool, adopt the persona from
   `.claude/agents/release-manager.md`).
2. Give it this instruction: `Please check this project against your Gambling Release Checklist, .claude/docs/mobile-first-contract.md, AND against the non-negotiable invariants in .claude/docs/quality-bar.md (§9 plus a sample of §1–§8). Treat any phone/expanded matrix failure, capped phone wrapper, fake device frame, unusable wide reflow, pointer-only essential interaction, or undocumented orientation/device-family restriction as NO-GO, and write the report to production/session-logs/release-[date].md`
3. If `production/playtest/*/PLAYTEST-REPORT.md` and `design/asset-review.md` exist, the
   release-manager must take their verdicts into account (NOT-PLAYABLE, or a failed
   asset-review, means NO-GO).
4. Report the result (GO / NO-GO) to the user.
