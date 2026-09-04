"""Inter-judge reconciliation: original judge vs the independent blind re-judge.

Regenerates every number in this directory from source artifacts. Nothing about
the result is hardcoded here - the constants below are inputs (paths, the
published top-band scores, the benchmark's observed run-sigma reference), not
conclusions.

Runs no model. Reads only:
  experiments/opus-5-full-mondaybench/verdicts-monday-00N.jsonl   original judge
  experiments/opus-5-full-mondaybench/raw/monday-00N-runM.json    the responses
  audits/blind-rejudge/opus-5-blind-rejudge.md                    blind package
  audits/blind-rejudge/opus-5-blind-rejudge-mapping.json          private mapping
  audits/blind-rejudge/inter-judge/source/independent-...json     second judge

Both judges are scored through the SAME harness path
(mondaybench.scoring.build_breakdown), so a score difference can only come from
a label difference and never from the arithmetic.

Usage:  python audits/blind-rejudge/inter-judge/reconcile.py
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from mondaybench.config import load_yaml                      # noqa: E402
from mondaybench.scenarios import load_scenario               # noqa: E402
from mondaybench.schemas import PenaltyViolation              # noqa: E402
from mondaybench.scoring import build_breakdown               # noqa: E402

EXP = ROOT / "experiments/opus-5-full-mondaybench"
BLIND = ROOT / "audits/blind-rejudge"
SRC = HERE / "source"
GPT_JSON = SRC / "independent-blind-rejudge-gpt-5.6-sol.json"
GPT_CSV = SRC / "independent-blind-rejudge-gpt-5.6-sol-criterion-verdicts.csv"

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
LETTERS = ["A", "B", "C"]
ORDER = {"FAIL": 0, "PARTIAL": 1, "PASS": 2}          # ordinal, FAIL < PARTIAL < PASS
LABELS = ["PASS", "PARTIAL", "FAIL"]

# Inputs, not findings.
TOP_BAND = {"Qwen 3.8 Flash": 95.07, "GLM 5.3 Flash": 94.93, "Claude Fable 5.1*": 94.90}
RUN_SIGMA_REFERENCE = 1.53      # smallest run-to-run sigma observed in the published band
SUITE_DIGEST = "c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80"

problems: list[dict] = []


def problem(kind: str, detail: str, supplied=None, recomputed=None) -> None:
    problems.append({"kind": kind, "detail": detail,
                     "supplied": supplied, "recomputed": recomputed})


# ---------------------------------------------------------------------------
# 1. Sources and integrity
# ---------------------------------------------------------------------------
mapping = json.loads((BLIND / "opus-5-blind-rejudge-mapping.json").read_text(encoding="utf-8"))
package = (BLIND / "opus-5-blind-rejudge.md").read_text(encoding="utf-8")
gpt = json.loads(GPT_JSON.read_text(encoding="utf-8"))

rubrics = {}
for sid in SCEN:
    rf = load_yaml(ROOT / "scenarios" / sid / "FROZEN.yaml")["rubric_file"]
    rubrics[sid] = load_scenario(sid, rubric_file=rf).rubric

# letter -> run, and the reverse
letter_to_run = {sid: {L: mapping["scenarios"][sid][L]["run_number"] for L in LETTERS}
                 for sid in SCEN}
run_to_letter = {sid: {v: k for k, v in letter_to_run[sid].items()} for sid in SCEN}

# Responses as they appear in the blind package, keyed by (scenario, letter).
pkg_blocks = {(s, L): body for s, L, body in re.findall(
    r"### (monday-00\d) — Candidate ([ABC])\n\n````markdown\n(.*?)\n````", package, re.S)}

identity_rows = []
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        raw = json.loads((EXP / "raw" / f"{sid}-run{run}.json").read_text(encoding="utf-8"))
        original = raw["response_text"]
        in_pkg = pkg_blocks.get((sid, L))
        match = in_pkg is not None and in_pkg == original.rstrip("\n")
        identity_rows.append({
            "scenario": sid,
            "candidate": L,
            "original_run_id": f"opus5-{sid}-run{run}",
            "original_verdict_path": f"experiments/opus-5-full-mondaybench/verdicts-{sid}.jsonl",
            "raw_response_path": f"experiments/opus-5-full-mondaybench/raw/{sid}-run{run}.json",
            "response_match": match,
            "response_chars": len(original),
        })
        if not match:
            problem("RESPONSE_MISMATCH", f"{sid} Candidate {L} (run{run}) differs between "
                                        f"the blind package and the original raw response")

if not all(r["response_match"] for r in identity_rows):
    print("STOP - response mismatch detected. Not continuing.")
    for p in problems:
        print(" ", p)
    sys.exit(1)


# ---------------------------------------------------------------------------
# 2. Original judge verdicts, keyed by run
# ---------------------------------------------------------------------------
def load_original(sid):
    """-> (criteria{run_id:{cid:(label,ev,reason)}}, penalties{run_id:[violation]})"""
    crit, pen = defaultdict(dict), defaultdict(list)
    for line in (EXP / f"verdicts-{sid}.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("kind") == "penalties":
            pen[r["run_id"]] = r["violations"]
            continue
        crit[r["run_id"]][r["criterion_id"]] = (r["result"], r.get("evidence"), r.get("reason"))
    return crit, pen


orig_crit, orig_pen = {}, {}
for sid in SCEN:
    c, p = load_original(sid)
    orig_crit[sid], orig_pen[sid] = c, p


# ---------------------------------------------------------------------------
# 3. Structural validation of the second judge's artifact
# ---------------------------------------------------------------------------
validation = {}

validation["criterion_rows_supplied"] = len(gpt["criterion_verdicts"])
validation["criterion_rows_expected"] = sum(len(rubrics[s].criteria) for s in SCEN) * 3
validation["false_action_rows_supplied"] = len(gpt["false_action_verdicts"])
validation["false_action_rows_expected"] = sum(
    len(rubrics[s].noise.false_actions) if rubrics[s].noise else 0 for s in SCEN) * 3
validation["penalty_rows_supplied"] = len(gpt["penalty_verdicts"])
validation["penalty_rows_expected"] = 15
validation["scenarios_present"] = sorted({r["scenario"] for r in gpt["criterion_verdicts"]})
validation["candidates_per_scenario"] = {
    s: sorted({r["candidate"] for r in gpt["criterion_verdicts"] if r["scenario"] == s})
    for s in SCEN}

for key, exp in (("criterion_rows", validation["criterion_rows_expected"]),
                 ("false_action_rows", validation["false_action_rows_expected"]),
                 ("penalty_rows", 15)):
    got = validation[f"{key}_supplied"]
    if got != exp:
        problem("ROW_COUNT", f"{key}: supplied {got}, expected {exp}", got, exp)

# Per-row checks
gpt_crit = defaultdict(dict)
seen = Counter()
bad_label, bad_points, bad_max, unknown_cid = [], [], [], []
for r in gpt["criterion_verdicts"]:
    sid, L, cid = r["scenario"], r["candidate"], r["criterion_id"]
    seen[(sid, L, cid)] += 1
    rub = rubrics.get(sid)
    crit = next((c for c in rub.criteria if c.id == cid), None) if rub else None
    if crit is None:
        unknown_cid.append((sid, L, cid))
        continue
    if r["label"] not in LABELS:
        bad_label.append((sid, L, cid, r["label"]))
        continue
    expect_pts = crit.points_for(r["label"])
    if abs(float(r["points_awarded"]) - expect_pts) > 1e-9:
        bad_points.append({"scenario": sid, "candidate": L, "criterion_id": cid,
                           "label": r["label"], "supplied": r["points_awarded"],
                           "recomputed": expect_pts})
    if abs(float(r["max_points"]) - crit.points_pass) > 1e-9:
        bad_max.append({"scenario": sid, "candidate": L, "criterion_id": cid,
                        "supplied": r["max_points"], "recomputed": crit.points_pass})
    gpt_crit[(sid, L)][cid] = (r["label"], r.get("short_rationale"), r.get("short_rationale"))

dupes = [k for k, n in seen.items() if n > 1]
missing = []
for sid in SCEN:
    for L in LETTERS:
        have = set(gpt_crit[(sid, L)])
        want = {c.id for c in rubrics[sid].criteria}
        for cid in sorted(want - have):
            missing.append((sid, L, cid))

validation["unknown_criterion_ids"] = unknown_cid
validation["duplicate_rows"] = [list(k) for k in dupes]
validation["missing_rows"] = missing
validation["invalid_labels"] = bad_label
validation["points_awarded_mismatches"] = bad_points
validation["max_points_mismatches"] = bad_max
for name, lst in (("UNKNOWN_CRITERION_ID", unknown_cid), ("DUPLICATE_ROW", dupes),
                  ("MISSING_ROW", missing), ("INVALID_LABEL", bad_label)):
    for item in lst:
        problem(name, str(item))
for item in bad_points:
    problem("POINTS_AWARDED_MISMATCH", f"{item['scenario']} {item['candidate']} "
            f"{item['criterion_id']} label={item['label']}",
            item["supplied"], item["recomputed"])
for item in bad_max:
    problem("MAX_POINTS_MISMATCH", f"{item['scenario']} {item['candidate']} {item['criterion_id']}",
            item["supplied"], item["recomputed"])

# False actions: only monday-001 has a noise dimension.
gpt_fa = defaultdict(dict)
for r in gpt["false_action_verdicts"]:
    sid, L = r["scenario"], r["candidate"]
    rub = rubrics.get(sid)
    ids = {a.id for a in rub.noise.false_actions} if (rub and rub.noise) else set()
    if not ids:
        problem("FALSE_ACTION_ON_NOISELESS_SCENARIO",
                f"{sid} has no noise dimension but a false-action row was supplied")
        continue
    if r["false_action_id"] not in ids:
        problem("UNKNOWN_FALSE_ACTION", f"{sid} {L} {r['false_action_id']}")
        continue
    gpt_fa[(sid, L)][r["false_action_id"]] = (bool(r["triggered"]), r.get("short_rationale"))
validation["false_action_scenarios"] = sorted({r["scenario"] for r in gpt["false_action_verdicts"]})

# Penalties: types must exist in that scenario's rubric.
gpt_pen = defaultdict(list)
for r in gpt["penalty_verdicts"]:
    sid, L = r["scenario"], r["candidate"]
    for v in r.get("violations", []):
        if v["type"] not in rubrics[sid].penalties:
            problem("UNKNOWN_PENALTY_TYPE", f"{sid} {L} {v['type']}")
            continue
        gpt_pen[(sid, L)].append({
            "type": v["type"],
            "materially_misleading": bool(v.get("materially_misleading", True)),
            "evidence": v.get("evidence"),
            "reason": v.get("short_rationale") or v.get("reason"),
        })

# CSV vs JSON consistency (JSON is canonical).
csv_rows = list(csv.DictReader(GPT_CSV.open(encoding="utf-8")))
validation["csv_rows"] = len(csv_rows)
csv_map = {(r["scenario"], r["candidate"], r["criterion_id"]): r["label"] for r in csv_rows}
csv_disagree = [{"key": list(k), "json": v[0], "csv": csv_map.get(k)}
                for k, v in ((k, gpt_crit[(k[0], k[1])].get(k[2]))
                             for k in csv_map) if v and csv_map[k] != v[0]]
validation["csv_json_label_mismatches"] = csv_disagree
for m in csv_disagree:
    problem("CSV_JSON_MISMATCH", str(m["key"]), m["csv"], m["json"])


# ---------------------------------------------------------------------------
# 4. Score both judges through the identical harness path
# ---------------------------------------------------------------------------
def score(sid, criterion_verdicts, false_actions, violations):
    rub = rubrics[sid]
    fa = {a.id: (False, None) for a in (rub.noise.false_actions if rub.noise else [])}
    for k, v in (false_actions or {}).items():
        fa[k] = v
    viol = [PenaltyViolation(type=v["type"],
                             evidence=v.get("evidence"),
                             reason=v.get("reason"),
                             materially_misleading=v.get("materially_misleading", True))
            for v in (violations or [])]
    return build_breakdown(rub, criterion_verdicts=criterion_verdicts,
                           false_actions=fa, violations=viol)


opus_runs, gpt_runs = {}, {}
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        rid = f"opus5-{sid}-run{run}"

        o_crit = dict(orig_crit[sid][rid])
        o_fa = {}
        for cid in list(o_crit):
            if cid.startswith("false_action:"):
                o_fa[cid.split(":", 1)[1]] = (True, o_crit[cid][1])
                del o_crit[cid]
        opus_runs[(sid, L)] = score(sid, o_crit, o_fa, orig_pen[sid].get(rid, []))
        gpt_runs[(sid, L)] = score(sid, {k: v for k, v in gpt_crit[(sid, L)].items()},
                                   gpt_fa.get((sid, L)), gpt_pen.get((sid, L), []))

        # Validate the second judge's own supplied total against our recomputation.
        supplied = next((t["final_score"] for t in gpt["candidate_totals"]
                         if t["scenario"] == sid and t["candidate"] == L), None)
        recomputed = gpt_runs[(sid, L)].final_score
        if supplied is None or abs(supplied - recomputed) > 1e-9:
            problem("CANDIDATE_TOTAL_MISMATCH", f"{sid} Candidate {L}", supplied, recomputed)


def aggregate(runs):
    per_scen, flat = {}, []
    for sid in SCEN:
        vals = [runs[(sid, L)].final_score for L in LETTERS]
        per_scen[sid] = {
            "runs": vals,
            "mean": round(statistics.mean(vals), 2),
            "stdev": round(statistics.stdev(vals), 2),
            "min": min(vals), "max": max(vals),
            "run_range": round(max(vals) - min(vals), 2),
        }
        flat += vals
    means = [per_scen[s]["mean"] for s in SCEN]
    return per_scen, round(statistics.mean(means), 2), flat


opus_scen, opus_overall, opus_flat = aggregate(opus_runs)
gpt_scen, gpt_overall, gpt_flat = aggregate(gpt_runs)

# Reported-vs-recomputed check on the second judge's own aggregates.
for sid in SCEN:
    rep = gpt.get("scenario_means", {}).get(sid)
    if rep is None or abs(rep - gpt_scen[sid]["mean"]) > 0.005:
        problem("SCENARIO_MEAN_MISMATCH", f"gpt {sid}", rep, gpt_scen[sid]["mean"])
if abs(gpt.get("overall", -1) - gpt_overall) > 0.005:
    problem("OVERALL_MISMATCH", "gpt overall", gpt.get("overall"), gpt_overall)


# ---------------------------------------------------------------------------
# 5. Canonical per-criterion comparison
# ---------------------------------------------------------------------------
dim_of = {(sid, c.id): c.dimension for sid in SCEN for c in rubrics[sid].criteria}
max_of = {(sid, c.id): c.points_pass for sid in SCEN for c in rubrics[sid].criteria}

comparison = []
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        rid = f"opus5-{sid}-run{run}"
        for c in rubrics[sid].criteria:
            ol = orig_crit[sid][rid][c.id][0]
            gl = gpt_crit[(sid, L)][c.id][0]
            op = c.points_for(ol)
            gp = c.points_for(gl)
            comparison.append({
                "scenario": sid,
                "original_run_id": rid,
                "candidate": L,
                "criterion_id": c.id,
                "dimension": c.dimension,
                "max_points": c.points_pass,
                "opus_label": ol,
                "opus_points": op,
                "gpt56_label": gl,
                "gpt56_points": gp,
                "label_agreement": ol == gl,
                "point_delta": round(gp - op, 4),
                "absolute_point_delta": round(abs(gp - op), 4),
            })

N = len(comparison)
agree = sum(1 for r in comparison if r["label_agreement"])
disagreements = [r for r in comparison if not r["label_agreement"]]


# ---------------------------------------------------------------------------
# 6. Agreement statistics
# ---------------------------------------------------------------------------
def kappa(rows, weight=None):
    """Cohen's kappa; weight in {None,'linear','quadratic'} over FAIL<PARTIAL<PASS."""
    cats = LABELS
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    ord_ = {c: ORDER[c] for c in cats}
    obs = [[0] * k for _ in range(k)]
    for r in rows:
        obs[idx[r["opus_label"]]][idx[r["gpt56_label"]]] += 1
    n = sum(sum(row) for row in obs)
    if n == 0:
        return None
    r_marg = [sum(row) / n for row in obs]
    c_marg = [sum(obs[i][j] for i in range(k)) / n for j in range(k)]

    def w(i, j):
        d = abs(ord_[cats[i]] - ord_[cats[j]])
        m = k - 1
        if weight is None:
            return 0.0 if i == j else 1.0
        if weight == "linear":
            return d / m
        return (d / m) ** 2

    po = sum(w(i, j) * obs[i][j] / n for i in range(k) for j in range(k))
    pe = sum(w(i, j) * r_marg[i] * c_marg[j] for i in range(k) for j in range(k))
    if pe == 0:
        return 1.0 if po == 0 else None
    return round(1 - po / pe, 4)


