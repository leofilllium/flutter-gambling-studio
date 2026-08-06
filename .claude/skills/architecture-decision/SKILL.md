---
name: architecture-decision
description: "Creates an ADR for a key technical decision, with an analysis of the alternatives and the consequences."
argument-hint: "[a short description of the decision]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# /architecture-decision [decision]

Invocation: the user runs `/architecture-decision [a short description of the decision]`

## Goal

Creates an Architecture Decision Record (ADR) — a document recording a significant technical
decision, its context, the alternatives considered and the consequences.
Every significant technical decision should have an ADR.

## Agents

- `technical-director` — runs the ADR process and makes the final call
- `lead-programmer` — technical expertise

## When to create an ADR

- Choosing the RNG approach (why Random.secure and not X)
- Choosing the GameState architecture (sealed class vs enum vs boolean)
- Choosing state management (ValueNotifier vs Riverpod vs Bloc)
- Choosing the reel structure (infinite scroll vs sprite swap)
- Adding a new dependency to pubspec.yaml
- Changing the directory structure
- Choosing the RTP range and volatility

## Order of work

### Step 1: technical-director — gathering context

Ask the user:
1. What problem are we solving?
2. Which alternatives were considered?
3. What are the constraints (time, technology, compatibility)?

### Step 2: analysing the alternatives

```
Option A: [name]
  Pros: ...
  Cons: ...
  Game-specific risks: ...

Option B: [name]
  Pros: ...
  Cons: ...
  Game-specific risks: ...
```

### Step 3: the technical-director's recommendation

A clear recommendation with its rationale.
Taking into account: RNG safety, RTP correctness, performance, maintainability.

### Step 4: creating the ADR file

Create `docs/architecture/adr-NNN-short-title.md`:

```markdown
# ADR-NNN: [Decision title]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Author**: technical-director
**Approved by**: [user/agent]

## Context

[Why does this decision need to be made? What problem is being solved?]

## Game integrity context

[How does this decision affect RNG safety / RTP correctness / the fairness of the game?]

## Options considered

### Option A: [name]
- Pros: ...
- Cons: ...

### Option B: [name]
- Pros: ...
- Cons: ...

## The decision

[Option X] — because [rationale].

## Consequences

### Positive
- ...

### Negative / trade-offs
- ...

### Game integrity
- [Impact on RNG / RTP / the fairness of the game]

## Implementation

Responsible agent: [mechanics-programmer / lead-programmer / ...]
Related files: [the list of files that will change]
```

## ADR numbering

- `docs/architecture/` — the folder for every ADR
- Numbering: ADR-001, ADR-002, ...
- The last number comes from `ls docs/architecture/adr-*.md | tail -1`

## The ADR index

Maintain `docs/architecture/README.md` with a table of every ADR:
```markdown
| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | Using Random.secure() for the RNG | Accepted | 2026-01-15 |
```
