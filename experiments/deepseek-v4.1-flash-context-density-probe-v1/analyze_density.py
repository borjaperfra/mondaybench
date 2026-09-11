"""The density curve, and the decision gate exactly as it was specified.

    python analyze_density.py

Writes `analysis/density-summary.json`, `analysis/density-report.md` and
`analysis/density-observations.csv`.

## What the primary metric is

Task success: CORRECT over all attempted samples at that level, with
BUDGET_EXHAUSTED counted as a failure and reported in its own column. INCORRECT,
UNPARSEABLE and BUDGET_EXHAUSTED are never merged - a wrong answer, an
unreadable answer and a run that never finished thinking are three different
behaviours.

Infrastructure failures are different again: they say nothing about the model
and are excluded from the denominator, and reported separately.

## What reasoning tokens are not

Secondary description. Phase 1a established on this route that reported compute
does not move monotonically with anything useful, and that the input accounting
can vary for byte-identical input. So more reasoning tokens are not read as
better reasoning, and no causal claim is made from them here. The prompt-token
check is repeated because it is cheap and because it has fired before.
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEVELS = ("compact", "medium", "dense")

CSV_FIELDS = [
    "sample_id", "level", "variant", "reasoning_effort_sent", "status", "outcome",
    "scored_verdict", "parsed_answer", "expected_answer", "timestamp_utc",
    "request_id", "request_id_shape", "http_status", "prompt_bytes", "prompt_tokens",
    "output_tokens", "reasoning_tokens_reported", "reasoning_tokens_field_present",
    "reasoning_stream_observed", "reasoning_stream_event_count", "ttft_ms", "ttfa_ms",
    "total_latency_ms", "finish_reason", "answer_lines_found", "retries",
    "response_sha256", "prompt_sha256", "raw_answer",
]


def quantile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    import math
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
        "min": round(min(values), 1),
        "p25": round(quantile(values, 0.25), 1),
        "median": round(statistics.median(values), 1),
        "p75": round(quantile(values, 0.75), 1),
        "max": round(max(values), 1),
        "mean": round(statistics.fmean(values), 1),
        "stdev": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
    }


def level_block(rows: list[dict]) -> dict:
    attempted = [r for r in rows if r.get("outcome") != "INFRA_FAILURE"]
    infra = [r for r in rows if r.get("outcome") == "INFRA_FAILURE"]
    outcomes = [r.get("outcome") for r in attempted]
    answered = [r for r in attempted if r["status"] == "OK"]
    reported = [float(r["reasoning_tokens_reported"]) for r in answered
                if r.get("reasoning_tokens_reported") is not None]
    delivered = sum(1 for r in answered if r.get("reasoning_stream_observed") is True)
    correct = outcomes.count("CORRECT")
    return {
        "n_slots": len(rows),
        "n_attempted": len(attempted),
        "infrastructure_failures": len(infra),
        "correct": correct,
        "incorrect": outcomes.count("INCORRECT"),
        "unparseable": outcomes.count("UNPARSEABLE"),
        "budget_exhausted": outcomes.count("BUDGET_EXHAUSTED"),
        "task_success_rate": round(correct / len(attempted), 4) if attempted else None,
        "wrong_answers_given": sorted({str(r.get("parsed_answer")) for r in attempted
                                       if r.get("outcome") == "INCORRECT"}),
        "reasoning_tokens": {
            "reported_count": len(reported),
            "missing_count": len(answered) - len(reported),
            "reported_zero_count": sum(1 for r in answered
                                       if r.get("reasoning_tokens_reported") == 0),
            **describe(reported),
        },
        "output_tokens": describe([float(r["output_tokens"]) for r in answered
                                   if r.get("output_tokens") is not None]),
        "total_latency_ms": describe([float(r["total_latency_ms"]) for r in answered
                                      if r.get("total_latency_ms") is not None]),
        "ttfa_ms": describe([float(r["ttfa_ms"]) for r in answered
                             if r.get("ttfa_ms") is not None]),
        "prompt_tokens_observed": sorted({r["prompt_tokens"] for r in answered
                                          if r.get("prompt_tokens") is not None}),
        "prompt_bytes": next((r["prompt_bytes"] for r in rows
                              if r.get("prompt_bytes")), None),
        "reasoning_delivery": {
            "stream_observed_true": delivered,
            "percentage_observed": round(100 * delivered / len(answered), 1)
            if answered else None,
            "note": "false means delivery was not observed, not that the model "
                    "did not reason",
        },
        "finish_reasons": {str(f): sum(1 for r in attempted
                                       if r.get("finish_reason") == f)
                           for f in sorted({str(r.get("finish_reason"))
                                            for r in attempted})},
        "request_id_shapes": {s: sum(1 for r in answered
                                     if r.get("request_id_shape") == s)
                              for s in sorted({str(r.get("request_id_shape"))
                                               for r in answered})},
    }


def main() -> int:
    config = json.loads((HERE / "experiment-config.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in
            (HERE / "raw" / "baseline-density.jsonl").read_text(
                encoding="utf-8").splitlines() if line.strip()]

    (HERE / "analysis").mkdir(exist_ok=True)
    with (HERE / "analysis" / "density-observations.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in CSV_FIELDS})

    per_level = {level: level_block([r for r in rows if r["level"] == level])
                 for level in LEVELS}

    def rate(level):
        return per_level[level]["task_success_rate"]

    def med(level, metric):
        return per_level[level][metric].get("median")

    deltas = {}
    for first, second in (("compact", "medium"), ("medium", "dense"),
                          ("compact", "dense")):
        a, b = rate(first), rate(second)
        deltas[f"{first} -> {second}"] = {
            "success_rate_delta_pp": (round(100 * (b - a), 2)
                                      if a is not None and b is not None else None),
            "reasoning_tokens_median_delta": (
                round(med(second, "reasoning_tokens") - med(first, "reasoning_tokens"), 1)
                if med(first, "reasoning_tokens") is not None
                and med(second, "reasoning_tokens") is not None else None),
            "latency_median_delta_ms": (
                round(med(second, "total_latency_ms") - med(first, "total_latency_ms"), 1)
                if med(first, "total_latency_ms") is not None
                and med(second, "total_latency_ms") is not None else None),
            "budget_exhausted_delta": (per_level[second]["budget_exhausted"]
                                       - per_level[first]["budget_exhausted"]),
        }

    # Byte-identical input per level, so any spread inside a level is the
    # accounting behaviour seen in phase 1a, not a prompt difference.
    accounting = {
        level: {
            "prompt_bytes": per_level[level]["prompt_bytes"],
            "prompt_tokens_observed": per_level[level]["prompt_tokens_observed"],
            "varies_within_level": len(per_level[level]["prompt_tokens_observed"]) > 1,
            "bytes_per_token": (
                round(per_level[level]["prompt_bytes"]
                      / per_level[level]["prompt_tokens_observed"][0], 2)
                if per_level[level]["prompt_tokens_observed"] else None),
        }
        for level in LEVELS
    }
    any_variation = any(entry["varies_within_level"] for entry in accounting.values())

    # ---- decision gate, the four cases as specified ------------------------
    compact_rate = rate("compact")
    candidate_levels = [level for level in ("medium", "dense")
                        if rate(level) is not None and 0.20 <= rate(level) <= 0.80]
    only_budget_failures = all(
        per_level[level]["incorrect"] == 0 and per_level[level]["unparseable"] == 0
        for level in LEVELS) and any(per_level[level]["budget_exhausted"] > 0
                                     for level in LEVELS)
    all_saturated = all(rate(level) == 1.0 for level in LEVELS)

    if compact_rate is None:
        case, outcome, recommendation = "indeterminate", "no compact data", "STOP"
    elif compact_rate < 0.80:
        case = "CASE 1"
        outcome = ("STOP - compact is below 80%, so the instrument probably raised "
                   "the underlying logical difficulty rather than isolating "
                   "context density. Degradation cannot be attributed to density.")
        recommendation = "STOP"
    elif only_budget_failures:
        case = "CASE 4"
        outcome = ("STOP - the only failures are BUDGET_EXHAUSTED. Whether this "
                   "measures context reliability or output-budget behaviour is a "
                   "human decision, not an automatic selection.")
        recommendation = "STOP"
    elif all_saturated:
        case = "CASE 3"
        outcome = ("STOP - all three levels are saturated. The instrument does not "
                   "discriminate, and no harder one is designed automatically.")
        recommendation = "STOP"
    elif compact_rate == 1.0 and candidate_levels:
        case = "CASE 2"
        outcome = (f"CANDIDATE at {', '.join(candidate_levels)} - compact is 100% and "
                   f"that level sits in the 20-80% band. The pre-registered next "
                   f"step is to extend ONLY that level to 10 baseline runs, with no "
                   f"treatment, and re-check that it stays in 30-85%.")
        recommendation = "CANDIDATE FOUND"
    else:
        case = "no case matched cleanly"
        outcome = ("STOP - the pattern does not match any specified case; reporting "
                   "rather than choosing.")
        recommendation = "STOP"

    # More than one specified case can hold at once, and here the order they are
    # tested in is an implementation choice of mine, not something the
    # specification fixed. So every case that holds is reported, and the one the
    # branch above happened to reach first is not presented as the only reading.
    cases_matched = []
    if compact_rate is not None and compact_rate < 0.80:
        cases_matched.append("CASE 1 (compact below 80%)")
    if compact_rate == 1.0 and candidate_levels:
        cases_matched.append("CASE 2 (compact 100%, a denser level in band)")
    if all_saturated:
        cases_matched.append("CASE 3 (all three saturated)")
    if only_budget_failures:
        cases_matched.append("CASE 4 (the only failures are budget exhaustion)")

    total_incorrect = sum(per_level[level]["incorrect"] for level in LEVELS)
    total_unparseable = sum(per_level[level]["unparseable"] for level in LEVELS)
    case_1_rationale_holds = total_incorrect > 0 or total_unparseable > 0

    gate = {
        "case": case,
        "case_selected_by": "first match in my implementation's test order; the "
                            "specification did not fix a precedence",
        "cases_matched": cases_matched,
        "case_1_rationale_supported_by_the_data": case_1_rationale_holds,
        "case_1_rationale_note": (
            "CASE 1 reads a low compact score as the instrument having raised the "
            "logical difficulty. That reading requires wrong answers, and there "
            f"were {total_incorrect} incorrect and {total_unparseable} unparseable "
            "responses in the whole run. Where CASE 4 also holds, it is the better "
            "description of what happened. Both recommend STOP, so nothing about "
            "the outcome turns on which is quoted."
        ) if not case_1_rationale_holds else None,
        "compact_success_rate": compact_rate,
        "medium_success_rate": rate("medium"),
        "dense_success_rate": rate("dense"),
        "candidate_levels_in_20_80_band": candidate_levels,
        "all_three_saturated": all_saturated,
        "failures_are_only_budget_exhaustion": only_budget_failures,
        "outcome": outcome,
        "recommendation": recommendation,
        "treatment_executed": False,
        "max_executed": False,
        "note": "no treatment is run by this script under any outcome. "
                "baseline-vs-high is phase 1d and needs explicit authorisation.",
    }

    degradation = {
        "success_rate_falls_with_density": (
            compact_rate is not None and rate("dense") is not None
            and rate("dense") < compact_rate),
        "monotone_fall": (
            None if any(rate(level) is None for level in LEVELS)
            else rate("compact") >= rate("medium") >= rate("dense")),
        "latency_rises_with_density": (
            med("compact", "total_latency_ms") is not None
            and med("dense", "total_latency_ms") is not None
            and med("dense", "total_latency_ms") > med("compact", "total_latency_ms")),
        "reasoning_tokens_rise_with_density": (
            med("compact", "reasoning_tokens") is not None
            and med("dense", "reasoning_tokens") is not None
            and med("dense", "reasoning_tokens") > med("compact", "reasoning_tokens")),
        "budget_exhaustions_appear_with_density": (
            per_level["dense"]["budget_exhausted"] > per_level["compact"]["budget_exhausted"]),
        "variability_rises_with_density": (
            per_level["compact"]["reasoning_tokens"].get("stdev") is not None
            and per_level["dense"]["reasoning_tokens"].get("stdev") is not None
            and per_level["dense"]["reasoning_tokens"]["stdev"]
            > per_level["compact"]["reasoning_tokens"]["stdev"]),
        "reasoning_delivery_changes": len({
            per_level[level]["reasoning_delivery"]["percentage_observed"]
            for level in LEVELS}) > 1,
        "caution": "n=5 per level. A single sample moves a rate by 20 points, so "
                   "the shape of this curve is a direction to investigate, not an "
                   "estimate. No causal claim is made from reasoning tokens.",
        "what_this_can_and_cannot_separate": {
            "H1 reasoning deficit": "argued against, not by this phase alone but "
                                    "with phase 1b's 24/24 on compact problems plus "
                                    "whatever compact scores here",
            "H2 constraint persistence under context": "supported only if compact "
                                                       "stays high while a denser "
                                                       "level falls",
        },
    }

    summary = {
        "experiment": HERE.name,
        "phase": "1c",
        "is_mondaybench_run": False,
        "treatment_executed": False,
        "answer_key": config["answer_key"],
        "prompt_hashes": config["prompt_hashes"],
        "calls": {
            "slots": len(rows),
            "attempted": sum(per_level[level]["n_attempted"] for level in LEVELS),
            "infrastructure_failures": sum(per_level[level]["infrastructure_failures"]
                                           for level in LEVELS),
            "retries_total": sum(r.get("retries", 0) for r in rows),
            "api_attempts": sum(len(r.get("attempts", [])) for r in rows),
        },
        "per_level": per_level,
        "density_curve": [
            {"level": level,
             "prompt_bytes": per_level[level]["prompt_bytes"],
             "prompt_tokens": per_level[level]["prompt_tokens_observed"],
             "success": f"{per_level[level]['correct']}/{per_level[level]['n_attempted']}",
             "task_success_rate": rate(level),
             "reasoning_tokens_median": med(level, "reasoning_tokens"),
             "latency_median_ms": med(level, "total_latency_ms")}
            for level in LEVELS
        ],
        "deltas": deltas,
        "prompt_token_accounting": {
            **accounting,
            "varies_for_byte_identical_input_within_any_level": any_variation,
            "note": "each level's prompt is byte-identical across its samples, so "
                    "any spread within a level is the accounting behaviour first "
                    "seen in phase 1a. Observable behaviour only; nothing here "
                    "establishes anything about the provider's internals.",
        },
        "degradation_assessment": degradation,
        "decision_gate": gate,
    }
    (HERE / "analysis" / "density-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    lines = render(summary)
    (HERE / "analysis" / "density-report.md").write_text("\n".join(lines) + "\n",
                                                         encoding="utf-8")
    print("\n".join(lines))
    return 0


def render(s: dict) -> list[str]:
    out = [f"# {s['experiment']} - phase 1c report", "",
           f"Answer key `{s['answer_key']}`, identical in all three levels. "
           f"Baseline only - no treatment was sent.",
           "Not a MondayBench run.", "", "## Calls", ""]
    out += [f"- {k}: {v}" for k, v in s["calls"].items()]

    out += ["", "## Density curve", "",
            "| density | prompt bytes | prompt tokens | success | rate | "
            "reasoning median | latency median ms |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in s["density_curve"]:
        out.append(f"| {row['level']} | {row['prompt_bytes']} | "
                   f"{row['prompt_tokens']} | {row['success']} | "
                   f"{row['task_success_rate']} | {row['reasoning_tokens_median']} | "
                   f"{row['latency_median_ms']} |")

    out += ["", "## Outcomes, never merged", "",
            "| density | CORRECT | INCORRECT | UNPARSEABLE | BUDGET_EXHAUSTED | "
            "infra failures | wrong answers given |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        block = s["per_level"][level]
        out.append(f"| {level} | {block['correct']} | {block['incorrect']} | "
                   f"{block['unparseable']} | {block['budget_exhausted']} | "
                   f"{block['infrastructure_failures']} | "
                   f"{block['wrong_answers_given']} |")

    out += ["", "## Deltas", "",
            "| step | success rate delta | reasoning median delta | "
            "latency median delta ms | budget exhausted delta |",
            "| --- | --- | --- | --- | --- |"]
    for step, delta in s["deltas"].items():
        out.append(f"| {step} | {delta['success_rate_delta_pp']} pp | "
                   f"{delta['reasoning_tokens_median_delta']} | "
                   f"{delta['latency_median_delta_ms']} | "
                   f"{delta['budget_exhausted_delta']} |")

    for metric, title in (("reasoning_tokens", "reasoning_tokens (secondary)"),
                          ("total_latency_ms", "total latency ms (secondary)"),
                          ("ttfa_ms", "TTFA ms (secondary)"),
                          ("output_tokens", "output_tokens (secondary)")):
        out += ["", f"## {title}", "",
                "| stat | compact | medium | dense |", "| --- | --- | --- | --- |"]
        for stat in ("n", "min", "p25", "median", "p75", "max", "mean", "stdev"):
            out.append(f"| {stat} | " + " | ".join(
                str(s["per_level"][level][metric].get(stat)) for level in LEVELS) + " |")

    out += ["", "## Reasoning delivery", ""]
    for level in LEVELS:
        block = s["per_level"][level]["reasoning_delivery"]
        out.append(f"- {level}: {block['stream_observed_true']} observed "
                   f"({block['percentage_observed']}%)")

    acct = s["prompt_token_accounting"]
    out += ["", "## prompt_tokens against prompt bytes", "",
            "| level | bytes | tokens observed | varies within level | bytes/token |",
            "| --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        entry = acct[level]
        out.append(f"| {level} | {entry['prompt_bytes']} | "
                   f"{entry['prompt_tokens_observed']} | "
                   f"{entry['varies_within_level']} | {entry['bytes_per_token']} |")
    out += ["", f"- varies for byte-identical input within any level: "
                f"**{acct['varies_for_byte_identical_input_within_any_level']}**",
            f"- {acct['note']}"]

    deg = s["degradation_assessment"]
    out += ["", "## Degradation assessment", ""]
    for key in ("success_rate_falls_with_density", "monotone_fall",
                "latency_rises_with_density", "reasoning_tokens_rise_with_density",
                "budget_exhaustions_appear_with_density",
                "variability_rises_with_density", "reasoning_delivery_changes"):
        out.append(f"- {key}: **{deg[key]}**")
    out += [f"- {deg['caution']}", "",
            f"- H1 (reasoning deficit): {deg['what_this_can_and_cannot_separate']['H1 reasoning deficit']}",
            f"- H2 (constraint persistence under context): "
            f"{deg['what_this_can_and_cannot_separate']['H2 constraint persistence under context']}"]

    g = s["decision_gate"]
    out += ["", "## Decision gate", "",
            f"- compact {g['compact_success_rate']}, medium {g['medium_success_rate']}, "
            f"dense {g['dense_success_rate']}",
            f"- candidate levels in the 20-80% band: "
            f"{g['candidate_levels_in_20_80_band']}",
            f"- cases matched: {g['cases_matched']}",
            f"- first match in my test order: **{g['case']}** "
            f"({g['case_selected_by']})",
            f"- **outcome: {g['outcome']}**",]
    if g.get("case_1_rationale_note"):
        out += [f"- NOTE: {g['case_1_rationale_note']}"]
    out += [
            f"- **recommendation: {g['recommendation']}**",
            f"- treatment executed: {g['treatment_executed']}; "
            f"max executed: {g['max_executed']}", f"- {g['note']}"]
    return out


if __name__ == "__main__":
    raise SystemExit(main())
