---
name: design-review
description: "Checks a GDD for completeness, quality and mathematical correctness against the studio's standards."
argument-hint: "[file or system]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent
---

# /design-review [file or system]

Invocation: the user runs `/design-review [path to the GDD or the system's name]`

## Goal

Checks the completeness and quality of a mini-game's Game Design Document.
Confirms that the GDD contains all 8 required sections, that the mathematics is correct, that
edge cases are described and that the acceptance criteria are testable.

## Agents

- `game-designer` — design completeness and correctness
- `game-mathematician` — verification of the mathematical formulas

## Order of work

### Step 1: find the GDD documents

If a path was given, check that specific file.
If not, check every file in `design/gdd/`.

### Step 2: game-designer — GDD completeness check

The `game-designer` agent checks each GDD:

**The 8 required sections:**
- [ ] Overview — there is an introductory paragraph
- [ ] Player fantasy — the feeling is described
- [ ] Detailed rules — stated unambiguously
- [ ] Formulas — every calculation, with variables
- [ ] Edge cases — at least 5 situations
- [ ] Dependencies — the systems are listed
- [ ] Tuning knobs — a table with ranges
- [ ] Acceptance criteria — at least 5 testable criteria

**Gambling-specific checks (where applicable):**
- [ ] The target RTP is stated (95–97%)
- [ ] The paytable is present
- [ ] The Wild symbol: what it substitutes for, and what it does not
- [ ] Scatter: how it triggers the bonus, and from which positions
- [ ] The near-miss effect is described (if there is one)
- [ ] Free spins: the trigger condition, the count, the multiplier

**Document status:**
- [ ] There is a `Status:` line (Draft / Review / Approved / Implemented)
- [ ] Approved documents carry a date

**Language:**
- [ ] The document is written in English, like everything else the studio produces

### Step 3: game-mathematician — the mathematical check

The `game-mathematician` agent checks:

- [ ] The RTP formulas are correct and complete
- [ ] The symbol weights in the table agree with `rtp-config.json`
- [ ] The hit rate is realistic (15–45%)
- [ ] The payouts are balanced (no obvious holes in the math model)
- [ ] The free spins contribution to the RTP has been computed

### Step 4: the report

```markdown
# Design Review — [system] — [date]

## Documents reviewed
- design/gdd/XXX.md — [status]

## 🚨 DEFICIENCIES (they block implementation)
- Section X is missing from document Y

## ⚠️ OBSERVATIONS
- Formula Z is incomplete

## ✅ MEETS THE STANDARD
- All 8 sections are present

## Recommendation: READY TO IMPLEMENT / NEEDS REVISION
```

## Arguments

- No arguments: review every GDD in `design/gdd/`
- `reel-mechanics` — review `design/gdd/reel-mechanics.md`
- `--math-only` — the mathematical check only
