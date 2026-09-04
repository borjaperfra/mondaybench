"""Build the GLM 5.3 audit summaries from what is already on disk.

Reads the run files, the stored evaluations and the pricing probes, and writes
run-summary.json, score-summary.json and pricing-summary.json. Recomputes every
score from the atomic criterion verdicts rather than copying a total, so the
audit's arithmetic is independent of the leaderboard's.
"""
from __future__ import annotations
import json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent

SLUG = "glm5.3"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}

# Measured from gateway cost_details, 2026-09-03. See pricing-probes.json and
# routing-probes.json in this directory.
RATE_IN_PER_M = 0.075
RATE_OUT_PER_M = 0.25
ALT_RATE_IN_PER_M = 0.15
ALT_RATE_OUT_PER_M = 0.50


def load_runs():
    rows = []
    for sid in SCENARIOS:
        d = ROOT / "runs" / sid / SLUG
        for p in sorted(d.glob("run-*.json")):
            r = json.loads(p.read_text(encoding="utf-8"))
            perf = r.get("performance") or {}
            usage = r.get("usage") or {}
            reasoning = r.get("reasoning") or {}
            gen = r.get("generation") or {}
            rows.append({
                "scenario": sid,
                "run_id": r["run_id"],
                "run_number": r["run_number"],
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "requested_model": (r.get("model") or {}).get("model_id"),
                "provider": (r.get("model") or {}).get("provider"),
                "prompt_sha256": r.get("scenario_prompt_sha256"),
                "system_prompt_sha256": gen.get("system_prompt_sha256"),
                "config_sha256": gen.get("config_sha256"),
                "temperature": gen.get("temperature"),
                "top_p": gen.get("top_p"),
                "safety_ceiling_tokens": gen.get("safety_ceiling_tokens") or gen.get("max_output_tokens"),
                "unsupported_parameters": gen.get("unsupported_parameters") or [],
                "finish_reason": r.get("finish_reason"),
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "reasoning_tokens": usage.get("reasoning_tokens"),
                "cache_read_tokens": usage.get("cache_read_tokens"),
                "cache_write_tokens": usage.get("cache_write_tokens"),
                "reasoning_status": reasoning.get("status"),
                "reasoning_evidence": reasoning.get("evidence"),
                "ttft_ms": perf.get("ttft_ms"),
                "ttfa_ms": perf.get("ttfa_ms"),
                "total_latency_ms": perf.get("total_latency_ms"),
                "response_sha256": __import__("hashlib").sha256((r.get("response") or "").encode("utf-8")).hexdigest(),
                "response_chars": len(r.get("response") or ""),
            })
    return rows


def load_evaluations():
    """Every stored evaluation for this model, keyed by scenario and run."""
    out = {}
    for sid in SCENARIOS:
        ev = EVALUATORS[sid]
        base = ROOT / "evaluations" / ev / sid / SLUG
        if not base.exists():
            continue
        for p in sorted(base.glob("run-*.json")):
            e = json.loads(p.read_text(encoding="utf-8"))
            out.setdefault(sid, []).append(e)
    return out


