---
name: playtest
description: "Deep GAMEPLAY verification (not just 'the screens open'): actually plays the game through headless Chrome CDP — N gameplay actions, checking that the score/balance CHANGE, that the win path is reachable, that game-over is handled, that progression works, that the board is animated (vision-based frame comparison), and that there are no exceptions or leaks. Produces a PLAYTEST REPORT with a verdict and prioritised fixes. Called from /autocreate-finalize (Phase 10.6) or run manually."
argument-hint: "[--rounds N] [--no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Playtest — "is this actually playable?"

`/emulator-test` checks that the screens open and do not crash. `/playtest` checks that
**THE GAME PLAYS**: actions produce results, numbers change, wins are celebrated, losses are
handled, the board is alive. It is the last filter between "it compiles" and "a professional
game" (see `.claude/docs/quality-bar.md`).

**Preconditions**: `dart analyze lib/` with 0 errors; `node` ≥21 and Chrome/Chromium available
(otherwise report an honest SKIPPED, as `/emulator-test` does).

Read `.claude/docs/mobile-first-contract.md` and run the game first at the canonical phone size,
then at an expanded Web viewport. Chrome must use the full host canvas; a centered phone strip,
fake device frame, dead margins, or pointer-only essential interaction is a HIGH failure.

---

## Phase 1 — launching the game (headless web) [~2 min]

The same path as `/autocreate-finalize` Phase 10.5 (a web server plus waiting for the URL, with
an early exit on a build error):

```bash
mkdir -p .claude/runtime-logs
WEB_PORT=8099
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && break
  grep -qE "Failed to compile|Target dart2js failed|Compilation failed|^Error: " \
    .claude/runtime-logs/flutter-run.log 2>/dev/null && break
  sleep 2
done
TS=$(date +%Y%m%d-%H%M%S); PT_DIR="production/playtest/$TS"; mkdir -p "$PT_DIR"
```

## Phase 2 — the play session (CDP) [~4 min]

Three passes of `tools/web_verify.mjs`:

```bash
# 2.1 A tour of the screens + baseline shots (manifest.json: steps/semanticLabels/consoleErrors)
timeout 220 node tools/web_verify.mjs --url "$WEB_URL" --out "$PT_DIR" --budget 180 \
  2>&1 | tee "$PT_DIR/web_verify.log"

# 2.2 Gameplay load: N repeats of the main action (default 60; --rounds sets it)
timeout 240 node tools/web_verify.mjs --url "$WEB_URL" --out "$PT_DIR" --soak "${ROUNDS:-60}" \
  2>&1 | tee -a "$PT_DIR/web_verify.log"

# 2.3 Expanded Web gameplay: prove the same core loop fills and works at desktop size
mkdir -p "$PT_DIR/1440x900"
timeout 180 node tools/web_verify.mjs --url "$WEB_URL" --out "$PT_DIR/1440x900" \
  --size 1440x900 --budget 150 --quick \
  2>&1 | tee "$PT_DIR/1440x900/web_verify.log"
```

Afterwards, stop the server: `kill "$(cat .claude/runtime-logs/flutter.pid)" 2>/dev/null`.

## Phase 3 — the gameplay checks (P1–P10)

Sources: the screenshots (`Read` vision), `manifest.json` (`semanticLabels`, `consoleErrors`,
`soak.heapUsed*`, `soak.suspectLeak`), and `.claude/runtime-logs/flutter-run.log`.

| # | Check | How to verify it | Severity on FAIL |
|---|-------|------------------|------------------|
| P1 | **An action produces a result** | Compare the frames before/after the action (vision): the field changed, the pixels are not identical | CRITICAL |
| P2 | **The numbers change** | The score/balance in the screenshot AFTER a series of actions ≠ the value BEFORE (vision-reading the HUD digits) | CRITICAL |
| P3 | **The win path is reachable** | Over N rounds, win feedback is visible at least once (overlay/particles/a rising number) | HIGH |
| P4 | **A loss is handled** | Game-over / insufficient-funds appears and there is a way out of it (restart/menu) | HIGH |
| P5 | **The board is alive** | Two frames of the idle state, taken apart, differ (idle animation) — vision | HIGH |
| P6 | **Progression works** | Level/Mode Select opens, and choosing a level starts the game with a different config | HIGH |
| P7 | **Pause/return** | Going to the menu and back does not break the state (the balance is preserved, no red screen) | HIGH |
| P8 | **0 exceptions during the session** | `consoleErrors` is empty; no EXCEPTION CAUGHT in flutter-run.log | CRITICAL |
| P9 | **No leak** | `soak.suspectLeak == false`, the heap does not grow monotonically | MEDIUM |
| P10 | **The starting experience** | From launch to the first game action is ≤ 3 taps (splash→menu→play) | MEDIUM |

> For P1/P2/P5, vision comparison is the main instrument. The shots in `$PT_DIR` are numbered by
> tour step; the soak adds frames before and after the series. If there are not enough frames to
> compare, run 2.2 again with a smaller N and take the before/after shots manually through
> web_verify.

## Phase 4 — the report and automatic fixes [~3 min]

Write `$PT_DIR/PLAYTEST-REPORT.md`:

```markdown
# Playtest Report — [game], [date]
## Verdict: PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED
| # | Check | Result | Evidence |
|---|-------|--------|----------|
| P1 | An action produces a result | PASS | 04→05.png: the field changed |
...
## Prioritised fixes
1. [CRITICAL] ...
```

- **NOT-PLAYABLE** = any CRITICAL (P1/P2/P8). Without `--no-fix`, run an auto-fix loop of up to
  2 iterations against the table of permitted fixes in `/autocreate-finalize` 10.5.3 (targeted
  edits only: ValueNotifier wiring, a component not added to the World, a route, an asset path;
  NOT balance, NOT configs, NOT rewriting screens). After a fix, repeat phases 1–3.
- **PLAYABLE-WITH-ISSUES** = HIGH items remain — list them in the report; do not fix them silently.

## Exit criteria

- `$PT_DIR/PLAYTEST-REPORT.md` with a verdict and the P1–P10 table
- 0 CRITICAL (or the 2 fix iterations are exhausted — the verdict is honestly NOT-PLAYABLE)
- The server and headless Chrome are stopped (no orphaned processes)
