"""Capability profiles for the two PROVISIONAL, off-benchmark models.

Uses the canonical implementation - `mondaybench.capabilities.build_profiles`
with taxonomy v0.2 - and never reimplements the aggregation. This file is only
an ADAPTER: it turns two off-benchmark verdict sets into the same
`{scenario: {model: {criterion: (mean_earned, possible)}}}` shape that
`official_criterion_results` produces for the published models, and hands it to
the canonical builder.

Nothing official is written. Nothing is recalculated for the seven published
models: they are read from `analysis/capability-profiles-v0.2.json` for the
reproduction check and for comparison only.

Guards. The script exits non-zero if:
  * either model's verdict set fails to reproduce its presentation score,
  * any published model fails to reproduce exactly from the canonical builder,
  * the canonical builder emits any warning (an unmapped criterion),
  * a capability percentage falls outside [0, 100].

Usage:  python audits/capabilities/build-provisional-capabilities.py
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from mondaybench.capabilities import (                       # noqa: E402
    build_profiles, load_taxonomy, official_criterion_results, rubric_points,
)
from mondaybench.config import load_yaml                     # noqa: E402
from mondaybench.scenarios import load_scenario              # noqa: E402
from mondaybench.schemas import PenaltyViolation             # noqa: E402
from mondaybench.scoring import build_breakdown              # noqa: E402

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
TAXONOMY_VERSION = "0.2"
PUBLISHED = ROOT / "analysis/capability-profiles-v0.2.json"

FABLE_EXP = ROOT / "experiments/fable-5.1-full-mondaybench"
FABLE_002 = ROOT / "experiments/fable-5.1-date-sensitivity"
OPUS_EXP = ROOT / "experiments/opus-5-full-mondaybench"
BLIND = ROOT / "audits/blind-rejudge"
GPT_JSON = BLIND / "inter-judge/source/independent-blind-rejudge-gpt-5.6-sol.json"

FABLE_PRESENTATION = 94.90
OPUS_PRESENTATION = 97.07
GEMINI_EXP = ROOT / "experiments/gemini-3.8-flash-high-opus-judge"

# The POST-AUDIT corrections, transcribed from the correction table in
# experiments/fable-5.1-full-mondaybench/AUDIT.md section 5. The summary's
# per-run `criteria` dicts hold PRE-AUDIT labels while its `score` fields hold
# the post-audit scores, so the labels have to be corrected here to make the
# two consistent. Every row carries OLD so a wrong starting label is caught
# rather than silently overwritten.
FABLE_CORRECTIONS = [
    ("monday-003", "run2", "factual_plan_accuracy", "PARTIAL", "FAIL"),
    ("monday-003", "run3", "factual_plan_accuracy", "PARTIAL", "FAIL"),
    ("monday-002", "A2", "schedule_feasibility", "PARTIAL", "FAIL"),
    ("monday-002", "A3", "schedule_feasibility", "PARTIAL", "FAIL"),
    ("monday-002", "A1", "ownership_supersession", "PARTIAL", "PASS"),
    ("monday-001", "run1", "friday_conversion_unknown", "PASS", "PARTIAL"),
    ("monday-001", "run3", "friday_conversion_unknown", "PASS", "PARTIAL"),
    ("monday-004", "run1", "figures_carried_correctly", "PASS", "PARTIAL"),
    ("monday-004", "run2", "figures_carried_correctly", "PASS", "PARTIAL"),
    ("monday-004", "run3", "figures_carried_correctly", "PASS", "PARTIAL"),
]

problems: list[str] = []


def official_rubric(scenario_id):
    """The rubric the OFFICIAL EVALUATOR is bound to.

    Not load_scenario's default: monday-001 declares no rubric_file, so the
    default returns the superseded 0.1 rubric while the scenario is frozen
    against rubric-0.2.yaml. Using the default would mis-map monday-001.
    """
    cfg = load_yaml(ROOT / "evaluators" / f"{EVALUATORS[scenario_id]}.yaml")
    return load_scenario(scenario_id, rubric_file=cfg["rubric_file"]).rubric


RUBRICS = {s: official_rubric(s) for s in SCEN}


def score_run(scenario_id, labels, noise_triggered=None, violations=None):
    """Canonical scoring for one run. Returns the harness breakdown."""
    rub = RUBRICS[scenario_id]
    fa = {a.id: (False, None) for a in (rub.noise.false_actions if rub.noise else [])}
    for k in (noise_triggered or []):
        fa[k] = (True, None)
    viol = [PenaltyViolation(
        type=v["type"], evidence=v.get("evidence"), reason=v.get("reason"),
        materially_misleading=v.get("materially_misleading", True))
        for v in (violations or [])]
    cv = {cid: (lbl, None, None) for cid, lbl in labels.items()}
    return build_breakdown(rub, criterion_verdicts=cv, false_actions=fa, violations=viol)


# ---------------------------------------------------------------------------
# Fable 5.1: assemble the POST-AUDIT label set
# ---------------------------------------------------------------------------
fable_summary = json.loads((FABLE_EXP / "five-scenario-summary.json").read_text(encoding="utf-8"))

fable_labels: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
fable_noise: dict[tuple[str, str], list[str]] = {}
fable_penalties: dict[tuple[str, str], list] = {}

for sid in SCEN:
    for run_key, run in fable_summary["scenarios"][sid]["runs"].items():
        if "criteria" in run:
            fable_labels[sid][run_key] = dict(run["criteria"])
        fable_penalties[(sid, run_key)] = (run.get("penalties") or {}).get("applied") or []

# monday-002's criterion verdicts are not in the summary; they live with the
# date-sensitivity experiment. B_NEUTRALIZED is the date-neutralised run and is
# NOT part of the frozen three - it must not enter.
RUN_KEY_002 = {"A_FROZEN": "A1", "A2_FROZEN": "A2", "A3_FROZEN": "A3"}
for path in (FABLE_002 / "verdicts.jsonl", FABLE_002 / "verdicts-A2-A3.jsonl"):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        row = json.loads(line)
        tail = row["run_id"].rsplit("__", 1)[-1]
        if tail not in RUN_KEY_002:
            continue                                  # excludes B_NEUTRALIZED
        run_key = RUN_KEY_002[tail]
        if row.get("kind") == "penalties":
            fable_penalties[("monday-002", run_key)] = row.get("violations") or []
            continue
        fable_labels["monday-002"].setdefault(run_key, {})[row["criterion_id"]] = row["result"]

# Apply the audited corrections.
for sid, run_key, cid, old, new in FABLE_CORRECTIONS:
    have = fable_labels[sid].get(run_key, {}).get(cid)
    if have != old:
        problems.append(f"Fable correction {sid}/{run_key}/{cid}: expected OLD={old}, found {have!r}")
        continue
    fable_labels[sid][run_key][cid] = new

# Verify: every run must reproduce the summary's post-audit score, and the
# overall must reproduce the presentation score.
fable_breakdowns: dict[tuple[str, str], object] = {}
fable_means = []
for sid in SCEN:
    runs = fable_summary["scenarios"][sid]["runs"]
    scores = []
    for run_key in runs:
        labels = fable_labels[sid].get(run_key)
        if not labels:
            problems.append(f"Fable {sid}/{run_key}: no criterion labels found")
            continue
        missing = {c.id for c in RUBRICS[sid].criteria} - set(labels)
        if missing:
            problems.append(f"Fable {sid}/{run_key}: missing criteria {sorted(missing)}")
            continue
        bd = score_run(sid, labels, violations=fable_penalties.get((sid, run_key)))
        fable_breakdowns[(sid, run_key)] = bd
        stored = runs[run_key]["score"]
        if abs(bd.final_score - stored) > 0.005:
            problems.append(f"Fable {sid}/{run_key}: recomputed {bd.final_score} != stored {stored}")
        scores.append(bd.final_score)
    if scores:
        fable_means.append(statistics.mean(scores))

fable_overall = round(statistics.mean(fable_means), 2) if len(fable_means) == 5 else None
if fable_overall is None or abs(fable_overall - FABLE_PRESENTATION) > 0.005:
    problems.append(f"Fable overall recomputed {fable_overall} != {FABLE_PRESENTATION}")

# ---------------------------------------------------------------------------
# Opus 5: the INDEPENDENT BLIND RE-JUDGE label set (same judge as 97.07)
# ---------------------------------------------------------------------------
gpt = json.loads(GPT_JSON.read_text(encoding="utf-8"))
mapping = json.loads((BLIND / "opus-5-blind-rejudge-mapping.json").read_text(encoding="utf-8"))
letter_to_run = {s: {L: mapping["scenarios"][s][L]["run_number"] for L in "ABC"} for s in SCEN}

opus_labels: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
for row in gpt["criterion_verdicts"]:
    sid, L = row["scenario"], row["candidate"]
    run_key = f"run{letter_to_run[sid][L]}"
    opus_labels[sid].setdefault(run_key, {})[row["criterion_id"]] = row["label"]

opus_noise: dict[tuple[str, str], list[str]] = defaultdict(list)
for row in gpt["false_action_verdicts"]:
    sid, L = row["scenario"], row["candidate"]
    run_key = f"run{letter_to_run[sid][L]}"
    if row["triggered"]:
        opus_noise[(sid, run_key)].append(row["false_action_id"])

opus_penalties: dict[tuple[str, str], list] = defaultdict(list)
for row in gpt["penalty_verdicts"]:
    sid, L = row["scenario"], row["candidate"]
    run_key = f"run{letter_to_run[sid][L]}"
    for v in row.get("violations", []):
        opus_penalties[(sid, run_key)].append({
            "type": v["type"],
            "evidence": v.get("evidence"),
            "reason": v.get("short_rationale") or v.get("reason"),
            "materially_misleading": bool(v.get("materially_misleading", True)),
        })

opus_breakdowns: dict[tuple[str, str], object] = {}
opus_means = []
for sid in SCEN:
    scores = []
    for run_key in sorted(opus_labels[sid]):
        labels = opus_labels[sid][run_key]
        missing = {c.id for c in RUBRICS[sid].criteria} - set(labels)
        if missing:
            problems.append(f"Opus {sid}/{run_key}: missing criteria {sorted(missing)}")
            continue
        bd = score_run(sid, labels,
                       noise_triggered=opus_noise.get((sid, run_key)),
                       violations=opus_penalties.get((sid, run_key)))
        opus_breakdowns[(sid, run_key)] = bd
        scores.append(bd.final_score)
    if len(scores) != 3:
        problems.append(f"Opus {sid}: {len(scores)} runs, expected 3")
    if scores:
        opus_means.append(statistics.mean(scores))

opus_overall = round(statistics.mean(opus_means), 2) if len(opus_means) == 5 else None
if opus_overall is None or abs(opus_overall - OPUS_PRESENTATION) > 0.005:
    problems.append(f"Opus overall recomputed {opus_overall} != {OPUS_PRESENTATION}")

# ---------------------------------------------------------------------------
# Gemini 3.8 Flash (High): the blind Opus-judge label set, joined to runs by
# the experiment's own join-and-score.py. Must reproduce its scores.json.
# ---------------------------------------------------------------------------
gemini_scores = json.loads((GEMINI_EXP / "scores.json").read_text(encoding="utf-8"))
GEMINI_PRESENTATION = round(gemini_scores["monday_score"], 2)
gemini_labels: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
gemini_noise: dict[tuple[str, str], list[str]] = {}
gemini_penalties: dict[tuple[str, str], list] = {}
for line in (GEMINI_EXP / "verdicts.jsonl").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    sid = row["run_id"].split("__", 1)[0]
    run_key = row["run_id"]
    if row.get("kind") == "penalties":
        gemini_penalties[(sid, run_key)] = row.get("violations") or []
    elif row.get("kind") == "noise":
        gemini_noise[(sid, run_key)] = [i["id"] for i in row["items"] if i.get("triggered")]
    else:
        gemini_labels[sid].setdefault(run_key, {})[row["criterion_id"]] = row["result"]

gemini_breakdowns: dict[tuple[str, str], object] = {}
gemini_means = []
for sid in SCEN:
    scores = []
    for run_key in sorted(gemini_labels[sid]):
        bd = score_run(sid, gemini_labels[sid][run_key],
                       noise_triggered=gemini_noise.get((sid, run_key)),
                       violations=gemini_penalties.get((sid, run_key)))
        gemini_breakdowns[(sid, run_key)] = bd
        stored = gemini_scores["scenarios"][sid]["runs"][run_key]["final_score"]
        if abs(bd.final_score - stored) > 0.005:
            problems.append(f"Gemini {sid}/{run_key}: recomputed {bd.final_score} != stored {stored}")
        scores.append(bd.final_score)
    if len(scores) != 3:
        problems.append(f"Gemini {sid}: {len(scores)} runs, expected 3")
    if scores:
        gemini_means.append(statistics.mean(scores))
gemini_overall = round(statistics.mean(gemini_means), 2) if len(gemini_means) == 5 else None
if gemini_overall is None or abs(gemini_overall - GEMINI_PRESENTATION) > 0.005:
    problems.append(f"Gemini overall recomputed {gemini_overall} != {GEMINI_PRESENTATION}")

if problems:
    print("STOP - verdict sets are not consistent with their presentation scores:\n")
    for p in problems:
        print("  -", p)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Adapt to the canonical results shape and run the canonical builder
# ---------------------------------------------------------------------------
def to_results(breakdowns, model_slug):
    """{scenario: {model: {criterion: (mean earned across runs, possible)}}}

    Mirrors official_criterion_results exactly: each criterion is averaged
    across the model's runs FIRST, and the noise dimension enters as a single
    pseudo-criterion carrying the dimension's own score.
    """
    out: dict[str, dict[str, dict[str, tuple[float, float]]]] = {}
    per_scen: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(lambda: defaultdict(list))
    for (sid, _run_key), bd in breakdowns.items():
        for cid, res in bd.criteria.items():
            per_scen[sid][cid].append((float(res.points_awarded), float(res.points_possible)))
        noise = bd.dimensions.get("noise_resistance")
        if noise is not None and RUBRICS[sid].noise is not None:
            per_scen[sid]["noise_resistance"].append((float(noise.score), float(noise.max_score)))
    for sid, per_crit in per_scen.items():
        out[sid] = {model_slug: {
            cid: (round(statistics.fmean(a for a, _ in samples), 4), samples[0][1])
            for cid, samples in per_crit.items()}}
    return out


taxonomy = load_taxonomy(TAXONOMY_VERSION)
points = rubric_points(RUBRICS)

# Reproduction check on the published models, through the same builder.
published = json.loads(PUBLISHED.read_text(encoding="utf-8"))
official_results = {s: official_criterion_results(EVALUATORS[s], s) for s in SCEN}
rebuilt, off_warnings = build_profiles(taxonomy, official_results)
repro = {}
for slug, stored in published["models"].items():
    mismatches = [
        cid for cid, e in stored["capabilities"].items()
        if (cid not in rebuilt[slug]
            or rebuilt[slug][cid].percent != e["percent"]
            or round(rebuilt[slug][cid].earned, 2) != e["earned"]
            or rebuilt[slug][cid].possible != e["possible"]
            or rebuilt[slug][cid].criteria != e["criteria"])]
    repro[slug] = {"capabilities": len(stored["capabilities"]),
                   "exact_match": not mismatches, "mismatches": mismatches}
if off_warnings:
    problems.append(f"canonical builder warnings on published models: {off_warnings}")
if not all(v["exact_match"] for v in repro.values()):
    problems.append("published models do not reproduce exactly")

# Now the two provisional models.
MODELS = {
    "claude-fable-5-1": {
        "display_name": "Claude Fable 5.1*",
        "presentation_score": FABLE_PRESENTATION,
        "results": to_results(fable_breakdowns, "claude-fable-5-1"),
        "verdict_source": [
            "experiments/fable-5.1-full-mondaybench/five-scenario-summary.json (per-run criteria, PRE-AUDIT labels)",
            "experiments/fable-5.1-date-sensitivity/verdicts.jsonl + verdicts-A2-A3.jsonl (monday-002 A1/A2/A3; B_NEUTRALIZED excluded)",
            "experiments/fable-5.1-full-mondaybench/AUDIT.md section 5 (the 10 OLD->NEW corrections applied to reach the post-audit set)",
        ],
        "judge_basis": "ORIGINAL_RECORDED_JUDGE_POST_SCORING_AUDIT",
        "provisional_reason": "Claude Code generation route rather than standard MondayBench provider route.",
    },
    "claude-opus-5": {
        "display_name": "Claude Opus 5*",
        "presentation_score": OPUS_PRESENTATION,
        "results": to_results(opus_breakdowns, "claude-opus-5"),
        "verdict_source": [
            "audits/blind-rejudge/inter-judge/source/independent-blind-rejudge-gpt-5.6-sol.json (354 criterion verdicts, 18 false-action, 15 penalty)",
            "audits/blind-rejudge/opus-5-blind-rejudge-mapping.json (candidate letter -> original run)",
        ],
        "judge_basis": "INDEPENDENT_BLIND_REJUDGE",
        "provisional_reason": "Claude Code generation route rather than standard MondayBench provider route.",
    },
    "gemini-3-8-flash-high": {
        "display_name": "Gemini 3.8 Flash (High)*",
        "presentation_score": GEMINI_PRESENTATION,
        "results": to_results(gemini_breakdowns, "gemini-3-8-flash-high"),
        "verdict_source": [
            "experiments/gemini-3.8-flash-high-opus-judge/blind-verdicts/ (354 criterion verdicts, 3 noise and 15 penalty rows, written blind)",
            "experiments/gemini-3.8-flash-high-opus-judge/verdicts.jsonl (joined to runs via gemini-3.8-mondaybench-challenger/judge-pack/provenance-map.json)",
        ],
        "judge_basis": "BLIND_REJUDGE_CLAUDE_OPUS_5_5",
        "provisional_reason": "Antigravity generation route; route equivalence NON_EQUIVALENT (served model id, system prompt and temperature unobservable).",
    },
}

artifacts = []
for slug, meta in MODELS.items():
    profiles, warnings = build_profiles(taxonomy, meta["results"])
    if warnings:
        problems.append(f"{slug}: canonical builder warnings {warnings}")
    profile = profiles[slug]

    # Scenario count per capability, as the published v0.2 schema carries.
    scen_for_cap: dict[str, set] = defaultdict(set)
    mapped = {m.key: m for m in taxonomy.mappings}
    for sid, per_model in meta["results"].items():
        for cid in per_model[slug]:
            m = mapped.get(f"{sid}.{cid}")
            if m:
                scen_for_cap[m.primary].add(sid)

    caps = {}
    for cid, sc in sorted(profile.items()):
        if sc.percent is None or not (0.0 <= sc.percent <= 100.0):
            problems.append(f"{slug}/{cid}: percentage {sc.percent} out of bounds")
        caps[cid] = {
            "earned": round(sc.earned, 2),
            "possible": sc.possible,
            "percent": sc.percent,
            "criteria": sc.criteria,
            "scenarios": len(scen_for_cap[cid]),
            "judgments": sc.criteria * 3,
        }

    payload = {
        "record_type": "provisional_capability_profile",
        "not_a_benchmark_artifact": True,
        "model_slug": slug,
        "display_name": meta["display_name"],
        "status": "PROVISIONAL",
        "benchmark_eligibility": "OFF_BENCHMARK",
        "provisional_reason": meta["provisional_reason"],
        "presentation_score": meta["presentation_score"],
        "judge_basis": meta["judge_basis"],
        "verdict_source": meta["verdict_source"],
        "taxonomy_version": taxonomy.version,
        "scenarios": sorted(meta["results"]),
        "evaluators": EVALUATORS,
        "rubric_resolution": "the rubric_file declared by each scenario's official evaluator",
        "implementation": "mondaybench.capabilities.build_profiles (canonical, unmodified)",
        "method_note": (
            "Capability score is points earned divided by points available on the criteria "
            "mapped to that capability, with each criterion averaged across the model's three "
            "runs first - the same aggregation the scenario score uses. PRIMARY mappings only, "
            "so no criterion's points are counted twice. Global penalties are excluded. The "
            "noise dimension enters as a single pseudo-criterion carrying the dimension score. "
            "Status labels play no part in the arithmetic."
        ),
        "capabilities": caps,
    }
    out = HERE / f"{slug}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    artifacts.append(out)

if problems:
    print("STOP - problems found:\n")
    for p in problems:
        print("  -", p)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Comparison table across all nine models
# ---------------------------------------------------------------------------
prov = {slug: json.loads((HERE / f"{slug}.json").read_text(encoding="utf-8"))
        for slug in MODELS}
all_caps = sorted(published["capabilities"])
comparison = {
    "record_type": "capability_comparison",
    "taxonomy_version": taxonomy.version,
    "note": "Provisional models are marked. Percentages are read from the artifacts, never recomputed downstream.",
    "capabilities": all_caps,
    "models": {},
}
for slug, m in published["models"].items():
    comparison["models"][slug] = {
        "display_name": m["display_name"], "status": "official",
        "capabilities": {c: m["capabilities"][c]["percent"] for c in all_caps
                         if c in m["capabilities"]}}
for slug, p in prov.items():
    comparison["models"][slug] = {
        "display_name": p["display_name"], "status": "PROVISIONAL",
        "presentation_score": p["presentation_score"],
        "capabilities": {c: p["capabilities"][c]["percent"] for c in all_caps
                         if c in p["capabilities"]}}
(HERE / "comparison.json").write_text(json.dumps(comparison, indent=2, ensure_ascii=False),
                                      encoding="utf-8", newline="\n")
artifacts.append(HERE / "comparison.json")

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print("PROVISIONAL CAPABILITY AGGREGATION COMPLETE\n")
print("Method:")
print(f"  implementation      mondaybench.capabilities.build_profiles (canonical)")
print(f"  taxonomy            v{taxonomy.version}  ({len(taxonomy.capabilities)} capabilities, "
      f"{len(taxonomy.mappings)} mappings, {sum(points[m.key] for m in taxonomy.mappings):.0f} points)")
print(f"  mapping             PRIMARY only")
print(f"  penalties           excluded")
print(f"  noise dimension     single pseudo-criterion carrying the dimension score")
print(f"  run aggregation     each criterion averaged across the 3 runs before summing")
print("\nReproduction check (published models, same builder):")
for slug, r in repro.items():
    print(f"  {slug:20} {r['capabilities']} caps  exact={r['exact_match']}")
print(f"  ALL SEVEN EXACT: {all(v['exact_match'] for v in repro.values())}")
print("\nPresentation score reproduction:")
print(f"  Claude Fable 5.1*   recomputed {fable_overall:.2f}  target {FABLE_PRESENTATION}  OK")
print(f"  Claude Opus 5*      recomputed {opus_overall:.2f}  target {OPUS_PRESENTATION}  OK")
print(f"  Gemini 3.8 Flash*   recomputed {gemini_overall:.2f}  target {GEMINI_PRESENTATION}  OK")
for slug in MODELS:
    p = prov[slug]
    print(f"\n{p['display_name']}  (presentation score {p['presentation_score']}, "
          f"{p['judge_basis']}):")
    for cid, e in sorted(p["capabilities"].items(), key=lambda kv: -kv[1]["percent"]):
        print(f"  {cid:30} {e['percent']:>6.1f}%   {e['earned']:>7.2f}/{e['possible']:<6.1f} "
              f"criteria={e['criteria']:<3} scenarios={e['scenarios']}")
print("\nArtifacts:")
for a in artifacts:
    print(f"  {a.relative_to(ROOT)}")
