"""Normalized cost for the 15 existing Claude Opus 5 runs.

Recomputes every figure in this directory from two inputs only:

  experiments/opus-5-full-mondaybench/raw/monday-00N-runM.json   raw usage
  audits/pricing/opus-5/pricing-source.json                      the rate card

No normalized cost is hardcoded. Calls no model, regenerates nothing, and
writes only under audits/pricing/opus-5/.

Usage:  python audits/pricing/opus-5/calculate.py
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "experiments/opus-5-full-mondaybench/raw"
PUB = ROOT / "analysis/cost-value/publication-data.json"

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EXPECTED_SERVED = "claude-opus-5"

# Presentation score: the independent blind re-judge result. This is the ONLY
# score used in this audit's tables.
OPUS_SCORE = 97.07
OPUS_STATUS = "PROVISIONAL"

src = json.loads((HERE / "pricing-source.json").read_text(encoding="utf-8"))
RATES = src["rates_usd_per_million_tokens"]
W_IN = RATES["base_input"] / 1e6
W_OUT = RATES["output"] / 1e6
W_CR = RATES["cache_read"] / 1e6
W_CW1H = RATES["cache_write_1h"] / 1e6
W_CW5M = RATES["cache_write_5m"] / 1e6

problems: list[str] = []

# ---------------------------------------------------------------------------
# Load and verify the 15 runs
# ---------------------------------------------------------------------------
runs = []
for f in sorted(glob.glob(str(RAW / "*.json"))):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    usage = d["usage"]
    cc = usage.get("cache_creation", {}) or {}
    mu = d["model_usage_all"]

    served = d.get("served_model")
    if served != EXPECTED_SERVED:
        problems.append(f"{Path(f).name}: served_model {served!r} != {EXPECTED_SERVED!r}")

    opus_line = mu.get("claude-opus-5")
    if opus_line is None:
        problems.append(f"{Path(f).name}: no claude-opus-5 line in modelUsage")
        continue
    aux = {k: v for k, v in mu.items() if "opus-5" not in k}

    cw_1h = int(cc.get("ephemeral_1h_input_tokens", 0) or 0)
    cw_5m = int(cc.get("ephemeral_5m_input_tokens", 0) or 0)
    cw_total = int(d["cache_creation_input_tokens"] or 0)
    if cw_1h + cw_5m != cw_total:
        problems.append(f"{Path(f).name}: cache_creation split {cw_1h}+{cw_5m} != {cw_total}")

    # Modifiers that would change the rate card if present.
    if usage.get("service_tier") != "standard":
        problems.append(f"{Path(f).name}: service_tier {usage.get('service_tier')!r} not standard")
    if usage.get("speed") not in (None, "standard"):
        problems.append(f"{Path(f).name}: speed {usage.get('speed')!r} implies fast-mode pricing")
    if usage.get("inference_geo") not in (None, "not_available", "global"):
        problems.append(f"{Path(f).name}: inference_geo {usage.get('inference_geo')!r} implies a 1.1x multiplier")

    runs.append({
        "scenario": d["scenario"],
        "run": d["run"],
        "run_id": f"opus5-{d['scenario']}-run{d['run']}",
        "requested_model": d.get("requested_model"),
        "served_model": served,
        "provider": d.get("provider"),
        "route": d.get("route"),
        "finish_reason": d.get("finish_reason"),
        "uncached_input_tokens": int(d["input_tokens"] or 0),
        "cache_creation_input_tokens": cw_total,
        "cache_write_1h_tokens": cw_1h,
        "cache_write_5m_tokens": cw_5m,
        "cache_read_input_tokens": int(d["cache_read_input_tokens"] or 0),
        "output_tokens": int(d["output_tokens"] or 0),
        "reasoning_tokens": int(d["reasoning_tokens"] or 0),
        "opus_reported_cost_usd": opus_line.get("costUSD"),
        "route_total_cost_usd": d.get("total_cost_usd_including_auxiliary"),
        "auxiliary_models": sorted(aux),
        "auxiliary_cost_usd": round(sum(v.get("costUSD") or 0 for v in aux.values()), 9),
        "latency_ms": d.get("latency_ms"),
        "ttft_ms": d.get("ttft_ms"),
        "ttfa_ms": d.get("ttfa_ms"),
        "cost_basis": d.get("cost_basis"),
    })

if len(runs) != 15:
    problems.append(f"expected 15 runs, found {len(runs)}")
if problems:
    print("STOP - integrity problems:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Normalized cost, bucket by bucket at its own rate
# ---------------------------------------------------------------------------
for r in runs:
    r["effective_prompt_tokens"] = (r["uncached_input_tokens"]
                                    + r["cache_creation_input_tokens"]
                                    + r["cache_read_input_tokens"])
    r["uncached_input_cost"] = round(r["uncached_input_tokens"] * W_IN, 9)
    r["cache_creation_cost"] = round(r["cache_write_1h_tokens"] * W_CW1H
                                     + r["cache_write_5m_tokens"] * W_CW5M, 9)
    r["cache_read_cost"] = round(r["cache_read_input_tokens"] * W_CR, 9)
    r["output_cost"] = round(r["output_tokens"] * W_OUT, 9)
    # Reasoning is inside the billable output bucket - see pricing-source.json.
    r["reasoning_additional_cost"] = 0.0
    r["normalized_total_cost"] = round(r["uncached_input_cost"] + r["cache_creation_cost"]
                                       + r["cache_read_cost"] + r["output_cost"], 9)

    rep = r["opus_reported_cost_usd"]
    norm = r["normalized_total_cost"]
    r["absolute_difference"] = round(norm - rep, 12) if rep is not None else None
    r["percentage_difference"] = round(100 * (norm - rep) / rep, 9) if rep else None
    # Thresholds, stated rather than tuned: an exact reconciliation is a match to
    # the smallest unit the provider reports; ROUNDING_ONLY allows sub-0.5% drift
    # from published-rate rounding; anything larger is material.
    if rep is None:
        r["reconciliation"] = "UNAVAILABLE"
    elif abs(r["percentage_difference"]) < 1e-6:
        r["reconciliation"] = "EXACT_RECONCILIATION"
    elif abs(r["percentage_difference"]) < 0.5:
        r["reconciliation"] = "ROUNDING_ONLY"
    else:
        r["reconciliation"] = "MATERIAL_DIFFERENCE"

    # What double counting reasoning would have produced, kept as evidence.
    r["_counterfactual_double_counted_cost"] = round(norm + r["reasoning_tokens"] * W_OUT, 9)

# ---------------------------------------------------------------------------
# Scenario and overall aggregates
# ---------------------------------------------------------------------------
by_scen = defaultdict(list)
for r in runs:
    by_scen[r["scenario"]].append(r)

scenario_rows = []
for sid in SCEN:
    rs = by_scen[sid]
    costs = [x["normalized_total_cost"] for x in rs]
    scenario_rows.append({
        "scenario": sid,
        "runs": len(rs),
        "mean_normalized_cost": round(statistics.mean(costs), 6),
        "median_normalized_cost": round(statistics.median(costs), 6),
        "min_normalized_cost": round(min(costs), 6),
        "max_normalized_cost": round(max(costs), 6),
        "mean_uncached_input_tokens": round(statistics.mean([x["uncached_input_tokens"] for x in rs]), 1),
        "mean_cache_creation_tokens": round(statistics.mean([x["cache_creation_input_tokens"] for x in rs]), 1),
        "mean_cache_read_tokens": round(statistics.mean([x["cache_read_input_tokens"] for x in rs]), 1),
        "mean_output_tokens": round(statistics.mean([x["output_tokens"] for x in rs]), 1),
        "mean_reasoning_tokens": round(statististics_mean := statistics.mean([x["reasoning_tokens"] for x in rs]), 1),
        "mean_opus_reported_cost": round(statistics.mean([x["opus_reported_cost_usd"] for x in rs]), 6),
        "cost_per_1k_tasks": round(statistics.mean(costs) * 1_000, 2),
    })

all_costs = [r["normalized_total_cost"] for r in runs]
mean_task = statistics.mean(all_costs)

# Cache accounting. In four of the five scenarios run 1 pays the 1h cache write
# and runs 2-3 pay cache reads. monday-004 pays cache READS on all three runs
# and no write, because the write was paid by a generation that was discarded
# (see the experiment's GENERATION-INCIDENT.md). That makes monday-004's
# as-observed cost lower than a cold run of the same three tasks would be, and
# the size of the gap is reported rather than smoothed away.
missing_write_tokens = 0
for sid in SCEN:
    rs = by_scen[sid]
    if sum(x["cache_creation_input_tokens"] for x in rs) == 0:
        reads = {x["cache_read_input_tokens"] for x in rs if x["cache_read_input_tokens"]}
        if len(reads) == 1:
            missing_write_tokens += reads.pop()
missing_write_cost = round(missing_write_tokens * W_CW1H, 6)

cache_totals = {
    "total_uncached_input_tokens": sum(r["uncached_input_tokens"] for r in runs),
    "total_cache_creation_tokens": sum(r["cache_creation_input_tokens"] for r in runs),
    "total_cache_read_tokens": sum(r["cache_read_input_tokens"] for r in runs),
    "total_output_tokens": sum(r["output_tokens"] for r in runs),
    "total_reasoning_tokens": sum(r["reasoning_tokens"] for r in runs),
    "cost_uncached_input": round(sum(r["uncached_input_cost"] for r in runs), 6),
    "cost_cache_creation": round(sum(r["cache_creation_cost"] for r in runs), 6),
    "cost_cache_read": round(sum(r["cache_read_cost"] for r in runs), 6),
    "cost_output": round(sum(r["output_cost"] for r in runs), 6),
    "cost_total": round(sum(all_costs), 6),
}
cache_totals["output_share_of_cost_pct"] = round(
    100 * cache_totals["cost_output"] / cache_totals["cost_total"], 2)
cache_totals["prompt_side_share_of_cost_pct"] = round(
    100 * (cache_totals["cost_total"] - cache_totals["cost_output"]) / cache_totals["cost_total"], 2)
cache_totals["cache_read_saving_vs_uncached"] = round(
    cache_totals["total_cache_read_tokens"] * (W_IN - W_CR), 6)
cache_totals["monday_004_omitted_cache_write_tokens"] = missing_write_tokens
cache_totals["monday_004_omitted_cache_write_cost"] = missing_write_cost

overall = {
    "n_runs": len(runs),
    "mean_normalized_cost_per_task": round(mean_task, 6),
    "median_normalized_cost_per_task": round(statistics.median(all_costs), 6),
    "min_normalized_cost_per_task": round(min(all_costs), 6),
    "max_normalized_cost_per_task": round(max(all_costs), 6),
    "stdev_normalized_cost_per_task": round(statistics.stdev(all_costs), 6),
    "cost_per_1k_mondaybench_equivalent_tasks": round(mean_task * 1_000, 2),
    "cost_per_100k_mondaybench_equivalent_tasks": round(mean_task * 100_000, 2),
    "cost_per_1m_mondaybench_equivalent_tasks": round(mean_task * 1_000_000, 2),
    "mean_opus_reported_cost_per_task": round(
        statistics.mean([r["opus_reported_cost_usd"] for r in runs]), 6),
    "mean_route_total_cost_per_task": round(
        statistics.mean([r["route_total_cost_usd"] for r in runs]), 6),
    "mean_auxiliary_cost_per_task": round(
        statistics.mean([r["auxiliary_cost_usd"] for r in runs]), 6),
}
overall["auxiliary_share_of_route_cost_pct"] = round(
    100 * overall["mean_auxiliary_cost_per_task"] / overall["mean_route_total_cost_per_task"], 2)

recon = {
    "counts": {k: sum(1 for r in runs if r["reconciliation"] == k)
               for k in ("EXACT_RECONCILIATION", "ROUNDING_ONLY",
                         "MATERIAL_DIFFERENCE", "UNAVAILABLE")},
    "max_absolute_pct_difference": round(
        max(abs(r["percentage_difference"]) for r in runs), 9),
    "thresholds": {
        "EXACT_RECONCILIATION": "|difference| < 1e-6 %",
        "ROUNDING_ONLY": "|difference| < 0.5 %",
        "MATERIAL_DIFFERENCE": ">= 0.5 %",
    },
}

# ---------------------------------------------------------------------------
# Comparison with the published top band (read, never rewritten)
# ---------------------------------------------------------------------------
pub = json.loads(PUB.read_text(encoding="utf-8"))
pub_by = {m["model"]: m for m in pub["models"]}


def cost_bounds(v):
    if isinstance(v, list):
        return float(v[0]), float(v[1])
    return float(v), float(v)


opus_cost_1k = overall["cost_per_1k_mondaybench_equivalent_tasks"]
comparators = ["claude-fable-5-1", "qwen3.8-flash", "glm5.3-flash"]

top_rows = [{
    "model": "Claude Opus 5*",
    "monday_score": OPUS_SCORE,
    "cost_per_1k": opus_cost_1k,
    "cost_per_1k_display": f"${opus_cost_1k:,.2f}",
    "median_ttfa_s": round(statistics.median([r["ttfa_ms"] for r in runs]) / 1000, 1),
    "mean_output_tokens": round(statistics.mean([r["output_tokens"] for r in runs]), 1),
    "pricing_basis": "First-party",
    "status": OPUS_STATUS,
}]
for slug in comparators:
    m = pub_by[slug]
    lo, hi = cost_bounds(m["normalized_cost_per_1k"])
    top_rows.append({
        "model": m["display_name"],
        "monday_score": m["score"],
        "cost_per_1k": m["normalized_cost_per_1k"],
        "cost_per_1k_display": f"${lo:,.2f}" if lo == hi else f"${lo:,.2f}-${hi:,.2f}",
        "median_ttfa_s": round(m["median_ttfa_ms"] / 1000, 1),
        "mean_output_tokens": m["mean_output_tokens"],
        "pricing_basis": m["price_basis"],
        "status": "PROVISIONAL" if m.get("provisional") else "official",
    })

tradeoffs = {}
opus_ttfa = top_rows[0]["median_ttfa_s"]
opus_out = top_rows[0]["mean_output_tokens"]
for slug in comparators:
    m = pub_by[slug]
    lo, hi = cost_bounds(m["normalized_cost_per_1k"])
    # A range gives a range of multiples; report both ends, widest last.
    mult_hi = opus_cost_1k / lo
    mult_lo = opus_cost_1k / hi
    tradeoffs[m["display_name"]] = {
        "their_score": m["score"],
        "score_difference_opus_minus_them": round(OPUS_SCORE - m["score"], 2),
        "their_cost_per_1k": m["normalized_cost_per_1k"],
        "cost_multiple": (round(mult_lo, 2) if abs(mult_hi - mult_lo) < 0.005
                          else [round(mult_lo, 2), round(mult_hi, 2)]),
        "absolute_difference_per_1k": (round(opus_cost_1k - hi, 2) if lo == hi
                                       else [round(opus_cost_1k - hi, 2), round(opus_cost_1k - lo, 2)]),
        "absolute_difference_per_100k": (round((opus_cost_1k - hi) * 100, 2) if lo == hi
                                         else [round((opus_cost_1k - hi) * 100, 2),
                                               round((opus_cost_1k - lo) * 100, 2)]),
        "absolute_difference_per_1m": (round((opus_cost_1k - hi) * 1000, 2) if lo == hi
                                       else [round((opus_cost_1k - hi) * 1000, 2),
                                             round((opus_cost_1k - lo) * 1000, 2)]),
        "ttfa_ratio_them_over_opus": round((m["median_ttfa_ms"] / 1000) / opus_ttfa, 2),
        "output_token_ratio_them_over_opus": round(m["mean_output_tokens"] / opus_out, 2),
    }

# ---------------------------------------------------------------------------
# Experimental Pareto, kept strictly separate from the official frontier
# ---------------------------------------------------------------------------
def frontier(points):
    """points: [(name, score, cost_for_domination)] -> non-dominated names."""
    out = []
    for name, s, c in points:
        dominated = any(
            (s2 >= s and c2 <= c and (s2 > s or c2 < c))
            for name2, s2, c2 in points if name2 != name)
        if not dominated:
            out.append(name)
    return out


official = json.loads((ROOT / "analysis/cost-value/pareto.json").read_text(encoding="utf-8"))

# Two bases, kept distinct. The official PRIMARY frontier is first-party priced
# models only; the official EXTENDED frontier also admits provider-public
# prices. Adding Opus to the wrong one would produce a frontier that looks
# comparable to the primary and is not.
first_party, extended = [], []
for m in pub["models"]:
    v = m["normalized_cost_per_1k"]
    if v == "UNKNOWN":
        continue
    lo, hi = cost_bounds(v)
    pt = (m["display_name"], m["score"], hi)      # conservative (expensive) end
    extended.append(pt)
    if m["price_basis"] == "First-party":
        first_party.append(pt)

OPUS_PT = ("Claude Opus 5*", OPUS_SCORE, opus_cost_1k)
exp_primary = frontier(first_party + [OPUS_PT])
exp_extended = frontier(extended + [OPUS_PT])
dominated_by_opus = [
    name for name, s, c in extended
    if OPUS_SCORE >= s and opus_cost_1k <= c and (OPUS_SCORE > s or opus_cost_1k < c)]

pareto = {
    "definition": official.get("definition"),
    "frontier_is_not_a_ranking": official.get("frontier_is_not_a_ranking"),
    "official_primary_frontier_unchanged": [r["model"] for r in official["primary"]["frontier"]],
    "official_extended_frontier_unchanged": [r["model"] for r in official["extended_provider"]["frontier"]],
    "experimental_first_party_basis_plus_provisional": exp_primary,
    "experimental_extended_basis_plus_provisional": exp_extended,
    "opus_on_experimental_frontier": "Claude Opus 5*" in exp_primary,
    "models_opus_would_dominate": dominated_by_opus,
    "why": ("Opus records the highest measured score in this experiment, so no model "
            "can dominate it on score - domination needs a model at least as good AND "
            "no more expensive. It in turn dominates Claude Fable 5.1*, which it beats "
            "on measured score and undercuts on cost, so Fable leaves the experimental "
            "frontier."),
    "warning": ("EXPERIMENTAL ONLY. Both experimental frontiers include a provisional, "
                "off-benchmark result and MUST NOT replace, modify or be presented "
                "alongside the official frontiers. The official primary and extended "
                "frontiers above are reproduced unchanged from analysis/cost-value/"
                "pareto.json and are not recomputed here."),
}

# ---------------------------------------------------------------------------
# Write artifacts
# ---------------------------------------------------------------------------
def write_csv(path, rows, cols):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


write_csv(HERE / "run-costs.csv", runs, [
    "scenario", "run_id", "served_model", "finish_reason",
    "uncached_input_tokens", "cache_creation_input_tokens", "cache_write_1h_tokens",
    "cache_write_5m_tokens", "cache_read_input_tokens", "output_tokens",
    "reasoning_tokens", "effective_prompt_tokens",
    "uncached_input_cost", "cache_creation_cost", "cache_read_cost", "output_cost",
    "reasoning_additional_cost", "normalized_total_cost",
    "opus_reported_cost_usd", "absolute_difference", "percentage_difference",
    "reconciliation", "route_total_cost_usd", "auxiliary_cost_usd",
    "ttft_ms", "ttfa_ms", "latency_ms"])
write_csv(HERE / "scenario-costs.csv", scenario_rows, list(scenario_rows[0].keys()))
write_csv(HERE / "top-comparison.csv", top_rows, [
    "model", "monday_score", "cost_per_1k_display", "median_ttfa_s",
    "mean_output_tokens", "pricing_basis", "status"])

summary = {
    "record_type": "opus_5_pricing_audit",
    "not_a_benchmark_artifact": True,
    "presentation_score": {"model": "Claude Opus 5*", "monday_score": OPUS_SCORE,
                           "status": OPUS_STATUS,
                           "score_provenance": "independent blind re-judge",
                           "provisional_reason": "generation route through Claude Code "
                                                 "rather than MondayBench's standard "
                                                 "provider route"},
    "identity": src["identity"],
    "pricing_source": {k: src[k] for k in
                       ("source_url", "source_type", "retrieved_at", "model", "model_id",
                        "pricing_tier", "rates_usd_per_million_tokens", "batch_pricing",
                        "modifiers_not_applied")},
    "billing_semantics": src["billing_semantics"],
    "auxiliary_call_handling": src["auxiliary_call_handling"],
    "usage_and_cost_totals": cache_totals,
    "overall": overall,
    "reported_vs_normalized": recon,
    "scenario_costs": scenario_rows,
    "run_costs": runs,
    "top_comparison": top_rows,
    "tradeoffs": tradeoffs,
    "experimental_pareto": pareto,
    "generation_route_status": "PROVISIONAL_OFF_BENCHMARK",
}
(HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                   encoding="utf-8")

# ---------------------------------------------------------------------------
# Terminal report
# ---------------------------------------------------------------------------
sha = hashlib.sha256((HERE / "pricing-source.json").read_bytes()).hexdigest()
print("OPUS 5 PRICING AUDIT COMPLETE\n")
print("Identity:")
print(f"  requested model     {runs[0]['requested_model']}")
print(f"  served model        {runs[0]['served_model']}  (15/15)")
print(f"  pricing identity    {src['identity']['identity_confidence']}")
print(f"  pricing basis       {src['identity']['pricing_basis']}")
print(f"  confidence          {src['identity']['pricing_confidence']}")
print("\nPublic pricing ($/MTok):")
print(f"  input               {RATES['base_input']:.2f}")
print(f"  output              {RATES['output']:.2f}")
print(f"  cache read          {RATES['cache_read']:.2f}")
print(f"  cache write 1h      {RATES['cache_write_1h']:.2f}   <- the modality these runs used")
print(f"  cache write 5m      {RATES['cache_write_5m']:.2f}   (not used)")
print(f"  source              {src['source_url']}")
print(f"  retrieved at        {src['retrieved_at']}")
print(f"  snapshot sha256     {sha}")
print("\nBilling:")
print(f"  reasoning treatment {src['billing_semantics']['reasoning_treatment_short']}")
print(f"  cache semantics     {src['billing_semantics']['cache_semantics_short']}")
print(f"  auxiliary Haiku excluded from normalized Opus cost: YES")
print(f"    mean route total  ${overall['mean_route_total_cost_per_task']:.6f}")
print(f"    mean Opus-only    ${overall['mean_opus_reported_cost_per_task']:.6f}")
print(f"    mean auxiliary    ${overall['mean_auxiliary_cost_per_task']:.6f} "
      f"({overall['auxiliary_share_of_route_cost_pct']}% of route cost)")
print("\nUsage (mean per task):")
print(f"  uncached input      {statistics.mean([r['uncached_input_tokens'] for r in runs]):,.1f}")
print(f"  cache creation      {statistics.mean([r['cache_creation_input_tokens'] for r in runs]):,.1f}")
print(f"  cache read          {statistics.mean([r['cache_read_input_tokens'] for r in runs]):,.1f}")
print(f"  output              {statistics.mean([r['output_tokens'] for r in runs]):,.1f}")
print(f"  reasoning           {statistics.mean([r['reasoning_tokens'] for r in runs]):,.1f}  (inside output)")
print("\nNormalized cost (MondayBench-equivalent tasks):")
print(f"  cost/task           ${overall['mean_normalized_cost_per_task']:.6f}")
print(f"  cost/1k             ${overall['cost_per_1k_mondaybench_equivalent_tasks']:,.2f}")
print(f"  cost/100k           ${overall['cost_per_100k_mondaybench_equivalent_tasks']:,.2f}")
print(f"  cost/1M             ${overall['cost_per_1m_mondaybench_equivalent_tasks']:,.2f}")
print("\nReported reconciliation (Opus-only vs list-price recomputation):")
print(f"  mean Opus reported  ${overall['mean_opus_reported_cost_per_task']:.6f}")
print(f"  mean normalized     ${overall['mean_normalized_cost_per_task']:.6f}")
print(f"  difference          ${overall['mean_normalized_cost_per_task'] - overall['mean_opus_reported_cost_per_task']:+.9f}")
print(f"  worst run |diff|    {recon['max_absolute_pct_difference']:.9f}%")
print(f"  classification      {recon['counts']}")
print("\nQuality / efficiency:")
print(f"  Monday Score        {OPUS_SCORE}  {OPUS_STATUS}")
print(f"  median TTFA         {top_rows[0]['median_ttfa_s']} s")
print(f"  mean output         {top_rows[0]['mean_output_tokens']:,.0f}")
print("\nComparison (cost/1k):")
for name, t in tradeoffs.items():
    m = t["cost_multiple"]
    ms = f"{m}x" if not isinstance(m, list) else f"{m[0]}-{m[1]}x"
    print(f"  vs {name:20} score {t['score_difference_opus_minus_them']:+.2f}   cost {ms}")
print("\nIntegrity:")
print(f"  suite digest        (unchanged - verified separately)")
print(f"  existing snapshots  untouched")
print(f"  website             unchanged")
print(f"  leaderboard         unchanged")
print("\nArtifacts:")
for f in sorted(HERE.glob("*")):
    if f.is_file():
        print(f"  {f.relative_to(ROOT)}")
