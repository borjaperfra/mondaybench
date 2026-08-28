"""Audit artefacts for the monday-002 official battery.

Writes `criterion-matrix.md` and `analysis.md` next to the published
leaderboard. Reads only what the harness already produced - the leaderboard
payload, the evaluations and the raw runs - and computes nothing that is not
derivable from them. Nothing here scores anything.

Run after `mondaybench publish --scenario monday-002 --evaluator evaluator-opus5-v0.2`.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCENARIO = "monday-002"
EVALUATOR = "evaluator-opus5-v0.2"
OUT = ROOT / "leaderboard" / SCENARIO
EVAL_DIR = ROOT / "evaluations" / EVALUATOR / SCENARIO
RUN_DIR = ROOT / "runs" / SCENARIO

SYM = {"PASS": "P", "PARTIAL": "~", "FAIL": "F"}
VALUE = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0}

# Calibration reference points, for the "did the redesign hold up" comparison.
CALIBRATION = {
    "v0.1 calibration (4 models, 21 criteria)": 75.5,
    "v0.2 calibration (4 models, 20 criteria)": 37.0,
}

# Each story is a rubric criterion plus the plain-English failure it represents.
# The script supplies the models and the recorded evidence; it never writes a
# narrative the evaluations do not support.
STORIES = [
    ("choose_option_b", "Picked the riskier release path"),
    ("schedule_feasibility", "Lost the asynchronous delta review"),
    ("option_b_sequence", "Broke the release dependency chain"),
    ("expansion_fully_reconciled", "Left the €54k gap open"),
    ("avoid_acme_false_positive", "Read Acme's explained decline as churn"),
    ("no_unsupported_causality", "Invented a cause the sources do not establish"),
    ("orion_missing_evidence", "Settled Orion without the evidence to settle it"),
    ("conditional_launch_timing", "Turned an estimate into an external promise"),
]


def load():
    payload = json.loads((OUT / "leaderboard.json").read_text(encoding="utf-8"))
    rows = payload["models"]
    order = [r["model_slug"] for r in rows]
    names = {r["model_slug"]: r["display_name"] for r in rows}

    # Follow the leaderboard's own provenance rather than globbing the
    # directories. An evaluation can exist on disk for a run that no longer
    # qualifies - monday-002/qwen3.8-flash/run-002 is exactly that - and it must
    # not reach the matrices or the analysis any more than it reaches the mean.
    evals: dict[str, list[dict]] = {}
    runs: dict[str, list[dict]] = {}
    for row in rows:
        slug = row["model_slug"]
        prov = row["provenance"]
        evals[slug] = [
            json.loads((ROOT / rel).read_text(encoding="utf-8")) for rel in prov["evaluations"]
        ]
        runs[slug] = [
            json.loads((ROOT / rel).read_text(encoding="utf-8")) for rel in prov["runs"]
        ]
    return payload, rows, order, names, evals, runs


def criteria_order(evals) -> list[str]:
    first = next(iter(evals.values()))[0]
    return list(first["criteria"])


def points_map(evals) -> dict[str, float]:
    first = next(iter(evals.values()))[0]
    return {cid: c["points_possible"] for cid, c in first["criteria"].items()}


def dimension_of() -> dict[str, str]:
    import yaml

    raw = yaml.safe_load(
        (ROOT / "scenarios" / SCENARIO / "rubric.yaml").read_text(encoding="utf-8")
    )
    return {
        c["id"]: dim
        for dim, body in raw["dimensions"].items()
        for c in body["criteria"]
    }


def pattern(labels: list[str]) -> str:
    """`3P`, `2P + 1~`, ... - the shape of a model's three runs on one criterion."""
    parts = [f"{labels.count(k)}{SYM[k]}" for k in ("PASS", "PARTIAL", "FAIL") if labels.count(k)]
    return " + ".join(parts)


