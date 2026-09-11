"""Phase-D analysis. The primary metric is SUCCESS RATE, not reasoning tokens.

    python analyze_phase_d.py

Writes `analysis/phase-d-observations.csv`, `analysis/phase-d-summary.json` and
`analysis/phase-d-report.md`.

## What is primary and what is not

Success rate is the question. Reasoning tokens, latency and prompt tokens are
secondary and are reported as description. Phase 1a already showed that the
prompt-token accounting on this route can vary for byte-identical input, so
`reasoning_tokens` differences are explicitly NOT used as causal evidence about
effort here; the confound check below decides whether they can be read at all.

## Tests

* **Fisher's exact test** on the 2x2 table of correct/not-correct by variant,
  computed exactly from hypergeometric probabilities (two-sided, by summing all
  tables no more probable than the observed one). Exact is the right choice at
  n=20 per arm.
* **Percentile bootstrap** for the success-rate difference, fixed seed.
* **Wilson score intervals** for each arm's rate, because a normal
  approximation misbehaves near 0 and 1.
* **Odds ratio**, with the Haldane-Anscombe 0.5 correction applied and flagged
  when a cell is zero. Reported as uninterpretable when an arm is degenerate.

Nothing is trimmed. UNPARSEABLE is always reported separately from INCORRECT.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESAMPLES = 10000
ALPHA = 0.05

CSV_FIELDS = [
    "sample_id", "phase", "microtest_id", "variant", "reasoning_effort_sent",
    "reasoning_effort_field_present", "status", "timestamp_utc", "request_id",
    "request_id_shape", "http_status", "prompt_tokens", "output_tokens",
    "reasoning_tokens_reported", "reasoning_tokens_field_present",
    "reasoning_stream_observed", "reasoning_stream_event_count",
    "ttft_ms", "ttfa_ms", "total_latency_ms", "finish_reason",
    "verdict", "parsed_answer", "expected_answer", "answer_lines_found",
    "retries", "response_sha256", "raw_answer",
]


def quantile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = q * (len(ordered) - 1)
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return float(ordered[low])
    return float(ordered[low] + (ordered[high] - ordered[low]) * (position - low))


def describe(values):
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": round(statistics.fmean(values), 1),
        "median": round(statistics.median(values), 1),
        "min": round(min(values), 1),
        "max": round(max(values), 1),
        "p25": round(quantile(values, 0.25), 1),
        "p75": round(quantile(values, 0.75), 1),
        "p90": round(quantile(values, 0.90), 1),
        "stdev": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
    }


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> dict:
    """Two-sided Fisher exact test on [[a, b], [c, d]].

    Sums the hypergeometric probability of every table with the same margins
    whose probability is no greater than the observed one (the conventional
    two-sided definition), with a tolerance for floating-point ties.
    """
    row1, row2 = a + b, c + d
    col1 = a + c
    total = row1 + row2
    if min(row1, row2, col1, b + d) < 0 or total == 0:
        return {"available": False}

    def probability(x: int) -> float:
        return (math.comb(row1, x) * math.comb(row2, col1 - x)) / math.comb(total, col1)

    low = max(0, col1 - row2)
    high = min(row1, col1)
    observed = probability(a)
    p_value = sum(probability(x) for x in range(low, high + 1)
                  if probability(x) <= observed * (1 + 1e-9))
    return {
        "available": True,
        "table": {"baseline": {"correct": c, "not_correct": d},
                  "high": {"correct": a, "not_correct": b}},
        "p_two_sided": round(min(1.0, p_value), 5),
        "method": "exact hypergeometric, two-sided by summing tables no more "
                  "probable than the observed one",
    }


def odds_ratio(a: int, b: int, c: int, d: int) -> dict:
    """high-correct odds over baseline-correct odds, with a zero-cell note."""
    zero_cell = 0 in (a, b, c, d)
    if zero_cell:
        aa, bb, cc, dd = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    else:
        aa, bb, cc, dd = a, b, c, d
    if bb == 0 or cc == 0 or dd == 0:
        return {"available": False, "reason": "degenerate table"}
    value = (aa * dd) / (bb * cc)
    log_se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    return {
        "available": True,
        "odds_ratio": round(value, 4),
        "ci95_low": round(math.exp(math.log(value) - 1.96 * log_se), 4),
        "ci95_high": round(math.exp(math.log(value) + 1.96 * log_se), 4),
        "haldane_anscombe_correction_applied": zero_cell,
        "interpretable": not zero_cell,
        "note": ("a zero cell forced the 0.5 correction, so the point estimate is "
                 "an artefact of that correction as much as of the data")
        if zero_cell else "no zero cells",
    }


def wilson(correct: int, n: int) -> dict:
    if n == 0:
        return {"available": False}
    z = 1.959963984540054
    phat = correct / n
    denominator = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denominator
    margin = (z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / denominator
    return {"available": True, "rate": round(phat, 4),
            "ci95_low": round(max(0.0, centre - margin), 4),
            "ci95_high": round(min(1.0, centre + margin), 4),
            "method": "Wilson score interval"}


def bootstrap_rate_difference(high: list[float], base: list[float], seed: int) -> dict:
    if not high or not base:
        return {"available": False}
    rng = random.Random(seed)
    diffs = []
    for _ in range(RESAMPLES):
        rh = [high[rng.randrange(len(high))] for _ in range(len(high))]
        rb = [base[rng.randrange(len(base))] for _ in range(len(base))]
        diffs.append(statistics.fmean(rh) - statistics.fmean(rb))
    diffs.sort()
    point = statistics.fmean(high) - statistics.fmean(base)
    return {
        "available": True, "resamples": RESAMPLES, "seed": seed,
        "point_estimate_pp": round(100 * point, 2),
        "ci95_low_pp": round(100 * quantile(diffs, ALPHA / 2), 2),
        "ci95_high_pp": round(100 * quantile(diffs, 1 - ALPHA / 2), 2),
        "includes_zero": quantile(diffs, ALPHA / 2) <= 0 <= quantile(diffs, 1 - ALPHA / 2),
    }


def jackknife_difference(high: list[float], base: list[float]) -> dict:
    """Recompute the difference dropping one observation at a time.

    Answers "is this carried by a single sample?" without deleting anything from
    the headline numbers.
    """
    if len(high) < 2 or len(base) < 2:
        return {"available": False}
    diffs = []
    for i in range(len(high)):
        subset = high[:i] + high[i + 1:]
        diffs.append(statistics.fmean(subset) - statistics.fmean(base))
    for i in range(len(base)):
        subset = base[:i] + base[i + 1:]
        diffs.append(statistics.fmean(high) - statistics.fmean(subset))
    return {
        "available": True,
        "min_pp": round(100 * min(diffs), 2),
        "max_pp": round(100 * max(diffs), 2),
        "all_same_sign_as_observed": all(
            (d > 0) == (statistics.fmean(high) - statistics.fmean(base) > 0) for d in diffs),
    }


def variant_block(rows: list[dict]) -> dict:
    ok = [r for r in rows if r["status"] == "OK"]
    verdicts = [r["verdict"] for r in ok]
    reported = [float(r["reasoning_tokens_reported"]) for r in ok
                if r["reasoning_tokens_reported"] is not None]
    delivered = sum(1 for r in ok if r["reasoning_stream_observed"] is True)
    return {
        "n_slots": len(rows),
        "n_ok": len(ok),
        "n_failed": len(rows) - len(ok),
        "correct": verdicts.count("CORRECT"),
        "incorrect": verdicts.count("INCORRECT"),
        "unparseable": verdicts.count("UNPARSEABLE"),
        "success_rate": round(verdicts.count("CORRECT") / len(ok), 4) if ok else None,
        "wilson_ci": wilson(verdicts.count("CORRECT"), len(ok)),
        "distinct_wrong_answers": sorted({str(r["parsed_answer"]) for r in ok
                                          if r["verdict"] == "INCORRECT"}),
        "reasoning_tokens": {
            "reported_count": len(reported),
            "missing_count": len(ok) - len(reported),
            "reported_zero_count": sum(1 for r in ok
                                       if r["reasoning_tokens_reported"] == 0),
            **describe(reported),
        },
        "output_tokens": describe([float(r["output_tokens"]) for r in ok
                                   if r["output_tokens"] is not None]),
        "ttfa_ms": describe([float(r["ttfa_ms"]) for r in ok if r["ttfa_ms"] is not None]),
        "total_latency_ms": describe([float(r["total_latency_ms"]) for r in ok]),
        "reasoning_delivery": {
            "stream_observed_true": delivered,
            "percentage_observed": round(100 * delivered / len(ok), 1) if ok else None,
            "note": "false means delivery was not observed, not that the model "
                    "did not reason",
        },
        "prompt_tokens_counts": {
            str(pt): sum(1 for r in ok if r["prompt_tokens"] == pt)
            for pt in sorted({r["prompt_tokens"] for r in ok}, key=lambda v: (v is None, v))
        },
        "request_id_shapes": {s: sum(1 for r in ok if r["request_id_shape"] == s)
                              for s in sorted({r["request_id_shape"] for r in ok})},
        "finish_reasons": {str(f): sum(1 for r in ok if r["finish_reason"] == f)
                           for f in sorted({str(r["finish_reason"]) for r in ok})},
    }


def main() -> int:
    config = json.loads((HERE / "phase-d-config.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in
            (HERE / "raw" / "phase-d.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()]
    seed = config["bootstrap_seed"]

    (HERE / "analysis").mkdir(exist_ok=True)
    with (HERE / "analysis" / "phase-d-observations.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in CSV_FIELDS})

    base_rows = [r for r in rows if r["variant"] == "baseline"]
    high_rows = [r for r in rows if r["variant"] == "high"]
    per_variant = {"baseline": variant_block(base_rows), "high": variant_block(high_rows)}

    def ok(rs):
        return [r for r in rs if r["status"] == "OK"]

    correct_base = [1.0 if r["verdict"] == "CORRECT" else 0.0 for r in ok(base_rows)]
    correct_high = [1.0 if r["verdict"] == "CORRECT" else 0.0 for r in ok(high_rows)]

    a = per_variant["high"]["correct"]
    b = per_variant["high"]["n_ok"] - a
    c = per_variant["baseline"]["correct"]
    d = per_variant["baseline"]["n_ok"] - c

    diff_pp = (round(100 * (per_variant["high"]["success_rate"]
                            - per_variant["baseline"]["success_rate"]), 2)
               if per_variant["high"]["success_rate"] is not None
               and per_variant["baseline"]["success_rate"] is not None else None)

    primary = {
        "metric": "success rate",
        "baseline": per_variant["baseline"]["success_rate"],
        "high": per_variant["high"]["success_rate"],
        "difference_pp": diff_pp,
        "relative_pct": (round(100 * (per_variant["high"]["success_rate"]
                                      - per_variant["baseline"]["success_rate"])
                               / per_variant["baseline"]["success_rate"], 2)
                         if per_variant["baseline"]["success_rate"] else None),
        "bootstrap": bootstrap_rate_difference(correct_high, correct_base, seed),
        "fisher_exact": fisher_exact_two_sided(a, b, c, d),
        "odds_ratio": odds_ratio(a, b, c, d),
        "jackknife": jackknife_difference(correct_high, correct_base),
    }

    # ---- prompt-token confound check, carried over from phase 1a -------------
    all_ok = ok(rows)
    distinct_pt = sorted({r["prompt_tokens"] for r in all_ok},
                         key=lambda v: (v is None, v))
    pt_cross = {
        str(pt): {
            "baseline": sum(1 for r in ok(base_rows) if r["prompt_tokens"] == pt),
            "high": sum(1 for r in ok(high_rows) if r["prompt_tokens"] == pt),
            "correct": sum(1 for r in all_ok
                           if r["prompt_tokens"] == pt and r["verdict"] == "CORRECT"),
            "n": sum(1 for r in all_ok if r["prompt_tokens"] == pt),
        }
        for pt in distinct_pt
    }
    for bucket in pt_cross.values():
        bucket["success_rate"] = (round(bucket["correct"] / bucket["n"], 4)
                                  if bucket["n"] else None)
    varies = len(distinct_pt) > 1
    rates = [v["success_rate"] for v in pt_cross.values()
             if v["n"] >= 3 and v["success_rate"] is not None]
    confound = {
        "prompt_bytes_identical_in_every_sample": True,
        "distinct_prompt_token_counts": distinct_pt,
        "varies_for_identical_input": varies,
        "cross_tab": pt_cross,
        "prompt_token_group_predicts_correctness": (
            (max(rates) - min(rates) >= 0.2) if len(rates) > 1 else False),
        "consequence": (
            "prompt-token accounting varied again for byte-identical input. "
            "Per the standing rule from phase 1a, reasoning_tokens differences "
            "are NOT read as causal evidence about effort. Whether the SUCCESS "
            "RATE comparison is also affected is decided by whether the groups "
            "are distributed unevenly across variants - see cross_tab."
        ) if varies else "single consistent prompt token count; no confound observed",
        "interpretation_limit": "observable accounting only; nothing here "
                                "establishes what the provider served or why",
    }

    # ---- exploratory: compute and latency against correctness ---------------
    exploratory = {}
    for scope, rs in (("pooled", all_ok), ("baseline", ok(base_rows)), ("high", ok(high_rows))):
        buckets = {}
        for verdict in ("CORRECT", "INCORRECT", "UNPARSEABLE"):
            subset = [r for r in rs if r["verdict"] == verdict]
            if not subset:
                continue
            buckets[verdict] = {
                "n": len(subset),
                "reasoning_tokens": describe([float(r["reasoning_tokens_reported"])
                                              for r in subset
                                              if r["reasoning_tokens_reported"] is not None]),
                "total_latency_ms": describe([float(r["total_latency_ms"]) for r in subset]),
                "prompt_tokens": describe([float(r["prompt_tokens"]) for r in subset
                                           if r["prompt_tokens"] is not None]),
            }
        exploratory[scope] = buckets
    exploratory["caution"] = ("differences between correct and incorrect responses "
                              "are associations within one instrument. They do not "
                              "establish that spending more compute causes a correct "
                              "answer, or the reverse.")

    # ---- decision gate, operationalised and stated -------------------------
    parsing_asymmetry = abs(per_variant["high"]["unparseable"]
                            - per_variant["baseline"]["unparseable"]) > 2
    jack = primary["jackknife"]
    single_sample_fragile = not (jack.get("available")
                                 and jack.get("all_same_sign_as_observed", False))
    gate_a = bool(diff_pp is not None and diff_pp >= 10
                  and not parsing_asymmetry and not single_sample_fragile)
    boot = primary["bootstrap"]
    fisher = primary["fisher_exact"]
    gate_b = bool(diff_pp is not None and 0 < diff_pp < 10
                  and ((fisher.get("available") and fisher["p_two_sided"] < 0.10)
                       or (boot.get("available") and not boot["includes_zero"])))
    blocked = bool(confound["varies_for_identical_input"]
                   and confound["prompt_token_group_predicts_correctness"])

    if blocked:
        outcome = ("STOP - a confound blocks a reasonable causal reading of the "
                   "quality comparison")
        recommendation = "STOP"
    elif gate_a:
        outcome = "PROCEED TO LARGER SAMPLE - quality signal observed at >= 10 pp"
        recommendation = "INCREASE SAMPLE"
    elif gate_b:
        outcome = ("PROCEED TO LARGER SAMPLE - difference below 10 pp but "
                   "consistent enough to justify more statistical power")
        recommendation = "INCREASE SAMPLE"
    else:
        outcome = "STOP - no quality signal observed"
        recommendation = "STOP"

    gate = {
        "A_quality_signal": {
            "criterion": "success rate improves by >= 10 pp, and the effect is not "
                         "carried by one extreme sample or by a parsing asymmetry",
            "difference_pp": diff_pp,
            "parsing_asymmetry_detected": parsing_asymmetry,
            "unparseable_baseline": per_variant["baseline"]["unparseable"],
            "unparseable_high": per_variant["high"]["unparseable"],
            "jackknife_keeps_the_sign": not single_sample_fragile,
            "met": gate_a,
        },
        "B_weaker_but_consistent": {
            "criterion": "difference below 10 pp but the exact test or the bootstrap "
                         "CI suggests a signal worth more power",
            "fisher_p": fisher.get("p_two_sided"),
            "bootstrap_ci_pp": [boot.get("ci95_low_pp"), boot.get("ci95_high_pp")],
            "met": gate_b,
        },
        "confound_blocks_causal_reading": blocked,
        "outcome": outcome,
        "recommendation": recommendation,
        "larger_sample_not_executed": True,
        "max_variant_executed": False,
        "note": "no further samples are run by this script under any outcome, and "
                "reasoning_effort=max is outside this phase entirely.",
    }

    summary = {
        "experiment": HERE.name,
        "phase": "D",
        "is_mondaybench_run": False,
        "microtest_id": config["microtest_id"],
        "prompt_sha256": config["prompt_sha256"],
        "answer_key": config["answer_key"],
        "answer_type": config["answer_type"],
        "calls": {
            "phase_d_slots": len(rows),
            "phase_d_ok": len(all_ok),
            "phase_d_failed": len(rows) - len(all_ok),
            "retries_total": sum(r.get("retries", 0) for r in rows),
            "api_attempts": sum(len(r.get("attempts", [])) for r in rows),
        },
        "primary": primary,
        "per_variant": per_variant,
        "prompt_token_confound": confound,
        "exploratory_compute_vs_quality": exploratory,
        "decision_gate": gate,
    }
    (HERE / "analysis" / "phase-d-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    lines = render(summary)
    (HERE / "analysis" / "phase-d-report.md").write_text("\n".join(lines) + "\n",
                                                         encoding="utf-8")
    print("\n".join(lines))
    return 0


def render(s: dict) -> list[str]:
    b, h = s["per_variant"]["baseline"], s["per_variant"]["high"]
    p = s["primary"]
    out = [f"# {s['experiment']} - phase D report", "",
           f"Microtest `{s['microtest_id']}`, prompt sha256 `{s['prompt_sha256']}`, "
           f"answer key `{s['answer_key']}` ({s['answer_type']}).",
           "Primary metric: **success rate**. Not a MondayBench run.", "",
           "## Calls", ""]
    out += [f"- {k}: {v}" for k, v in s["calls"].items()]

    out += ["", "## Primary: task quality", "",
            "| metric | baseline | high |", "| --- | --- | --- |",
            f"| completed | {b['n_ok']} | {h['n_ok']} |",
            f"| CORRECT | {b['correct']} | {h['correct']} |",
            f"| INCORRECT | {b['incorrect']} | {h['incorrect']} |",
            f"| UNPARSEABLE | {b['unparseable']} | {h['unparseable']} |",
            f"| **success rate** | **{b['success_rate']}** | **{h['success_rate']}** |",
            f"| Wilson 95% CI | [{b['wilson_ci'].get('ci95_low')}, "
            f"{b['wilson_ci'].get('ci95_high')}] | [{h['wilson_ci'].get('ci95_low')}, "
            f"{h['wilson_ci'].get('ci95_high')}] |",
            f"| distinct wrong answers | {b['distinct_wrong_answers']} | "
            f"{h['distinct_wrong_answers']} |", "",
            f"- difference: **{p['difference_pp']} pp** absolute"
            + (f", {p['relative_pct']}% relative" if p["relative_pct"] is not None else "")]
    if p["bootstrap"].get("available"):
        boot = p["bootstrap"]
        out.append(f"- bootstrap 95% CI: [{boot['ci95_low_pp']}, {boot['ci95_high_pp']}] pp "
                   f"({boot['resamples']} resamples, seed {boot['seed']}, "
                   f"includes zero: {boot['includes_zero']})")
    if p["fisher_exact"].get("available"):
        out.append(f"- Fisher exact (two-sided): p = {p['fisher_exact']['p_two_sided']}")
    if p["odds_ratio"].get("available"):
        odds = p["odds_ratio"]
        out.append(f"- odds ratio: {odds['odds_ratio']} "
                   f"[{odds['ci95_low']}, {odds['ci95_high']}] - "
                   f"interpretable: {odds['interpretable']}; {odds['note']}")
    else:
        out.append(f"- odds ratio: not interpretable ({p['odds_ratio'].get('reason')})")
    if p["jackknife"].get("available"):
        jack = p["jackknife"]
        out.append(f"- jackknife difference range: [{jack['min_pp']}, {jack['max_pp']}] pp; "
                   f"sign stable under dropping any single sample: "
                   f"{jack['all_same_sign_as_observed']}")

    for metric, title in (("reasoning_tokens", "reasoning_tokens (secondary)"),
                          ("total_latency_ms", "total latency ms (secondary)"),
                          ("ttfa_ms", "TTFA ms (secondary)"),
                          ("output_tokens", "output_tokens (secondary)")):
        out += ["", f"## {title}", "", "| stat | baseline | high |", "| --- | --- | --- |"]
        for stat in ("n", "mean", "median", "min", "p25", "p75", "p90", "max", "stdev"):
            out.append(f"| {stat} | {b[metric].get(stat)} | {h[metric].get(stat)} |")
    out += ["",
            f"- reasoning_tokens reported / absent / zero: "
            f"baseline {b['reasoning_tokens']['reported_count']} / "
            f"{b['reasoning_tokens']['missing_count']} / "
            f"{b['reasoning_tokens']['reported_zero_count']}, "
            f"high {h['reasoning_tokens']['reported_count']} / "
            f"{h['reasoning_tokens']['missing_count']} / "
            f"{h['reasoning_tokens']['reported_zero_count']}",
            f"- reasoning delivery observed: "
            f"baseline {b['reasoning_delivery']['stream_observed_true']}/{b['n_ok']} "
            f"({b['reasoning_delivery']['percentage_observed']}%), "
            f"high {h['reasoning_delivery']['stream_observed_true']}/{h['n_ok']} "
            f"({h['reasoning_delivery']['percentage_observed']}%)"]

    conf = s["prompt_token_confound"]
    out += ["", "## prompt_tokens cross-tab (byte-identical input)", "",
            f"- distinct prompt_token counts: {conf['distinct_prompt_token_counts']}",
            f"- varies for identical input: **{conf['varies_for_identical_input']}**",
            f"- group predicts correctness: "
            f"{conf['prompt_token_group_predicts_correctness']}", "",
            "| prompt_tokens | baseline n | high n | correct | n | success rate |",
            "| --- | --- | --- | --- | --- | --- |"]
    for key, bucket in conf["cross_tab"].items():
        out.append(f"| {key} | {bucket['baseline']} | {bucket['high']} | "
                   f"{bucket['correct']} | {bucket['n']} | {bucket['success_rate']} |")
    out += ["", f"- {conf['consequence']}"]

    out += ["", "## Exploratory: compute and latency vs correctness", ""]
    for scope in ("pooled", "baseline", "high"):
        buckets = s["exploratory_compute_vs_quality"].get(scope) or {}
        for verdict, block in buckets.items():
            out.append(f"- {scope} / {verdict}: n={block['n']}, "
                       f"reasoning median={block['reasoning_tokens'].get('median')}, "
                       f"latency median={block['total_latency_ms'].get('median')}, "
                       f"prompt_tokens median={block['prompt_tokens'].get('median')}")
    out += ["", f"- {s['exploratory_compute_vs_quality']['caution']}"]

    g = s["decision_gate"]
    out += ["", "## Decision gate", "",
            f"- A: {g['A_quality_signal']['criterion']}",
            f"  - difference {g['A_quality_signal']['difference_pp']} pp, "
            f"parsing asymmetry {g['A_quality_signal']['parsing_asymmetry_detected']}, "
            f"jackknife sign stable {g['A_quality_signal']['jackknife_keeps_the_sign']} "
            f"-> **{'MET' if g['A_quality_signal']['met'] else 'NOT MET'}**",
            f"- B: {g['B_weaker_but_consistent']['criterion']}",
            f"  - Fisher p {g['B_weaker_but_consistent']['fisher_p']}, bootstrap CI "
            f"{g['B_weaker_but_consistent']['bootstrap_ci_pp']} pp "
            f"-> **{'MET' if g['B_weaker_but_consistent']['met'] else 'NOT MET'}**",
            f"- confound blocks causal reading: {g['confound_blocks_causal_reading']}",
            f"- **outcome: {g['outcome']}**",
            f"- **recommendation: {g['recommendation']}**",
            f"- larger sample not executed: {g['larger_sample_not_executed']}; "
            f"max executed: {g['max_variant_executed']}"]
    return out


if __name__ == "__main__":
    raise SystemExit(main())
