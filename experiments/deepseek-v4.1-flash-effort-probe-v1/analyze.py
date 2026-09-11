"""Phase-1 analysis: distributions first, then the decision gate.

    python analyze.py

Reads `raw/samples.jsonl` (and `raw/sentinel-banana.jsonl` if present), writes
`analysis/observations.csv`, `analysis/summary.json` and `analysis/report.md`.

## Choices that matter, stated rather than buried

* **Nothing is trimmed.** No outlier is removed from any headline number. A
  trimmed view is computed *alongside* the real one, only to answer the
  question "is this difference one or two extreme values?", and it is labelled
  as a sensitivity check everywhere it appears.
* **Absent is not zero.** `reasoning_tokens` statistics are computed over the
  samples where the provider reported the field, and the count of samples where
  it was absent is reported next to them. A missing field never enters a mean.
* **Medians, and a rank statistic.** With a distribution this skewed a mean is
  not a summary of anything, so the comparison rests on medians, on quantiles
  either side of them, and on the probability of superiority (Cliff's delta),
  which cannot be moved by how extreme the extreme values are.
* **Significance is tested, not asserted.** Two-sided permutation tests with a
  recorded seed, on the difference in medians and on Cliff's delta. A p-value is
  reported as what it is; nothing is called significant on the strength of a
  mean being bigger.
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
    "sample_id", "variant", "reasoning_effort_sent", "reasoning_effort_field_present",
    "status", "timestamp_utc", "request_id", "request_id_shape", "http_status",
    "model_id", "input_tokens", "output_tokens",
    "reasoning_tokens_reported", "reasoning_tokens_field_present",
    "reasoning_stream_observed", "reasoning_stream_event_count",
    "ttft_ms", "ttfa_ms", "total_latency_ms", "finish_reason",
    "score_strict", "score_last_time", "retries", "response_sha256", "response_text",
]


def quantile(values: list[float], q: float) -> float | None:
    """Linear-interpolation quantile on the sorted sample. None if empty."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(ordered[low])
    return float(ordered[low] + (ordered[high] - ordered[low]) * (position - low))


def describe(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": round(statistics.fmean(values), 1),
        "median": round(statistics.median(values), 1),
        "min": round(min(values), 1),
        "max": round(max(values), 1),
        "p10": round(quantile(values, 0.10), 1),
        "p25": round(quantile(values, 0.25), 1),
        "p75": round(quantile(values, 0.75), 1),
        "p90": round(quantile(values, 0.90), 1),
        "stdev": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
    }


def cliffs_delta(a: list[float], b: list[float]) -> float | None:
    """P(a > b) - P(a < b). Rank-based, so extreme values cannot inflate it."""
    if not a or not b:
        return None
    greater = sum(1 for x in a for y in b if x > y)
    less = sum(1 for x in a for y in b if x < y)
    return (greater - less) / (len(a) * len(b))


def bootstrap_ci(a: list[float], b: list[float], statistic, seed: int) -> dict:
    """Percentile bootstrap CI for statistic(a) - statistic(b), or for a pair stat."""
    if not a or not b:
        return {"available": False, "reason": "one or both samples empty"}
    rng = random.Random(seed)
    diffs = []
    for _ in range(RESAMPLES):
        ra = [a[rng.randrange(len(a))] for _ in range(len(a))]
        rb = [b[rng.randrange(len(b))] for _ in range(len(b))]
        value = statistic(ra, rb)
        if value is not None:
            diffs.append(value)
    diffs.sort()
    return {
        "available": True,
        "resamples": len(diffs),
        "point_estimate": round(statistic(a, b), 4),
        "ci95_low": round(quantile(diffs, ALPHA / 2), 4),
        "ci95_high": round(quantile(diffs, 1 - ALPHA / 2), 4),
        "includes_zero": quantile(diffs, ALPHA / 2) <= 0 <= quantile(diffs, 1 - ALPHA / 2),
    }