def write_matrix(order, names, evals, cids, pts):
    L = {
        slug: {cid: [e["criteria"][cid]["result"] for e in evals[slug]] for cid in cids}
        for slug in order
    }
    lines = [
        f"# monday-002 — criterion matrix ({EVALUATOR}, rubric 0.2)",
        "",
        "Every criterion, every model, all three official runs. `P` = PASS, "
        "`~` = PARTIAL, `F` = FAIL.",
        "",
        "## A. Summary — the shape of each model's three runs",
        "",
    ]
    head = "| # | Criterion | Points | " + " | ".join(names[s] for s in order) + " |"
    lines += [head, "|---:|---|---:|" + "---|" * len(order)]
    for i, cid in enumerate(cids, 1):
        cells = " | ".join(pattern(L[s][cid]) for s in order)
        lines.append(f"| {i} | `{cid}` | {pts[cid]:g} | {cells} |")

    lines += ["", "## B. Full per-run matrix", ""]
    cols = [f"{names[s]} r{n}" for s in order for n in (1, 2, 3)]
    lines += [
        "| # | Criterion | Points | " + " | ".join(cols) + " |",
        "|---:|---|---:|" + "---|" * len(cols),
    ]
    for i, cid in enumerate(cids, 1):
        cells = " | ".join(SYM[L[s][cid][n]] for s in order for n in range(3))
        lines.append(f"| {i} | `{cid}` | {pts[cid]:g} | {cells} |")

    (OUT / "criterion-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return L


def write_analysis(payload, rows, order, names, evals, runs, cids, pts, L):
    dim_of = dimension_of()
    dims = list(rows[0]["dimensions"])

    # Constant criteria: identical label in every run of every model.
    constant = [cid for cid in cids if len({x for s in order for x in L[s][cid]}) == 1]
    const_pts = sum(pts[c] for c in constant)

    # Modal-constant: every model lands on the same *majority* label, without
    # every run agreeing. A criterion where a model's three runs are all
    # different has no majority and therefore no mode - picking one would be
    # arbitrary, and `max(set(...), key=count)` picked a different one on every
    # process because set iteration order is not stable.
    def majority(labels: list[str]) -> str | None:
        best = max(set(labels), key=lambda x: (labels.count(x), x))
        return best if labels.count(best) * 2 > len(labels) else None

    modal_constant = [
        cid
        for cid in cids
        if cid not in constant
        and None not in (modes := {majority(L[s][cid]) for s in order})
        and len(modes) == 1
    ]

    # Dispersion: spread of earned points across models, on a criterion.
    def earned(slug, cid):
        return pts[cid] * statistics.mean(VALUE[x] for x in L[slug][cid])

    dispersion = sorted(
        ((max(earned(s, c) for s in order) - min(earned(s, c) for s in order), c) for c in cids),
        reverse=True,
    )

    lines = [
        f"# MondayBench #002 — Moving Targets: official analysis",
        "",
        f"Scenario `{SCENARIO}` v{payload['rubric_version']} · evaluator `{EVALUATOR}` · "
        f"judge `{rows[0]['provenance']['judge_model_id']}` · "
        f"prompt `{payload['frozen_prompt_sha256'][:16]}…`",
        "",
        f"Seven models, three official runs each ({sum(r['score']['runs'] for r in rows)} runs). "
        "Monday Score is the mean of the three. Quality, speed and cost are reported "
        "separately and never combined.",
        "",
        "## Ranking",
        "",
        "| # | Model | Monday Score | Runs | Min | Max | Range | Stddev |",
        "|---:|---|---:|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        sc = r["score"]
        runs_txt = " / ".join(f"{v:.1f}" for v in r["run_scores"])
        lines.append(
            f"| {r['rank']} | {r['display_name']} | **{sc['mean']:.1f}** | {runs_txt} | "
            f"{sc['min']:.1f} | {sc['max']:.1f} | {sc['range']:.1f} | {sc['stddev']:.2f} |"
        )

    means = [r["score"]["mean"] for r in rows]
    lines += [
        "",
        f"Spread {min(means):.1f} – {max(means):.1f} = **{max(means)-min(means):.1f} points**.",
        "",
        "## Consistency",
        "",
        "| Model | Range | Stddev |",
        "|---|---:|---:|",
    ]
    by_stability = sorted(rows, key=lambda r: (r["score"]["stddev"], r["score"]["range"]))
    for r in by_stability:
        lines.append(
            f"| {r['display_name']} | {r['score']['range']:.1f} | {r['score']['stddev']:.2f} |"
        )
    lines += [
        "",
        f"Most consistent: **{by_stability[0]['display_name']}** "
        f"(range {by_stability[0]['score']['range']:.1f}). "
        f"Least: **{by_stability[-1]['display_name']}** "
        f"(range {by_stability[-1]['score']['range']:.1f}).",
        "",
        "## Constant criteria",
        "",
        f"**{len(constant)} of {len(cids)} criteria return the same label in all "
        f"{sum(r['score']['runs'] for r in rows)} runs, worth {const_pts:.1f} of 100 points.** "
        f"{100 - const_pts:.1f} points discriminate.",
        "",
        "| Reference | Constant point mass |",
        "|---|---:|",
    ]
    for k, v in CALIBRATION.items():
        lines.append(f"| {k} | {v:.1f} |")
    lines.append(
        f"| **v0.2 official (7 models, 20 criteria)** | **{const_pts:.1f}** |"
    )
    lines += ["", "Constant across every run:", ""]
    for cid in constant:
        label = L[order[0]][cid][0]
        lines.append(f"- `{cid}` ({pts[cid]:g} pts) — always {label}")
    if not constant:
        lines.append("- none")
    if modal_constant:
        lines += [
            "",
            "Same modal label for every model, but not identical in every run "
            "(these move with run-to-run variance rather than with capability):",
            "",
        ]
        for cid in modal_constant:
            lines.append(f"- `{cid}` ({pts[cid]:g} pts)")

    lines += [
        "",
        "## Most discriminative criteria",
        "",
        "Gap between the best and worst model's mean earned points on that criterion.",
        "",
        "| Criterion | Points | Spread | Dimension |",
        "|---|---:|---:|---|",
    ]
    for gap, cid in dispersion[:8]:
        lines.append(f"| `{cid}` | {pts[cid]:g} | {gap:.2f} | {dim_of[cid]} |")

    lines += ["", "## Dimension leaders", "", "| Dimension | Max | Leader | Score |", "|---|---:|---|---:|"]
    dim_max = {}
    for cid, dname in dim_of.items():
        dim_max[dname] = dim_max.get(dname, 0) + pts[cid]
    for d in dims:
        top = max(r["dimensions"][d] for r in rows)
        winners = [r["display_name"] for r in rows if r["dimensions"][d] == top]
        lines.append(
            f"| {d} | {dim_max[d]:g} | {', '.join(winners)} | {top:.1f} |"
        )

    lines += ["", "## Failure stories", "",
              "Each entry is a rubric criterion a model missed, quoted from the recorded "
              "evaluation evidence. Nothing here is inferred beyond the labels.", ""]
    for cid, title in STORIES:
        misses = []
        for slug in order:
            for n, e in enumerate(evals[slug], 1):
                c = e["criteria"][cid]
                if c["result"] != "PASS":
                    misses.append((names[slug], n, c["result"], c["evidence"]))
        if not misses:
            lines += [f"### {title}", "", f"`{cid}` — no model missed this.", ""]
            continue
        lines += [f"### {title}", "", f"`{cid}` ({pts[cid]:g} pts) — {len(misses)} miss(es).", ""]
        for name, n, result, evidence in misses[:6]:
            lines.append(f"- **{name} run {n}** ({result}): {evidence}")
        if len(misses) > 6:
            lines.append(f"- …and {len(misses)-6} more; see `criterion-matrix.md`.")
        lines.append("")

    lines += ["## Penalties", "", "| Model | Run | Type | Points | Evidence |", "|---|---:|---|---:|---|"]
    any_pen = False
    for slug in order:
        for n, e in enumerate(evals[slug], 1):
            for item in (e.get("penalties") or {}).get("items") or []:
                any_pen = True
                ev = item.get("evidence", "").replace("|", "\\|")
                lines.append(
                    f"| {names[slug]} | {n} | {item['type']} | {item['points']:+.0f} | {ev} |"
                )
    if not any_pen:
        lines.append("| — | — | none | 0 | — |")

    lines += [
        "",
        "## Speed and cost",
        "",
        "Reported separately from quality. No combined efficiency score exists, "
        "by design.",
        "",
        "| Model | TTFA median | Total latency median | Output tokens median | Cost median |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        perf = r["performance"]
        econ = r["economics"]

        def ms(v):
            return "-" if v is None else f"{v / 1000:.1f}s"

        tokens = perf.get("median_output_tokens")
        cost = econ.get("median_cost_usd")
        lines.append(
            f"| {r['display_name']} | {ms(perf.get('median_ttfa_ms'))} | "
            f"{ms(perf.get('median_total_latency_ms'))} | "
            f"{'-' if tokens is None else format(tokens, '.0f')} | "
            f"{'-' if cost is None else '$' + format(cost, '.4f')} |"
        )

    lines += [
        "",
        "## Not yet: an Overall Monday Score",
        "",
        "Two scenarios is not a benchmark suite. #001 and #002 measure overlapping "
        "but different things, and averaging two numbers would imply a weighting "
        "nobody has argued for. The per-scenario results are published in a shape "
        "that can be aggregated later; no aggregate is published now.",
        "",
    ]
    (OUT / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    payload, rows, order, names, evals, runs = load()
    cids = criteria_order(evals)
    pts = points_map(evals)
    L = write_matrix(order, names, evals, cids, pts)
    write_analysis(payload, rows, order, names, evals, runs, cids, pts, L)
    print(f"wrote {OUT / 'criterion-matrix.md'}")
    print(f"wrote {OUT / 'analysis.md'}")


if __name__ == "__main__":
    main()
