"""Join the blind labels to runs through the provenance map, and score them,
per model, for the two NaN challengers of 2026-10-19.

Adapted from experiments/gemini-3.8-flash-high-opus-judge/join-and-score.py;
one pack per model, under pack/<key>/ and blind-verdicts/<key>/, where <key>
is the first 8 hex of sha256(slug).

The five label files in `blind-verdicts/<key>/` were written from the blind pack alone
(see JUDGING.md): the judges never opened `provenance-map.json`. This script
performs the join mechanically, so no judgement is exercised where labels and
runs meet, and scores every run through the harness's own `build_breakdown`
against each scenario's OFFICIAL rubric.

Writes:
  verdicts/<slug>.jsonl     the labels keyed by run id instead of candidate id
  scores/<slug>.json        per-run final scores, dimension scores and
                            penalties, scenario means, sample stddev, Monday Score

Usage:  python experiments/nan-challengers-2026-10-19-opus-judge/join-and-score.py <slug>
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from mondaybench.config import load_yaml                     # noqa: E402
from mondaybench.scenarios import load_scenario              # noqa: E402
from mondaybench.schemas import PenaltyViolation             # noqa: E402
from mondaybench.scoring import build_breakdown              # noqa: E402

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {f"monday-00{i}": f"evaluator-opus5-v0.{i}" for i in range(1, 6)}
MODELS = sys.argv[1:2]
KEY = hashlib.sha256(MODELS[0].encode("utf-8")).hexdigest()[:8] if MODELS else ""
PACK = HERE / "pack" / KEY


def official_rubric(sid):
    cfg = load_yaml(ROOT / "evaluators" / f"{EVALUATORS[sid]}.yaml")
    return load_scenario(sid, rubric_file=cfg["rubric_file"]).rubric


def main() -> int:
    prov = json.loads((PACK / "provenance-map.json").read_text(encoding="utf-8"))
    cand_to_run = {c["candidate_id"]: c["true_run_id"]
                   for sid in SCEN for c in prov["scenarios"][sid]}
    run_to_model = {c["true_run_id"]: c["model_slug"]
                    for sid in SCEN for c in prov["scenarios"][sid]}

    problems: list[str] = []
    joined: dict[str, list[dict]] = {m: [] for m in MODELS}
    results = {m: {"model": m, "judge": "claude-opus-5-5, in-session, blind",
                   "scenarios": {}} for m in MODELS}
    means: dict[str, list[float]] = {m: [] for m in MODELS}
    for sid in SCEN:
        rub = official_rubric(sid)
        crit_ids = {c.id for c in rub.criteria}
        rows = [json.loads(l) for l in
                (HERE / "blind-verdicts" / KEY / f"{sid}.blind.jsonl").read_text(encoding="utf-8").splitlines()
                if l.strip()]
        labels: dict[str, dict[str, str]] = {}
        noise: dict[str, list[str]] = {}
        viol: dict[str, list] = {}
        for r in rows:
            run = cand_to_run[r["candidate_id"]]
            joined[run_to_model[run]].append(
                {"run_id": run, **{k: v for k, v in r.items() if k != "candidate_id"}})
            if r.get("kind") == "penalties":
                viol[run] = r.get("violations") or []
            elif r.get("kind") == "noise":
                noise[run] = [i["id"] for i in r["items"] if i.get("triggered")]
            else:
                labels.setdefault(run, {})[r["criterion_id"]] = r["result"]

        runs = {}
        for run in sorted(labels):
            lab = labels[run]
            if set(lab) != crit_ids:
                problems.append(f"{run}: criteria mismatch, missing {sorted(crit_ids - set(lab))}, "
                                f"extra {sorted(set(lab) - crit_ids)}")
                continue
            if run not in viol:
                problems.append(f"{run}: no penalties row")
            if rub.noise and run not in noise:
                problems.append(f"{run}: no noise row")
            fa = {a.id: (False, None) for a in (rub.noise.false_actions if rub.noise else [])}
            for k in noise.get(run, []):
                fa[k] = (True, None)
            vs = [PenaltyViolation(type=v["type"], evidence=v.get("evidence"), reason=v.get("reason"),
                                   materially_misleading=v.get("materially_misleading", True))
                  for v in viol.get(run, [])]
            bd = build_breakdown(rub, criterion_verdicts={c: (l, None, None) for c, l in lab.items()},
                                 false_actions=fa, violations=vs)
            runs[run] = {
                "final_score": bd.final_score,
                "base_score": bd.base_score,
                "dimensions": {k: d.score for k, d in bd.dimensions.items()},
                "penalties": [{"type": v.type, "materially_misleading": v.materially_misleading}
                              for v in vs],
                "noise_triggered": noise.get(run, []),
            }
        for m in MODELS:
            mine = {k: v for k, v in runs.items() if run_to_model[k] == m}
            if len(mine) != 3:
                problems.append(f"{sid} {m}: {len(mine)} scored runs, expected 3")
                continue
            scores = [r["final_score"] for r in mine.values()]
            mean = statistics.mean(scores)
            means[m].append(mean)
            results[m]["scenarios"][sid] = {
                "rubric_version": rub.version,
                "runs": mine,
                "mean": mean,
                "range": max(scores) - min(scores),
                "stddev_sample": statistics.stdev(scores),
            }

    if problems:
        print("STOP:")
        for p in problems:
            print("  -", p)
        return 1

    (HERE / "verdicts").mkdir(exist_ok=True)
    for m in MODELS:
        results[m]["monday_score"] = statistics.mean(means[m])
        with (HERE / "verdicts" / f"{m}.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
            for r in sorted(joined[m], key=lambda r: r["run_id"]):
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (HERE / "scores").mkdir(exist_ok=True)
    (HERE / "scores" / f"{MODELS[0]}.json").write_text(
        json.dumps(results[MODELS[0]], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    for m in MODELS:
        print(m)
        for sid in SCEN:
            s = results[m]["scenarios"][sid]
            print(f"  {sid}  mean {s['mean']:6.2f}  runs {[r['final_score'] for r in s['runs'].values()]}")
        print(f"  Monday Score {results[m]['monday_score']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
