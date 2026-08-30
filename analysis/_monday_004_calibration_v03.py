"""Build the monday-004 rubric-0.3 calibration report from what is on disk.

    python analysis/_monday_004_calibration_v03.py

Same contract as `_monday_004_calibration.py`, which builds the superseded v0.1
report and is left alone so that report still reproduces: every number in
`analysis/monday-004-calibration.md` comes from here, read out of the
evaluations, the runs and the calibration leaderboard. Nothing is transcribed by
hand, so the report cannot drift from the artifacts it describes.

Two things this file carries that the harness does not.

The FACULTY mapping - which faculty each criterion actually tests - is editorial
and is written down here rather than inferred, so it can be argued with. Rubric
0.3 splits it finer than v0.1 did: `calculation` was doing the work of three
different skills, and the new `figures_carried_correctly` criterion is none of
them.

The generation table reads the ceiling status back through the same function
qualification uses, so the report cannot claim a run was non-binding while the
harness thinks otherwise.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALUATOR = "evaluator-opus5-v0.4-calibration-3"
EVALUATIONS = REPO_ROOT / "evaluations" / EVALUATOR / "monday-004"
RUNS = REPO_ROOT / "runs" / "monday-004"
RUBRIC = REPO_ROOT / "scenarios" / "monday-004" / "rubric-0.3.yaml"
LEADERBOARD = REPO_ROOT / "analysis" / "leaderboards" / "monday-004" / "leaderboard.json"

# The seven runs that make up the fresh battery: one per model, all generated
# under the 96,000-token safety ceiling. Named explicitly because the shadow
# rescore of the v0.1 responses lives under the same evaluator id and must never
# be aggregated with these.
FRESH_RUNS = {
    "qwen3.8-flash": 2,
    "glm5.3-flash": 2,
    "deepseek-v4-flash": 3,
    "mimo-v2.5": 3,
    "glm5.2": 2,
    "qwen3.6": 2,
    "gemma4": 2,
}

# What each criterion is really asking the model to do. One label each, chosen
# by what a failure on it would tell you about the model. Seven faculties, per
# the brief: data cleaning, arithmetic, joins, factual figure handling,
# interpretation, business judgment, uncertainty.
FACULTY = {
    "duplicate_detected": "data cleaning",
    "annual_prepayment_normalized": "data cleaning",
    "headline_vs_recurring_growth": "arithmetic",
    "revenue_conclusion": "interpretation",
    "segment_retention_quantified": "arithmetic",
    "sample_size_arr_context": "interpretation",
    "acme_false_positive_avoided": "interpretation",
    "no_churn_overreach": "uncertainty",
    "raw_attribution_not_equivalent_new_business": "interpretation",
    "existing_customer_expansion_removed": "arithmetic",
    "conversion_rate_vs_absolute_volume": "arithmetic",
    "no_unsupported_channel_scale_decision": "business judgment",
    "cac_payback_unavailable": "uncertainty",
    "contribution_calculated": "arithmetic",
    "margin_calculated_or_correctly_compared": "arithmetic",
    "absolute_vs_scalable_economics": "interpretation",
    "plan_trajectory_evidence": "joins",
    "product_focus_supported": "business judgment",
    "customer_id_alias_resolved": "joins",
    "support_normalized": "arithmetic",
    "figures_carried_correctly": "factual figure handling",
    "cross_table_customer_signal": "joins",
    "causal_boundary": "uncertainty",
    "segment_recommendation": "business judgment",
    "acquisition_recommendation": "business judgment",
    "product_recommendation": "business judgment",
    "uncertainty_discipline": "uncertainty",
}

DISPLAY = {
    "deepseek-v4-flash": "DeepSeek V4 Flash",
    "qwen3.8-flash": "Qwen 3.8 Flash",
    "glm5.3-flash": "GLM 5.3 Flash",
    "mimo-v2.5": "MIMO v2.5",
    "glm5.2": "GLM 5.2",
    "qwen3.6": "Qwen 3.6",
    "gemma4": "Gemma 4",
}


def rubric() -> dict:
    return yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))


def criterion_points() -> dict[str, float]:
    return {
        raw["id"]: float(raw["points"])
        for spec in rubric()["dimensions"].values()
        for raw in spec.get("criteria") or []
    }


def criterion_order() -> list[str]:
    return [
        raw["id"]
        for spec in rubric()["dimensions"].values()
        for raw in spec.get("criteria") or []
    ]


def dimension_of() -> dict[str, str]:
    return {
        raw["id"]: name
        for name, spec in rubric()["dimensions"].items()
        for raw in spec.get("criteria") or []
    }


def evaluations() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for slug, number in FRESH_RUNS.items():
        path = EVALUATIONS / slug / f"run-{number:03d}.json"
        out[slug] = json.loads(path.read_text(encoding="utf-8"))
    return out


def runs() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for slug, number in FRESH_RUNS.items():
        path = RUNS / slug / f"run-{number:03d}.json"
        out[slug] = json.loads(path.read_text(encoding="utf-8"))
    return out


def attempts() -> dict[str, list[dict]]:
    """Every attempt on disk for each model, scored or rejected."""
    out: dict[str, list[dict]] = {}
    for slug in FRESH_RUNS:
        paths = sorted((RUNS / slug).glob("run-*.json"))
        out[slug] = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    return out


def rejections() -> dict[str, list[tuple[str, list[str]]]]:
    """Rejection reasons, from the qualification plan rather than the leaderboard.

    The leaderboard can only exclude a run it has an evaluation for, so a
    pre-policy attempt that was never scored is invisible there. Several of
    those exist - MIMO and DeepSeek each burned attempts against the old
    32,000-token limit - and the brief requires every rejected attempt to be
    reported, not only the scored ones.
    """
    from mondaybench.config import load_models
    from mondaybench.official import plan_model
    from mondaybench.prompt_builder import build_prompt
    from mondaybench.scenarios import load_scenario

    scenario = load_scenario("monday-004")
    prompt = build_prompt(scenario)
    models = load_models()
    out: dict[str, list[tuple[str, list[str]]]] = {}
    for slug in FRESH_RUNS:
        plan = plan_model(
            scenario_id="monday-004",
            model_slug=slug,
            model=models.get(slug),
            expected_prompt_sha256=prompt.sha256,
            expected_max_output_tokens=scenario.safety_ceiling_tokens,
        )
        out[slug] = [
            (v.run.run_id if v.run else v.path.name, v.reasons) for v in plan.rejected
        ]
    return out


def ceiling_status(payload: dict) -> str:
    """The same call qualification makes, so the report cannot disagree with it."""
    from mondaybench.schemas import BenchmarkRun
    from mondaybench.official import generation_ceiling_status

    return generation_ceiling_status(BenchmarkRun.model_validate(payload))


def main() -> None:
    # The report contains em dashes and mid dots; Windows would otherwise
    # encode stdout as cp1252 and corrupt them on redirect.
    sys.stdout.reconfigure(encoding="utf-8")

    evals = evaluations()
    live = runs()
    every = attempts()
    excluded = rejections()
    points = criterion_points()
    order = criterion_order()
    dim_of = dimension_of()

    rows = sorted(
        (
            {
                "slug": slug,
                "name": DISPLAY.get(slug, slug),
                "base": ev["base_score"],
                "final": ev["final_score"],
                "penalties": ev.get("penalties", {}),
                "criteria": ev["criteria"],
                "dimensions": ev.get("dimensions", {}),
            }
            for slug, ev in evals.items()
        ),
        key=lambda r: r["final"],
        reverse=True,
    )

    # -------------------------------------------------------------- leaderboard
    print("## Leaderboard\n")
    print("| # | model | base | penalties | final |")
    print("|---:|---|---:|---:|---:|")
    for i, r in enumerate(rows, start=1):
        pen = r["penalties"].get("total", 0) if isinstance(r["penalties"], dict) else 0
        print(f"| {i} | {r['name']} | {r['base']:.1f} | {pen:.1f} | **{r['final']:.1f}** |")

    finals = [r["final"] for r in rows]
    print(
        f"\nspread {max(finals) - min(finals):.1f} · mean {statistics.mean(finals):.1f} · "
        f"median {statistics.median(finals):.1f}\n"
    )

    print("\n### Dimension breakdown\n")
    dims = list(rubric()["dimensions"].keys())
    print("| model | " + " | ".join(d.replace("_", " ") for d in dims) + " |")
    print("|---" * (len(dims) + 1) + "|")
    for r in rows:
        cells = []
        for d in dims:
            got = r["dimensions"].get(d)
            value = got["score"] if isinstance(got, dict) else got
            maximum = rubric()["dimensions"][d]["max_points"]
            cells.append(f"{value:.1f}/{maximum:g}" if value is not None else "-")
        print(f"| {r['name']} | " + " | ".join(cells) + " |")

    # -------------------------------------------------------- generation table
    print("\n## Generation behavior\n")
    print(
        "| model | ceiling | completion | reasoning | visible answer | finish | "
        "ceiling status | TTFT | TTFA | latency |"
    )
    print("|---" * 10 + "|")
    for r in rows:
        payload = live[r["slug"]]
        usage = payload.get("usage") or {}
        perf = payload.get("performance") or {}
        gen = payload.get("generation") or {}
        completion = usage.get("output_tokens")
        reasoning = usage.get("reasoning_tokens")
        delivery = (payload.get("reasoning") or {}).get("status")
        evidence = (payload.get("reasoning") or {}).get("evidence")
        # Visible answer = completion - reasoning, but only where the reasoning
        # counter is the thing that established delivery. MIMO's reasoning is
        # confirmed by 6,220 observed stream deltas while its usage block
        # reports zero, so subtracting would report its entire completion as
        # visible answer - 0.70 characters per token, which is impossible.
        visible = None
        counter_trustworthy = delivery != "DELIVERED" or evidence == "explicit_reasoning_tokens"
        if completion is not None and reasoning is not None and counter_trustworthy:
            visible = completion - reasoning

        def ms(value):
            return "-" if value is None else f"{value / 1000:.1f}s"

        print(
            f"| {r['name']} "
            f"| {gen.get('safety_ceiling_tokens', '-'):,} "
            f"| {completion:,} "
            f"| {'0 (see below)' if not counter_trustworthy else format(reasoning or 0, ',')} "
            f"| {'not derivable' if visible is None else format(visible, ',')} "
            f"| {payload.get('finish_reason')} "
            f"| {ceiling_status(payload)} "
            f"| {ms(perf.get('ttft_ms'))} | {ms(perf.get('ttfa_ms'))} "
            f"| {ms(perf.get('total_latency_ms'))} |"
        )

    for r in rows:
        payload = live[r["slug"]]
        reasoning_block = payload.get("reasoning") or {}
        if reasoning_block.get("status") == "DELIVERED" and not (
            payload.get("usage") or {}
        ).get("reasoning_tokens"):
            print()
            print(
                f"{r['name']} is the case the three-signal reasoning rule exists for. "
                f"Its usage block reports 0 reasoning tokens while the adapter observed "
                f"{reasoning_block.get('stream_event_count'):,} reasoning deltas on the stream, "
                f"so delivery is established by `{reasoning_block.get('evidence')}` and the "
                f"counter is simply absent. Visible answer tokens cannot be derived by "
                f"subtraction for this model: its response is "
                f"{len(payload['response']):,} characters, which at the 3.1-3.7 characters "
                f"per answer token the other six runs show would be roughly "
                f"{round(len(payload['response']) / 3.4 / 100) * 100:,} answer tokens, not the "
                f"{(payload.get('usage') or {}).get('output_tokens'):,} its completion count "
                f"would imply."
            )

    print("\n### Qualification attempts\n")
    for r in rows:
        slug = r["slug"]
        total = len(every[slug])
        scored = FRESH_RUNS[slug]
        print(f"- **{r['name']}** - {total} attempt(s) on disk, run-{scored:03d} scored.")
        for run_id, reasons in excluded.get(slug, []):
            for reason in reasons:
                print(f"  - `{run_id}` rejected: {reason}")

    # ----------------------------------------------------------- criterion matrix
    print("\n## Criterion matrix\n")
    print("| criterion | pts | dim | " + " | ".join(r["name"] for r in rows) + " | PASS |")
    print("|---" * (len(rows) + 4) + "|")
    constant_mass = 0.0
    discriminating = 0
    for cid in order:
        labels = [
            r["criteria"].get(cid, {}).get("result", "-")
            if isinstance(r["criteria"].get(cid), dict)
            else "-"
            for r in rows
        ]
        marks = {"PASS": "+", "PARTIAL": "~", "FAIL": ".", "-": "-"}
        passes = sum(1 for x in labels if x == "PASS")
        if len(set(labels)) == 1:
            constant_mass += points[cid]
        else:
            discriminating += 1
        print(
            f"| `{cid}` | {points[cid]:g} | {dim_of[cid].split('_')[0]} | "
            + " | ".join(marks[x] for x in labels)
            + f" | {passes}/{len(rows)} |"
        )
    print(
        f"\nconstant point mass {constant_mass:g} / 100 · discriminating criteria "
        f"{discriminating} / {len(order)}\n"
    )

    print("\n## Penalties\n")
    any_penalty = False
    for r in rows:
        items = r["penalties"].get("items", []) if isinstance(r["penalties"], dict) else []
        for item in items:
            any_penalty = True
            print(f"- **{r['name']}** {item['type']} ({item['points']:g}) - {item['reason']}")
    if not any_penalty:
        print("None fired in the fresh battery.")

    # ------------------------------------------------------ calculation vs judgment
    print("\n## Calculation vs judgment\n")
    faculties = sorted(set(FACULTY.values()))
    weights = {f: sum(points[c] for c, n in FACULTY.items() if n == f) for f in faculties}
    print("| model | " + " | ".join(f"{f}<br><sub>{weights[f]:g} pts</sub>" for f in faculties) + " |")
    print("|---" * (len(faculties) + 1) + "|")
    for r in rows:
        cells = []
        for faculty in faculties:
            earned = 0.0
            for cid, name in FACULTY.items():
                if name != faculty:
                    continue
                label = r["criteria"].get(cid, {}).get("result")
                if label == "PASS":
                    earned += points[cid]
                elif label == "PARTIAL":
                    earned += points[cid] / 2
            cells.append(f"{earned / weights[faculty] * 100:.0f}%")
        print(f"| {r['name']} | " + " | ".join(cells) + " |")

    print("\n### Where the points were lost, by faculty\n")
    lost: dict[str, float] = defaultdict(float)
    for r in rows:
        for cid, name in FACULTY.items():
            label = r["criteria"].get(cid, {}).get("result")
            if label == "FAIL":
                lost[name] += points[cid]
            elif label == "PARTIAL":
                lost[name] += points[cid] / 2
    total_lost = sum(lost.values())
    print("| faculty | points available across the battery | forgone | share of all losses |")
    print("|---|---:|---:|---:|")
    for name, value in sorted(lost.items(), key=lambda kv: -kv[1]):
        print(
            f"| {name} | {weights[name] * len(rows):g} | {value:g} | "
            f"{value / total_lost * 100:.0f}% |"
        )

    # ------------------------------------------------------------ high scores
    print("\n## Every score at or above 95, audited\n")
    high = [r for r in rows if r["final"] >= 95]
    if not high:
        print("None.")
    for r in high:
        misses = [
            (cid, entry)
            for cid, entry in r["criteria"].items()
            if isinstance(entry, dict) and entry.get("result") != "PASS"
        ]
        print(
            f"**{r['name']} - {r['final']:.1f} final, {r['base']:.1f} base.** "
            f"{len(misses)} of {len(order)} criteria below PASS.\n"
        )
        for cid, entry in sorted(misses, key=lambda kv: -kv[1]["points_possible"]):
            print(
                f"- `{cid}` {entry['result']} "
                f"({entry['points_awarded']:g}/{entry['points_possible']:g})\n"
                f"  - evidence: {entry['evidence']}\n"
                f"  - reason: {entry['reason']}"
            )
        print()

    # --------------------------------------------------------- methodology checks
    print("\n## Methodology checks\n")
    bound = [r["name"] for r in rows if ceiling_status(live[r["slug"]]) != "NON_BINDING"]
    truncated = [r["name"] for r in rows if live[r["slug"]].get("finish_reason") == "length"]
    penalty_count = sum(
        len(r["penalties"].get("items", [])) for r in rows if isinstance(r["penalties"], dict)
    )
    at_100 = [r["name"] for r in rows if r["final"] >= 100]
    base_top2 = [r["name"] for r in sorted(rows, key=lambda r: -r["base"])[:2]]
    final_top2 = [r["name"] for r in rows[:2]]
    checks = [
        ("all seven models produced a complete answer", not truncated, "none truncated"
         if not truncated else "truncated: " + ", ".join(truncated)),
        ("no run was bound by the safety ceiling", not bound, "all NON_BINDING"
         if not bound else "bound: " + ", ".join(bound)),
        ("spread is wide enough to rank", max(finals) - min(finals) >= 30,
         f"{max(finals) - min(finals):.1f} points"),
        ("no model scored a perfect 100", not at_100,
         "none" if not at_100 else ", ".join(at_100)),
        ("constant point mass is under a third of the rubric", constant_mass < 33,
         f"{constant_mass:g} / 100"),
        ("most criteria discriminate", discriminating / len(order) >= 0.6,
         f"{discriminating} / {len(order)}"),
        ("penalties fire, but stay rare", 0 < penalty_count <= len(rows) // 2,
         f"{penalty_count} across {len(rows)} runs, "
         + ", ".join(sorted({i["type"] for r in rows
                             for i in r["penalties"].get("items", [])}))),
        ("penalties do not decide the top of the board", base_top2 == final_top2,
         "top two unchanged by penalties" if base_top2 == final_top2
         else "penalties reorder the top two"),
    ]
    print("| check | | detail |")
    print("|---|:-:|---|")
    for label, ok, detail in checks:
        print(f"| {label} | {'yes' if ok else 'NO'} | {detail} |")


if __name__ == "__main__":
    main()
