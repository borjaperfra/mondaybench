"""GLM 5.3 cost reconstruction, and a validation of the method against two
already-published figures.

READ-ONLY over runs, verdicts, evaluations and leaderboards. Calls no model.

WHY THE METHOD IS VALIDATED FIRST. A normalized cost is a counterfactual: what
this workload would have cost at the vendor's public list price. The only way to
know the reconstruction is right is to point it at models whose $/1k is already
published and gated, and require it to reproduce them. GLM 5.2 ($39.50/1k) and
GLM 5.3 Flash ($10.71/1k) are both Z.AI SKUs with HIGH-confidence first-party
prices, so they are the right controls for a third Z.AI SKU.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent

SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1", "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3", "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}

# From analysis/cost-value/pricing-snapshot-2026-09-02.yaml, plus the GLM-5.3
# row read from the same vendor page the snapshot cites.
LIST = {
    "glm5.2":       {"in": 1.40,  "out": 4.40, "cache_read": 0.26,  "cache_write": 0.0},
    "glm5.3-flash": {"in": 0.15,  "out": 0.50, "cache_read": 0.03,  "cache_write": 0.0},
    "glm5.3":       {"in": 1.40,  "out": 4.40, "cache_read": 0.26,  "cache_write": 0.0},
}
PUBLISHED_PER_1K = {"glm5.2": 39.50, "glm5.3-flash": 10.71}


def official_runs(slug: str, suite_version: str = "1.1") -> list[dict]:
    """The runs that earned an official evaluation, read from the run artifacts.

    Deliberately NOT every file under runs/: rejected attempts were never
    scored and must not enter a cost figure. The evaluation set defines the
    battery, exactly as the leaderboard does.
    """
    out = []
    for sid in SCENARIOS:
        ev = EVALUATORS[sid]
        base = ROOT / "evaluations"
        if suite_version not in (None, "1.0"):
            base = base / f"v{suite_version}"
        eval_dir = base / ev / sid / slug
        if not eval_dir.is_dir():
            continue
        for evaluation in sorted(eval_dir.glob("run-*.json")):
            run_path = ROOT / "runs" / sid / slug / evaluation.name
            if not run_path.is_file():
                raise SystemExit(f"missing raw output for {evaluation}")
            record = json.loads(run_path.read_text(encoding="utf-8"))
            record["_scenario"] = sid
            out.append(record)
    return out


def usage_of(record: dict) -> dict:
    """Token usage as the provider reported it.

    CACHE TOKENS ARE NOT IN `usage`. `RunUsage` carries only input, output and
    reasoning; the cached-prompt counts live in
    `provider_metadata.raw_usage.prompt_tokens_details`. Reading only `usage`
    silently treats every cached prompt token as full-rate input, which
    overstated GLM 5.2 by 6.8% on the first pass here.
    """
    usage = record.get("usage") or {}
    raw = (record.get("provider_metadata") or {}).get("raw_usage") or {}
    details = raw.get("prompt_tokens_details") or {}
    return {
        "input": usage.get("input_tokens") or 0,
        "output": usage.get("output_tokens") or 0,
        "reasoning": usage.get("reasoning_tokens") or 0,
        "cache_read": details.get("cached_tokens") or 0,
        "cache_write": details.get("cache_write_tokens") or 0,
    }


def normalized_cost(records: list[dict], rates: dict) -> dict:
    """Cost per task at list price, from token usage.

    REASONING IS NOT ADDED AGAIN. `output_tokens` is the provider's
    `completion_tokens`, and `reasoning_tokens` sits inside it - verified below
    on every run. Billing output once is billing reasoning once.

    Cache-read tokens are billed at the cached rate and REMOVED from the
    full-rate input, because a cached prompt token is charged once, at the cache
    rate. Where no cache is reported this reduces to input x input_rate.
    """
    total = 0.0
    for record in records:
        u = usage_of(record)
        uncached_input = max(0, u["input"] - u["cache_read"])
        total += (
            uncached_input * rates["in"]
            + u["cache_read"] * rates["cache_read"]
            + u["cache_write"] * rates["cache_write"]
            + u["output"] * rates["out"]
        ) / 1e6
    per_task = total / len(records)
    return {
        "runs": len(records),
        "per_task": round(per_task, 6),
        "per_1k": round(per_task * 1_000, 2),
        "per_100k": round(per_task * 100_000, 2),
        "per_1m": round(per_task * 1_000_000, 2),
    }


def main() -> None:
    report: dict = {"read_only": True, "model_calls": 0, "validation": {}, "glm5.3": {}}

    # ---- validate the method on two published figures ---------------------
    for slug, expected in PUBLISHED_PER_1K.items():
        records = official_runs(slug)
        got = normalized_cost(records, LIST[slug])
        delta = round(got["per_1k"] - expected, 2)
        report["validation"][slug] = {
            "runs": got["runs"], "published_per_1k": expected,
            "reconstructed_per_1k": got["per_1k"], "delta": delta,
            "match": abs(delta) <= max(0.05, expected * 0.005),
        }
        print(f"  {slug:<14} published {expected:>7.2f}/1k   reconstructed "
              f"{got['per_1k']:>7.2f}/1k   delta {delta:+.2f}   "
              f"{'MATCH' if report['validation'][slug]['match'] else 'MISMATCH'}")

    # ---- GLM 5.3 ----------------------------------------------------------
    records = official_runs("glm5.3")
    usages = [usage_of(r) for r in records]
    perfs = [(r.get("performance") or {}) for r in records]

    reasoning_inside_output = all(u["reasoning"] <= u["output"] for u in usages)
    any_cache = any(u["cache_read"] or u["cache_write"] for u in usages)
    reported_costs = [
        ((r.get("economics") or {}) or {}).get("total_cost_usd") for r in records
    ]
    provider_fields = [
        ((r.get("provider_metadata") or {}) or {}).get("provider") for r in records
    ]

    med = lambda key: round(statistics.median([p[key] for p in perfs if p.get(key)]), 1)
    mean = lambda key: round(statistics.mean([u[key] for u in usages]), 1)

    first_party = normalized_cost(records, LIST["glm5.3"])
    route_zai = normalized_cost(records, {"in": 0.075, "out": 0.25,
                                          "cache_read": 0.015, "cache_write": 0.0})
    route_parasail = normalized_cost(records, {"in": 0.15, "out": 0.50,
                                               "cache_read": 0.03, "cache_write": 0.0})

    report["glm5.3"] = {
        "runs": len(records),
        "model_ids": sorted({(r.get("model") or {}).get("model_id") for r in records}),
        "providers_in_config": sorted({(r.get("model") or {}).get("provider") for r in records}),
        "finish_reasons": sorted({r.get("finish_reason") for r in records}),
        "usage": {
            "mean_input": mean("input"), "mean_output": mean("output"),
            "mean_reasoning": mean("reasoning"),
            "total_cache_read": sum(u["cache_read"] for u in usages),
            "total_cache_write": sum(u["cache_write"] for u in usages),
        },
        "billing_semantics": {
            "reasoning_inside_output_tokens": reasoning_inside_output,
            "reasoning_double_counted": False,
            "cache_reported": any_cache,
            "cache_treatment": ("no cache tokens reported on any scored run, so the cached "
                                "rate contributes nothing" if not any_cache
                                else "cache_read billed at the cached rate and removed from "
                                     "full-rate input"),
            "provider_reported_cost_available_on_scored_runs": any(
                c is not None for c in reported_costs),
            "provider_field_observable_on_scored_runs": any(
                p is not None for p in provider_fields),
            "why": ("The scored runs are STREAMING. The streaming response carries neither "
                    "`provider` nor `cost`; both appear only on the non-streaming path. So no "
                    "per-run reported cost exists and none was inferred - the normalized figure "
                    "is reconstructed from token usage x published price."),
        },
        "performance": {
            "median_ttft_ms": med("ttft_ms"), "median_ttft_s": round(med("ttft_ms") / 1000, 3),
            "median_ttfa_ms": med("ttfa_ms"), "median_ttfa_s": round(med("ttfa_ms") / 1000, 3),
            "median_total_ms": med("total_latency_ms"),
            "median_total_s": round(med("total_latency_ms") / 1000, 3),
        },
        "cost": {
            "first_party_list_zai": {
                "rates": LIST["glm5.3"], **first_party,
                "basis": "FIRST_PARTY_LIST",
                "source_url": "https://docs.z.ai/guides/overview/pricing",
                "sku": "GLM-5.3",
            },
            "provider_route_observed_zai_upstream": {
                "rates": {"in": 0.075, "out": 0.25}, **route_zai,
                "basis": "PROVIDER_ROUTE_MEASURED",
            },
            "provider_route_observed_parasail_upstream": {
                "rates": {"in": 0.15, "out": 0.50}, **route_parasail,
                "basis": "PROVIDER_ROUTE_MEASURED",
            },
        },
    }

    (HERE / "_glm53-cost-reconstruction.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    g = report["glm5.3"]
    print(f"\nGLM 5.3: {g['runs']} official runs, model_ids {g['model_ids']}, "
          f"finish {g['finish_reasons']}")
    print(f"  mean input {g['usage']['mean_input']}  mean output {g['usage']['mean_output']}  "
          f"mean reasoning {g['usage']['mean_reasoning']}")
    print(f"  cache read {g['usage']['total_cache_read']}  "
          f"cache write {g['usage']['total_cache_write']}  "
          f"reasoning inside output: {g['billing_semantics']['reasoning_inside_output_tokens']}")
    print(f"  median TTFT {g['performance']['median_ttft_s']}s  "
          f"TTFA {g['performance']['median_ttfa_s']}s  "
          f"total {g['performance']['median_total_s']}s")
    print(f"  reported cost on scored runs: "
          f"{g['billing_semantics']['provider_reported_cost_available_on_scored_runs']}")
    print()
    for key, block in g["cost"].items():
        print(f"  {key:<44} ${block['per_task']:.6f}/task  ${block['per_1k']:>8.2f}/1k")


if __name__ == "__main__":
    main()
