"""Build the monday-004 v0.1 calibration report from the evaluations on disk.

Everything in `analysis/monday-004-calibration.md` that is a number comes from
here. Nothing is transcribed by hand, so the report cannot drift from the
evaluations it describes.

    python analysis/_monday_004_calibration.py

The one thing this file carries that the harness does not is the
CALCULATION VS JUDGMENT mapping: which faculty each criterion actually tests.
monday-004 exists to say *why* a model failed, not only how far it got, and that
requires a stated view of what each criterion is measuring. The mapping is
editorial and is written down here rather than inferred, so it can be argued
with.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALUATIONS = REPO_ROOT / "evaluations" / "evaluator-opus5-v0.4-calibration" / "monday-004"
RUNS = REPO_ROOT / "runs" / "monday-004"
RUBRIC = REPO_ROOT / "scenarios" / "monday-004" / "rubric.yaml"

# What each criterion is really asking the model to do. One label each, chosen
# by what a failure on it would tell you about the model.
FACULTY = {
    "duplicate_detected": "data cleaning",
    "annual_prepayment_normalized": "data cleaning",
    "headline_vs_recurring_growth": "calculation",
    "revenue_conclusion": "interpretation",
    "segment_churn_math": "calculation",
    "sample_size_arr_context": "interpretation",
    "acme_false_positive_avoided": "interpretation",
    "no_churn_overreach": "uncertainty",
    "raw_attribution_not_equivalent_new_business": "interpretation",
    "existing_customer_expansion_removed": "calculation",
    "conversion_rate_vs_absolute_volume": "calculation",
    "no_unsupported_channel_scale_decision": "business judgment",
    "cac_payback_unavailable": "uncertainty",
    "contribution_calculated": "calculation",
    "margin_calculated_or_correctly_compared": "calculation",
    "enterprise_revenue_not_margin": "interpretation",
    "product_focus_supported": "business judgment",
    "customer_id_alias_resolved": "table joining",
    "support_normalized": "calculation",
    "cross_table_customer_signal": "table joining",
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


def load_rubric() -> dict:
    return yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))


def criterion_points() -> dict[str, float]:
    out: dict[str, float] = {}
    for _, spec in load_rubric()["dimensions"].items():
        for raw in spec.get("criteria") or []:
            out[raw["id"]] = float(raw["points"])
    return out


def criterion_order() -> list[str]:
    out: list[str] = []
    for _, spec in load_rubric()["dimensions"].items():
        for raw in spec.get("criteria") or []:
            out.append(raw["id"])
    return out


def dimension_of() -> dict[str, str]:
    out: dict[str, str] = {}
    for name, spec in load_rubric()["dimensions"].items():
        for raw in spec.get("criteria") or []:
            out[raw["id"]] = name
    return out


def evaluations() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for model_dir in sorted(EVALUATIONS.iterdir()):
        if not model_dir.is_dir():
            continue
        for path in sorted(model_dir.glob("run-*.json")):
            out[model_dir.name] = json.loads(path.read_text(encoding="utf-8"))
    return out


def run_meta() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for model_dir in sorted(RUNS.iterdir()):
        if not model_dir.is_dir():
            continue
        runs = sorted(model_dir.glob("run-*.json"))
        payloads = [json.loads(p.read_text(encoding="utf-8")) for p in runs]
        # The qualifying run, not the first one: DeepSeek's first attempt was
        # truncated and its second is the one that carries the score.
        qualifying = [p for p in payloads if p.get("finish_reason") != "length"]
        out[model_dir.name] = {
            "attempts": len(runs),
            "rejected": len(payloads) - len(qualifying),
            "payload": qualifying[0] if qualifying else (payloads[0] if payloads else None),
        }
    return out


def main() -> None:
    evals = evaluations()
    meta = run_meta()
    points = criterion_points()
    order = criterion_order()
    dim_of = dimension_of()

    rows = []
    for slug, ev in evals.items():
        rows.append(
            {
                "slug": slug,
                "name": DISPLAY.get(slug, slug),
                "base": ev["base_score"],
                "final": ev["final_score"],
                "penalties": ev.get("penalties", {}),
                "criteria": ev["criteria"],
                "dimensions": ev.get("dimensions", {}),
            }
        )
    rows.sort(key=lambda r: r["final"], reverse=True)

    print("## Score table\n")
    print("| # | model | base | penalties | final | out tok | latency |")
    print("|---:|---|---:|---:|---:|---:|---:|")
    for i, r in enumerate(rows, start=1):
        payload = meta.get(r["slug"], {}).get("payload") or {}
        usage = payload.get("usage", {})
        perf = payload.get("performance", {})
        pen = r["penalties"].get("total", 0) if isinstance(r["penalties"], dict) else 0
        print(
            f"| {i} | {r['name']} | {r['base']:.1f} | {pen:.1f} | **{r['final']:.1f}** | "
            f"{usage.get('output_tokens', '-')} | "
            f"{(perf.get('total_latency_ms') or 0) / 1000:.1f}s |"
        )

    finals = [r["final"] for r in rows]
    print(f"\nspread {max(finals) - min(finals):.1f}  mean {statistics.mean(finals):.1f}  "
          f"median {statistics.median(finals):.1f}\n")

    print("\n## Dimension breakdown\n")
    dims = list(load_rubric()["dimensions"].keys())
    header = "| model | " + " | ".join(d.replace("_", " ") for d in dims) + " |"
    print(header)
    print("|---" * (len(dims) + 1) + "|")
    for r in rows:
        cells = []
        for d in dims:
            got = r["dimensions"].get(d)
            value = got["score"] if isinstance(got, dict) else got
            maximum = load_rubric()["dimensions"][d]["max_points"]
            cells.append(f"{value:.1f}/{maximum:g}" if value is not None else "-")
        print(f"| {r['name']} | " + " | ".join(cells) + " |")

    print("\n## Criterion matrix\n")
    print("| criterion | pts | dim | " + " | ".join(r["name"] for r in rows) + " | PASS |")
    print("|---" * (len(rows) + 4) + "|")
    constant_mass = 0.0
    discriminating = 0
    for cid in order:
        labels = []
        for r in rows:
            entry = r["criteria"].get(cid, {})
            labels.append(entry.get("result", "-") if isinstance(entry, dict) else "-")
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
    print(f"\nconstant point mass {constant_mass:g} / 100 · discriminating criteria "
          f"{discriminating} / {len(order)}\n")

    print("\n## Penalties\n")
    any_penalty = False
    for r in rows:
        items = r["penalties"].get("items", []) if isinstance(r["penalties"], dict) else []
        for item in items:
            any_penalty = True
            print(f"- **{r['name']}** {item['type']} ({item['points']:g}) - {item['reason']}")
    if not any_penalty:
        print("None.")

    print("\n## Calculation vs judgment\n")
    faculties = sorted(set(FACULTY.values()))
    print("| model | " + " | ".join(faculties) + " |")
    print("|---" * (len(faculties) + 1) + "|")
    for r in rows:
        cells = []
        for faculty in faculties:
            earned = 0.0
            possible = 0.0
            for cid, name in FACULTY.items():
                if name != faculty:
                    continue
                possible += points[cid]
                entry = r["criteria"].get(cid, {})
                label = entry.get("result") if isinstance(entry, dict) else None
                if label == "PASS":
                    earned += points[cid]
                elif label == "PARTIAL":
                    earned += points[cid] / 2
            cells.append(f"{earned / possible * 100:.0f}%")
        print(f"| {r['name']} | " + " | ".join(cells) + " |")

    print("\n### Where the points were lost, by faculty\n")
    lost: dict[str, float] = defaultdict(float)
    for r in rows:
        for cid, name in FACULTY.items():
            entry = r["criteria"].get(cid, {})
            label = entry.get("result") if isinstance(entry, dict) else None
            if label == "FAIL":
                lost[name] += points[cid]
            elif label == "PARTIAL":
                lost[name] += points[cid] / 2
    total_lost = sum(lost.values())
    for name, value in sorted(lost.items(), key=lambda kv: -kv[1]):
        print(f"- {name}: {value:g} points forgone across the battery "
              f"({value / total_lost * 100:.0f}% of all losses)")

    print("\n## Highest scores, audited\n")
    for r in rows[:2]:
        misses = [
            (cid, entry)
            for cid, entry in r["criteria"].items()
            if isinstance(entry, dict) and entry.get("result") != "PASS"
        ]
        print(f"**{r['name']} - {r['final']:.1f} final, {r['base']:.1f} base.** "
              f"{len(misses)} of 25 criteria below PASS.\n")
        for cid, entry in sorted(misses, key=lambda kv: -kv[1]["points_possible"]):
            print(f"- `{cid}` {entry['result']} "
                  f"({entry['points_awarded']:g}/{entry['points_possible']:g}) - "
                  f"{entry['reason']}")
        print()

    print("\n## Qualification attempts\n")
    for slug, info in sorted(meta.items()):
        payload = info["payload"] or {}
        rejected = info.get("rejected", 0)
        note = f", {rejected} rejected (truncated)" if rejected else ""
        print(
            f"- {DISPLAY.get(slug, slug)}: {info['attempts']} attempt(s){note}, "
            f"scored run finish_reason={payload.get('finish_reason')}, "
            f"output_tokens={payload.get('usage', {}).get('output_tokens')}, "
            f"reasoning_tokens={payload.get('usage', {}).get('reasoning_tokens')}"
        )


if __name__ == "__main__":
    main()
