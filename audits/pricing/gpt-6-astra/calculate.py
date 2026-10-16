"""Estimated cost per MondayBench task for GPT-6 Astra's 15 official runs.

The runs carry no API usage (Codex CLI route, `usage.*` is null), so the
cost is ESTIMATED, not metered. Inputs, all read from disk:

  runs/monday-00N/gpt-6-astra/run-00M.json      official run artefacts (response,
                                                Codex session counters)
  scenarios/ + mondaybench.prompt_builder       the exact frozen prompt, rebuilt
                                                and checked against each run's
                                                scenario_prompt_sha256
  audits/pricing/gpt-6-astra/pricing-source.json  the rate card

Token method (see README.md):
  input   = o200k_base count of system prompt + scenario prompt, i.e. what an
            API call of this task sends. No caching assumed.
  output  = the Codex session's own output_tokens counter, which INCLUDES
            reasoning_output_tokens. Cross-checked against an o200k_base count
            of the visible response.

No cost is hardcoded. Calls no model. Writes only under this directory.

Usage:  python audits/pricing/gpt-6-astra/calculate.py
Needs:  tiktoken (pip install tiktoken); not a project dependency.
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

import tiktoken

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402

SLUG = "gpt-6-astra"
SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
ENCODING = "o200k_base"

src = json.loads((HERE / "pricing-source.json").read_text(encoding="utf-8"))
R = src["rates_usd_per_million_tokens"]
W_IN, W_CACHED, W_OUT = R["input"] / 1e6, R["cached_input"] / 1e6, R["output"] / 1e6
LONG_CTX = src["long_context"]["threshold_input_tokens"]

enc = tiktoken.get_encoding(ENCODING)


def ntok(text: str) -> int:
    return len(enc.encode(text, disallowed_special=()))


problems: list[str] = []

# ---------------------------------------------------------------------------
# The exact input: rebuilt from the frozen scenario, verified by hash
# ---------------------------------------------------------------------------
prompts = {}
for sid in SCEN:
    b = build_prompt(load_scenario(sid))
    prompts[sid] = {"sha256": b.sha256,
                    "system_tokens": ntok(b.system_prompt),
                    "prompt_tokens": ntok(b.text)}

# ---------------------------------------------------------------------------
# The 15 runs
# ---------------------------------------------------------------------------
runs = []
for f in sorted(glob.glob(str(ROOT / "runs" / "monday-00*" / SLUG / "run-*.json"))):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    sid = d["scenario_id"]
    rel = Path(f).relative_to(ROOT).as_posix()
    if d["scenario_prompt_sha256"] != prompts[sid]["sha256"]:
        problems.append(f"{rel}: prompt hash does not match the rebuilt frozen prompt")
    for k in ("input_tokens", "output_tokens", "reasoning_tokens"):
        if d["usage"].get(k) is not None:
            problems.append(f"{rel}: usage.{k} is not null - this run is metered, "
                            "price it from usage instead of estimating")
    cx = d["provider_metadata"]["raw_usage"]["codex_runtime"]
    cu = cx["codex_usage"]
    if cx.get("requested_model_id") != SLUG:
        problems.append(f"{rel}: requested_model_id {cx.get('requested_model_id')!r}")

    p = prompts[sid]
    input_tokens = p["system_tokens"] + p["prompt_tokens"]
    visible = ntok(d["response"])
    out = int(cu["output_tokens"])
    reasoning = int(cu["reasoning_output_tokens"])
    if input_tokens > LONG_CTX:
        problems.append(f"{rel}: {input_tokens} input tokens exceeds the long-context "
                        "threshold; this script does not price the long-context tier")

    row = {
        "scenario": sid,
        "run": d["run_number"],
        "run_id": d["run_id"],
        "requested_model": SLUG,
        "served_model": None,
        "route": "codex_cli",
        "input_tokens": input_tokens,
        "system_prompt_tokens": p["system_tokens"],
        "scenario_prompt_tokens": p["prompt_tokens"],
        "cached_input_tokens": 0,
        "output_tokens": out,
        "reasoning_tokens": reasoning,
        "visible_output_tokens_o200k": visible,
        "output_crosscheck_residual": out - reasoning - visible,
        "codex_input_tokens": int(cu["input_tokens"]),
        "codex_cached_input_tokens": int(cu["cached_input_tokens"]),
        "codex_harness_context_tokens": int(cu["input_tokens"]) - input_tokens,
        "input_cost": round(input_tokens * W_IN, 9),
        "output_cost": round(out * W_OUT, 9),
        "reasoning_additional_cost": 0.0,
        "ttft_ms": None,
        "ttfa_ms": None,
        "latency_ms_host_wall_clock": cx.get("latency_ms_host_wall_clock"),
    }
    row["normalized_total_cost"] = round(row["input_cost"] + row["output_cost"], 9)
    # Sensitivity: the session exactly as Codex metered it, Codex's own
    # harness context and its cache hits included. Not the headline.
    row["as_metered_by_codex_cost"] = round(
        (row["codex_input_tokens"] - row["codex_cached_input_tokens"]) * W_IN
        + row["codex_cached_input_tokens"] * W_CACHED + out * W_OUT, 9)
    row["visible_only_lower_bound_cost"] = round(input_tokens * W_IN + visible * W_OUT, 9)
    runs.append(row)

if len(runs) != 15:
    problems.append(f"expected 15 runs, found {len(runs)}")
if problems:
    print("STOP - integrity problems:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Aggregates, normalised as in audits/pricing/opus-5
# ---------------------------------------------------------------------------
by_scen = defaultdict(list)
for r in runs:
    by_scen[r["scenario"]].append(r)


def m(rows, k, nd=1):
    return round(statistics.mean([x[k] for x in rows]), nd)


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
        "mean_input_tokens": m(rs, "input_tokens"),
        "mean_output_tokens": m(rs, "output_tokens"),
        "mean_reasoning_tokens": m(rs, "reasoning_tokens"),
        "mean_visible_output_tokens_o200k": m(rs, "visible_output_tokens_o200k"),
        "cost_per_1k_tasks": round(statistics.mean(costs) * 1_000, 2),
    })

all_costs = [r["normalized_total_cost"] for r in runs]
mean_task = statistics.mean(all_costs)
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
    "mean_input_tokens_per_task": m(runs, "input_tokens"),
    "mean_output_tokens_per_task": m(runs, "output_tokens"),
    "mean_reasoning_tokens_per_task": m(runs, "reasoning_tokens"),
    "mean_visible_output_tokens_per_task_o200k": m(runs, "visible_output_tokens_o200k"),
    "max_input_tokens": max(r["input_tokens"] for r in runs),
    "long_context_threshold_input_tokens": LONG_CTX,
    "long_context_surcharge_applies": any(r["input_tokens"] > LONG_CTX for r in runs),
    "output_share_of_cost_pct": round(
        100 * sum(r["output_cost"] for r in runs) / sum(all_costs), 2),
}
sens_metered = statistics.mean([r["as_metered_by_codex_cost"] for r in runs])
sens_visible = statistics.mean([r["visible_only_lower_bound_cost"] for r in runs])
residuals = sorted({r["output_crosscheck_residual"] for r in runs})
harness_ctx = sorted({r["codex_harness_context_tokens"] for r in runs})

sensitivity = {
    "as_metered_by_codex_cost_per_1k": round(sens_metered * 1_000, 2),
    "as_metered_by_codex_note": (
        "The Codex session counters priced as they stand: Codex's own harness "
        f"context ({', '.join(map(str, harness_ctx))} extra input tokens per run) "
        "is included and the cached-input hits Codex reported are priced at the "
        "cached rate. Higher than the headline because a direct API call of a "
        "MondayBench task would not send Codex's context."),
    "visible_output_only_cost_per_1k": round(sens_visible * 1_000, 2),
    "visible_output_only_note": (
        "Reasoning tokens left out, as if only the visible answer were billed. "
        "A floor for comparison with the Gemini estimate, which can only see "
        "the visible answer."),
}

crosscheck = {
    "method": ("For each run, Codex output_tokens - reasoning_output_tokens - "
               "o200k_base(visible response). If o200k_base is the tokenizer that "
               "served the run and reasoning is a subset of output, the residual "
               "is a small constant (message framing)."),
    "residual_values_observed": residuals,
    "codex_harness_context_tokens_observed": harness_ctx,
    "interpretation": (
        f"A residual of {residuals[0]} to {residuals[-1]} tokens on every run (out of "
        "hundreds to thousands) confirms that o200k_base reproduces the route's own "
        "token counts for this model, that reasoning_output_tokens is inside "
        "output_tokens (not in addition to it), and that Codex adds a fixed block of "
        "harness context to every input."
        if max(abs(x) for x in residuals) <= 10 else
        "The residual exceeds 10 tokens on some run; treat the tokenizer match as "
        "approximate."),
}

# ---------------------------------------------------------------------------
# Write artefacts (LF line endings, as the repository requires)
# ---------------------------------------------------------------------------
RUN_COLS = [
    "scenario", "run_id", "input_tokens", "system_prompt_tokens",
    "scenario_prompt_tokens", "cached_input_tokens", "output_tokens",
    "reasoning_tokens", "visible_output_tokens_o200k", "output_crosscheck_residual",
    "codex_input_tokens", "codex_cached_input_tokens", "codex_harness_context_tokens",
    "input_cost", "output_cost", "reasoning_additional_cost", "normalized_total_cost",
    "as_metered_by_codex_cost", "visible_only_lower_bound_cost", "ttfa_ms"]


def write_csv(path, rows, cols):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


write_csv(HERE / "run-costs.csv", runs, RUN_COLS)
write_csv(HERE / "scenario-costs.csv", scenario_rows, list(scenario_rows[0].keys()))

summary = {
    "record_type": "estimated_pricing_audit",
    "not_a_benchmark_artifact": True,
    "estimate": True,
    "estimate_note": src["estimate_note"],
    "identity": src["identity"],
    "pricing_source": {k: src[k] for k in (
        "model", "model_id", "pricing_tier", "rates_usd_per_million_tokens",
        "long_context", "sources", "retrieved_at", "verification")},
    "token_method": {
        "tokenizer": ENCODING,
        "tiktoken_version": tiktoken.__version__,
        "input": ("o200k_base count of the system prompt plus the frozen scenario "
                  "prompt, rebuilt by mondaybench.prompt_builder and hash-checked "
                  "against every run. Chat-format framing (a handful of tokens) is "
                  "not added."),
        "output": ("Codex session counter output_tokens, which includes "
                   "reasoning_output_tokens. Codex-reported, not provider "
                   "accounting; cross-checked against o200k_base below."),
        "caching": "None assumed. Every input token is priced at the uncached rate.",
        "reasoning": ("Observed (Codex reasoning_output_tokens) and inside output, "
                      "so it is billed once at the output rate and not added again. "
                      "OpenAI: reasoning tokens 'are billed as output tokens'."),
        "crosscheck": crosscheck,
    },
    "overall": overall,
    "sensitivity": sensitivity,
    "scenario_costs": scenario_rows,
    "run_costs": runs,
    "caveats": src["caveats"],
}
with (HERE / "summary.json").open("w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

sha = hashlib.sha256((HERE / "pricing-source.json").read_bytes()).hexdigest()
print("GPT-6 ASTRA ESTIMATED PRICING\n")
print(f"  rates ($/MTok)      input {R['input']:.2f}  output {R['output']:.2f}  "
      f"(cached {R['cached_input']:.2f}, not used)")
print(f"  pricing-source sha  {sha}")
print(f"  tokenizer           {ENCODING} (tiktoken {tiktoken.__version__})")
print(f"  mean input/task     {overall['mean_input_tokens_per_task']:,.1f}")
print(f"  mean output/task    {overall['mean_output_tokens_per_task']:,.1f}  "
      f"(reasoning {overall['mean_reasoning_tokens_per_task']:,.1f} inside)")
print(f"  max input           {overall['max_input_tokens']:,}  "
      f"(long-context surcharge applies: {overall['long_context_surcharge_applies']})")
print(f"  crosscheck residual {residuals}   harness context {harness_ctx}")
print(f"  cost/task           ${overall['mean_normalized_cost_per_task']:.6f}")
print(f"  cost/1k             ${overall['cost_per_1k_mondaybench_equivalent_tasks']:,.2f}")
print(f"  sensitivity         as metered by Codex ${sensitivity['as_metered_by_codex_cost_per_1k']:,.2f}/1k, "
      f"visible-only ${sensitivity['visible_output_only_cost_per_1k']:,.2f}/1k")
