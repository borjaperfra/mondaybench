"""READ-ONLY re-judge inventory and cost estimate for MondayBench v1.1.

Counts what exists, what would have to be re-judged, and what that would cost -
under both of the routes this project can actually use. Calls no model.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analyse import EVALUATORS, SCENARIOS  # noqa: E402
from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402

OFFICIAL = ["glm5.3-flash", "glm5.2", "mimo-v2.5", "deepseek-v4-flash",
            "qwen3.8-flash", "qwen3.6", "gemma4", "glm5.3"]
# Reachable only through a route that is not the official provider route, so
# they are outside the official migration by construction.
PROVISIONAL = ["claude-opus-5", "claude-fable-5-1"]

CHARS_PER_TOKEN = 4.0  # conventional English estimate; stated, not measured


def main() -> None:
    inv = {"official_models": OFFICIAL, "scenarios": SCENARIOS,
           "regeneration_required": 0, "rows": [], "blockers": []}

    # ---- what raw output exists -------------------------------------------
    per_model = {}
    for slug in OFFICIAL:
        row = {"model": slug, "scenarios": 0, "runs_on_disk": 0, "responses": 0,
               "raw_output_available": True, "needs_regeneration": False,
               "needs_rejudge": True, "per_scenario": {}, "missing": []}
        for sid in SCENARIOS:
            d = ROOT / "runs" / sid / slug
            files = sorted(d.glob("run-*.json")) if d.is_dir() else []
            ev = ROOT / "evaluations" / EVALUATORS[sid] / sid / slug
            evals = sorted(ev.glob("run-*.json")) if ev.is_dir() else []
            row["per_scenario"][sid] = {"runs_on_disk": len(files),
                                        "judged_runs": len(evals)}
            row["runs_on_disk"] += len(files)
            # The re-judge scope is the runs that were JUDGED, not every file on
            # disk: the surplus files are rejected attempts that never earned an
            # evaluation and must not acquire one now.
            row["responses"] += len(evals)
            if files:
                row["scenarios"] += 1
            if len(evals) < 3:
                row["missing"].append(sid + ": " + str(len(evals)) + "/3 judged")
                row["raw_output_available"] = False
            for e in evals:
                if not (d / e.name).exists():
                    row["missing"].append(sid + ": no raw output for " + e.name)
                    row["raw_output_available"] = False
        if row["missing"]:
            inv["blockers"].append(slug + " -> " + "; ".join(row["missing"]))
        per_model[slug] = row
        inv["rows"].append(row)

    inv["total_official_responses"] = sum(r["responses"] for r in inv["rows"])
    inv["total_responses_available"] = sum(
        r["responses"] for r in inv["rows"] if r["raw_output_available"])

    # ---- judge work per scenario ------------------------------------------
    work = {}
    for sid in SCENARIOS:
        cfg = load_evaluator(EVALUATORS[sid])
        sc = load_scenario(sid, rubric_file=cfg.rubric_file)
        r = sc.rubric
        has_noise = r.noise is not None
        source_chars = sum(len(sc.source_text[n]) for n in sc.sources)
        gt_chars = len(json.dumps(sc.ground_truth, ensure_ascii=False)) if sc.ground_truth \
            else len(sc.ground_truth_text or "")
        crit_def_chars = sum(len(c.pass_definition) + len(c.partial_definition)
                             + len(c.fail_definition) for c in r.criteria)
        resp_chars = []
        for slug in OFFICIAL:
            d = ROOT / "runs" / sid / slug
            ed = ROOT / "evaluations" / EVALUATORS[sid] / sid / slug
            judged = {f.name for f in ed.glob("run-*.json")} if ed.is_dir() else set()
            for f in sorted(d.glob("run-*.json")) if d.is_dir() else []:
                if f.name in judged:
                    resp_chars.append(len(json.loads(f.read_text(encoding="utf-8"))["response"]))
        work[sid] = {
            "criteria": len(r.criteria),
            "has_noise_dimension": has_noise,
            "judge_calls_per_run": len(r.criteria) + (1 if has_noise else 0) + 1,
            "source_material_chars": source_chars,
            "ground_truth_chars": gt_chars,
            "criterion_definition_chars": crit_def_chars,
            "mean_response_chars": round(statistics.mean(resp_chars)) if resp_chars else 0,
            "median_response_chars": round(statistics.median(resp_chars)) if resp_chars else 0,
            "responses_counted": len(resp_chars),
        }
    inv["per_scenario_judge_work"] = work

    # ---- route 1: the API judge (HYPOTHETICAL - forbidden on this project) --
    calls = tokens_in = 0
    for sid in SCENARIOS:
        w = work[sid]
        runs = w["responses_counted"]
        mean_crit_def = w["criterion_definition_chars"] / max(1, w["criteria"])
        # one call per criterion: its definitions + a ground-truth slice + the response
        per_crit = (mean_crit_def + w["ground_truth_chars"] * 0.15 + w["mean_response_chars"] + 1200)
        crit_calls = w["criteria"] * runs
        # the penalty call carries the WHOLE source material - the expensive one
        pen = (w["source_material_chars"] + w["ground_truth_chars"] + w["mean_response_chars"] + 2500)
        noise = (w["mean_response_chars"] + 900) if w["has_noise_dimension"] else 0
        calls += crit_calls + runs + (runs if w["has_noise_dimension"] else 0)
        tokens_in += (per_crit * crit_calls + pen * runs + noise * runs) / CHARS_PER_TOKEN
    out_tokens = calls * 120  # short JSON verdicts
    api = {
        "status": "HYPOTHETICAL - NOT AVAILABLE",
        "why": ("This project has no Anthropic API key and no credits, and spending them is a "
                "hard rule violation rather than a cost trade-off. Every published MondayBench "
                "evaluation used route=recorded. Costed here only to size the alternative."),
        "judge_calls": int(calls),
        "estimated_input_tokens": int(tokens_in),
        "estimated_output_tokens": int(out_tokens),
        "assumptions": {"chars_per_token": CHARS_PER_TOKEN,
                        "ground_truth_slice_fraction": 0.15,
                        "output_tokens_per_call": 120,
                        "no_historical_judge_token_data": True,
                        "why_no_data": ("JudgeRecord stores no token counts, and no evaluation "
                                        "was ever produced through the API route, so there is "
                                        "nothing historical to calibrate against.")},
    }
    # Opus 5 list pricing is not asserted from the repo; a range is given instead.
    for lo, hi, label in [(5.0, 15.0, "usd_per_million_input_output_low_high")]:
        api["estimated_cost_usd_range"] = {
            "note": ("input x $" + str(lo) + "/M and output x $" + str(hi) + "/M, the common "
                     "frontier band. The repo pins no Opus 5 price, so this is a band, not a quote."),
            "low": round(tokens_in / 1e6 * lo + out_tokens / 1e6 * hi, 2),
            "high": round(tokens_in / 1e6 * (lo * 2) + out_tokens / 1e6 * (hi * 2), 2),
        }
    inv["route_api_judge"] = api

    # ---- route 2: the recorded judge (the only permitted one) --------------
    total_criteria = sum(work[s]["criteria"] * work[s]["responses_counted"] for s in SCENARIOS)
    total_runs = sum(work[s]["responses_counted"] for s in SCENARIOS)
    read_chars = 0
    for sid in SCENARIOS:
        w = work[sid]
        # a session must read each response once, plus the rubric, the judge
        # prompt and the answer key once per scenario
        read_chars += w["mean_response_chars"] * w["responses_counted"]
        read_chars += w["source_material_chars"] + w["ground_truth_chars"] + w["criterion_definition_chars"]
    inv["route_recorded_judge"] = {
        "status": "THE ONLY PERMITTED ROUTE",
        "what_it_is": ("Claude Opus 5 reading each response against the rubric in an interactive "
                       "session and writing one labelled verdict per criterion, replayed with "
                       "`evaluate --verdicts`. The budget item is supervised session time, not "
                       "API tokens."),
        "criterion_verdicts_to_produce": total_criteria,
        "noise_verdicts": sum(work[s]["responses_counted"] for s in SCENARIOS
                              if work[s]["has_noise_dimension"]),
        "penalty_verdicts": total_runs,
        "total_verdict_records": total_criteria + total_runs
                                 + sum(work[s]["responses_counted"] for s in SCENARIOS
                                       if work[s]["has_noise_dimension"]),
        "material_to_read_chars": read_chars,
        "material_to_read_tokens_estimate": int(read_chars / CHARS_PER_TOKEN),
        "comparison_point": ("The GLM 5.3 campaign produced 354 criterion verdicts for one model "
                             "across the five scenarios. A full re-judge is that work times eight."),
    }

    # ---- the alternative that needs no judging at all -----------------------
    inv["route_rescore_only"] = {
        "what_it_is": ("Replay the EXISTING recorded verdict files under a new evaluator id. The "
                       "labels do not change, so no judging happens and no score moves; what "
                       "changes is that each new evaluation carries the scenario-specific "
                       "contract fingerprint."),
        "judge_calls": 0,
        "criterion_verdicts_to_produce": 0,
        "estimated_cost_usd": 0.0,
        "verdict_files_reused": sorted(
            str(p.relative_to(ROOT)).replace("\\", "/") for p in
            list((ROOT / "verdicts").glob("*.jsonl")) + list((ROOT / "verdicts").glob("*/*.jsonl"))),
        "caveat": ("It re-stamps rather than re-derives. It fixes the fingerprint defect and "
                   "nothing else: cross-session judging drift, which the fingerprint never "
                   "captured, stays exactly as it is in v1.0."),
    }

    inv["provisional_models_out_of_scope"] = {
        "models": PROVISIONAL,
        "why": ("Their generations did not come through the official provider route - Opus 5 and "
                "Fable 5.1 are reachable only from the Claude Code subscription, whose system "
                "prompt and injected context are not the frozen ones (see "
                "audits/monday-002/fable-5.1-preflight.md). Re-judging them under v1.1 would "
                "make their EVALUATION comparable while their GENERATION still is not."),
        "if_wanted_later": ("Judge them under the same v1.1 contract but publish them in a "
                            "separate experimental namespace, never inside the official board."),
    }

    (HERE / "rejudge-inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print("%-18s %9s %8s %8s %10s %7s" % ("model", "scenarios", "on disk", "judged",
                                          "raw avail", "regen?"))
    for r in inv["rows"]:
        print("%-18s %9d %8d %8d %10s %7s" % (
            r["model"], r["scenarios"], r["runs_on_disk"], r["responses"],
            "yes" if r["raw_output_available"] else "NO", "no"))
    print("\ntotal official responses: " + str(inv["total_official_responses"])
          + "   available: " + str(inv["total_responses_available"])
          + "   regeneration required: " + str(inv["regeneration_required"]))
    print("blockers: " + (", ".join(inv["blockers"]) if inv["blockers"] else "none"))
    print("\nfull re-judge (recorded route): "
          + str(inv["route_recorded_judge"]["criterion_verdicts_to_produce"])
          + " criterion verdicts, "
          + str(inv["route_recorded_judge"]["total_verdict_records"]) + " verdict records")
    print("same work through the API route (forbidden here): "
          + str(api["judge_calls"]) + " calls, ~"
          + f"{api['estimated_input_tokens']:,}" + " in / ~"
          + f"{api['estimated_output_tokens']:,}" + " out tokens, $"
          + str(api["estimated_cost_usd_range"]["low"]) + "-"
          + str(api["estimated_cost_usd_range"]["high"]))
    print("re-score only (no judging): 0 calls, $0")


if __name__ == "__main__":
    main()