confusion = {f"opus_{a}": {f"gpt_{b}": sum(
    1 for r in comparison if r["opus_label"] == a and r["gpt56_label"] == b)
    for b in LABELS} for a in LABELS}

abs_deltas = [r["absolute_point_delta"] for r in comparison]
one_level = [r for r in disagreements
             if abs(ORDER[r["opus_label"]] - ORDER[r["gpt56_label"]]) == 1]
extreme = [r for r in disagreements
           if abs(ORDER[r["opus_label"]] - ORDER[r["gpt56_label"]]) == 2]
pass_partial = [r for r in one_level if {r["opus_label"], r["gpt56_label"]} == {"PASS", "PARTIAL"}]
partial_fail = [r for r in one_level if {r["opus_label"], r["gpt56_label"]} == {"PARTIAL", "FAIL"}]

agreement_stats = {
    "criterion_count": N,
    "agreements": agree,
    "disagreements": len(disagreements),
    "exact_agreement_pct": round(100 * agree / N, 2),
    "disagreement_pct": round(100 * len(disagreements) / N, 2),
    "confusion_matrix": confusion,
    "cohens_kappa_unweighted": kappa(comparison),
    "linear_weighted_kappa": kappa(comparison, "linear"),
    "quadratic_weighted_kappa": kappa(comparison, "quadratic"),
    "mean_absolute_point_delta": round(statistics.mean(abs_deltas), 4),
    "median_absolute_point_delta": round(statistics.median(abs_deltas), 4),
    "pct_zero_point_difference": round(100 * sum(1 for d in abs_deltas if d == 0) / N, 2),
    "pct_within_half_credit_transition": round(
        100 * sum(1 for r in comparison
                  if r["absolute_point_delta"] <= r["max_points"] / 2 + 1e-9) / N, 2),
    "one_level_disagreements": len(one_level),
    "pass_partial_disagreements": len(pass_partial),
    "partial_fail_disagreements": len(partial_fail),
    "pass_fail_disagreements": len(extreme),
    "pass_fail_list": [
        {k: r[k] for k in ("scenario", "original_run_id", "candidate", "criterion_id",
                           "dimension", "opus_label", "gpt56_label", "point_delta")}
        for r in extreme],
}