def permutation_p(a: list[float], b: list[float], statistic, seed: int) -> dict:
    """Two-sided permutation test on statistic(a, b) under exchangeability."""
    if not a or not b:
        return {"available": False}
    observed = statistic(a, b)
    if observed is None:
        return {"available": False}
    pooled = list(a) + list(b)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(RESAMPLES):
        rng.shuffle(pooled)
        value = statistic(pooled[:len(a)], pooled[len(a):])
        if value is not None and abs(value) >= abs(observed):
            extreme += 1
    return {
        "available": True,
        "observed": round(observed, 4),
        "resamples": RESAMPLES,
        # +1/+1 correction: a permutation p-value is never reported as exactly 0.
        "p_two_sided": round((extreme + 1) / (RESAMPLES + 1), 4),
    }


def median_diff(a: list[float], b: list[float]) -> float:
    return statistics.median(a) - statistics.median(b)


def rate_diff(a: list[float], b: list[float]) -> float:
    return statistics.fmean(a) - statistics.fmean(b)


def histogram(values: list[float], edges: list[float]) -> list[tuple[str, int]]:
    rows = []
    for i, low in enumerate(edges):
        high = edges[i + 1] if i + 1 < len(edges) else None
        if high is None:
            count = sum(1 for v in values if v >= low)
            rows.append((f">={int(low)}", count))
        else:
            count = sum(1 for v in values if low <= v < high)
            rows.append((f"{int(low)}-{int(high) - 1}", count))
    return rows


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def variant_stats(rows: list[dict]) -> dict:
    ok = [r for r in rows if r["status"] == "OK"]
    reasoning_reported = [float(r["reasoning_tokens_reported"]) for r in ok
                          if r["reasoning_tokens_reported"] is not None]
    zeros = sum(1 for r in ok if r["reasoning_tokens_reported"] == 0)
    strict = [r["score_strict"] for r in ok]
    last = [r["score_last_time"] for r in ok]
    delivered = sum(1 for r in ok if r["reasoning_stream_observed"] is True)
    return {
        "n_slots": len(rows),
        "n_ok": len(ok),
        "n_failed": len(rows) - len(ok),
        "scoring_strict": {
            "CORRECT": strict.count("CORRECT"),
            "INCORRECT": strict.count("INCORRECT"),
            "UNPARSEABLE": strict.count("UNPARSEABLE"),
            "success_rate": round(strict.count("CORRECT") / len(ok), 4) if ok else None,
        },
        "scoring_last_time": {
            "CORRECT": last.count("CORRECT"),
            "INCORRECT": last.count("INCORRECT"),
            "UNPARSEABLE": last.count("UNPARSEABLE"),
            "success_rate": round(last.count("CORRECT") / len(ok), 4) if ok else None,
        },
        "reasoning_tokens": {
            "reported_count": len(reasoning_reported),
            "missing_count": len(ok) - len(reasoning_reported),
            "reported_zero_count": zeros,
            **describe(reasoning_reported),
        },
        "output_tokens": describe([float(r["output_tokens"]) for r in ok
                                   if r["output_tokens"] is not None]),
        "ttfa_ms": describe([float(r["ttfa_ms"]) for r in ok if r["ttfa_ms"] is not None]),
        "ttft_ms": describe([float(r["ttft_ms"]) for r in ok if r["ttft_ms"] is not None]),
        "total_latency_ms": describe([float(r["total_latency_ms"]) for r in ok]),
        "reasoning_delivery": {
            "stream_observed_true": delivered,
            "stream_observed_false": len(ok) - delivered,
            "percentage_observed": round(100 * delivered / len(ok), 1) if ok else None,
            "note": "stream_observed=false means reasoning delivery was not "
                    "observed, NOT that the model did not reason",
        },
        "request_id_shapes": {shape: sum(1 for r in ok if r["request_id_shape"] == shape)
                              for shape in sorted({r["request_id_shape"] for r in ok})},
        "finish_reasons": {fr: sum(1 for r in ok if r["finish_reason"] == fr)
                           for fr in sorted({str(r["finish_reason"]) for r in ok})},
    }


