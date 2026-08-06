# Balancing the mathematical model: [System name]

**Category:** [C1–C6]
**Model:** [M1–M6]
**Target metric:** [e.g. "RTP 96.0%" / "hard pity 70 at SSR 1.2%" / "run win-rate 32%"]
**Config:** `design/balance/[file].json`
**Date computed:** [date]

## Parameter table

For M1 (paytable RTP):

| Symbol | Weight | Hit frequency | Multiplier (x3) | Contribution to RTP |
|--------|--------|---------------|-----------------|---------------------|
| Cherry | 100 | 50% | x2 | 12.5% |
| Lemon  | ... | ... | ... | ... |
| **TOTAL** | **SUM** | **100%** | | **[XX]%** |

For the other models, use the corresponding table: outcomes and probabilities (M2), spin events
and unlock prices (M3), rarities and pity (M4), round thresholds and modifiers (M5), buckets and
multipliers (M6).

## Bonus factors
Wild / Scatter / free spins / pity / jokers — exactly how they affect the final metric and how
much of it they account for.

## Run results

```bash
python3 tools/simulate_math.py --model [m1-m6] --config design/balance/[file].json --trials 1000000
```

- Theoretical value: [XX]
- Measured value: [XX]
- Deviation: [X]
- Verdict: [PASS / CONCERNS / FAIL]

The full report: `design/balance/simulation-report.md`.

> A run that is not written to a report does not count as having happened. The
> `simulation.last_run_date` field in the config is updated by every run.
