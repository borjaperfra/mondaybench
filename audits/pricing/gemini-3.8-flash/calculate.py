"""Estimated LOWER-BOUND cost per MondayBench task for Gemini 3.8 Flash (High).

The 15 official runs went through the Antigravity Language Server, which
reports no token usage of any kind, so the cost is ESTIMATED from the text
alone. Inputs, all read from disk:

  runs/monday-00N/gemini-3-8-flash-high/run-00M.json  official run artefacts
  scenarios/ + mondaybench.prompt_builder             the exact frozen prompt,
                                                      rebuilt and hash-checked
  audits/pricing/gemini-3.8-flash/pricing-source.json the rate card

Token method (see README.md):
  input   = o200k_base count of the scenario prompt. The route sends no system
            prompt (Google-side instructions it adds are unseen and uncounted).
  output  = o200k_base count of the visible response.
  thinking tokens are NOT recorded and ARE billed as output by Google, so the
  result is a minimum. o200k_base is OpenAI's tokenizer, used as a proxy:
  Gemini's tokenizer has no public offline release.

No cost is hardcoded. Calls no model. Writes only under this directory.

Usage:  python audits/pricing/gemini-3.8-flash/calculate.py
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

SLUG = "gemini-3-8-flash-high"
SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
ENCODING = "o200k_base"

src = json.loads((HERE / "pricing-source.json").read_text(encoding="utf-8"))
CUR = src["rates_usd_per_million_tokens"]
POST = src["post_introductory"]["rates_usd_per_million_tokens"]

enc = tiktoken.get_encoding(ENCODING)


def ntok(text: str) -> int:
    return len(enc.encode(text, disallowed_special=()))


def price(inp: int, out: int, rates: dict) -> float:
    return round(inp * rates["input"] / 1e6 + out * rates["output"] / 1e6, 9)


problems: list[str] = []

prompts = {}
for sid in SCEN:
    b = build_prompt(load_scenario(sid))
    prompts[sid] = {"sha256": b.sha256, "prompt_tokens": ntok(b.text)}

runs = []
for f in sorted(glob.glob(str(ROOT / "runs" / "monday-00*" / SLUG / "run-*.json"))):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    sid = d["scenario_id"]
    rel = Path(f).relative_to(ROOT).as_posix()
    ag = d["provider_metadata"]["raw_usage"]["antigravity_runtime"]
    if d["scenario_prompt_sha256"] != prompts[sid]["sha256"]:
        problems.append(f"{rel}: prompt hash does not match the rebuilt frozen prompt")
    if hashlib.sha256(d["response"].encode("utf-8")).hexdigest() != ag["response_sha256"]:
        problems.append(f"{rel}: response does not match its recorded sha256")
    if d["generation"]["system_prompt_sent"] is not False:
        problems.append(f"{rel}: system_prompt_sent is not false; input count would miss it")
    for k in ("input_tokens", "output_tokens", "reasoning_tokens"):
        if d["usage"].get(k) is not None:
            problems.append(f"{rel}: usage.{k} is not null - price it from usage instead")

    inp = prompts[sid]["prompt_tokens"]
    out = ntok(d["response"])
    row = {
        "scenario": sid,
        "run": d["run_number"],
        "run_id": d["run_id"],
        "requested_model": SLUG,
        "served_model": None,
        "route": "antigravity_language_server",
        "input_tokens": inp,
        "output_tokens": out,
        "reasoning_tokens": None,
        "response_chars": len(d["response"]),
        "input_cost": round(inp * CUR["input"] / 1e6, 9),
        "output_cost": round(out * CUR["output"] / 1e6, 9),
        "normalized_total_cost": price(inp, out, CUR),
        "post_intro_total_cost": price(inp, out, POST),
        "ttft_ms": None,
        "ttfa_ms": None,
        "latency_ms_host_wall_clock": ag.get("latency_ms_host_wall_clock"),
    }
    runs.append(row)

if len(runs) != 15:
    problems.append(f"expected 15 runs, found {len(runs)}")
if problems:
    print("STOP - integrity problems:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

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
        "cost_per_1k_tasks": round(statistics.mean(costs) * 1_000, 2),
        "post_intro_cost_per_1k_tasks": round(
            statistics.mean([x["post_intro_total_cost"] for x in rs]) * 1_000, 2),
    })

all_costs = [r["normalized_total_cost"] for r in runs]
mean_task = statistics.mean(all_costs)
mean_post = statistics.mean([r["post_intro_total_cost"] for r in runs])
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
    "is_lower_bound": True,
    "rates_in_force": f"introductory, through {src['introductory_until']}",
    "post_intro_mean_cost_per_task": round(mean_post, 6),
    "post_intro_cost_per_1k_mondaybench_equivalent_tasks": round(mean_post * 1_000, 2),
    "post_intro_effective_from": src["post_introductory"]["effective_from"],
    "mean_input_tokens_per_task": m(runs, "input_tokens"),
    "mean_output_tokens_per_task": m(runs, "output_tokens"),
    "mean_reasoning_tokens_per_task": None,
    "max_input_tokens": max(r["input_tokens"] for r in runs),
    "output_share_of_cost_pct": round(
        100 * sum(r["output_cost"] for r in runs) / sum(all_costs), 2),
}
# What the missing thinking tokens are worth, per 1,000 of them per task.
# Not an estimate of how many there were - that is unknown.
thinking_sensitivity = {
    "added_cost_per_1k_tasks_per_1000_thinking_tokens_per_task": round(
        1000 * CUR["output"] / 1e6 * 1_000, 2),
    "added_cost_per_1k_tasks_per_1000_thinking_tokens_per_task_post_intro": round(
        1000 * POST["output"] / 1e6 * 1_000, 2),
    "note": ("Every 1,000 thinking tokens per task that the route did not report adds "
             "this much to the cost per 1,000 tasks. How many there were is unknown; "
             "the run used thinking budget 'High'."),
}


def write_csv(path, rows, cols):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


write_csv(HERE / "run-costs.csv", runs, [
    "scenario", "run_id", "input_tokens", "output_tokens", "reasoning_tokens",
    "response_chars", "input_cost", "output_cost", "normalized_total_cost",
    "post_intro_total_cost", "ttfa_ms"])
write_csv(HERE / "scenario-costs.csv", scenario_rows, list(scenario_rows[0].keys()))

summary = {
    "record_type": "estimated_pricing_audit",
    "not_a_benchmark_artifact": True,
    "estimate": True,
    "estimate_note": src["estimate_note"],
    "identity": src["identity"],
    "pricing_source": {k: src[k] for k in (
        "model", "model_id", "pricing_tier", "rates_usd_per_million_tokens",
        "introductory_until", "post_introductory", "sources", "retrieved_at",
        "verification")},
    "token_method": {
        "tokenizer": ENCODING,
        "tiktoken_version": tiktoken.__version__,
        "tokenizer_assumption": ("o200k_base is OpenAI's tokenizer, not Gemini's. Google "
                                 "publishes no offline Gemini tokenizer, so the same "
                                 "o200k_base count used for GPT-6 Astra stands in for "
                                 "it. Real Gemini counts will differ somewhat in either "
                                 "direction."),
        "input": ("o200k_base count of the frozen scenario prompt, rebuilt by "
                  "mondaybench.prompt_builder and hash-checked against every run. "
                  "No system prompt was sent on this route; any Google-side "
                  "instructions the backend adds are unseen and not counted."),
        "output": "o200k_base count of the visible response only.",
        "reasoning": ("NOT RECORDED. Google bills thinking tokens as output ('Output "
                      "price (including thinking tokens)'), the run used thinking "
                      "budget 'High', and the route reports none. reasoning_tokens is "
                      "null on every run, so the cost is a LOWER BOUND."),
        "caching": "None assumed. Every input token is priced at the standard rate.",
    },
    "overall": overall,
    "thinking_sensitivity": thinking_sensitivity,
    "scenario_costs": scenario_rows,
    "run_costs": runs,
    "caveats": src["caveats"],
}
with (HERE / "summary.json").open("w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

sha = hashlib.sha256((HERE / "pricing-source.json").read_bytes()).hexdigest()
print("GEMINI 3.8 FLASH (HIGH) ESTIMATED LOWER-BOUND PRICING\n")
print(f"  rates ($/MTok)      input {CUR['input']:.2f}  output {CUR['output']:.2f}  "
      f"(through {src['introductory_until']}; then {POST['input']:.2f}/{POST['output']:.2f})")
print(f"  pricing-source sha  {sha}")
print(f"  tokenizer           {ENCODING} (proxy; tiktoken {tiktoken.__version__})")
print(f"  mean input/task     {overall['mean_input_tokens_per_task']:,.1f}")
print(f"  mean output/task    {overall['mean_output_tokens_per_task']:,.1f}  (visible only; thinking unrecorded)")
print(f"  cost/task           ${overall['mean_normalized_cost_per_task']:.6f}  (lower bound)")
print(f"  cost/1k             ${overall['cost_per_1k_mondaybench_equivalent_tasks']:,.2f}")
print(f"  cost/1k post-intro  ${overall['post_intro_cost_per_1k_mondaybench_equivalent_tasks']:,.2f}")
print(f"  +1k thinking/task   +${thinking_sensitivity['added_cost_per_1k_tasks_per_1000_thinking_tokens_per_task']:,.2f} per 1k tasks")