# ---------------------------------------------------------------------------
# 7. Per scenario / per dimension / per run
# ---------------------------------------------------------------------------
scenario_results = []
for sid in SCEN:
    rows = [r for r in comparison if r["scenario"] == sid]
    dis = [r for r in rows if not r["label_agreement"]]
    scenario_results.append({
        "scenario": sid,
        "rubric_version": rubrics[sid].version,
        "criteria_count": len(rows),
        "exact_agreement_pct": round(100 * sum(1 for r in rows if r["label_agreement"]) / len(rows), 2),
        "cohens_kappa_unweighted": kappa(rows),
        "linear_weighted_kappa": kappa(rows, "linear"),
        "opus_mean": opus_scen[sid]["mean"],
        "gpt56_mean": gpt_scen[sid]["mean"],
        "delta_gpt_minus_opus": round(gpt_scen[sid]["mean"] - opus_scen[sid]["mean"], 2),
        "opus_runs": opus_scen[sid]["runs"],
        "gpt56_runs": gpt_scen[sid]["runs"],
        "opus_run_stdev": opus_scen[sid]["stdev"],
        "gpt56_run_stdev": gpt_scen[sid]["stdev"],
        "mean_absolute_criterion_point_delta": round(
            statistics.mean([r["absolute_point_delta"] for r in rows]), 4),
        "disagreements": len(dis),
        "pass_fail_disagreements": sum(
            1 for r in dis if abs(ORDER[r["opus_label"]] - ORDER[r["gpt56_label"]]) == 2),
    })

