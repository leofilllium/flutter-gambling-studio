#!/usr/bin/env python3
"""Universal math verifier for the gambling studio.

One entry point for all six math models declared in .claude/docs/math-models.md:

    M1  paytable RTP      C1  slots, roulette, video poker, blackjack, bingo
    M2  instant-win RTP   C2  crash, mines, dice, hi-lo, tower, keno, scratch, pick
    M3  economy           C3  spin-to-progress hybrids
    M4  gacha             C4  banner pulls, packs, crates
    M5  run win-rate      C5  casino roguelikes
    M6  physics RTP       C6  plinko, pachinko, coin pusher

Where the outcome space is enumerable the model is solved EXACTLY (analytic RTP beats a
Monte Carlo estimate and runs in milliseconds). Monte Carlo is used only where the model
is path-dependent: economy sessions, gacha pity, roguelike runs, empirical physics.

Usage
-----
    python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
    python3 tools/simulate_math.py --model m4 --config design/balance/gacha-config.json --trials 1000000
    python3 tools/simulate_math.py --model m1 --config ... --report design/balance/simulation-report.md
    python3 tools/simulate_math.py --selftest

Exit code is 0 on PASS, 1 on CONCERNS, 2 on FAIL — so CI and hooks can gate on it.
Stdlib only, no dependencies.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

PASS, CONCERNS, FAIL = "PASS", "CONCERNS", "FAIL"
_VERDICT_EXIT = {PASS: 0, CONCERNS: 1, FAIL: 2}
_VERDICT_MARK = {PASS: "✅", CONCERNS: "⚠️", FAIL: "❌"}

# Enumerating more than this many reel combinations is slower than sampling them.
EXACT_ENUMERATION_LIMIT = 8_000_000


# --------------------------------------------------------------------------------------
# result plumbing
# --------------------------------------------------------------------------------------


@dataclass
class Metric:
    """One checked number: what we wanted, what we got, and whether that is acceptable."""

    name: str
    value: float
    target: str
    verdict: str
    fmt: str = "{:.4f}"
    note: str = ""

    def rendered(self) -> str:
        return self.fmt.format(self.value)


@dataclass
class Report:
    model: str
    title: str
    config_path: str
    method: str
    trials: int
    seed: int | None = None
    metrics: list[Metric] = field(default_factory=list)
    tables: list[tuple[str, list[str], list[list[str]]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, metric: Metric) -> Metric:
        self.metrics.append(metric)
        return metric

    def table(self, caption: str, header: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
        self.tables.append((caption, list(header), [[str(c) for c in r] for r in rows]))

    @property
    def verdict(self) -> str:
        if any(m.verdict == FAIL for m in self.metrics):
            return FAIL
        if any(m.verdict == CONCERNS for m in self.metrics):
            return CONCERNS
        return PASS

    def to_markdown(self) -> str:
        out: list[str] = []
        out.append(f"# Simulation Report — {self.title}")
        out.append("")
        out.append(f"- **Модель**: {self.model}")
        out.append(f"- **Конфиг**: `{self.config_path}`")
        out.append(f"- **Метод**: {self.method}")
        out.append(f"- **Испытаний**: {num(self.trials)}")
        if self.seed is not None:
            out.append(f"- **Seed**: {self.seed}")
        out.append(f"- **Дата**: {date.today().isoformat()}")
        out.append("")
        out.append("## Результат")
        out.append("")
        out.append("| Метрика | Целевое | Получено | Вердикт |")
        out.append("|---------|---------|----------|---------|")
        for m in self.metrics:
            mark = f"{_VERDICT_MARK[m.verdict]} {m.verdict}"
            out.append(f"| {m.name} | {m.target} | {m.rendered()} | {mark} |")
        out.append("")
        for caption, header, rows in self.tables:
            out.append(f"## {caption}")
            out.append("")
            out.append("| " + " | ".join(header) + " |")
            out.append("|" + "|".join("---" for _ in header) + "|")
            for row in rows:
                out.append("| " + " | ".join(row) + " |")
            out.append("")
        failing = [m for m in self.metrics if m.verdict != PASS]
        out.append("## Вердикт")
        out.append("")
        if self.verdict == PASS:
            out.append("✅ **PASS** — модель в целевом окне, конвейер можно продолжать.")
        else:
            head = "⚠️ **CONCERNS**" if self.verdict == CONCERNS else "❌ **FAIL**"
            out.append(f"{head} — требует внимания `game-mathematician`:")
            out.append("")
            for m in failing:
                detail = f" — {m.note}" if m.note else ""
                out.append(f"- **{m.name}**: получено {m.rendered()}, цель {m.target}{detail}")
        if self.notes:
            out.append("")
            out.append("## Примечания")
            out.append("")
            for n in self.notes:
                out.append(f"- {n}")
        out.append("")
        return "\n".join(out)


def num(n: float | int) -> str:
    """Thousands separator as a space — a bare .replace(",", " ") also eats literal commas."""
    return f"{n:,}".replace(",", "\u00a0")


def band(value: float, ok: tuple[float, float], warn: tuple[float, float] | None = None) -> str:
    """Classify a value against a PASS band and an optional wider CONCERNS band."""
    if ok[0] <= value <= ok[1]:
        return PASS
    if warn is not None and warn[0] <= value <= warn[1]:
        return CONCERNS
    return FAIL


def _require(cfg: dict, key: str, model: str) -> Any:
    if key not in cfg:
        raise ConfigError(f"[{model}] в конфиге нет обязательного поля '{key}'")
    return cfg[key]


class ConfigError(ValueError):
    """Config is missing something the model cannot be run without."""


# --------------------------------------------------------------------------------------
# M1 — paytable RTP (C1)
# --------------------------------------------------------------------------------------


def _cum_weights(weights: Sequence[float]) -> list[float]:
    total = 0.0
    out = []
    for w in weights:
        total += w
        out.append(total)
    return out


def _line_payout(
    line: Sequence[int],
    payouts: dict[int, dict[int, float]],
    wild_id: int | None,
    scatter_id: int | None,
) -> float:
    """Longest left-to-right run, wilds substituting for anything but scatter."""
    base: int | None = None
    for sym in line:
        if sym == wild_id:
            continue
        base = sym
        break
    if base is None:  # all wilds
        base = wild_id if wild_id is not None else line[0]
    if base == scatter_id:
        return 0.0
    run = 0
    for sym in line:
        if sym == base or (wild_id is not None and sym == wild_id):
            run += 1
        else:
            break
    table = payouts.get(base, {})
    return float(table.get(run, 0.0))


def _reel_rtp(
    reels_cfg: dict,
    symbols: list[dict],
    paylines: list[list[int]],
    wild_id: int | None,
    scatter_id: int | None,
    bet_per_line: float,
    trials: int = 1_000_000,
    rng_seed: int | None = None,
) -> tuple[float, float, dict[int, float], str]:
    """RTP of one reel set.

    Enumerates the grid outcome space exactly when it is small enough (a 3-reel game is a
    few thousand combinations — an exact answer beats any sample), and falls back to batched
    Monte Carlo for the large 5x3 spaces where enumeration is intractable.

    Returns (rtp, hit_rate, scatter_count_probabilities, method_description).
    """
    reel_count = int(reels_cfg["count"])
    rows = int(reels_cfg.get("visible_rows", 3))
    weights = [float(s["weight"]) for s in symbols]
    ids = [int(s["id"]) for s in symbols]
    total_weight = sum(weights)
    probs = [w / total_weight for w in weights]

    payouts: dict[int, dict[int, float]] = {}
    for s in symbols:
        payouts[int(s["id"])] = {int(k): float(v) for k, v in s.get("payouts", {}).items()}

    cells = reel_count * rows
    space = len(ids) ** cells
    total_bet = bet_per_line * len(paylines)

    # Precompute the payout of every distinct line sequence once; a 5-reel line over 6 symbols
    # is 7776 sequences, versus re-deriving it for every spin of a million-spin run.
    line_cache: dict[tuple[int, ...], float] = {}

    def line_pay(seq: tuple[int, ...]) -> float:
        cached = line_cache.get(seq)
        if cached is None:
            cached = _line_payout(seq, payouts, wild_id, scatter_id)
            line_cache[seq] = cached
        return cached

    ev = 0.0
    hit = 0.0
    scatter_hist: dict[int, float] = {}

    if space <= EXACT_ENUMERATION_LIMIT:
        for combo in itertools.product(range(len(ids)), repeat=cells):
            p = 1.0
            for idx in combo:
                p *= probs[idx]
            cellvals = [ids[i] for i in combo]

            win = 0.0
            for line in paylines:
                seq = tuple(cellvals[r * rows + line[r]] for r in range(reel_count))
                win += line_pay(seq) * bet_per_line

            if scatter_id is not None:
                n = cellvals.count(scatter_id)
                scatter_hist[n] = scatter_hist.get(n, 0.0) + p

            ev += p * win
            if win > 0:
                hit += p
        rtp = ev / total_bet if total_bet else 0.0
        return rtp, hit, scatter_hist, f"точный перебор {num(space)} исходов"

    # Monte Carlo. Symbols are drawn in large batches so the per-spin cost stays in C.
    rng = random.Random(rng_seed)
    cum = _cum_weights(weights)
    batch = 20_000
    wins = 0
    scatter_counts: dict[int, int] = {}
    done = 0
    while done < trials:
        n = min(batch, trials - done)
        flat = rng.choices(ids, cum_weights=cum, k=n * cells)
        for i in range(n):
            base = i * cells
            win = 0.0
            for line in paylines:
                seq = tuple(flat[base + r * rows + line[r]] for r in range(reel_count))
                win += line_pay(seq) * bet_per_line
            if scatter_id is not None:
                c = flat[base : base + cells].count(scatter_id)
                scatter_counts[c] = scatter_counts.get(c, 0) + 1
            ev += win
            if win > 0:
                wins += 1
        done += n

    rtp = (ev / done) / total_bet if total_bet else 0.0
    hit = wins / done
    scatter_hist = {k: v / done for k, v in scatter_counts.items()}
    return rtp, hit, scatter_hist, f"Monte Carlo, {num(done)} спинов"


def model_m1(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    kind = cfg.get("type", "reels")
    target = float(cfg.get("target_rtp", 0.96))

    if kind == "table":
        # Explicit outcome distribution — roulette, blackjack, video poker, bingo.
        outcomes = _require(cfg, "outcomes", "M1")
        total_w = sum(float(o.get("weight", o.get("probability", 0.0))) for o in outcomes)
        if total_w <= 0:
            raise ConfigError("[M1] сумма весов/вероятностей исходов равна нулю")
        ev = 0.0
        hit = 0.0
        rows = []
        payoffs: list[tuple[float, float]] = []
        for o in outcomes:
            p = float(o.get("weight", o.get("probability", 0.0))) / total_w
            pay = float(o["payout"])
            ev += p * pay
            if pay > 0:
                hit += p
            payoffs.append((p, pay))
            rows.append([o.get("name", "?"), f"{p:.6f}", f"{pay:g}×", f"{p * pay:.6f}"])
        rtp = ev  # payouts are expressed as a multiple of the stake
        report.method = "точный расчёт по таблице исходов"
        report.table("Вклад исходов в RTP", ["Исход", "Вероятность", "Выплата", "Вклад в RTP"], rows)
        mean = ev
        var = sum(p * (pay - mean) ** 2 for p, pay in payoffs)
        vol = math.sqrt(var) / mean if mean else 0.0
    else:
        symbols = _require(cfg, "symbols", "M1")
        reels_cfg = _require(cfg, "reels", "M1")
        paylines = [list(pl) for pl in _require(cfg, "paylines", "M1")]
        wild_id = next((int(s["id"]) for s in symbols if s.get("is_wild")), None)
        scatter_id = next((int(s["id"]) for s in symbols if s.get("is_scatter")), None)

        rtp, hit, scatter_hist, method = _reel_rtp(
            reels_cfg, symbols, paylines, wild_id, scatter_id,
            bet_per_line=1.0, trials=args.trials, rng_seed=args.seed,
        )
        base_rtp = rtp
        report.method = method

        bonus_rtp = 0.0
        bonus = cfg.get("bonus")
        if bonus and scatter_id is not None:
            trigger_n = int(bonus.get("free_spins_trigger_count", 3))
            spins = int(bonus.get("free_spins_count", 10))
            mult = float(bonus.get("free_spins_multiplier", 1))
            p_trigger = sum(p for n, p in scatter_hist.items() if n >= trigger_n)
            # Free spins replay the base game (optionally on their own weights) at a multiplier.
            fs_symbols = bonus.get("symbols", symbols)
            fs_rtp, _, _, _ = _reel_rtp(
                reels_cfg, fs_symbols, paylines, wild_id, scatter_id,
                bet_per_line=1.0, trials=args.trials, rng_seed=args.seed,
            )
            bonus_rtp = p_trigger * spins * mult * fs_rtp
            rtp = base_rtp + bonus_rtp
            report.table(
                "Разложение RTP",
                ["Источник", "Значение", "Доля от общего RTP"],
                [
                    ["Базовая игра", f"{base_rtp:.4f}", f"{base_rtp / rtp * 100:.1f}%" if rtp else "—"],
                    ["Бонус (free spins)", f"{bonus_rtp:.4f}", f"{bonus_rtp / rtp * 100:.1f}%" if rtp else "—"],
                ],
            )
            report.notes.append(
                f"Триггер бонуса: P({trigger_n}+ скаттеров) = {p_trigger:.6f}; "
                f"{spins} спинов × множитель {mult:g}."
            )
        vol = float(cfg.get("declared_volatility_index", 0.0))
        report.table(
            "Символы",
            ["ID", "Имя", "Вес", "Вероятность на ячейку"],
            [
                [
                    s["id"],
                    s.get("name", "?"),
                    s["weight"],
                    f"{float(s['weight']) / sum(float(x['weight']) for x in symbols):.4f}",
                ]
                for s in symbols
            ],
        )

    report.add(
        Metric(
            "RTP",
            rtp,
            "95.0–97.0%",
            band(rtp, (0.95, 0.97), (0.94, 0.98)),
            fmt="{:.2%}",
            note=f"целевой по конфигу {target:.2%}",
        )
    )
    report.add(Metric("Hit rate", hit, "20–35%", band(hit, (0.20, 0.35), (0.15, 0.45)), fmt="{:.2%}"))
    if vol:
        report.add(Metric("Индекс волатильности", vol, "информативно", PASS, fmt="{:.3f}"))

    declared = cfg.get("simulation", {}).get("last_run_rtp")
    if declared is not None and abs(float(declared) - rtp) > 0.005:
        report.notes.append(
            f"⚠️ `simulation.last_run_rtp` = {float(declared):.4f} расходится с пересчитанным "
            f"{rtp:.4f} — обнови конфиг."
        )


# --------------------------------------------------------------------------------------
# M2 — instant-win RTP (C2)
# --------------------------------------------------------------------------------------


def _comb(n: int, k: int) -> int:
    return math.comb(n, k) if 0 <= k <= n else 0


def model_m2(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    kind = _require(cfg, "type", "M2")
    edge = float(cfg.get("house_edge", 0.03))
    cap = float(cfg.get("max_multiplier", math.inf))
    report.method = "точный расчёт"

    if kind == "step":
        # mines / tower: reveal cells one at a time, each survival multiplies the stake.
        # RTP must be identical for every cash-out depth the player can actually choose —
        # a depth where it is not is a leak, so we check the whole strategy space.
        cells = int(_require(cfg, "cells", "M2"))
        bad = int(_require(cfg, "bad_cells", "M2"))
        max_picks = int(cfg.get("max_picks", cells - bad))
        rows = []
        rtps = []
        capped_at: list[int] = []
        for k in range(1, min(max_picks, cells - bad) + 1):
            p_survive = _comb(cells - bad, k) / _comb(cells, k)
            fair = (1.0 - edge) / p_survive
            mult = min(fair, cap)
            if mult < fair:
                capped_at.append(k)
            rtp_k = p_survive * mult
            rtps.append(rtp_k)
            rows.append([k, f"{p_survive:.6f}", f"{mult:.4f}×", f"{rtp_k:.4%}"])
        report.table("RTP по числу открытых ячеек", ["Открыто", "P(дожить)", "Множитель", "RTP"], rows)
        rtp = statistics.fmean(rtps) if rtps else 0.0
        spread = (max(rtps) - min(rtps)) if rtps else 0.0
        report.add(
            Metric(
                "Разброс RTP по глубинам",
                spread,
                "≤ 0.001 (RTP не зависит от глубины)",
                PASS if spread <= 1e-3 else FAIL,
                fmt="{:.6f}",
                note="если RTP зависит от числа открытых ячеек — формула множителя или кап дают утечку",
            )
        )
        if capped_at:
            report.notes.append(
                f"Кап множителя ({cap:g}×) урезает выплату на глубинах {capped_at} — на них RTP ниже "
                f"объявленного. Либо подними кап, либо ограничь `max_picks`."
            )

    elif kind == "crash":
        # P(crash point >= x) = (1 - edge) / x. RTP is edge-invariant across cash-out targets;
        # we verify that numerically across the whole policy space rather than assuming it.
        targets = cfg.get("cashout_targets", [1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 50.0])
        rows = []
        rtps = []
        for t in targets:
            t = float(t)
            if t > cap:
                continue
            p_win = (1.0 - edge) / t
            rtp_t = p_win * t
            rtps.append(rtp_t)
            rows.append([f"{t:g}×", f"{p_win:.6f}", f"{rtp_t:.4%}"])
        report.table("RTP по точке cash-out", ["Цель", "P(выигрыша)", "RTP"], rows)
        rtp = statistics.fmean(rtps) if rtps else 0.0
        spread = (max(rtps) - min(rtps)) if rtps else 0.0
        report.add(
            Metric(
                "Разброс RTP по стратегиям",
                spread,
                "≤ 0.001 (RTP не зависит от цели)",
                PASS if spread <= 1e-3 else FAIL,
                fmt="{:.6f}",
                note="если RTP зависит от точки cash-out — формула множителя неверна",
            )
        )

    elif kind == "threshold":
        # dice roll-under: player picks a threshold, payout scales inversely with win chance.
        sides = int(cfg.get("outcomes", 100))
        rows = []
        rtps = []
        for thr in cfg.get("thresholds", list(range(5, sides, max(1, sides // 10)))):
            thr = int(thr)
            p_win = thr / sides
            if p_win <= 0 or p_win >= 1:
                continue
            mult = min((1.0 - edge) / p_win, cap)
            rtp_t = p_win * mult
            rtps.append(rtp_t)
            rows.append([thr, f"{p_win:.4f}", f"{mult:.4f}×", f"{rtp_t:.4%}"])
        report.table("RTP по порогу", ["Порог", "P(выигрыша)", "Множитель", "RTP"], rows)
        rtp = statistics.fmean(rtps) if rtps else 0.0

    elif kind == "draw":
        # keno: pick k of n, house draws d, paytable keyed by number of matches.
        n = int(_require(cfg, "pool", "M2"))
        k = int(_require(cfg, "picks", "M2"))
        d = int(_require(cfg, "draws", "M2"))
        paytable = {int(m): float(v) for m, v in _require(cfg, "paytable", "M2").items()}
        rtp = 0.0
        rows = []
        for matches in range(0, k + 1):
            p = _comb(k, matches) * _comb(n - k, d - matches) / _comb(n, d)
            pay = paytable.get(matches, 0.0)
            rtp += p * pay
            rows.append([matches, f"{p:.8f}", f"{pay:g}×", f"{p * pay:.6f}"])
        report.table("Вклад совпадений", ["Совпало", "Вероятность", "Выплата", "Вклад в RTP"], rows)

    elif kind == "table":
        outcomes = _require(cfg, "outcomes", "M2")
        total_w = sum(float(o.get("weight", o.get("probability", 0.0))) for o in outcomes)
        rtp = sum(
            float(o.get("weight", o.get("probability", 0.0))) / total_w * float(o["payout"])
            for o in outcomes
        )
        report.table(
            "Исходы",
            ["Исход", "Вероятность", "Выплата"],
            [
                [
                    o.get("name", "?"),
                    f"{float(o.get('weight', o.get('probability', 0.0))) / total_w:.6f}",
                    f"{float(o['payout']):g}×",
                ]
                for o in outcomes
            ],
        )
    else:
        raise ConfigError(f"[M2] неизвестный type='{kind}' (ожидается step|crash|threshold|draw|table)")

    report.add(
        Metric("RTP", rtp, "96.0–99.0%", band(rtp, (0.96, 0.99), (0.95, 0.995)), fmt="{:.2%}")
    )
    report.add(
        Metric(
            "House edge объявлен",
            edge,
            "должен быть в правилах игры",
            PASS if "house_edge" in cfg else FAIL,
            fmt="{:.2%}",
            note="добавь house_edge в конфиг и покажи его на экране правил",
        )
    )
    report.add(
        Metric(
            "Максимальный множитель",
            cap if math.isfinite(cap) else 0.0,
            "объявлен и капнут",
            PASS if math.isfinite(cap) else FAIL,
            fmt="{:.0f}×",
            note="без max_multiplier один раунд может пробить любую экономику",
        )
    )


# --------------------------------------------------------------------------------------
# M3 — economy (C3)
# --------------------------------------------------------------------------------------


def model_m3(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    rng = random.Random(args.seed)
    sessions = args.trials if args.trials != args.default_trials else int(cfg.get("sessions", 10_000))

    energy_cap = int(_require(cfg, "energy_cap", "M3"))
    regen_per_hour = float(_require(cfg, "energy_regen_per_hour", "M3"))
    spin_cost = int(cfg.get("spin_energy_cost", 1))
    sessions_per_day = float(cfg.get("expected_sessions_per_day", 3))
    seconds_per_spin = float(cfg.get("seconds_per_spin", 4))

    events = _require(cfg, "spin_events", "M3")
    total_w = sum(float(e["weight"]) for e in events)
    if total_w <= 0:
        raise ConfigError("[M3] сумма весов событий спина равна нулю")
    cum = _cum_weights([float(e["weight"]) for e in events])

    unlocks = [float(u) for u in _require(cfg, "unlock_prices", "M3")]
    # Real hybrids scale payouts as the player progresses; a flat income against geometric
    # prices always reads as a grind wall no matter how the prices are tuned.
    income_growth = float(cfg.get("income_growth_per_unlock", 1.0))

    total_income = 0.0
    income_at_last_unlock = 0.0
    total_spins = 0
    session_lengths: list[float] = []
    dead_sessions = 0
    coins = float(cfg.get("starting_coins", 0))
    unlock_index = 0
    unlock_session: list[int] = []
    event_counts = {i: 0 for i in range(len(events))}

    for s in range(sessions):
        energy = energy_cap
        spins_this_session = 0
        gained = 0.0
        scale = income_growth ** unlock_index
        while energy >= spin_cost:
            energy -= spin_cost
            roll = rng.random() * total_w
            idx = len(cum) - 1
            for i, c in enumerate(cum):
                if roll <= c:
                    idx = i
                    break
            event_counts[idx] += 1
            gained += float(events[idx].get("coins", 0)) * scale
            spins_this_session += 1
        total_spins += spins_this_session
        total_income += gained
        coins += gained
        session_lengths.append(spins_this_session * seconds_per_spin / 60.0)

        spent_this_session = False
        while unlock_index < len(unlocks) and coins >= unlocks[unlock_index]:
            coins -= unlocks[unlock_index]
            unlock_index += 1
            unlock_session.append(s + 1)
            income_at_last_unlock = total_income
            spent_this_session = True
        if not spent_this_session and gained <= 0:
            dead_sessions += 1

    # Ratio is only meaningful over the window where sinks still exist. Once the content
    # ladder is exhausted every further session is pure income and would skew it to infinity.
    total_sink = sum(unlocks[:unlock_index])
    income_window = income_at_last_unlock if unlock_index else total_income
    ratio = (income_window / total_sink) if total_sink else float("inf")
    pace = (statistics.fmean([b - a for a, b in zip([0] + unlock_session, unlock_session)])
            if unlock_session else float("inf"))
    avg_len = statistics.fmean(session_lengths) if session_lengths else 0.0
    daily_regen = regen_per_hour * 24 / max(1.0, energy_cap)
    dead_rate = dead_sessions / sessions if sessions else 0.0
    steps = [unlocks[i + 1] / unlocks[i] for i in range(len(unlocks) - 1) if unlocks[i] > 0]
    worst_step = max(steps) if steps else 1.0

    report.method = f"Monte Carlo, {num(sessions)} сессий «среднего игрока»"
    report.trials = sessions
    report.add(Metric("Source/sink ratio", ratio, "0.90–1.15", band(ratio, (0.90, 1.15), (0.80, 1.30)), fmt="{:.3f}",
                      note="приход валюты против стоимости анлоков"))
    report.add(Metric("Пейс прогресса (сессий на анлок)", pace, "2–5", band(pace, (2, 5), (1.5, 8)), fmt="{:.2f}"))
    report.add(Metric("Длина сессии, мин", avg_len, "3–7", band(avg_len, (3, 7), (2, 10)), fmt="{:.2f}"))
    report.add(Metric("Сессий покрыто регеном в сутки", daily_regen, f"≥ {sessions_per_day:g}",
                      PASS if daily_regen >= sessions_per_day else CONCERNS, fmt="{:.2f}"))
    report.add(Metric("Худший шаг цены анлока", worst_step, "≤ 1.60", band(worst_step, (0, 1.6), (0, 2.0)), fmt="{:.2f}×"))
    report.add(Metric("Dead-end rate", dead_rate, "< 10%", band(dead_rate, (0, 0.10), (0, 0.20)), fmt="{:.2%}"))

    report.table(
        "Фактическое распределение событий спина",
        ["Событие", "Вес", "Ожидаемая доля", "Фактическая доля"],
        [
            [
                e.get("name", f"#{i}"),
                e["weight"],
                f"{float(e['weight']) / total_w:.4f}",
                f"{event_counts[i] / max(1, total_spins):.4f}",
            ]
            for i, e in enumerate(events)
        ],
    )
    report.notes.append(f"Открыто анлоков за прогон: {unlock_index} из {len(unlocks)}.")
    if unlock_index < len(unlocks):
        report.notes.append(
            "⚠️ Не весь контент достижим за смоделированное число сессий — проверь хвост кривой цен."
        )


# --------------------------------------------------------------------------------------
# M4 — gacha (C4)
# --------------------------------------------------------------------------------------


def model_m4(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    rng = random.Random(args.seed)
    pulls = args.trials

    rarities = _require(cfg, "rarities", "M4")
    top = max(rarities, key=lambda r: float(r.get("base_rate", 0.0)) * -1)  # rarest = lowest rate
    top = min(rarities, key=lambda r: float(r["base_rate"]))
    base_rate = float(top["base_rate"])
    hard_pity = int(_require(cfg, "hard_pity", "M4"))
    soft_pity_start = int(cfg.get("soft_pity_start", max(1, int(hard_pity * 0.75))))
    soft_step = float(cfg.get("soft_pity_step", 0.0))

    rate_sum = sum(float(r["base_rate"]) for r in rarities)

    def rate_at(counter: int) -> float:
        if counter + 1 >= hard_pity:
            return 1.0
        if counter + 1 >= soft_pity_start and soft_step > 0:
            return min(1.0, base_rate + soft_step * (counter + 1 - soft_pity_start + 1))
        return base_rate

    counter = 0
    hits = 0
    gaps: list[int] = []
    pity_triggers = 0
    pity_misses = 0
    for _ in range(pulls):
        counter += 1
        chance = rate_at(counter - 1)
        forced = counter >= hard_pity
        if rng.random() < chance:
            hits += 1
            gaps.append(counter)
            if forced:
                pity_triggers += 1
            counter = 0
        elif forced:
            pity_misses += 1
            counter = 0

    effective = hits / pulls if pulls else 0.0
    expected_pulls = 1 / effective if effective else float("inf")
    gaps_sorted = sorted(gaps)
    p90 = gaps_sorted[int(len(gaps_sorted) * 0.90)] if gaps_sorted else 0
    worst = gaps_sorted[-1] if gaps_sorted else 0

    report.method = f"Monte Carlo, {num(pulls)} пуллов"
    report.add(Metric("Base rate (редчайшая)", base_rate, "0.5–2.0%", band(base_rate, (0.005, 0.02)), fmt="{:.3%}"))
    report.add(Metric("Сумма вероятностей редкостей", rate_sum, "= 1.000",
                      PASS if abs(rate_sum - 1.0) < 1e-6 else FAIL, fmt="{:.6f}",
                      note="редкости обязаны покрывать всё пространство исходов"))
    report.add(Metric("Hard pity", float(hard_pity), "50–90 пуллов", band(hard_pity, (50, 90), (40, 100)), fmt="{:.0f}"))
    report.add(Metric("Эффективный rate", effective, f"расчётный ±0.1 п.п.",
                      PASS if effective >= base_rate else FAIL, fmt="{:.3%}",
                      note="pity обязан поднимать фактический шанс выше base rate"))
    report.add(Metric("E[пуллов до редчайшей]", expected_pulls, f"≤ {hard_pity}",
                      PASS if expected_pulls <= hard_pity else FAIL, fmt="{:.1f}"))
    report.add(Metric("90-й перцентиль пуллов", float(p90), f"≤ {hard_pity}",
                      PASS if p90 <= hard_pity else FAIL, fmt="{:.0f}"))
    report.add(Metric("Худшая серия без редкости", float(worst), f"≤ {hard_pity}",
                      PASS if worst <= hard_pity else FAIL, fmt="{:.0f}",
                      note="превышение hard pity означает, что счётчик реализован неверно"))
    report.add(Metric("Пропусков pity", float(pity_misses), "0",
                      PASS if pity_misses == 0 else FAIL, fmt="{:.0f}"))

    report.table(
        "Таблица редкостей",
        ["Редкость", "Base rate", "Дубликат конвертируется"],
        [[r.get("name", "?"), f"{float(r['base_rate']):.3%}", "да" if r.get("duplicate_value") else "❌ нет"]
         for r in rarities],
    )
    if any(not r.get("duplicate_value") for r in rarities):
        report.notes.append(
            "⚠️ Есть редкости без ценности дубликата — пулл, дающий «ничего», это провал дизайна."
        )
    report.notes.append(
        f"Раскрытие шансов игроку обязано показывать base rate ({base_rate:.2%}), hard pity "
        f"({hard_pity}) и эффективный rate ({effective:.2%}) — см. responsible-gaming.md §2.4."
    )


# --------------------------------------------------------------------------------------
# M5 — run win-rate (C5)
# --------------------------------------------------------------------------------------


def model_m5(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    runs = args.trials if args.trials != args.default_trials else int(cfg.get("runs", 100_000))
    targets = [float(t) for t in _require(cfg, "round_targets", "M5")]
    base_score = float(_require(cfg, "base_score", "M5"))
    score_sigma = float(cfg.get("score_sigma", 0.25))
    income = float(cfg.get("income_per_round", 4))
    mod_cost = float(cfg.get("modifier_cost", 5))
    mod_gain = float(cfg.get("modifier_multiplier", 1.35))
    # Shops offer a random assortment, so the strength of what you can actually buy varies.
    # Without this the win-rate is a step function of income and cannot be tuned smoothly.
    mod_sigma = float(cfg.get("modifier_multiplier_sigma", 0.0))
    max_mods = int(cfg.get("max_modifiers", 5))

    def play(seed: int, gain: float, cap_mods: int) -> tuple[bool, int, list[float]]:
        rng = random.Random(seed)
        power = base_score
        money = 0.0
        mods = 0
        log: list[float] = []
        for i, target in enumerate(targets):
            score = power * max(0.0, rng.gauss(1.0, score_sigma))
            log.append(score)
            if score < target:
                return False, i, log
            money += income
            while mods < cap_mods and money >= mod_cost:
                money -= mod_cost
                offered = gain if mod_sigma <= 0 else max(1.0, rng.gauss(gain, mod_sigma))
                power *= offered
                mods += 1
        return True, len(targets), log

    def win_rate_of(gain: float, cap_mods: int, n: int, salt: int) -> float:
        return sum(play(salt + i, gain, cap_mods)[0] for i in range(n)) / n

    wins = 0
    depths: list[int] = []
    for i in range(runs):
        won, depth, _ = play((args.seed or 0) + i, mod_gain, max_mods)
        wins += won
        depths.append(depth)
    win_rate = wins / runs

    steps = [targets[i + 1] / targets[i] for i in range(len(targets) - 1) if targets[i] > 0]
    worst_step = max(steps) if steps else 1.0

    # determinism: identical seed must reproduce the run bit for bit
    _, _, a_log = play(4242, mod_gain, max_mods)
    _, _, b_log = play(4242, mod_gain, max_mods)
    deterministic = a_log == b_log

    report.method = f"Monte Carlo, {num(runs)} забегов ботом-«средним игроком»"
    report.trials = runs
    report.add(Metric("Run win-rate", win_rate, "25–40%", band(win_rate, (0.25, 0.40), (0.15, 0.55)), fmt="{:.2%}"))
    report.add(Metric("Худший шаг цели раунда", worst_step, "≤ 2.0×", band(worst_step, (0, 2.0), (0, 2.5)), fmt="{:.2f}×"))
    report.add(Metric("Детерминизм по seed", 1.0 if deterministic else 0.0, "идентичный забег",
                      PASS if deterministic else FAIL, fmt="{:.0f}",
                      note="один seed обязан воспроизводить забег бит-в-бит"))

    # Per-modifier balance. Absolute thresholds are meaningless here — any modifier stacked to
    # the budget cap eventually wins — so we rank each modifier against the MEDIAN of the set
    # at an equal budget. The design question is "is the choice meaningful?", i.e. is any option
    # strictly better or strictly worse than its peers, not "does it win on its own".
    modifiers = cfg.get("modifiers")
    if modifiers and len(modifiers) >= 3:
        probe = min(4_000, runs)
        spread_limit = float(cfg.get("modifier_spread_limit", 0.25))
        results = [(m, win_rate_of(float(m["multiplier"]), max_mods, probe, 800_000)) for m in modifiers]
        median = statistics.median(r for _, r in results)
        rows = []
        dominant, dead = 0, 0
        for m, r in results:
            delta = r - median
            if delta > spread_limit:
                verdict, dominant = "доминирует", dominant + 1
            elif delta < -spread_limit:
                verdict, dead = "мёртвый", dead + 1
            else:
                verdict = "ок"
            rows.append([m.get("name", "?"), f"{float(m['multiplier']):.2f}×", f"{r:.2%}", f"{delta:+.1%}", verdict])
        report.table(
            "Баланс модификаторов (равный бюджет, отклонение от медианы набора)",
            ["Модификатор", "Множитель", "Win-rate", "Δ к медиане", "Вердикт"],
            rows,
        )
        report.add(Metric("Доминирующих модификаторов", float(dominant), "0",
                          PASS if dominant == 0 else FAIL, fmt="{:.0f}",
                          note=f"модификатор сильнее медианы более чем на {spread_limit:.0%} — выбор перестаёт быть выбором"))
        report.add(Metric("Мёртвых модификаторов", float(dead), "0",
                          PASS if dead == 0 else CONCERNS, fmt="{:.0f}",
                          note=f"модификатор слабее медианы более чем на {spread_limit:.0%} — его никогда не возьмут"))
        report.notes.append(f"Медиана win-rate по набору модификаторов: {median:.2%}.")
    else:
        report.notes.append(
            "⚠️ В конфиге нет списка `modifiers` (нужно ≥3) — баланс выбора не верифицирован. "
            "Добавь `modifiers: [{name, multiplier}, ...]`."
        )

    hist: dict[int, int] = {}
    for d in depths:
        hist[d] = hist.get(d, 0) + 1
    report.table(
        "Где обрываются забеги",
        ["Раунд", "Цель", "Доля забегов, оборвавшихся здесь"],
        [[i + 1, f"{targets[i]:g}", f"{hist.get(i, 0) / runs:.2%}"] for i in range(len(targets))],
    )


# --------------------------------------------------------------------------------------
# M6 — physics RTP (C6)
# --------------------------------------------------------------------------------------


def model_m6(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    kind = cfg.get("type", "plinko")
    multipliers = [float(m) for m in _require(cfg, "bucket_multipliers", "M6")]

    if kind == "plinko":
        # A peg board is a Galton board: exact binomial landing distribution.
        rows = int(cfg.get("rows", len(multipliers) - 1))
        bias = float(cfg.get("right_bias", 0.5))
        if len(multipliers) != rows + 1:
            raise ConfigError(
                f"[M6] для {rows} рядов нужно {rows + 1} корзин, в конфиге {len(multipliers)}"
            )
        probs = [_comb(rows, k) * (bias ** k) * ((1 - bias) ** (rows - k)) for k in range(rows + 1)]
        report.method = f"точное биномиальное распределение, {rows} рядов"
    elif kind == "buckets":
        probs = [float(p) for p in _require(cfg, "bucket_probabilities", "M6")]
        total = sum(probs)
        probs = [p / total for p in probs]
        report.method = "точный расчёт по заданному распределению корзин"
    elif kind == "empirical":
        # Landing counts dumped by the game's own headless physics harness.
        src = Path(_require(cfg, "empirical_landings", "M6"))
        if not src.exists():
            raise ConfigError(
                f"[M6] нет файла замеров {src}. Coin pusher/пачинко нельзя посчитать аналитически — "
                f"выгрузи распределение попаданий из headless-прогона игры (fixed timestep, "
                f"фиксированный seed, ≥10 000 прогревочных монет)."
            )
        counts = json.loads(src.read_text())
        counts = [float(c) for c in (counts["landings"] if isinstance(counts, dict) else counts)]
        total = sum(counts)
        probs = [c / total for c in counts]
        report.method = f"эмпирические замеры из {src} ({num(int(total))} запусков)"
        report.trials = int(total)
    else:
        raise ConfigError(f"[M6] неизвестный type='{kind}' (ожидается plinko|buckets|empirical)")

    if len(probs) != len(multipliers):
        raise ConfigError(f"[M6] корзин {len(multipliers)}, а вероятностей {len(probs)}")

    rtp = sum(p * m for p, m in zip(probs, multipliers))
    # A rare jackpot bucket is the point of the game; a bucket the player literally never
    # reaches in a session is a design bug. 0.1% ≈ once per 1000 drops — visible, but rare.
    dead = [i for i, p in enumerate(probs) if p < 0.001]
    fixed_step = bool(cfg.get("fixed_timestep", False))
    seeded = bool(cfg.get("deterministic_seed", False))

    report.table(
        "Распределение по корзинам",
        ["Корзина", "Множитель", "Вероятность", "Вклад в RTP"],
        [[i, f"{m:g}×", f"{p:.6f}", f"{p * m:.6f}"] for i, (p, m) in enumerate(zip(probs, multipliers))],
    )
    report.add(Metric("RTP", rtp, "95.0–97.0%", band(rtp, (0.95, 0.97), (0.94, 0.98)), fmt="{:.2%}"))
    report.add(Metric("«Мёртвых» корзин (<0.1%)", float(len(dead)), "0",
                      PASS if not dead else CONCERNS, fmt="{:.0f}",
                      note=f"корзины {dead} практически недостижимы — игрок это заметит" if dead else ""))
    report.add(Metric("Фиксированный timestep", 1.0 if fixed_step else 0.0, "обязателен",
                      PASS if fixed_step else FAIL, fmt="{:.0f}",
                      note="без fixed timestep RTP плывёт при просадке fps"))
    report.add(Metric("Детерминированный seed", 1.0 if seeded else 0.0, "обязателен",
                      PASS if seeded else FAIL, fmt="{:.0f}",
                      note="без воспроизводимости RTP невозможно верифицировать"))

    if kind == "empirical":
        report.notes.append(
            "Для coin pusher RTP нестационарен: замер обязан быть сделан в установившемся режиме "
            "(после ≥10 000 прогревочных монет), а не с пустого поля."
        )


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


MODELS: dict[str, tuple[str, Callable[[dict, argparse.Namespace, Report], None], int]] = {
    "m1": ("M1 — Paytable RTP (C1)", model_m1, 1_000_000),
    "m2": ("M2 — Instant-Win RTP (C2)", model_m2, 1_000_000),
    "m3": ("M3 — Economy (C3)", model_m3, 10_000),
    "m4": ("M4 — Gacha (C4)", model_m4, 1_000_000),
    "m5": ("M5 — Run Win-Rate (C5)", model_m5, 100_000),
    "m6": ("M6 — Physics RTP (C6)", model_m6, 1_000_000),
}


def run(args: argparse.Namespace) -> int:
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    label, fn, default_trials = MODELS[args.model]
    args.default_trials = default_trials
    if args.trials is None:
        args.trials = default_trials

    report = Report(
        model=label,
        title=cfg.get("game_name", Path(args.config).stem),
        config_path=args.config,
        method="",
        trials=args.trials,
        seed=args.seed,
    )
    fn(cfg, args, report)

    md = report.to_markdown()
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")

    print(md)
    print(f"\nОтчёт сохранён: {out}")
    return _VERDICT_EXIT[report.verdict]


# --------------------------------------------------------------------------------------
# self-test — runs every model on a built-in reference config
# --------------------------------------------------------------------------------------


SELFTEST_CONFIGS: dict[str, dict] = {
    "m1": {
        "game_name": "Selftest Slot",
        "target_rtp": 0.96,
        "reels": {"count": 3, "visible_rows": 1},
        "paylines": [[0, 0, 0]],
        "symbols": [
            {"id": 0, "name": "cherry", "weight": 30, "payouts": {"2": 0.55, "3": 2}},
            {"id": 1, "name": "bar", "weight": 20, "payouts": {"3": 6}},
            {"id": 2, "name": "seven", "weight": 10, "payouts": {"3": 25}},
            {"id": 3, "name": "wild", "weight": 4, "is_wild": True, "payouts": {"3": 75}},
        ],
    },
    "m2": {
        "game_name": "Selftest Mines",
        "type": "step",
        "cells": 25,
        "bad_cells": 3,
        "max_picks": 12,
        "house_edge": 0.02,
        "max_multiplier": 5000,
    },
    "m3": {
        "game_name": "Selftest Village",
        "energy_cap": 50,
        "energy_regen_per_hour": 7,
        "spin_energy_cost": 1,
        "seconds_per_spin": 5,
        "starting_coins": 0,
        "income_growth_per_unlock": 1.5,
        "spin_events": [
            {"name": "coins_small", "weight": 50, "coins": 120},
            {"name": "coins_big", "weight": 12, "coins": 500},
            {"name": "shield", "weight": 15, "coins": 0},
            {"name": "raid", "weight": 15, "coins": 300},
            {"name": "jackpot", "weight": 8, "coins": 1500},
        ],
        "unlock_prices": [40000, 60000, 90000, 135000, 202500, 303750, 455625, 683437],
    },
    "m4": {
        "game_name": "Selftest Banner",
        "hard_pity": 70,
        "soft_pity_start": 55,
        "soft_pity_step": 0.06,
        "rarities": [
            {"name": "SSR", "base_rate": 0.012, "duplicate_value": "shards"},
            {"name": "SR", "base_rate": 0.088, "duplicate_value": "shards"},
            {"name": "R", "base_rate": 0.900, "duplicate_value": "dust"},
        ],
    },
    "m5": {
        "game_name": "Selftest Roguelike",
        "round_targets": [300, 550, 1000, 1850, 3400, 6300, 11600, 21000],
        "base_score": 420,
        "score_sigma": 0.22,
        "income_per_round": 7.5,
        "modifier_cost": 5,
        "modifier_multiplier": 1.55,
        "modifier_multiplier_sigma": 0.30,
        "max_modifiers": 20,
        "modifiers": [
            {"name": "Пара+", "multiplier": 1.45},
            {"name": "Флеш+", "multiplier": 1.55},
            {"name": "Стрит+", "multiplier": 1.50},
            {"name": "Каре+", "multiplier": 1.60},
        ],
    },
    "m6": {
        "game_name": "Selftest Plinko",
        "type": "plinko",
        "rows": 8,
        "fixed_timestep": True,
        "deterministic_seed": True,
        "bucket_multipliers": [25, 3.8, 1.4, 0.38, 0.2, 0.38, 1.4, 3.8, 25],
    },
}


def selftest() -> int:
    import tempfile

    failures = 0
    for model in MODELS:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / f"{model}.json"
            cfg_path.write_text(json.dumps(SELFTEST_CONFIGS[model]), encoding="utf-8")
            args = argparse.Namespace(
                model=model,
                config=str(cfg_path),
                trials=None if model not in ("m3", "m5") else (2_000 if model == "m3" else 20_000),
                seed=7,
                report=str(Path(tmp) / "report.md"),
            )
            if model in ("m1", "m2", "m6"):
                args.trials = None
            if model == "m4":
                args.trials = 200_000
            try:
                code = run(args)
                label = MODELS[model][0]
                print(f"\n>>> {label}: завершено с кодом {code}\n{'=' * 78}")
            except Exception as exc:  # noqa: BLE001 — self-test reports, does not crash
                failures += 1
                print(f"\n!!! {model} упал: {type(exc).__name__}: {exc}\n{'=' * 78}")
    print(f"\nSelf-test: моделей {len(MODELS)}, падений {failures}")
    return 1 if failures else 0


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Верификатор математических моделей гемблинг-студии",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Модели: " + "; ".join(f"{k} = {v[0]}" for k, v in MODELS.items()),
    )
    p.add_argument("--model", choices=sorted(MODELS), help="какую модель проверять")
    p.add_argument("--config", help="путь к JSON-конфигу модели")
    p.add_argument("--trials", type=int, default=None, help="число испытаний (по умолчанию — из модели)")
    p.add_argument("--seed", type=int, default=None, help="seed для Monte Carlo моделей")
    p.add_argument(
        "--report",
        default="design/balance/simulation-report.md",
        help="куда записать отчёт",
    )
    p.add_argument("--selftest", action="store_true", help="прогнать все модели на встроенных конфигах")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.model or not args.config:
        p.error("нужны --model и --config (или --selftest)")

    try:
        return run(args)
    except ConfigError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"❌ файл не найден: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
