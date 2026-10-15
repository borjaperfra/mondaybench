"""Join the blind labels to runs through the provenance map, and score them.

The five label files in `blind-verdicts/` were written from the blind pack alone
(see JUDGING.md): the judges never opened `provenance-map.json` and were never
told a prior score. This script performs the join mechanically, so no judgement
is exercised where labels and runs meet, and scores every run through the
harness's own `build_breakdown` against each scenario's OFFICIAL rubric.

Writes:
  verdicts.jsonl   the labels keyed by run id instead of candidate id
  scores.json      per-run final scores, dimension scores and penalties,
                   scenario means, sample stddev and the Monday Score

Usage:  python experiments/gemini-3.8-flash-high-opus-judge/join-and-score.py
"""
from __future__ import annotations

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
PACK = ROOT / "gemini-3.8-mondaybench-challenger" / "judge-pack"


def official_rubric(sid):
    cfg = load_yaml(ROOT / "evaluators" / f"{EVALUATORS[sid]}.yaml")
    return load_scenario(sid, rubric_file=cfg["rubric_file"]).rubric


def main() -> int:
    prov = json.loads((PACK / "provenance-map.json").read_text(encoding="utf-8"))
    cand_to_run = {c["candidate_id"]: c["true_run_id"]
                   for sid in SCEN for c in prov["scenarios"][sid]}

    problems: list[str] = []
    joined: list[dict] = []
    result = {"model": "gemini-3-8-flash-high", "judge": "claude-opus-5-5, in-session, blind",
              "scenarios": {}}
    means = []
    for sid in SCEN:
        rub = official_rubric(sid)
        crit_ids = {c.id for c in rub.criteria}
        rows = [json.loads(l) for l in
                (HERE / "blind-verdicts" / f"{sid}.blind.jsonl").read_text(encoding="utf-8").splitlines()
                if l.strip()]
        labels: dict[str, dict[str, str]] = {}
        noise: dict[str, list[str]] = {}
        viol: dict[str, list] = {}
        for r in rows:
            run = cand_to_run[r["candidate_id"]]
            joined.append({"run_id": run, **{k: v for k, v in r.items() if k != "candidate_id"}})
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
        if len(runs) != 3:
            problems.append(f"{sid}: {len(runs)} scored runs, expected 3")
            continue
        scores = [r["final_score"] for r in runs.values()]
        mean = statistics.mean(scores)
        means.append(mean)
        result["scenarios"][sid] = {
            "rubric_version": rub.version,
            "runs": runs,
            "mean": mean,
            "range": max(scores) - min(scores),
            "stddev_sample": statistics.stdev(scores),
        }

    if problems:
        print("STOP:")
        for p in problems:
            print("  -", p)
        return 1

    result["monday_score"] = statistics.mean(means)
    with (HERE / "verdicts.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in joined:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (HERE / "scores.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8", newline="\n")
    for sid in SCEN:
        s = result["scenarios"][sid]
        print(f"{sid}  mean {s['mean']:6.2f}  runs {[r['final_score'] for r in s['runs'].values()]}")
    print(f"Monday Score {result['monday_score']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