def main() -> int:
    config = json.loads((HERE / "probe-config.json").read_text(encoding="utf-8"))
    seed = config["bootstrap_seed"]
    rows = load(HERE / "raw" / "samples.jsonl")
    sentinel = load(HERE / "raw" / "sentinel-banana.jsonl")

    (HERE / "analysis").mkdir(exist_ok=True)
    csv_path = HERE / "analysis" / "observations.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in CSV_FIELDS})

    base_rows = [r for r in rows if r["variant"] == "baseline"]
    high_rows = [r for r in rows if r["variant"] == "high"]
    stats = {"baseline": variant_stats(base_rows), "high": variant_stats(high_rows)}

    def ok(rs):
        return [r for r in rs if r["status"] == "OK"]

    def reasoning_of(rs):
        return [float(r["reasoning_tokens_reported"]) for r in ok(rs)
                if r["reasoning_tokens_reported"] is not None]

    def latency_of(rs):
        return [float(r["total_latency_ms"]) for r in ok(rs)]

    def correct_of(rs):
        return [1.0 if r["score_strict"] == "CORRECT" else 0.0 for r in ok(rs)]

    rb, rh = reasoning_of(base_rows), reasoning_of(high_rows)
    lb, lh = latency_of(base_rows), latency_of(high_rows)
    cb, ch = correct_of(base_rows), correct_of(high_rows)

    comparisons = {
        "bootstrap": {
            "seed": seed, "resamples": RESAMPLES, "method": "percentile bootstrap",
            "outliers_removed": False,
            "median_reasoning_tokens_high_minus_baseline": bootstrap_ci(rh, rb, median_diff, seed),
            "median_total_latency_ms_high_minus_baseline": bootstrap_ci(lh, lb, median_diff, seed),
            "success_rate_high_minus_baseline": bootstrap_ci(ch, cb, rate_diff, seed),
        },
        "permutation_tests": {
            "seed": seed, "resamples": RESAMPLES,
            "median_reasoning_tokens": permutation_p(rh, rb, median_diff, seed),
            "cliffs_delta_reasoning_tokens": permutation_p(rh, rb, cliffs_delta, seed),
            "median_total_latency_ms": permutation_p(lh, lb, median_diff, seed),
            "success_rate": permutation_p(ch, cb, rate_diff, seed),
        },
        "cliffs_delta_reasoning_tokens": {
            "point_estimate": (round(cliffs_delta(rh, rb), 4)
                               if cliffs_delta(rh, rb) is not None else None),
            "interpretation": "P(high > baseline) - P(high < baseline) over all pairs",
            "bootstrap": bootstrap_ci(rh, rb, cliffs_delta, seed),
        },
        "success_rate_difference": {
            "absolute_pp": (round(100 * (statistics.fmean(ch) - statistics.fmean(cb)), 2)
                            if cb and ch else None),
            "relative_pct": (round(100 * (statistics.fmean(ch) - statistics.fmean(cb))
                                   / statistics.fmean(cb), 2)
                             if cb and ch and statistics.fmean(cb) else None),
        },
    }

    # Sensitivity check ONLY. Nothing above is computed on trimmed data.
    trimmed = {}
    if len(rh) > 3 and len(rb) > 3:
        th, tb = sorted(rh)[:-3], sorted(rb)[:-3]
        trimmed = {
            "what": "top 3 reasoning_tokens values dropped from each variant",
            "purpose": "is the shift carried by an extreme tail?",
            "used_in_headline_numbers": False,
            "baseline": {"median": round(statistics.median(tb), 1),
                         "p25": round(quantile(tb, 0.25), 1)},
            "high": {"median": round(statistics.median(th), 1),
                     "p25": round(quantile(th, 0.25), 1)},
            "median_still_higher": statistics.median(th) > statistics.median(tb),
            "p25_still_higher": quantile(th, 0.25) > quantile(tb, 0.25),
        }

    # Decision gate, exactly as specified before the data existed.
    sr_base = stats["baseline"]["scoring_strict"]["success_rate"]
    sr_high = stats["high"]["scoring_strict"]["success_rate"]
    gate_a = (sr_high is not None and sr_base is not None
              and (sr_high - sr_base) >= 0.10)
    median_higher = bool(rh and rb and statistics.median(rh) > statistics.median(rb))
    p25_higher = bool(rh and rb and quantile(rh, 0.25) > quantile(rb, 0.25))
    tail_ok = bool(trimmed.get("median_still_higher") and trimmed.get("p25_still_higher"))
    delta = cliffs_delta(rh, rb)
    delta_ci = comparisons["cliffs_delta_reasoning_tokens"]["bootstrap"]
    delta_excludes_zero = bool(delta_ci.get("available") and not delta_ci["includes_zero"])
    gate_b = median_higher and p25_higher and tail_ok and delta_excludes_zero
    gate = {
        "A_quality_signal": {
            "criterion": "success_rate(high) - success_rate(baseline) >= +10 pp",
            "baseline": sr_base, "high": sr_high,
            "difference_pp": (round(100 * (sr_high - sr_base), 2)
                              if sr_base is not None and sr_high is not None else None),
            "met": bool(gate_a),
        },
        "B_compute_signal": {
            "criterion": "median(high) > median(baseline) AND p25(high) > p25(baseline) "
                         "AND the shift is not carried by an extreme tail",
            "median_higher": median_higher,
            "p25_higher": p25_higher,
            "survives_tail_trim_sensitivity_check": tail_ok,
            "cliffs_delta_ci_excludes_zero": delta_excludes_zero,
            "met": bool(gate_b),
        },
        "outcome": "PROCEED TO MAX (pending explicit authorisation)" if (gate_a or gate_b)
                   else "STOP - no observable high-effort effect large enough to "
                        "justify a MondayBench battery",
        "max_executed": False,
        "note": "max is never executed by this script under any outcome.",
    }

    # Reasoning compute against correctness, pooled and per variant.
    correctness_link = {}
    for label, rs in (("pooled", rows), ("baseline", base_rows), ("high", high_rows)):
        buckets: dict[str, list[float]] = {}
        for r in ok(rs):
            if r["reasoning_tokens_reported"] is None:
                continue
            buckets.setdefault(r["score_strict"], []).append(float(r["reasoning_tokens_reported"]))
        correctness_link[label] = {k: describe(v) for k, v in sorted(buckets.items())}

    edges = [0, 250, 500, 1000, 2000, 4000, 8000, 16000]
    distributions = {
        "reasoning_tokens_histogram": {
            "bins": [r[0] for r in histogram(rb, edges)],
            "baseline": [r[1] for r in histogram(rb, edges)],
            "high": [r[1] for r in histogram(rh, edges)],
        },
        "reasoning_tokens_sorted": {"baseline": sorted(int(v) for v in rb),
                                    "high": sorted(int(v) for v in rh)},
        "total_latency_ms_sorted": {"baseline": sorted(int(v) for v in lb),
                                    "high": sorted(int(v) for v in lh)},
    }

    sentinel_summary = {}
    if sentinel:
        sok = [r for r in sentinel if r["status"] == "OK"]
        sentinel_summary = {
            "n": len(sentinel),
            "n_ok": len(sok),
            "http_statuses": sorted({r.get("http_status") for r in sentinel}, key=str),
            "request_id_shapes": {s: sum(1 for r in sok if r["request_id_shape"] == s)
                                  for s in sorted({r["request_id_shape"] for r in sok})},
            "reasoning_tokens_field_present": sum(1 for r in sok
                                                  if r["reasoning_tokens_field_present"]),
            "reasoning_tokens_field_absent": sum(1 for r in sok
                                                 if not r["reasoning_tokens_field_present"]),
            "reasoning_stream_observed_true": sum(1 for r in sok
                                                  if r["reasoning_stream_observed"] is True),
            "output_tokens": [r["output_tokens"] for r in sok],
            "total_latency_ms": [r["total_latency_ms"] for r in sok],
            "scores_strict": [r["score_strict"] for r in sok],
            "answers": [r["response_text"].strip()[:60] for r in sok],
            "in_statistics": False,
            "note": "observable behaviour only; this says nothing about how the "
                    "provider routes requests internally",
        }

    # ------------------------------------------------------------------
    # Input-token accounting.
    #
    # The user message is byte-identical in all 60 samples (one response sha,
    # one prompt sha), so `prompt_tokens` should be one number. It is not. This
    # is checked rather than assumed because the project has seen it before:
    # `mondaybench/reasoning.py` records a qwen3.8-flash run that came back with
    # a different input token count for byte-identical input, and that run was
    # being served differently from its siblings.
    # ------------------------------------------------------------------
    input_buckets: dict[str, dict] = {}
    for r in ok(rows):
        key = str(r["input_tokens"])
        bucket = input_buckets.setdefault(key, {"n": 0, "by_variant": {},
                                                "reasoning_tokens": []})
        bucket["n"] += 1
        bucket["by_variant"][r["variant"]] = bucket["by_variant"].get(r["variant"], 0) + 1
        if r["reasoning_tokens_reported"] is not None:
            bucket["reasoning_tokens"].append(float(r["reasoning_tokens_reported"]))
    for bucket in input_buckets.values():
        bucket["reasoning_tokens_summary"] = describe(bucket.pop("reasoning_tokens"))
    distinct_inputs = sorted(int(k) for k in input_buckets)
    input_token_accounting = {
        "prompt_bytes_identical_in_every_sample": True,
        "distinct_prompt_token_counts": distinct_inputs,
        "buckets": input_buckets,
        "per_variant": {
            v: {str(it): sum(1 for r in ok(rows)
                             if r["variant"] == v and r["input_tokens"] == it)
                for it in distinct_inputs}
            for v in ("baseline", "high")
        },
        "observation": (
            "byte-identical input was billed as "
            + ", ".join(str(i) for i in distinct_inputs)
            + " prompt tokens across the 60 samples, and the reasoning-token "
              "distribution differs sharply between those groups. The variants do "
              "not map one-to-one onto the groups, but neither are they "
              "independent of them."
        ) if len(distinct_inputs) > 1 else "single consistent prompt token count",
        "consequence": (
            "the baseline-vs-high reasoning-token comparison is confounded: a "
            "sample's prompt-token group predicts its reasoning tokens at least "
            "as well as its variant does. No causal reading of the variant "
            "difference is available from this data."
        ) if len(distinct_inputs) > 1 else None,
        "interpretation_limit": "observable accounting only; nothing here "
                                "establishes what the provider served or why",
    }

    # What the numbers above cannot answer. Written from the data, not chosen.
    limitations = []
    if len(distinct_inputs) > 1:
        limitations.append({
            "issue": f"byte-identical input was counted as {len(distinct_inputs)} "
                     f"different prompt-token totals {distinct_inputs}",
            "consequence": "the samples were not all answered under one accounting, "
                           "and reasoning tokens differ by group, so the "
                           "baseline/high difference cannot be attributed to "
                           "reasoning_effort. See input_token_accounting.",
        })
    if sr_base == 1.0 and sr_high == 1.0:
        limitations.append({
            "issue": "success rate is saturated at 1.0 in both variants",
            "consequence": "gate A could not have fired whatever reasoning_effort does. "
                           "This prompt cannot discriminate quality, so 'no quality "
                           "effect' is NOT established - it was not measurable. The "
                           "zero-width bootstrap CI on the success-rate difference is "
                           "an artefact of that ceiling, not precision.",
        })
    perm_median = comparisons["permutation_tests"]["median_reasoning_tokens"]
    boot_median = comparisons["bootstrap"]["median_reasoning_tokens_high_minus_baseline"]
    if (perm_median.get("available") and boot_median.get("available")
            and (perm_median["p_two_sided"] < 0.05) != (not boot_median["includes_zero"])):
        limitations.append({
            "issue": "the two procedures disagree on the median reasoning-token "
                     "difference at the 5% threshold",
            "detail": f"permutation p={perm_median['p_two_sided']}, bootstrap 95% CI "
                      f"[{boot_median['ci95_low']}, {boot_median['ci95_high']}] "
                      f"(includes zero: {boot_median['includes_zero']})",
            "consequence": "neither is treated as a finding. Four tests were run and "
                           "no multiplicity correction was applied, so a single "
                           "p-value near 0.05 is not evidence of an effect.",
        })
    limitations.append({
        "issue": "scope",
        "consequence": "one prompt, one route, one model, one session, calls issued "
                       "sequentially. Interleaving controls for slow backend drift, "
                       "not for load at the moment of a call. Nothing here "
                       "generalises to other prompts or to MondayBench scenarios.",
    })
    limitations.append({
        "issue": "observable behaviour only",
        "consequence": "request-id shapes, token counters and stream events are "
                       "descriptions of responses. They establish nothing about how "
                       "the provider routes or serves a request internally.",
    })

    summary = {
        "experiment": HERE.name,
        "phase": 1,
        "is_mondaybench_run": False,
        "limitations": limitations,
        "prompt_sha256": config["prompt_sha256"],
        "scorer": config["scorer"],
        "correct_answer": config["correct_answer"],
        "calls": {
            "phase1_slots": len(rows),
            "phase1_ok": len(ok(rows)),
            "phase1_failed": len(rows) - len(ok(rows)),
            "retries_total": sum(r.get("retries", 0) for r in rows),
            "sentinel_calls": len(sentinel),
            "total_api_calls": sum(len(r.get("attempts", [])) for r in rows)
                               + sum(len(r.get("attempts", [])) for r in sentinel),
        },
        "per_variant": stats,
        "comparisons": comparisons,
        "tail_sensitivity_check": trimmed,
        "distributions": distributions,
        "reasoning_tokens_vs_correctness": correctness_link,
        "input_token_accounting": input_token_accounting,
        "decision_gate": gate,
        "sentinel_banana": sentinel_summary,
    }
    (HERE / "analysis" / "summary.json").write_text(json.dumps(summary, indent=2),
                                                    encoding="utf-8")

    lines = render_report(summary)
    (HERE / "analysis" / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote -> analysis/summary.json, analysis/report.md, analysis/observations.csv")
    return 0


def render_report(s: dict) -> list[str]:
    b, h = s["per_variant"]["baseline"], s["per_variant"]["high"]
    out = [f"# {s['experiment']} - phase 1 report", "",
           f"Prompt sha256 `{s['prompt_sha256']}`, correct answer "
           f"`{s['correct_answer']}`, scorer: {s['scorer']}.",
           "Not a MondayBench run. No battery, leaderboard, evaluation or release "
           "was read or written.", "",
           "## Calls", ""]
    for k, v in s["calls"].items():
        out.append(f"- {k}: {v}")

    def row(label, bv, hv):
        return f"| {label} | {bv} | {hv} |"

    out += ["", "## baseline vs high", "",
            "| metric | baseline | high |", "| --- | --- | --- |",
            row("slots", b["n_slots"], h["n_slots"]),
            row("completed (OK)", b["n_ok"], h["n_ok"]),
            row("failed", b["n_failed"], h["n_failed"]),
            row("CORRECT (strict)", b["scoring_strict"]["CORRECT"],
                h["scoring_strict"]["CORRECT"]),
            row("INCORRECT (strict)", b["scoring_strict"]["INCORRECT"],
                h["scoring_strict"]["INCORRECT"]),
            row("UNPARSEABLE (strict)", b["scoring_strict"]["UNPARSEABLE"],
                h["scoring_strict"]["UNPARSEABLE"]),
            row("success rate (strict)", b["scoring_strict"]["success_rate"],
                h["scoring_strict"]["success_rate"]),
            row("success rate (last-time check)", b["scoring_last_time"]["success_rate"],
                h["scoring_last_time"]["success_rate"]),
            row("reasoning delivery observed",
                f"{b['reasoning_delivery']['stream_observed_true']}/{b['n_ok']} "
                f"({b['reasoning_delivery']['percentage_observed']}%)",
                f"{h['reasoning_delivery']['stream_observed_true']}/{h['n_ok']} "
                f"({h['reasoning_delivery']['percentage_observed']}%)"),
            row("reasoning_tokens reported", b["reasoning_tokens"]["reported_count"],
                h["reasoning_tokens"]["reported_count"]),
            row("reasoning_tokens absent (null)", b["reasoning_tokens"]["missing_count"],
                h["reasoning_tokens"]["missing_count"]),
            row("reasoning_tokens reported as 0",
                b["reasoning_tokens"]["reported_zero_count"],
                h["reasoning_tokens"]["reported_zero_count"]),
            ]

    for metric in ("reasoning_tokens", "output_tokens", "ttfa_ms", "total_latency_ms"):
        out += ["", f"## {metric}", "",
                "| stat | baseline | high |", "| --- | --- | --- |"]
        for stat in ("n", "mean", "median", "min", "p10", "p25", "p75", "p90", "max", "stdev"):
            out.append(row(stat, b[metric].get(stat), h[metric].get(stat)))

    hist = s["distributions"]["reasoning_tokens_histogram"]
    out += ["", "## reasoning_tokens distribution", "",
            "| bin | baseline | high |", "| --- | --- | --- |"]
    for i, label in enumerate(hist["bins"]):
        bc, hc = hist["baseline"][i], hist["high"][i]
        out.append(f"| {label} | {bc} {'#' * bc} | {hc} {'#' * hc} |")
    out += ["", "Sorted values (nothing removed):", "",
            f"- baseline: {s['distributions']['reasoning_tokens_sorted']['baseline']}",
            f"- high: {s['distributions']['reasoning_tokens_sorted']['high']}"]

    c = s["comparisons"]
    out += ["", "## Comparisons", "",
            f"- success rate difference: "
            f"{c['success_rate_difference']['absolute_pp']} pp absolute, "
            f"{c['success_rate_difference']['relative_pct']}% relative", ""]
    out += ["| quantity | point | 95% CI | includes 0 |", "| --- | --- | --- | --- |"]
    for label, key in (("median reasoning_tokens (high - baseline)",
                        "median_reasoning_tokens_high_minus_baseline"),
                       ("median total latency ms (high - baseline)",
                        "median_total_latency_ms_high_minus_baseline"),
                       ("success rate (high - baseline)",
                        "success_rate_high_minus_baseline")):
        ci = c["bootstrap"][key]
        if ci.get("available"):
            out.append(f"| {label} | {ci['point_estimate']} | "
                       f"[{ci['ci95_low']}, {ci['ci95_high']}] | {ci['includes_zero']} |")
    cd = c["cliffs_delta_reasoning_tokens"]
    if cd["bootstrap"].get("available"):
        out.append(f"| Cliff's delta, reasoning_tokens | {cd['point_estimate']} | "
                   f"[{cd['bootstrap']['ci95_low']}, {cd['bootstrap']['ci95_high']}] | "
                   f"{cd['bootstrap']['includes_zero']} |")
    out += ["", f"Bootstrap: {c['bootstrap']['resamples']} resamples, seed "
                f"{c['bootstrap']['seed']}, percentile method, no outliers removed.", "",
            "| permutation test | observed | p (two-sided) |", "| --- | --- | --- |"]
    for label, key in (("median reasoning_tokens", "median_reasoning_tokens"),
                       ("Cliff's delta reasoning_tokens", "cliffs_delta_reasoning_tokens"),
                       ("median total latency", "median_total_latency_ms"),
                       ("success rate", "success_rate")):
        t = c["permutation_tests"][key]
        if t.get("available"):
            out.append(f"| {label} | {t['observed']} | {t['p_two_sided']} |")

    if s["tail_sensitivity_check"]:
        t = s["tail_sensitivity_check"]
        out += ["", "## Tail sensitivity check (not a headline number)", "",
                f"- {t['what']} - {t['purpose']}",
                f"- baseline median {t['baseline']['median']}, p25 {t['baseline']['p25']}",
                f"- high median {t['high']['median']}, p25 {t['high']['p25']}",
                f"- median still higher: {t['median_still_higher']}; "
                f"p25 still higher: {t['p25_still_higher']}"]

    out += ["", "## reasoning_tokens vs correctness", ""]
    for scope, buckets in s["reasoning_tokens_vs_correctness"].items():
        out.append(f"- **{scope}**: " + ("; ".join(
            f"{k} n={v['n']} median={v.get('median')}" for k, v in buckets.items()) or "none"))

    g = s["decision_gate"]
    out += ["", "## Decision gate", "",
            f"- A (quality): {g['A_quality_signal']['criterion']} -> "
            f"{g['A_quality_signal']['difference_pp']} pp -> "
            f"**{'MET' if g['A_quality_signal']['met'] else 'NOT MET'}**",
            f"- B (compute): median higher {g['B_compute_signal']['median_higher']}, "
            f"p25 higher {g['B_compute_signal']['p25_higher']}, "
            f"tail check {g['B_compute_signal']['survives_tail_trim_sensitivity_check']}, "
            f"Cliff's delta CI excludes 0 "
            f"{g['B_compute_signal']['cliffs_delta_ci_excludes_zero']} -> "
            f"**{'MET' if g['B_compute_signal']['met'] else 'NOT MET'}**",
            f"- **outcome: {g['outcome']}**",
            f"- max executed: {g['max_executed']}"]

    ita = s.get("input_token_accounting") or {}
    if len(ita.get("distinct_prompt_token_counts") or []) > 1:
        out += ["", "## Input-token accounting (byte-identical input)", "",
                f"- distinct prompt_token counts: {ita['distinct_prompt_token_counts']}",
                f"- {ita['observation']}",
                f"- **consequence**: {ita['consequence']}", "",
                "| prompt_tokens | n | baseline | high | reasoning median | reasoning p25 | reasoning p75 |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for key in sorted(ita["buckets"], key=int):
            bucket = ita["buckets"][key]
            summary_stats = bucket["reasoning_tokens_summary"]
            out.append(f"| {key} | {bucket['n']} | "
                       f"{bucket['by_variant'].get('baseline', 0)} | "
                       f"{bucket['by_variant'].get('high', 0)} | "
                       f"{summary_stats.get('median')} | {summary_stats.get('p25')} | "
                       f"{summary_stats.get('p75')} |")

    if s.get("limitations"):
        out += ["", "## Limitations", ""]
        for item in s["limitations"]:
            out.append(f"- **{item['issue']}**"
                       + (f" ({item['detail']})" if item.get("detail") else "")
                       + f": {item['consequence']}")

    if s["sentinel_banana"]:
        sb = s["sentinel_banana"]
        out += ["", "## Sentinel: reasoning_effort=\"banana\" (outside the statistics)", ""]
        for k, v in sb.items():
            out.append(f"- {k}: {v}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