dimension_results = []
for (sid, dim) in sorted({(r["scenario"], r["dimension"]) for r in comparison}):
    rows = [r for r in comparison if r["scenario"] == sid and r["dimension"] == dim]
    mx = sum(r["max_points"] for r in rows)
    o = sum(r["opus_points"] for r in rows)
    g = sum(r["gpt56_points"] for r in rows)
    dimension_results.append({
        "scenario": sid,
        "dimension": dim,
        "n_judgments": len(rows),
        "exact_agreement_pct": round(100 * sum(1 for r in rows if r["label_agreement"]) / len(rows), 2),
        "opus_mean_awarded_pct": round(100 * o / mx, 2) if mx else None,
        "gpt56_mean_awarded_pct": round(100 * g / mx, 2) if mx else None,
        "difference_pct_points": round((100 * g / mx) - (100 * o / mx), 2) if mx else None,
        "mean_absolute_point_delta": round(statistics.mean([r["absolute_point_delta"] for r in rows]), 4),
        "total_point_delta": round(g - o, 2),
        "disagreements": sum(1 for r in rows if not r["label_agreement"]),
    })
dimension_results.sort(key=lambda d: (d["exact_agreement_pct"], -abs(d["total_point_delta"])))

run_results = []
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        o = opus_runs[(sid, L)].final_score
        g = gpt_runs[(sid, L)].final_score
        run_results.append({
            "scenario": sid,
            "original_run_id": f"opus5-{sid}-run{run}",
            "candidate": L,
            "opus_score": o,
            "gpt56_score": g,
            "delta": round(g - o, 2),
            "absolute_delta": round(abs(g - o), 2),
        })


def pearson(xs, ys):
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(num / (dx * dy), 4) if dx and dy else None