def main() -> None:
    runs = load_runs()
    (HERE / "run-summary.json").write_text(json.dumps({
        "model_slug": SLUG,
        "runs": len(runs),
        "distinct_response_hashes": len({r["response_sha256"] for r in runs if r["response_sha256"]}),
        "finish_reasons": sorted({r["finish_reason"] for r in runs}),
        "reasoning_states": sorted({r["reasoning_status"] for r in runs}),
        "unsupported_parameters": sorted({p for r in runs for p in r["unsupported_parameters"]}),
        "rows": runs,
    }, indent=2) + "\n", encoding="utf-8")

    evals = load_evaluations()
    scen = {}
    for sid in SCENARIOS:
        rows = evals.get(sid) or []
        if not rows:
            continue
        per_run = []
        for e in rows:
            # Recomputed from the atomic verdicts, not read off `final_score`.
            crit = e["criteria"]
            earned = sum(c["points_awarded"] for c in crit.values())
            dims = e["dimensions"]
            noise = dims.get("noise_resistance", {}).get("score")
            base = round(earned + (noise or 0), 2)
            pen = e["penalties"]["total"]
            per_run.append({
                "run_id": e["run_id"],
                "criteria_points": round(earned, 2),
                "noise_points": noise,
                "penalties": pen,
                "recomputed_final": round(max(0.0, base + pen), 2),
                "stored_final": e["final_score"],
                "matches": abs(round(max(0.0, base + pen), 2) - e["final_score"]) < 0.005,
                "labels": {k: v["result"] for k, v in crit.items()},
            })
        finals = [r["recomputed_final"] for r in per_run]
        scen[sid] = {
            "evaluator": EVALUATORS[sid],
            "runs": per_run,
            "mean": round(sum(finals) / len(finals), 2),
            "stdev": round(statistics.stdev(finals), 2) if len(finals) > 1 else 0.0,
            "min": min(finals),
            "max": max(finals),
            "range": round(max(finals) - min(finals), 2),
        }

    overall = None
    if len(scen) == 5:
        means = [scen[s]["mean"] for s in SCENARIOS]
        overall = round(sum(means) / 5, 2)

    worst = min(scen, key=lambda s: scen[s]["mean"]) if scen else None
    best = max(scen, key=lambda s: scen[s]["mean"]) if scen else None
    (HERE / "score-summary.json").write_text(json.dumps({
        "model_slug": SLUG,
        "aggregation": "equal-weight mean of the five scenario means; NOT weighted by criterion count",
        "scenarios": scen,
        "overall_monday_score": overall,
        "worst_monday": worst,
        "best_monday": best,
        "scenario_spread": round(max(s["mean"] for s in scen.values()) - min(s["mean"] for s in scen.values()), 2) if scen else None,
        "spread_note": "Scenario spread is variation across DIFFERENT tasks. It is not an estimate of judge noise and must not be read as one.",
    }, indent=2) + "\n", encoding="utf-8")

    # ---- pricing -----------------------------------------------------------
    tin = sum(r["input_tokens"] or 0 for r in runs)
    tout = sum(r["output_tokens"] or 0 for r in runs)
    treason = sum(r["reasoning_tokens"] or 0 for r in runs)
    n = len(runs)
    cost_task = (tin / n * RATE_IN_PER_M + tout / n * RATE_OUT_PER_M) / 1e6 if n else None
    alt_task = (tin / n * ALT_RATE_IN_PER_M + tout / n * ALT_RATE_OUT_PER_M) / 1e6 if n else None
    lat = [r["total_latency_ms"] for r in runs if r["total_latency_ms"]]
    ttft = [r["ttft_ms"] for r in runs if r["ttft_ms"]]
    ttfa = [r["ttfa_ms"] for r in runs if r["ttfa_ms"]]
    (HERE / "pricing-summary.json").write_text(json.dumps({
        "model_slug": SLUG,
        "basis": "measured from Helmcode gateway usage.cost_details on non-streaming completions, 2026-09-03",
        "first_party_verifiable": True,
        "observed_rates_usd_per_million": {
            "Z.AI upstream": {"input": RATE_IN_PER_M, "output": RATE_OUT_PER_M,
                              "observations": 6, "note": "every probe at benchmark prompt size routed here"},
            "Parasail upstream": {"input": ALT_RATE_IN_PER_M, "output": ALT_RATE_OUT_PER_M,
                                  "observations": 1, "note": "one long-prompt call; same served model id"},
            "repeat-prompt input": {"input": 0.016063,
                                    "note": "effective input rate on an immediately repeated prompt, despite extra_body caching:false"},
        },
        "per_run_cost_observable": False,
        "per_run_cost_note": "The STREAMING response the runner uses carries neither `provider` nor `cost`; both appear only on non-streaming calls. Per-run cost is therefore derived from measured rates and recorded token counts, not read from the run files.",
        "tokens": {
            "runs": n,
            "total_input": tin, "total_output": tout, "total_reasoning": treason,
            "mean_input": round(tin / n, 1) if n else None,
            "mean_output": round(tout / n, 1) if n else None,
            "mean_reasoning": round(treason / n, 1) if n else None,
            "reasoning_double_count_note": "reasoning_tokens are INSIDE output_tokens (completion_tokens). They are not added again.",
            "cache_read_tokens": sum(r["cache_read_tokens"] or 0 for r in runs),
            "cache_write_tokens": sum(r["cache_write_tokens"] or 0 for r in runs),
        },
        "normalized_cost_usd": None if cost_task is None else {
            "per_task": round(cost_task, 6),
            "per_1k_tasks": round(cost_task * 1_000, 2),
            "per_100k_tasks": round(cost_task * 100_000, 2),
            "per_1m_tasks": round(cost_task * 1_000_000, 2),
            "upper_bound_per_task_parasail_rate": round(alt_task, 6),
            "upper_bound_per_1k_tasks": round(alt_task * 1_000, 2),
            "basis_note": "one completion per task. MondayBench is not an agent benchmark and there are no steps to multiply.",
        },
        "efficiency": {
            "median_ttft_ms": round(statistics.median(ttft), 1) if ttft else None,
            "median_ttfa_ms": round(statistics.median(ttfa), 1) if ttfa else None,
            "median_total_latency_ms": round(statistics.median(lat), 1) if lat else None,
        },
    }, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"runs": n, "scenarios_scored": list(scen), "overall": overall}, indent=2))


if __name__ == "__main__":
    main()
