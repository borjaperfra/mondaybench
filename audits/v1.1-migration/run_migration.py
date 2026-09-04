"""Execute the v1.1 re-stamp and write the migration audit artifacts.

Calls no model. Writes only under evaluations/v1.1/ and audits/v1.1-migration/.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent

from mondaybench.contract import contract_for            # noqa: E402
from mondaybench.evaluator import (                      # noqa: E402
    find_evaluations, load_evaluation, models_with_evaluations,
)
from mondaybench.migrate import migrate_scenario, verify_migration  # noqa: E402

TARGET = "1.1"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
INCUMBENTS = ["glm5.3-flash", "glm5.2", "mimo-v2.5", "deepseek-v4-flash",
              "qwen3.8-flash", "qwen3.6", "gemma4"]
CHALLENGER = "glm5.3"


def main() -> None:
    all_results = []
    per_scenario = {}
    fingerprints = {}

    for sid, ev in EVALUATORS.items():
        contract, fp = contract_for(sid, ev)
        results = migrate_scenario(
            scenario_id=sid, evaluator_id=ev, target_suite_version=TARGET, write=True)
        report = verify_migration(results)
        if not report["clean"]:
            raise SystemExit(f"STOP: {sid} migration changed judgments: {report['offenders']}")
        all_results.extend(results)
        per_scenario[sid] = {"evaluator_id": ev, "contract_fingerprint": fp, **report}

        legacy = set()
        for slug in models_with_evaluations(ev, sid):
            for p in find_evaluations(ev, sid, slug):
                legacy.add(load_evaluation(p).judge.prompt_fingerprint)
        new = set()
        for slug in models_with_evaluations(ev, sid, None, TARGET):
            for p in find_evaluations(ev, sid, slug, None, TARGET):
                new.add(load_evaluation(p).judge.contract_fingerprint)
        fingerprints[sid] = {
            "legacy_unique": sorted(x for x in legacy if x),
            "legacy_unique_count": len(legacy),
            "v1_1_unique": sorted(x for x in new if x),
            "v1_1_unique_count": len(new),
            "expected": "1",
            "pass": len(new) == 1,
        }
        print(f"{sid}: {report['evaluations_migrated']} migrated, "
              f"{report['criterion_labels_changed']} labels changed, "
              f"legacy {len(legacy)} -> v1.1 {len(new)}")

    overall = verify_migration(all_results)

    # ---- score invariance, recomputed per model ----------------------------
    invariance = {"incumbents": {}, "challenger": {}, "violations": []}
    for slug in INCUMBENTS + [CHALLENGER]:
        rows = {}
        for sid, ev in EVALUATORS.items():
            old = [load_evaluation(p).final_score for p in find_evaluations(ev, sid, slug)]
            new = [load_evaluation(p).final_score
                   for p in find_evaluations(ev, sid, slug, None, TARGET)]
            om = round(statistics.mean(old), 2) if old else None
            nm = round(statistics.mean(new), 2) if new else None
            rows[sid] = {"v1_0_runs": old, "v1_1_runs": new,
                         "v1_0_mean": om, "v1_1_mean": nm,
                         "runs_equal": old == new, "mean_delta": None if om is None
                         else round((nm or 0) - om, 2)}
            if old != new:
                invariance["violations"].append(f"{slug}/{sid}: run scores differ")
        means_old = [rows[s]["v1_0_mean"] for s in EVALUATORS]
        means_new = [rows[s]["v1_1_mean"] for s in EVALUATORS]
        entry = {
            "scenarios": rows,
            "v1_0_overall": round(sum(means_old) / 5, 2) if all(m is not None for m in means_old) else None,
            "v1_1_overall": round(sum(means_new) / 5, 2) if all(m is not None for m in means_new) else None,
        }
        entry["overall_delta"] = (
            None if entry["v1_0_overall"] is None
            else round(entry["v1_1_overall"] - entry["v1_0_overall"], 2))
        if entry["overall_delta"] not in (None, 0.0):
            invariance["violations"].append(f"{slug}: overall moved by {entry['overall_delta']}")
        (invariance["challenger"] if slug == CHALLENGER else invariance["incumbents"])[slug] = entry

    invariance["clean"] = not invariance["violations"]

    (HERE / "score-invariance.json").write_text(json.dumps({
        "read_only_inputs": True,
        "model_calls": 0, "judge_calls": 0, "candidate_regenerations": 0,
        "changed_historical_labels": overall["criterion_labels_changed"],
        "summary": {k: overall[k] for k in overall if k != "offenders"},
        **invariance,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")

    (HERE / "fingerprint-migration.json").write_text(json.dumps({
        "target_suite_version": TARGET,
        "scenarios": fingerprints,
        "all_pass": all(v["pass"] for v in fingerprints.values()),
        "note": ("Legacy counts are the stored judge_prompt_fingerprint values in the v1.0 "
                 "evaluations. v1.1 counts are the stored contract_fingerprint values in the "
                 "migrated ones. No v1.0 file was read for anything but comparison."),
    }, indent=2) + "\n", encoding="utf-8", newline="\n")

    print("\nscore invariance:", "CLEAN" if invariance["clean"] else invariance["violations"])
    print("total migrated:", overall["evaluations_migrated"],
          "| labels changed:", overall["criterion_labels_changed"],
          "| run scores changed:", overall["run_scores_changed"])
    print("glm5.3 v1.1 overall:", invariance["challenger"][CHALLENGER]["v1_1_overall"])


if __name__ == "__main__":
    main()