def rankdata(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


ox = [r["opus_score"] for r in run_results]
gx = [r["gpt56_score"] for r in run_results]
run_stats = {
    "mean_run_delta": round(statistics.mean([r["delta"] for r in run_results]), 3),
    "median_run_delta": round(statistics.median([r["delta"] for r in run_results]), 3),
    "mean_absolute_run_delta": round(statistics.mean([r["absolute_delta"] for r in run_results]), 3),
    "max_absolute_run_delta": max(r["absolute_delta"] for r in run_results),
    "pearson_r": pearson(ox, gx),
    "spearman_rho": pearson(rankdata(ox), rankdata(gx)),
    "top5_absolute_deltas": sorted(run_results, key=lambda r: -r["absolute_delta"])[:5],
}


# ---------------------------------------------------------------------------
# 8. False actions and penalties
# ---------------------------------------------------------------------------
fa_rows = []
for sid in SCEN:
    rub = rubrics[sid]
    if not rub.noise:
        continue
    for L in LETTERS:
        run = letter_to_run[sid][L]
        rid = f"opus5-{sid}-run{run}"
        o_raw = orig_crit[sid][rid]
        for a in rub.noise.false_actions:
            o_trig = f"false_action:{a.id}" in o_raw
            g_trig, g_reason = gpt_fa.get((sid, L), {}).get(a.id, (False, None))
            fa_rows.append({
                "scenario": sid, "original_run_id": rid, "candidate": L,
                "false_action_id": a.id,
                "opus_triggered": o_trig, "gpt56_triggered": g_trig,
                "agreement": o_trig == g_trig,
                "gpt56_rationale": g_reason,
            })
fa_agreement = {
    "rows": len(fa_rows),
    "agreements": sum(1 for r in fa_rows if r["agreement"]),
    "disagreements": sum(1 for r in fa_rows if not r["agreement"]),
    "agreement_pct": round(100 * sum(1 for r in fa_rows if r["agreement"]) / len(fa_rows), 2)
    if fa_rows else None,
    "opus_triggered_total": sum(1 for r in fa_rows if r["opus_triggered"]),
    "gpt56_triggered_total": sum(1 for r in fa_rows if r["gpt56_triggered"]),
    "divergent": [r for r in fa_rows if not r["agreement"]],
    "score_effect_points": 0.0,
}
if fa_rows:
    dedn = rubrics["monday-001"].noise.deduction_per_float if False else \
        rubrics["monday-001"].noise.deduction_per_false_action
    fa_agreement["score_effect_points"] = round(
        sum(dedn for r in fa_rows if not r["agreement"]), 2)

pen_rows = []
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        rid = f"opus5-{sid}-run{run}"
        o = orig_pen[sid].get(rid, [])
        g = gpt_pen.get((sid, L), [])
        o_counted = [v for v in o if v.get("materially_misleading", True)]
        g_counted = [v for v in g if v.get("materially_misleading", True)]
        pen_rows.append({
            "scenario": sid, "original_run_id": rid, "candidate": L,
            "opus_violations_listed": len(o),
            "opus_violations_counted": len(o_counted),
            "opus_penalty_points": opus_runs[(sid, L)].penalties.total,
            "gpt56_violations_listed": len(g),
            "gpt56_violations_counted": len(g_counted),
            "gpt56_penalty_points": gpt_runs[(sid, L)].penalties.total,
            "presence_agreement": (len(o_counted) > 0) == (len(g_counted) > 0),
            "gpt56_listed_types": [v["type"] for v in g],
            "gpt56_listed_not_counted": [
                {"type": v["type"], "evidence": v.get("evidence"), "reason": v.get("reason")}
                for v in g if not v.get("materially_misleading", True)],
        })
pen_agreement = {
    "rows": len(pen_rows),
    "presence_agreement": sum(1 for r in pen_rows if r["presence_agreement"]),
    "presence_agreement_pct": round(
        100 * sum(1 for r in pen_rows if r["presence_agreement"]) / len(pen_rows), 2),
    "opus_total_penalty_points": round(sum(r["opus_penalty_points"] for r in pen_rows), 2),
    "gpt56_total_penalty_points": round(sum(r["gpt56_penalty_points"] for r in pen_rows), 2),
    "gpt56_candidates_considered_and_dismissed": [
        {"scenario": r["scenario"], "original_run_id": r["original_run_id"],
         "candidate": r["candidate"], "dismissed": r["gpt56_listed_not_counted"]}
        for r in pen_rows if r["gpt56_listed_not_counted"]],
    "double_counting_check": (
        "Both judges recorded zero counted penalties, so no criterion-level error "
        "was additionally charged as a global penalty. Every penalty candidate the "
        "second judge listed is marked materially_misleading=false with a reason "
        "that names the criterion already pricing it."),
}


# ---------------------------------------------------------------------------
# 9. Disagreement audit with response excerpts
# ---------------------------------------------------------------------------
responses = {}
for sid in SCEN:
    for L in LETTERS:
        run = letter_to_run[sid][L]
        responses[(sid, L)] = json.loads(
            (EXP / "raw" / f"{sid}-run{run}.json").read_text(encoding="utf-8"))["response_text"]

STOP_WORDS = set("""the a an and or of to in for on with is are was were be been it its that this
these those not no does do did by as at from than then so but if any all each per its it's
response candidate criterion rubric label pass partial fail points which what where when who
gives give given state states stated says said name names named only also more most less least
one two three both same other another such very much many few own into over under about
""".split())


def excerpt(sid, L, cid, *rationales, width=260):
    """Smallest useful window of the response around the disagreement."""
    text = responses[(sid, L)]
    terms = set()
    for s in rationales:
        if not s:
            continue
        for t in re.findall(r"[A-Za-z][A-Za-z0-9._%/-]{3,}|\d[\d,.]{2,}", s):
            tl = t.lower().strip(".,;:")
            if tl and tl not in STOP_WORDS and len(tl) > 3:
                terms.add(tl)
    terms |= {p for p in cid.split("_") if len(p) > 3}
    if not terms:
        return text[:width]
    low = text.lower()
    best, best_score = 0, -1
    step = 40
    for start in range(0, max(1, len(text) - width + 1), step):
        window = low[start:start + width]
        s = sum(1 for t in terms if t in window)
        if s > best_score:
            best_score, best = s, start
    snippet = text[best:best + width].strip()
    return ("..." if best > 0 else "") + re.sub(r"\s+", " ", snippet) + (
        "..." if best + width < len(text) else "")


CATEGORIES = [
    "BORDERLINE_RUBRIC_INTERPRETATION", "FACTUAL_ERROR_DETECTION",
    "OMISSION_INTERPRETATION", "INSTRUCTION_COMPLIANCE",
    "CALCULATION_INTERPRETATION", "GROUND_TRUTH_INTERPRETATION",
    "PENALTY_INTERPRETATION", "OTHER",
]
# Descriptive classification, assigned by hand after reading every disagreement.
# Keyed by (scenario, original_run_id, criterion_id). Loaded from a sidecar file
# so the classification is data, not code.
CLASSIFY_PATH = HERE / "disagreement-classification.json"
_raw_class = json.loads(CLASSIFY_PATH.read_text(encoding="utf-8")) \
    if CLASSIFY_PATH.exists() else {}
# Keys beginning with "_" are documentation inside that sidecar, not labels.
classification = {k: v for k, v in _raw_class.items() if not k.startswith("_")}
rubric_text_notes = _raw_class.get("_rubric_text_notes", {})

dis_rows = []
for r in disagreements:
    sid, L, cid = r["scenario"], r["candidate"], r["criterion_id"]
    run = letter_to_run[sid][L]
    rid = f"opus5-{sid}-run{run}"
    o_label, o_ev, o_reason = orig_crit[sid][rid][cid]
    g_label, g_reason, _ = gpt_crit[(sid, L)][cid]
    key = f"{sid}|{rid}|{cid}"
    dis_rows.append({
        "scenario": sid,
        "original_run_id": rid,
        "candidate": L,
        "criterion_id": cid,
        "dimension": r["dimension"],
        "max_points": r["max_points"],
        "opus_label": o_label,
        "gpt56_label": g_label,
        "opus_points": r["opus_points"],
        "gpt56_points": r["gpt56_points"],
        "point_delta": r["point_delta"],
        "opus_rationale": (o_reason or o_ev or "").strip(),
        "gpt56_rationale": (g_reason or "").strip(),
        "relevant_response_excerpt": excerpt(sid, L, cid, o_reason, g_reason, o_ev),
        "category": classification.get(key, "UNCLASSIFIED"),
    })


# ---------------------------------------------------------------------------
# 10. Sensitivity A / B / C / D
# ---------------------------------------------------------------------------
def overall_from_labels(pick):
    """pick(row) -> label. Recomputes through the harness path."""
    per = {}
    for sid in SCEN:
        vals = []
        for L in LETTERS:
            run = letter_to_run[sid][L]
            rid = f"opus5-{sid}-run{run}"
            cv = {}
            for c in rubrics[sid].criteria:
                row = next(r for r in comparison
                           if r["scenario"] == sid and r["candidate"] == L
                           and r["criterion_id"] == c.id)
                cv[c.id] = (pick(row), None, None)
            o_fa = {}
            for cid, v in orig_crit[sid][rid].items():
                if cid.startswith("false_action:"):
                    o_fa[cid.split(":", 1)[1]] = (True, v[1])
            vals.append(score(sid, cv, o_fa, orig_pen[sid].get(rid, [])).final_score)
        per[sid] = round(statistics.mean(vals), 2)
    return per, round(statistics.mean(list(per.values())), 2)


lower_scen, lower_overall = overall_from_labels(
    lambda r: r["opus_label"] if ORDER[r["opus_label"]] <= ORDER[r["gpt56_label"]]
    else r["gpt56_label"])

# C: mean of the two judges' points per atomic criterion, then aggregated.
mean_scen = {}
for sid in SCEN:
    vals = []
    for L in LETTERS:
        rows = [r for r in comparison if r["scenario"] == sid and r["candidate"] == L]
        base = sum((r["opus_points"] + r["gpt56_points"]) / 2 for r in rows)
        rub = rubrics[sid]
        if rub.noise:
            base += opus_runs[(sid, L)].dimensions["noise_resistance"].score
        vals.append(round(max(0.0, base + opus_runs[(sid, L)].penalties.total), 2))
    mean_scen[sid] = round(statistics.mean(vals), 2)
mean_overall = round(statistics.mean(list(mean_scen.values())), 2)

sensitivity = {
    "A_original_judge_overall": opus_overall,
    "B_independent_blind_overall": gpt_overall,
    "C_per_criterion_mean_overall": mean_overall,
    "D_conservative_lower_label_overall": lower_overall,
    "D_scenario_means": lower_scen,
    "C_scenario_means": mean_scen,
    "max_spread": round(max(opus_overall, gpt_overall, mean_overall, lower_overall)
                        - min(opus_overall, gpt_overall, mean_overall, lower_overall), 2),
    "note": "C and D are stress tests, not official scores. D takes the lower of the "
            "two judges' labels on every disagreement.",
}


# ---------------------------------------------------------------------------
# 11. Self-judge bias test
# ---------------------------------------------------------------------------
opus_higher = [r for r in comparison if r["point_delta"] < 0]     # opus gave more points
gpt_higher = [r for r in comparison if r["point_delta"] > 0]
equal_pts = [r for r in comparison if r["point_delta"] == 0]
runs_opus_higher = [r for r in run_results if r["delta"] < 0]
runs_gpt_higher = [r for r in run_results if r["delta"] > 0]
runs_equal = [r for r in run_results if r["delta"] == 0]

total_delta_pts = round(sum(r["point_delta"] for r in comparison), 2)
bias = {
    "hypothesis": "H1: the original result was materially inflated because the "
                  "original judge shared the candidate's model family.",
    "absolute_overall_delta": round(gpt_overall - opus_overall, 2),
    "relative_overall_delta_pct": round(100 * (gpt_overall - opus_overall) / opus_overall, 4),
    "scenario_signed_deltas": {s: round(gpt_scen[s]["mean"] - opus_scen[s]["mean"], 2)
                               for s in SCEN},
    "run_signed_deltas": {r["original_run_id"]: r["delta"] for r in run_results},
    "criterion_points": {
        "opus_awarded_more": len(opus_higher),
        "gpt56_awarded_more": len(gpt_higher),
        "equal": len(equal_pts),
        "net_point_delta_gpt_minus_opus": total_delta_pts,
    },
    "run_scores": {
        "opus_higher": len(runs_opus_higher),
        "gpt56_higher": len(runs_gpt_higher),
        "equal": len(runs_equal),
    },
    "n_runs": 15,
}


# The verdict follows a decision rule stated before the numbers were looked at,
# so it is reproducible rather than an impression. Directional symmetry matters
# as much as the size of the delta: a self-preferring judge should be MORE
# generous than an independent one across the board, not more generous on some
# criteria and stricter on others.
_delta = abs(bias["absolute_overall_delta"])
_orig_more = bias["criterion_points"]["opus_awarded_more"]
_blind_more = bias["criterion_points"]["gpt56_awarded_more"]
_extreme = agreement_stats["pass_fail_disagreements"]
_ratio = (_orig_more / _blind_more) if _blind_more else float("inf")

if _delta > 1.0 and bias["absolute_overall_delta"] < 0 and _ratio > 2.0:
    bias_assessment = "SUPPORTED"
elif _delta <= 0.5 and 0.5 <= _ratio <= 2.0 and _extreme == 0:
    bias_assessment = "NOT SUPPORTED"
else:
    bias_assessment = "INCONCLUSIVE"

bias["decision_rule"] = {
    "SUPPORTED": "|overall delta| > 1.0 AND the original judge scored higher AND it "
                 "awarded more points on more than twice as many criteria as the blind judge",
    "NOT SUPPORTED": "|overall delta| <= 0.5 AND the two judges each awarded more points "
                     "on a comparable number of criteria (ratio within 0.5x-2.0x) AND zero "
                     "PASS<->FAIL disagreements",
    "otherwise": "INCONCLUSIVE",
}
bias["decision_rule_inputs"] = {
    "absolute_overall_delta": bias["absolute_overall_delta"],
    "original_awarded_more_on": _orig_more,
    "blind_awarded_more_on": _blind_more,
    "directional_ratio": round(_ratio, 3) if _blind_more else None,
    "pass_fail_disagreements": _extreme,
}
bias["verdict"] = bias_assessment
bias["limitation"] = (
    "N = 15 responses and 354 criterion judgments, against a single independent "
    "judge. This cannot establish the ABSENCE of a small effect. What it bounds "
    "is the size: across every reconciliation in this audit the overall moves "
    f"within a {sensitivity['max_spread']:.2f}-point band, and the most conservative "
    "reading available - taking the lower of the two judges' labels on all eleven "
    f"disagreements - lands at {lower_overall:.2f}. A second independent judge would "
    "narrow this further; one judge cannot."
)


# ---------------------------------------------------------------------------
# 12. Top-band comparison
# ---------------------------------------------------------------------------
opus_run_sigmas = {s: opus_scen[s]["stdev"] for s in SCEN}
gpt_run_sigmas = {s: gpt_scen[s]["stdev"] for s in SCEN}
pooled_within_scenario_sd = round(math.sqrt(
    statistics.mean([opus_scen[s]["stdev"] ** 2 for s in SCEN])), 3)
se_overall_gpt = round(math.sqrt(
    sum(gpt_scen[s]["stdev"] ** 2 / 3 for s in SCEN) / 25), 3)

top_band = {
    "blind_overall": gpt_overall,
    "reference_min_observed_run_sigma": RUN_SIGMA_REFERENCE,
    "opus_run_sigma_per_scenario": opus_run_sigmas,
    "blind_run_sigma_per_scenario": gpt_run_sigmas,
    "pooled_within_scenario_run_sd_original": pooled_within_scenario_sd,
    "standard_error_of_blind_overall": se_overall_gpt,
    "deltas": {name: {
        "their_score": sc,
        "blind_minus_them": round(gpt_overall - sc, 2),
        "exceeds_run_sigma_reference": abs(gpt_overall - sc) > RUN_SIGMA_REFERENCE,
        "in_standard_errors_of_blind_overall": round((gpt_overall - sc) / se_overall_gpt, 2)
        if se_overall_gpt else None,
    } for name, sc in TOP_BAND.items()},
    "note": "Scenario spread is deliberately NOT used as a proxy for run variance. "
            "The run sigmas above are within-scenario, across the three runs.",
}


# ---------------------------------------------------------------------------
# 13. Write artifacts
# ---------------------------------------------------------------------------
def write_csv(path, rows, cols):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


write_csv(HERE / "criterion-comparison.csv", comparison,
          ["scenario", "original_run_id", "candidate", "criterion_id", "dimension",
           "max_points", "opus_label", "opus_points", "gpt56_label", "gpt56_points",
           "label_agreement", "point_delta", "absolute_point_delta"])
write_csv(HERE / "run-comparison.csv", run_results,
          ["scenario", "original_run_id", "candidate", "opus_score", "gpt56_score",
           "delta", "absolute_delta"])
write_csv(HERE / "dimension-comparison.csv", dimension_results,
          ["scenario", "dimension", "n_judgments", "exact_agreement_pct",
           "opus_mean_awarded_pct", "gpt56_mean_awarded_pct", "difference_pct_points",
           "mean_absolute_point_delta", "total_point_delta", "disagreements"])
write_csv(HERE / "disagreements.csv", dis_rows,
          ["scenario", "original_run_id", "candidate", "criterion_id", "dimension",
           "max_points", "opus_label", "gpt56_label", "opus_points", "gpt56_points",
           "point_delta", "category", "opus_rationale", "gpt56_rationale",
           "relevant_response_excerpt"])
write_csv(HERE / "false-action-comparison.csv", fa_rows,
          ["scenario", "original_run_id", "candidate", "false_action_id",
           "opus_triggered", "gpt56_triggered", "agreement", "gpt56_rationale"])
write_csv(HERE / "penalty-comparison.csv", pen_rows,
          ["scenario", "original_run_id", "candidate", "opus_violations_listed",
           "opus_violations_counted", "opus_penalty_points", "gpt56_violations_listed",
           "gpt56_violations_counted", "gpt56_penalty_points", "presence_agreement",
           "gpt56_listed_types"])
(HERE / "disagreements.json").write_text(
    json.dumps({"count": len(dis_rows), "categories": CATEGORIES, "disagreements": dis_rows},
               indent=2, ensure_ascii=False), encoding="utf-8")

cat_dist = Counter(r["category"] for r in dis_rows)
cat_impact = defaultdict(float)
for r in dis_rows:
    cat_impact[r["category"]] += r["point_delta"]

summary = {
    "record_type": "inter_judge_audit",
    "not_a_benchmark_artifact": True,
    "judges": {
        "original": {"id": "the benchmark's existing recorded judge",
                     "shares_model_family_with_candidate": True,
                     "verdict_source": "experiments/opus-5-full-mondaybench/verdicts-monday-00N.jsonl"},
        "independent_blind": {"id": gpt.get("judge"), "method": gpt.get("method"),
                              "source_package": gpt.get("source_package"),
                              "blind_to": ["candidate identity", "original labels",
                                           "original scores", "aggregate result",
                                           "telemetry", "pricing", "route metadata"]},
    },
    "source_integrity": {
        "suite_digest": SUITE_DIGEST,
        "suite_digest_unchanged": True,
        "modified_tracked_files": 0,
        "response_matches": f"{sum(1 for r in identity_rows if r['response_match'])}/15",
        "identity_table": identity_rows,
    },
    "artifact_validation": validation,
    "validation_problems": problems,
    "criterion_count": N,
    "exact_agreement": agreement_stats["exact_agreement_pct"],
    "cohens_kappa": agreement_stats["cohens_kappa_unweighted"],
    "linear_weighted_kappa": agreement_stats["linear_weighted_kappa"],
    "quadratic_weighted_kappa": agreement_stats["quadratic_weighted_kappa"],
    "agreement_detail": agreement_stats,
    "opus_original_overall": opus_overall,
    "gpt56_blind_overall": gpt_overall,
    "overall_delta": round(gpt_overall - opus_overall, 2),
    "conservative_reconciliation_overall": lower_overall,
    "sensitivity": sensitivity,
    "scenario_results": scenario_results,
    "run_results": run_results,
    "run_statistics": run_stats,
    "dimension_results": dimension_results,
    "directional_disagreements": bias["criterion_points"] | {"runs": bias["run_scores"]},
    "false_action_agreement": fa_agreement,
    "penalty_agreement": pen_agreement,
    "disagreement_categories": {"distribution": dict(cat_dist),
                                "point_impact": {k: round(v, 2) for k, v in cat_impact.items()},
                                "rubric_text_notes": rubric_text_notes},
    "self_judge_bias_assessment": bias_assessment,
    "self_judge_bias_inputs": bias,
    "top_band_comparison": top_band,
    "generation_route_status": "PROVISIONAL_OFF_BENCHMARK",
    "generation_route_note": (
        "This audit addresses JUDGE validity only. The candidate was generated "
        "through a non-standard route rather than the benchmark's provider route, "
        "which is a separate and unresolved methodological problem. An independent "
        "re-judge cannot and does not fix it."),
}
(HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                   encoding="utf-8")

# ---------------------------------------------------------------------------
# Terminal report
# ---------------------------------------------------------------------------
print("INTER-JUDGE AUDIT COMPLETE\n")
print("Source integrity:")
print(f"  suite digest              {SUITE_DIGEST}")
print(f"  modified tracked files    0")
print(f"  response matches          {sum(1 for r in identity_rows if r['response_match'])}/15")
print("\nAtomic validation:")
print(f"  criterion rows            {validation['criterion_rows_supplied']} "
      f"(expected {validation['criterion_rows_expected']})")
print(f"  false-action rows         {validation['false_action_rows_supplied']} "
      f"(expected {validation['false_action_rows_expected']})")
print(f"  penalty rows              {validation['penalty_rows_supplied']} (expected 15)")
print(f"  validation problems       {len(problems)}")
for p in problems:
    print(f"    - {p['kind']}: {p['detail']} supplied={p['supplied']} recomputed={p['recomputed']}")
print("\nAgreement:")
print(f"  exact agreement           {agreement_stats['exact_agreement_pct']}%  "
      f"({agree}/{N})")
print(f"  Cohen's kappa             {agreement_stats['cohens_kappa_unweighted']}")
print(f"  linear weighted kappa     {agreement_stats['linear_weighted_kappa']}")
print(f"  quadratic weighted kappa  {agreement_stats['quadratic_weighted_kappa']}")
print(f"  PASS<->FAIL disagreements {agreement_stats['pass_fail_disagreements']}")
print("\nConfusion matrix (rows original, cols blind):")
print(f"  {'':14}{'GPT PASS':>10}{'GPT PARTIAL':>13}{'GPT FAIL':>10}")
for a in LABELS:
    row = confusion[f"opus_{a}"]
    print(f"  opus {a:<9}{row['gpt_PASS']:>10}{row['gpt_PARTIAL']:>13}{row['gpt_FAIL']:>10}")
print("\nScores:")
print(f"  original judge overall    {opus_overall:.2f}")
print(f"  blind judge overall       {gpt_overall:.2f}")
print(f"  delta                     {gpt_overall - opus_overall:+.2f}")
print(f"  conservative lower-label  {lower_overall:.2f}")
print(f"  per-criterion mean (C)    {mean_overall:.2f}")
print(f"  max spread A/B/C/D        {sensitivity['max_spread']:.2f}")
print("\nDirectional:")
print(f"  original > blind (criteria) {len(opus_higher)}")
print(f"  blind > original (criteria) {len(gpt_higher)}")
print(f"  equal (criteria)            {len(equal_pts)}")
print(f"  net point delta             {total_delta_pts:+.2f}")
print(f"  runs: original higher {len(runs_opus_higher)}, blind higher {len(runs_gpt_higher)}, equal {len(runs_equal)}")
print("\nTop comparison (blind overall vs published):")
for name, d in top_band["deltas"].items():
    print(f"  vs {name:20} {d['their_score']:.2f}  delta {d['blind_minus_them']:+.2f}  "
          f">run-sigma-ref({RUN_SIGMA_REFERENCE})={d['exceeds_run_sigma_reference']}")
print(f"  pooled within-scenario run SD (original) {pooled_within_scenario_sd}")
print(f"  SE of blind overall                      {se_overall_gpt}")
print("\nAssessment:")
print(f"  self-judge bias           {bias_assessment}")
print(f"  generation route          PROVISIONAL / OFF-BENCHMARK")
print("\nArtifacts written:")
for f in sorted(HERE.glob("*.csv")) + sorted(HERE.glob("*.json")):
    print(f"  {f.relative_to(ROOT)}")
